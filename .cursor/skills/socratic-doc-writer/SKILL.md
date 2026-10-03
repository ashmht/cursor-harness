---
name: socratic-doc-writer
description: >-
  Write documents through bounded Socratic interrogation. Surface the reader,
  decision, assumptions, alternatives, constraints, and reversal conditions
  before producing a decision-focused draft. Use for "write a doc", "draft an
  RFC", "help me write", or `/doc`.
---

# Socratic Document Writer

Capture reasoning, not just conclusions.

## Flow

```text
Interrogate → Gate check → Confirm → Draft → Hostile Clarity review
```

## 1. Interrogate

Ask no more than eight questions, grouped into one message. Always establish:

1. What type of document is this?
2. Who is the primary reader?
3. What do they decide or do after reading?
4. What do they already know?

Choose the remaining questions from:

- Why this approach over the obvious alternative?
- What happens if nothing changes?
- What would change your mind?
- What is explicitly out of scope?
- What would a smart opponent challenge?
- Which assumption is least supported?
- Is the success metric falsifiable?
- What is the cost of being wrong versus learning more?
- What is the default if nobody decides?

Do not draft or advocate during this phase. Follow up once on a vague answer,
then record the unresolved item as an open question.

## 2. Gate check

Do not draft until all three gates pass:

- A specific reader or decision-making role is named.
- The action or decision after reading is explicit.
- At least one alternative or reason not to act is identified.

If three or more sections would be unknown, produce a research plan instead of
pretending the document is ready.

## 3. Confirm

Restate:

```markdown
- Reader and existing context:
- Decision or goal:
- Recommendation or approach:
- Hard constraint:
- Main trade-off:
- Reversal condition:
- Assumptions:
```

Wait for confirmation only when a mismatch would materially change the draft.

## 4. Draft

Use `staff-eng-writing` for the artifact shape. Apply these invariants:

- Decision first, context second.
- Tables for three or more same-shaped items.
- One canonical artifact, updated in place.
- Exact owners and dates.
- Honest alternatives and trade-offs.
- Unknowns remain visible.

Decision documents require alternatives, what is being given up, reversal
conditions, and risks. Execution documents require scope, interfaces, tests,
rollout, rollback, and open questions. Status updates contain only current
state, changed evidence, next action, and decisions.

## 5. Hostile Clarity review

Check:

1. Can the reader reconstruct the plan from the first screen?
2. Where must the reader guess?
3. Is the decision a concrete question with options and recommendation?
4. Can any section be removed without losing reasoning?
5. Does the decision follow from constraints and evidence?
6. Is the altitude right for the named reader?

Return a pass or list exact failures and revise them.
