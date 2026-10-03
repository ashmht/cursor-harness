---
name: cross-collab-project-contract
description: Defines and reviews agreements between independently accountable teams or functions when a mismatch in behavior, data meaning, interface semantics, risk acceptance, or launch ownership could cause customer, financial, compliance, or launch harm. Use to create, audit, change, or assess readiness of a cross-collaboration contract. Do not use for routine multi-service implementation, single-owner work, ordinary PRD drafting, or investigations that do not require a new agreement.
---

# Cross-collaboration project contract

**A cross-collaboration project contract** is the set of explicit, approved
agreements that lets independently accountable parties implement and launch one
project without silently relying on different assumptions. It locks the
load-bearing details, not every implementation choice or edge case.

The contract is normally a section or decision ledger in an existing
authoritative artifact. Do not create a second canonical document unless the
owners explicitly choose it and record which older artifacts it supersedes.

This skill is not a generic design-doc writer. It owns cross-boundary agreement,
decision evidence, and readiness. Use `loop-design-doc` to author the underlying
RFC or architecture proposal, then return here for agreement review.

## Select an operating mode

Choose one mode from the request and available artifacts. Ask the user only when
the choice changes the work materially.

- `CREATE`: establish the first shared agreement before implementation.
- `AUDIT`: find contradictions, unsupported assumptions, stale evidence, and
  missing ownership in existing artifacts.
- `CHANGE REVIEW`: assess one proposed contract change and its affected
  requirements, scenarios, tests, metrics, owners, and launch gates.
- `READINESS REVIEW`: issue a readiness verdict from existing evidence.

`CREATE` produces the full minimum contract. Other modes update or report only
the affected sections. Do not regenerate unaffected material.

## Required outcome

Every mode identifies:

1. The authoritative artifact and accountable maintainer.
2. Decisions locked and decisions still open.
3. Requirements and affected scenarios.
4. Decision owners and attributable approval states.
5. The next safe step.

Only `READINESS REVIEW` issues a readiness verdict. Do not call the project
ready while a material decision is implicit, disputed, unsupported, stale, or
approved only by someone speaking for another function.

## Procedure

### 1. Establish the project boundary

Identify:

- The user or business outcome.
- Independently accountable parties and the decisions they share.
- The irreversible or money-moving actions.
- The authoritative source for each important fact.
- Existing PRDs, specs, interface contracts, meeting notes, code, dashboards,
  and launch procedures.

Read-only evidence gathering is the default when tools and access are available.
External writes still require the user's request. For each material source,
record:

```markdown
| Artifact | Authority and scope | Owner | Version or date | Last verified | Status |
|---|---|---|---|---|---|
```

Declare exactly one authoritative home for each decision domain. Code and
runtime evidence establish implemented behavior; they do not override Product
intent. Meeting notes provide history; they do not override a later approved
decision. Record conflicts instead of choosing silently:

```markdown
| Conflict | Sources | Consequence | Accountable decider | Resolution deadline | Status |
|---|---|---|---|---|---|
```

Missing access, stale evidence, or unresolved conflict on a material decision
blocks `READY`.

### 2. Build the canonical contract

Add or update these sections in the declared authoritative artifact. Preserve
existing terminology and identifiers.

