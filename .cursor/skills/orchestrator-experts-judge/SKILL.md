---
name: orchestrator-experts-judge
description: "OEJ meta-pattern (Orchestrator-Experts-Judge) for parallel multi-source investigations with grounded verification. Runtime- and org-agnostic core with a maintained Cursor adapter. Use for ramp-gate reports, dashboard/monitor patches, multi-axis PR review, regression triage, or any task with 3-6 parallel sources and a rubric-gated deliverable. Triggers: OEJ, multi-agent investigation, parallel domain experts, grounded judge, methodology check, ramp gate report."
metadata:
  category: plan
  persona: backend-engineer, tech-lead, sre
allowed-tools:
  - Subagent
  - ReadFile
  - ApplyPatch
  - rg
  - Shell
---

# Orchestrator + Experts + Judge (OEJ)

A meta-pattern for tasks where (a) work decomposes into 3-6 parallel specialist subtasks AND (b) output quality benefits from external-evidence verification before delivery.

**This skill does not do work itself.** It defines a pattern that any task
instantiates. The core is runtime-agnostic; `adapters/` maps it to a concrete
agent runtime.

## How This Skill Is Organized

```
SKILL.md                  (you are here — the generic meta-pattern)
templates/                (generic role prompts + rubric design)
  orchestrator.md         (plan → dispatch → synthesize → iterate → deliver)
  expert.md               (self-contained specialist that writes an artifact)
  judge.md                (grounded verification with structured verdict)
  grounded-checks.md      (design guide for rubrics that actually bite)
adapters/                 (map the abstract pattern onto a concrete runtime)
  cursor.md               (Cursor IDE runtime: Subagent tool, worker types, MCP)
  [author your own]       (other runtimes require their own tested adapter)
```

**To use OEJ in a new environment:** copy an existing adapter as a starting point, replace runtime/org details, done.

## Minimum Viable Run

```
1. Create workspace:      mkdir -p <workspace>/findings
2. Write plan.md          (copy templates/orchestrator.md §Phase 1, fill brackets)
3. Dispatch experts       (N parallel workers per your runtime's concurrency primitive)
4. Read findings/*.md  →  synthesize draft.md (or draft.<ext>)
5. Dispatch judge         (one worker, executes rubric checks against artifacts)
6. On FAIL:               re-dispatch ONLY named experts with critique prepended; max 3 rounds
7. On PASS:               promote draft → final deliverable; append verdict + attribution
8. Persist the run externally if requested (knowledge base / Notion / ticket / doc page)
9. Run any repository-required post-delivery steps.
```

The specifics of step 3 (how to dispatch parallel workers), step 5 (how to spawn a judge), step 8 (how to persist externally), and step 9 (what "org-required" means) come from the adapters. The abstract flow is the same regardless.

## Optional Persistence

OEJ always writes a local filesystem workspace first. That workspace is the source of truth: `plan.md`, `findings/*.md`, `draft.*`, `judge-verdict-round-*.md`, `audit.log`, and any final deliverable. If the task should be durable beyond the local checkout, the orchestrator can mirror the run to an external knowledge base starting right after `plan.md` is written (`DRAFT` status), then update it after expert findings, judge verdicts, final PASS, or ESCALATE.

Persistence is adapter-specific. Examples:

| Environment | Persistence target |
|---|---|
| Generic | A wiki page, ticket comment, artifact bundle, or doc page |
| Notion-enabled | Notion page via an installed Notion adapter |

The persisted record should include:

- Original question, decision-maker, deadline
- Workspace path and artifact manifest
- Expert list with confidence levels
- Judge verdict(s), including failed checks and critiques
- Final deliverable or link/path to it
- Audit log summary (who/what/when)
- Open gaps, caveats, and next actions

Do not make the external page the only copy. It is a mirror for reviewability, searchability, and cross-session continuity; the local artifacts remain the replayable record.

## When It Applies

All three must be true:

| Check | Why it matters |
|---|---|
| 3-6 genuinely parallel subtasks (different sources, different axes) | < 3 = single agent is faster; > 6 = task isn't truly parallelizable |
| You can pre-commit to 5-8 grounded checks the judge will execute | If you can't write down what the judge *checks*, the pattern has no teeth |
| Cost of a wrong answer exceeds ~15 min of your time + tokens | OEJ burns more tokens than a single agent; ROI must clear the bar |

## When NOT to Apply

| Anti-shape | Use instead |
|---|---|
| A single existing specialist skill already covers the whole question | Invoke that skill directly. OEJ is for cross-skill synthesis. |
| Real-time or latency-critical work (seconds matter) | Single agent; capture OEJ-shape lessons afterward. |
| Code-change work where multiple experts would edit the same files | Single agent. OEJ is analysis + verification; coding comes AFTER the judge passes on the plan. |
| Open-ended creative work with no rubric | Single agent. An ungrounded judge *degrades* quality (Huang et al. ICLR 2024). |
| Task value < ~15 min of your time saved | Single agent. OEJ's pre-flight cost (plan + rubric) exceeds the win. |

**Honest test:** if you can't write down what the judge would check before starting, the pattern doesn't fit.

## The Three Roles

