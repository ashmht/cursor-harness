# Onboarding path

Verified against commit `{{commit}}` ({{date}}). Paths are repo-relative.

## Day 1

1. Read `{{html}}` end to end and do "Check yourself".
2. Get the system running locally (`<command>`).
3. Trace <the main flow> with a real request.

## Week 1

1. Ship one small change using a recipe from [recipes.md](recipes.md).
2. Debug one real issue with [debugging.md](debugging.md).

## Staff: 30/60/90

**Days 1 to 30, learn.** Run the system, trace the main money or access flow end to end, read every
row of "Migrations in flight" in [decisions.md](decisions.md), shadow on call, ship a small fix in two
different areas.

**Days 31 to 60, map.** Write down the top risks and the slowest feedback loops with numbers:

| Loop | Today | Source |
|---|---|---|
| <CI time, flaky rate, deploy frequency, review latency, local setup time> | <value> | <source> |

Check each with the owning team in [ownership.md](ownership.md).

**Days 61 to 90, lead.** Pick one migration or reliability gap, write the plan, get it agreed across
the teams it touches.

## Where the leverage is

| Area | Risk or drag | Evidence | Owner |
|---|---|---|---|
| <system> | <what goes wrong or slows people down> | <citation or number> | <team> |
