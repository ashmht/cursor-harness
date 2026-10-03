---
name: teach
description: >-
  Explain any complex topic so simply, visually, and concretely that you can
  teach it to others AND defend it against hard follow-up questions. Produces a
  "Teaching Card": plain-language hook, an analogy, a diagram, one traced worked
  example, a depth ladder (ELI5 → practitioner → expert), a curveball-defense
  block of anticipated hard questions with crisp answers, a retrieval quiz, and a
  60-second teach-back script. Grounds technical claims against real source/data.
  Use when the user says /teach, "explain X so I can teach it", "help me
  understand X deeply", "ELI5 but then go deeper", "I need to present X", "prep me
  for questions on X", or wants to master something well enough to handle
  curveballs.
disable-model-invocation: true
---

# /teach — Understand it deeply enough to teach it

Goal: take one topic and turn it into a **Teaching Card** — an explanation the
user can (a) deliver to others in plain language, and (b) stand behind when
someone throws a hard follow-up question. The second half is the point. Most
explanations sound good and collapse on the first "but why not X?". This skill
builds the collapse-proof version.

**Built on two proven foundations** (see [reference.md](reference.md) for the science):

- **Feynman Technique** — explain as if to a smart 12-year-old; where you reach
  for jargon or hand-wave, that is your gap; fix it at the source; repeat.
- **The six evidence-based learning strategies** — retrieval practice, spaced
  practice, interleaving, elaboration, concrete examples, dual coding.

The Teaching Card operationalizes both, plus a **curveball defense** module that
red-teams the user's own understanding.

---

## Two modes — match the effort to the ask

- **Quick** (default for a casual "/teach me X"): one-liner + analogy (with its
  seam) + the picture + the single sharpest curveball. ~5 lines. Then offer:
  "want the full Teaching Card?" Don't run the quality streak or full grounding for
  a throwaway question.
- **Full card** (when the user will teach it, present it, or be questioned on it):
  the complete workflow below. This is the mode for "prep me for questions,"
  "explain so I can teach it," or any topic the user is staking credibility on.

If unsure which, produce Quick and offer Full. Never bury a simple question under
the full machinery.

---

## Workflow

Copy this checklist and work top to bottom. Do not skip the grounding or the
gap-hunt — those are what make the difference between "sounds smart" and "is right".

```
Teaching Card build:
- [ ] 0. Scope: one concept, named audience, depth target
- [ ] 1. Ground: verify claims against real source (code / docs / data)
- [ ] 2. Draft the card (8 sections below)
- [ ] 3. Gap-hunt (Feynman): mark every jargon-lean and hand-wave
- [ ] 4. Curveball defense: generate + answer the 6 hardest questions
- [ ] 5. Quality streak: 2 consecutive clean passes (reader + accuracy)
- [ ] 6. Deliver + offer format (chat / markdown / HTML / canvas / slides)
```

### 0. Scope (ask only if genuinely ambiguous)

Pin down three things. Infer sensible defaults rather than interrogating:

- **Concept** — one idea, not a whole field. "How retry deduplication works," not
  "distributed systems." A card that tries to teach everything teaches nothing.
- **Audience** — who receives this? (new hire / XFN partner / exec / the user
  themselves / a specific skeptic). This sets vocabulary and which curveballs matter.
- **Depth target** — where on the ladder does the user need to operate? Presenting
  to execs = strong ELI5 + a few expert caveats. Onboarding a teammate = full ladder.

If the topic is broad, pick the highest-leverage sub-concept and say so.

### 1. Ground before you explain

A confident wrong explanation is worse than none — it fails on the first curveball
and burns the user's credibility. For any factual or technical topic:

- Read the actual source (code, RFC, runbook, schema, dashboard). Do not explain
  from memory when the source is one tool call away.
- For domain topics, route through the relevant expert skill and verify
  load-bearing claims against source code, documentation, or approved runtime
  evidence. Preserve unavailable or stale evidence as an explicit gap.
- Tag any claim you could not verify: `[unverified]`. Never smuggle a guess in as fact.

The truth-seeking rule applies: if the obvious explanation is X, spend one beat on
why it might be wrong before committing.

### 2. Draft the Teaching Card (the output artifact)

Eight sections. Keep each tight. This is the template:

