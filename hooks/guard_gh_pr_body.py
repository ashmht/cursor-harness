#!/usr/bin/env python3
"""beforeShellExecution: deny blind full PR-body overwrites via gh pr edit.

Agents should use pr-body-edit.py --section <name> (fetches the live body and replaces
only one marked section). Creating a PR (`gh pr create`) is allowed. Bypass only after
explicit user approval by adding `# pr-body-ok` to the command. Fails open on parse errors.
"""

from __future__ import annotations

import json
import os
import re
import sys

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
BYPASS = "# pr-body-ok"
MESSAGE = (
    "Blocked: blind `gh pr edit --body` / `--body-file` overwrites sections other "
    "sessions or humans may have just added. "
    f"Use {HOOKS_DIR}/pr-body-edit.py <pr> --section <name> --file <path> "
    "(or --stdin / --text); it re-fetches and replaces only your "
    "<!-- agent-section:NAME --> block. "
    f"Add '{BYPASS}' only after the user approves a full rewrite of the fetched body."
)

EDIT = re.compile(
    r"(?:^|&&|\|\||[;|\n]|\bthen\b|\bdo\b)\s*"
    r"(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*"
    r"gh\s+pr\s+edit\b",
    re.S,
)
BODY_FLAG = re.compile(r"(?:^|\s)(--body\b|--body-file\b|-F\s*body=|--raw-field\s*body=)")


def denies(command: str) -> bool:
    if BYPASS in command:
        return False
    if not EDIT.search(command):
        return False
    return bool(BODY_FLAG.search(command))


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        print(json.dumps({"permission": "allow"}))
        return
    command = payload.get("command") or ""
    if denies(command):
        print(
            json.dumps(
                {
                    "permission": "deny",
                    "user_message": MESSAGE,
                    "agent_message": MESSAGE,
                }
            )
        )
        return
    print(json.dumps({"permission": "allow"}))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        print(json.dumps({"permission": "allow"}))
