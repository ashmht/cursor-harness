---
name: testing-skills
description: >-
  Use when creating or editing an agent skill, Cursor rule, AGENTS.md or
  CLAUDE.md section, or system prompt, before relying on it, or when an agent
  keeps ignoring or misapplying an existing skill.
---

# Testing Skills

A skill is untested until an agent without it did the wrong thing and an agent
with it did the right thing.

## The description decides whether the body gets read

- Write only trigger conditions: situations, symptoms, and phrases the user
  says. Start with "Use when".
- Never summarize the workflow in the description. Agents follow a summary
  instead of opening the body: a description saying "code review between tasks"
  produced one review when the body required two, spec then quality.
- Name the problem, not one technology's symptom, unless the skill is
  technology-specific.
- Add "Not for ..." naming the sibling skill when two skills could match the
  same request.
- Third person, under about 500 characters.

## Test cycle

1. **Baseline.** Fix at least two realistic scenarios and one boundary or
   positive-control case before any run. Run each in a fresh isolated subagent
   without the skill and record its result. Do this even when the requester
   names the cause or asks to skip testing; a treatment-only check proves no
   lift.
2. **Write** the smallest skill that fixes those observed failures. Skip
   sections for failures you did not see.
3. **Re-run** the same scenarios with the skill in the subagent's prompt.
   Prevent cross-contamination so the baseline cannot see the skill or notes,
   and grade blind on a separate model family when possible.
4. **Close loopholes.** A new excuse gets an explicit counter, then re-run.

If every baseline passes, report no measured lift. A requested policy may still
be documented as unvalidated, but do not call the skill tested or validated. For
discovery failures, run the same trigger and boundary prompts before and after
changing the description.

Run the full cycle for discipline skills (verification, test-first, review
gates), always-applied rules, and edits to either. For reference skills, a
retrieval check is enough: can a fresh agent find the right section and apply
it?

| Skill type | Test with |
|---|---|
| Discipline: rules an agent is tempted to skip | Pressure: time ("prod is down"), sunk cost ("you already wrote it"), authority ("the lead said skip tests"), then all three combined |
| Technique: how-to | A case the skill never mentions, and a case with missing information |
| Reference: facts and commands | Can the agent find the answer and use it correctly? |

## Hardening discipline skills

- Forbid the specific workarounds you observed, not just the rule.
- Keep a table of the excuses agents actually gave, each with its answer.
- Add a short stop-signals list the agent can check itself against.
- Say early that following the letter while dodging the purpose is a violation.

## Budget

- Always-applied rules load into every chat. Keep additions to a few lines and
  point to a skill for detail.
- Skills load on demand. Aim for under about 500 words and move heavy reference
  to a sibling file linked from the body.
- Reference other skills by name instead of pasting their content.
- One excellent example beats several mediocre ones.

## Avoid

- Narratives ("in an earlier session we found...").
- Flowcharts for linear steps. Use numbered lists; keep flowcharts for a
  non-obvious decision.
- Writing several skills and shipping them all untested.
