# Maintaining the {{skill_name}} skill

For whoever updates this skill or teaches from it.

## What each file is for

| File | Holds | Source of truth? |
|---|---|---|
| `SKILL.md` | 30-second version, five facts, "what to read", skill router | Yes |
| `references/*.md` | Everything else, one topic per file | Yes |
| `references/capabilities.md` | The capability map; the card's table is generated from it | Yes |
| `card.json` | The teaching card. Its `capabilities` line is generated | No, it summarizes the references |
| `{{html}}` | Rendered from `card.json` | No, never edit it |
| `onboarding.config.json` | Path roots for the checker; display prefixes and intro for the card | Yes |

## Keeping it fresh

Every reference starts with the commit it was verified against. Before trusting a claim from a stale
skill, or after editing it, run from the repo root:

```bash
python3 {{dest}}/scripts/lint_skill.py
python3 {{dest}}/scripts/check_citations.py --since <stamped commit>
```

`scripts/lint_skill.py` fails on unfilled placeholders, leftover instruction comments, broken links or
anchors, and missing staff files, and warns when a stamp is older than `max_age_days` in
`onboarding.config.json`. The citation checker reports:

- **ERROR:** a cited file is gone, or a cited line is past the end of the file. Exits 1.
- **WARN:** the code near a cited line no longer names the identifier the sentence names, or a bare
  filename matches several files.
- **INFO:** a deprecation marker near a cited line or in the cited file's header. Confirm the skill
  calls that code legacy, or point it at the replacement.

A clean run does not prove the claims are true. `--since` lists cited paths that changed; re-read each
citation into them by hand. The checker skips citations starting with the skill's own folder, `http`
or `/`, and any containing `*`, `<` or `...`. Then:

1. Fix the Markdown.
2. If `references/capabilities.md` changed: `python3 {{dest}}/scripts/build_card.py` (`--check`
   exits 1 when the card is out of date).
3. If anything the card repeats changed (diagrams, traced flow, quiz), edit `card.json` and run
   `python3 {{dest}}/scripts/render_card.py {{dest}}/card.json -o {{dest}}/{{html}}`.
4. Restamp each reference and `card.json` with the commit you checked against.

## Known stale docs

Other docs in the repo that disagree with the code. Fix the doc when you can, then delete the row.

| Doc says | Code says |
|---|---|
| <`doc path:line`: claim> | <what the code does, with citation> |

## Teaching it to a person

Walk them through `{{html}}`: the one-liner, the analogy, the diagrams, the capability table (ask
which row their first ticket lands in), the traced flow, then the hard questions. End with "Check
yourself". If they can give the 60-second teach-back from memory, they're ready for a ticket. For a
staff engineer, follow with [onboarding-path.md](references/onboarding-path.md).
