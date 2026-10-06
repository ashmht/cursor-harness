#!/usr/bin/env python3
"""Copy the capability map from references/capabilities.md into card.json, then render the HTML.

Usage: python3 <skill>/scripts/build_card.py [--check]

capabilities.md is the source of truth. This rewrites only the top-level "capabilities" line of
card.json, so the rest of the file keeps its hand formatting. Display prefixes, the intro and the
HTML file name come from onboarding.config.json. With --check, exits 1 if card.json is out of date
instead of writing it.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SOURCE = SKILL_DIR / "references" / "capabilities.md"
CARD = SKILL_DIR / "card.json"
CONFIG_PATH = SKILL_DIR / "onboarding.config.json"
CONFIG = json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH.exists() else {}
HTML = SKILL_DIR / CONFIG.get("html", "codebase-map.html")
DISPLAY_PREFIXES = CONFIG.get("display_prefixes", {})
INTRO = CONFIG.get(
    "capabilities_intro",
    "What the product offers, and where each piece lives. The full version, with vendors and "
    "runbooks per capability, is references/capabilities.md. Hover a path to see it in full.",
)

LINK = re.compile(r"\[([^\]]+)\]\(([^)#]+)(?:#[^)]*)?\)")
PATH = re.compile(r"`([^`]+)`")
FIELD = re.compile(r"^- \*\*([^*]+):\*\* (.*)$")


def plain(text):
    def label(m):
        name, target = m.group(1), m.group(2)
        return f"{target} {name}" if name.startswith("§") else name
    return LINK.sub(label, text)


def parse(text):
    rows = []
    group = None
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            group = line[3:].strip()
        elif line.startswith("### "):
            current = {"group": group, "capability": line[4:].strip(), "what": "", "fields": {}}
            rows.append(current)
        elif current is not None:
            field = FIELD.match(line)
            if field:
                current["fields"][field.group(1)] = field.group(2)
            elif line.strip() and not current["what"]:
                current["what"] = line.strip().rstrip(".")
    return [_row(r) for r in rows if "<" not in r["capability"]]


def _row(r):
    fields = r["fields"]
    read = [plain(fields[k]) for k in ("Read next", "Flow", "Model", "Owner") if k in fields]
    if "When it breaks" in fields:
        read.append("debugging.md: " + plain(fields["When it breaks"]))
    return {
        "group": r["group"],
        "capability": r["capability"],
        "what": r["what"],
        "backend": PATH.findall(fields.get("Backend", "")),
        "client": PATH.findall(fields.get("Client", fields.get("Web", ""))),
        "read": "; ".join(read),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if card.json is out of date")
    args = ap.parse_args(argv)

    rows = parse(SOURCE.read_text())
    if not rows:
        print(f"error: no filled-in capabilities in {SOURCE}", file=sys.stderr)
        return 2
    caps = {"intro": INTRO, "display_prefixes": DISPLAY_PREFIXES, "rows": rows}
    new_line = '  "capabilities": ' + json.dumps(caps, ensure_ascii=False) + ","

    lines = CARD.read_text().splitlines()
    index = [i for i, line in enumerate(lines) if line.startswith('  "capabilities": ')]
    if len(index) != 1:
        print('error: card.json needs exactly one top-level "capabilities" line', file=sys.stderr)
        return 2
    if lines[index[0]] == new_line:
        print(f"card.json is up to date ({len(rows)} capabilities)")
        return 0
    if args.check:
        print("card.json is out of date; run scripts/build_card.py", file=sys.stderr)
        return 1

    lines[index[0]] = new_line
    CARD.write_text("\n".join(lines) + "\n")
    json.loads(CARD.read_text())
    subprocess.check_call([sys.executable, str(SKILL_DIR / "scripts" / "render_card.py"), str(CARD), "-o", str(HTML)])
    print(f"wrote {len(rows)} capabilities to card.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
