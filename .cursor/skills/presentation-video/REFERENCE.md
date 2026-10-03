# Presentation Video Reference

## Configuration contract

```json
{
  "title": "Talk title",
  "words_per_minute": 136,
  "fps": 30,
  "viewport": [1920, 1080],
  "validation_viewports": [[1920, 1080], [1366, 768]],
  "same_slide_transition": 0.35,
  "between_slide_transition": 0.5,
  "forbidden_patterns": ["PROJ-[0-9]+", "INC-[0-9]+"],
  "hide_selectors": ".controls,.toc,.scrim,.notes-panel,.scroll-hint,footer",
  "voice": {
    "reference_text": "A representative sentence in the intended register.",
    "description": "A concrete voice-design instruction."
  },
  "slides": [
    {
      "id": "title",
      "beats": [
        {
          "paragraphs": [0, 2],
          "pause": 1.5,
          "focus": {
            "candidates": ".epigraph,.sub,.by",
            "active": ".epigraph"
          }
        },
        {
          "paragraphs": [2, 4],
          "pause": 1.6,
          "focus": {
            "candidates": ".epigraph,.sub,.by",
            "active": ".sub,.by"
          }
        }
      ]
    }
  ]
}
```

`paragraphs` is a half-open range `[first, last]` over narrated `<p>` elements in the
slide's `<template class="speaker-notes">`. Paragraphs beginning with `Time:` are delivery
cues and are excluded before indexing.

Every slide's beat ranges must:

- start at paragraph 0;
- be contiguous;
- end at the slide's narrated paragraph count;
- contain no empty range.

`focus` may be `null`. When present, both selectors are scoped to the current slide.

## HTML contract

Presented slides are `header` or `section` elements with unique `id` values. Each includes:

```html
<section id="example">
  <h2>Visible title</h2>
  <!-- visible slide content -->
  <template class="speaker-notes">
    <p><b>Time: 0:45.</b> Delivery cue. Not narrated.</p>
    <p>First narrated paragraph.</p>
    <p>Second narrated paragraph.</p>
  </template>
</section>
```

Appendices may be omitted from the configuration.

## Voice design

Describe observable delivery, not celebrity imitation:

- age range and register;
- vocal energy;
- accent or dialect;
- pace and diction;
- relationship to the audience;
- behaviors to avoid.

Default:

> Calm and authoritative with a warm low-mid register and restrained energy. Clear
> international English, measured pace, and understated confidence. Sound like a senior
> engineer explaining a hard-earned lesson to respected peers. Use natural conversational
> phrasing and selective emphasis. Avoid announcer polish, sales energy, theatrical drama,
> sing-song cadence, and exaggerated sentence endings.

Use a reference sentence that contains the talk's normal vocabulary and emotional range.
Do not use the opening quote if it is unusually dramatic.

## Beat design

A beat is one visual state and one uninterrupted narration file.

Good boundaries:

- setup → reveal;
- claim → evidence;
- first half → second half of a grid;
- action → verifier;
- case resolution → closing line.

Avoid:

- one beat per sentence;
- a beat over roughly 90 words;
- splitting a sentence across beats;
- visual focus that changes before the spoken subject changes.

Pauses:

- 0.8–1.1s: continuation;
- 1.2–1.6s: idea boundary;
- 1.7–2.2s: reveal, slide close, or final line.

## Story gate

Ask these before rendering:

1. Does the opening expose a real mistake, tension, or decision?
2. Does one case appear in the first two minutes?
3. Does the same case carry the conceptual progression?
4. Is every historical claim traceable?
5. Does the talk demonstrate a failure and a recovery or honest stop?
6. Does the final line restate the argument the case actually proved?
7. Are human responsibilities explicit?
8. Are there three or fewer closing takeaways?

Common failure: a deck calls a hypothetical prompt answer historical. Use:

- “A prompt-only review **could have** looked ready.”
- “The audit **found** zero dedicated alerts.”

Do not write: “The recommendation changed” unless an actual prior recommendation exists.

## Visual gate

At both validation viewports:

- no child content extends below the viewport;
- no label intersects a card number;
- outcome text remains at least 16px;
- body text intended for projection remains at least 18px where practical;
- inactive focus states remain legible enough to preserve orientation;
- diagrams match the roles and edges described in the narration.

Prefer a compact responsive layout over shrinking all typography.

## Audio gate

Required:

- one canonical reference voice;
- median pairwise speaker similarity near 0.99 for Qwen speaker embeddings;
- pace factors normally within 0.75–1.25;
- no clipping;
- no unexplained silence of 2.5 seconds or more;
- consistent sample rate and mono channel count.

LUFS is contextual. Spoken technical presentations often land around -20 to -16 LUFS.
Do not compress a voice merely to hit a number if it already sounds natural.

## Video gate

Required:

- 1920×1080 H.264 video;
- AAC audio;
- full decode succeeds;
- number of frames equals number of configured beats;
- number of holds equals beats;
- number of transitions equals beats minus one;
- cumulative video timing drift under one frame;
- `+faststart` enabled.

Frame drift must be prevented during construction. Keep a floating target clock and assign
each state:

```text
state_frames = round(cumulative_target_frames) - emitted_frames
```

Do not independently `ceil()` every segment.

## Recovery

- **One slide changed:** rerender only that slide, then normalize and rebuild everything.
- **Voice identity drift:** keep the reference; regenerate the outlier beat with a different
  deterministic seed.
- **Pacing factor outlier:** regenerate before changing the global WPM.
- **Text clips at 1366×768:** use a compact height media query or change grid columns.
- **Video drift:** inspect cumulative frame allocation, not the final mux.
- **gws rejects an absolute path:** run from the file's directory and upload `./file.mp4`.
- **Hosted HTML is stale:** verify by fetching and asserting unique final text.
