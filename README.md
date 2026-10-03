# Cursor Harness

A portable personal setup for Cursor: session protocols, reusable rules,
authored skills, memory-bank patterns, editor templates, and validation gates.

The repository is intentionally public-safe. It contains no raw account
configuration, workplace-specific workflows, private service endpoints,
credentials, runtime state, or plugin caches.

## What is here

- `.cursor/rules/`: workflow, reasoning, writing, voice, and engineering rules.
- `.cursor/skills/`: reusable skills for documentation, teaching, handoffs,
  presentations, writing, reviews, and multi-agent investigations.
- `.memory-bank/`: a small example of durable cross-session learning.
- `hooks/`: a local-only session cost estimator with no network calls.
- `templates/`: sanitized examples for Cursor CLI config, MCP servers, hooks,
  editor settings, keybindings, and personal instructions.
- `scripts/install.py`: a dry-run-first installer for rules, skills, and hooks.
- `scripts/validate.py`: layered privacy, portability, secret, structure, and
  syntax validation.

See [the export inventory](docs/inventory.md) for the inclusion and exclusion
boundary.

## Quick start

Clone and validate:

```bash
git clone https://github.com/ashmht/cursor-harness.git
cd cursor-harness
python3 scripts/validate.py
```

Preview installation into `~/.cursor`:

```bash
python3 scripts/install.py
```

Apply only after reviewing the plan:

```bash
python3 scripts/install.py --apply
```

Existing files are never replaced by default. To back them up and install the
repository version:

```bash
python3 scripts/install.py --apply --force
```

The installer handles rules, skills, and hook scripts. Configuration templates
are manual because blindly replacing editor, CLI, hook, or MCP configuration
can remove existing integrations.

## Configuration templates

- `templates/cli-config.example.json`: preferences only, with identity and team
  metadata removed.
- `templates/mcp.example.json`: public integrations with no credentials or
  account-specific OAuth values.
- `templates/hooks.example.json`: session-cost hook registration.
- `templates/settings.example.jsonc`: portable editor and monorepo-performance
  settings.
- `templates/keybindings.example.json`: the personal Agent shortcut.
- `templates/claude-personal.md`: a small personal instruction template.
- `templates/harness.yaml.example`: project roots, context files, and build
  gates for a local `.cursor/harness.yaml`.

Merge the desired keys into the corresponding local file. Keep credentials and
account metadata outside version control.

The hook template points to `${HOME}/.cursor/hooks/session-cost.sh`, which is
where the installer places the script. Merge those hook entries into
`~/.cursor/hooks.json` after installation.

## Repository harness

Copy the repository-level pieces into another project:

```text
.cursor/rules/workflow.mdc
.cursor/rules/lang-memory-bank.mdc
.memory-bank/
templates/claude-personal.md
```

The global installer does not copy `.memory-bank/` because project memory
belongs in each repository. Copy that directory explicitly when bootstrapping a
new project; the workflow treats it and `CLAUDE.md` as optional when absent.

Copy `templates/harness.yaml.example` to `.cursor/harness.yaml`, customize the
project roots and commands, and keep it untracked. The workflow reads it when
present and otherwise infers the project from repository context.

## Validation

The native validator runs five fail-closed layers:

```bash
python3 scripts/validate.py
```

For a private employer or client denylist, pass terms at runtime without
committing them:

```bash
CURSOR_HARNESS_FORBIDDEN_TERMS_JSON='["company-name","internal-domain.example"]' \
  python3 scripts/validate.py
```

See [validation details](docs/validation.md). CI runs the native validation,
shell syntax check, and installer dry run on every change.

## Design principles

- Allowlist exports instead of mirroring a home directory.
- Prefer templates over raw account configuration.
- Keep plugin and built-in skills at their upstream source.
- Make installation non-destructive and inspectable.
- Separate project context from reusable behavior.
- Persist lessons, but evict stale or low-value memory.
- Stop and hand off before long sessions become expensive or incoherent.

## License

MIT. Individual imported skills retain their own attribution and license files
where present. See [provenance](docs/provenance.md) and
[third-party notices](THIRD_PARTY_NOTICES.md).
