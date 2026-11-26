---
name: systematic-debugging
description: >-
  Load FIRST (before any domain skill) whenever something is wrong and you are
  about to investigate or fix it: a test/CI/build failure, flake, unexpected
  code or data behavior, a previous fix that did not stick, error spike, "why
  is this failing", "root cause", "debug", "investigate", "what's broken",
  "still failing", "regression", or stop-guessing. Also load when the user
  pastes a stack trace, red CI, or a wrong number from a query.
---

# Systematic Debugging

No fix until the root cause is known. A fix that makes the symptom go away
without an explanation is a guess, and guesses compound.

```text
- [ ] 1. Root cause: read, reproduce, check changes, gather evidence, trace back
- [ ] 2. Pattern: find working code that does the same thing and diff it
- [ ] 3. Hypothesis: one written theory, one minimal test
- [ ] 4. Fix: failing test first, one change, verify
```

Do not start a phase until the previous one is done. If a fix is already on the
table before phase 1 is finished, set it aside.

## 1. Root cause

1. **Read the whole error.** Full stack trace, every warning, the exact file,
   line, and error code. The answer is often already there.
2. **Reproduce it.** Write down the exact command or steps. If it does not
   reproduce reliably, gather more data instead of guessing.
3. **Name the tree.** Confirm which branch and worktree you are in, and which
   checkout or container the running service is bound to
   (`git rev-parse --abbrev-ref HEAD`, `git status`). A reproduction in the
   wrong worktree proves nothing.
4. **Check what changed.** `git diff`, `git log -p -- <path>`,
   `git log -S'<symbol>'`, dependency and config changes, environment
   differences between where it works and where it fails.
5. **Instrument the boundaries.** When the path crosses components (CI to build
   to deploy, controller to service to worker to database, frontend to API),
   log what enters and leaves each boundary once, then read where the data
   first goes wrong. Investigate only that component.
6. **Trace backward.** From the bad value, ask what produced it and who called
   that, until you reach the source. Fix at the source, not where it surfaced.

Phase 1 is done when you can state what is wrong and why, citing `path:line`.

## 2. Pattern

1. Find code in the same repo that does the same thing and works (a sibling
   handler, another resource's serializer, another test that passes).
2. If you are applying a pattern or reference implementation, read it
   completely before adapting it.
3. List every difference between working and broken, however small. Do not rule
   one out as "can't matter" without checking.
4. List what the broken code depends on: config, env vars, feature flags, data
   shape, ordering, timing.

## 3. Hypothesis

1. Write one sentence: "I think X is the root cause because Y."
2. Make the smallest change that would confirm or refute it. One variable at a
   time.
3. Confirmed: go to phase 4. Refuted: revert, form a new hypothesis. Never stack
   a second change on an unconfirmed first.
4. If you do not understand something, say so and go find out. Do not paper
   over it.

## 4. Fix

1. **Failing test first.** Write the simplest reproduction as an automated test
   using the repository's test runner (or a minimal script under `tmp/` if no
   framework fits). Test the real code; mock only what cannot run. Watch it
   fail for the reason you expect, not a typo or load error.
2. **One change** that addresses the root cause. No bundled refactors or
   "while I'm here" edits.
3. **Verify.** The new test passes, related tests still pass, and the original
   symptom is gone when reproduced the same way as in phase 1.
4. **Prove the test catches the bug.** Revert the fix, rerun the test and see
   it fail, restore the fix, see it pass. A test that passes either way proves
   nothing.

## Three strikes

Count fix attempts. After a failed fix, return to phase 1 with what you learned.

After **three** failed fixes, stop guessing. Each fix revealing a new problem
somewhere else, or a fix that needs a large refactor, means the design is
wrong, not the hypothesis. Go back to phase 1 and find the root cause the
earlier fixes missed.

- **Root cause confirmed, and the user asked for another attempt:** make the
  root-cause fix. Say plainly that the earlier fixes treated the symptom, and
  why this one is different.
- **No confirmed root cause, or the fix needs a redesign:** write the state to
  `.agent-progress.md` under a `Blocker:` entry (what was tried, what each
  attempt showed, the likely structural cause) and ask the user before a fourth
  attempt.

Never make a fourth attempt that repeats the earlier approach, such as a longer
sleep or another special case.

## Stop signals

Return to phase 1 if you notice any of these:

- "Quick fix for now, investigate later."
- "Let me just try changing X."
- Several changes before running the test.
- Skipping the test because you will check manually.
- "It's probably X" without evidence that it is X.
- Adapting a pattern you only skimmed.
- Listing fixes before tracing the data flow.
- The user asks "is that actually happening?", "stop guessing", or "are we
  stuck?"

## Genuinely external causes

If the investigation shows the cause is environmental, timing-dependent, or in
a third party, say what you checked, add handling that fits (retry, timeout,
clear error), and add logging so the next occurrence leaves evidence. Most "no
root cause" conclusions are an incomplete phase 1, so check that first.

For a flaky or timing-dependent test, wait on the condition (poll until the
expected state appears, with a timeout) instead of adding or lengthening a
sleep.

## Report

```markdown
**Root cause:** <one sentence> (`path:line`)
**Evidence:** <the log, query, diff, or test output that shows it>
**Fix:** <the single change and why it addresses the cause>
**Verified by:** <test name and command, plus the reproduction re-run>
**Not verified:** <anything you could not confirm>
```
