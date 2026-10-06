#!/usr/bin/env python3
"""Check that every code citation in an onboarding skill still points at live code.

Usage: python3 <skill>/scripts/check_citations.py [--since <commit>]

Reads <skill>/onboarding.config.json for path roots. Reports, per cited `path` or `path:line`:
  ERROR  the path no longer exists, or the line range is past the end of the file
  WARN   none of the identifiers named next to the citation appear near the cited lines,
         or a bare filename matches more than one file
  INFO   the cited file or range carries a deprecation marker
With --since, also lists cited files changed between that commit and HEAD.
Exits 1 when there is any ERROR.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REPO = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=SKILL_DIR, text=True).strip())
CONFIG_PATH = SKILL_DIR / "onboarding.config.json"
CONFIG = json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH.exists() else {}
SOURCES = [
    SKILL_DIR / "SKILL.md",
    SKILL_DIR / "maintaining.md",
    *sorted((SKILL_DIR / "references").glob("*.md")),
    SKILL_DIR / "card.json",
]
ROOTS = ["", *[r if r.endswith("/") else r + "/" for r in CONFIG.get("roots", []) if r]]
PREFERRED_ROOTS = tuple(CONFIG.get("preferred_roots", []))
SKILL_PREFIX = SKILL_DIR.relative_to(REPO).as_posix() + "/"
SKIP_PREFIXES = (SKILL_PREFIX, "http", "/", *CONFIG.get("skip_prefixes", []))
HOSTNAME = re.compile(r"^[a-z0-9-]+(\.[a-z0-9-]+)*\.(com|dev|site|io|net|org|app)(/|$)")
EXTENSIONS = "rb|rake|ts|tsx|mts|js|mjs|jsx|json|jsonc|yml|yaml|md|swift|kt|kts|rs|go|java|proto|graphql|py|sh|toml|html|env|sql|tf|ex|exs|cs|php"

CITATION = re.compile(
    r"`((?:[A-Za-z0-9_.@$\[\]()\-]+/)*(?:Gemfile|Makefile|Dockerfile|justfile|[A-Za-z0-9_.@$\[\]()\-]*[A-Za-z0-9_\]\-]\.(?:" + EXTENSIONS + r"))"
    r"|[A-Za-z0-9_.\-]+/[A-Za-z0-9_.$\[\]()\-]+/?[A-Za-z0-9_./$\[\]()\-]*)(?::(\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*))?`"
)
CONSTANT_LIKE = re.compile(r"^[A-Z]")
INLINE_LINES = re.compile(r"`:(\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*)`")
IDENTIFIER = re.compile(r"`([A-Za-z_][A-Za-z0-9_:]*[?!]?)`")
RANGE_DEPRECATION = re.compile(r"\b(deprecated|retired|legacy|do not use|no longer used)\b", re.IGNORECASE)
HEADER_DEPRECATION = re.compile(r"\b(deprecated|retired|do not use|no longer used)\b", re.IGNORECASE)
CONTEXT_LINES = 4


def tracked_files():
    out = subprocess.check_output(["git", "ls-files"], cwd=REPO, text=True)
    return out.splitlines()


def by_basename(files):
    index = {}
    for f in files:
        index.setdefault(Path(f).name, []).append(f)
    return index


def source_lines(path):
    if not path.exists():
        return []
    if path.suffix == ".json":
        data = json.loads(path.read_text())
        for row in (data.get("capabilities") or {}).get("rows", []):
            for key in ("backend", "client"):
                row[key] = [f"`{p}`" for p in row.get(key, [])]
        text = json.dumps(data, indent=1, ensure_ascii=False).replace("\\n", "\n")
        return text.splitlines()
    return path.read_text().splitlines()


def narrow(matches, context_dirs):
    if len(matches) <= 1:
        return matches
    for directory in context_dirs:
        near = [m for m in matches if m.startswith(directory + "/")]
        if len(near) == 1:
            return near
    for root in PREFERRED_ROOTS:
        preferred = [m for m in matches if m.startswith(root) and "/test/" not in m and "/spec/" not in m]
        if len(preferred) == 1:
            return preferred
    return matches


def resolve(raw, files_set, basenames, context_dirs):
    raw = raw.rstrip("/")
    for root in ROOTS:
        candidate = root + raw
        if candidate in files_set or (REPO / candidate).is_dir():
            return [candidate]
    if "/" not in raw:
        return narrow(basenames.get(raw, []), context_dirs)
    return narrow([f for f in files_set if f.endswith("/" + raw)], context_dirs)


def parse_ranges(spec):
    ranges = []
    for part in spec.split(","):
        start, _, end = part.partition("-")
        ranges.append((int(start), int(end or start)))
    return ranges


def check(args):
    files = tracked_files()
    files_set = set(files)
    basenames = by_basename(files)
    errors = warnings = 0
    cited = set()

    for source in SOURCES:
        rel_source = source.relative_to(REPO) if source.exists() else source
        last_path = None
        context_dirs = []
        for lineno, line in enumerate(source_lines(source), 1):
            last_path = None
            hits = [(m.start(), m.group(1), m.group(2)) for m in CITATION.finditer(line)]
            hits += [(m.start(), None, m.group(1)) for m in INLINE_LINES.finditer(line)]
            hits.sort()
            segment_start = 0
            for position, raw, spec in hits:
                segment = line[segment_start:position].rsplit("|", 1)[-1]
                segment_start = position + 1
                named = {m for m in IDENTIFIER.findall(segment) if len(m) > 3 and not m.endswith("_")}
                if raw is not None:
                    if raw.startswith(SKIP_PREFIXES) or HOSTNAME.match(raw) or "..." in raw or "<" in raw or "*" in raw:
                        continue
                    if (SKILL_DIR / raw.rstrip("/")).exists():
                        continue
                    matches = resolve(raw, files_set, basenames, context_dirs)
                    where = f"{rel_source}:{lineno}"
                    if not matches:
                        print(f"ERROR {where}  `{raw}` not found in the repo")
                        errors += 1
                        last_path = None
                        continue
                    if len(matches) > 1:
                        if spec:
                            print(f"WARN  {where}  `{raw}` is ambiguous ({len(matches)} files), line check skipped")
                            warnings += 1
                        last_path = None
                        continue
                    last_path = matches[0]
                    cited.add(last_path)
                    parent = str(Path(last_path).parent)
                    context_dirs = [parent] + [d for d in context_dirs if d != parent][:9]
                elif last_path is None:
                    continue
                if not spec or (REPO / last_path).is_dir():
                    continue
                target_lines = (REPO / last_path).read_text(errors="replace").splitlines()
                whole_file = "\n".join(target_lines).lower()
                where = f"{rel_source}:{lineno}"
                windows = []
                for start, end in parse_ranges(spec):
                    if end > len(target_lines) or start < 1:
                        print(f"ERROR {where}  `{last_path}:{spec}` is past the end of the file ({len(target_lines)} lines)")
                        errors += 1
                        continue
                    windows.append("\n".join(target_lines[max(0, start - 1 - CONTEXT_LINES):end + CONTEXT_LINES]))
                    if RANGE_DEPRECATION.search("\n".join(target_lines[start - 1:end])):
                        print(f"INFO  {where}  `{last_path}:{spec}` has a deprecation marker in the cited lines")
                if not windows:
                    continue
                window = "\n".join(windows).lower()

                def found(name):
                    bare = name.split("::")[-1].rstrip("?!")
                    short = bare.lower()
                    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", bare).lower()
                    return short in window or snake in window or (CONSTANT_LIKE.match(name.split("::")[-1]) and short in whole_file)

                wanted = {n for n in named if n.split("::")[-1].rstrip("?!").lower() not in Path(last_path).name.lower()}
                if wanted and not any(found(n) for n in wanted):
                    print(f"WARN  {where}  `{last_path}:{spec}` doesn't mention {', '.join(sorted(wanted))}")
                    warnings += 1

    for path in sorted(cited):
        full = REPO / path
        if full.is_file() and HEADER_DEPRECATION.search("\n".join(full.read_text(errors="replace").splitlines()[:15])):
            print(f"INFO  `{path}` has a deprecation marker in its header")

    if args.since:
        changed = subprocess.check_output(["git", "diff", "--name-only", args.since, "HEAD"], cwd=REPO, text=True).split()
        touched = sorted(p for p in cited if p in changed or any(c.startswith(p + "/") for c in changed))
        print(f"\n{len(touched)} cited paths changed since {args.since}:")
        for p in touched:
            print(f"  {p}")

    print(f"\n{len(cited)} cited paths, {errors} errors, {warnings} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--since", help="commit the skill was last verified against")
    sys.exit(check(parser.parse_args()))
