---
name: loop-design-doc
description: >-
  Design doc loop — Socratic interrogation, BLUF draft, devil's-advocate stress-test,
  staff-eng structure, Larson/Fowler voice, humanizer, and optional destination adapter.
  Use when writing an RFC, tech spec, ADR, alignment doc, architecture decision,
  buy-in doc, or when the user says "design doc loop", "run the RFC loop", or
  "architecture doc with adversarial review".
---

# Loop: Design Doc

**Based on:** FF #024 Devil's-advocate + #002 Architecture satisfaction (when design ships as code)

## Copy the loop

```
Take [topic] and produce a decision-ready design document.

PHASE 1 — INTERROGATE (read ~/.cursor/skills/socratic-doc-writer/SKILL.md)
Ask and answer before drafting:
- Doc type: RFC | Tech Spec | ADR | Alignment
- Who reads this? Name the person, not "stakeholders."
- What do they decide after reading? One sentence.
- What do they already know? Sets altitude.

PHASE 2 — DRAFT (read ~/.cursor/skills/staff-eng-writing/SKILL.md)
- BLUF in the first paragraph: recommendation or ask before rationale.
- Minto pyramid for trade-offs: answer → grouped reasons → evidence.
- Minimum material for the decision; everything else → appendix.
- Voice: `~/.cursor/rules/larson-voice.mdc` (essay) for RFC/alignment;
  `~/.cursor/rules/fowler-voice.mdc` (Article) for tech spec and (Pattern) for ADR.

PHASE 3 — DEVIL'S ADVOCATE (read ~/.cursor/skills/loop-devils-advocate/SKILL.md)
Initialize /tmp/redteam-{projectname}.md.
Critic sub-agent: strongest evidence-backed case that the design is wrong.
For each objection log: evidence, impact, status (open | resolved | accepted).
Builder: fix and verify, OR accept with explicit rationale under stated criteria.
Critic may reopen weak answers. Merely answering in the log does not resolve.
Repeat until no new high-impact objection and every logged item is resolved or accepted.
If same unresolved objections repeat two rounds without progress → report stalemate honestly.

PHASE 4 — HUMANIZE
Run humanizer on all prose. Read framing.mdc anti-AI guardrails.

PHASE 5 — SHIP (if requested)
- Google Doc → use a user-installed destination adapter; otherwise deliver
  canonical Markdown ready to paste or import
- Notion / markdown → deliver file path + summary for reviewer

Finish with: BLUF, decision ask, objection log path, open risks, suggested reviewers.
```

## Verify / stop

**The design survives adversarial review and the reader can decide in under five minutes.**

- BLUF states recommendation or ask in paragraph one
- Every high-impact objection in `/tmp/redteam-{projectname}.md` is resolved or explicitly accepted with evidence
- No new business logic smuggled in as "documentation only" unless PR title says so
- humanizer pass complete; no AI tells in final prose

## When to use

- Architecture redesign (FC/IS, service boundaries, migration plans)
- Cross-team alignment before build
- Staff-review gates (hot path, FF ramp, data model changes)

## Skills to read (in order)

1. `~/.cursor/skills/socratic-doc-writer/SKILL.md`
2. `~/.cursor/skills/staff-eng-writing/SKILL.md`
3. `~/.cursor/rules/larson-voice.mdc` or `~/.cursor/rules/fowler-voice.mdc`
4. `~/.cursor/skills/humanizer/SKILL.md`
5. An optional destination adapter, if installed and explicitly requested

## Memory

Track progress in `/tmp/redteam-{projectname}.md` and optionally `/tmp/design-doc-{projectname}.md` (outline, BLUF, reviewer list).
