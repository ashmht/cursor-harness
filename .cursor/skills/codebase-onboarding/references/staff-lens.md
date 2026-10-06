# The staff lens

A new engineer needs to know what exists and how to change it safely. A staff engineer is hired to
change the shape of things: pick which problems matter, steer migrations, and make calls other teams
live with. That needs four things the basic map doesn't carry: the reasons behind the current design,
who owns and decides what, how the system ships and fails, and where the risk and leverage sit.

## decisions.md

- **Decisions that shaped the system.** Five to ten, each with the choice, the alternatives, the
  reason as recorded (ADR, RFC, PR description, commit message), and what it costs today. If no
  record exists, say so; don't invent the reason.
- **Migrations in flight.** A table: from, to, how far along (with evidence), how to tell which side
  a piece of code is on, what new code should do, who owns it. This is the single most useful table
  for a staff engineer, because most cross-team friction comes from half-finished moves.
- **Deprecated but still live.** Code that is marked legacy and still serves traffic, with the
  citation for both facts.
- **Known debt with blast radius.** Not a wish list: the items that cause incidents, slow every
  change in an area, or block a strategic move.

## ownership.md

- Areas to owning teams, from `CODEOWNERS` or a service catalog, with the citation.
- How cross-team decisions get made: RFC process, architecture review, who approves schema or API
  changes.
- On-call: rotations, paging tool, escalation path.
- Review norms: required reviewers, bots, merge gates.

## operations.md

- **Path to production.** Diagram and steps: PR checks, merge queue, build, deploy targets, rollout
  (flags, canaries, percentages), rollback, and how schema migrations and mobile releases differ.
- **Environments.** What exists (local, preview, staging, production), what data each uses.
- **Scale and SLOs.** Requests, jobs, data volume, latency budgets, availability targets, each with a
  source and date, plus the dashboard that shows it live.
- **Incidents.** The last three to five serious ones: what broke, why, what changed after. Link the
  postmortems.
- **Cost hotspots**, if the repo or the user can source them.

## security.md

- Trust boundaries diagram: where untrusted input enters, where auth happens, where privileges rise.
- Authentication and authorization model, with the code that enforces it.
- Sensitive paths: money movement, credentials, personal data, admin tooling.
- Compliance scope as enforced in code (for example a card-data vault or audit logging), not as a
  list of certificates.

## onboarding-path.md: 30/60/90 for a staff engineer

- **Days 1 to 30, learn:** run the system locally, trace the main money or access flow end to end,
  read every migration-in-flight row, sit on call as a shadow, ship one small fix in each of two areas.
- **Days 31 to 60, map:** write down the top risks and the slowest feedback loops (build time, flaky
  suites, deploy frequency, review latency) with numbers, and check them with the owners.
- **Days 61 to 90, lead:** pick one migration or one reliability gap, write the plan, and get it
  agreed across the teams it touches.

The template carries these as prompts; fill them with this company's systems, not generic advice.
