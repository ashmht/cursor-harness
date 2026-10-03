#!/usr/bin/env python3
"""Cursor session cost tracker — accumulates metrics, estimates tokens/cost on sessionEnd.

Hooks do not expose billing fields. This script proxies cost from:
  - preCompact snapshots (peak context_tokens)
  - stop turn counts
  - postToolUse tool call counts
  - transcript size at session end (chars / 4)

Output on sessionEnd: macOS notification + ~/.cursor/hooks/cost-log.jsonl
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_DIR = Path.home() / ".cursor" / "hooks" / "state"
LOG_PATH = Path.home() / ".cursor" / "hooks" / "cost-log.jsonl"
LAST_SUMMARY = Path.home() / ".cursor" / "hooks" / "last-session-cost.txt"

# Rough API-equivalent $/1M tokens (input, output). Not actual Cursor invoice.
MODEL_RATES: dict[str, tuple[float, float]] = {
    "opus": (15.0, 75.0),
    "sonnet": (3.0, 15.0),
    "haiku": (0.8, 4.0),
    "gpt-5": (2.5, 10.0),
    "gpt-4": (10.0, 30.0),
    "composer": (1.25, 5.0),
    "gemini": (1.25, 5.0),
    "default": (3.0, 15.0),
}

AVG_OUTPUT_TOKENS_PER_TURN = 900
REINGESTION_FACTOR = 0.55  # avg context re-sent per turn vs peak


def load_input() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def session_key(data: dict[str, Any]) -> str:
    for key in ("conversation_id", "session_id", "tab_id"):
        value = str(data.get(key, "")).strip()
        if value:
            return re.sub(r"[^A-Za-z0-9._-]", "_", value)
    return f"unknown-{datetime.now(timezone.utc).strftime('%Y%m%d')}"


def state_path(key: str) -> Path:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    return STATE_DIR / f"{key}.json"


def load_state(key: str) -> dict[str, Any]:
    path = state_path(key)
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "session_key": key,
        "started_at": _now_iso(),
        "turns": 0,
        "tool_calls": 0,
        "compactions": 0,
        "peak_context_tokens": 0,
        "peak_context_pct": 0.0,
        "context_window_size": 200000,
        "models": [],
        "last_model": None,
    }


def save_state(key: str, state: dict[str, Any]) -> None:
    state_path(key).write_text(json.dumps(state, indent=2))


def delete_state(key: str) -> None:
    path = state_path(key)
    if path.exists():
        path.unlink()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _model_rates(model: str | None) -> tuple[float, float]:
    if not model:
        return MODEL_RATES["default"]
    lower = model.lower()
    for needle, rates in MODEL_RATES.items():
        if needle != "default" and needle in lower:
            return rates
    return MODEL_RATES["default"]


def _fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def _fmt_usd(amount: float) -> str:
    if amount < 0.01:
        return f"${amount:.4f}"
    if amount < 1:
        return f"${amount:.3f}"
    return f"${amount:.2f}"


def estimate_tokens_from_transcript(path: str | None) -> int | None:
    if not path or not os.path.isfile(path):
        return None
    try:
        chars = 0
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                chars += len(chunk)
        return max(chars // 4, 0)
    except OSError:
        return None


def estimate_cost(
    *,
    turns: int,
    peak_context: int,
    transcript_tokens: int | None,
    model: str | None,
) -> dict[str, Any]:
    """Rough API-equivalent cost, not Cursor invoice."""
    context_basis = peak_context
    if transcript_tokens and transcript_tokens > context_basis:
        context_basis = transcript_tokens

    if turns <= 0:
        turns = 1

    est_input = int(turns * max(context_basis, 2000) * REINGESTION_FACTOR)
    est_output = int(turns * AVG_OUTPUT_TOKENS_PER_TURN)

    rate_in, rate_out = _model_rates(model)
    cost = (est_input / 1_000_000) * rate_in + (est_output / 1_000_000) * rate_out

    return {
        "est_input_tokens": est_input,
        "est_output_tokens": est_output,
        "est_total_tokens": est_input + est_output,
        "transcript_tokens": transcript_tokens,
        "peak_context_tokens": peak_context,
        "est_api_cost_usd": round(cost, 4),
        "model": model,
        "rate_input_per_m": rate_in,
        "rate_output_per_m": rate_out,
    }


def append_log(record: dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a") as fh:
        fh.write(json.dumps(record) + "\n")


def notify(title: str, message: str) -> None:
    if sys.platform != "darwin":
        return
    import subprocess

    script = (
        f'display notification {json.dumps(message)} '
        f'with title {json.dumps(title)}'
    )
    try:
        subprocess.run(["osascript", "-e", script], check=False, capture_output=True)
    except OSError:
        pass


def handle_session_start(data: dict[str, Any]) -> None:
    key = session_key(data)
    state = load_state(key)
    state["started_at"] = _now_iso()
    state["composer_mode"] = data.get("composer_mode")
    save_state(key, state)
    print("{}")


def handle_stop(data: dict[str, Any]) -> None:
    if data.get("status") != "completed":
        print("{}")
        return

    key = session_key(data)
    state = load_state(key)
    state["turns"] = int(state.get("turns", 0)) + 1

    model = data.get("model_id") or data.get("model")
    if model:
        state["last_model"] = model
        models = state.setdefault("models", [])
        if model not in models:
            models.append(model)

    save_state(key, state)
    print("{}")


def handle_pre_compact(data: dict[str, Any]) -> None:
    key = session_key(data)
    state = load_state(key)
    state["compactions"] = int(state.get("compactions", 0)) + 1

    tokens = int(data.get("context_tokens") or 0)
    pct = float(data.get("context_usage_percent") or 0)
    window = int(data.get("context_window_size") or state.get("context_window_size") or 200000)

    if tokens > int(state.get("peak_context_tokens", 0)):
        state["peak_context_tokens"] = tokens
    if pct > float(state.get("peak_context_pct", 0)):
        state["peak_context_pct"] = pct
    state["context_window_size"] = window

    save_state(key, state)
    print("{}")


def handle_post_tool_use(data: dict[str, Any]) -> None:
    key = session_key(data)
    state = load_state(key)
    state["tool_calls"] = int(state.get("tool_calls", 0)) + 1
    save_state(key, state)
    print("{}")


def handle_session_end(data: dict[str, Any]) -> None:
    key = session_key(data)
    state = load_state(key)

    transcript = (
        data.get("transcript_path")
        or os.environ.get("CURSOR_TRANSCRIPT_PATH")
    )
    transcript_tokens = estimate_tokens_from_transcript(transcript)

    peak = int(state.get("peak_context_tokens", 0))
    if peak == 0 and transcript_tokens:
        peak = transcript_tokens

    turns = int(state.get("turns", 0))
    tool_calls = int(state.get("tool_calls", 0))
    model = state.get("last_model")

    cost = estimate_cost(
        turns=turns,
        peak_context=peak,
        transcript_tokens=transcript_tokens,
        model=model,
    )

    duration_ms = int(data.get("duration_ms") or 0)
    duration_min = duration_ms / 60_000 if duration_ms else 0

    summary = {
        "timestamp": _now_iso(),
        "session_key": key,
        "reason": data.get("reason"),
        "duration_ms": duration_ms,
        "turns": turns,
        "tool_calls": tool_calls,
        "compactions": int(state.get("compactions", 0)),
        "peak_context_pct": state.get("peak_context_pct"),
        "workspace": (data.get("workspace_roots") or [None])[0],
        **cost,
    }

    append_log(summary)

    line = (
        f"~{_fmt_tokens(cost['est_total_tokens'])} tokens "
        f"({_fmt_tokens(cost['est_input_tokens'])} in / "
        f"{_fmt_tokens(cost['est_output_tokens'])} out) · "
        f"est. {_fmt_usd(cost['est_api_cost_usd'])} · "
        f"{turns} turns · {tool_calls} tools"
    )
    if duration_min >= 1:
        line += f" · {duration_min:.0f}m"

    detail = (
        f"Model: {model or 'unknown'} · peak ctx {_fmt_tokens(peak)}"
    )
    if transcript_tokens:
        detail += f" · transcript ~{_fmt_tokens(transcript_tokens)}"

    LAST_SUMMARY.write_text(f"{line}\n{detail}\n")
    notify("Cursor session cost (est.)", line)

    delete_state(key)
    print("{}")


def main() -> None:
    data = load_input()
    event = data.get("hook_event_name", "")

    handlers = {
        "sessionStart": handle_session_start,
        "stop": handle_stop,
        "preCompact": handle_pre_compact,
        "postToolUse": handle_post_tool_use,
        "sessionEnd": handle_session_end,
    }

    handler = handlers.get(event)
    if handler:
        handler(data)
    else:
        print("{}")


if __name__ == "__main__":
    main()
