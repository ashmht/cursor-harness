#!/usr/bin/env python3
"""Check that an onboarding skill is finished and its links work.

Usage: python3 <skill>/scripts/lint_skill.py

Reports:
  ERROR  a template placeholder like `<path>` or an instruction comment is still in the text
  ERROR  a relative link points at a missing file, or at a heading that doesn't exist
  ERROR  the audience is "staff" and a staff file is missing
  WARN   a "Verified against commit" stamp is older than max_age_days, or names an unknown commit
Exits 1 when there is any ERROR. Reads audience and max_age_days from onboarding.config.json.
"""

import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_DIR / "onboarding.config.json"
CONFIG = json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH.exists() else {}
AUDIENCE = CONFIG.get("audience", "staff")
MAX_AGE_DAYS = int(CONFIG.get("max_age_days", 90))
STAFF_FILES = ("decisions.md", "ownership.md", "operations.md", "security.md", "onboarding-path.md")

HTML_TAGS = {
    "a", "b", "br", "code", "details", "div", "em", "hr", "i", "img", "kbd", "li", "ol", "p", "pre",
    "small", "span", "strong", "sub", "summary", "sup", "table", "tbody", "td", "th", "thead", "tr", "ul",
}
PLACEHOLDER = re.compile(r"(?<![A-Za-z0-9_\]\)])<(?!!--)(/?)([^<>\n]{1,400})>")
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
STAMP = re.compile(r"Verified against commit `([0-9a-f]{7,40}|[^`]+)`")
FENCE = re.compile(r"^\s*(```|~~~)")


def markdown_files():
    return [SKILL_DIR / "SKILL.md", SKILL_DIR / "maintaining.md", *sorted((SKILL_DIR / "references").glob("*.md"))]


def prose_lines(text):
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield lineno, line


def slug(heading):
    text = heading.strip().lower().replace("`", "")
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(path):
    found = set()
    counts = {}
    for _, line in prose_lines(path.read_text()):
        if line.startswith("#"):
            base = slug(line.lstrip("#"))
            n = counts.get(base, 0)
            found.add(base if n == 0 else f"{base}-{n}")
            counts[base] = n + 1
    return found


def placeholder_problems(text):
    for lineno, line in prose_lines(text):
        if "<!--" in line:
            yield lineno, "instruction comment left in"
        for m in PLACEHOLDER.finditer(line):
            closing, raw = m.group(1), m.group(2)
            if raw[:1].isspace():
                continue
            inner = raw.strip()
            tag = re.split(r"[\s>]", inner, maxsplit=1)[0].lower()
            if tag in HTML_TAGS and (closing or " " not in inner or "=" in inner):
                continue
            if inner.startswith(("http", "=", "-")):
                continue
            yield lineno, f"unfilled placeholder <{inner}>"


def card_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from card_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from card_strings(item)


def commit_age_days(commit):
    try:
        stamp = subprocess.check_output(
            ["git", "show", "-s", "--format=%ct", commit], cwd=SKILL_DIR, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.CalledProcessError:
        return None
    return (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromtimestamp(int(stamp), dt.timezone.utc)).days


def main():
    errors = warnings = 0
    stamps = {}

    def error(where, message):
        nonlocal errors
        errors += 1
        print(f"ERROR {where}  {message}")

    def warn(where, message):
        nonlocal warnings
        warnings += 1
        print(f"WARN  {where}  {message}")

    for path in markdown_files():
        if not path.exists():
            continue
        rel = path.relative_to(SKILL_DIR)
        text = path.read_text()
        for lineno, message in placeholder_problems(text):
            error(f"{rel}:{lineno}", message)
        for lineno, line in prose_lines(text):
            for target in LINK.findall(line):
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                file_part, _, anchor = target.partition("#")
                linked = (path.parent / file_part).resolve() if file_part else path
                if not linked.exists():
                    error(f"{rel}:{lineno}", f"link to missing file {file_part}")
                elif anchor and linked.suffix == ".md" and anchor not in anchors(linked):
                    error(f"{rel}:{lineno}", f"link to missing heading #{anchor} in {file_part or rel}")
        for commit in STAMP.findall(text):
            stamps.setdefault(commit, []).append(str(rel))

    card = SKILL_DIR / "card.json"
    if card.exists():
        data = json.loads(card.read_text())
        for value in card_strings(data):
            for _, message in placeholder_problems(value):
                error("card.json", message)
        for commit in STAMP.findall(json.dumps(data)):
            stamps.setdefault(commit, []).append("card.json")

    if AUDIENCE == "staff":
        for name in STAFF_FILES:
            if not (SKILL_DIR / "references" / name).exists():
                error(f"references/{name}", "missing; required when audience is staff")

    for commit, files in sorted(stamps.items()):
        age = commit_age_days(commit)
        if age is None:
            warn(", ".join(files[:3]), f"stamp `{commit}` is not a commit in this repo")
        elif age > MAX_AGE_DAYS:
            warn(", ".join(files[:3]), f"stamp `{commit}` is {age} days old (max {MAX_AGE_DAYS}); re-verify")

    print(f"\n{errors} errors, {warnings} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
