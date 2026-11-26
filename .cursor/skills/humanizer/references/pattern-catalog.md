# Humanizer pattern catalog

Read this file whenever running `detect`, `rewrite`, or `edit`. Scan all 52
patterns. Mechanical fixes may be applied automatically. Specificity, stakes,
examples, numbers, and anecdotes must obey the fabrication boundary in
`../SKILL.md`.

## Content (P1-P8)

- **P1 Significance inflation.** Detect "pivotal", "testament", "underscores
   the importance", "broader landscape", and similar importance claims. State
   what happened or what the thing does.
- **P2 Notability name-dropping.** Detect lists of publications used as proof
   of importance. Pick one source and report what it said, or cut the list.
- **P3 Superficial `-ing` phrases.** Detect trailing clauses such as
   "highlighting", "ensuring", "reflecting", or "fostering". Delete them or
   promote real information into a sourced sentence.
- **P4 Promotional language.** Detect "vibrant", "renowned", "seamless",
   "robust", "world-class", "cutting-edge", and travel-brochure prose. Replace
   adjectives with facts.
- **P5 Vague attribution.** Detect "experts argue", "research suggests", and
   unnamed reports. Name and cite the source or remove the claim.
- **P6 Formulaic challenges sections.** Detect "Despite these challenges",
   "Future outlook", and generic challenge/optimism templates. Use dated,
   concrete problems or cut the section.
- **P7 AI vocabulary.** Detect clusters including additionally, align with,
   bolster, crucial, delve, enduring, enhance, foster, garner, highlight,
   interplay, intricate, key, landscape, leverage, multifaceted, notably,
   pivotal, realm, showcase, tapestry, testament, underscore, utilize,
   valuable, vibrant, moreover, furthermore, quietly ("quietly shipped"),
   meticulous, deep dive, facilitate, empower, streamline, harness,
   transformative, "it's worth noting", and "in terms of". Replace with plain
   language or delete. A word used in its technical sense is not a hit:
   "critical" severity, a "gated" feature, an API "key", a "robust" estimator.
- **P8 Copula avoidance.** Detect "serves as", "stands as", "represents",
   "boasts", and "features" where `is`, `are`, or `has` is clearer.

## Language and style (P9-P18)

- **P9 Negative parallelism.** Detect "not only X but Y", "not just X, it's
   Y", "X rather than Y", the same contrast split across two sentences ("This
   doesn't mean X. It means Y."), and clipped tails ("..., no guessing"). One
   sighting is enough. State the point directly; keep a contrast only when the
   reader actually holds the belief being corrected.
- **P10 Rule of three.** Detect forced triads, especially abstract nouns.
    Use the natural number of items.
- **P11 Synonym cycling.** Detect unnecessary renaming of the same entity.
    Repeat the clearest term. *Weak alone*: Wikipedia now lists it as a
    human habit.
- **P12 False ranges.** Detect "from X to Y" when X and Y are not a real
    spectrum. Name the items directly. *Weak alone*, for the same reason.
- **P13 Dashes.** Any U+2014 em dash is a hit, and so is an en dash (U+2013)
    or a spaced ` -- ` used to join clauses. Leave dashes in code, URLs, and
    numeric ranges ("10–12"). Replace each with punctuation appropriate to
    the sentence, not with a semicolon or colon every time.
- **P14 Formatting overuse.** Detect bold on routine nouns, emoji headers,
    arrows (`→`) used as connectors or decoration in prose, a horizontal rule
    between every section, and formatting that does not fit the destination.
    Strip it.
- **P15 Structured-list syndrome.** Detect bullets shaped as
    `**Bold label:** prose`, lists that are really paragraphs, and short
    messages rebuilt as labeled sections (`Root cause:` / `Impact:` /
    `Next steps:`, `Why` / `What` / `Impact`, `TL;DR` on a five-line note).
    Restore prose unless the content is genuinely parallel or sequential, or
    the labels belong to a format the team repeats (a weekly
    Progress / Plans / Problems update, "why it matters:" in a launch post).
- **P16 Title-case headings.** Use sentence case unless the destination's
    style requires title case.
