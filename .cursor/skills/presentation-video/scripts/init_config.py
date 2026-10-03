from __future__ import annotations

import argparse
import math
from pathlib import Path

from decklib import parse_deck, write_json


DEFAULT_REFERENCE_TEXT = (
    "Better models help. The larger gains come from systems that can see the "
    "right evidence, act within boundaries, check their work, and keep what matters."
)
DEFAULT_VOICE = (
    "Calm and authoritative with a warm low-mid register and restrained energy. "
    "Clear international English, measured pace, and understated confidence. "
    "Sound like a senior engineer explaining a hard-earned lesson to respected peers. "
    "Use natural conversational phrasing and selective emphasis. Avoid announcer polish, "
    "sales energy, theatrical drama, sing-song cadence, and exaggerated sentence endings."
)


def paragraph_ranges(paragraphs: list[str]) -> list[list[int]]:
    words = [len(paragraph.split()) for paragraph in paragraphs]
    beat_count = max(1, min(4, math.ceil(sum(words) / 80)))
    beat_count = min(beat_count, len(paragraphs))
    target = sum(words) / beat_count
    ranges: list[list[int]] = []
    first = 0
    accumulated = 0

    for index, count in enumerate(words):
        accumulated += count
        paragraphs_left = len(paragraphs) - index - 1
        groups_left = beat_count - len(ranges) - 1
        if groups_left and accumulated >= target and paragraphs_left >= groups_left:
            ranges.append([first, index + 1])
            first = index + 1
            accumulated = 0

    ranges.append([first, len(paragraphs)])
    return ranges


def main() -> None:
    arguments = argparse.ArgumentParser(
        description="Create a presentation-video configuration skeleton"
    )
    arguments.add_argument("deck", type=Path)
    arguments.add_argument("-o", "--output", type=Path, required=True)
    options = arguments.parse_args()

    slides = parse_deck(options.deck.resolve())
    config = {
        "title": options.deck.stem,
        "words_per_minute": 136,
        "fps": 30,
        "viewport": [1920, 1080],
        "validation_viewports": [[1920, 1080], [1366, 768]],
        "same_slide_transition": 0.35,
        "between_slide_transition": 0.5,
        "forbidden_patterns": ["PROJ-[0-9]+", "INC-[0-9]+"],
        "hide_selectors": (
            ".controls,.toc,.scrim,.notes-panel,.hero .scroll-hint,footer"
        ),
        "voice": {
            "reference_text": DEFAULT_REFERENCE_TEXT,
            "description": DEFAULT_VOICE,
        },
        "slides": [],
    }

    for slide in slides:
        ranges = paragraph_ranges(slide.paragraphs)
        config["slides"].append(
            {
                "id": slide.slide_id,
                "heading": slide.heading,
                "beats": [
                    {
                        "paragraphs": paragraph_range,
                        "pause": 1.5 if index == len(ranges) - 1 else 1.0,
                        "focus": None,
                    }
                    for index, paragraph_range in enumerate(ranges)
                ],
            }
        )

    options.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    write_json(options.output.resolve(), config)
    print(
        f"Wrote {options.output} with {len(slides)} slides and "
        f"{sum(len(slide['beats']) for slide in config['slides'])} beats"
    )


if __name__ == "__main__":
    main()
