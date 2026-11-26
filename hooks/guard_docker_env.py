#!/usr/bin/env python3
"""beforeShellExecution: deny docker commands that print a container's environment.

Container environments often hold package-registry tokens, API keys, or database credentials;
`docker inspect ... .Config.Env` or `docker exec <c> env` lands them in the agent transcript,
and grep filters on names like "token" miss non-standard variable names. Writing the env to a
file for `--env-file` is allowed, as is printing variable names only. Fails open on parse errors.
"""

from __future__ import annotations

import json
import re
import sys

BYPASS = "# env-print-ok"
SEGMENT_SPLIT = re.compile(r"&&|\|\||;|\n")
HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?")
INSPECT = re.compile(r"\bdocker\s+(?:container\s+)?inspect\b")
FORMAT_FLAG = re.compile(r"(?:--format\b|\s-f\s)")
ENV_FIELD = re.compile(r"\.Env\b|\bEnv\b")
ENV_COMMAND = re.compile(
    r"\bdocker\s+(?:exec|run|compose\s+(?:exec|run))\b.*?\s(?:env|printenv|export|set)\s*(?:$|[|>])"
)
FILE_REDIRECT = re.compile(r"(?<![0-9&])>\s*(?!&)\S")
NAMES_ONLY = re.compile(
    r"\|\s*(?:cut\s+-d\s*['\"]?=['\"]?\s+-f\s*1\b|sed\s+['\"]?s/=\.\*//|awk\s+-F\s*['\"]?=['\"]?\s+['\"]?\{\s*print\s+\$1)"
)

MESSAGE = (
    "Blocked: this prints a container's environment, which may contain secrets or package-registry "
    "credentials that grep filters miss. To reuse the env, write it to a file without printing: "
    "docker inspect <container> --format '{{range .Config.Env}}{{println .}}{{end}}' > /tmp/container.env, "
    "then pass --env-file /tmp/container.env (delete the file after). To list variable names only, "
    "pipe through `cut -d= -f1`. Ask the user before printing values; add '"
    + BYPASS
    + "' only if approved."
)


def segment_prints_env(segment: str) -> bool:
    if INSPECT.search(segment):
        reads_env = bool(ENV_FIELD.search(segment) or not FORMAT_FLAG.search(segment))
    else:
        reads_env = bool(ENV_COMMAND.search(segment))
    if not reads_env:
        return False
    return not (FILE_REDIRECT.search(segment) or NAMES_ONLY.search(segment))


def strip_heredocs(command: str) -> str:
    lines, out, terminator = command.split("\n"), [], None
    for line in lines:
        if terminator is not None:
            if line.strip() == terminator:
                terminator = None
            continue
        out.append(line)
        match = HEREDOC.search(line)
        if match:
            terminator = match.group(1)
    return "\n".join(out)


def prints_env(command: str) -> bool:
    if BYPASS in command or "docker" not in command:
        return False
    return any(segment_prints_env(s) for s in SEGMENT_SPLIT.split(strip_heredocs(command)))


def respond(permission: str, agent_message: str | None = None) -> None:
    out: dict[str, str] = {"permission": permission}
    if agent_message:
        out["agent_message"] = agent_message
        out["user_message"] = agent_message
    print(json.dumps(out))
    sys.exit(0)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        respond("allow")
    if prints_env(payload.get("command", "")):
        respond("deny", MESSAGE)
    respond("allow")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        print(json.dumps({"permission": "allow"}))
