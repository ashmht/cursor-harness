# Discovery: where each fact comes from

Run these from the target repo root. They are starting points: read what they return, then cite the
file you actually opened. Prefer `rg` and `git` over guesses from directory names.

## Before anything

```bash
git rev-parse --abbrev-ref HEAD
git fetch origin --quiet && git log -1 --oneline origin/HEAD
ls; cat README* AGENTS.md CLAUDE.md CONTRIBUTING.md 2>/dev/null | head -200
```

Rebase onto the default branch before you stamp anything. Read the repo's own agent docs and
conventions first; they are also your first source of stale claims.

## system-map.md

| Fact | Where to look |
|---|---|
| Top-level areas and their stacks | Top-level directories; each one's manifest (`package.json`, `Gemfile`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `build.gradle*`, `Package.swift`) |
| Workspaces and packages | `pnpm-workspace.yaml`, `turbo.json`, `nx.json`, Cargo or Go workspaces |
| Entry points | HTTP routes (`config/routes*`, `urls.py`, router files), GraphQL schema roots, gRPC service definitions, CLI `main` functions, worker and queue definitions |
| Where it runs | `infra/`, `terraform/`, `pulumi/`, `k8s/`, `helm/`, `Dockerfile*`, `docker-compose*`, `wrangler.*`, `vercel.json`, `fly.toml`, `Procfile` |
| How services talk | gRPC protos, queue or topic names (`rg -n "topic|queue" config`), webhook routes, shared client libraries |

## data-model.md

| Fact | Where to look |
|---|---|
| Tables and columns | `db/schema.rb`, `structure.sql`, `schema.prisma`, migrations folder, ORM model files |
| Public ids versus internal ids | Id prefix or slug helpers (`rg -n "prefix|tag|slug" app/models`), API serializers |
| Renamed concepts | Model names that don't match API or UI names: compare model files to serializers and UI copy |
| Other datastores | Clients and configs for caches, search, analytics stores, object storage, ledgers |

## capabilities.md

Start from what the company sells, not from folders: the marketing or pricing pages in the repo, the
navigation of the main app and the admin dashboard, and the public API reference. For each capability,
find its backend folder, its client routes, its flow, its vendors and its owner.

## flows.md and recipes.md

Pick the flows that move money, grant access or lose data when they break. Trace each from the client
call to the last side effect: controller or resolver, service, job, external call, webhook back, state
change. Recipes come from the changes people make weekly: `git log --since=90.days --name-only` and
look for the files that change together.

## debugging.md

| Fact | Where to look |
|---|---|
| Common failures | Error-tracking groupings, incident docs, `rg -n "raise|throw" <hot path>` |
| Runbooks that already exist | `docs/`, `runbooks/`, wiki links in the repo, incident skills |
| Commands | Make, just or npm scripts; repo CLIs; console and log commands |

## vendors.md

```bash
rg -n "webhook" <routes files>
ls config/initializers 2>/dev/null; rg -il "api_key|ENV\[|process.env" <config dirs> | head
rg -n "^gem |\"dependencies\"" Gemfile package.json
ls <services dir> | rg -i "<vendor-ish names>"
```

Order of trust: webhook routes and initializers (live integrations), then service folders, then
dependency manifests (may be unused), then infrastructure code.

## tools.md

Error tracking and APM configs, metrics and log shippers, dashboards referenced in docs, analytics SDK
init code, warehouse and BI references, flag SDKs, CI workflow files (`.github/workflows`,
`.circleci`, `buildkite`), dev tooling (`mise.toml`, `.tool-versions`, `devcontainer.json`, repo CLIs),
secret managers, admin panels.

## decisions.md

```bash
ls docs/adr* docs/rfc* docs/decisions* 2>/dev/null
git log --diff-filter=D --name-only --since=2.years -- '<old area>' | head
git log -S'<old system name>' --oneline | tail -5
rg -n -i "deprecated|legacy|migrat|sunset|retire" --glob '!**/node_modules/**' | head -100
```

Half-done migrations show up as two implementations of one thing, a flag or routing table that picks
between them, and a "do not add new code here" comment.

## ownership.md

`CODEOWNERS`, team fields in service catalogs (`catalog-info.yaml`, `OWNERS`), on-call config or docs,
`git shortlog -sn --since=6.months -- <dir>` for who actually changes an area. Use roles and team
names, not personal details, unless the repo already publishes them.

## operations.md

Deploy workflows and their triggers, environment configs, feature-flag rollout code, migration deploy
steps, mobile release tooling, dashboards and alert definitions, incident or postmortem docs. Numbers
need a source and a date; if the repo has none, ask the user and record who gave it.

## security.md

Auth middleware, session and token code, permission checks, admin access paths, secret management,
encryption helpers, code that handles card data, credentials or personal data, and any compliance
notes. Draw the trust boundaries from where requests cross from untrusted to trusted code.
