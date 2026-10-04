---
name: loop-html-doc
description: >-
  HTML documentation loop — standalone reference or analysis pages with dark
  theme, scannable layout, Boeing-747 visual satisfaction iteration, Evans
  walkthrough + Fowler definition boxes, humanizer. Use for HTML docs, visual
  explainers, offline reference pages, wiki HTML exports, or when the user says
  "HTML doc loop", "best HTML docs", or "visual concept page". Prefer canvas
  skill for live interactive Cursor artifacts; use this loop for persistent .html files.
---

# Loop: HTML Doc

**Based on:** FF #021 Boeing 747 benchmark (iterate until visually satisfied)

## Copy the loop

```
Create a standalone HTML document: [title] for [audience].

PHASE 1 — CHOOSE DELIVERABLE
- Interactive analysis in Cursor session → use Cursor's optional built-in
  Canvas skill when available; otherwise continue with this persistent HTML loop
- Persistent file the user opens in browser → continue this loop
- Engineer working page (todos, standup) → use a dedicated task-dashboard workflow

PHASE 2 — STRUCTURE
Required sections:
- Header: title, one-line BLUF, last-updated
- Table of contents (anchor links)
- Body: scannable H2/H3, max 3 sentences per paragraph
- One architecture diagram (mermaid rendered to SVG or clean ASCII in <pre>)
- Fowler Bliki <aside> boxes for defined terms
- Footer: sources, related links

Design system (default):
- Dark theme: bg #0f1117, text #e6edf3, accent #4F46E5
- System-ui font stack; code in monospace
- Responsive: readable at 375px and 1280px
- No markdown tables dumped raw — use HTML layout
- Print-friendly @media print block

PHASE 3 — PROSE
Write the body in the Julia Evans register and asides as Fowler definitions.
Before embedding prose, apply this checklist. Open the humanizer skill only
if a pattern is unclear:
- Remove AI vocabulary, stacked hedges, and em dashes.
- Vary sentence length.
- Do not invent numbers, names, or anecdotes.

PHASE 4 — BOEING 747 LOOP (FF #021, adapted for docs)
Build a repeatable "inspection checklist" — same views every iteration:
- Desktop 1280px
- Mobile 375px
- Print preview
After each significant layout change:
1. Render/inspect those three views (describe what you see)
2. Identify the weakest section (clarity, hierarchy, density, contrast)
3. Improve only that section; preserve what already works
4. Log iteration in /tmp/html-doc-{slug}.md
Stop when you cannot identify another visible issue worth fixing.

PHASE 5 — WRITE FILE
Save to the user-specified path or `./docs/[slug].html`
Confirm: file path, inspection log path, open command (open path on macOS).
```

## Verify / stop

**You are satisfied the HTML doc is clear at desktop, mobile, and print.**

- Boeing 747 inspection checklist shows every required section
- No visible hierarchy/clarity issue worth another iteration
- Prose humanized; Fowler asides distinguish terms
- File saved and path reported

## When to use

- Durable reference pages outside Cursor
- Architecture diagrams + narrative in one shareable file
- State-machine references, analysis dashboards, and system walkthroughs

## Related skills

| Need | Skill |
|------|-------|
| Live interactive artifact | Optional Cursor Canvas; HTML fallback when absent |
| Daily engineer todo page | A dedicated task-dashboard workflow |
| Dark architecture diagram only | `~/.cursor/skills/architecture-diagram/SKILL.md` |

## Memory

`/tmp/html-doc-{slug}.md` — iteration log, inspection notes, weakest-section history.
