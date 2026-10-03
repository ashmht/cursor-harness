# Generic voice and calibration reference

This material is inactive for calibrated drafts unless the user explicitly
requests an upstream generic profile. The selected `.mdc` voice rules always take
precedence. See `../SKILL.md`.

## Generic profiles

### Casual

- Use contractions and first person where appropriate.
- Allow fragments, informal transitions, and occasional asides.
- Prefer honest uncertainty to polished neutrality.

### Professional

- Use selective contractions and short paragraphs.
- Prefer concrete examples and dry understatement.
- Use first person for owned opinions or experience.

### Technical

- Use the exact technical term.
- Make one point per sentence.
- Preserve code and meaningful numbers.
- Avoid decorative metaphors and labels such as "Note:".

### Warm

- Use "we" only for a real shared experience.
- Acknowledge difficulty without performative reassurance.
- Keep paragraphs short and encouragement specific.

### Blunt

- Use short, active sentences.
- Remove pleasantries and unsupported hedging.
- Do not turn uncertainty into false confidence.

## Slack-native register

`slack-native` is a register, not a voice. It complements the Slack formatting
rules in `../SKILL.md`.

- Compress hard. A one-line answer can be complete.
- Lowercase sentence starts are allowed when calibration samples support them.
- Do not gloss shared jargon. Match the audience's acronym-expansion rate.
- Answer the exact question first. Quote source text afterward only when the
  thread has enough branches that the reference is otherwise ambiguous.
- Use numbered lists only for a real dependency chain.
- Separate the source's claim from the author's estimate.
- Preserve harmless inconsistency from real samples. Perfect normalization is
  a tell.
- Do not add sign-offs or gratitude scaffolding.

## Calibration fingerprint

When `--calibrate` is set, read the supplied real, un-AI-edited samples and
record:

1. Median sentence or message length and the observed range.
2. Sentence-start capitalization rate.
3. Contraction rate.
4. Gloss ratio: the fraction of domain terms the author explains.
5. Inconsistency signature: spelling drift, abbreviations, omitted apostrophes.
6. Structural habits: answer-first phrasing, mid-thought openings, list use,
   and separation of sourced claims from owned estimates.

The fingerprint sets measurable targets. A selected `.mdc` sets tone. Where
they conflict on measurable habits, the real samples win.

If the user asks to persist calibration, write a short fingerprint plus three
to five raw samples to `humanizer-context.md` in the working directory.

## Honest human texture

These techniques may only rearrange or emphasize material the author supplied:

- State an actual opinion.
- Acknowledge real uncertainty.
- Use a real experiential detail.
- Allow a brief relevant aside.
- Vary paragraph length.
- Start mid-thought when the destination permits it.
- Break mechanical parallel structure.
- Use callbacks.
- Preserve a genuine self-correction.
- Stop without a generic conclusion.

Never invent a personal experience, emotional state, number, example, or
sensory detail to make prose seem human. That is P46.
