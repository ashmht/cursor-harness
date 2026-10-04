# Agent instructions

Portable checks for this repository. Cursor session behavior lives in `.cursor/rules/`.

## Before handing off

```bash
python3 scripts/validate.py
bash -n hooks/session-cost.sh
python3 scripts/install.py --target /tmp/cursor-harness-test
```

## Boundaries

- This repo is the harness, not an application. Change rules, skills, hooks, and their checks.
- Do not commit generated indexes, knowledge graphs, hook state, or cost logs.
- A code graph belongs in an application repo. Use a description-triggered rule, and keep working if the graph is missing.
