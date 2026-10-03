from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg
import soundfile as sf
from playwright.sync_api import sync_playwright

from decklib import load_config, parse_deck, validate_config, write_json


MAC_CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def chrome_path(requested: Path | None) -> str | None:
    if requested:
        return str(requested.resolve())
    if MAC_CHROME.exists():
        return str(MAC_CHROME)
    return shutil.which("google-chrome") or shutil.which("chromium")


def main() -> None:
    arguments = argparse.ArgumentParser(description="Build a narrated deck video")
    arguments.add_argument("--deck", type=Path, required=True)
    arguments.add_argument("--config", type=Path, required=True)
    arguments.add_argument("--work-dir", type=Path, required=True)
    arguments.add_argument("--audio", type=Path, required=True)
    arguments.add_argument("--output", type=Path, required=True)
    arguments.add_argument("--chrome", type=Path)
    options = arguments.parse_args()

    deck = options.deck.resolve()
    config = load_config(options.config.resolve())
    slides = validate_config(parse_deck(deck), config)
    work_dir = options.work_dir.resolve()
    beat_dir = work_dir / "paced-beats"
    frame_dir = work_dir / "frames"
    segment_dir = work_dir / "segments"
    frame_dir.mkdir(parents=True, exist_ok=True)
    segment_dir.mkdir(parents=True, exist_ok=True)
    options.output.resolve().parent.mkdir(parents=True, exist_ok=True)

    fps = int(config.get("fps", 30))
    viewport = config.get("viewport", [1920, 1080])
    same_slide_transition = float(config.get("same_slide_transition", 0.35))
    between_slide_transition = float(config.get("between_slide_transition", 0.5))
    hidden = config.get(
        "hide_selectors",
        ".controls,.toc,.scrim,.notes-panel,.hero .scroll-hint,footer",
    )

    states: list[dict[str, object]] = []
    for slide_index, (slide, slide_config) in enumerate(
        zip(slides, config["slides"])
    ):
        for beat_index, beat in enumerate(slide_config["beats"]):
            beat_path = beat_dir / f"{slide_index:02d}-{beat_index:02d}.wav"
            if not beat_path.exists():
                raise FileNotFoundError(f"Missing paced narration: {beat_path}")
            states.append(
                {
                    "slide_index": slide_index,
                    "slide_id": slide.slide_id,
                    "beat_index": beat_index,
                    "focus": beat.get("focus"),
                    "duration": sf.info(beat_path).duration
                    + float(beat.get("pause", 0)),
                    "image": frame_dir / f"{slide_index:02d}-{beat_index:02d}.png",
                }
            )

    with sync_playwright() as playwright:
        executable = chrome_path(options.chrome)
        launch = {
            "headless": True,
            "args": ["--allow-file-access-from-files", "--hide-scrollbars"],
        }
        if executable:
            launch["executable_path"] = executable
        browser = playwright.chromium.launch(**launch)
        page = browser.new_page(
            viewport={"width": int(viewport[0]), "height": int(viewport[1])},
            device_scale_factor=1,
        )
        page.goto(deck.as_uri(), wait_until="load")
        page.evaluate("document.fonts.ready")
        page.add_style_tag(
            content=f"""
            html {{ scroll-behavior: auto !important; }}
            body {{ overflow-x: hidden !important; }}
            {hidden} {{ display: none !important; }}
            *, *::before, *::after {{
              animation: none !important;
              transition: none !important;
              caret-color: transparent !important;
            }}
            """
        )

        for state_number, state in enumerate(states):
            print(
                f"Capturing state {state_number + 1}/{len(states)}: "
                f"{state['slide_id']} beat {int(state['beat_index']) + 1}"
            )
            result = page.evaluate(
                """({slideId, focus}) => {
                  document.querySelectorAll("[data-video-focus]").forEach(el => {
                    el.style.opacity = "";
                    el.style.filter = "";
                    delete el.dataset.videoFocus;
                  });
                  const slide = document.getElementById(slideId);
                  if (!slide) return {error: `Missing slide #${slideId}`};
                  slide.scrollIntoView({block: "start", inline: "nearest"});
                  window.dispatchEvent(new Event("scroll"));
                  if (!focus) return {candidates: 0, active: 0};
                  const candidates = Array.from(
                    slide.querySelectorAll(focus.candidates)
                  );
                  const active = new Set(slide.querySelectorAll(focus.active));
                  candidates.forEach(el => {
                    el.dataset.videoFocus = "1";
                    if (active.has(el)) {
                      el.style.opacity = "1";
                      el.style.filter = "none";
                    } else {
                      el.style.opacity = "0.38";
                      el.style.filter = "grayscale(.35) brightness(.76)";
                    }
                  });
                  return {candidates: candidates.length, active: active.size};
                }""",
                {"slideId": state["slide_id"], "focus": state["focus"]},
            )
            if result.get("error"):
                raise ValueError(result["error"])
            if state["focus"] and (
                result.get("candidates", 0) == 0 or result.get("active", 0) == 0
            ):
                raise ValueError(
                    f"Stale focus selector on {state['slide_id']} "
                    f"beat {int(state['beat_index']) + 1}: {result}"
                )
            page.wait_for_timeout(80)
            page.screenshot(path=str(state["image"]), full_page=False)
        browser.close()

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    segment_paths: list[Path] = []
    emitted_frames = 0
    target_frame_cursor = 0.0
    timeline: list[dict[str, object]] = []

    for state_index, state in enumerate(states):
        has_next = state_index + 1 < len(states)
        same_slide = (
            has_next
            and states[state_index + 1]["slide_index"] == state["slide_index"]
        )
        transition_seconds = (
            same_slide_transition
            if same_slide
            else between_slide_transition
            if has_next
            else 0.0
        )
        duration = float(state["duration"])
        target_frame_cursor += duration * fps
        state_frames = max(1, round(target_frame_cursor) - emitted_frames)
        transition_frames = round(transition_seconds * fps) if transition_seconds else 0
        transition_frames = min(transition_frames, max(0, state_frames - 1))
        hold_frames = max(1, state_frames - transition_frames)
        hold_path = segment_dir / f"{state_index:03d}-hold.mp4"
        run(
            [
                ffmpeg,
                "-y",
                "-loglevel",
                "error",
                "-loop",
                "1",
                "-framerate",
                str(fps),
                "-i",
                str(state["image"]),
                "-frames:v",
                str(hold_frames),
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-tune",
                "stillimage",
                "-pix_fmt",
                "yuv420p",
                "-r",
                str(fps),
                str(hold_path),
            ]
        )
        segment_paths.append(hold_path)
        emitted_frames += hold_frames

        if transition_frames:
            next_image = states[state_index + 1]["image"]
            transition_path = segment_dir / f"{state_index:03d}-transition.mp4"
            actual_transition = transition_frames / fps
            run(
                [
                    ffmpeg,
                    "-y",
                    "-loglevel",
                    "error",
                    "-loop",
                    "1",
                    "-framerate",
                    str(fps),
                    "-i",
                    str(state["image"]),
                    "-loop",
                    "1",
                    "-framerate",
                    str(fps),
                    "-i",
                    str(next_image),
                    "-filter_complex",
                    (
                        f"[0:v][1:v]xfade=transition=fade:"
                        f"duration={actual_transition:.6f}:offset=0,format=yuv420p"
                    ),
                    "-frames:v",
                    str(transition_frames),
                    "-an",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "medium",
                    "-tune",
                    "stillimage",
                    "-pix_fmt",
                    "yuv420p",
                    "-r",
                    str(fps),
                    str(transition_path),
                ]
            )
            segment_paths.append(transition_path)
            emitted_frames += transition_frames

        timeline.append(
            {
                "slide": state["slide_id"],
                "beat": int(state["beat_index"]) + 1,
                "duration_seconds": round(duration, 6),
                "hold_frames": hold_frames,
                "transition_frames": transition_frames,
                "emitted_frames": emitted_frames,
            }
        )

    concat_file = work_dir / "segments.txt"
    concat_file.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in segment_paths)
    )
    video_only = work_dir / "video-only.mp4"
    run(
        [
            ffmpeg,
            "-y",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(video_only),
        ]
    )
    run(
        [
            ffmpeg,
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(video_only),
            "-i",
            str(options.audio.resolve()),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(options.output.resolve()),
        ]
    )
    write_json(
        work_dir / "timeline.json",
        {"fps": fps, "total_frames": emitted_frames, "states": timeline},
    )
    print(f"Wrote {options.output.resolve()}")


if __name__ == "__main__":
    main()
