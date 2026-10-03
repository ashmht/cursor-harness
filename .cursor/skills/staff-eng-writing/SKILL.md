---
name: staff-eng-writing
description: >-
  Write concise, decision-focused engineering documents using BLUF, the Minto
  Pyramid, just-in-time context, and audience-aware detail. Use for RFCs,
  proposals, status updates, escalations, risk registers, alignment documents,
  and launch-readiness plans.
---

# Staff Engineer Writing

Write documents that drive decisions, not documents that demonstrate effort.

## Route before drafting

- Use `socratic-doc-writer` when the reader, decision, recommendation, or
  trade-off is unresolved.
- Use this skill when the reasoning is settled and the artifact needs structure.
- Apply a destination adapter only after the content is stable.

## Before writing

Answer three questions:

1. Who is the primary reader?
2. What do they decide or do after reading?
3. What is the minimum evidence they need?

## Core techniques

### BLUF

The first paragraph contains the recommendation, status, or ask. If the reader
stops after two sentences, they should know what happened and what is needed.

### Minto Pyramid

Structure longer arguments top-down:

1. Governing thought: the actionable conclusion.
2. Up to three independent reasons.
3. Evidence needed to make those reasons credible.

Merge overlapping reasons. Move non-decision-changing detail to an appendix.

### Just-in-time context

Put context where the reader needs it. Avoid historical openings. In an
escalation, lead with the problem and impact. In an RFC, lead with the
recommendation and key trade-off. In a status update, lead with state and what
changed.

### Audience altitude

- Two-minute reader: summary, risk, effort, and decision.
- Ten-minute reader: architecture, phases, owners, and open questions.
- Implementer: contracts, paths, data model, rollback, and tests.

The executive summary must be sufficient on its own.

## Document templates

### RFC

```markdown
# RFC: [Decision title]

## Recommendation
[Decision and why it wins.]

## Problem
[Current behavior, evidence, and cost of doing nothing.]

## Goals and non-goals

## Proposal

## Alternatives
| Option | Effort | Risk | Trade-off |
|---|---|---|---|

## Risks
| Risk | Probability | Impact | Mitigation | Owner |
|---|---|---|---|---|

## Decision
[Who decides what, by when, and the default if silent.]

## Open questions

## Appendix
```

### Status update

```markdown
**Status:** On track | At risk | Blocked
**Progress:** [Delivered outcome]
**Risk:** [Risk → impact → mitigation or ask]
**Next:** [Deliverable and date]
**Decision needed:** [Question, options, recommendation, or None]
```

### Escalation

```markdown
**Problem:** [One quantified sentence]
**Risk:** [Default outcome if nothing changes]
**Evidence:** [Two or three verified facts]
**Options:** [Effort, risk, and trade-off]
**Recommendation:** [Choice and deadline]
```

### Launch readiness

```markdown
## Launch readiness: [Feature]
**Owner:** [Name]
**Decision date:** [Date]
**BLUF:** [Ready, blocked, or ready with accepted risk]

### Criteria
| Criterion | Status | Evidence | Owner |
|---|---|---|---|

### Risks and tripwires
| Risk | Threshold | Action | Owner |
|---|---|---|---|

### Rollback
[Steps, authority, and expected duration.]
```

## Risk writing

A risk is a decision:

1. Quantify the affected population or consequence.
2. Name the decision deadline.
3. State the default outcome.
4. Present options and a recommendation.

Risk without numbers is noise. Risk without options is a complaint.

## Hostile Clarity review

Before publishing:

- Does sentence one tell the reader what to do?
- Are owner, date, decision, and default explicit?
- Are risks quantified and paired with options?
- Can the recommendation be re-derived from constraints and evidence?
- Is the detail appropriate for the named reader?
- Can any section be deleted without weakening the decision?

Revise every failed check.
