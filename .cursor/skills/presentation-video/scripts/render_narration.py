from __future__ import annotations

import argparse
from pathlib import Path

import mlx.core as mx
import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

from decklib import beat_text, load_config, parse_deck, validate_config


VOICE_DESIGN_MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit"
CLONE_MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"


def trim_edges(
    audio: np.ndarray, sample_rate: int, threshold: float = 0.003
) -> np.ndarray:
    frame = max(1, round(sample_rate * 0.02))
    usable = len(audio) // frame * frame
    if not usable:
        return audio
    rms = np.sqrt(np.mean(audio[:usable].reshape(-1, frame) ** 2, axis=1))
    active = np.flatnonzero(rms >= threshold)
    if not len(active):
        return audio
    margin = round(sample_rate * 0.12)
    start = max(0, active[0] * frame - margin)
    end = min(len(audio), (active[-1] + 1) * frame + margin)
    return audio[start:end]


def unit_embedding(model, audio: np.ndarray) -> np.ndarray:
    embedding = np.asarray(model.extract_speaker_embedding(mx.array(audio))).reshape(-1)
    norm = np.linalg.norm(embedding)
    if not norm:
        raise ValueError("TTS model produced a zero speaker embedding")
    return embedding / norm


def main() -> None:
    arguments = argparse.ArgumentParser(description="Render one cloned voice for a deck")
    arguments.add_argument("--deck", type=Path, required=True)
    arguments.add_argument("--config", type=Path, required=True)
    arguments.add_argument("--work-dir", type=Path, required=True)
    arguments.add_argument("--reference", type=Path)
    arguments.add_argument("--slide", help="Render one configured slide id")
    arguments.add_argument("--batch-size", type=int, default=4)
    arguments.add_argument("--voice-design-model", default=VOICE_DESIGN_MODEL)
    arguments.add_argument("--clone-model", default=CLONE_MODEL)
    options = arguments.parse_args()

    deck_slides = parse_deck(options.deck.resolve())
    config = load_config(options.config.resolve())
    slides = validate_config(deck_slides, config)
    raw_dir = options.work_dir.resolve() / "raw-beats"
    raw_dir.mkdir(parents=True, exist_ok=True)
    reference_path = (
        options.reference.resolve()
        if options.reference
        else options.work_dir.resolve() / "reference.wav"
    )
    reference_path.parent.mkdir(parents=True, exist_ok=True)

    voice = config.get("voice") or {}
    reference_text = voice.get("reference_text")
    voice_description = voice.get("description")
    if not reference_text or not voice_description:
        raise ValueError("Config voice needs reference_text and description")

    selected: list[tuple[int, int, str]] = []
    for slide_index, (slide, slide_config) in enumerate(
        zip(slides, config["slides"])
    ):
        if options.slide and slide.slide_id != options.slide:
            continue
        for beat_index, beat in enumerate(slide_config["beats"]):
            selected.append((slide_index, beat_index, beat_text(slide, beat)))
    if options.slide and not selected:
        raise ValueError(f"Unknown configured slide id: {options.slide}")

    if not reference_path.exists():
        print("Designing one canonical reference voice", flush=True)
        design_model = load_model(options.voice_design_model)
        mx.random.seed(4242)
        result = list(
            design_model.generate(
                text=reference_text,
                instruct=voice_description,
                lang_code="English",
                temperature=0.68,
                split_pattern=None,
                max_tokens=1024,
                top_k=40,
                top_p=0.90,
                repetition_penalty=1.08,
                verbose=False,
            )
        )[0]
        reference_audio = trim_edges(
            np.asarray(result.audio, dtype=np.float32), design_model.sample_rate
        )
        sf.write(
            reference_path,
            reference_audio,
            design_model.sample_rate,
            subtype="PCM_16",
        )
        del design_model
        mx.clear_cache()

    print("Loading the reference-conditioned cloning model", flush=True)
    model = load_model(options.clone_model)
    reference_audio, reference_rate = sf.read(reference_path, dtype="float32")
    if reference_audio.ndim > 1:
        reference_audio = reference_audio.mean(axis=1)
    if reference_rate != model.sample_rate:
        raise ValueError(
            f"Reference is {reference_rate} Hz; model expects {model.sample_rate} Hz"
        )
    reference_embedding = unit_embedding(model, reference_audio)
    embeddings: list[np.ndarray] = []

    for batch_start in range(0, len(selected), options.batch_size):
        batch = selected[batch_start : batch_start + options.batch_size]
        labels = ", ".join(
            f"{slide_index + 1}.{beat_index + 1}"
            for slide_index, beat_index, _ in batch
        )
        print(f"Generating slide.beat batch {labels}", flush=True)
        mx.random.seed(8000 + batch_start)
        results = sorted(
            list(
                model.batch_generate(
                    texts=[text for _, _, text in batch],
                    ref_audio=str(reference_path),
                    ref_text=reference_text,
                    lang_code="English",
                    temperature=0.65,
                    max_tokens=4096,
                    top_k=40,
                    top_p=0.90,
                    repetition_penalty=1.5,
                    stream=False,
                    verbose=False,
                )
            ),
            key=lambda result: result.sequence_idx,
        )
        if len(results) != len(batch):
            raise RuntimeError("TTS batch returned an unexpected result count")
        for (slide_index, beat_index, _), result in zip(batch, results):
            audio = trim_edges(
                np.asarray(result.audio, dtype=np.float32), model.sample_rate
            )
            output = raw_dir / f"{slide_index:02d}-{beat_index:02d}.wav"
            sf.write(output, audio, model.sample_rate, subtype="PCM_16")
            embeddings.append(unit_embedding(model, audio))

    similarities = np.asarray(
        [float(np.dot(reference_embedding, embedding)) for embedding in embeddings]
    )
    print(
        "Reference cosine similarity min/median/mean: "
        f"{similarities.min():.4f}/{np.median(similarities):.4f}/"
        f"{similarities.mean():.4f}"
    )
    if len(embeddings) > 1:
        pairwise = np.asarray(
            [
                float(np.dot(left, right))
                for index, left in enumerate(embeddings)
                for right in embeddings[index + 1 :]
            ]
        )
        print(
            "Pairwise cosine similarity min/median/mean: "
            f"{pairwise.min():.4f}/{np.median(pairwise):.4f}/"
            f"{pairwise.mean():.4f}"
        )
    print(f"Wrote {len(selected)} raw beats to {raw_dir}")


if __name__ == "__main__":
    main()
