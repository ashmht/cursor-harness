# Session Learnings

Max 20 entries. Eviction policy:

- Score each entry on **recency** (check `last-used` date; >30 days = low) and **blast radius** (one-off = low).
- Remove lowest-scoring entries first.
- Consolidate related entries into grouped entries before dropping.
- Format: `- [YYYY-MM-DD] Entry text here` — the date is when the entry was last useful, not when it was added. Update the date each time an entry prevents a mistake.

## Patterns and Gotchas

- [2026-09-22] Export personal agent setup with an allowlist, not a home-directory mirror. Template account configuration; exclude plugin caches, runtime state, private overlays, and symlinks to other repositories.
- [2026-09-22] A public-data audit must inspect the current tree, commit author metadata, and historical blobs. Rewriting only the latest files does not remove old emails, hostnames, or identifiers from visible history.
- [2026-09-22] Do not redistribute an imported skill without a discoverable license. Retain required notices, replace it with an original implementation, or exclude it.

## Workflow Preferences

- [2026-09-22] Installers should dry-run by default, preflight every conflict before the first write, reject symlinks, and create backups before forced replacement.
