---
name: presentation-video
description: Turns a self-contained HTML slide deck with embedded speaker notes into a polished narrated MP4. Audits the story, generates one consistent cloned TTS voice, normalizes pacing, renders beat-aligned focus states and dissolves, verifies projector layouts and media timing, and optionally uploads the result to Google Drive with gws. Use when the user asks to make, narrate, rebuild, review, or publish a presentation video.
---

# Presentation video

**Presentation video** is the procedure for turning an HTML slide deck and its embedded
speaker notes into a beat-synchronized narrated MP4. It is not a screen-recording
procedure. The renderer creates deliberate visual states for the ideas being spoken.

Use `wow-deck` first when the user still needs an HTML deck. This skill starts from a
self-contained HTML deck containing one `<template class="speaker-notes">` per presented
`header` or `section`.

## Non-negotiable gates

Do not call the result final until all pass:

1. **Story:** one concrete case or question runs through the talk. Hypothetical outcomes
   stay labeled hypothetical. Factual claims cite an artifact, source, or date.
2. **Slides:** no clipping at 1920×1080 or 1366×768. Projector body text is at least
   18px where practical; outcome labels are at least 16px.
3. **Notes:** visible content and narration agree. Timing labels sum to the expected
   runtime. Delivery cues are not narrated.
4. **Voice:** design one canonical reference voice, then clone that reference for every
   beat. Never redesign the voice independently per slide.
5. **Pacing:** default to 136 WPM. Regenerate beats outside a 0.75–1.25 time-stretch
   factor before accepting mechanical stretching.
6. **Video:** focus changes align to semantic beats. Use restrained dissolves. Allocate
   frames cumulatively so drift stays below one frame.
7. **Media:** every beat exists, MP4/WAV decode, no clipping, no narration dropout,
   and video/audio drift is below one frame.
8. **Privacy:** remove ticket IDs, customer identifiers, and internal-only details that
   do not help the audience. Do not hide the evidence needed to support a claim.

## Workflow

### 1. Audit before rendering

Review the deck and notes across three independent surfaces:

- **Story and claims:** hook, case continuity, transitions, evidence, human role, close.
- **Visuals:** hierarchy, clipping, overlap, density, projector readability, accessibility.
- **Media plan:** beat boundaries, focus selectors, pauses, runtime, transitions.

Lead with blockers. Fix factual integrity before visual polish.

For a case study, distinguish:

- what a prompt-only review **could** have concluded;
- what the evidence-backed workflow **actually** found;
- what remained incomplete or blocked.

### 2. Create the render configuration

```bash
python3 ~/.cursor/skills/presentation-video/scripts/init_config.py \
  deck.html -o presentation-video.json
```

Review every generated beat. Edit `presentation-video.json` so each beat contains:

- a contiguous paragraph range from the slide's speaker notes;
- a deliberate pause after the beat;
- optional CSS focus selectors:
  - `candidates`: elements eligible for dimming;
  - `active`: elements kept at full emphasis.

Do not add focus animation merely to create motion. Use it to direct attention to the
sentence currently being spoken.

Run the early layout gate before spending time on narration:

```bash
python3 ~/.cursor/skills/presentation-video/scripts/qa.py \
  --deck deck.html \
  --config presentation-video.json \
  --work-dir /tmp/my-talk-video \
  --audio /tmp/not-rendered.wav \
  --video /tmp/not-rendered.mp4 \
  --layout-only
```

### 3. Generate one canonical voice

Use an Apple Silicon Python environment with:

```bash
pip install mlx-audio soundfile numpy imageio-ffmpeg playwright
```

Render all narration:

```bash
PYTHON=/path/to/mlx-python
"$PYTHON" ~/.cursor/skills/presentation-video/scripts/render_narration.py \
  --deck deck.html \
  --config presentation-video.json \
  --work-dir /tmp/my-talk-video
```

The first run designs a reference voice. Later runs reuse it. To regenerate only one
changed slide:

```bash
"$PYTHON" ~/.cursor/skills/presentation-video/scripts/render_narration.py \
  --deck deck.html \
  --config presentation-video.json \
  --work-dir /tmp/my-talk-video \
  --slide slide-id
```

### 4. Normalize pacing

```bash
"$PYTHON" ~/.cursor/skills/presentation-video/scripts/normalize_audio.py \
  --deck deck.html \
  --config presentation-video.json \
  --work-dir /tmp/my-talk-video \
  --output talk.wav
```

Inspect `pace-report.json`. Regenerate beats outside the safe factor range. Do not hide a
bad take with extreme time stretching.

### 5. Build the video

```bash
"$PYTHON" ~/.cursor/skills/presentation-video/scripts/build_video.py \
  --deck deck.html \
  --config presentation-video.json \
  --work-dir /tmp/my-talk-video \
  --audio talk.wav \
  --output talk.mp4
```

The renderer:

- captures one 1920×1080 frame per semantic beat;
- dims only configured candidates;
- uses 0.35s same-slide and 0.50s slide-to-slide dissolves by default;
- allocates frames from a cumulative clock to prevent drift;
- writes H.264 video with AAC audio and fast-start metadata.

### 6. Run the release gate

```bash
"$PYTHON" ~/.cursor/skills/presentation-video/scripts/qa.py \
  --deck deck.html \
  --config presentation-video.json \
  --work-dir /tmp/my-talk-video \
  --audio talk.wav \
  --video talk.mp4
```

Treat any reported blocker as no-ship. After the automated gate, spot-listen:

- opening;
- the slowest and fastest pace-factor beats;
- the central claim;
- the final minute;
- every regenerated outlier.

Automated audio metrics cannot judge authority, warmth, pronunciation, or whether a pause
feels earned.

### 7. Publish

Upload to the user's Google Drive only when requested:

```bash
gws drive files create \
  --json '{"name":"Presentation.mp4","mimeType":"video/mp4"}' \
  --upload "./Presentation.mp4" \
  --upload-content-type "video/mp4"
```

`gws` only uploads files inside its current directory. Run it from the video's directory.
Verify the upload with `gws drive files get` and return the `webViewLink`. Do not change
sharing permissions unless the user asks.

## Configuration

See [REFERENCE.md](REFERENCE.md) for the JSON contract, voice-design guidance, review
rubric, and recovery procedures.

## Attribution

When publishing or describing the artifact, note that the presentation/video was rendered
with Cursor. Do not imply a human recorded synthetic narration.
