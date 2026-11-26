#!/usr/bin/env python3
"""beforeShellExecution: block unquoted $VAR uses that zsh passes as ONE argument where a list is
expected, and unquoted words starting with `=` (zsh EQUALS expansion: `echo ======` fails).

zsh does not word-split unquoted parameter expansions (sh_word_split is off), so `F="a b"; rspec $F`,
`for f in $F`, `files=$(git diff --name-only); rubocop $files`, and `P="pnpm --flag"; $P lint` each
receive a single word. Bypass for a deliberate one-word use: put `# zsh-split-ok` in the command.
Fails open on malformed input.
"""

from __future__ import annotations

import json
import re
import sys

NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
ASSIGN_WORD = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\[[^\]]*\])?\+?=")
LISTISH = re.compile(
    r"(?i)(?:^|_)(?:files|paths|specs|dirs|args|argv|list|targets|branches|shas|ids|tags|opts|flags|cmd|items|"
    r"prs|tickets|refs|worktrees|tests)$"
)
GIT = r"git\s+(?:-C\s+\S+\s+)?"
ALWAYS_LIST = re.compile(
    GIT + r"(?:diff|show|log)\b[^|;)]*--name-(?:only|status)|" + GIT + r"ls-files\b|"
    r"\btr\s+(?:-s\s+)?['\"]\\n['\"]\s+['\"][ ,]['\"]|\bpaste\s+-s|\bxargs\b|"
    r"\bhead\s+-(?:n\s*)?(?:[2-9]|[1-9]\d+)\b"
)
MAYBE_LIST = re.compile(
    r"(?:^|[\s(|;])(?:rg(?:\s[^|;)]*)?\s(?:-[a-zA-Z]*l[a-zA-Z]*|--files(?:-with-matches)?)\b|"
    + GIT
    + r"(?:grep(?:\s[^|;)]*)?\s-[a-zA-Z]*l\b|ls-tree\b)|grep(?:\s[^|;)]*)?\s-[a-zA-Z]*l\b|(?:find|fd)\s|ls(?:\s|\)|$))"
)
ONE_LINE = re.compile(r"\b(?:head|tail)\s+-(?:n\s*)?1\b|\bwc\s+-[lwc]\b")
SPLIT_OK = re.compile(r"\bsetopt\s+(?:\S+\s+)*(?:sh_?word_?split)\b|\bemulate\s+(?:-\S+\s+)*(?:sh|ksh|bash)\b", re.I)
NO_SPLIT_COMMANDS = {"echo", "print", "export", "local", "typeset", "declare", "readonly", "integer", "float"}
KEYWORDS = {"do", "then", "else", "elif", "if", "while", "until", "!", "time", "{", "nohup", "command", "builtin"}
WORD_BREAK = set(" \t\n;&|()<>")
BYPASS = "# zsh-split-ok"


def respond(permission: str, agent_message: str | None = None) -> None:
    out: dict[str, str] = {"permission": permission}
    if agent_message:
        out["agent_message"] = agent_message
        out["user_message"] = agent_message
    print(json.dumps(out))
    sys.exit(0)


def matching_brace(s: str, i: int) -> int:
    depth = 0
    while i < len(s):
        if s[i] == "\\":
            i += 2
            continue
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(s) - 1


def braced_name(inner: str) -> tuple[str | None, bool]:
    """Return (name, explicitly_split) for the contents of ${...}."""
    split = False
    rest = inner
    while rest:
        if rest[0] == "(":
            close = rest.find(")")
            flags = rest[1:close] if close > 0 else ""
            if re.search(r"[zf@0]|s.", flags):
                split = True
            rest = rest[close + 1 :] if close > 0 else ""
        elif rest[0] in "=^~":
            split = split or rest[0] == "="
            rest = rest[1:]
        elif rest[0] in "#+":
            return None, True
        else:
            break
    m = NAME.match(rest)
    if not m:
        return None, True
    tail = rest[m.end() :]
    if tail.startswith("[@]") or tail.startswith("[*]"):
        split = True
    return m.group(0), split


def heredoc_delims(s: str, start: int) -> tuple[str | None, int]:
    """Parse `<<[-]DELIM` at start (just past `<<`); return (delimiter, index after it)."""
    i = start
    if i < len(s) and s[i] == "-":
        i += 1
    while i < len(s) and s[i] in " \t":
        i += 1
    if i < len(s) and s[i] in "'\"":
        q = s[i]
        end = s.find(q, i + 1)
        end = len(s) if end < 0 else end
        return s[i + 1 : end], end + 1
    m = re.match(r"\\?([A-Za-z0-9_.-]+)", s[i:])
    if not m:
        return None, i
    return m.group(1), i + m.end()


