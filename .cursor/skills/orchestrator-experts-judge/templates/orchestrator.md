# Orchestrator Template

You are the lead agent. You do NOT do specialist work. Your job: plan → dispatch → synthesize → verify → deliver.

This template is runtime-agnostic. For concrete dispatch mechanics (parallel
worker primitives, subagent types, and message batching), read the maintained
Cursor runtime adapter (`adapters/cursor.md`) or a tested adapter supplied by
your runtime. Read the target repository's workflow and attribution rules
before external writes.

## Phase 0: Framing Gate (skip if task is already concrete)

If the user's request is vague, run a framing pass first to produce concrete Reader / Decision / Deliverable / Constraint. Gate the rest of OEJ on the framing pass succeeding.

Many environments have a dedicated Socratic intake skill that fits here. Use it
when available.

If the request is already concrete, skip to Phase 1.

## Phase 1: Plan

Write `<workspace>/plan.md` BEFORE dispatching. Template:

```markdown
# Investigation Plan — <task-id>

## Question
<One sentence. Concrete, falsifiable.>

## Context
- Relevant codebase / system docs read: <paths, or "cross-codebase">
- Deadline: <datetime + decision-maker>
- Key timestamps: <apply times, window boundaries, data-replication lag>

## Deliverable
<report at <path> | comment on <PR/ticket> | patch file at <path> | scorecard JSON>
Audience: <named person(s)>

## Persistence target
<none | knowledge-base page | Notion page | ticket comment | doc page>
If external persistence is enabled, state:
- Target parent/database/page: <where to create or update>
- Visibility: <who can read>
- Redaction policy: <what must not be uploaded>

## Decision being made
<Who decides what, by when>

## Experts (3-6)

| # | Expert | Scope (1 sentence) | Source(s) | Output artifact |
|---|---|---|---|---|
| 1 | <name> | <exact slice> | <tool / skill / data source> | `findings/<name>.md` |
| …

## Boundaries (anti-duplication)
- Expert A handles X, NOT Y.
- Expert B handles Y, NOT X.
- No expert proposes the decision — orchestrator drafts after judge PASSes.

## Judge rubric (5-8 grounded checks)
<Inline the check definitions. Each MUST cite a tool. See templates/grounded-checks.md.>

## Iteration budget
- Max iterations: 3
- Max worker invocations: 15 (3 rounds × 5 experts avg)
- Max wall clock: <runtime-appropriate cap>
- Escalate trigger: <specific check that indicates data integrity, not methodology>
```

If any of Reader / Decision / Experts / Rubric can't be filled concretely, stop. The task isn't OEJ-shaped.

If `Persistence target` is not `none`, create or update the external run page immediately after `plan.md` is written with status **DRAFT**. Write `<workspace>/persistence-manifest.md` with the external URL, current upload status, and any authentication / redaction caveats. Update this same page after each major phase rather than creating new pages.

## Phase 2: Dispatch (parallel)

Spawn ALL experts concurrently using your runtime's parallel-worker primitive. Sequential dispatch defeats the pattern.

Prompt template: see `templates/expert.md`.

**Worker-type choice** (see runtime adapter for the exact names):
- Prefer a **read-only worker** for any expert that only reads data sources. Cheaper + safer.
- Use a **write-capable worker** ONLY when the expert must write to the filesystem directly AND you can't have the orchestrator write the artifact from the worker's return value instead.
- Use a **CLI worker** when the expert's slice is purely shell / CLI.

**Hand-off rule:** experts write findings to `<workspace>/findings/<expert>.md`. They return only `ARTIFACT:`, `SUMMARY:`, `CONFIDENCE:` in their response. The orchestrator reads artifact files directly. Never roundtrip findings through chat context — it blows up context windows and loses the audit trail.

## Phase 3: Synthesize Draft

After every expert returns, read every `findings/*.md`. Write `<workspace>/draft.md` (or `draft.html`, `draft.<ext>` as appropriate).

