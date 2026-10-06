#!/usr/bin/env python3
"""Create a <company>-expert onboarding skill inside a target repo from this skill's templates.

Usage, from the target repo root:
  python3 <codebase-onboarding>/scripts/scaffold.py --company "Acme" --dest .cursor/skills/acme-expert

Copies templates/ and the checker, card builder and renderer into --dest, fills the company name,
skill name, today's date and the current commit, and renders a first HTML card. Refuses to write
into an existing folder unless --force is given.
"""

import argparse
import datetime as dt
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "templates"
SCRIPTS = ("check_citations.py", "build_card.py", "render_card.py")


def git(*args, cwd):
    try:
        return subprocess.check_output(["git", *args], cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def fill(text, values):
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--company", required=True, help="company or product name, as people say it")
    ap.add_argument("--dest", required=True, help="folder to create, for example .cursor/skills/acme-expert")
    ap.add_argument("--html", default="codebase-map.html", help="file name for the rendered card")
    ap.add_argument("--force", action="store_true", help="write into an existing folder")
    args = ap.parse_args(argv)

    dest = Path(args.dest).resolve()
    if dest.exists() and any(dest.iterdir()) and not args.force:
        print(f"error: {dest} already exists and is not empty; pass --force to write into it", file=sys.stderr)
        return 2

    repo = git("rev-parse", "--show-toplevel", cwd=dest.parent if dest.parent.exists() else Path.cwd())
    if not repo:
        print("error: --dest must be inside a git repository", file=sys.stderr)
        return 2
    repo = Path(repo)
    values = {
        "company": args.company,
        "skill_name": dest.name,
        "commit": git("rev-parse", "--short=11", "HEAD", cwd=repo) or "unknown",
        "date": dt.date.today().isoformat(),
        "html": args.html,
        "dest": dest.relative_to(repo).as_posix(),
    }

    for source in sorted(TEMPLATES.rglob("*")):
        if source.is_dir():
            continue
        relative = source.relative_to(TEMPLATES)
        target = dest / (relative.with_name("SKILL.md") if relative.name == "SKILL.md.template" else relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(fill(source.read_text(), values))

    (dest / "scripts").mkdir(parents=True, exist_ok=True)
    for name in SCRIPTS:
        shutil.copy2(SKILL_DIR / "scripts" / name, dest / "scripts" / name)

    subprocess.check_call(
        [sys.executable, str(dest / "scripts" / "render_card.py"), str(dest / "card.json"), "-o", str(dest / args.html)],
        stdout=subprocess.DEVNULL,
    )
    print(f"created {values['dest']} for {args.company} at commit {values['commit']}")
    print("next: follow references/discovery.md in the codebase-onboarding skill to fill each file")
    return 0


if __name__ == "__main__":
    sys.exit(main())
