from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import imageio_ffmpeg
import numpy as np
import soundfile as sf
from playwright.sync_api import sync_playwright

from decklib import load_config, parse_deck, validate_config, write_json


MAC_CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
SEMANTIC_SELECTORS = (
    "h1,h2,h3,p,li,td,th,.card,.tool,.callout,.stage-diagram,"
    ".mapcard,.joinrow,.attr,.slede,.mantra"
)


def chrome_path(requested: Path | None) -> str | None:
    if requested:
        return str(requested.resolve())
    if MAC_CHROME.exists():
        return str(MAC_CHROME)
    return shutil.which("google-chrome") or shutil.which("chromium")


def media_duration(ffmpeg: str, path: Path) -> float:
    result = subprocess.run(
        [ffmpeg, "-i", str(path)],
        capture_output=True,
        text=True,
    )
    match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr)
    if not match:
        raise ValueError(f"Could not read media duration: {path}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def add(
    collection: list[dict[str, Any]], code: str, message: str, **details: Any
) -> None:
    collection.append({"code": code, "message": message, **details})


def main() -> None:
    arguments = argparse.ArgumentParser(description="Release gate for presentation video")
    arguments.add_argument("--deck", type=Path, required=True)
    arguments.add_argument("--config", type=Path, required=True)
    arguments.add_argument("--work-dir", type=Path, required=True)
    arguments.add_argument("--audio", type=Path, required=True)
    arguments.add_argument("--video", type=Path, required=True)
    arguments.add_argument("--chrome", type=Path)
    arguments.add_argument(
        "--layout-only",
        action="store_true",
        help="Run deck/config/layout checks before narration exists",
    )
    options = arguments.parse_args()

    deck = options.deck.resolve()
    config = load_config(options.config.resolve())
    slides = validate_config(parse_deck(deck), config)
    work_dir = options.work_dir.resolve()
    work_dir.mkdir(parents=True, exist_ok=True)
    audio_path = options.audio.resolve()
    video_path = options.video.resolve()
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    metrics: dict[str, Any] = {}
    expected_beats = sum(len(slide["beats"]) for slide in config["slides"])

    html = deck.read_text()
    for pattern in config.get("forbidden_patterns", []):
        matches = sorted(set(re.findall(pattern, html)))
        if matches:
            add(
                blockers,
                "forbidden-pattern",
                f"Deck contains forbidden pattern {pattern}",
                matches=matches[:20],
            )

    for directory_name in ("raw-beats", "paced-beats"):
        directory = work_dir / directory_name
        count = len(list(directory.glob("*.wav"))) if directory.exists() else 0
        metrics[f"{directory_name}_count"] = count
        if count < expected_beats:
            add(
                blockers,
                "missing-beats",
                f"{directory_name} has {count} files; expected {expected_beats}",
            )

    pace_report = work_dir / "pace-report.json"
    if not pace_report.exists():
        add(blockers, "missing-pace-report", "pace-report.json is missing")
    else:
        pace = json.loads(pace_report.read_text())
        unsafe = pace.get("unsafe_beats", [])
        metrics["unsafe_pace_beats"] = len(unsafe)
        if unsafe:
            add(
                blockers,
                "unsafe-time-stretch",
                "Regenerate beats outside the 0.75–1.25 pace-factor range",
                beats=unsafe,
            )

    if not audio_path.exists():
        add(blockers, "missing-audio", f"Audio file does not exist: {audio_path}")
    else:
        audio, sample_rate = sf.read(audio_path, dtype="float32")
        if audio.ndim > 1:
            add(blockers, "stereo-audio", "Narration output must be mono")
            audio = audio.mean(axis=1)
        peak = float(np.max(np.abs(audio))) if len(audio) else 0.0
        metrics.update(
            {
                "audio_seconds": round(len(audio) / sample_rate, 4),
                "audio_sample_rate": sample_rate,
                "audio_peak": round(peak, 6),
            }
        )
        if peak >= 0.999:
            add(blockers, "audio-clipping", f"Audio peak is {peak:.4f}")

    hidden = config.get(
        "hide_selectors",
        ".controls,.toc,.scrim,.notes-panel,.hero .scroll-hint,footer",
    )
    validation_viewports = config.get(
        "validation_viewports", [[1920, 1080], [1366, 768]]
    )
    layout_results: list[dict[str, Any]] = []
    with sync_playwright() as playwright:
        executable = chrome_path(options.chrome)
        launch = {
            "headless": True,
            "args": ["--allow-file-access-from-files", "--hide-scrollbars"],
        }
        if executable:
            launch["executable_path"] = executable
        browser = playwright.chromium.launch(**launch)
        for width, height in validation_viewports:
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(deck.as_uri(), wait_until="load")
            page.evaluate("document.fonts.ready")
            page.add_style_tag(
                content=f"""
                html {{ scroll-behavior: auto !important; }}
                {hidden} {{ display: none !important; }}
                *, *::before, *::after {{
                  animation: none !important;
                  transition: none !important;
                }}
                """
            )
            for slide in slides:
                result = page.evaluate(
                    """({slideId, selectors, width, height}) => {
                      const slide = document.getElementById(slideId);
                      if (!slide) return {error: `Missing slide #${slideId}`};
                      slide.scrollIntoView({block: "start"});
                      const elements = Array.from(slide.querySelectorAll(selectors))
                        .filter(el => {
                          const style = getComputedStyle(el);
                          const rect = el.getBoundingClientRect();
                          return style.display !== "none" &&
                            style.visibility !== "hidden" &&
                            rect.width > 0 && rect.height > 0;
                        });
                      const bounds = elements.map(el => {
                        const rect = el.getBoundingClientRect();
                        return {
                          tag: el.tagName.toLowerCase(),
                          className: String(el.className || "").slice(0, 100),
                          text: String(el.textContent || "").trim().slice(0, 80),
                          left: rect.left,
                          right: rect.right,
                          top: rect.top,
                          bottom: rect.bottom,
                          fontSize: parseFloat(getComputedStyle(el).fontSize)
                        };
                      });
                      return {
                        overflow: bounds.filter(item =>
                          item.left < -1 || item.right > width + 1 ||
                          item.top < -1 || item.bottom > height + 1
                        ),
                        tinyText: bounds.filter(item =>
                          item.text && item.fontSize < 16
                        )
                      };
                    }""",
                    {
                        "slideId": slide.slide_id,
                        "selectors": SEMANTIC_SELECTORS,
                        "width": width,
                        "height": height,
                    },
                )
                if result.get("error"):
                    add(blockers, "missing-slide", result["error"])
                    continue
                entry = {
                    "slide": slide.slide_id,
                    "viewport": [width, height],
                    "overflow": result["overflow"],
                    "tiny_text": result["tinyText"],
                }
                layout_results.append(entry)
                if result["overflow"]:
                    add(
                        blockers,
                        "layout-overflow",
                        f"{slide.slide_id} overflows at {width}×{height}",
                        elements=result["overflow"][:10],
                    )
                if result["tinyText"]:
                    add(
                        warnings,
                        "small-text",
                        f"{slide.slide_id} has text below 16px at {width}×{height}",
                        elements=result["tinyText"][:10],
                    )
            page.close()
        browser.close()
    metrics["layout_checks"] = layout_results

    if options.layout_only:
        media_codes = {
            "missing-beats",
            "missing-pace-report",
            "unsafe-time-stretch",
            "missing-audio",
            "stereo-audio",
            "audio-clipping",
        }
        blockers = [item for item in blockers if item["code"] not in media_codes]
        metrics = {
            key: value
            for key, value in metrics.items()
            if key == "layout_checks"
        }
        report = {
            "status": "PASS" if not blockers else "FAIL",
            "blockers": blockers,
            "warnings": warnings,
            "metrics": metrics,
        }
        write_json(work_dir / "qa-layout-report.json", report)
        print(json.dumps(report, indent=2))
        if blockers:
            raise SystemExit(1)
        return

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    if not video_path.exists():
        add(blockers, "missing-video", f"Video file does not exist: {video_path}")
    else:
        decode = subprocess.run(
            [ffmpeg, "-v", "error", "-i", str(video_path), "-f", "null", "-"],
            capture_output=True,
            text=True,
        )
        if decode.returncode:
            add(
                blockers,
                "video-decode",
                "Final video failed a full decode",
                stderr=decode.stderr[-2000:],
            )
        metrics["final_video_seconds"] = round(
            media_duration(ffmpeg, video_path), 4
        )

    timeline_path = work_dir / "timeline.json"
    video_only = work_dir / "video-only.mp4"
    if not timeline_path.exists() or not video_only.exists():
        add(
            blockers,
            "missing-timeline",
            "timeline.json or video-only.mp4 is missing",
        )
    elif audio_path.exists():
        timeline = json.loads(timeline_path.read_text())
        fps = int(timeline["fps"])
        frame_seconds = timeline["total_frames"] / fps
        audio_seconds = float(metrics["audio_seconds"])
        drift = abs(frame_seconds - audio_seconds)
        metrics.update(
            {
                "timeline_states": len(timeline["states"]),
                "timeline_frames": timeline["total_frames"],
                "video_only_seconds": round(media_duration(ffmpeg, video_only), 4),
                "calculated_drift_seconds": round(drift, 6),
                "one_frame_seconds": round(1 / fps, 6),
            }
        )
        if len(timeline["states"]) != expected_beats:
            add(
                blockers,
                "state-count",
                f"Timeline has {len(timeline['states'])} states; "
                f"expected {expected_beats}",
            )
        if drift > 1 / fps:
            add(
                blockers,
                "timing-drift",
                f"Calculated video/audio drift is {drift:.4f}s, over one frame",
            )

    report = {
        "status": "PASS" if not blockers else "FAIL",
        "blockers": blockers,
        "warnings": warnings,
        "metrics": metrics,
    }
    write_json(work_dir / "qa-report.json", report)
    print(json.dumps(report, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
