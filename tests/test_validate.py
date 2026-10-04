#!/usr/bin/env python3
"""Behavior tests for the layered validator."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_validate():
    spec = importlib.util.spec_from_file_location("harness_validate", ROOT / "scripts" / "validate.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["harness_validate"] = module
    spec.loader.exec_module(module)
    return module


class ValidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_validate()

    def test_email_in_work_tree_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            email = "leak" + "@" + "private.test"
            (root / "note.md").write_text(f"contact {email}\n", encoding="utf-8")
            layer = self.mod.validate_identity(root, self.mod.repo_files(root), [])
            self.assertTrue(any("email address" in error for error in layer.errors))

    def test_public_attribution_email_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "note.md").write_text("author hello@cocoon-ai.com\n", encoding="utf-8")
            layer = self.mod.validate_identity(root, self.mod.repo_files(root), [])
            self.assertEqual(layer.errors, [])

    def test_invalid_yaml_fails_and_valid_yaml_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            broken = root / "bad.yaml"
            broken.write_text("a: [\n  1,\n", encoding="utf-8")
            layer = self.mod.validate_syntax(root, self.mod.repo_files(root))
            self.assertTrue(any("invalid YAML" in error for error in layer.errors))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ok.yaml").write_text("version: 1\nnames:\n  - ruby\n", encoding="utf-8")
            layer = self.mod.validate_syntax(root, self.mod.repo_files(root))
            self.assertEqual(layer.errors, [])

    def test_shell_syntax_and_executable_bit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            broken = root / "bad.sh"
            broken.write_text("#!/bin/bash\nif [\n", encoding="utf-8")
            broken.chmod(0o755)
            layer = self.mod.validate_syntax(root, self.mod.repo_files(root))
            self.assertTrue(any("bad.sh" in error for error in layer.errors))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "plain.sh"
            script.write_text("#!/bin/bash\necho ok\n", encoding="utf-8")
            layer = self.mod.validate_syntax(root, self.mod.repo_files(root))
            self.assertTrue(any("not executable" in error for error in layer.errors))

    def test_deleted_email_remains_visible_in_history(self) -> None:
        email = "leak" + "@" + "private.test"
        author = "maintainer" + "@" + "example.net"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", author], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            secret = root / "secret.md"
            secret.write_text(email + "\n", encoding="utf-8")
            subprocess.run(["git", "add", "secret.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "add secret"], cwd=root, check=True, capture_output=True)
            secret.unlink()
            subprocess.run(["git", "add", "secret.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "remove secret"], cwd=root, check=True, capture_output=True)
            layer = self.mod.validate_identity(root, self.mod.repo_files(root), [])
            self.assertTrue(any(error.startswith("git-history:") and "email" in error for error in layer.errors))

    def test_git_author_email_is_not_a_tree_leak(self) -> None:
        author = "maintainer" + "@" + "example.net"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", author], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            (root / "readme.md").write_text("hello\n", encoding="utf-8")
            subprocess.run(["git", "add", "readme.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True)
            layer = self.mod.validate_identity(root, self.mod.repo_files(root), [])
            self.assertEqual(layer.errors, [])

    def test_commit_trailer_email_is_not_a_tree_leak(self) -> None:
        trailer = "leak" + "@" + "private.test"
        author = "maintainer" + "@" + "example.net"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", author], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            (root / "readme.md").write_text("hello\n", encoding="utf-8")
            subprocess.run(["git", "add", "readme.md"], cwd=root, check=True)
            subprocess.run(
                ["git", "commit", "-m", f"init\n\nCo-authored-by: Someone <{trailer}>"],
                cwd=root,
                check=True,
                capture_output=True,
            )
            layer = self.mod.validate_identity(root, self.mod.repo_files(root), [])
            self.assertEqual(layer.errors, [])


if __name__ == "__main__":
    unittest.main()