```markdown
# <Topic> — Teaching Card

## The one-liner
<The whole thing in one plain sentence a smart 12-year-old gets. No jargon.
This is the hook you lead with and the thing they'll remember.>

## The analogy
<Map the unknown onto something the audience already owns. Name where the
analogy holds AND where it breaks — a broken-but-unflagged analogy is how
curveballs land.>

## The picture   ← dual coding
<A diagram. Mermaid for flows/state/architecture; ASCII for quick sketches;
a small table for comparisons. The reader should grasp the shape before the words.>

## How it actually works
<One concrete, TRACED worked example. Follow a single real object end to end
(one transaction, one request, one row). Number the steps. No abstract
"the system processes the data" — say what happens to THIS thing.>

## The depth ladder   ← interleaving / flex your altitude
- **ELI5:** <the child version>
- **Practitioner:** <what someone who uses it daily needs>
- **Expert:** <the mechanism + the caveat only operators know>

## Curveball defense   ← the differentiator (see step 4)
<The 6 hardest questions a skeptic asks, each with a crisp answer.>

## Check yourself   ← retrieval practice
<3-5 questions that force recall, not recognition. Include the answers,
collapsed or below. These are what you'd ask your audience — and yourself
tomorrow — to prove it stuck.>

## The 60-second teach-back
<A compressed script the user can say aloud from memory. If they can deliver
this cold, they own the topic.>
```

Not every topic needs all eight at full weight. A process topic leans on the
picture + traced example; a concept topic leans on analogy + curveball defense.
Keep the section, shrink the ones that don't carry weight — but never drop the
one-liner, the traced example, or the curveball defense.

### 3. Gap-hunt (the Feynman step — do not skip)

Re-read the draft as the audience. Mark every place you:

- reached for a term you didn't define in plain words → **define it or cut it**
- wrote "basically / essentially / it just" → **you're hand-waving; open the source**
- skipped a step in the traced example → **that skip is your gap**

Each mark is a hole in the user's understanding, not just the prose. Fix at the
source, then re-read. This is where surface familiarity becomes real knowledge.

### 4. Curveball defense (what makes this world-class)

Standard explainers stop at "here's how it works." This skill's job is to make the
user un-embarrassable. Generate the hardest questions **before** the audience does,
by running the topic through these six lenses:

| Lens | The question it produces |
|---|---|
| **Misconception** | "I thought it worked like ___ — why is that wrong?" |
| **Boundary** | "Where does this break / stop being true?" |
| **Why-not-X** | "Why not the obvious alternative? What's the tradeoff?" |
| **Second-order** | "If we change this, what breaks three steps downstream?" |
| **Adjacent confusion** | "How is this different from <the thing it's often confused with>?" |
| **Operator's caveat** | "What does someone who's run this in prod know that the docs don't say?" |

For each lens, write the question in the skeptic's voice, then answer it in 1-3
sentences. If you can't answer one, that's the most important thing to go learn —
flag it as `OPEN` rather than bluffing. An honest `OPEN` beats a confident wrong
answer every time (and the audience can smell the bluff).

Pick the 6 sharpest across the lenses. Order them worst-first — lead your defense
with the question you'd least want to be asked.

### 5. Quality streak (converge, don't ship the first draft)

Run two tests. Reset the streak on any failure. Stop after **2 consecutive clean passes**:

- **Reader test:** could the named audience follow the traced example and repeat
  the one-liner back, with no prior context? If not, the explanation is for you,
  not them.
- **Accuracy test:** is every non-`[unverified]` claim checkable against source?
  Is every analogy's breaking-point named? Does each curveball answer actually
  answer the question asked, not a softer nearby one?

### 6. Deliver

Default to rendering the card inline in chat. Then offer a richer format when it
fits — do not silently pick one:

- **HTML doc** — visual, shareable, offline reference → **use the bundled script (below)**
- **Markdown file** — reusable notes / wiki
- **Canvas** — interactive/explorable → `canvas` skill
- **Slides** — presenting to a room → `wow-deck`
- **Diagram-heavy** — architecture/flows → `architecture-diagram`

#### HTML output — token-efficient, reusable (`scripts/render_card.py`)

Do **not** hand-write HTML/CSS in chat. That burns thousands of tokens per card and
drifts in style. Instead emit only the card *content* as JSON and let the committed
script own all layout, styling, collapsible answers, and diagram rendering.

Workflow:

1. Write the card as compact JSON to a temp file. The installed examples and
   renderer live under `~/.cursor/skills/teach/scripts/`.
2. Run the renderer:

```bash
RENDERER="$HOME/.cursor/skills/teach/scripts/render_card.py"
python3 "$RENDERER" card.json            # -> ~/teach-cards/<slug>-<date>.html
python3 "$RENDERER" card.json --open     # also open in browser
cat card.json | python3 "$RENDERER" -    # or pipe via stdin
```

3. Report the output path. Offer `--open` rather than opening unprompted.

JSON contract (only `topic` + `one_liner` are required; omit any section to skip it):

