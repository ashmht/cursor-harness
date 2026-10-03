---
name: taste-loop
description: >-
  Personal predict -> check against reality -> log where you were wrong ->
  graduate loop for building judgment (taste) on reports, Slack messages,
  designs, product calls, and AI output. Use when the user wants to log a taste
  prediction before shipping a human-facing artifact, resolve a prediction once
  reality lands, run a periodic taste review, or graduate a recurring pattern
  into a voice rule. Triggers: "log a taste prediction", "taste loop", "taste
  check", "resolve a prediction", "review my taste log", "/taste". Also offer a
  predict entry proactively right after producing a high-stakes report or Slack
  draft in chat.
---

# Taste Loop

Taste is a discriminator trained by feedback, not a thing you read your way into. This loop trains it on your own ground truth: **predict -> check against reality -> log where you were wrong -> graduate stable patterns.**

- **Log file (single source of truth):** `~/.cursor/local/taste-log.md`. Create it from the template below if missing. It is precious data; suggest backing it up or versioning it.
- **This file** is the workflow definition. Iterating on the loop means editing this file. Iterating on your taste means the log filling up.

## Pick the verb

Infer which one the user wants; if ambiguous, state your assumption and proceed.

| Verb | When | Section it writes |
|------|------|-------------------|
| `predict` | about to ship or accept something | `## Open` |
| `check` | reality arrived for an open prediction | moves Open -> `## Closed` |
| `review` | periodic mining of closed entries | reads Closed, writes `## Graduated` |
| `graduate` | a pattern recurred 3+ times | `## Graduated` + the canonical rule file |

## predict (the 30-second capture)

The loop dies if this step has friction. Assign an immutable ID before appending
under `## Open`. Use `TASTE-YYYYMMDD-NNN`, where `NNN` is one greater than the
highest sequence already present for that date. Search the entire log, including
Closed and Graduated; never reuse or renumber an ID.

```markdown
### TASTE-YYYYMMDD-NNN — [YYYY-MM-DD] <artifact in <=4 words>
- **Type:** report | slack | design | code | product-call | ai-output
- **Prediction:** one falsifiable line — what good looks like or what will happen
- **Confidence:** <0-100>%
- **Reality check:** the ground-truth signal that will tell me I was right or wrong
```

Honesty gates:
- **Falsifiable or it doesn't count.** "It's a good report" builds nothing. "VP approves widening with zero follow-up questions" does.
- **Name the ground-truth signal now**, while you have no stake in the answer. If you can't say how you'd know you were wrong, you have a hope, not a prediction.
- **One confidence number.** It is what lets the review calibrate you later.

## check (resolve when reality lands)

Resolve by exact ID, not by artifact title or date. If the user supplies no ID
and more than one open entry could match, list the candidate IDs and ask. Move
the entry from `## Open` to `## Closed` without changing its ID, then append:

```markdown
- **Outcome:** what actually happened — the observed ground truth
- **Verdict:** RIGHT | WRONG | PARTIAL
- **Delta:** one sentence — the gap between what you predicted and what was true
```

The **Delta** line is the entire asset. Everything else is bookkeeping.

Honesty gates:
- A stretch with zero WRONG or PARTIAL means predictions are too vague or checks too generous. Tighten.
- Resolve the misses first. Wins build confidence; misses build taste.

## review (periodic — piggyback on /weekly-update)

1. Read all `## Closed` entries since the last review.
2. **Calibration:** group by confidence band; for each band, what share were RIGHT? RIGHT-rate well below stated confidence means overconfident (and vice versa).
3. **Cluster the Delta lines.** Recurring deltas are your blind spots. Name each cluster as a short noun-phrase pattern.
4. Any pattern that has recurred 3+ times and looks stable is a graduation candidate.
5. Report: calibration read, top 1-3 recurring patterns, graduation candidates.

## graduate (close the loop into your tooling)

A pattern earns promotion at 3+ recurrences. Move it out of the log so it stops being a lesson and becomes a default:

| Pattern kind | Destination |
|--------------|-------------|
| Slack / async writing tells | `~/.cursor/rules/framing.mdc` |
| Report shape / prose voice | the relevant `~/.cursor/rules/<voice>.mdc` |
| Cross-domain judgment | the user's configured knowledge base |
| Repo-specific gotcha | that repo's `.memory-bank/session-learnings.md` |

Record each promotion under `## Graduated` with date, source IDs, and destination,
so the log shows taste compounding rather than just accumulating. Source IDs make
the 3+ recurrence gate auditable.

## Hooks (so the log doesn't die)

A journal's only failure mode is forgetting to write in it. Attach capture to rituals that already exist:
- **After producing a human-facing report or Slack draft in chat:** offer one `predict` entry before moving on.
- **Session End** (per `workflow.mdc`): resolve any open predictions whose reality has landed; add predictions for what shipped.
- **/weekly-update:** run `review`.

## Log file template (create if missing)

```markdown
# Taste Log
Predict -> check against reality -> log where you were wrong -> graduate.
Loop definition: ~/.cursor/skills/taste-loop/SKILL.md

## Earned rules
<!-- One-line index of patterns that graduated out, newest first. Link the destination. -->

## Open
<!-- Predictions awaiting reality. -->

## Closed
<!-- Resolved predictions, newest first. The Delta line is the point. -->

## Graduated
<!-- [date] pattern (source IDs: TASTE-..., TASTE-..., TASTE-...) -> destination file. -->
```

## Working principles
- Predict before you peek. A call written after you know the outcome trains nothing.
- IDs are immutable: preserve them across Open, Closed, and Graduated references.
- Falsifiable or it doesn't count.
- The Delta line is the asset.
- Graduate ruthlessly. A log nobody acts on is a diary.
- Taste is the reject function; this loop sharpens it against your own ground truth.
