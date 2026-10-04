# Harness Changelog

Track changes to agent harness infrastructure.

## 2026-10-04 — Portable checks and code-graph policy

- Added `AGENTS.md` with the repository handoff checks.
- Added a description-triggered code-graph rule. This harness does not vendor a knowledge graph.
- Aligned the cost-discipline handoff thresholds with the proxy signals.
- Ignored generated graph output.

## 2026-09-22 — Portable personal setup export

- Added reusable writing, documentation, teaching, presentation, handoff,
  review, and multi-agent workflow skills.
- Added global reasoning, voice, communication, rebase, and cost-discipline
  rules with project-specific examples removed.
- Added a local-only session-cost hook and sanitized editor, CLI, MCP,
  keybinding, and hook templates.
- Added a dry-run-first installer and five-layer validation gate.
- Added CI validation and documented the allowlist/exclusion boundary.

## 2026-07-12 — Fintech/trading domain patterns

Consolidated recurring functional-core, ledger, and risk-control patterns from
several independent financial-system projects.

### Added

- `.cursor/rules/fcis-domain-core.mdc`: glob-activated rule for
  `domain/`, `core/`, `ledger/` directories — Functional Core/Imperative
  Shell discipline (zero I/O, zero hidden inputs, property-tested
  invariants).
- `.cursor/skills/money-ledger-invariants/SKILL.md`: playbook for
  double-entry ledger / money-movement code — no floats, single money path,
  idempotency at three layers, conservation property tests.
- `.cursor/skills/risk-gate-kill-switch/SKILL.md`: playbook for pre-trade
  risk gates and kill switches — deny-dominates, exhaustive rule
  evaluation, backtest/live shared exit logic.

## YYYY-MM-DD — Initial Setup

### Added

- `.cursor/harness.yaml`: Codebase config with build gates
- `.agent-progress.md`: Cross-session progress tracker
- `.cursor/rules/workflow.mdc`: Single always-apply rule covering session lifecycle
- `.cursor/rules/lang-memory-bank.mdc`: Glob-activated language context loading
- `.memory-bank/session-learnings.md`: Pattern log with eviction policy
