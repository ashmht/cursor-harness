---
name: loop-docs-sweep
description: >-
  Documentation sweep loop — review codebase against docs (README, Google Doc
  source paths, HTML, runbooks), update stale material, verify commands and
  links, record no-change when clean. Use for doc maintenance, post-PR doc
  drift, scheduled /loop cadence, or when the user says "docs sweep", "sync
  docs with code", or "documentation pass".
---

# Loop: Docs Sweep

**Source:** [FF Loop #001](https://signals.forwardfuture.ai/loop-library/loops/overnight-docs-sweep/)

## Copy the loop

```
Whenever a documentation pass is needed for [package/path/doc set]:

1. Review implementation changes since the last documentation pass
   (git log, merged PRs, or user-specified window).

2. Compare documentation against current code, configuration, commands,
   and behavior that now ships:
   - README.md / package-local README files / memory-bank entries
   - Google Doc source-of-truth paths (if user provides doc ID or path)
   - HTML reference pages in a user-specified wiki or the repository
   - Runbooks and ownership/contribution rules

3. Update only stale material. Do not rewrite accurate docs for activity.

4. Verify:
   - Commands in docs still run (or mark as requiring env setup)
   - Links resolve (Jira, GitHub, Notion labels)
   - Examples match current file paths and APIs
   - Diagrams reflect current architecture

5. If actionable drift found:
   - Fix docs in place OR open a PR with documentation-only changes
   - Summarize: what drifted, what was fixed, what was verified

6. If no actionable drift:
   - Stop without making changes
   - Record no-change result with date and scope checked
```

## Verify / stop

**Documentation matches the current implementation.**

Finish with a reviewable PR or a recorded no-change result with evidence of what was checked.

## When to use

- After merging architecture or documentation changes
- Weekly maintenance: `/loop 1w Run loop-docs-sweep on [package/path]`
- Before publishing an updated Google Doc sourced from repo

## Scheduled invocation

```
/loop 1w Run loop-docs-sweep on [path]. Check README, OWNERS.gh, memory-bank. Record no-change if clean.
```

## Memory

`/tmp/docs-sweep-{scope}.md` — last run date, files checked, drift found, PR link or no-change.
