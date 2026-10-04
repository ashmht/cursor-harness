#!/usr/bin/env python3
"""Behavior tests for installer profiles and config merge."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_install():
    spec = importlib.util.spec_from_file_location("harness_install", ROOT / "scripts" / "install.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["harness_install"] = module
    spec.loader.exec_module(module)
    return module


class InstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_install()

    def test_profiles_cover_every_shipped_rule_and_skill(self) -> None:
        rules = {path.name for path in (ROOT / ".cursor" / "rules").glob("*.mdc")}
        covered_rules = set().union(*self.mod.RULE_PROFILES.values())
        self.assertEqual(rules, covered_rules)

        skills = {
            path.parent.name
            for path in (ROOT / ".cursor" / "skills").glob("*/SKILL.md")
        }
        covered_skills = set().union(*self.mod.SKILL_PROFILES.values())
        self.assertEqual(skills - self.mod.EXCLUDED_SKILLS, covered_skills)
        self.assertIn("example-skill", skills)
        self.assertNotIn("example-skill", covered_skills)

    def test_default_profile_is_core_only(self) -> None:
        relative = {path.as_posix() for _, path in self.mod.source_files(None)}
        self.assertIn("rules/workflow.mdc", relative)
        self.assertIn("hooks/session-cost.sh", relative)
        self.assertNotIn("rules/fcis-domain-core.mdc", relative)
        self.assertNotIn("skills/reddit-post-writer/SKILL.md", relative)
        self.assertFalse(any("example-skill" in path for path in relative))

    def test_all_profile_includes_writing_and_fintech(self) -> None:
        relative = {path.as_posix() for _, path in self.mod.source_files(["all"])}
        self.assertIn("rules/fcis-domain-core.mdc", relative)
        self.assertIn("skills/reddit-post-writer/SKILL.md", relative)
        self.assertIn("skills/money-ledger-invariants/SKILL.md", relative)
        self.assertFalse(any("example-skill" in path for path in relative))

    def test_existing_file_conflicts_until_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(self.mod.install(target, apply=True, force=False, profiles=["core"]), 0)
            workflow = target / "rules" / "workflow.mdc"
            workflow.write_text("local edit\n", encoding="utf-8")
            self.assertEqual(self.mod.install(target, apply=False, force=False, profiles=["core"]), 2)
            self.assertEqual(self.mod.install(target, apply=True, force=True, profiles=["core"]), 0)
            self.assertIn("Workflow", workflow.read_text(encoding="utf-8"))
            backups = list((target / "rules").glob("workflow.mdc.bak-*"))
            self.assertEqual(len(backups), 1)

    def test_symlink_source_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "demo"
            skill.mkdir()
            outside = root / "outside.md"
            outside.write_text("x\n", encoding="utf-8")
            (skill / "SKILL.md").symlink_to(outside)
            original = self.mod.SKILLS_ROOT
            self.mod.SKILLS_ROOT = root
            try:
                with self.assertRaises(ValueError):
                    self.mod.source_files(["core"])
            finally:
                self.mod.SKILLS_ROOT = original

    def test_config_merge_keeps_existing_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            user = home / ".config" / "Cursor" / "User"
            user.mkdir(parents=True)
            settings = user / "settings.json"
            settings.write_text(
                json.dumps({"editor.fontSize": 12, "workbench.colorTheme": "Quiet Light"}) + "\n",
                encoding="utf-8",
            )
            original_user_dir = self.mod.cursor_user_dir
            self.mod.cursor_user_dir = lambda _home: user
            try:
                status = self.mod.install_config(home, apply=True, force=False)
            finally:
                self.mod.cursor_user_dir = original_user_dir
            self.assertEqual(status, 0)
            merged = json.loads(settings.read_text(encoding="utf-8"))
            self.assertEqual(merged["editor.fontSize"], 12)
            self.assertEqual(merged["workbench.colorTheme"], "Quiet Light")
            self.assertEqual(merged["[ruby]"]["editor.tabSize"], 2)
            self.assertNotIn("python.defaultInterpreterPath", merged)


if __name__ == "__main__":
    unittest.main()
