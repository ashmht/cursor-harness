#!/usr/bin/env python3
"""Create a PENDING GitHub review with inline comments. Never submits it.

  post_pending_review.py --pr N --input review.json [--repo owner/name]
                         [--dry-run] [--append] [--allow-own]

Input format and comment shape: ../references/pending-review.md.
Exit 0 posted (or dry run clean), 1 validation failed, 2 GitHub call failed.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

SEVERITY_PREFIX = {"blocking": "Blocking:", "nit": "Nit:", "question": "Question:", "concern": None}
CONTRACT_LABEL = re.compile(
    r"^[\s>*_-]*(Severity|Location|Behavior|Impact|Evidence|Refutation attempted|Suggested direction)\W*:",
    re.I | re.M,
)
OPENER = re.compile(r"^(great|nice|awesome|good catch|thanks|thank you|i noticed|it looks like|just a)\b", re.I)
FENCE = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`\n]*`")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$", re.M)
HEADING = re.compile(r"^#{1,6}\s", re.M)
HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
MAX_COMMENT_WORDS = 90
MAX_BODY_WORDS = 80

ADD_THREAD = """
mutation($review: ID!, $path: String!, $line: Int!, $side: DiffSide, $startLine: Int,
         $startSide: DiffSide, $body: String!) {
  addPullRequestReviewThread(input: {pullRequestReviewId: $review, path: $path, line: $line,
      side: $side, startLine: $startLine, startSide: $startSide, body: $body}) {
    thread { id }
  }
}
"""


class GhError(Exception):
    pass


def gh(args: list[str], payload: dict | None = None):
    cmd = ["gh", "api", *args]
    if payload is not None:
        cmd += ["--input", "-"]
    proc = subprocess.run(
        cmd,
        input=json.dumps(payload) if payload is not None else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise GhError(f"gh api {' '.join(args)}: {(proc.stderr or proc.stdout).strip()}")
    out = proc.stdout.strip()
    return json.loads(out) if out else None


def gh_all(path: str) -> list:
    pages = gh(["--paginate", "--slurp", path])
    return [item for page in pages for item in page]


def diff_lines(patch: str) -> dict[str, dict[int, int]]:
    sides: dict[str, dict[int, int]] = {"LEFT": {}, "RIGHT": {}}
    hunk, old, new = -1, 0, 0
    for raw in patch.splitlines():
        m = HUNK.match(raw)
        if m:
            hunk, old, new = hunk + 1, int(m[1]), int(m[2])
            continue
        if hunk < 0 or raw.startswith("\\"):
            continue
        if raw.startswith("+"):
            sides["RIGHT"][new] = hunk
            new += 1
        elif raw.startswith("-"):
            sides["LEFT"][old] = hunk
            old += 1
        else:
            sides["RIGHT"][new] = hunk
            sides["LEFT"][old] = hunk
            old, new = old + 1, new + 1
    return sides


def prose(text: str) -> str:
    text = FENCE.sub(" ", text)
    text = TABLE_ROW.sub(" ", text)
    return INLINE_CODE.sub("code", text)


def lint(text: str, where: str, max_words: int, errors: list[str], warnings: list[str]) -> None:
    words = prose(text)
    if CONTRACT_LABEL.search(text):
        errors.append(f"{where}: finding-contract labels belong in the local report, not the comment")
    if HEADING.search(words):
        errors.append(f"{where}: no Markdown headings")
    if re.search("[\u2014\u2013]", words):
        errors.append(f"{where}: em or en dash in prose; run humanizer")
    if OPENER.match(text.strip()):
        warnings.append(f"{where}: opens with filler ({text.strip().split()[0]}...); lead with the point")
    count = len(words.split())
    if count > max_words:
        warnings.append(f"{where}: {count} words of prose (aim for under {max_words})")


def validate_comment(
    i: int,
    c: dict,
    files: dict[str, dict[str, dict[int, int]] | None],
    errors: list[str],
    warnings: list[str],
) -> None:
    where = f"comment {i} ({c.get('path')}:{c.get('line')})"
    body = (c.get("body") or "").strip()
    if not body:
        errors.append(f"{where}: empty body")
        return
    severity = c.get("severity")
    if severity not in SEVERITY_PREFIX:
        errors.append(f"{where}: severity must be one of {', '.join(SEVERITY_PREFIX)}")
    else:
        prefix = SEVERITY_PREFIX[severity]
        starts = next((p for p in SEVERITY_PREFIX.values() if p and body.startswith(p)), None)
        if prefix and starts != prefix:
            errors.append(f"{where}: a {severity} comment must start with '{prefix}'")
        if not prefix and starts:
            errors.append(f"{where}: a concern has no prefix, but this starts with '{starts}'")
    lint(body, where, MAX_COMMENT_WORDS, errors, warnings)

    path = c.get("path")
    if path not in files:
        errors.append(f"{where}: {path} is not in this PR's diff; move the finding to the review body")
        return
    sides = files[path]
    if sides is None:
        errors.append(f"{where}: GitHub has no patch for {path} (binary or too large); use the review body")
        return
    side = c.get("side", "RIGHT")
    start_side = c.get("start_side", side)
    line = c.get("line")
    if side not in sides or start_side not in sides:
        errors.append(f"{where}: side must be RIGHT or LEFT")
        return
    if not isinstance(line, int) or line not in sides[side]:
        errors.append(f"{where}: line {line} is not on the {side} side of the diff; re-anchor or use the body")
        return
    start = c.get("start_line")
    if start is not None:
        if not isinstance(start, int) or start >= line:
            errors.append(f"{where}: start_line must be an integer below line")
        elif start not in sides[start_side] or sides[start_side][start] != sides[side][line]:
            errors.append(f"{where}: start_line {start} and line {line} must sit in the same diff hunk")


def api_comment(c: dict) -> dict:
    out = {"path": c["path"], "line": c["line"], "side": c.get("side", "RIGHT"), "body": c["body"].strip()}
    if c.get("start_line") is not None:
        out["start_line"] = c["start_line"]
        out["start_side"] = c.get("start_side", out["side"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pr", type=int, required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--repo")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--append", action="store_true", help="add threads to your existing pending review")
    ap.add_argument("--allow-own", action="store_true", help="testing only: allow your own PR")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        review = json.load(f)
    if "event" in review:
        print("FAIL: input sets 'event'; this script only creates pending reviews", file=sys.stderr)
        return 1

    try:
        repo = args.repo or subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        me = gh(["user"])["login"]
        pr = gh([f"repos/{repo}/pulls/{args.pr}"])
        files = {
            f["filename"]: diff_lines(f["patch"]) if f.get("patch") else None
            for f in gh_all(f"repos/{repo}/pulls/{args.pr}/files?per_page=100")
        }
        reviews = gh_all(f"repos/{repo}/pulls/{args.pr}/reviews?per_page=100")
        threads = gh_all(f"repos/{repo}/pulls/{args.pr}/comments?per_page=100")
    except (GhError, subprocess.CalledProcessError) as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    head = pr["head"]["sha"]
    if pr["state"] != "open":
        errors.append(f"PR #{args.pr} is {pr['state']}")
    if pr["user"]["login"] == me and not args.allow_own:
        errors.append("this is your own PR: fix findings locally instead (section 6, own change)")
    if review.get("head_sha") != head:
        errors.append(f"head moved or head_sha missing: reviewed {review.get('head_sha')}, current {head}; revalidate")

    comments = review.get("comments") or []
    body = (review.get("body") or "").strip()
    if not comments and not body:
        errors.append("nothing to post: no comments and no body")
    if body:
        lint(body, "review body", MAX_BODY_WORDS, errors, warnings)
    for i, c in enumerate(comments, 1):
        validate_comment(i, c, files, errors, warnings)
        for t in threads:
            if t["path"] == c.get("path") and c.get("line") in (t.get("line"), t.get("original_line")):
                snippet = t["body"].strip().splitlines()[0][:80]
                warnings.append(
                    f"comment {i}: {t['user']['login']} already has a thread at "
                    f"{t['path']}:{c['line']} ({snippet}); skip it if it says the same"
                )

    pending = [r for r in reviews if r["state"] == "PENDING" and r["user"]["login"] == me]
    if pending and not args.append:
        errors.append(
            f"you already have pending review {pending[0]['id']} on this PR; submit or delete it "
            "in GitHub, or rerun with --append to add these threads to it"
        )
    if args.append and not pending:
        errors.append("--append given but you have no pending review on this PR")

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"FAIL: {e}")
    if errors:
        return 1

    print(
        f"OK: {repo}#{args.pr} at {head[:12]}, {len(comments)} inline comment(s), "
        f"body {'set' if body else 'empty'}, author {pr['user']['login']}"
    )
    if args.dry_run:
        print("dry run: nothing posted")
        return 0

    try:
        if pending:
            target = pending[0]
            for c in comments:
                a = api_comment(c)
                gh(
                    ["graphql"],
                    {
                        "query": ADD_THREAD,
                        "variables": {
                            "review": target["node_id"],
                            "path": a["path"],
                            "line": a["line"],
                            "side": a["side"],
                            "startLine": a.get("start_line"),
                            "startSide": a.get("start_side"),
                            "body": a["body"],
                        },
                    },
                )
            if body and not (target.get("body") or "").strip():
                gh(["-X", "PUT", f"repos/{repo}/pulls/{args.pr}/reviews/{target['id']}"], {"body": body})
            elif body:
                print("WARN: kept the existing pending review body; add yours by hand if it is still needed")
            review_id = target["id"]
        else:
            created = gh(
                ["-X", "POST", f"repos/{repo}/pulls/{args.pr}/reviews"],
                {
                    "commit_id": head,
                    "body": body,
                    "comments": [api_comment(c) for c in comments],
                },
            )
            review_id = created["id"]
        posted = gh([f"repos/{repo}/pulls/{args.pr}/reviews/{review_id}"])
        posted_comments = gh_all(f"repos/{repo}/pulls/{args.pr}/reviews/{review_id}/comments?per_page=100")
    except GhError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 2

    if posted["state"] != "PENDING":
        print(f"FAIL: review {review_id} is {posted['state']}, expected PENDING", file=sys.stderr)
        return 2
    print(f"PENDING review {review_id}: {len(posted_comments)} comment(s) on it, {len(comments)} added now")
    print(posted["html_url"])
    print("Only you can see it. Read, edit and submit it in GitHub.")
    if len(posted_comments) < len(comments):
        print(f"FAIL: expected at least {len(comments)} comment(s) on the review", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
