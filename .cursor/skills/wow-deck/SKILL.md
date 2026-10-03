---
name: wow-deck
description: >-
  Generate a stunning, self-contained, fully-offline HTML slide deck that opens in any
  browser with zero dependencies. Bakes in the 2026 best-in-class deck design system
  (massive display type, dark mode + neon accent, real glassmorphism, bento grids,
  grid+grain background depth, a shimmer signature effect, strategic kinetic motion,
  prefers-reduced-motion, WCAG-minded contrast) and an anti-slop checklist (no
  Inter/Roboto as display, no purple-on-white, no flat backgrounds, no fixed px sizes,
  no over-animation). Authors content as JSON; a Python script renders one .html file
  with keyboard/touch nav, a speaker-transcript panel (press S), an overview grid, and
  deep-linkable slides. Use when the user asks to build a presentation, slide deck,
  pitch deck, keynote, "wow slides", a talk, or to turn a doc/plan into slides. Pair the
  prose with a voice rule (~/.cursor/rules/<voice>.mdc) and run framing.mdc's anti-em-dash
  + anti-AI pass on all on-slide and transcript text before rendering.
---

# Wow Deck

Build presentation decks that look like a 2026 product-keynote, not a default template.
One `.html` file, no build step, no network, runs from a thumb drive or a locked-down
conference wifi.

## When to use

- "make me a presentation / slide deck / pitch / keynote"
- "turn this doc/plan/RFC into slides"
- "I'm presenting X, build the deck"
- "make these slides look amazing / wow"

For a scrolling reference page (not a slide deck), use `loop-html-doc` instead.
For a live interactive Cursor artifact, use the `canvas` skill.

## The workflow

1. **Scope the deck (Socratic, brief).** Audience (peers / committee / leadership), what
   the deck must do (share a plan vs. ask for approval vs. teach), runtime, and the one
   thing they must remember. If the user has a source doc, read it.

2. **Pick the structure.** Default to the approval/sharing spine that tests well
   (winningpresentations Approval Packet + PSVM "why now"):
   `hook → problem (quantified) → why now (closing window) → options (steel-man rejected)
    → solution → why best-in-class → proof (real code/data) → before/after → rollout
    → risk box (with kill-switch) → what's next`.
   Cut to 6 for a pure decision audience; keep proof slides for engineers.

3. **Write the prose in voice.** Pick ONE voice rule from `~/.cursor/rules/` (larson for
   asks/status, pragmatic-engineer for findings, patio11 for dollarized impact). Then run
   `~/.cursor/rules/framing.mdc`: BLUF, owned claims, varied sentence rhythm, **no
   em-dashes**, no AI tells. This applies to BOTH on-slide text and the speaker transcript.

4. **Author content.json.** One object per slide (types below). Put the spoken script in
   `notes` (string or list). Keep on-slide text short; the transcript carries the words.

5. **Render.**
   ```bash
   python3 ~/.cursor/skills/wow-deck/build_deck.py content.json -o deck.html --accent "#38e1d6"
   ```
   The script self-checks for external deps and Inter, and prints warnings.

6. **Inspect against the rubric (below).** Open it (`open deck.html`). Check desktop +
   mobile + the speaker panel (press S). Fix the weakest slide. Stop when it scores
   >=27/30 and you can't find another visible upgrade.

## Content JSON

Top level: `{ "title", "accent"?, "footerLeft"?, "slides": [...] }`.
`accent` is the neon hex (drives orbs, kicker, progress bar, gradients). Default `#38e1d6`.

Every slide: `{ "type": "...", "notes": "..."|[...], "navTitle"? }`. Inline HTML is allowed
in headings, labels, bullets, callouts (use `<span class="em">gradient text</span>`,
`<span class="mono">code</span>`, `<b>`). Code slides use colored spans:
`<span class="k">keyword</span> <span class="s">"string"</span> <span class="f">func</span>
 <span class="c"># comment</span> <span class="n">CONST</span>`, and `<span class="hl">...</span>`
to highlight a line. Diff code uses `<span class="del">` / `<span class="add">`.

### Slide types

| type | fields |
|---|---|
| `hook` | `quote`, `by`, `turn` (cold open; quote can hold `<span class="em">`) |
| `bento` | `kicker`, `heading`, `tiles:[{stat?,label?,hero?,wide?,tone?,size?}]` (hero spans 2 rows; wide spans 2 cols) |
| `split` | `kicker`, `heading`, `lead?`, `left:{title,bullets,tone}`, `right:{...}`, `callout?` |
| `options` | `kicker`, `heading`, `cards:[{title,bullets,tone,reco?}]` (mark one `reco:true`) |
| `pipeline` | `kicker`, `heading`, `stages:[{layer,desc}]`, `callout?` |
| `code` | `kicker`, `heading`, `code` (span-colored), `callout?` |
| `diff` | `kicker`, `heading`, `before:{tag,code}`, `after:{tag,code}`, `chips:[..]` |
| `list` | `kicker`, `heading`, `items:[..]`, `callout?` |
| `table` | `kicker`, `heading`, `columns:[..]`, `rows:[[cell,..]]`, `callout?` (use `<span class="pill md">` for risk pills) |
| `statement` | `kicker?`, `big`, `sub?` (one massive centered line) |

`tone` values: `bad`/`danger` (red), `good` (green). `callout` is a string or
`{tone:"accent|green|amber|red", text}`. The `accent` callout gets the shimmer signature effect.

See `example.json` for a working 4-slide deck.

## The rubric (score before shipping, target >=27/30)

From 2026 design research (visualbest, slideegg, inkppt, skills-slides anti-slop):

1. Massive hero typography that reads from the back row /3
2. Bento-grid modular layout where content is mixed (not bullet walls) /3
3. Dark mode + neon accent, OLED-friendly, premium not loud /3
4. Glassmorphism as an accent (frosted panels, not every surface screaming) /3
5. Strategic kinetic motion (reveals/guides; never spinning/flying) /3
6. Distinctive display font + monospace for code (NEVER Inter/Roboto/Arial) /3
7. Background depth: orbs + grid + grain (never flat solid) /3
8. prefers-reduced-motion honored + WCAG AA contrast /3
9. A signature visual effect that makes it memorable /3
10. Self-contained, offline, projector + mobile responsive /3
11. Screen-reader navigation announces "Slide N of M: title" through the built-in live region

**Anti-slop hard-fails (rebuild if present):** Inter/Roboto as display font, purple
gradient on white, flat solid background, fixed px font sizes, over-animation (flying
bullets, spin transitions). The build script catches the first two automatically.

## Hard constraints (don't break these)

- **Offline always.** No CDN, no web fonts, no `<script src>`. The font stack uses
  OS-native premium faces (SF Pro / Segoe Variable) so it's distinctive without a download.
- **No Mermaid.** Hand-build diagrams with CSS/SVG (pipeline, bento, aggregate seams). A
  CDN dependency dies on conference wifi.
- **No em-dashes** in any human-facing text (framing.mdc). En-dashes in numeric ranges
  (`6-9`, `08-11`) are fine.
- **Speaker transcript lives in `notes`,** off the projector, toggled with `S`.

## Controls (built into every deck)

`←/→` or click (right half forward) navigate · `S` speaker transcript · `F` fullscreen ·
`O` overview grid · number keys jump · `#N` in the URL deep-links slide N.

## Files

- `build_deck.py` — the generator (design system + renderers + self-checks).
- `example.json` — minimal working content file; copy and edit.

## Provenance

Design system distilled from iterative deck reviews and current presentation
design research. If a new pattern consistently improves real presentations,
add it to `build_deck.py`'s template and update the rubric here.
