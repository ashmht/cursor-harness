# Humanizer

A Cursor and Claude Code skill that removes AI writing tells without inventing
the author's facts, stakes, or experiences. No dependencies or network calls.

## What it does

- Detects **46 AI writing patterns** (P1-P46, including register, grounding, and fabricated-specificity checks)
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
2. **Detect**: Scans for 46 AI patterns across six categories
3. **Rewrite**: Applies mechanical fixes and the selected voice without fabricating substantive detail
4. **Verify**: Checks output against detection patterns, sentence variance, and the "who wrote this?" test
5. **Output**: Clean text with change summary

## Pattern categories

| Category | Patterns | Examples |
|---|---|---|
| Content | P1-P8 | Significance inflation, notability name-dropping, -ing phrases, copula avoidance |
| Language & Style | P9-P18 | Negative parallelisms, em dash overuse, bold abuse, list syndrome |
| Communication | P19-P21 | Chatbot artifacts, disclaimers, sycophancy |
| Filler & Hedging | P22-P30 | Filler phrases, hedging, generic conclusions, uniform sentence length |
| Emerging (2026) | P31-P43 | Elegant variation, citation leaks, tracking URLs, register shifts, treadmill prose |
| Register & Grounding (2026) | P44-P46 | Over-explained context, stakelessness, fabricated specificity |

## Credits

Built from research across:
- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- Softaworks agent-toolkit humanizer by @blader
- Davila7 claude-code-templates (humanizer + writing-clearly-and-concisely)
- William Strunk Jr., *The Elements of Style* (1918)
- Community research from Reddit, HackerNews, and writing communities

## License

MIT
