# Grounded Checks — Design Guide

The highest-leverage thing in OEJ. A judge with bad checks is worse than no judge — it adds cost AND a stamp of approval to bad output (Huang et al. ICLR 2024). This file teaches you to design checks that bite.

The 6 categories below are runtime- and org-agnostic. For domain-specific checks (e.g., "does the draft address any cohort with delta_pp < -5?"), see your org adapter.

## The One Rule

**Every check MUST be answerable by executing a tool and reading the result.**

| OK | Not OK |
|---|---|
| "Run database query X. Row count > 1,000?" | "Is the dataset large enough?" |
| "Read `findings/aging.md`. Does it cite a matched-age filter?" | "Did the expert account for aging?" |
| "Run `<VCS> view <PR/commit>`. Fewer than 5 commits?" | "Is the change appropriately scoped?" |
| "Search logs for `service=X AND level=ERROR AND message=OOM` in last 1h. Zero hits?" | "Is the service healthy?" |
| "Read `draft.md`. Decision block appears in the first 200 lines?" | "Is the summary at the top?" |

The OK column is grounded: the judge runs a thing, gets a numeric/boolean answer. The Not OK column requires the judge to opine — exactly the failure mode the pattern exists to avoid.

## Check Anatomy

Every check has five fields. Skip any and the check loses its bite.

```
### CHECK_NN: <short-descriptive-name>
- Question: <precise thing being verified, 1 sentence>
- Tool: <database query | log search | shell | file read | VCS | …>
- Command: <literal command/query, ready to copy-paste — NOT a description>
- Pass criteria: <numeric/boolean — "X > 1000" or "result == 'finalized'" or "file exists">
- Fail criteria: <inverse — when does this check FAIL, explicitly>
```

**Good example:**

```
### CHECK_01: matched-age-comparison-present
- Question: Does the draft compare this period to the prior one using matched-age methodology?
- Tool: regex file search
- Command: search findings/ and draft.md for DATEDIFF-style age filter or "within N min" phrase
- Pass: ≥ 1 match in either findings/ or draft.md
- Fail: 0 matches → the comparison did not normalize for data aging
```

**Bad example (would not catch a methodology error):**

```
### CHECK_01: methodology-sound
- Question: Is the methodology correct?
- Tool: (none)
- Pass: "Looks reasonable"
```

## Six Check Categories

Pick the ones that fit. 5-8 total is the sweet spot. More than 12 = you're using the judge to do investigation work (that should live in an expert).

### 1. Source Primacy

Verify key claims trace to primary sources, not derivatives.

| Check | Pass criteria |
|---|---|
| All numeric claims in draft link to a findings query | Every number ≥ 100 appears at least once in a findings file |
| No claim cites only a dashboard / summary UI | URL to dashboard does not appear as the sole source for any claim |

### 2. Methodology Integrity

For time-series comparisons, regression analysis, baseline shifts.

| Check | Pass criteria |
|---|---|
| Matched-age / maturity-normalized comparison present | Specific phrase in findings (e.g., `DATEDIFF`, `within N min`, `matched-age`, or period-over-period alongside rolling baseline) |
| Both rolling AND period-over-period baselines shown | Two distinct baseline references in draft |
| Sample size adequate per cohort | Each cohort N ≥ task-specific threshold; cite row count |
| Aging-cutoff window consistent | All compared windows end at same lookback offset |

### 3. Cohort / Segmentation Correctness

| Check | Pass criteria |
|---|---|
| Segment compared to segment-specific baseline (not population) | Baseline query has segment filter |
| Sub-channels separated where they should be | Source / channel / cohort dimension explicit in queries |
| Excluded entities explicitly excluded | Exclusion list cited and applied |

### 4. Counterfactual Presence

| Check | Pass criteria |
|---|---|
| Causal claim has a control comparison | "X caused Y" also shows the case without X (pre-window, untreated cohort, non-X subjects) |
| Pre-event baseline shown for event-driven signals | Trend includes pre-event days, not just post-event |

### 5. Cross-System Consistency

| Check | Pass criteria |
|---|---|
| Multi-system claims cite both systems | Findings reference BOTH System-A AND System-B for any cross-system claim |
| Trace IDs cited for cross-service flows | ≥ 1 trace_id present in findings when claim spans services |
| Sparse signals cite volume context | Low-volume endpoint numbers cited with rate context (`/hr`, `/min`) so sparse-sample distortion is visible |

### 6. Output Hygiene

| Check | Pass criteria |
|---|---|
| Decision / recommendation in first N lines (BLUF) | Head of draft contains Decision/Recommendation/Verdict phrase |
| Owner / deadline named for every action item | Action table has Owner + By columns populated, no "TBD" |
| Confidence carried forward from experts | Low-confidence findings flagged in draft, not silently promoted |
| Default-if-silent stated | Decision-needed sections include the default outcome if no decision is made |
| Attribution policy compliance | Required attribution footer / metadata present (form depends on org — see org adapter) |

## How Many Checks?

| Task value | Check count |
|---|---|
| Low (< ~15 min of time saved) | Don't use OEJ at all |
| Medium (~15 min – 2 hr saved) | 4-6 checks |
| High (2 hr – 1 day saved) | 6-10 checks |
| Critical (exec-facing, irreversible, high-cost-if-wrong) | 8-12 checks + two-pass judge + (ideally) human sign-off on verdict |

More than 12 = you're using the judge to do investigation work.

## Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| "Is this report well-written?" | Subjective; no tool; judge becomes stylistic editor. |
| "Are the conclusions reasonable?" | Same model, same priors, same blind spots; will agree by default. |
| "Did we cover all the angles?" | Unbounded; judge always says "no, also consider…"; never PASS. |
| "Is the SQL correct?" without running it | Static analysis unreliable; require an actual row count. |
| Single check that's actually 5 checks AND-ed | Hides which sub-check failed; orchestrator can't dispatch a useful critique. |
| Pass criteria "looks right" or "seems plausible" | Restate in numbers/booleans or drop the check. |

## Designing for a New Task Type

1. **List failure modes that have happened before** (or that you're worried about). For investigations: aging confound, wrong baseline, missing counterfactual. For code reviews: failing tests, security regression, scope creep. For config patches: non-idempotent edit, silent regression in a dependent component.
2. **For each failure mode, write the question** that, if answered "yes", confirms the failure happened.
3. **For each question, write the tool + command** that produces a numeric/boolean answer.
4. **For each tool result, pre-commit to the pass/fail threshold.** If you can't pre-commit, the check is too vague.
5. **Stress-test:** would this check have caught the failure mode in past cases? If not, refine.

## Stress Test: The Eval Case

Apply your rubric to a captured near-miss from your own domain. Your judge MUST flag the original (wrong) framing as FAIL on a specific subset of checks, AND PASS the corrected framing on all checks.

If your rubric doesn't catch the past error, you don't have a working judge — you have a stamp.

Write this as a dependency-light runnable regression test with paired
`fixtures/wrong/` and `fixtures/correct/` inputs. The eval is the institutional
memory of mistakes the judge must never let through.
