---
name: skill-adoption-eval
description: Measures whether an agent skill or workflow creates team leverage using named adopters, repeat usage, task outcomes, quality, time, and cost. Use when evaluating skill adoption, AI productivity claims, team-agent usage, or multiplier evidence.
---

# Skill adoption eval

Evaluate adoption, not artifact volume. A skill existing, being installed, or
being mentioned is not proof that it changed team outcomes.

## Inputs

Infer these from the request and available evidence. Ask only for missing inputs
that would materially change the result.

- Artifact: skill, runbook, agent, MCP tool, or recurring workflow
- Intended users and teams
- Task the artifact should improve
- Evaluation window
- Baseline window or comparison cohort
- Candidate outcome metric

Default to four weeks before and four weeks after adoption. Use a shorter window
only when launch timing or data retention requires it, and disclose the limit.

## Workflow

### 1. Define the claim before gathering data

Write one falsifiable sentence:

> Using [artifact] for [task] changes [metric] from [baseline] to [target] by
> [date], without worsening [quality guardrail].

Reject claims that name no task, metric, target, date, or guardrail.

### 2. Verify the artifact is team-operable

Check:

- Canonical location is shared, not only in the author's home directory.
- Trigger and inputs are documented.
- Another engineer can run it without the author.
- Ownership and feedback path are named.
- Output can be audited.

If these fail, classify the artifact as `personal` and stop short of a Team
pillar claim.

### 3. Gather evidence

Use the smallest set of sources that can verify the claim:

- Source control: merged artifact, contributors, references from other
  packages, follow-up changes by non-authors
- Public Slack: named users reporting use, outcomes, failures, or asking for
  changes
- Buildkite or workflow telemetry: runs, unique actors, success rate, duration
- Jira or incident records: task closure, MTTR, recurrence, escaped defects
- Cost systems: model, token, or infrastructure cost per successful task
- Before-and-after samples: manual task time and quality versus assisted task

Public Slack is allowed. Request consent before searching private channels or
DMs.

Do not treat downloads, page views, reactions, copied prompts, or the author's
own runs as adoption.

### 4. Classify adoption

Use the highest stage supported by evidence:

1. **Available**: shared artifact exists.
2. **Tried**: at least one non-author completed one real task.
3. **Recurring**: at least two non-authors used it in two separate weeks.
4. **Team-owned**: non-authors contribute fixes or depend on it in a standard
   workflow.
5. **Cross-team**: another team and its agents use it without the author
   operating the workflow.

Report human adopters and agent invocations separately. Do not multiply them
into a synthetic "leverage" number.

### 5. Measure outcomes

Prefer one primary metric and one quality guardrail.

Primary metric examples:

- Median triage minutes per case
- PR time-to-first-actionable-review
- Incident MTTR
- Engineer-hours per migration
- Cost per successful review or investigation
- Weekly successful tasks per engineer

Quality guardrail examples:

- Escaped defects
- Finding precision confirmed by a human
- Reopened tickets
- Rollbacks or change-failure rate
- False-positive rate
- Tasks requiring author rescue

Every quantitative claim must include:

- Baseline and post-adoption value
- Sample size
- Time range
- Data source
- Important exclusions

Never claim "10x," dollars saved, or avoided GMV without measured inputs and
shown arithmetic.

### 6. Produce the evaluation

Lead with one of:

- **Adopted with measured outcome**
- **Adopted, outcome not yet measured**
- **Tried, not recurring**
- **Available, no verified adoption**
- **Insufficient evidence**

Then provide:

1. **Verdict**: adoption stage, primary metric movement, and confidence
2. **Evidence**: named adopters, dates, tasks, and source links
3. **Guardrail**: quality result and any regressions
4. **Limits**: missing telemetry, selection bias, or small samples
5. **Next experiment**: one action, owner, metric, and decision date
6. **Career evidence paragraph**: ready to paste into a private review record

Use a Cursor Canvas when the evaluation contains a timeline, more than five
evidence rows, or multiple quantitative comparisons.

## Career evidence paragraph

Use this shape without inflating the claim:

> I moved [artifact] from [starting stage] to [adoption stage]. [N] engineers
> across [teams] used it for [task] during [window]. [Primary metric] changed
> from [baseline] to [result] across [sample size], while [guardrail] remained
> at [result]. [Named non-author] now owns or contributes to [durable mechanism].

If adoption or outcome is unverified, say so explicitly and omit the claim.

## Cadence

- Weekly: record new adopters, runs, failures, and rescue work.
- Monthly: recompute the primary metric and guardrail.
- Quarterly: decide whether to invest, revise, transfer ownership, or retire.

When the user supplies a career rubric, calibrate the evidence paragraph against
that rubric without overstating adoption or outcomes.
