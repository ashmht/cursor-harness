# Judge Template

The judge is the load-bearing piece. Get it wrong and the pattern hurts you (Huang et al. ICLR 2024 — ungrounded self-review degrades quality). Get it right and you catch the error that would have shipped otherwise.

Read this AND `templates/grounded-checks.md` before instantiating.

## Naming Note

What this template implements is the 2026 pattern called **Agent-as-a-Judge** (Apr 2026, *The Sequence*; arxiv 2601.05111) — a judge that itself plans its evaluation, decomposes into sub-checks, uses tools to verify against external evidence, and emits a structured verdict. This is the documented evolution of the older single-pass *LLM-as-a-Judge* pattern, which research has shown to be insufficient for high-stakes verification (see §Illusory Consensus below). Whether you call it "the judge" or "Agent-as-a-Judge", the implementation is what's described here.

## What the Judge Is

A separate worker that:
- Reads the original question, all expert findings, and the draft deliverable
- Executes each rubric check by running a tool (query, file read, log search, shell) and citing the result
- Returns a structured verdict: PASS / FAIL_WITH_CRITIQUE / ESCALATE
- Names which check failed and which expert(s) need to re-run

## What the Judge Is NOT

- Not a free-form reviewer ("does this look right?")
- Not a stylistic critic ("consider rephrasing")
- Not an extender — does not add new analysis, only verifies what's there
- Not an agreement bot — runs grounded checks, not vibes

## The Judge Prompt Template

```
You are the <methodology | data integrity> judge for task <TASK_ID>.

You do NOT do the investigation. You do NOT propose new analysis. You ONLY
verify that the draft's claims are supported by external evidence and that
the rubric below is satisfied.

## Inputs
- Original question: <WORKSPACE>/plan.md
- Expert findings:   <WORKSPACE>/findings/*.md
- Draft deliverable: <WORKSPACE>/draft.md  (or draft.<ext>)

Read all of them before judging.

## Rubric (run EVERY check; each MUST execute a tool)

<Orchestrator inlines task-specific checks here, each in this shape:>

### CHECK_NN: <short-name>
- Question: <what you're verifying>
- Tool: <database query | log search | shell | file read | VCS | …>
- Command: <literal, ready-to-copy-paste>
- Pass criteria: <numeric or boolean — "N > 100" or "result == 0" or "file exists">
- Fail criteria: <inverse — explicit>

(See templates/grounded-checks.md for design rules and category catalogue.)

## Verdict format

Write your verdict to: <WORKSPACE>/judge-verdict-round-<N>.md

---
verdict: PASS | FAIL_WITH_CRITIQUE | ESCALATE
round: <N>
overall_note: |
  <1-3 sentences. Headline judgment.>
---

## Per-check results

### CHECK_NN: <name>
- status: PASS | FAIL
- tool_run: <exact command/query you executed>
- tool_result: <result summarized — row count / value / boolean>
- evidence: <exact quote / row / log line that proves verdict>
- note: <if FAIL, what specifically is wrong; if PASS, brief confirmation>

<repeat for every check>

## Critique (only if verdict == FAIL_WITH_CRITIQUE)

- expert: <name of expert whose findings are insufficient>
  failed_check: <CHECK_NN>
  instruction: |
    <VERY specific. Quote the literal query/command to run, not "investigate further".>

<repeat per expert needing re-dispatch>

## Escalate reason (only if verdict == ESCALATE)

<Why no further iteration will help. Allowed reasons:
 - Tool required by a check is unavailable (authentication expired, network down)
 - Data required by a check doesn't exist in the source system
 - Fundamental ambiguity in the original question
 - Round 3 persistent FAIL on the same check>
```

## Hard Rules

1. EVERY check status MUST cite a tool you ran and its result. If you cannot run the tool, the check is FAIL with reason `could not verify — tool unavailable: <name>`. No prose-only PASS.
2. Do NOT pass a check on prose alone. "The expert says they checked X" is not evidence; you must verify X yourself.
3. Do NOT critique style or word choice. Only methodology and evidence support.
4. If two experts contradict each other on a fact, that's automatic FAIL_WITH_CRITIQUE against the expert with weaker evidence (lower confidence, older data, smaller sample). Name the conflict.
5. ESCALATE allowed in round 1 only if: (a) at least one check returned `tool unavailable` AS the failure reason AND (b) the orchestrator did not flag the missing tool in the plan. Otherwise round 1 defaults to FAIL_WITH_CRITIQUE. Round 3 persistent FAIL may ESCALATE.
6. Do not invent new checks beyond the rubric. The orchestrator-defined rubric is the contract. If you notice a gap, note it in `overall_note` but do not silently run additional checks.

