---
name: codebase-onboarding
description: >-
  Build a verified, visual onboarding skill for any company's codebase: a
  "<company>-expert" folder with a glossary, system map, data model, product
  capability to code map, traced flows, recipes, debugging runbooks, vendors,
  internal tools, and (for staff-level onboarding) architecture decisions,
  migrations in flight, ownership, the path to production, scale and SLOs, and
  trust boundaries. Ships a citation checker that fails when cited code moves,
  a card builder, and an HTML renderer for the visual map. Use when joining a
  new company or startup, onboarding someone else, or when the user asks to
  "map the codebase", "build an onboarding guide", "make a <company>-expert
  skill", or "help a staff engineer ramp up".
---

# Codebase onboarding

Produce an onboarding skill that lives inside the target repo, so every future agent and person loads
the same verified map. The output is a folder, not a chat answer.

## What you produce

```
<skill-root>/<company>-expert/
  SKILL.md                    30-second version, five facts, "what to read" table, skill router
  maintaining.md              file roles, freshness steps, stale docs elsewhere, how to teach it
  onboarding.config.json      path roots for the checker, display prefixes for the card
  card.json                   the teaching card (analogy, diagrams, quiz); capabilities are generated
  codebase-map.html           rendered from card.json; never edited by hand
  references/
    glossary.md               terms, and pairs people mix up
    system-map.md             what runs where, stacks, hosts, entry points
    data-model.md             core models, ids, renames, datastores
    capabilities.md           each product capability: code, flow, vendors, runbook, owner, skill
    flows.md                  request-time traces of the flows that matter
    recipes.md                how to make the common changes
    debugging.md              method, runbooks, symptom table
    vendors.md                outside systems the product calls
    tools.md                  tools engineers use: observability, data, flags, CI, local dev, admin
    decisions.md              staff: why it is built this way, migrations in flight, debt
    ownership.md              staff: who owns what, how decisions get made, on-call
    operations.md             staff: path to production, rollback, scale numbers, SLOs, incidents
    security.md               staff: trust boundaries, auth, sensitive data, compliance scope
    onboarding-path.md        day 1, week 1, and a 30/60/90 for staff
  scripts/
    lint_skill.py             fails on unfilled placeholders, broken links, missing staff files
    check_citations.py        fails when a cited path or line no longer exists
    build_card.py             copies capabilities.md into card.json and re-renders
    render_card.py            card.json to HTML
```

The four staff files are optional for a new-engineer onboarding and required for a staff one.

## Workflow

1. **Scope.** Ask who it is for (new engineer, staff engineer, agents only) and where skills live in the
   repo (`.cursor/skills/`, `.claude/skills/`, `.ai-skills/`). Read the repo's own agent docs first.
2. **Scaffold.** From the target repo root:

   ```bash
   python3 <this-skill>/scripts/scaffold.py --company "Acme" --dest .cursor/skills/acme-expert
   ```

   It copies `templates/`, fills the company name, today's date and the current commit, and refuses
   to overwrite an existing folder unless you pass `--force`. Add `--ci` to also write a GitHub
   Actions workflow that runs all three checks on PRs touching the skill and every Monday, which
   catches citations broken by code changes elsewhere. Set `audience` in `onboarding.config.json` to
   `new` if the staff files aren't wanted.
3. **Discover.** Follow [references/discovery.md](references/discovery.md). It lists, per file, the
   commands that surface the facts (entry points, manifests, webhooks, CODEOWNERS, CI, git history).
   Use parallel explore subagents for large repos, one per area, and spot-check what they return.
4. **Draft.** Fill each template. Every `<...>` placeholder and HTML comment is an instruction; delete
   it once filled. Staff files follow [references/staff-lens.md](references/staff-lens.md).
5. **Draw.** Build the diagram set in [references/visuals.md](references/visuals.md) into `card.json`,
   then run `scripts/build_card.py` to pull in the capability table and render the HTML.
6. **Verify.** Run `scripts/lint_skill.py` until it reports 0 errors (a fresh scaffold fails it on
   purpose; the citation checker alone passes an empty skill, because it skips `<...>` placeholders).
   Then run `scripts/check_citations.py` until it reports 0 errors and 0 warnings, then the
   two-test review loop in [references/review-loop.md](references/review-loop.md) until two rounds in
   a row pass, capped at 10.
7. **Ship.** Open a PR in the target repo. Add the skill to the repo's skill index if it has one.

## Rules for claims

These are what keep the map trustworthy. Each one exists because breaking it produced a wrong
onboarding doc that someone acted on.

- **Cite before asserting.** Every claim that code exists or behaves a certain way gets a `path` or
  `path:line` you opened. No citation means "I believe", or go check.
- **Never assert absence from a failed search.** Search the concept under two or more names, run
  `git log -S'<term>'`, and check the sibling domain. Still nothing: write "searched A, B, C and did
  not find it", never "there is no X".
- **Legacy only when the code says so.** Mark something legacy, retired or deprecated only with a
  citation to the comment, flag, removal commit or doc that says it. Otherwise it is active or
  "unclear", and unclear means you could not tell, not that it looks old.
- **Name your tree.** Stamp every reference file with the commit it was verified against. Never
  describe a feature branch as `main`.
- **The code wins.** When a repo doc disagrees with the code, the map follows the code and records
  the disagreement in `maintaining.md` under "Known stale docs".
- **One source of truth per fact.** References are the source; the card summarizes them; the HTML is
  generated. Capabilities live only in `capabilities.md`.
- **Public-safe by default.** No secrets, tokens, customer data, personal emails or internal hostnames
  that the repo itself doesn't already expose. Numbers (traffic, revenue, SLOs) need a source and a date.

## Staff coverage gate

A staff engineer is ready to lead work when the skill answers all of these. Treat a missing answer as a
failed review round, not a nice-to-have.

| Question | File |
|---|---|
| Why is it built this way, and which alternatives were rejected? | `decisions.md` |
| Which migrations are half done, and how do I tell which side a piece of code is on? | `decisions.md` |
| Who owns each area, who decides cross-team changes, and who is on call? | `ownership.md` |
| How does a commit reach production, how do we roll back, and what gates it? | `operations.md` |
| What are the scale numbers and SLOs, and where do I see them live? | `operations.md` |
| What were the last few serious incidents, and what changed after them? | `operations.md` |
| Where are the trust boundaries, and which code touches money, credentials or personal data? | `security.md` |
| Which product capability does each folder serve, and which vendor sits behind it? | `capabilities.md`, `vendors.md` |
| Where is the highest-leverage work: the riskiest systems and the slowest feedback loops? | `onboarding-path.md` |

## Keeping it fresh

The generated `maintaining.md` carries the freshness steps. In short: `scripts/lint_skill.py` warns
when a stamp is older than `max_age_days` (default 90); then run
`scripts/check_citations.py --since <stamped commit>`, re-read every citation into the files it lists,
fix the Markdown, run `scripts/build_card.py`, and restamp the commit.
