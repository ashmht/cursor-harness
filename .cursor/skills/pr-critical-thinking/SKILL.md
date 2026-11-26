---
name: pr-critical-thinking
description: >-
  Use at the start of an important pull-request task, and again before it is
  marked ready for review, a human reviewer is requested, or it is merged,
  including PRs the agent wrote itself. Skip on low-risk PRs (confirm with the
  user when unsure). Also use when the user says "make me think", "quiz me
  before I ship", "what did you decide for me", or "what didn't the checks
  prove". Not for a full line-by-line code walkthrough or reviewing
  someone else's PR (critical-pr-review).
---

# PR Critical Thinking

The agent did the work; the user owns the result. This skill produces questions
the user answers, not answers they read. Running every step while handing them
the answers is a violation.

## 1. Hypothesis, before the work

Check section 2 first. If the PR is **Skip (low-risk)**, confirm in one line
when unsure or borderline ("Looks low-risk — skip PR thinking and blind review
passes?") and skip sections 1, 3, and 4.

For **Full** (and non-skipped) PRs, at the start of the task before reading
code or running anything, ask in one short message:

- **Hypothesis:** what do you think the cause or change is? A bad guess is fine.
- **Verified means:** which output would convince you it's done (a test, a query
  result, a metric, a screenshot)?
- **Out of scope:** what this PR won't touch.

Log their words verbatim (section 5). Never suggest answers. "Skip" -> log
`hypothesis: skipped`. Work already done when the skill loads -> log
`hypothesis: none (asked late)`; never reconstruct one for them.

## 2. Tier

- **Skip (low-risk):** docs, `CODEOWNERS`, dev tooling, tests-only, small
  low-risk UI/config/copy/cleanup tweaks that do not touch money, ledger,
  settlement, auth/security, migrations, deletion, or live-path
  concurrency/retries. Confirm with the user in one line when unsure or
  borderline; once confirmed, skip PR thinking and blind PR review passes
  (`critical-pr-review`, `verifier`) and do not log `surrendered` (no log entry
  needed).
- **Full (follow the process):** production code touching money, ledger,
  settlement, auth/security, migrations, deletion, retries or concurrency, a
  live-path default, or core pipeline config; or substantial/multi-file
  production changes (>150 changed lines).
- **Light (optional downgrade):** when the user asks for a lighter pass on a
  non-skipped PR instead of Full or Skip (items 1, 6, and 7 only, 1 quiz
  question).

State the tier and the reason. The user may downgrade or confirm Skip; log
downgrades on non-skipped PRs.

## 3. The card, before ready-for-review

Run it after the Before Creating PR steps (build, `critical-pr-review`), so it
reuses their output. The PR stays **draft** until section 4 is done.

A card the user skims trains surrender. Full tier: under about 400 words, one
line per item, riskiest first; overflow goes in a collapsed list below the
quiz. Light tier: items 1, 6, and 7 only; add 2–5 only when one has real
content, never to fill the slot.

Post in chat, in this order:

1. **Evidence before summary.** Each command behind a claim, with its exit code
   and the output lines that show the result (`12 examples, 0 failures`, the row
   count, the balance). A claim with no command this session is listed
   **not run**. No prose summary above this list.
2. **What each green check proved, and what it didn't.** Per check: the property
   it establishes, one plausible bug it would still pass, and whether this
   session wrote the check from the same assumption as the code (then it can
   share the mistake).
3. **Decisions I made for you.** Defaults, scope cuts, reinterpreted or
   conflicting requirements, rejected alternatives, cases deliberately left
   unhandled, numbers taken on someone's word. For each: what was picked, the
   alternative, why. Full tier: at least 3, or say what you looked for.
4. **What would make this wrong.** 2 or 3 falsifiers, each with the check that
   would expose it and whether it ran. Include any number in the diff or PR body
   that doesn't tie to another number in it.
5. **Strongest case against shipping**, taken from the fresh-context review's
   findings, not re-argued by the authoring session.
6. **Quiz.** Full: 3 questions. Light: 1. Anchor each to a `path:line` at a
   risky spot (transaction boundary, ordering, default, amount or sign, nil
   path, an operational step a human must do, a caller outside the diff). Ask
   them to apply the change to a case the PR doesn't mention. No answers, hints,
   or "expected answer" in the card or the PR body.
7. **Your turn.** (a) Your hypothesis against what happened, one line. (b) One
   thing nothing checked. (c) Would you defend this to the person who maintains
   it? Yes or no, and why.

## 4. Grade honestly

Grade answers honestly: one probe on a vague answer; "lgtm", "ship it", "the
agent did it", and silence are not answers. Quote the user's answers verbatim. After they answer, show what the
code actually does for each question and mark it **pass** or **gap**. A gap that
exposes a code or PR-body bug is a finding: fix it before ready.

Mark ready or request review only when every question is a pass or the user
explicitly accepts a named gap. If they say "skip, ship it", comply once, log
`surrendered`, and don't argue it again.

## 5. Log

Optionally record the entry in `.memory-bank/pr-thinking-log.md` (newest first):

```markdown
### <branch> — <PR link | no PR yet>
- Tier: full | light (downgraded: yes/no)
- Hypothesis: "<verbatim>" | skipped | none (asked late)
- Verified means: "<verbatim>"
- Hypothesis vs reality: "<their line>"
- Quiz: <n> pass, <n> gap (<topic>) | surrendered
- Unchecked: "<their words>"
- Would defend: yes/no — "<their reason>"
```

A gap topic seen three times should become a mechanism (a test, linter check,
or hook), not another prose reminder.

## Stop signals

| You are about to | Instead |
|---|---|
| write "tests pass" or "verified" with no command and output | paste the command, exit code, and result line |
| put the answer next to a quiz question, or explain it in the PR body | delete it; reveal only after the user answers |
| write a hypothesis for the user | log `none (asked late)` |
| mark ready because CI is green | finish section 4 first |
| count "looks good" as a pass | probe once, then log a gap or `surrendered` |
| silently skip a risky PR because it is small | small changes touching money, auth/security, migrations, deletion, or live defaults stay Full; only confirm-skip genuinely low-risk PRs |
| run hypothesis/card/quiz on a clearly low-risk PR without checking | propose Skip in one line and skip PR thinking + blind review passes once confirmed |
| pad a Light card with decisions and falsifiers to look thorough | drop the empty sections |
