#!/usr/bin/env python3
"""Behavior tests for the codebase-onboarding scaffold, card builder, and citation checker."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD = ROOT / ".cursor" / "skills" / "codebase-onboarding" / "scripts" / "scaffold.py"
CAPABILITY = """
## Sell

### Billing

Charges a customer's card.

- **Backend:** `app/services/billing`, `app/services/billing/charge.rb:2`
- **Owner:** Payments
"""


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(args), cwd=cwd, text=True, capture_output=True)


class CodebaseOnboardingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        service = self.repo / "app" / "services" / "billing"
        service.mkdir(parents=True)
        (service / "charge.rb").write_text("class Charge\n  def call; end\nend\n")
        run("git", "init", "-q", cwd=self.repo)
        run("git", "add", ".", cwd=self.repo)
        run("git", "-c", "user.email=a@b.com", "-c", "user.name=test", "commit", "-qm", "init", cwd=self.repo)
        self.dest = self.repo / ".cursor" / "skills" / "acme-expert"
        result = run(sys.executable, str(SCAFFOLD), "--company", "Acme", "--dest", str(self.dest), cwd=self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def script(self, name: str, *args: str) -> subprocess.CompletedProcess[str]:
        return run(sys.executable, str(self.dest / "scripts" / name), *args, cwd=self.repo)

    def test_scaffold_fills_placeholders_and_renders(self) -> None:
        skill = (self.dest / "SKILL.md").read_text()
        self.assertIn("name: acme-expert", skill)
        for path in self.dest.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".json"}:
                self.assertNotIn("{{", path.read_text(), path)
        self.assertTrue((self.dest / "codebase-map.html").exists())
        json.loads((self.dest / "card.json").read_text())

    def test_scaffold_refuses_to_overwrite(self) -> None:
        result = run(sys.executable, str(SCAFFOLD), "--company", "Acme", "--dest", str(self.dest), cwd=self.repo)
        self.assertEqual(result.returncode, 2)

    def test_build_card_copies_capabilities(self) -> None:
        capabilities = self.dest / "references" / "capabilities.md"
        capabilities.write_text(capabilities.read_text() + CAPABILITY)
        self.assertEqual(self.script("build_card.py").returncode, 0)
        self.assertEqual(self.script("build_card.py", "--check").returncode, 0)
        rows = json.loads((self.dest / "card.json").read_text())["capabilities"]["rows"]
        self.assertEqual([r["capability"] for r in rows], ["Billing"])
        self.assertIn("Billing", (self.dest / "codebase-map.html").read_text())

    def test_checker_passes_live_citations_and_fails_missing_ones(self) -> None:
        capabilities = self.dest / "references" / "capabilities.md"
        capabilities.write_text(capabilities.read_text() + CAPABILITY)
        self.assertEqual(self.script("check_citations.py").returncode, 0)
        capabilities.write_text(capabilities.read_text() + "\n- **Backend:** `app/services/gone.rb`\n")
        result = self.script("check_citations.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("app/services/gone.rb", result.stdout)

    def test_checker_flags_line_past_end_of_file(self) -> None:
        capabilities = self.dest / "references" / "capabilities.md"
        capabilities.write_text(capabilities.read_text() + "\nSee `app/services/billing/charge.rb:40`.\n")
        result = self.script("check_citations.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("past the end of the file", result.stdout)


if __name__ == "__main__":
    unittest.main()
