---
name: engineering-blog
description: >-
  Draft long-form public engineering essays from incidents, retrospectives,
  migrations, or recurring operational patterns. Produces a scene-based,
  Larson-register essay with named patterns, verified technical anchors, and
  confidential-data review. Use for "turn this retro into a blog", incident or
  migration stories, and engineering essays. For a short post about shipped
  code or WordPress packaging, use technical-writing.
---

# Engineering Blog Writing

Turn a real incident, migration, or system-design story into a public-facing essay that engineers will share, save, and learn from. Optimised for the Will Larson / Stripe / Pragmatic Engineer reading audience.

This skill layers on top of `larson-voice.mdc` (voice rule) and `staff-eng-writing` (structure for internal docs). It is the public-blog counterpart, not a replacement.

## When to use this skill

Apply when the user wants to:

- Convert a retro, post-mortem, or migration story into a Substack / personal-blog post
- Draft an engineering essay around a named pattern they keep teaching from
- Turn a one-pager or review doc into something publishable
- Critically review an existing draft against best-in-class engineering blogs

Do NOT apply for: internal RFCs, alignment docs, JIRA descriptions, status updates, or executive memos. Those use `staff-eng-writing` and live behind authentication.

Use `technical-writing` instead when the source of truth is a shipped feature
or git diff and the destination is a short Markdown/WordPress post. If an essay
also needs code investigation or WordPress packaging, this skill owns the
narrative and delegates only those bounded steps.

## Related skills (compose, do not duplicate)

This skill is the macro workflow. It chains into two specialized skills for the parts they own better:

| Skill | What it owns | When this skill calls it |
| ----- | ------------ | ------------------------ |
| `humanizer` | 46-pattern AI-tell catalog, fabrication boundary, scoring, voice-aware rewrite | Phase 4 lint pass (mandatory before publish) |
| `technical-writing` | Shipped-code investigation, WordPress publishing, frontmatter | Only for a bounded code-research or WordPress-packaging step |

Voice rules consumed (from `~/.cursor/rules/`): `larson-voice.mdc` (default essay register), `framing.mdc` (anti-AI guardrails). Pick a voice rule before drafting; humanizer will apply it during rewrite.

Do NOT replicate humanizer's pattern catalog or technical-writing's WordPress logic in this skill. Defer.

## The four-phase workflow

### Phase 1: Discovery (before writing a single sentence)

Pull the raw material and answer three questions:

1. **What is the smallest concrete artifact at the heart of the story?** One character, one field, one config line, one alert. The post hooks on this artifact.
2. **What named pattern does the writer keep using afterward?** "Service-green vs merchant-green", "cheap wrongness", "consequence asymmetry". Without a named pattern, the post is a diary.
3. **Who is the reader?** Junior engineer learning the craft, senior IC running a similar program, leadership making a similar decision. Pick one; secondary readers come along for free.

If the user has a retro doc, transcripts, or wiki notes, read those first. Do not invent the failure mode.

### Phase 2: First draft (get the story out)

Structure as a scene-based essay, not a numbered post-mortem. The opening is the smallest artifact. The middle is the work. The end is the gate question.

Default section arc (six sections, all optional, all reorderable):

1. **The hook** — the one-character / one-field artifact that broke things. Show it inline as JSON or code.
2. **The migration that looked normal** — what was being shipped, why it felt like a deploy, why it wasn't.
3. **The contract was not the document** — what the failure actually was, plus the structural cause (often ownership split, undocumented behavior, compressed timeline).
4. **Streams of work afterward** — revert, contract fix, ramp redesign, observability. Code blocks here.
5. **The hard argument** — the human layer. Trust, conflict, the meeting where the right framing won.
6. **The slower damage / what I take from it** — personal aftermath, named patterns the reader can carry, closing gate question.

Get the story out in one pass. Do not edit yet.

### Phase 3: Technical anchors

This is what separates an engineering blog from a journal. Every claim about a system or fix gets a concrete artifact next to it.

**JSON contract diffs** for any contract / schema change:

```html
<pre><code>// Expected legacy contract
{
  "card_id": "card_example",
  "expiration_date": "1028"
}

// Shipped new contract
{
  "card_id": "card_example",
  "expiration_date": "10/28"
}</code></pre>
```

**Routing / config before-and-after** for any rollout strategy change:

```html
<pre><code># BEFORE: binary key list, all pilot keys on new path instantly
routing:
  - match: request.headers["X-Merchant-Key"] in ["pk_01", "pk_02", ..., "pk_76"]
    route_to: new-platform-service

# AFTER: phased percentage ramp inside a smaller cohort
routing:
  - match: request.headers["X-Merchant-Key"] in ["pk_01", "pk_02", ..., "pk_06"]
    percentage_ramp: 10%  # incremental: 1% -> 5% -> 10% -> 100%
    route_to: new-platform-service</code></pre>
```

