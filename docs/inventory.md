# Export inventory

This repository is an allowlisted export of a personal Cursor setup. It is not
a mirror of the entire Cursor home directory.

## Included

- Role-specialized subagents (`coder`, `critic`, `scout`, `verifier`) for
  multi-vendor coding, read-only exploration, blind critique, and verification.
- Session workflow, memory-bank conventions, progress tracking, outbound-safety
  guards, and reusable engineering rules.
- Voice and writing rules that contain no workplace-specific examples.
- Portable authored skills for documentation, debugging, PR ownership, skill
  testing, teaching, presentations, reviews, handoffs, writing, and multi-agent
  investigations.
- Active shell safety guards (git push, zsh word-splitting, docker env printing,
  and section-safe PR body edits) plus a local session-cost hook.
- Sanitized examples for CLI preferences, editor settings, keybindings, hooks,
  and public MCP integrations.
- A dry-run-first installer and layered repository validator.

## Intentionally excluded

- Employer, customer, merchant, incident, ticket, and production-system
  material.
- Work-only domain skills, service experts, operational runbooks, and database
  safety controls.
- Raw account metadata, authentication identifiers, OAuth client IDs, tokens,
  private document IDs, remote hosts, and absolute home-directory paths.
- Runtime state, transcripts, cost logs, hook state, generated reports, and
  local memory.
- Cursor-maintained built-in skills and plugin caches. Those should be installed
  from their upstream source instead of vendored here.
- Symlinked skills whose canonical source is another repository.

## Selection rule

A file is included only when another user can understand and run it without
access to the original author's employer, workstation, private accounts, or
unpublished context. When a workflow depended on those details, it was either
generalized or omitted.
