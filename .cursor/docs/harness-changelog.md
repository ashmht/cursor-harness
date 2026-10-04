# Harness Changelog

Track changes to agent harness infrastructure.

## 2026-10-04 — Review fixes, Ruby language pack

- Session-cost hook fails open, prices the turn count it prints, reads the
  model from the session-end payload, and does not merge events that have no
  stable session id. Tool counts are append-only.
- Truth-seeking and rebase rules are description-triggered instead of
  always-on. Fintech globs no longer match a generic `core/` directory.
- Installer profiles are `core` (default), `writing`, and `fintech`.
  `example-skill` is not installed. `--config` merges local Cursor and Claude
  config without replacing existing keys.
- Validator rejects unexpected email addresses, unparsable YAML, and shell
  syntax errors, and scans git history for leaks that were deleted from the
  work tree.
- Language pack is Ruby. Kotlin memory-bank stubs are gone.
- Documentation loops carry their own checklists and no longer require reading
  every child skill up front.

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