**Alert rules / queries** for any observability claim:

```html
<pre><code># Alert: merchant authorization rate collapse
# Trigger if a merchant's 5m auth approval rate drops 30% below its 14d baseline
alert: CohortMerchantAuthCollapse
expr: |
  (
    sum(rate(auth_success_total[5m])) by (merchant)
    /
    sum(rate(auth_attempts_total[5m])) by (merchant)
  ) < (
    sum(rate(auth_success_total[14d])) by (merchant)
    /
    sum(rate(auth_attempts_total[14d])) by (merchant)
  ) * 0.70
for: 10m</code></pre>
```

The rule: every system-level claim gets a code block. If you cannot show a config, query, or schema, the claim is probably too abstract.

### Phase 4: Editorial pass (three sub-passes, in order)

This is where most posts fail. Run all three before publishing.

#### 4a. Voice & register (manual)

Apply `larson-voice.mdc` while drafting. The essential moves:

- **First-person, owned claims.** "I went to bed thinking we'd done a deploy." Not "the team thought."
- **Escape valves.** "I'm still working out which is which." "The exact gate set will vary by org."
- **Named patterns.** Service-green vs merchant-green. Cheap wrongness. Consequence asymmetry. Coin one or two.
- **Concrete anchors.** Read-card API. A dozen merchants. About half a day. (Anonymise the numbers, but keep the shape.)
- **Soft sign-off.** End on a gate question or honest summary. No "Let's go ship it!" energy.

#### 4b. Anonymise confidential information (engineering-blog specific)

This is the only sub-pass humanizer cannot do for you. Run it manually.

Replace anything that ties back to internal systems:

- **Real merchant names** → "a large wireless retailer", "an educational travel merchant"
- **Internal ticket IDs** → drop entirely
- **Internal team or service names** → generic equivalents such as "the new
  stack", "the partner-facing API", or "the platform team"
- **Real numbers from a retro** → round or blur the supplied magnitude. "70% → 6%" becomes "above seventy percent to single digits." "$420K GMV" becomes "hundreds of thousands of dollars routed through the broken path." Never invent a replacement magnitude.
- **ULID-shaped IDs** that look like real prefixes → `card_example`, `order_demo`, etc.
- **Specific dates** that pin the incident → "last spring", "a Monday", "months later"

The story should feel real because the **shape** is real, not because the **numbers** are.

After this pass, also re-check that no paragraph leaks an anonymised number it had restored elsewhere (e.g., changing "fourteen hours" to "about half a day" in one place but leaving "nine-hour detect gap" three paragraphs later).

#### 4c. Run the `humanizer` skill (mechanical lint)

Invoke the `humanizer` skill on the draft in `detect` mode with scoring, using
`larson-voice.mdc` as the selected voice context. This is a skill invocation,
not a shell command or CLI. It will:

- Scan for all 46 AI-writing patterns, including register, grounding, and fabricated specificity
- Compute a 0-100 AI-tell density score and burstiness (sentence-length variance)
- Surface a prioritised list of fixes

**Target: score under 20** ("pristine on mechanical tells"). For any remaining
pattern hits, invoke `humanizer` in `rewrite` mode on the offending paragraph,
with `larson-voice.mdc` loaded. Do not rewrite the whole post when human-written
sections already pass.

Common patterns this skill's drafts hit, and the standard fix:

| Humanizer pattern | Common engineering-blog manifestation | Fix |
| ----------------- | ------------------------------------- | --- |
| P39 (paragraph-closing "Whether..." summary) | "Whether their auth rate stays steady is what matters." | Cut and replace with the strongest specific point |
| P40 (symbolic gloss) | "The auth graph is the product" used twice | Keep the load-bearing instance; vary the other |
| P30 (uniform sentence length) | 3+ medium-length sentences in a row | Insert a fragment: "We weren't.", "Sounds naive.", "Not consciously." |
| P11/P31 (synonym cycling) | "merchant" → "retailer" → "partner" → "client" for the same entity | Pick the clearest term and repeat |
| P8 (copula avoidance) | "serves as the auth proxy" | Use "is": "is the auth proxy" |

## Critical-review pass (compare against best-in-class)

Before declaring the draft done, ask:

- **Stripe blog test**: Does every system claim have a concrete artifact next to it? (Schema, query, config.) If not, add one.
- **Pragmatic Engineer test**: Are numbers anchored to events, not floating? "Eighteen merchants over fourteen hours" beats "many merchants over many hours."
- **Will Larson test**: Do I own every claim? Is at least one pattern named? Are there escape valves?
- **Julia Evans test**: Could a junior engineer read this and learn the craft? Or does it assume too much?
- **Anti-journal test**: Does the post teach something portable, or is it just "here's what happened to me"? If the latter, add a named pattern and a closing gate question.

## Output format

