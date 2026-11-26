# Pending review on another person's pull request

A pending review is a draft on GitHub. Only the user who made it can see it,
and nobody is notified until they press Submit. That makes it the right
hand-off: the agent writes and anchors the comments, and the user reads,
edits and submits.

## Comment shape

One finding per comment, three short paragraphs at most:

1. **The point.** What goes wrong, in the author's terms, in one sentence.
   Prefix `Blocking:`, `Nit:` or `Question:` when the finding is one of
   those. A concern gets no prefix, because it is the default.
2. **The evidence.** One to three sentences: the `path:line` that proves it,
   the caller or test that is missing, a measured number, a PR it repeats.
3. **The fix.** One sentence that starts with what to do, or a
   ```` ```suggestion ```` block when the change fits the anchored lines.

Keep each comment under about 90 words of prose; code, suggestion blocks
and tables don't count. Write it as the user, in the first person. A
finding you could not confirm is a question ("Does `retry!` reach this when
the lock is held?"), not a claim.

The finding contract labels (`Severity:`, `Behavior:`, `Impact:`,
`Evidence:`, `Refutation attempted:`, `Suggested direction:`) stay in the
local report. Include the refutation only when the author needs it ("`call`
rescues `Timeout`, but not `Faraday::ConnectionFailed`").

A good one:

```markdown
Blocking: an external collaborator who isn't on the default team gets an empty
200. The controller admits collaborators (`reports_controller.rb:191`) and
`ReportQuery` counts their items (`report_query.rb:598-606`), but `index` only
applies `VisibleTeam.restrict`.

Include `CollaboratorAccess.item_ids_for(user:, org:)` when
`!visible_team.everyone?`, plus a test for the collaborator case.
```

Run humanizer in rewrite mode over every comment and the review body. They
are messages to the PR author, so its message rules apply: answer first, no
labeled sections, no flattery, no em dashes. Use GitHub Markdown, not Slack
mrkdwn. Keep identifiers, numbers and code exactly as written.

## Review body

One to three sentences: the verdict ("Two blocking issues, both in the retry
path; the rest are nits."), then any finding that cannot anchor to a diff
line, with a permalink at the head SHA
(`https://github.com/<owner>/<repo>/blob/<sha>/<path>#L<n>`). Don't repeat
the inline comments and don't add headers.

## What to post

- Every blocking finding and every concern that survived section 5.
- At most three nits. Fold the rest into one body sentence or drop them.
- Nothing an existing thread already says. When an open thread covers the
  same finding and you have new evidence, put that evidence in the review
  body and name the thread.

## Input file

```json
{
  "head_sha": "<the head SHA you reviewed>",
  "body": "Two blocking issues, both in the retry path; the rest are nits.",
  "comments": [
    {"path": "app/x.rb", "line": 42, "severity": "blocking", "body": "Blocking: ..."},
    {"path": "app/x.rb", "start_line": 50, "line": 54, "severity": "concern", "body": "..."},
    {"path": "app/y.rb", "line": 7, "side": "LEFT", "severity": "nit", "body": "Nit: ..."}
  ]
}
```

`line` is the file line on that side of the diff: `RIGHT` (default) for
added and context lines, `LEFT` for removed ones. A multi-line comment adds
`start_line` in the same hunk. `severity` is `blocking`, `concern`, `nit` or
`question`.

## Posting

```bash
S=~/.cursor/skills/critical-pr-review/scripts/post_pending_review.py
python3 "$S" --pr <n> --input /tmp/review-<n>.json --dry-run
python3 "$S" --pr <n> --input /tmp/review-<n>.json
```

The script refuses to post when the head moved since `head_sha`, a comment
is not on a diff line, a body breaks the shape above, or the PR is the
user's own. It never sends an `event`, so the review stays pending, and it
reads the review back to confirm `PENDING` and the comment count. If you
already have a pending review on the PR, it stops and names it; `--append`
adds the new threads to that review and leaves its existing comments and
body alone.
