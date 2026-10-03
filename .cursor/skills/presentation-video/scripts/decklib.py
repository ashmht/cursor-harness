from __future__ import annotations

import json
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


@dataclass
class SlideNotes:
    slide_id: str
    heading: str
    paragraphs: list[str]


class DeckParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.current_slide_id: str | None = None
        self.current_heading: list[str] = []
        self.heading_tag: str | None = None
        self.in_notes = False
        self.in_paragraph = False
        self.paragraph: list[str] = []
        self.notes: list[str] = []
        self.slides: list[SlideNotes] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag in {"header", "section"} and attributes.get("id"):
            self.current_slide_id = attributes["id"]
            self.current_heading = []
            self.notes = []
        elif self.current_slide_id and tag in {"h1", "h2", "h3"} and not self.current_heading:
            self.heading_tag = tag
        elif (
            self.current_slide_id
            and tag == "template"
            and "speaker-notes" in (attributes.get("class") or "").split()
        ):
            self.in_notes = True
            self.notes = []
        elif self.in_notes and tag == "p":
            self.in_paragraph = True
            self.paragraph = []

    def handle_endtag(self, tag: str) -> None:
        if self.heading_tag == tag:
            self.heading_tag = None
        elif self.in_notes and tag == "p" and self.in_paragraph:
            text = " ".join("".join(self.paragraph).split())
            if text and not text.startswith("Time:"):
                self.notes.append(text)
            self.in_paragraph = False
        elif tag == "template" and self.in_notes:
            if self.current_slide_id:
                self.slides.append(
                    SlideNotes(
                        slide_id=self.current_slide_id,
                        heading=" ".join("".join(self.current_heading).split()),
                        paragraphs=self.notes.copy(),
                    )
                )
            self.in_notes = False
        elif tag in {"header", "section"}:
            self.current_slide_id = None
            self.heading_tag = None

    def handle_data(self, data: str) -> None:
        if self.in_notes and self.in_paragraph:
            self.paragraph.append(data)
        elif self.current_slide_id and self.heading_tag:
            self.current_heading.append(data)


def parse_deck(path: Path) -> list[SlideNotes]:
    parser = DeckParser()
    parser.feed(path.read_text())
    if not parser.slides:
        raise ValueError(f"No speaker-note templates found in {path}")
    ids = [slide.slide_id for slide in parser.slides]
    if len(ids) != len(set(ids)):
        raise ValueError("Each presented slide must have a unique id")
    return parser.slides


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text())
    if not isinstance(config.get("slides"), list) or not config["slides"]:
        raise ValueError("Config must contain a non-empty slides array")
    return config


def validate_config(
    deck_slides: list[SlideNotes], config: dict[str, Any]
) -> list[SlideNotes]:
    by_id = {slide.slide_id: slide for slide in deck_slides}
    configured: list[SlideNotes] = []
    seen: set[str] = set()

    for slide_config in config["slides"]:
        slide_id = slide_config.get("id")
        if slide_id in seen:
            raise ValueError(f"Duplicate configured slide id: {slide_id}")
        if slide_id not in by_id:
            raise ValueError(f"Configured slide id not found in deck notes: {slide_id}")
        seen.add(slide_id)
        slide = by_id[slide_id]
        beats = slide_config.get("beats")
        if not isinstance(beats, list) or not beats:
            raise ValueError(f"Slide {slide_id} must contain at least one beat")

        expected_start = 0
        for beat_index, beat in enumerate(beats):
            paragraph_range = beat.get("paragraphs")
            if (
                not isinstance(paragraph_range, list)
                or len(paragraph_range) != 2
                or not all(isinstance(value, int) for value in paragraph_range)
            ):
                raise ValueError(
                    f"Slide {slide_id} beat {beat_index + 1} needs [first,last] paragraphs"
                )
            first, last = paragraph_range
            if first != expected_start or last <= first:
                raise ValueError(
                    f"Slide {slide_id} beat ranges must be contiguous and non-empty"
                )
            if last > len(slide.paragraphs):
                raise ValueError(
                    f"Slide {slide_id} beat {beat_index + 1} exceeds note paragraphs"
                )
            if float(beat.get("pause", 0)) < 0:
                raise ValueError(f"Slide {slide_id} beat pause cannot be negative")
            focus = beat.get("focus")
            if focus is not None and (
                not focus.get("candidates") or not focus.get("active")
            ):
                raise ValueError(
                    f"Slide {slide_id} beat focus needs candidates and active selectors"
                )
            expected_start = last

        if expected_start != len(slide.paragraphs):
            raise ValueError(
                f"Slide {slide_id} beats cover {expected_start} of "
                f"{len(slide.paragraphs)} paragraphs"
            )
        configured.append(slide)

    return configured


def beat_text(slide: SlideNotes, beat: dict[str, Any]) -> str:
    first, last = beat["paragraphs"]
    return " ".join(slide.paragraphs[first:last])


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n")
