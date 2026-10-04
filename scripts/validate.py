#!/usr/bin/env python3
"""Run layered privacy, portability, structure, and syntax validation."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 2 * 1024 * 1024

FORBIDDEN_PATH_PARTS = {
    ".cursor/plugins/cache",
    ".cursor/hooks/state",
    "__pycache__",
    ".DS_Store",
}

MACHINE_PATTERNS = {
    "macOS home path": re.compile("/" + r"Users/[A-Za-z0-9._-]+/"),
    "Linux home path": re.compile("/" + r"home/[A-Za-z0-9._-]+/"),
    "Windows home path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\"),
    "account auth id": re.compile(r"\bauth0\|[A-Za-z0-9_-]+"),
    "workspace document id": re.compile(
        r"https://(?:www\.)?notion\.so/[A-Za-z0-9_-]*[0-9a-f]{24,}",
        re.IGNORECASE,
    ),
    "drive document id": re.compile(
        r"https://docs\.google\.com/document/d/[A-Za-z0-9_-]{20,}"
    ),
}

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
ALLOWED_EMAILS = {
    "a@b.com",
    "hello@cocoon-ai.com",
    "you@example.com",
}

SECRET_PATTERNS = {
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    "generic API token": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "private key": re.compile(
        "-----BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
    "assigned credential": re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|"
        r"client[_-]?secret|password)\b[\"'\s:=]+"
        r"(?!\$\{|<|your_|example|xxxx)[A-Za-z0-9_./+=-]{12,}"
    ),
}


@dataclass
class Layer:
    name: str
    checked: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "PASS" if not self.errors else "FAIL"


SKIP_PARTS = {".git", "__pycache__"}


def repo_files(root: Path) -> list[Path]:
    return [
        path
        for path in sorted(root.rglob("*"))
        if not SKIP_PARTS.intersection(path.parts)
        and path.suffix != ".pyc"
        and (path.is_file() or path.is_symlink())
    ]


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def load_forbidden_terms(cli_json: str | None) -> list[str]:
    raw = cli_json or os.environ.get("CURSOR_HARNESS_FORBIDDEN_TERMS_JSON", "[]")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid forbidden-terms JSON: {exc}") from exc
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError("forbidden terms must be a JSON array of strings")
    return sorted({item.strip().lower() for item in value if item.strip()})


def validate_filesystem(root: Path, files: list[Path]) -> Layer:
    layer = Layer("filesystem")
    for path in files:
        layer.checked += 1
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            layer.errors.append(f"{relative}: symlinks are not portable")
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            layer.errors.append(f"{relative}: exceeds {MAX_FILE_BYTES} bytes")
        if any(part in relative for part in FORBIDDEN_PATH_PARTS):
            layer.errors.append(f"{relative}: generated or private state path")
        if ".bak-" in path.name or ".slim-backup-" in path.name:
            layer.errors.append(f"{relative}: backup artifact")
    layer.errors.extend(tracked_generated(root))
    return layer


def tracked_generated(root: Path) -> list[str]:
    """Fail when bytecode was committed. Local __pycache__ is ignored."""
    if not (root / ".git").exists():
        return []
    listed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True,
        check=False,
    )
    if listed.returncode != 0:
        return ["git-index: unable to list tracked files"]
    errors: list[str] = []
    for raw in listed.stdout.split(b"\0"):
        if not raw:
            continue
        relative = raw.decode("utf-8", "replace")
        parts = relative.split("/")
        if "__pycache__" in parts or relative.endswith(".pyc"):
            errors.append(f"{relative}: generated or private state path")
    return errors


def unwanted_email_offsets(text: str) -> list[int]:
    offsets: list[int] = []
    for match in EMAIL_RE.finditer(text):
        if match.group(0).lower() not in ALLOWED_EMAILS:
            offsets.append(match.start())
    return offsets


def scan_identity_text(
    layer: Layer,
    label: str,
    text: str,
    forbidden_terms: list[str],
) -> None:
    layer.checked += 1
    for pattern_label, pattern in MACHINE_PATTERNS.items():
        for match in pattern.finditer(text):
            line = line_number(text, match.start())
            layer.errors.append(f"{label}:{line}: {pattern_label}")
    for offset in unwanted_email_offsets(text):
        line = line_number(text, offset)
        layer.errors.append(f"{label}:{line}: email address")
    lowered = text.lower()
    for term in forbidden_terms:
        offset = lowered.find(term)
        if offset >= 0:
            line = line_number(text, offset)
            layer.errors.append(f"{label}:{line}: external forbidden term matched")


def history_text(root: Path) -> str | None:
    """Return patches from every commit, excluding author headers and trailers.

    None means this root is not its own git checkout. A failed read is an
    empty string so the caller can fail closed. Commit messages are omitted
    because trailers such as Co-authored-by carry author identity, not file
    contents.
    """
    if not (root / ".git").exists():
        return None
    top = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if top.returncode != 0:
        return ""
    if Path(top.stdout.strip()).resolve() != root.resolve():
        return None
    log = subprocess.run(
        ["git", "-C", str(root), "log", "--all", "--pretty=format:", "-p"],
        capture_output=True,
        text=True,
        check=False,
    )
    if log.returncode != 0:
        return ""
    return log.stdout


def validate_identity(
    root: Path,
    files: list[Path],
    forbidden_terms: list[str],
) -> Layer:
    layer = Layer("identity-and-organization")
    current_parts: list[str] = []
    for path in files:
        text = read_text(path)
        if text is None:
            continue
        relative = path.relative_to(root).as_posix()
        scan_identity_text(layer, relative, text, forbidden_terms)
        current_parts.append(text)

    history = history_text(root)
    if history is None:
        return layer
    if history == "":
        layer.errors.append("git-history: unable to read commit history")
        return layer

    current = "\n".join(current_parts)
    layer.checked += 1
    for pattern_label, pattern in MACHINE_PATTERNS.items():
        for match in pattern.finditer(history):
            snippet = match.group(0)
            if snippet in current:
                continue
            line = line_number(history, match.start())
            layer.errors.append(f"git-history:{line}: {pattern_label}")
    for match in EMAIL_RE.finditer(history):
        email = match.group(0)
        if email.lower() in ALLOWED_EMAILS or email in current:
            continue
        line = line_number(history, match.start())
        layer.errors.append(f"git-history:{line}: email address")
    lowered_history = history.lower()
    lowered_current = current.lower()
    for term in forbidden_terms:
        if term in lowered_current:
            continue
        offset = lowered_history.find(term)
        if offset >= 0:
            line = line_number(history, offset)
            layer.errors.append(
                f"git-history:{line}: external forbidden term matched"
            )
    return layer


def validate_secrets(root: Path, files: list[Path]) -> Layer:
    layer = Layer("secrets")
    for path in files:
        text = read_text(path)
        if text is None:
            continue
        layer.checked += 1
        relative = path.relative_to(root).as_posix()
        for label, pattern in SECRET_PATTERNS.items():
            for match in pattern.finditer(text):
                line = line_number(text, match.start())
                layer.errors.append(f"{relative}:{line}: possible {label}")
    return layer


def frontmatter(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    return text[4:end]


def frontmatter_value(header: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", header)
    return match.group(1).strip("\"'") if match else None


def validate_structure(root: Path, files: list[Path]) -> Layer:
    layer = Layer("structure-and-reuse")
    skill_names = {
        path.parent.name
        for path in files
        if path.name == "SKILL.md"
        and ".cursor" in path.parts
        and "skills" in path.parts
    }

    for path in files:
        text = read_text(path)
        if text is None:
            continue
        relative = path.relative_to(root).as_posix()

        if path.name == "SKILL.md":
            layer.checked += 1
            header = frontmatter(text)
            if header is None:
                layer.errors.append(f"{relative}: missing YAML frontmatter")
                continue
            name = frontmatter_value(header, "name")
            if not name:
                layer.errors.append(f"{relative}: missing frontmatter name")
            elif name != path.parent.name:
                layer.errors.append(
                    f"{relative}: skill name {name!r} != directory {path.parent.name!r}"
                )
            if "description:" not in header:
                layer.errors.append(f"{relative}: missing frontmatter description")

        if path.suffix == ".mdc":
            layer.checked += 1
            header = frontmatter(text)
            if header is None:
                layer.errors.append(f"{relative}: missing rule frontmatter")
            elif "alwaysApply:" not in header:
                layer.errors.append(f"{relative}: missing alwaysApply")

        for match in re.finditer(
            r"(?:~|\$HOME|\$\{HOME\})/\.cursor/skills/([a-z0-9-]+)/",
            text,
        ):
            referenced = match.group(1)
            if referenced not in skill_names:
                line = line_number(text, match.start())
                layer.errors.append(
                    f"{relative}:{line}: missing referenced skill {referenced}"
                )

        if relative == "templates/hooks.example.json":
            try:
                hook_config = json.loads(text)
                commands = [
                    entry["command"]
                    for entries in hook_config.get("hooks", {}).values()
                    for entry in entries
                ]
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                layer.errors.append(f"{relative}: invalid hook template: {exc}")
            else:
                expected = "${HOME}/.cursor/hooks/session-cost.sh"
                if not commands or any(command != expected for command in commands):
                    layer.errors.append(
                        f"{relative}: hook command must target installed script"
                    )

    return layer


def validate_syntax(root: Path, files: list[Path]) -> Layer:
    layer = Layer("syntax")
    for path in files:
        relative = path.relative_to(root).as_posix()
        if path.suffix in {".json", ".jsonc"}:
            layer.checked += 1
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                layer.errors.append(f"{relative}: invalid JSON: {exc}")
        elif path.suffix == ".py":
            layer.checked += 1
            try:
                source = path.read_text(encoding="utf-8")
                compile(source, str(path), "exec")
            except (SyntaxError, UnicodeDecodeError) as exc:
                layer.errors.append(f"{relative}: invalid Python: {exc}")
        elif path.suffix == ".sh":
            layer.checked += 1
            mode = path.stat().st_mode
            if not mode & stat.S_IXUSR:
                layer.errors.append(f"{relative}: shell script is not executable")
            syntax = subprocess.run(
                ["bash", "-n", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if syntax.returncode != 0:
                detail = syntax.stderr.strip().splitlines()
                message = detail[-1] if detail else "bash -n failed"
                layer.errors.append(f"{relative}: {message}")
        elif path.suffix in {".yaml", ".yml"} or path.name.endswith(
            (".yaml.example", ".yml.example")
        ):
            layer.checked += 1
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                layer.errors.append(f"{relative}: invalid YAML: {exc}")
                continue
            if "\t" in text:
                layer.errors.append(f"{relative}: YAML contains tab indentation")
            yaml_error = parse_yaml(text)
            if yaml_error:
                layer.errors.append(f"{relative}: {yaml_error}")
    return layer


def parse_yaml(text: str) -> str | None:
    try:
        import yaml
    except ImportError:
        return "PyYAML is required to validate YAML (pip install -r requirements.txt)"
    try:
        yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return f"invalid YAML: {exc}"
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument(
        "--forbidden-terms-json",
        help="JSON array of additional case-insensitive terms to reject",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    try:
        terms = load_forbidden_terms(args.forbidden_terms_json)
    except ValueError as exc:
        print(f"validation configuration error: {exc}", file=sys.stderr)
        return 2

    files = repo_files(root)
    layers = [
        validate_filesystem(root, files),
        validate_identity(root, files, terms),
        validate_secrets(root, files),
        validate_structure(root, files),
        validate_syntax(root, files),
    ]

    for layer in layers:
        print(f"{layer.status} {layer.name} ({layer.checked} checked)")
        for error in layer.errors:
            print(f"  - {error}")

    failures = sum(len(layer.errors) for layer in layers)
    if failures:
        print(f"validation failed with {failures} finding(s)", file=sys.stderr)
        return 1
    print(f"validation passed across {len(layers)} layers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
