---
name: loop-concept-explainer
description: >-
  Concept explainer loop — teach how something works with Julia Evans pedagogical
  voice, concrete stack examples, quality-streak review passes, Fowler Bliki
  sidebars for terms, humanizer finish. Use when explaining a concept, writing
  onboarding docs, internal tutorials, "how does X work", README walkthroughs,
  or when the user says "concept explainer loop" or "explain this for new hires".
---

# Loop: Concept Explainer

**Based on:** FF #009 Quality streak (N review passes before ship)

## Copy the loop

```
Explain [concept] for [audience: new hire | on-call | XFN partner | agent context].

PHASE 1 — SCOPE
- One sentence: what the reader can do after reading.
- One concrete example from the target stack (name the service, file, or metric).
- What this is NOT (distinguish from adjacent concepts).

PHASE 2 — DRAFT (Julia Evans register: conversational opener, one traced example, numbered mistakes)
Structure:
1. Conversational opener — no thesis statement; acknowledge what's confusing
2. What it is (plain language, 2-3 short paragraphs)
3. Why it matters in this codebase
4. How it works — one traced example (for example HTTP → service → database)
5. Common mistakes (numbered)
6. Checklist or template the reader can reuse
7. What to read next (links on labels)

Citation requirement:
- Cite every factual or behavioral claim to a repo path + symbol/line, runbook,
  metric/query, or durable source link.
- Put the citation next to the claim when practical; otherwise add a Sources
  section that maps each claim to its evidence.
- Label inference as inference. Remove claims that cannot be verified.

For load-bearing terms, add Fowler Bliki boxes:
  "**Term** is … It differs from **AdjacentTerm** because …"

PHASE 3 — QUALITY STREAK (FF loop #009, N=2)
Pass 1 — Reader test: can a [audience] follow the traced example without prior context?
  On fail: document gap, fix, reset streak.
Pass 2 — Accuracy test: every claim verifiable against repo, runbook, or metric.
  On fail: document gap, fix, reset streak.
Stop after 2 consecutive passes.

PHASE 4 — HUMANIZE
Apply this checklist. Open the humanizer skill only if a pattern is unclear:
- Remove AI vocabulary, stacked hedges, and em dashes.
- Vary sentence length.
- Do not invent numbers, names, or anecdotes.
- The Julia Evans voice wins over a generic tone.

Deliver as: markdown file | wiki section | HTML. Use the HTML doc loop only
when the page needs a visual layout this checklist does not specify.
```

## Verify / stop

**A [audience] reader can trace one real example and reuse the checklist without help.**

- 2 consecutive quality passes on reader test + accuracy test
- Every factual or behavioral claim has a citation, or is explicitly labeled inference
- Every failure during drafting was fixed (not waived)
- Fowler sidebars distinguish terms from adjacent concepts
- humanizer pass complete

## When to use

- Onboarding ("how does request expiration work across these services")
- Memory bank / agent context that must survive re-reads
- XFN partners who need mechanics, not opinions

## Deeper references

The phase checklist above is enough. Open one reference only when it does not
answer the question in front of you:

- julia-evans-voice, for the tutorial register
- fowler-voice, for a Bliki box
- humanizer, for a pattern the checklist does not name
- technical-writing, only when the page is published outside the team

## Memory

Optional: `/tmp/explainer-{concept}.md` — audience, traced example path, pass log.
