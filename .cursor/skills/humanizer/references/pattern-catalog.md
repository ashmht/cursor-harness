# Humanizer pattern catalog

Read this file whenever running `detect`, `rewrite`, or `edit`. Scan all 46
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
   valuable, vibrant, moreover, furthermore, "it's worth noting", and "in
   terms of". Replace with plain language or delete.
- **P8 Copula avoidance.** Detect "serves as", "stands as", "represents",
   "boasts", and "features" where `is`, `are`, or `has` is clearer.

## Language and style (P9-P18)

- **P9 Negative parallelism.** Detect repeated "not only X but Y" or "not
   just X, it's Y". State the point directly.
- **P10 Rule of three.** Detect forced triads, especially abstract nouns.
    Use the natural number of items.
- **P11 Synonym cycling.** Detect unnecessary renaming of the same entity.
    Repeat the clearest term.
- **P12 False ranges.** Detect "from X to Y" when X and Y are not a real
    spectrum. Name the items directly.
- **P13 Em dash.** Any U+2014 em dash is a hit. Replace it with punctuation
    appropriate to the sentence.
- **P14 Formatting overuse.** Detect bold on routine nouns, emoji headers,
    and formatting that does not fit the destination. Strip it.
- **P15 Structured-list syndrome.** Detect bullets shaped as
    `**Bold label:** prose` and lists that are really paragraphs. Restore prose
    unless the content is genuinely parallel or sequential.
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
- **P24 Generic positive conclusions.** Cut "the future looks bright",
    "exciting times lie ahead", and similar wrap-ups.
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
- **P30 Uniform sentence length.** Detect three or more similarly sized
    sentences. Vary length naturally without inventing content.

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
    thing", "The brutal truth", and similar viral pauses.
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
    admitted downside, or estimate. Never invent a position. Insert
    `[INSERT: your actual read / downside you would admit]` when the author has
    not supplied one.
- **P46 Fabricated specificity.** Detect any anecdote, number, example,
    identifier, or sensory detail introduced by the rewrite rather than the
    source or author. Remove it or replace it with
    `[INSERT: a real example here]`.

## Structural checks

- **Burstiness:** avoid three consecutive sentences with similar length. Use
  short, medium, and long sentences when the thought naturally supports them.
- **Information density:** each sentence must add a fact, claim, example,
  concession, or transition the argument needs.
- **Bullets versus prose:** use bullets for three or more parallel,
  independently scannable items; use numbered lists for real dependency order;
  keep arguments in prose. Never use `**Bold label:** description` bullets.
- **Flows:** show a multi-hop sequence as `A → B → C`, then explain only the
  non-obvious hop. Use real state names and values; otherwise insert an intake
  prompt.
