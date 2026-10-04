#!/usr/bin/env python3
"""Behavior tests for the session-cost hook."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "session-cost.py"


def run_hook(home: Path, payload: dict) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["HOME"] = str(home)
    return subprocess.run(
        ["python3", str(HOOK)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


class SessionCostTests(unittest.TestCase):
    def test_bad_payloads_fail_open(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            percent = run_hook(
                home,
                {
                    "hook_event_name": "preCompact",
                    "conversation_id": "s",
                    "context_tokens": "12%",
                },
            )
            self.assertEqual(percent.returncode, 0)
            self.assertEqual(percent.stdout.strip(), "{}")

            env = os.environ.copy()
            env["HOME"] = str(home)
            invalid = subprocess.run(
                ["python3", str(HOOK)],
                input="{not json",
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            self.assertEqual(invalid.returncode, 0)
            self.assertEqual(invalid.stdout.strip(), "{}")

    def test_summary_matches_priced_turns_and_end_model(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            result = run_hook(
                home,
                {
                    "hook_event_name": "sessionEnd",
                    "conversation_id": "s1",
                    "model": "gpt-5",
                    "duration_ms": 5000,
                },
            )
            self.assertEqual(result.returncode, 0)
            summary = (home / ".cursor" / "hooks" / "last-session-cost.txt").read_text()
            self.assertIn("1 turns", summary)
            self.assertNotIn("0 turns", summary)
            self.assertIn("Model: gpt-5", summary)
            self.assertIn("$0.012", summary)

    def test_tool_counts_are_append_only_and_unscoped_events_do_not_merge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            run_hook(home, {"hook_event_name": "sessionStart", "conversation_id": "s"})
            state = home / ".cursor" / "hooks" / "state" / "s.json"
            before = state.stat().st_mtime_ns
            run_hook(home, {"hook_event_name": "postToolUse", "conversation_id": "s"})
            run_hook(home, {"hook_event_name": "postToolUse", "conversation_id": "s"})
            self.assertEqual(state.stat().st_mtime_ns, before)
            tool_log = home / ".cursor" / "hooks" / "state" / "s.tools"
            self.assertEqual(tool_log.read_text().count("\n"), 2)

            run_hook(home, {"hook_event_name": "postToolUse"})
            run_hook(home, {"hook_event_name": "postToolUse"})
            names = sorted(path.name for path in (home / ".cursor" / "hooks" / "state").iterdir())
            self.assertEqual(names, ["s.json", "s.tools"])

            run_hook(
                home,
                {
                    "hook_event_name": "sessionEnd",
                    "conversation_id": "s",
                    "model": "composer",
                },
            )
            summary = (home / ".cursor" / "hooks" / "last-session-cost.txt").read_text()
            self.assertIn("2 tools", summary)
            self.assertIn("Model: composer", summary)


if __name__ == "__main__":
    unittest.main()
