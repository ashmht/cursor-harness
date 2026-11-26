# Humanizer

A Cursor and Claude Code skill that removes AI writing tells without inventing
the author's facts, stakes, or experiences. No dependencies or network calls.

## What it does

- Detects **52 AI writing patterns** (P1-P52, including register, grounding, fabricated-specificity, and self-reference checks)
- Rewrites text to sound like a specific human wrote it
- Preserves the fabrication boundary: mechanical fixes are automatic; substantive gaps are flagged for the author
- Three modes: scan-only, full rewrite, in-place file editing
- Uses the selected `.mdc` voice rules first; generic profiles remain available as an explicit fallback
- Supports calibrated and Slack-native output
- Zero dependencies. Pure Markdown.

## Installation

### Cursor

```bash
mkdir -p ~/.cursor/skills/humanizer
cp -R .cursor/skills/humanizer ~/.cursor/skills/
```

The repository-level installer handles this path automatically.

### Other agent runtimes

Copy the full directory into that runtime's user-skill location. Keep
`references/` beside `SKILL.md`.

### Usage

```
# Full rewrite (default)
/humanizer "Your AI-sounding text goes here"

# Scan only: report patterns without changing text
/humanizer "text" --mode detect

# Score the AI-tell density (0-100, lower is more human)
/humanizer "text" --mode detect --score

# Edit a file in place
/humanizer --mode edit --file src/docs/README.md

# Specify voice
/humanizer "text" --voice casual

# Aggressive mode + iterate to convergence (max 3 passes)
/humanizer "text" --aggressive --iterate 3

# Layer purpose-specific rules on top of voice
/humanizer "text" --voice warm --purpose marketing
```

### Voice options

| Voice | Best for |
|---|---|
| `casual` | Blog posts, social media, informal docs |
| `professional` | Business communication, formal docs |
| `technical` | API docs, READMEs, code comments |
| `warm` | Tutorials, onboarding, support content |
| `blunt` | Internal comms, reviews, direct feedback |

### Purpose presets (`--purpose`)

Layered on top of voice. Add content-type rules without losing voice flavor.

| Purpose | Effect |
|---|---|
| `essay` | No contractions, formal headings, structured arguments |
| `email` | Greetings allowed, signoff allowed, no markdown |
| `marketing` | Short paragraphs, concrete benefits, one CTA at end |
| `technical` | Code blocks preserved, precise jargon retained |
| `general` | No purpose-specific overrides (default) |

### Brand voice file

Drop a `humanizer-context.md` at the project root with your samples and banned phrases. Auto-loaded if present.

## How it works

1. **Parse**: Extracts text and flags from arguments
2. **Detect**: Scans for 52 AI patterns across seven categories
3. **Rewrite**: Applies mechanical fixes and the selected voice without fabricating substantive detail
4. **Verify**: Checks output against detection patterns, sentence variance, and the "who wrote this?" test
5. **Output**: The rewritten text, then at most a few sentences of editor's notes and up to three questions for facts it could not supply. Detect mode is a short plain-prose note, strongest passage first, with pattern numbers in parentheses. No report headers, severity labels, or per-pattern Why/Fix blocks.

Rewrites are checked for the fingerprint subtractive editing leaves behind: every paragraph in the same claim-support-kicker shape, staccato fragments, and label scaffolding. A blind study of blader/humanizer ([#229](https://github.com/blader/humanizer/issues/229)) found its pass cut AI vocabulary hits from 70 to 0 while uniform-rhythm hits rose from 60 to 101.

## Pattern categories

| Category | Patterns | Examples |
|---|---|---|
| Content | P1-P8 | Significance inflation, notability name-dropping, -ing phrases, copula avoidance |
| Language & Style | P9-P18 | Negative parallelisms, em dash overuse, bold abuse, list syndrome |
| Communication | P19-P21 | Chatbot artifacts, disclaimers, sycophancy |
| Filler & Hedging | P22-P30 | Filler phrases, hedging, generic conclusions, uniform sentence length |
| Emerging (2026) | P31-P43 | Elegant variation, citation leaks, tracking URLs, register shifts, treadmill prose |
| Register & Grounding (2026) | P44-P46 | Over-explained context, stakelessness, fabricated specificity |
| Staging & Self-reference (2026-11) | P47-P52 | Arguing with no one, sayings that sound deep, colon reveals, writing about the document, vague association, repeated openings |

## Credits

Built from research across:
- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- [blader/humanizer](https://github.com/blader/humanizer) v3.1 and v4.0.0 (strongest-first ranking, weak-alone patterns, embedded mode; from v4: arguing with no one, sayings that sound deep, writing about the document, vague association, en dash rule, input-as-material). v4's change to let the rewrite add facts is deliberately not adopted.
- [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) (smallest edit that works, colon reveals, lone-expert setups, delete fake-profound closers)
- [milock/humanizer](https://github.com/milock/humanizer) (claim-preservation check, technical-sense exemption, stet)
- [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) ("never inject these" rewrite guardrails)
- [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop)
- Davila7 claude-code-templates (humanizer + writing-clearly-and-concisely)
- William Strunk Jr., *The Elements of Style* (1918)
- Community research from Reddit, HackerNews, and writing communities

## License

MIT
