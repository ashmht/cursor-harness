#!/usr/bin/env python3
"""Section-safe PR body edits. Fetches the live body first; never blind-overwrites.

Usage:
  pr-body-edit.py <pr|branch> --show
  pr-body-edit.py <pr|branch> --section <name> --file <path>
  pr-body-edit.py <pr|branch> --section <name> --stdin
  pr-body-edit.py <pr|branch> --section <name> --text '...'

Markers (HTML comments, invisible in GitHub UI):
  <!-- agent-section:NAME begin -->
  ...section body...
  <!-- agent-section:NAME end -->
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

BEGIN = "<!-- agent-section:{name} begin -->"
END = "<!-- agent-section:{name} end -->"
SECTION_RE = re.compile(
    r"<!--\s*agent-section:(?P<name>[A-Za-z0-9_./:-]+)\s+begin\s*-->"
    r"(?P<body>.*?)"
    r"<!--\s*agent-section:(?P=name)\s+end\s*-->",
    re.S,
)


def gh_json(pr: str, fields: str) -> dict:
    out = subprocess.run(
        ["gh", "pr", "view", pr, "--json", fields],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if out.returncode != 0:
        raise SystemExit(f"FAIL gh pr view: {out.stderr.strip() or out.stdout.strip()}")
    return json.loads(out.stdout)


def upsert_section(body: str, name: str, content: str) -> str:
    content = content.strip("\n")
    block = f"{BEGIN.format(name=name)}\n{content}\n{END.format(name=name)}"
    pattern = re.compile(
        rf"<!--\s*agent-section:{re.escape(name)}\s+begin\s*-->"
        rf".*?"
        rf"<!--\s*agent-section:{re.escape(name)}\s+end\s*-->",
        re.S,
    )
    if pattern.search(body or ""):
        return pattern.sub(block, body, count=1)
    body = body or ""
    if body and not body.endswith("\n"):
        body += "\n"
    return body + ("\n" if body else "") + block + "\n"


def list_sections(body: str) -> list[str]:
    return [m.group("name") for m in SECTION_RE.finditer(body or "")]


def apply_edit(pr: str, name: str, content: str, dry_run: bool) -> int:
    data = gh_json(pr, "number,url,body,updatedAt")
    old = data.get("body") or ""
    new = upsert_section(old, name, content)
    if new == old:
        print(f"ok   PR #{data['number']} section '{name}' already up to date (updatedAt {data['updatedAt']})")
        return 0
    print(f"info PR #{data['number']} updatedAt {data['updatedAt']} — writing section '{name}' only")
    if dry_run:
        print(new)
        return 0
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(new)
        path = fh.name
    try:
        out = subprocess.run(
            ["gh", "pr", "edit", str(data["number"]), "--body-file", path],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    finally:
        Path(path).unlink(missing_ok=True)
    if out.returncode != 0:
        print(f"FAIL gh pr edit: {out.stderr.strip() or out.stdout.strip()}")
        return 1
    print(f"ok   wrote section '{name}' on {data['url']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pr", help="PR number, URL, or branch")
    ap.add_argument("--show", action="store_true", help="print live body + section names")
    ap.add_argument("--section", help="section name to write (required for edits)")
    ap.add_argument("--file", help="path to section markdown")
    ap.add_argument("--text", help="inline section markdown")
    ap.add_argument("--stdin", action="store_true", help="read section markdown from stdin")
    ap.add_argument("--dry-run", action="store_true", help="print resulting body; do not edit")
    args = ap.parse_args()
    if args.show:
        data = gh_json(args.pr, "number,url,body,updatedAt")
        body = data.get("body") or ""
        print(f"PR #{data['number']} {data['url']} updatedAt {data['updatedAt']}")
        names = list_sections(body)
        print("sections: " + (", ".join(names) if names else "(none)"))
        print("---")
        print(body)
        return 0
    if not args.section:
        ap.error("--section required to edit (full-body overwrite is refused)")
    if sum(bool(x) for x in (args.file, args.text, args.stdin)) != 1:
        ap.error("provide exactly one of --file / --text / --stdin")
    if args.file:
        content = Path(args.file).read_text(encoding="utf-8")
    elif args.text is not None:
        content = args.text
    else:
        content = sys.stdin.read()
    if not content.strip():
        print("FAIL empty section content")
        return 1
    return apply_edit(args.pr, args.section, content, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