class Scanner:
    """Walk a shell command tracking quoting, collecting unquoted expansions and assignments."""

    def __init__(self, s: str) -> None:
        self.s = s
        self.expansions: list[tuple[str, str, list[str]]] = []
        self.assignments: dict[str, tuple[str, str]] = {}
        self.equals_words: list[str] = []

    def run(self) -> Scanner:
        self.scan(0, None)
        return self

    def scan(self, i: int, terminator: str | None) -> int:
        s = self.s
        word_start = i
        cmd_words: list[str] = []
        in_dbl_bracket = False
        pending_heredocs: list[str] = []
        paren_depth = 0

        def word_text(end: int) -> str:
            return s[word_start:end]

        def end_word(end: int) -> None:
            nonlocal in_dbl_bracket
            w = word_text(end).strip()
            if w == "[[":
                in_dbl_bracket = True
            elif w == "]]":
                in_dbl_bracket = False
            if w.startswith("=") and len(w) > 1 and not in_dbl_bracket:
                self.equals_words.append(w)
            if w:
                if not cmd_words and ASSIGN_WORD.match(w):
                    self.record_assignment(w)
                elif cmd_words and cmd_words[0] in NO_SPLIT_COMMANDS and ASSIGN_WORD.match(w):
                    self.record_assignment(w)
                else:
                    cmd_words.append(w)

        while i < len(s):
            c = s[i]
            if terminator == ")" and c == ")" and paren_depth == 0:
                end_word(i)
                return i + 1
            if terminator == "`" and c == "`":
                end_word(i)
                return i + 1
            if c == "\\":
                i += 2
                continue
            if c == "'":
                end = s.find("'", i + 1)
                i = len(s) if end < 0 else end + 1
                continue
            if c == '"':
                i = self.scan_dq(i + 1)
                continue
            if c == "#" and (i == 0 or s[i - 1] in " \t\n;&|("):
                nl = s.find("\n", i)
                i = len(s) if nl < 0 else nl
                continue
            if s.startswith("$((", i):
                i = self.skip_arith(i + 3)
                continue
            if s.startswith("$(", i):
                i = self.scan(i + 2, ")")
                continue
            if c == "`":
                i = self.scan(i + 1, "`")
                continue
            if c == "$":
                i = self.record_expansion(i, word_text(i), cmd_words, in_dbl_bracket)
                continue
            if s.startswith("<<<", i):
                i += 3
                continue
            if s.startswith("<<", i):
                delim, i = heredoc_delims(s, i + 2)
                if delim:
                    pending_heredocs.append(delim)
                continue
            if c == "\n" and pending_heredocs:
                end_word(i)
                i = self.skip_heredocs(i + 1, pending_heredocs)
                pending_heredocs = []
                word_start = i
                cmd_words = []
                continue
            if c == "(" and word_text(i).endswith("=") and ASSIGN_WORD.match(word_text(i)):
                i = self.skip_parens(i)
                continue
            if c == "(":
                if s.startswith("((", i) and not word_text(i).strip():
                    end = s.find("))", i)
                    i = len(s) if end < 0 else end + 2
                    continue
                paren_depth += 1
            elif c == ")":
                paren_depth -= 1
            if c in WORD_BREAK:
                end_word(i)
                if c in ";&|()\n":
                    cmd_words = []
                word_start = i + 1
            i += 1
        end_word(i)
        return i

    def scan_dq(self, i: int) -> int:
        s = self.s
        while i < len(s):
            c = s[i]
            if c == "\\":
                i += 2
                continue
            if c == '"':
                return i + 1
            if s.startswith("$((", i):
                i = self.skip_arith(i + 3)
                continue
            if s.startswith("$(", i):
                i = self.scan(i + 2, ")")
                continue
            if c == "`":
                i = self.scan(i + 1, "`")
                continue
            i += 1
        return i

    def skip_arith(self, i: int) -> int:
        depth = 2
        while i < len(self.s) and depth:
            depth += {"(": 1, ")": -1}.get(self.s[i], 0)
            i += 1
        return i

    def skip_parens(self, i: int) -> int:
        depth = 0
        while i < len(self.s):
            c = self.s[i]
            if c == "\\":
                i += 2
                continue
            if c in "'\"":
                end = self.s.find(c, i + 1)
                i = len(self.s) if end < 0 else end + 1
                continue
            depth += {"(": 1, ")": -1}.get(c, 0)
            i += 1
            if depth == 0:
                return i
        return i

    def skip_heredocs(self, i: int, delims: list[str]) -> int:
        lines = self.s[i:].split("\n")
        consumed = 0
        for delim in delims:
            while consumed < len(lines) and lines[consumed].strip() != delim:
                consumed += 1
            consumed += 1
        return i + sum(len(line) + 1 for line in lines[:consumed])

    def record_expansion(self, i: int, current_word: str, cmd_words: list[str], in_dbl_bracket: bool) -> int:
        s = self.s
        if i + 1 < len(s) and s[i + 1] == "{":
            end = matching_brace(s, i + 1)
            name, split = braced_name(s[i + 2 : end])
            nxt = end + 1
        else:
            m = NAME.match(s, i + 1)
            if not m:
                return i + 1
            name, split, nxt = m.group(0), False, m.end()
            if s.startswith("[@]", nxt) or s.startswith("[*]", nxt):
                split = True
        words = list(cmd_words)
        while words and words[0] in KEYWORDS:
            words.pop(0)
        no_split_context = (
            in_dbl_bracket
            or bool(ASSIGN_WORD.match(current_word.strip() or "_"))
            or (words and words[0] in NO_SPLIT_COMMANDS)
            or (words and words[-1] == "case")
        )
        list_position = bool(words) and (
            (words[0] in ("for", "select") and "in" in words) or words[0] == "set"
        )
        standalone = not current_word.strip() and (nxt >= len(s) or s[nxt] in WORD_BREAK)
        if name and not split and not no_split_context:
            self.expansions.append((name, "loop" if list_position and standalone else "arg", list(cmd_words)))
        return nxt

    def record_assignment(self, word: str) -> None:
        m = NAME.match(word)
        if not m:
            return
        name = m.group(0)
        value = word.split("=", 1)[1]
        if value.startswith("("):
            kind = "array"
        elif "$(" in value or "`" in value:
            if ONE_LINE.search(value):
                kind = "word"
            elif ALWAYS_LIST.search(value):
                kind = "list"
            elif MAYBE_LIST.search(value):
                kind = "maybe-list"
            else:
                kind = "subst"
        elif re.search(r"\s", value):
            kind = "multiword"
        else:
            kind = "word"
        self.assignments[name] = (kind, value)


