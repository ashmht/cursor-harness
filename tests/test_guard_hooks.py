#!/usr/bin/env python3
"""Behavior tests for portable guard hooks, pr-body-edit, and post_pending_review lint."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class GuardGitPushTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_module("guard_git_push", ROOT / "hooks" / "guard_git_push.py")

    def test_blocks_main_and_force_and_unpinned_lease(self) -> None:
        cases = [
            ("git push origin main", "deny"),
            ("git push origin HEAD:refs/heads/master", "deny"),
            ("git push -f origin feat/x", "deny"),
            ("git push --force origin feat/x", "deny"),
            ("git push origin +feat/x", "deny"),
            ("git push --force-with-lease origin feat/x", "deny"),
            ("git push --force-with-lease=feat/x origin feat/x", "deny"),
            ("git push --force-with-lease=feat/x:abc1234 origin feat/x", "allow"),
            ("git push -u origin feat/x", "allow"),
            ("echo 'git push --force origin main'", "allow"),
        ]
        for command, want in cases:
            with self.subTest(command=command):
                permission, _, _ = self.mod.check_push(command, cwd="/nonexistent")
                self.assertEqual(permission, want)


class GuardDockerEnvTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_module("guard_docker_env", ROOT / "hooks" / "guard_docker_env.py")

    def test_docker_env_cases(self) -> None:
        cases = [
            ("docker inspect app --format '{{range .Config.Env}}{{println .}}{{end}}' | rg -v token", True),
            ("docker inspect app", True),
            ("docker inspect app | jq '.[0].Config'", True),
            ("docker exec app env", True),
            ("docker exec -it app printenv | grep KEY", True),
            ("docker inspect app --format '{{range .Config.Env}}{{println .}}{{end}}' > /tmp/x.env; echo ok", False),
            ("docker inspect app --format '{{range .Config.Env}}{{println .}}{{end}}' | cut -d= -f1", False),
            ("docker inspect app --format '{{.Config.Image}}'", False),
            ("docker run --rm --env-file /tmp/x.env img bash -lc 'bundle exec rspec'", False),
            ("docker ps --format '{{.Names}} {{.Status}}'", False),
            ("docker inspect app 2>&1 | head", True),
            ("docker exec app env # env-print-ok", False),
            ("cat >> notes.md <<'EOF'\ndocker exec app env\nEOF", False),
            ("cat > a.md <<'EOF'\nprose\nEOF\ndocker exec app env", True),
        ]
        for command, want in cases:
            with self.subTest(command=command):
                self.assertEqual(self.mod.prints_env(command), want)


class GuardGhPrBodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_module("guard_gh_pr_body", ROOT / "hooks" / "guard_gh_pr_body.py")

    def test_gh_pr_body_cases(self) -> None:
        cases = [
            ("gh pr edit 123 --body 'hello'", True),
            ("gh pr edit 123 --body-file /tmp/x.md", True),
            ("gh pr edit 123 -t 'title' --body \"x\"", True),
            ("cd repo && gh pr edit 99 --body-file ./b.md", True),
            ("gh pr edit $N --body-file \"$f\"", True),
            ("gh pr create --title t --body 'new'", False),
            ("gh pr edit 123 --add-label docs", False),
            ("gh pr edit 123 --title 'x'", False),
            ("gh pr view 123 --json body", False),
            ("gh pr edit 123 --body-file x.md # pr-body-ok", False),
            ("echo gh pr edit 123 --body hi", False),
        ]
        for command, want in cases:
            with self.subTest(command=command):
                self.assertEqual(self.mod.denies(command), want)


class PrBodyEditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_module("pr_body_edit", ROOT / "hooks" / "pr-body-edit.py")

    def test_upsert_preserves_other_sections_and_human_edits(self) -> None:
        body = "### Why\nhello\n"
        one = self.mod.upsert_section(body, "query-plans", "plan A")
        self.assertIn("agent-section:query-plans begin", one)
        self.assertIn("### Why\nhello\n", one)

        two = self.mod.upsert_section(one, "query-plans", "plan B")
        self.assertEqual(two.count("agent-section:query-plans begin"), 1)
        self.assertIn("plan B", two)
        self.assertNotIn("plan A", two)

        three = self.mod.upsert_section(two, "rollout", "step 1")
        self.assertEqual(self.mod.list_sections(three), ["query-plans", "rollout"])

        human = three.replace("### Why\nhello\n", "### Why\nhello from human\n")
        four = self.mod.upsert_section(human, "query-plans", "plan C")
        self.assertIn("hello from human", four)
        self.assertIn("plan C", four)


class GuardZshWordSplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_module("guard_zsh_word_split", ROOT / "hooks" / "guard_zsh_word_split.py")

    def test_zsh_word_split_and_equals_expansion(self) -> None:
        cases = [
            ('F="a b c"; bundle exec rspec $F', True),
            ('F="a b c"; bundle exec rspec ${F}', True),
            ('P="pnpm --filter web"; $P lint', True),
            ('F="a b"; for f in $F; do echo $f; done', True),
            ("files=$(git diff --name-only origin/main); rubocop $files", True),
            ('files="$(rg -l foo app)"; wc -l $files', True),
            ("bundle exec rspec $SPEC_FILES", True),
            ('cd /tmp && F="x y" && git diff -- $F', True),
            ('run="123 456"; set -- $run; gh run view $1 --job $2', True),
            ("echo ======", True),
            ("[ $a == b ] && echo y", True),
            ('F="a b c"; bundle exec rspec ${=F}', False),
            ('F="a b c"; bundle exec rspec "$F"', False),
            ("F=(a b c); bundle exec rspec $F", False),
            ('F=(a b c); bundle exec rspec "${F[@]}"', False),
            ('F="a b c"; echo $F', False),
            ('MSG="a b"; [[ -n $MSG ]] && echo ok', False),
            ("SHA=$(git rev-parse HEAD); git show $SHA", False),
            ("echo $HOME; ls $PWD", False),
            ("awk '{print $1}' file.txt", False),
            ("python3 - <<'EOF'\nfiles = '$files'\nEOF\necho ok", False),
            ('setopt sh_word_split; F="a b"; rspec $F', False),
            ('F="a b"; rspec $F  # zsh-split-ok', False),
            ("[[ $a == b ]] && echo y", False),
            ("echo '======'", False),
            ("echo ====== # zsh-split-ok", False),
        ]
        for command, expect_block in cases:
            with self.subTest(command=command):
                self.assertEqual(bool(self.mod.findings(command)), expect_block)


class PostPendingReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_module(
            "post_pending_review",
            ROOT / ".cursor" / "skills" / "critical-pr-review" / "scripts" / "post_pending_review.py",
        )

    def test_diff_lines_and_lint(self) -> None:
        patch = "@@ -10,3 +10,4 @@\n ctx\n-old\n+new1\n+new2\n tail\n"
        sides = self.mod.diff_lines(patch)
        self.assertIn(11, sides["LEFT"])
        self.assertIn(11, sides["RIGHT"])
        self.assertIn(12, sides["RIGHT"])

        errors: list[str] = []
        warnings: list[str] = []
        self.mod.lint("Severity: blocking — bad", "comment 1", 90, errors, warnings)
        self.assertEqual(len(errors), 2)

        errors2: list[str] = []
        warnings2: list[str] = []
        self.mod.lint("Blocking: skips auth check on retries. Add guard before enqueue.", "comment 1", 90, errors2, warnings2)
        self.assertEqual(errors2, [])
        self.assertEqual(warnings2, [])


if __name__ == "__main__":
    unittest.main()