## Illusory Consensus (the failure mode that makes cross-family mandatory for high-stakes)

A March 2026 paper (arxiv 2603.11027, "Beyond the Illusion of Consensus") established that LLM judges show extremely high *model-level* agreement (Spearman ρ = 0.99) but much weaker *sample-level* agreement (Pearson r̄ = 0.72). What this means: across many samples, judges agree on aggregate trends — but on any single sample, they may agree for the wrong reasons (shared surface heuristics like verbosity, formality, structural fluency) rather than substantive quality.

For OEJ this matters because the judge runs on *one* draft at a time. A high-confidence PASS on a single deliverable can be illusory consensus in disguise. Same-model agreement bias (5-7% inflation) compounds on top of this baseline.

## Cross-Family vs Two-Pass Judging

Mitigations in preference order:

1. **Cross-family judge.** Different model family for the judge than for the experts. **Required** for high-stakes terminal verdicts (exec-facing reports, irreversible actions, on-call escalations, > $5k impact). Concretely: if experts run on Claude Sonnet, run the judge on GPT or Gemini.
2. **Two-pass judge** (single-model fallback when cross-family is unavailable). Spawn the judge twice in parallel with distinct system prompts:
   - **Pass A — Methodology Auditor:** "Read findings/ and draft.md. Verify rubric checks by examining these artifacts. For each check, quote the specific finding + line that supports PASS or exposes FAIL."
   - **Pass B — Data Integrity Auditor:** "IGNORE findings/. Re-run primary-source queries from scratch against the draft's numeric claims. For each numeric claim > threshold, execute the underlying query yourself and verify the draft's number matches."
   - Both MUST PASS. If Pass A PASSes but Pass B FAILs, route the FAIL back to the relevant expert with Pass B's critique (counter-query is ground truth).
3. **Human sign-off on the verdict block.** The structured YAML verdict makes this fast — reviewer reads the per-check evidence, not the draft.

For low-stakes / high-frequency runs (daily scorecards, internal PR reviews), single-pass same-family is acceptable; the structured verdict format reduces stylistic-bias influence by ~30-40% (CALM framework). Sample 5% of PASS verdicts monthly with a cross-family re-judge to track agreement drift.

**Hard rule:** if a verdict feeds an irreversible action and you can't run a cross-family judge, downgrade the verdict label to `ADVISORY` and require explicit human sign-off — the human owns the decision, not the judge.

## Common Failure Shapes

These recur across most investigation domains. Your org adapter may add domain-specific ones.

| Failure shape | What the judge should catch |
|---|---|
| Aging confound | Time-series comparison uses windows with different data maturity. Verify with matched-age methodology. |
| Missing baseline | Single-period number with no comparison. Verify by searching draft for BOTH rolling AND period-over-period references. |
| Wrong cohort baseline | Segment compared to all-population baseline. Verify baseline query has the segment filter. |
| Sample too small | Conclusion drawn from N < threshold. Verify via row count from underlying query. |
| Derived metric, not primary source | Claim cited from a dashboard/summary, not a row count. Verify by re-running the underlying query. |
| Fan-out missed | Investigation ignores a downstream system that mediates the effect. Verify presence of cross-system trace evidence. |
| Counterfactual missing | "X caused Y" without checking the case where X didn't happen. Verify presence of control cohort or pre-window comparison. |

## Why "Ask the same model to check its work" doesn't work alone

Empirical finding (Huang et al., ICLR 2024 + ACL 2025): intrinsic self-correction WITHOUT external grounding **degrades** output quality on reasoning tasks. The model's self-feedback is bounded by what it already knew; if it didn't know the answer, it can't self-correct toward it. It often steers away from a correct answer it had stumbled into.

What works: **external grounding**. The judge runs a tool, gets a real result, compares to the draft's claim. That's not self-correction — that's verification against ground truth.

If you find yourself writing a check like "is this conclusion well-reasoned?", stop. Replace with: "does the row count from query X exceed threshold Y?" If you can't replace it with a tool-run check, drop the check.
