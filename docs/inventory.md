# Export inventory

This repository is an allowlisted export of a personal Cursor setup. It is not
a mirror of the entire Cursor home directory.

## Included

- Session workflow, memory-bank conventions, progress tracking, and reusable
  engineering rules.
- Voice and writing rules that contain no workplace-specific examples.
- Portable authored skills for documentation, teaching, presentations,
  reviews, handoffs, writing, and multi-agent investigations.
- A local session-cost hook that stores estimates under the user's Cursor home.
- Sanitized examples for CLI preferences, editor settings, keybindings, hooks,
  and public MCP integrations.
- A dry-run-first installer and layered repository validator.
- `AGENTS.md`: the portable handoff checks that apply outside Cursor.

## Intentionally excluded

- Employer, customer, merchant, incident, ticket, and production-system
  material.
- Work-only domain skills, service experts, operational runbooks, and database
  safety controls.
- Raw account metadata, authentication identifiers, OAuth client IDs, tokens,
  private document IDs, remote hosts, and absolute home-directory paths.
- Runtime state, transcripts, cost logs, hook state, generated reports,
  knowledge-graph output such as `graphify-out/`, and local memory.
- Cursor-maintained built-in skills and plugin caches. Those should be installed
  from their upstream source instead of vendored here.
- Symlinked skills whose canonical source is another repository.

## Selection rule

A file is included only when another user can understand and run it without
access to the original author's employer, workstation, private accounts, or
unpublished context. When a workflow depended on those details, it was either
generalized or omitted.
