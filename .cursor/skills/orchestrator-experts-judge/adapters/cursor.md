# Runtime Adapter — Cursor IDE

How OEJ maps onto Cursor's agent runtime. Pair it with the target repository's
workflow, ownership, and attribution rules.

## Concurrency Primitive

Cursor's `Subagent` tool spawns a worker. To run N experts in parallel, the orchestrator emits **a single assistant message containing multiple `Subagent` tool-use blocks**. Set `run_in_background=true` when the current interaction is in Multitask Mode; otherwise choose foreground/background based on whether independent parent work remains.

```
Assistant message turn:
  Subagent(description="expert-1", prompt="…", subagent_type="explore")
  Subagent(description="expert-2", prompt="…", subagent_type="explore")
  Subagent(description="expert-3", prompt="…", subagent_type="explore")
  Subagent(description="expert-4", prompt="…", subagent_type="explore")
  Subagent(description="expert-5", prompt="…", subagent_type="explore")
```

Sequential `Subagent` calls across multiple assistant turns defeat the parallelism. The "all in one message" pattern is the pattern.

The **judge** is dispatched the same way (one `Subagent` call, or two in one message for the two-pass judge).

## Worker Types (`subagent_type`)

| Value | Use for | Why |
|---|---|---|
| `explore` | Read-only codebase experts: VCS reads, grep, file reads, architecture tracing | Fast and scoped; cannot accidentally mutate state |
| `generalPurpose` | Multi-step experts that need broader tools or must write artifacts directly | Full tool access; use sparingly |
| `shell` | Pure-CLI experts (e.g., `kubectl get …`, a one-line API probe) | Scoped to shell execution only |

**Default: `explore`.** Flip only when you have a concrete need.

**Orchestrator-writes-the-artifact trick:** to keep an expert in `explore`, have the expert return its findings as the Subagent response (a structured markdown block). The orchestrator writes the artifact file itself.

## Model Family

Default to `model="inherit"`. Only select another model when the user explicitly requested an available model. Do not assume that a named model remains available across Cursor releases. When both judge passes inherit the same family, apply the role-separated two-pass pattern from `templates/judge.md` for high-stakes deliverables:

- Pass A — Methodology Auditor (reads findings + draft)
- Pass B — Data Integrity Auditor (ignores findings, re-runs primary queries)

Both MUST PASS.

## Cost / Budget Observables

Dollar-cost caps don't map cleanly to Cursor — there's no per-task billing signal. Use these observable proxies in plan.md §Iteration budget:

| Observable | Recommended cap |
|---|---|
| Max iterations | 3 |
| Max subagent invocations per task | 15 (3 rounds × 5 experts avg) |
| Max wall clock | 20 min |
| Max `findings/` total size | 500 KB (more = experts are writing prose, not evidence) |

If you hit the invocation cap, the rubric is too vague or experts aren't truly parallel.

## MCP Integration

MCP servers provide read-only tool access. Common patterns:

- **Observability MCPs** — use for metrics, logs, and trace experts.
- **Notion / doc MCPs** (`user-notion`) — use for runbook / prior-art / pre-approval experts.
- **VCS MCPs** — use for pull-request triage and commit-history lookups.

MCP availability is runtime- and worker-specific. Discover the tool schema in the parent before use. If a worker does not have the required MCP, the parent runs the read and passes a bounded artifact or result into the worker prompt. Do not claim evidence was checked when the needed server was unavailable.

For write-side operations, use the repository-approved CLI or integration and
keep mutations in the parent agent.

## Workspace Conventions

| Task shape | Workspace root |
|---|---|
| Investigation / ramp-gate report | `.investigation/<task-id>/` |
| PR review | `.review/<owner>-<repo>-<pr_number>/` |
| Config / dashboard patch | `.patch/<subject-slug>-<date>/` |
| Scheduled scorecard run | `.scorecard/<date>/` |
| Anything else | `.oej/<task-id>/` |

Every workspace has:

```
<workspace>/
├── plan.md
├── findings/
│   └── <expert-name>.md
├── draft.md (or draft.html, draft.<ext>)
├── judge-verdict-round-<N>.md
└── ESCALATE.md  (only if unresolved after round 3)
```

Final deliverable is promoted out of the workspace (e.g., to a top-level `report-*.html` or posted to GitHub).

## Attribution Footer

Cursor's convention is to note the agent tool in delivered artifacts. Use:

- Markdown: `<sub>Authored with Cursor via OEJ pattern (<N> experts + <K>-round judge).</sub>`
- HTML: `<footer class="attribution">Authored with Cursor via OEJ pattern (<N> experts + <K>-round judge).</footer>`
- PR comments / doc comments: same, stripped of tags.

## Orchestrator Flow in Cursor (concrete)

1. **Phase 1 plan:** orchestrator writes `plan.md` using `Write` tool.
2. **Phase 2 dispatch:** single assistant message with N `Subagent` calls, usually `subagent_type=explore`.
3. **Phase 3 synthesize:** orchestrator reads each `findings/*.md`, then writes `draft.md` (or `draft.html`).
4. **Phase 4 judge:** `Subagent` with `subagent_type=explore`, prompt = `templates/judge.md` filled in with the rubric from `plan.md`. For two-pass, issue two calls in one message.
5. **Phase 5 iterate:** on FAIL, single assistant message with M `Subagent` calls (one per critiqued expert, not all N).
6. **Phase 5 deliver:** `Write` for the final file path, `Shell` for any commit / post-hook.

## Anti-Patterns in Cursor Specifically

| Anti-pattern | Why it fails in Cursor |
|---|---|
| Dispatching experts across multiple assistant turns | Breaks parallelism — each turn is a separate round-trip. |
| Using `generalPurpose` for all experts "just to be safe" | Slower + costlier + grants unnecessary write access. |
| Returning findings in the `Subagent` response body AND writing the artifact | Duplicates — pick one. For `explore` agents, return body is fine (orchestrator writes artifact). |
| Spawning subagents from inside a subagent | Unbounded fanout; OEJ permits one hierarchy layer only. |
| Polling background subagents | Cursor sends completion notifications; continue independent work or end the turn. |
| Holding plan.md / findings/ in chat context instead of files | Context-window burn; reduces effective depth of the investigation. |
