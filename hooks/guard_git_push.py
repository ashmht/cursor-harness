#!/usr/bin/env python3
"""beforeShellExecution: block pushes to main/master, plain force pushes, and unpinned force-with-lease.

Optionally runs a repo-specific preflight script when PREFLIGHT_PUSH_SCRIPT is set.
Fails open on malformed input.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys

PUSH = re.compile(
    r"(?:^|&&|\|\||[;|(\n]|\bthen\b|\bdo\b)\s*(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*"
    r"git\s+(?:-C\s+(\"[^\"]+\"|'[^']+'|\S+)\s+)?push\b(.*?)(?=&&|\|\||;|\||$)",
    re.S,
)
PROTECTED = re.compile(r"^\+?(?:[^:]*:)?(?:refs/heads/)?(main|master)$")


def respond(permission: str, agent_message: str | None = None, user_message: str | None = None) -> None:
    out: dict[str, str] = {"permission": permission}
    if agent_message:
        out["agent_message"] = agent_message
    if user_message or (permission == "deny" and agent_message):
        out["user_message"] = user_message or agent_message or ""
    print(json.dumps(out))
    sys.exit(0)


def git(path: str, *args: str) -> str:
    return subprocess.run(["git", "-C", path, *args], capture_output=True, text=True, timeout=5, check=False).stdout.strip()


def push_dir(command: str, match: re.Match[str], cwd: str) -> str:
    if match.group(1):
        target = match.group(1).strip("\"'")
    else:
        cds = re.findall(r"\bcd\s+(\"[^\"]+\"|'[^']+'|[^\s;&|]+)", command[: match.start()])
        target = cds[-1].strip("\"'") if cds else cwd
    target = os.path.expanduser(target)
    return target if os.path.isabs(target) else os.path.join(cwd, target)


def check_push(command: str, cwd: str | None = None) -> tuple[str, str | None, str | None]:
    match = PUSH.search(command)
    if not match:
        return ("allow", None, None)
    try:
        args = shlex.split(match.group(2))
    except ValueError:
        args = match.group(2).split()
    options = [a for a in args if a.startswith("-")]
    positional = [a for a in args if not a.startswith("-")]
    refspecs = positional[1:]

    if any(PROTECTED.match(r) for r in refspecs):
        return (
            "deny",
            "Blocked by push guard: never push directly to main/master. Push a feature branch and open a PR.",
            "Push to protected branch blocked by hook.",
        )
    if any(o in ("-f", "--force") for o in options) or any(r.startswith("+") for r in refspecs):
        return (
            "deny",
            "Blocked: plain --force/+refspec can overwrite another session's push. "
            "Fetch the remote SHA and use a pinned lease: --force-with-lease=<branch>:<remote-sha>.",
            None,
        )
    for o in options:
        if o == "--force-with-lease" or (o.startswith("--force-with-lease=") and ":" not in o.split("=", 1)[1]):
            return (
                "deny",
                "Blocked: an unpinned --force-with-lease trusts the shared tracking ref, which another "
                "session's fetch or push may have moved. Pin it: --force-with-lease=<branch>:<remote-sha>.",
                None,
            )

    path = push_dir(command, match, cwd or os.getcwd())
    if not os.path.isdir(path):
        return ("allow", None, None)

    branch = git(path, "branch", "--show-current")
    if not refspecs and branch in ("main", "master"):
        return (
            "deny",
            f"Blocked by push guard: current branch is '{branch}'. Push a feature branch and open a PR.",
            "Push to protected branch blocked by hook.",
        )

    preflight = os.environ.get("PREFLIGHT_PUSH_SCRIPT")
    if preflight and os.path.isfile(preflight):
        targets = {r.split(":")[-1].replace("refs/heads/", "") for r in refspecs}
        if refspecs and branch not in targets and "HEAD" not in targets:
            return (
                "allow",
                f"Push guard: refspecs {sorted(targets)} differ from checked-out branch '{branch}', "
                "so preflight script was skipped.",
                None,
            )
        try:
            pre = subprocess.run(
                [preflight],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=25,
                env={**os.environ, "PREFLIGHT_NO_FETCH": "1"},
                check=False,
            )
        except subprocess.TimeoutExpired:
            return ("allow", "Push guard: preflight script timed out; run it manually if rewriting history.", None)
        fails = [line for line in pre.stdout.splitlines() if line.startswith("FAIL")]
        warns = [line for line in pre.stdout.splitlines() if line.startswith("WARN")]
        if fails:
            return ("deny", "Blocked by preflight script:\n" + "\n".join(fails + warns), None)
        if warns:
            return ("allow", "Preflight warnings (non-blocking):\n" + "\n".join(warns), None)

    return ("allow", None, None)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        respond("allow")
    permission, agent_msg, user_msg = check_push(
        payload.get("command", ""),
        payload.get("cwd") or os.getcwd(),
    )
    respond(permission, agent_msg, user_msg)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        print(json.dumps({"permission": "allow"}))
