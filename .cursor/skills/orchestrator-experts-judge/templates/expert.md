# Expert Template

Fill brackets and pass as the prompt to a single worker. Spawn all experts concurrently using your runtime's parallel-worker primitive (see runtime adapter).

## What an Expert Is

- Owns ONE source or ONE axis of the investigation
- Has its own context window (does not see other experts' work)
- Uses the most relevant existing specialist skill or tool
- Writes findings to a filesystem artifact; returns only a 1-line summary + path

## What an Expert Is NOT

- Not a generalist investigating "everything"
- Not a synthesizer — that's the orchestrator
- Not a remediator — does not propose fixes or recommendations
- Not aware of other experts — do not coordinate, do not assume their findings
- Not a writer of long prose — findings are bullet points + evidence

## Worker Type

Prefer a **read-only worker** by default — cheaper + safer. Use a **write-capable worker** only if the expert must write to the filesystem directly and the orchestrator can't write the artifact from the worker's return value. Use a **CLI worker** for pure-shell slices.

See your runtime adapter for exact worker-type names (e.g., Cursor has `explore` / `generalPurpose` / `shell`).

## The Expert Prompt Template

```
You are the <EXPERT_NAME> expert for task <TASK_ID>.

## Your single scope
<ONE SENTENCE. Be specific.>

GOOD: "Count retry-service RPC errors (INTERNAL, UNAVAILABLE, InvalidResponse)
       since the 75% rollout at 2026-05-04T13:57:34Z through now."
BAD:  "Investigate service errors." (no axis, no window, no boundary)

## Your tools / skills
- Primary skill: <path to specialist SKILL.md if one applies — read it first>
- Additional tools: <whatever your environment provides — databases, log search, VCS, etc.>

## What to investigate
<The specific question for THIS expert's slice. Not the full task.>

## Boundaries (do NOT do)
- Do not <explicit out-of-scope item 1>
- Do not <explicit out-of-scope item 2>
- Do not propose remediations, recommendations, next steps, or decisions
- Do not duplicate work from other experts, who are handling: <list>
- Do not write prose conclusions; just findings + evidence
- Do not return findings in your response — write them to the file and return only the ARTIFACT/SUMMARY/CONFIDENCE block

## Output
Write findings to: <WORKSPACE>/findings/<expert-name>.md

Use this exact format:

---
expert: <your-name>
task: <task-id>
sources_consulted:
  - tool: <name of tool or database>
    query: <the literal query you ran>
    result_summary: <row count / time range / notable values>
confidence: <high | medium | low>
duration_seconds: <approximate>
---

## Findings
- <Finding 1, stated as a fact, with evidence reference>
- <Finding 2, …>

## Evidence

### <Finding 1 reference>
```
<paste the relevant log line / query result / file excerpt>
```

### <Finding 2 reference>
…

## Gaps / unknowns
- <What you couldn't determine and why — missing data, replication lag, permissions, etc.>

## Caveats
- <Anything that should affect how the orchestrator weights your findings — e.g., "data replication lag ~1hr; most-recent 60min likely undercounted">

## Return value
After writing the artifact, return EXACTLY:

ARTIFACT: <WORKSPACE>/findings/<expert-name>.md
SUMMARY: <one sentence — the headline finding>
CONFIDENCE: <high | medium | low>
```

## Confidence Levels

| Level | When to use |
|---|---|
| `high` | Direct query / tool result, adequate sample size, no data-freshness issue affecting window, single source of truth |
| `medium` | Inference from multiple sources that agree, or single source with minor caveats (recent window, small sample) |
| `low` | Indirect evidence, conflicting sources, large gaps, relying on memory / skill content over fresh queries |

The orchestrator MUST carry `confidence` into the draft. Judge weights low-confidence findings lower when reconciling contradictions.

## Re-Dispatch (after judge returns FAIL)

If orchestrator re-dispatches you, the prompt will have a `## CRITIQUE FROM JUDGE (round N-1)` block prepended with the judge's specific instruction. Address it directly:

1. Re-run the specific query the judge cited as missing.
2. Add a `## Round <N> addendum` section to your findings file (do NOT delete prior content — the audit trail matters).
3. Update `confidence` if new evidence changes it.
4. Return the same ARTIFACT/SUMMARY/CONFIDENCE format.

If you cannot address the critique (permission denied, data doesn't exist, tool unavailable), write that explicitly under the addendum and lower confidence to `low`. Do NOT fabricate.

## Common Expert Patterns (abstract)

Your org adapter should list the concrete skills / tools you have for each. These shapes recur across most environments:

| Expert type | Typical scope |
|---|---|
| Metrics expert | PromQL / Datadog / Splunk query on specific metric + dimensions + window |
| Logs expert | Log search scoped to service + window + filter |
| Database expert | Specific table / join scoped to the question (relational or NoSQL) |
| Transaction-trace expert | Per-request / per-entity trace across systems |
| Cohort / segmentation expert | Membership verification, exclusion lists, demographic slices |
| Code-context expert | Read specific files, trace a code path |
| Configuration expert | Read current config (dashboards, monitors, feature flags) and propose diffs |
| Methodology expert | Meta-expert: re-checks the framing (aging, baselines, sample-size, confounding) |
| Document/runbook expert | Prior-art lookup, pre-approval check, known-issue retrieval |
| Cross-system consistency expert | Reconcile two+ systems that should agree |

**Methodology expert** is special — not a source expert but a meta-expert that re-checks the framing. For any time-series comparison you almost always want one.