def list_items(words: list[str]) -> list[str]:
    words = list(words)
    while words and words[0] in KEYWORDS:
        words.pop(0)
    if words and words[0] in ("for", "select") and "in" in words:
        return words[words.index("in") + 1 :]
    return [w for w in words[1:] if w != "--"]


def findings(command: str) -> list[tuple[str | None, str]]:
    if BYPASS in command or SPLIT_OK.search(command):
        return []
    scan = Scanner(command).run()
    out: list[tuple[str | None, str]] = [
        (
            None,
            f"`{word[:20]}` starts with `=`, which zsh expands to a command path (`echo ======` fails "
            f'with "===== not found" and ends the && chain)',
        )
        for word in dict.fromkeys(scan.equals_words)
    ]
    seen: set[str] = set()
    for name, position, words in scan.expansions:
        if name in seen:
            continue
        kind, value = scan.assignments.get(name, (None, None))
        looped = position == "loop" and len(list_items(words)) == 1
        listish = bool(LISTISH.search(name))
        reason = None
        if kind == "multiword":
            reason = f"`{name}` holds several words ({(value or '')[:60]})"
        elif kind == "list":
            reason = f"`{name}` holds a list of lines or words ({(value or '')[:60]})"
        elif kind in ("maybe-list", "subst") and (looped or listish):
            reason = f"`{name}` holds command output used as a list ({(value or '')[:60]})"
        elif kind is None and looped:
            reason = f"`for ... in ${name}` or `set -- ${name}` gets the whole value as one word"
        elif kind is None and listish:
            reason = f"`{name}` (set in an earlier command?) has a list-like name"
        if reason:
            seen.add(name)
            out.append((name, reason))
    return out


def message(found: list[tuple[str | None, str]]) -> str:
    if all(name is None for name, _ in found):
        lines = ["Blocked by the zsh guard: an unquoted word starting with `=` is zsh EQUALS expansion."]
        lines += [f"- {reason}." for _, reason in found]
        lines.append(f"Fix: quote the word (`echo '====='`) or use `echo '---'`. If deliberate, add `{BYPASS}`.")
        return "\n".join(lines)
    lines = [
        "Blocked by the zsh word-split guard. This shell is zsh with sh_word_split off, so an unquoted "
        "$VAR is passed as ONE argument (rspec/rubocop/git then see one bogus path, or `$P lint` runs a "
        "command named 'pnpm --flag')."
    ]
    for _, reason in found:
        lines.append(f"- {reason}.")
    name = next(name for name, _ in found if name is not None)
    lines.append(
        f"Fix: for a list write ${{={name}}} (or build an array `{name}=(a b c)` and pass \"${{{name}[@]}}\"; "
        f"for command output use `{name}=(${{(f)\"$(cmd)\"}})` to split on newlines). For a single argument "
        f"write \"${name}\". If the one-word use is deliberate, add `{BYPASS}` to the command."
    )
    return "\n".join(lines)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        respond("allow")
    found = findings(payload.get("command", ""))
    if found:
        respond("deny", message(found))
    respond("allow")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        print(json.dumps({"permission": "allow"}))