The draft MUST:
- Cite specific finding file + section for every numeric claim (no paraphrase loosely)
- Surface contradictions between experts as explicit caveats, not paper over them
- Carry forward each expert's `confidence` level (don't silently promote low-confidence findings)
- Include a "How this was assembled" footer listing experts consulted
- Satisfy every judge rubric check by construction (don't leave it to the judge to notice the gap)

Do NOT skip the draft step and go straight to the final deliverable. The judge needs a concrete artifact to evaluate.

## Phase 4: Judge

Spawn the judge as a single worker (read-only is usually enough — the judge reads artifacts and runs verification tools, it does not write). Prompt: `templates/judge.md`, rubric inlined from plan.md §Judge rubric.

Judge writes `<workspace>/judge-verdict-round-<N>.md`.

**Two-pass judge for high-stakes deliverables** (exec-facing, irreversible, high-cost-if-wrong): spawn the judge TWICE in parallel with distinct system prompts —
- Pass A: "methodology auditor" — reads findings/ and draft, verifies rubric against artifacts.
- Pass B: "data integrity auditor" — ignores findings, re-runs primary-source queries from scratch against the draft's numeric claims.

Both MUST return PASS for the task to PASS. This substitutes for cross-family judging when only one model family is available.

## Phase 5: Iterate or Deliver

**verdict = PASS:**
1. Promote `draft.md` → final deliverable path.
2. Append judge verdict block to deliverable footer (auditable trail).
3. Append attribution footer per your org's policy (see org adapter).
4. **Write `<workspace>/audit.log`** with one line per phase: `<timestamp> | <phase> | <details>` (plan written, N experts dispatched, draft written, judge verdict, final delivery). This is the forensic record the security and org adapters rely on for incident response.
5. **If a persistence target is configured**, mirror the run externally using the org adapter:
   - Create/update the same run page titled `<task-id> — OEJ Run`.
   - Upload or summarize `plan.md`, all `findings/*.md`, `draft.*`, final deliverable, judge verdict(s), and `audit.log`.
   - Write `<workspace>/persistence-manifest.md` with external page URL, uploaded sections, skipped/redacted artifacts, and timestamp.
   - Keep local files as source of truth; external persistence is a searchable mirror.
6. Run any org-required post-delivery hooks (progress tracker update, commit, ticket creation — see org adapter).

**Path-restriction invariant** (enforced throughout the run): the orchestrator and all experts write **only** under `<workspace>/` or to the explicit final deliverable path. No writes outside these paths at any phase. If an org-adapter hook requires a write elsewhere (e.g., updating a progress tracker file at the repo root), do it as a distinct post-delivery step AFTER the judge verdict is recorded — so the audit trail shows it clearly.

**verdict = FAIL_WITH_CRITIQUE and round < 3:**
1. Re-dispatch ONLY the experts named in `critique[].expert` — concurrent dispatch.
2. Each re-dispatched expert gets the original prompt PLUS a `## CRITIQUE FROM JUDGE (round N-1)` block prepended with the judge's specific instruction.
3. Other experts' findings carry forward untouched.
4. Re-draft, re-judge.

**verdict = FAIL after round 3, OR verdict = ESCALATE:**
1. Stop.
2. Write `<workspace>/ESCALATE.md`: original question, all judge verdicts, specific check(s) that wouldn't pass, best hypothesis for why, what tool / data is missing.
3. If a persistence target is configured, mirror the partial run externally and mark it **ESCALATED / NOT SHIPPED** at the top of the page.
4. Hand to user. Do NOT ship a half-passed draft.

## Anti-Patterns

| Anti-pattern | Why it kills the pattern |
|---|---|
| Sequential expert dispatch | Defeats parallelism; OEJ is a latency win only when experts run concurrently. |
| Vague expert scopes ("research the merchant") | Experts duplicate or miss the actual question. |
| Skipping the workspace dir, holding everything in chat context | Game-of-telephone; context window blows up; lose audit trail. |
| Judge with ungrounded checks ("is this report good?") | Judge becomes theater; ships bad output with a stamp. |
| Looping past round 3 | Signals rubric is wrong (too vague) or data isn't available. |
| Experts editing code mid-task | OEJ is for analysis; coding happens AFTER judge PASSes on the plan. |
| Experts spawning sub-experts | One layer of hierarchy. Deeper = unbounded cost. |
| Skipping org-adapter hooks (attribution, progress tracker) | Violates org conventions; breaks cross-session continuity. |

## Pre-Dispatch Checklist

- [ ] `plan.md` exists and every section filled concretely
- [ ] `findings/` subdir exists
- [ ] Relevant codebase / system docs read (per org adapter)
- [ ] Each expert has non-overlapping scope + explicit boundary list
- [ ] Judge rubric has 5-8 checks, each citing a tool + pass/fail criteria
- [ ] Deliverable path decided
- [ ] Persistence target decided (`none` is valid)
- [ ] Iteration budget + escalate trigger stated
- [ ] Runtime + org adapters read (worker dispatch, attribution, hooks)

If any unchecked: fix it. Sloppy upfront design is the #1 cause of OEJ failure.
