#!/usr/bin/env python3
"""Install portable rules, skills, hooks, and optional local config."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RULES_ROOT = REPO_ROOT / ".cursor" / "rules"
SKILLS_ROOT = REPO_ROOT / ".cursor" / "skills"
HOOKS_ROOT = REPO_ROOT / "hooks"
TEMPLATES = REPO_ROOT / "templates"

EXCLUDED_SKILLS = {"example-skill"}

RULE_PROFILES = {
    "core": {
        "workflow.mdc",
        "lang-memory-bank.mdc",
        "cursor-cost-discipline.mdc",
        "truth-seeking.mdc",
        "rebase-pr-branches.mdc",
    },
    "writing": {
        "fowler-voice.mdc",
        "framing.mdc",
        "julia-evans-voice.mdc",
        "larson-voice.mdc",
        "patio11-voice.mdc",
        "pragmatic-engineer-voice.mdc",
        "presentation-framing.mdc",
        "writing-compact.mdc",
    },
    "fintech": {
        "fcis-domain-core.mdc",
    },
}

SKILL_PROFILES = {
    "core": {
        "codebase-onboarding",
        "compact-chat",
        "critical-pr-review",
        "cross-collab-project-contract",
        "cursor-cost-handoff",
        "notion-mcp",
        "orchestrator-experts-judge",
        "skill-adoption-eval",
        "staff-eng",
    },
    "writing": {
        "architecture-diagram",
        "doc-loops",
        "engineering-blog",
        "humanizer",
        "loop-artifact",
        "loop-concept-explainer",
        "loop-design-doc",
        "loop-devils-advocate",
        "loop-docs-sweep",
        "loop-html-doc",
        "presentation-video",
        "reddit-post-writer",
        "socratic-doc-writer",
        "staff-eng-writing",
        "taste-loop",
        "teach",
        "technical-writing",
        "wow-deck",
    },
    "fintech": {
        "money-ledger-invariants",
        "risk-gate-kill-switch",
    },
}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def normalize_profiles(profiles: list[str] | None) -> list[str]:
    requested = profiles or ["core"]
    ordered: list[str] = []
    for name in requested:
        expanded = ["core", "writing", "fintech"] if name == "all" else [name]
        for item in expanded:
            if item not in ordered:
                ordered.append(item)
    return ordered


def selected_rules_and_skills(profiles: list[str]) -> tuple[set[str], set[str], bool]:
    rules: set[str] = set()
    skills: set[str] = set()
    for name in profiles:
        rules |= RULE_PROFILES[name]
        skills |= SKILL_PROFILES[name]
    return rules, skills, "core" in profiles


def source_files(profiles: list[str] | None = None) -> list[tuple[Path, Path]]:
    selected = normalize_profiles(profiles)
    rules, skills, include_hooks = selected_rules_and_skills(selected)
    files: list[tuple[Path, Path]] = []

    for source in sorted(RULES_ROOT.glob("*.mdc")):
        if source.name not in rules:
            continue
        files.append((source, Path("rules") / source.name))

    for source in sorted(SKILLS_ROOT.rglob("*")):
        if source.is_symlink():
            raise ValueError(f"Refusing symlink source: {source}")
        if not source.is_file() or "__pycache__" in source.parts:
            continue
        relative = source.relative_to(SKILLS_ROOT)
        skill_name = relative.parts[0]
        if skill_name in EXCLUDED_SKILLS or skill_name not in skills:
            continue
        files.append((source, Path("skills") / relative))

    if include_hooks:
        for source in sorted(HOOKS_ROOT.rglob("*")):
            if source.is_symlink():
                raise ValueError(f"Refusing symlink source: {source}")
            if source.is_file() and "__pycache__" not in source.parts:
                files.append((source, Path("hooks") / source.relative_to(HOOKS_ROOT)))
    return files


def backup_path(target: Path, timestamp: str) -> Path:
    candidate = target.with_name(f"{target.name}.bak-{timestamp}")
    counter = 2
    while candidate.exists():
        candidate = target.with_name(f"{target.name}.bak-{timestamp}-{counter}")
        counter += 1
    return candidate


def install(target_root: Path, *, apply: bool, force: bool, profiles: list[str] | None) -> int:
    target_root = target_root.expanduser().resolve()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    unsafe_conflicts: list[Path] = []
    existing_conflicts: list[Path] = []
    plan: list[tuple[Path, Path]] = []
    unchanged = 0

    for source, relative in source_files(profiles):
        target = target_root / relative
        if target.is_symlink():
            unsafe_conflicts.append(target)
            continue

        if target.exists() and digest(source) == digest(target):
            unchanged += 1
            continue

        if target.exists() and not force:
            existing_conflicts.append(target)
            continue

        plan.append((source, target))

    for target in unsafe_conflicts:
        print(f"CONFLICT symlink {target}")
    for target in existing_conflicts:
        print(f"CONFLICT exists {target}")
    for _, target in plan:
        action = "UPDATE" if target.exists() else "CREATE"
        print(f"{action} {target}")
    if "example-skill" in EXCLUDED_SKILLS:
        print("SKIP skill example-skill (template only, not installed)")

    conflicts = len(unsafe_conflicts) + len(existing_conflicts)
    mode = "apply blocked" if apply else "dry-run"
    if conflicts:
        print(
            f"{mode}: {len(plan)} planned, {unchanged} unchanged, "
            f"{conflicts} conflicts"
        )
        if unsafe_conflicts:
            print("Symlink conflicts must be resolved manually.", file=sys.stderr)
        elif not force:
            print(
                "Re-run with --force to back up and replace existing files.",
                file=sys.stderr,
            )
        return 2

    if not apply:
        print(f"dry-run: {len(plan)} changes, {unchanged} unchanged, 0 conflicts")
        return 0

    for source, target in plan:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            backup = backup_path(target, timestamp)
            shutil.copy2(target, backup)
            print(f"BACKUP {backup}")
        shutil.copy2(source, target)

    print(f"applied: {len(plan)} changes, {unchanged} unchanged, 0 conflicts")
    return 0


def cursor_user_dir(config_home: Path) -> Path:
    if sys.platform == "darwin":
        return config_home / "Library/Application Support/Cursor/User"
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata and config_home == Path.home():
            return Path(appdata) / "Cursor/User"
        return config_home / "AppData/Roaming/Cursor/User"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg and config_home == Path.home():
        return Path(xdg) / "Cursor/User"
    return config_home / ".config/Cursor/User"


def personal_instructions(text: str) -> str:
    return text.replace("Copy this to `~/.claude/CLAUDE.md` and customize.\n\n", "")


def load_json(path: Path) -> tuple[object | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, str(exc)


def merge_missing(base: dict, incoming: dict, *, force: bool) -> None:
    for key, value in incoming.items():
        if key not in base:
            base[key] = value
        elif isinstance(base[key], dict) and isinstance(value, dict):
            merge_missing(base[key], value, force=force)
        elif force and base[key] != value:
            base[key] = value


def merge_keybindings(existing: list, incoming: list, *, force: bool) -> list[str]:
    conflicts: list[str] = []
    by_key = {
        item.get("key"): item
        for item in existing
        if isinstance(item, dict) and item.get("key")
    }
    for item in incoming:
        if not isinstance(item, dict):
            continue
        key = item.get("key")
        current = by_key.get(key)
        if current is None:
            existing.append(item)
            by_key[key] = item
        elif current.get("command") != item.get("command"):
            if force:
                current["command"] = item.get("command")
            else:
                conflicts.append(str(key))
    return conflicts


def merge_hooks(existing: dict, incoming: dict, *, force: bool) -> None:
    if "version" not in existing:
        existing["version"] = incoming.get("version", 1)
    hooks = existing.setdefault("hooks", {})
    for event, entries in incoming.get("hooks", {}).items():
        current = hooks.setdefault(event, [])
        commands = {entry.get("command") for entry in current if isinstance(entry, dict)}
        for entry in entries:
            command = entry.get("command")
            if command not in commands:
                current.append(entry)
                commands.add(command)
            elif force:
                for index, current_entry in enumerate(current):
                    if current_entry.get("command") == command:
                        current[index] = entry


def config_targets(config_home: Path) -> list[tuple[str, Path, Path]]:
    user_dir = cursor_user_dir(config_home)
    return [
        ("cli", TEMPLATES / "cli-config.example.json", config_home / ".cursor" / "cli-config.json"),
        ("mcp", TEMPLATES / "mcp.example.json", config_home / ".cursor" / "mcp.json"),
        ("hooks", TEMPLATES / "hooks.example.json", config_home / ".cursor" / "hooks.json"),
        ("settings", TEMPLATES / "settings.example.jsonc", user_dir / "settings.json"),
        ("keybindings", TEMPLATES / "keybindings.example.json", user_dir / "keybindings.json"),
        ("claude", TEMPLATES / "claude-personal.md", config_home / ".claude" / "CLAUDE.md"),
    ]


def install_config(config_home: Path, *, apply: bool, force: bool) -> int:
    config_home = config_home.expanduser().resolve()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    conflicts = 0
    changes = 0
    unchanged = 0
    planned: list[tuple[Path, str]] = []

    for kind, source, target in config_targets(config_home):
        source_text = source.read_text(encoding="utf-8")
        if kind == "claude":
            desired = personal_instructions(source_text)
            if not target.exists():
                print(f"CREATE {target}")
                planned.append((target, desired))
                changes += 1
                continue
            current = target.read_text(encoding="utf-8")
            if current == desired:
                unchanged += 1
                continue
            if not force:
                print(f"CONFLICT exists {target}")
                conflicts += 1
                continue
            print(f"UPDATE {target}")
            planned.append((target, desired))
            changes += 1
            continue

        incoming, incoming_error = load_json(source)
        if incoming_error or incoming is None:
            print(f"CONFLICT template {source}: {incoming_error}")
            conflicts += 1
            continue
        if not target.exists():
            print(f"CREATE {target}")
            planned.append((target, json.dumps(incoming, indent=2) + "\n"))
            changes += 1
            continue
        current, current_error = load_json(target)
        if current_error or current is None:
            print(f"CONFLICT unreadable {target}: {current_error}")
            conflicts += 1
            continue

        if kind == "keybindings":
            if not isinstance(current, list) or not isinstance(incoming, list):
                print(f"CONFLICT shape {target}")
                conflicts += 1
                continue
            key_conflicts = merge_keybindings(current, incoming, force=force)
            if key_conflicts and not force:
                print(f"CONFLICT keybinding {target}: {', '.join(key_conflicts)}")
                conflicts += 1
                continue
            rendered = json.dumps(current, indent=2) + "\n"
        elif kind == "hooks":
            if not isinstance(current, dict) or not isinstance(incoming, dict):
                print(f"CONFLICT shape {target}")
                conflicts += 1
                continue
            merge_hooks(current, incoming, force=force)
            rendered = json.dumps(current, indent=2) + "\n"
        else:
            if not isinstance(current, dict) or not isinstance(incoming, dict):
                print(f"CONFLICT shape {target}")
                conflicts += 1
                continue
            merge_missing(current, incoming, force=force)
            rendered = json.dumps(current, indent=2) + "\n"

        if target.read_text(encoding="utf-8") == rendered:
            unchanged += 1
            continue
        print(f"MERGE {target}")
        planned.append((target, rendered))
        changes += 1

    mode = "apply blocked" if apply else "dry-run"
    if conflicts:
        print(f"config {mode}: {changes} planned, {unchanged} unchanged, {conflicts} conflicts")
        if not force:
            print("Re-run with --force to back up and replace conflicting config.", file=sys.stderr)
        return 2
    if not apply:
        print(f"config dry-run: {changes} changes, {unchanged} unchanged, 0 conflicts")
        return 0

    for target, rendered in planned:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            backup = backup_path(target, timestamp)
            shutil.copy2(target, backup)
            print(f"BACKUP {backup}")
        target.write_text(rendered, encoding="utf-8")
    print(f"config applied: {changes} changes, {unchanged} unchanged, 0 conflicts")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        type=Path,
        default=Path.home() / ".cursor",
        help="Cursor home to update (default: ~/.cursor)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform the installation. Without this flag, only print the plan.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Back up and replace files that already exist.",
    )
    parser.add_argument(
        "--profile",
        action="append",
        choices=["core", "writing", "fintech", "all"],
        help="Profile to install. Repeatable. Default: core. 'all' installs every profile except example-skill.",
    )
    parser.add_argument(
        "--config",
        action="store_true",
        help="Also merge CLI, MCP, hooks, editor settings, keybindings, and personal instructions.",
    )
    parser.add_argument(
        "--config-home",
        type=Path,
        default=None,
        help="Home directory used by --config (default: the real home directory).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        status = install(
            args.target,
            apply=args.apply,
            force=args.force,
            profiles=args.profile,
        )
        if args.config:
            config_status = install_config(
                args.config_home or Path.home(),
                apply=args.apply,
                force=args.force,
            )
            status = max(status, config_status)
        return status
    except (OSError, ValueError) as exc:
        print(f"install failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
