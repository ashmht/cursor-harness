# Harness Changelog

Track changes to agent harness infrastructure.

## 2026-11-25 — Subagents, active guard hooks, and upgraded review/writing stack

- Added `.cursor/agents/` (`coder`, `critic`, `scout`, `verifier`) for
  multi-vendor routing, read-only context offloading, and blind cross-vendor
  PR review; wired into `scripts/install.py` (`core` profile) and
  `scripts/validate.py`.
- Added portable `beforeShellExecution` guard hooks under `hooks/` and
  `templates/hooks.example.json`: `guard-git-push.sh` (blocks pushes to
  `main`/`master`, plain `--force`/`+refspec`, and unpinned
  `--force-with-lease`), `guard-zsh-split.sh` (catches zsh unquoted list
  expansions and `=`-word expansion), `guard-docker-env.sh` (blocks printing
  container environments), and `guard-gh-pr-body.sh` + `pr-body-edit.py`
  (section-scoped PR body updates).
- Updated `workflow.mdc` with PR risk-tiering, blind subagent isolation, model
  routing, fresh-proof discipline before claiming done, and mechanism-first
  learning capture.
- Added `check-sources-first.mdc` and `slack-send-confirmation.mdc`; updated
  `framing.mdc`, `writing-compact.mdc` (Staff+ technical posture, prose over
  label scaffolding), and `truth-seeking.mdc` (real artifact beats fixture).
- Added `pr-critical-thinking`, `systematic-debugging`, and `testing-skills`
  skills; upgraded `critical-pr-review` (performance,
  observability, boot/load-order, pending-review script), `humanizer`
  (52-pattern pass + `references/messages.md`), `compact-chat`, and
  `orchestrator-experts-judge`.

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