| Key | Type | Notes |
|---|---|---|
| `topic`, `audience`, `one_liner`, `teach_back`, `grounding` | string | |
| `analogy` | `{text, seam}` | `seam` renders as the "where it breaks" callout |
| `picture` | object or **list** of objects | beautiful inline SVG, fully offline. See diagram types below. |
| `how_it_works` | `{intro, steps[]}` | `steps` is the numbered traced example |
| `depth_ladder` | `{eli5, practitioner, expert}` | |
| `curveballs` | `[{lens, question, answer}]` | keep worst-first; an answer starting `OPEN` flags the gap |
| `check_yourself` | `[{q, a}]` | renders as click-to-reveal `<details>` |

Why JSON-not-HTML: the agent writes ~300-500 tokens of content; the script (already
on disk, zero token cost) produces a ~10KB styled page. Same pattern as `wow-deck`.
Inline strings support `` `code` `` and `**bold**`.

**Diagram types** (the `picture` field renders inline SVG, no CDN, prints/works offline).
Prefer these over ASCII. Pass one picture or a list of them:

| `type` | Spec | Use for |
|---|---|---|
| `graph` | `{nodes:[{id,label,col,row,shape,color}], edges:[{from,to,label}]}` | flowcharts, request paths, architecture. `shape`: `box` (default) / `pill` (start/end) / `diamond` (decision) / `cloud`. `col`/`row` are grid coords; edges route as clean elbows. |
| `loop` | `{kind:"reinforcing"\|"balancing", nodes:["a","b","c"]}` | feedback loops (systems thinking). Auto circular layout + R/B badge. |
| `stock_flow` | `{stock, inflow, outflow}` | the stock-and-flow primitive. |
| `orderbook` | `{asks:[[price,size]], bids:[[price,size]], spread_label?}` | price ladder / depth chart: red asks above, green bids below, best levels marked, bar width ∝ size. Don't fake a ladder with `graph`. |
| `queue_spread` | `{bids:[[price,size]], asks:[[price,size]], crosses?, spread_label?}` | **the two-queue metaphor**: buyers and sellers as facing queues, best prices in front, matcher in the middle at the spread. Use this when you say 'two sorted queues meeting at the spread'. |
| `ascii` / `mermaid` / `table` | `{content}` | fallbacks. `mermaid` needs a CDN (not offline); avoid unless asked. |

Keep labels short (they wrap). A list of small diagrams reads better than one dense one.

### Interactive mode (optional — offer it when the user wants to *retain*, not just read)

If the user wants to actually internalize the topic (not just get a doc), offer to
run it as a tutor loop instead of dumping the whole card:

1. Deliver the one-liner, analogy, and picture.
2. Ask the "Check yourself" questions **one at a time**. Wait for the user's answer.
3. Grade honestly: what they got, what they missed, the crisp correction. This is
   retrieval practice on the user — the single most effective way to make it stick.
4. Escalate to the curveball questions once the basics land. When they can answer a
   worst-first curveball in their own words, they own it.

Offer this with: "Want me to just explain it, or quiz you through it so it sticks?"

---

## Voice

Teach in the **Julia Evans register** (`~/.cursor/rules/julia-evans-voice.mdc`):
warm, concrete, short paragraphs, acknowledge what's hard, invitations not orders.
For the load-bearing term definitions and the "how is this different from X" answers,
switch to the **Fowler Bliki register** (`~/.cursor/rules/fowler-voice.mdc`): crisp,
definitional, cross-referenced. Run the final text through `framing.mdc` /
`humanizer` to strip AI tells (no "great question," no emoji unless asked, no
uniform sentence rhythm).

## Anti-patterns

- **Jargon-defining-jargon.** "It uses idempotency keys to dedupe." If the reader
  didn't know the first word, the definition didn't help. Bottom out in plain words.
- **The abstract worked example.** "The system validates and processes the request."
  That's not an example, it's a paraphrase of "it works." Trace one real thing.
- **Analogy without a seam.** Every analogy breaks somewhere. Unnamed seams are
  exactly where curveballs land. Name the seam.
- **Curveball theater.** Six softball questions you already answered in the body.
  The lens table exists to force genuinely hard ones. If a question doesn't make
  you slightly nervous, it's not a curveball.
- **Depth flattening.** Giving execs the expert version or teammates the ELI5 and
  stopping. The ladder exists so the user can meet the room where it is.

## Additional resources

- [reference.md](reference.md) — the learning science, why each move works, and
  the full curveball-generation playbook
- [examples.md](examples.md) — complete worked Teaching Cards (technical + general)
- `scripts/render_card.py` — JSON → self-contained HTML renderer (token-efficient)
- `scripts/example_card.json` — the JSON contract to copy from