```markdown
## Shared contract

### Contract metadata
- Authoritative artifact:
- Accountable maintainer:
- Contract version:
- Effective phase:
- Last verified:
- Supersedes:

### Outcome
- User or business problem:
- Expected behavior:
- Explicit non-goals:

### Glossary
| Term | Exact meaning | Not to be confused with | Owner |
|---|---|---|---|

### Scope by phase
| Behavior | Current | Phase 1 | Later phase | Owner |
|---|---|---|---|---|

### Invariants
- Must always remain true:
- Must never happen:
- Fail-open or fail-closed policy:

### Decision rights
| Decision | Accountable decider | Required consultees | Veto domain | Deadline | Escalation |
|---|---|---|---|---|---|

### Requirements traceability
| Requirement | Source | Owner | Contract clause | Scenarios | Test or proof | Metric | Launch gate | Status |
|---|---|---|---|---|---|---|---|---|

### System and data flow, when applicable
| Step | Producer | Input | Output | Timing | Source of truth | Failure behavior |
|---|---|---|---|---|---|---|

### Interface contract, when applicable
| Field or signal | Meaning | Freshness | Versioning | Producer | Consumer validation |
|---|---|---|---|---|---|

### Decision table
| Preconditions | Decision | Action | User effect | Metric or event |
|---|---|---|---|---|

### Exclusions and deferred cases
| Case | Why excluded | Current behavior | Revisit trigger | Owner |
|---|---|---|---|---|

### Measurement
- Unit of assignment:
- Unit of analysis:
- Success metrics:
- Guardrails:
- Reconciliation equations:
- Data owner:

### Rollout and rollback
- Shadow proof:
- Ramp steps:
- Promotion criteria:
- Hard stops:
- Rollback mechanism:
- Cleanup condition:

### Decisions and approval evidence
| Decision | Choice and trade-off | Accountable decider | Approval state | Contract version | Evidence link | Timestamp |
|---|---|---|---|---|---|---|
```

Valid approval states are `NOT REQUESTED`, `REQUESTED`, `APPROVED`, and
`DECLINED`. A name alone is not approval. `APPROVED` requires an attributable
link, timestamp, exact decision scope, approver identity, and contract version.
If another artifact format is better supported, preserve the same fields.

### 3. Scale review depth to risk

Classify risk before generating scenarios or requesting reviewers:

- `LOW`: reversible change, one bounded boundary, no sensitive data or
  customer-visible state. Require owner, decision table, key scenarios, proof,
  and rollback.
- `MEDIUM`: customer-visible behavior, multiple independent owners, asynchronous
  state, or material launch dependency. Add traceability, failure scenarios,
  metrics, staged rollout, and domain-owner approval.
- `HIGH`: money movement, irreversible state, security, privacy, legal,
  compliance, safety, or broad production exposure. Add the affected control
  owners, quantified exposure, tested rollback, stop thresholds, and independent
  adversarial review.

Derive reviewers from affected decisions and risks. Product, Engineering, Data
Science, Analytics, Operations, Security, Privacy, Legal, Compliance, Finance,
Support, Accessibility, and SRE are examples, not a fixed checklist.

### 4. Interrogate every boundary

Ask questions that force precise answers:

- What does each producer guarantee, and what does it merely attempt?
- Can the producer and consumer observe different versions of reality?
- What can change between prediction, decision, and action?
- Which timestamp represents event time, ingestion time, scoring time, and
  action time?
- How does the consumer prove that an input is current?
- What happens when input is late, duplicated, missing, stale, partial, or from
  a previous version?
- Which existing behavior remains active?
- Is the new behavior additive, replacing, or overriding?
- Which states or product variants are intentionally excluded?
- What does each metric count, and which denominator does it use?
- Who decides whether observed risk is acceptable?

Do not accept "probably," "usually," or "the model handles it" as a contract.
Convert each into a measurable guarantee, a bounded assumption, or an open
decision.

### 5. Create a risk-derived scenario matrix

Derive scenarios from the boundary inventory, requirements, and identified
hazards. Rank them by impact and plausibility. Do not use a fixed scenario quota.
Consider:

- Happy path.
- Boundary timing around material scheduled or asynchronous steps.
- State change between decision and action.
- Duplicate, delayed, missing, reordered, and partial input.
- Producer and consumer using different data sources.
- Existing rule conflicts with the new decision.
- Multiple related entities where one changes and another does not.
- Excluded products, states, regions, or cohorts that could change the outcome.
- Retry, replay, rollback, and rerun behavior.
- A concrete example for each irreversible or money-moving failure.

For each scenario record:

```markdown
| Scenario | Requirement | Risk | Starting state and timeline | Expected result | Verification method | Detector or mitigation | Status | Approver |
|---|---|---|---|---|---|---|---|---|
```

Record a reason for each material `N/A`. Use production-shaped examples where
permitted. Sanitize identifiers and customer data in durable artifacts.