- **P17 Typographic fingerprints.** Detect smart-quote normalization and
    mechanically perfect punctuation that conflicts with the author's samples.
- **P18 Formal-register overuse.** Replace bureaucratic phrases such as "it
    should be noted" and "the implementation of" with plain language.

## Communication (P19-P21)

- **P19 Chatbot artifacts.** Remove "I hope this helps", "Of course",
    "Certainly", "Would you like me to", "Let me know if", and "Here is a".
- **P20 Knowledge-cutoff disclaimers.** Remove model-status disclaimers.
    State the verified source and date when recency matters.
- **P21 Sycophancy.** Remove "Great question", "Excellent point",
    "Absolutely", and conclusion-level validation that lacks evidence.

## Filler and hedging (P22-P30)

- **P22 Filler phrases.** Delete words that do not change the claim.
- **P23 Excessive hedging.** Detect stacked hedges such as "could potentially
    possibly". Keep one honest uncertainty marker.
- **P24 Generic conclusions and one-line closers.** Cut "the future looks
    bright", "exciting times lie ahead", and similar wrap-ups. Also cut a short
    final line that restates the paragraph ("That's the real win.", "That
    distinction matters.", "Let that sink in."), a sentence that names what the
    example just showed, and rows of dramatic fragments ("No prior. No
    nostalgia."). One sighting is enough. Keep a short line only when it adds a
    new fact or consequence. Lines that tell the reader how to weigh what
    they just read count too: "That last part matters more than it sounds",
    "The key point is", "As you can see". Delete a fake-profound closer
    outright; do not rewrite it into a better metaphor.
- **P25 Hallucination markers.** Flag suspicious dates, numbers, obscure
    claims, or nonexistent sources for verification. Never repair by guessing.
- **P26 Perfect/error alternation.** Detect abrupt alternation between
    polished prose and basic errors. Match the verified author register.
- **P27 Question-format section titles.** Replace FAQ-like headings when the
    artifact is flowing long-form prose.
- **P28 Markdown bleeding.** Remove Markdown syntax where the destination
    does not render Markdown.
- **P29 Comprehensive-overview opening.** Cut "This comprehensive guide",
    "In this article", and "Let's dive into". Start with the claim.
- **P30 Uniform rhythm.** Detect three or more similarly sized sentences, and
    paragraphs that all share one shape (claim, two supports, short kicker).
    Rewrites cause this as often as drafts do. Fix it by merging, reordering, or
    developing sentences, never by chopping them into fragments.

## Emerging patterns (P31-P43)

- **P31 Noun-phrase cycling.** Detect three or more elaborate descriptions
    of the same referent. Repeat the clearest noun phrase.
- **P32 Collaborative framing leak.** Remove advice-to-user scaffolding such
    as "Let me walk you through" from publishable content.
- **P33 Placeholder leakage.** Detect `[Your Name]`, `2025-XX-XX`, HTML
    prompts, and unfilled template fields. Fill from supplied facts or delete.
    Deliberate `[INSERT: ...]` author-intake prompts are allowed before publish
    and must be resolved before the artifact ships.
- **P34 Chatbot citation markup.** Remove `citeturn...`,
    `contentReference...`, `oai_citation`, attachment tokens, and dead
    footnotes. Preserve a citation only by replacing it with a real reference.
- **P35 AI tracking parameters.** Strip AI-tool UTM and referrer parameters
    from URLs.
- **P36 Sudden register shift.** Detect a paragraph whose voice, locale, or
    error profile differs sharply from surrounding text. Match the author's
    actual register.
- **P37 Source-listing as content.** Detect coverage lists that substitute
    for substance. Report one source's finding or cut the list.
- **P38 Paragraph-reshuffling immunity.** If paragraphs can swap positions
    without changing the argument, add real dependency/callbacks, merge, or
    cut.
- **P39 Paragraph-closing `whether` summary.** Cut local SEO-style recap
    sentences beginning "Whether you/they/it's". End on the strongest fact.
- **P40 Symbolic gloss.** Detect sentences telling readers what a mundane
    fact "represents", "symbolizes", or "embodies". State the fact and
    consequence.
- **P41 Infomercial hooks.** Delete "The catch?", "The kicker?", "Here's the
    thing", "The brutal truth", and similar viral pauses. Also delete
    lone-expert setups ("What most people get wrong", "Here's what nobody
    tells you", "The part everyone misses") and staged reveals ("What if I
    told you", "Plot twist:", "Honestly?" before a routine claim).
- **P42 Erratic inline bolding.** Strip patternless mid-paragraph bold. Keep
    it only for a consistent semantic reason such as glossary terms or UI
    labels.
- **P43 Treadmill effect.** Detect sentences that only restate the prior
    sentence. Keep only information that advances the argument.

## Register and grounding (P44-P46)

- **P44 Over-explained shared context.** Detect acronym expansions,
    primers, and definitions the named audience already knows. Match the
    calibration sample's gloss ratio. Cut the gloss.
- **P45 Stakelessness.** Detect neutral reporting with no owned claim,
    admitted downside, or estimate. Never invent a position. When the author
    has not supplied one, ask for their read in the questions after the text.
- **P46 Fabricated specificity.** Detect any anecdote, number, example,
    identifier, or sensory detail introduced by the rewrite rather than the
    source or author. Remove it, and ask the author for the real one after the
    text.

## Staging and self-reference (P47-P52)

- **P47 Arguing with no one.** Detect defenses against an objection nobody
    raised ("To be clear", "I'm not saying", "Don't get me wrong", "This
    isn't about X") and rejected options nobody proposed ("A tempting
    approach would be...", "One might be tempted to..."). Cut the defense;
    if it holds a real claim, state the claim. Keep an objection the text
    attributes to someone, or an option a reader would actually weigh.
- **P48 Sayings that sound deep.** Detect "at its core", "the real question
    is", "fundamentally", "what really matters", "the heart of the matter",
    and aphorisms such as "X is the language of Y" or "X becomes a trap".
    Replace the saying with the specific claim, or cut it.
- **P49 Colon reveals.** Detect a noun phrase built up for drama, then a
    colon and the payoff: "The detail that makes it work: a second agent
    grades it.", "The best part: it learns."
    Write it as a plain sentence. A short label the author uses as a message
    opener ("Fix:", "Heads up:", "FYI:", "Update:") is ordinary Slack, not a
    hit.
- **P50 Writing about the document.** Detect history of what the text
    replaced ("was added to replace the previous approach"), narration of
    method ("figures come from each vendor's published pricing; anything we
    could not confirm is marked"), and layout the reader can already see
    ("the sections follow rollout order", "the table below compares"). Cut
    it; rewording it ("arranged" for "follow") is not a fix. Keep previous-version history only in
    changelogs and migration notes, and keep a caveat that changes what the
    reader does.
- **P51 Vague association.** Detect "associated with", "linked to", "tied
    to", "connected to", and "in connection with" where the text knows the
    real relationship. "He is associated with the orchestra, which he
    founded" becomes "He founded the orchestra"; a synonym is not a fix. If the relationship is unknown, keep the vague
    wording rather than guess.
- **P52 Repeated sentence openings.** Detect three or more sentences in a row
    opening with the same subject or word. Merge them or begin with the
    action. Deliberate repetition for rhythm stays.

## Structural checks

- **Burstiness:** avoid three consecutive sentences with similar length, and
  let length follow the thought. Manufactured rhythm (fragments, kickers) is
  a P30 hit of its own.
- **Information density:** each sentence must add a fact, claim, example,
  concession, or transition the argument needs.
- **Bullets versus prose:** use bullets for three or more parallel,
  independently scannable items; use numbered lists for real dependency order;
  keep arguments in prose. Never use `**Bold label:** description` bullets.
- **Sequences:** write a multi-hop sequence as a sentence with real state
  names ("the report never loaded, so the wire had nothing to match"). Use an
  arrow chain only inside a diagram, code, or a source that already had one.

## Weak alone

In detect mode these count only when other tells share the passage: P11, P12,
P13 (a single dash), P17, P23 (one honest hedge), P30 (one even run), P52, and
a single P7 word. Do not report an isolated hit as a finding. Rewrite and edit modes
still apply the mechanical fix, such as replacing the dash.