| Role | What it does | Template |
|---|---|---|
| **Orchestrator** (lead agent) | Plans, dispatches experts in parallel, synthesizes, runs the iteration loop, delivers | `templates/orchestrator.md` |
| **Expert** (1..N) | Self-contained specialist owning one source/axis. Writes findings to a filesystem artifact. Does NOT see other experts' work. | `templates/expert.md` |
| **Judge** | Runs grounded external checks against the draft. Returns PASS / FAIL_WITH_CRITIQUE / ESCALATE with named failing expert(s). | `templates/judge.md` |

The judge's checks live in `templates/grounded-checks.md`. That file is load-bearing — read it before writing a new rubric.

## Iteration Protocol

| Round | Trigger | Action |
|---|---|---|
| 1 | Always | Full plan → all experts in parallel → draft → judge |
| 2 | Judge returned FAIL_WITH_CRITIQUE | Re-dispatch ONLY the experts the critique names, with the critique prepended; merge; re-draft; re-judge |
| 3 | Judge still FAIL | Last attempt with stronger guidance; flag remaining uncertainty in output |
| Stop | Round 3 FAIL OR verdict ESCALATE | Write `ESCALATE.md`; hand to user. Do not ship a half-passed draft. |

**Hard limits** (abstract; your adapter maps these to its observables):

- Max 3 iterations.
- Max 8 experts per round (usually 3-6; more = the task isn't really parallelizable).
- Max ~15 worker invocations total (3 rounds × 5 experts).
- Per-task wall clock cap — set in your adapter based on your runtime's latency profile.

If you're exceeding the invocation cap, the rubric is too vague or the experts aren't parallelizable.

## Failure Modes

Each one has bitten in production. See `templates/grounded-checks.md` for the checks that catch them.

| # | Failure | Symptom | Mitigation |
|---|---|---|---|
| 1 | Ungrounded judge ("LGTM" judge) | Judge PASSes without executing a tool. Output ships with the error it was meant to catch. | Every rubric check MUST execute a tool and cite its result. Prose-only PASS = automatic FAIL. |
| 2 | Expert duplication / gap | Two experts run the same query; a critical axis is missed. | Orchestrator prompts state exact scope + boundaries + what OTHER experts handle. |
| 3 | Cost explosion / runaway loops | Iteration > 3, or experts spawn sub-experts. | Hard cap 3 rounds; no sub-expert dispatch; one layer of hierarchy only. |
| 4 | Same-model agreement bias | Same model judging same-model work inflates agreement 5-7%. | Cross-family judge preferred (different model for judge — see Claude Code adapter for model selection). If unavailable: two-pass judge with distinct roles ("methodology auditor" + "data integrity auditor"); require BOTH PASS. |
| 5 | Positional / verbosity bias | Judge favors longer findings over shorter accurate ones. | Rubric ranks evidence by tool output quality, not prose length. Structured verdict format (YAML) reduces stylistic drift. |
| 6 | Stateful-coding misuse | OEJ applied to code changes; experts conflict on file edits. | OEJ is analysis + verification. Coding is single-agent, runs AFTER judge PASSes on the plan. |
| 7 | Skill-wrapping theater | OEJ wraps a single specialist that already answers the question end-to-end. Adds cost and latency for no lift. | If one existing skill covers the whole task, invoke it directly. |

## Evaluation (Regression Tests)

The pattern depends critically on the rubric. A rubric change that looks harmless can silently re-admit a class of errors the pattern was designed to catch. **Every OEJ deployment should carry at least one eval case — a captured WRONG draft + a captured CORRECT draft, with assertions that the judge FAILs the former and PASSes the latter.**

How to write one (runtime-agnostic):

1. Capture a real near-miss or past correction from your domain.
2. Freeze two workspaces: `fixtures/wrong/` (the flawed draft + findings that produced it) and `fixtures/correct/` (the corrected draft + findings).
3. Write a runnable script that loads each fixture, executes your rubric's checks against it, and asserts the per-check statuses match expectations.
4. Exit non-zero on any mismatch. Hook to pre-commit if you iterate on the rubric often.

Keep the eval runner out of the agent workflow. Run it from a terminal when the
judge rubric changes, and commit a readable report when reviewers need to audit
the checks.

## Pre-Flight Checklist

Answer all before spawning the first worker. If any is "I'll figure it out", fix it first.

- [ ] Deliverable path + format (report, comment, patch, scorecard, …)
- [ ] Named reader / decision-maker + decision + deadline
- [ ] 3-6 experts, each with single non-overlapping scope
- [ ] 5-8 grounded checks the judge will run (each cites a tool)
- [ ] Workspace dir exists with `findings/` subdir
- [ ] Runtime adapter read (how do I dispatch parallel workers in my environment?)
- [ ] Repository workflow and attribution rules read
- [ ] Persistence target decided (`none`, wiki, ticket, or document page)
- [ ] Does any existing single skill already cover this? (If yes, stop; use it directly.)

## References

External:
- Anthropic, [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — orchestrator-worker pattern; 90.2% lift; 15× token cost
- Anthropic, [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — pattern catalogue
- Huang et al., ICLR 2024, [LLMs Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798) — why grounded checks matter
- Shinn et al., NeurIPS 2023, [Reflexion](https://arxiv.org/abs/2303.11366) — verbal RL via critique loops
