from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
import soundfile as sf

from decklib import (
    beat_text,
    load_config,
    parse_deck,
    validate_config,
    write_json,
)


def atempo_filter(factor: float) -> str:
    factors: list[float] = []
    while factor > 2:
        factors.append(2.0)
        factor /= 2
    while factor < 0.5:
        factors.append(0.5)
        factor /= 0.5
    factors.append(factor)
    return ",".join(f"atempo={value:.8f}" for value in factors)


def main() -> None:
    arguments = argparse.ArgumentParser(description="Normalize deck narration pacing")
    arguments.add_argument("--deck", type=Path, required=True)
    arguments.add_argument("--config", type=Path, required=True)
    arguments.add_argument("--work-dir", type=Path, required=True)
    arguments.add_argument("--output", type=Path, required=True)
    options = arguments.parse_args()

    config = load_config(options.config.resolve())
    slides = validate_config(parse_deck(options.deck.resolve()), config)
    words_per_minute = float(config.get("words_per_minute", 136))
    if words_per_minute <= 0:
        raise ValueError("words_per_minute must be positive")

    work_dir = options.work_dir.resolve()
    raw_dir = work_dir / "raw-beats"
    beat_dir = work_dir / "paced-beats"
    slide_dir = work_dir / "slide-audio"
    beat_dir.mkdir(parents=True, exist_ok=True)
    slide_dir.mkdir(parents=True, exist_ok=True)
    options.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    report: list[dict[str, object]] = []
    full_audio: list[np.ndarray] = []
    expected_rate: int | None = None

    for slide_index, (slide, slide_config) in enumerate(
        zip(slides, config["slides"])
    ):
        slide_audio: list[np.ndarray] = []
        for beat_index, beat in enumerate(slide_config["beats"]):
            raw_path = raw_dir / f"{slide_index:02d}-{beat_index:02d}.wav"
            paced_path = beat_dir / f"{slide_index:02d}-{beat_index:02d}.wav"
            if not raw_path.exists():
                raise FileNotFoundError(f"Missing narration beat: {raw_path}")
            info = sf.info(raw_path)
            if info.channels != 1:
                raise ValueError(f"Narration must be mono: {raw_path}")
            if expected_rate is None:
                expected_rate = info.samplerate
            elif info.samplerate != expected_rate:
                raise ValueError(f"Mixed sample rates detected at {raw_path}")

            text = beat_text(slide, beat)
            word_count = len(text.split())
            target_duration = word_count / words_per_minute * 60
            factor = info.duration / target_duration
            record = {
                "slide": slide.slide_id,
                "beat": beat_index + 1,
                "words": word_count,
                "raw_seconds": round(info.duration, 4),
                "target_seconds": round(target_duration, 4),
                "pace_factor": round(factor, 4),
                "safe": 0.75 <= factor <= 1.25,
            }
            report.append(record)
            print(
                f"{slide.slide_id} beat {beat_index + 1}: "
                f"{info.duration:.1f}s -> {target_duration:.1f}s ({factor:.3f}x)",
                flush=True,
            )
            subprocess.run(
                [
                    ffmpeg,
                    "-y",
                    "-loglevel",
                    "error",
                    "-i",
                    str(raw_path),
                    "-filter:a",
                    atempo_filter(factor),
                    "-ar",
                    str(info.samplerate),
                    "-ac",
                    "1",
                    "-c:a",
                    "pcm_s16le",
                    str(paced_path),
                ],
                check=True,
            )
            audio, sample_rate = sf.read(paced_path, dtype="float32")
            pause = float(beat.get("pause", 0))
            slide_audio.extend(
                [
                    audio,
                    np.zeros(round(pause * sample_rate), dtype=np.float32),
                ]
            )

        combined_slide = np.concatenate(slide_audio)
        sf.write(
            slide_dir / f"{slide_index:02d}.wav",
            combined_slide,
            expected_rate,
            subtype="PCM_16",
        )
        full_audio.append(combined_slide)

    if expected_rate is None:
        raise ValueError("No narration beats were configured")
    sf.write(
        options.output.resolve(),
        np.concatenate(full_audio),
        expected_rate,
        subtype="PCM_16",
    )
    write_json(
        work_dir / "pace-report.json",
        {
            "words_per_minute": words_per_minute,
            "beats": report,
            "unsafe_beats": [item for item in report if not item["safe"]],
        },
    )
    factors = [float(item["pace_factor"]) for item in report]
    print(
        "Pacing factor min/median/max: "
        f"{min(factors):.3f}/{np.median(factors):.3f}/{max(factors):.3f}"
    )
    print(f"Wrote {options.output.resolve()}")


if __name__ == "__main__":
    main()