Default to a self-contained HTML file with serif typography. Width ~680px. Charter / Bitstream Charter / Georgia for body. Monospace for code.

Storage path: workspace root or `~/blog-drafts/`. Filename: `blog-<topic-slug>.html` or `blog-<channel>-<slug>.html` for multi-channel drafts.

A working scaffold:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>YOUR TITLE</title>
  <style>
    :root {
      --bg: #fff;
      --text: #222;
      --muted: #555;
      --rule: #ddd;
      --mono: ui-monospace, Menlo, monospace;
      --sans: Charter, "Bitstream Charter", Georgia, serif;
      --code-bg: #f8f9fa;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: var(--sans); background: var(--bg); color: var(--text); font-size: 1.125rem; line-height: 1.7; }
    .wrap { max-width: 680px; margin: 0 auto; padding: 48px 20px 80px; }
    .meta { font-size: 0.85rem; color: var(--muted); margin-bottom: 24px; }
    h1 { font-size: 1.85rem; font-weight: normal; line-height: 1.25; margin-bottom: 32px; letter-spacing: -0.01em; }
    .lede { font-size: 1.18rem; margin-bottom: 1.2em; }
    p { margin-bottom: 1.1em; }
    h2 { font-size: 1.18rem; font-weight: normal; margin: 2.4em 0 0.8em; letter-spacing: -0.005em; }
    h3 { font-size: 1rem; font-weight: 600; margin: 1.8em 0 0.5em; }
    strong { font-weight: 600; }
    ul { margin: 1.1em 0 1.4em 1.4em; padding: 0; }
    li { margin-bottom: 0.5em; list-style: disc; }
    pre { background: var(--code-bg); border: 1px solid var(--rule); padding: 16px; overflow-x: auto; margin: 1.6em 0; font-family: var(--mono); font-size: 0.9rem; line-height: 1.5; }
    code { font-family: var(--mono); font-size: 0.95em; background: var(--code-bg); padding: 2px 4px; border-radius: 3px; }
    pre code { padding: 0; background: transparent; border-radius: 0; }
    em { font-style: italic; }
  </style>
</head>
<body>
  <article class="wrap">
    <p class="meta">YOUR NAME</p>
    <h1>YOUR TITLE</h1>
    <p class="lede">One-sentence hook on the smallest concrete artifact.</p>
    <!-- sections go here -->
    <p class="meta" style="margin-top: 2.5em;">YOUR FIRST NAME</p>
  </article>
</body>
</html>
```

## Title guidance

Lethain-register titles work best for engineering essays:

- **Concept-as-noun**: "On Lacking Launch Criteria", "On Pressure Without a Plan"
- **Named-pattern**: "Service-Green is Not Merchant-Green", "Compatibility Launches"
- **Direct hook**: "The API Was Green, but the Integration Was Dead"

Avoid: clickbait, all-caps, exclamation marks, "5 Lessons From..." listicle framing, generic "How We..." openers.

## Final pre-publish checklist

```text
- [ ] One named pattern coined or used as shorthand
- [ ] At least one JSON / YAML / PromQL code block per system claim
- [ ] First-person owned claims throughout
- [ ] At least one escape valve ("I'm still working out...", "varies by org")
- [ ] Phase 4b done: no internal ticket IDs, real merchant names, internal team names, or retro-specific numbers
- [ ] Phase 4c done: humanizer detect score under 20
- [ ] Closing gate question or honest summary, not a rally
- [ ] Title is concept / named-pattern / direct-hook (not clickbait)
- [ ] Read it out loud once, end to end
```

## Worked example

The post `blog-substack-green-is-wrong.html` (workspace root) is the canonical reference draft for this skill — incident-driven, Larson-register, with JSON / YAML / PromQL anchors and anonymised numbers. Title is `On Lacking Launch Criteria`. Primary thesis: launch criteria for partner API migrations need to be written rules that turn red when gates fail. Sub-pattern introduced inside the post: `service-green is not merchant-green` (one specific criterion). The two-level naming — title-level concept + sub-pattern — is the structural move worth copying.

The path it travelled, in case the user wants to repeat:

1. Started as a journal-style retro narrated in the first person ("I led the retrospective afterward...")
2. First critical review: "this reads like a journal, not a blog for fintech engineers"
3. Restructured into a numbered post-mortem with a metrics table
4. Second critical review: "too formal, less metrics, more storytelling"
5. Rewrote as scene-based essay with a single comparison box
6. Third review against Stripe / Figma standards: "needs technical anchors"
7. Added JSON contract diff, routing-config before/after, PromQL alert rule
8. Phase 4b anonymisation pass: removed retro numbers, ULID-shaped card IDs, real merchant names
9. Phase 4c humanizer detect pass: caught one P39 "Whether..." closer, one P40 echo, two P30 burstiness gaps. Final score ~10/100.

Each iteration tightened a specific dimension. The skill is the path, not the destination.