### 6. Run an adversarial review

Challenge the draft before implementation:

1. Find plausible timelines that produce the highest-impact wrong actions.
2. Find assumptions crossing service, warehouse, CDC, cache, queue, or model
   boundaries.
3. Compare the proposal with the closest existing production workflow.
4. Identify behavior that Product, Analytics, or Operations would find
   surprising during the first production run.
5. Identify a metric that could look healthy while the user outcome is wrong.
6. Identify any decision hidden in code structure, default values, scheduling,
   or retry policy.

Resolve findings in the contract. Do not leave important answers only in a
Slack thread, code review, or meeting recording.

### 7. Collect real sign-off

Assign exactly one accountable decider to each decision. Add required
consultation or veto authority only where that domain owns the consequence.
Record delegation explicitly.

Approval of a document does not imply approval of every section. Record who
approved each load-bearing decision using the evidence fields above. Never
infer approval from silence, attendance, prior document approval, or another
person's summary.

If a decider is unavailable, lacks authority, or declines:

1. Mark the decision blocked.
2. Preserve the competing positions and evidence.
3. Name the escalation owner and deadline.
4. Do not let implementation imply acceptance.
5. Re-baseline affected work if implementation has already started.

### 8. Issue the readiness verdict

Use one verdict:

- `READY`: every material requirement has authoritative evidence, traceability,
  verification, and attributable approval.
- `READY WITH RECORDED RISKS`: every remaining uncertainty has an accountable
  owner, maximum exposure, detector, stop threshold, tested rollback, expiry
  date, and explicit acceptance.
- `NOT READY`: a material behavior, interface, data assumption, owner, or
  launch gate remains unresolved, unsupported, stale, conflicted, declined, or
  unapproved.

Report:

```markdown
## Readiness verdict
[VERDICT]

## Decisions locked
- ...

## Open decisions
| Decision | Why it matters | Options | Required owner | Due before |
|---|---|---|---|---|

## Review coverage
| Domain | Reviewer | Status | Missing evidence |
|---|---|---|---|

## Accepted risks
| Risk | Owner | Maximum exposure | Detector | Stop threshold | Tested rollback | Expiry | Approval |
|---|---|---|---|---|---|---|---|

## Next safe step
- ...
```

Do not hide `NOT READY` behind a percentage-complete score.

## Change control after approval

Keep the declared authoritative artifacts as living records. Link supporting
PRDs, technical contracts, and launch procedures without duplicating their
content.

When a decision changes:

1. Update the authoritative contract section or decision ledger first.
2. Record the old and new behavior, reason, approver, and effective phase.
3. Update affected scenarios, tests, metrics, and launch gates.
4. Notify owners whose interface or operational responsibility changed.
5. Re-run the readiness review for the changed boundary.
6. Archive or mark superseded material so it cannot compete as current truth.

Slack can announce a decision. It must link back to the durable record.

## Working with AI

Use AI to interrogate, compare, and test the contract. Do not treat an
AI-generated specification as stakeholder agreement.

Before implementation, ask AI to:

- Trace every field and decision from producer to user-visible action.
- Find contradictions across PRD, spec, code, and launch documents.
- Generate adversarial timelines and scenario tests.
- List every assumption without direct evidence.
- Map acceptance criteria to executable tests and launch checks.

Humans remain accountable for product trade-offs, risk acceptance, and
cross-team commitments.

## Common misreading

"Lock details upfront" does not mean freezing all design choices or predicting
every edge case. It means that new evidence can refine the design without
revealing that teams disagreed about the basic behavior, source of truth,
interface meaning, or owner.

## Related skills

- Use `loop-design-doc` as the primary skill when the request is to author the
  underlying design. Return here for cross-boundary agreement.
- Use `loop-devils-advocate` only for the adversarial-review phase when the
  design is contested.
- Use `check-prd-alignment` after implementation. This skill owns pre-build
  agreement and readiness, not code-to-PRD comparison.
- Use `orchestrator-experts-judge` only when a material readiness claim requires
  evidence from several independent sources.
