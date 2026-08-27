#!/usr/bin/env python3
"""Behavior tests for read-only visible-candidate validation."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/codex-air/scripts/persist-visible-candidate.sh"


@unittest.skipIf(os.name == "nt" or not shutil.which("bash") or not shutil.which("git"), "POSIX Git test")
class VisibleCandidatePersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name).resolve()
        self.run_cmd("git", "init", "-q")
        self.run_cmd("git", "config", "user.email", "prove@example.invalid")
        self.run_cmd("git", "config", "user.name", "AIR test")
        (self.repo / "tracked.txt").write_text("baseline\n", encoding="utf-8")
        (self.repo / "deleted.txt").write_text("delete me\n", encoding="utf-8")
        (self.repo / "binary.bin").write_bytes(b"\x00baseline\xff")
        self.run_cmd("git", "add", "-A")
        self.run_cmd("git", "commit", "-qm", "baseline")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_cmd(
        self,
        *args: str,
        check: bool = True,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        command_env = os.environ.copy()
        if env:
            command_env.update(env)
        return subprocess.run(
            args,
            cwd=self.repo,
            check=check,
            env=command_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

    def worktree_snapshot(self) -> dict[str, tuple[str, bytes | str]]:
        snapshot: dict[str, tuple[str, bytes | str]] = {}
        for path in self.repo.rglob("*"):
            relative = path.relative_to(self.repo)
            if relative.parts[0] == ".git" or path.is_dir():
                continue
            if path.is_symlink():
                snapshot[str(relative)] = ("symlink", os.readlink(path))
            else:
                snapshot[str(relative)] = ("file", path.read_bytes())
        return snapshot

    def test_validates_tracked_added_deleted_empty_and_binary_paths_without_mutation(self) -> None:
        (self.repo / "tracked.txt").write_text("reviewed final\n", encoding="utf-8")
        (self.repo / "deleted.txt").unlink()
        (self.repo / "binary.bin").write_bytes(b"\x00reviewed\x10final\xff")
        (self.repo / "added.txt").write_text("staged candidate\n", encoding="utf-8")
        self.run_cmd("git", "add", "added.txt")
        (self.repo / "new file.txt").write_text("new candidate\n", encoding="utf-8")
        (self.repo / "empty.txt").touch()
        (self.repo / "unrelated.txt").write_text("must remain unrelated\n", encoding="utf-8")
        before = self.run_cmd("git", "status", "--porcelain=v1").stdout
        expected = {
            "tracked.txt": (self.repo / "tracked.txt").read_bytes(),
            "binary.bin": (self.repo / "binary.bin").read_bytes(),
            "added.txt": (self.repo / "added.txt").read_bytes(),
            "new file.txt": (self.repo / "new file.txt").read_bytes(),
            "empty.txt": b"",
            "unrelated.txt": (self.repo / "unrelated.txt").read_bytes(),
        }

        trace_fd, trace_name = tempfile.mkstemp(prefix="codex-air-git-trace-")
        os.close(trace_fd)
        trace_path = Path(trace_name)
        try:
            result = self.run_cmd(
                "bash",
                str(SCRIPT),
                "--workspace",
                str(self.repo),
                "tracked.txt",
                "deleted.txt",
                "binary.bin",
                "added.txt",
                "new file.txt",
                "empty.txt",
                env={"GIT_TRACE": str(trace_path)},
            )
            trace = trace_path.read_text(encoding="utf-8")
        finally:
            trace_path.unlink(missing_ok=True)

        self.assertIn("PERSISTENCE_PASS\tpaths=6", result.stdout)
        self.assertNotIn("unrelated.txt", result.stdout)
        for relative in ("tracked.txt", "deleted.txt", "binary.bin", "added.txt", "new file.txt", "empty.txt"):
            self.assertIn(f"PERSISTED\t{relative}\t", result.stdout)
        self.assertIn("PERSISTED\tdeleted.txt\tabsent", result.stdout)
        self.assertIn("git apply --reverse --check --binary", trace)
        self.assertNotIn("git apply --reverse --binary", trace)
        self.assertNotIn("git apply --binary", trace)
        self.assertFalse((self.repo / "deleted.txt").exists())
        for relative, content in expected.items():
            self.assertEqual(content, (self.repo / relative).read_bytes())
        self.assertEqual(before, self.run_cmd("git", "status", "--porcelain=v1").stdout)

    def test_rejects_noncanonical_path_before_validation(self) -> None:
        (self.repo / "tracked.txt").write_text("reviewed final\n", encoding="utf-8")
        result = self.run_cmd(
            "bash",
            str(SCRIPT),
            "--workspace",
            str(self.repo),
            "../tracked.txt",
            check=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("non-canonical relative path", result.stdout)
        self.assertEqual("reviewed final\n", (self.repo / "tracked.txt").read_text(encoding="utf-8"))

    def test_accepts_unambiguous_positional_workspace_shorthand(self) -> None:
        (self.repo / "tracked.txt").write_text("reviewed final\n", encoding="utf-8")
        result = self.run_cmd("bash", str(SCRIPT), str(self.repo), "tracked.txt")
        self.assertIn("PERSISTENCE_PASS\tpaths=1", result.stdout)
        self.assertEqual("reviewed final\n", (self.repo / "tracked.txt").read_text(encoding="utf-8"))

    def test_treats_explicit_path_as_literal_not_git_pathspec(self) -> None:
        (self.repo / "tracked.txt").write_text("reviewed final\n", encoding="utf-8")
        before_status = self.run_cmd("git", "status", "--porcelain=v1").stdout
        result = self.run_cmd(
            "bash",
            str(SCRIPT),
            "--workspace",
            str(self.repo),
            "*.txt",
            check=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("absent and untracked", result.stdout)
        self.assertNotIn("PERSISTED", result.stdout)
        self.assertEqual("reviewed final\n", (self.repo / "tracked.txt").read_text(encoding="utf-8"))
        self.assertEqual(before_status, self.run_cmd("git", "status", "--porcelain=v1").stdout)

    def test_rejects_missing_paths_without_discovering_or_mutating_worktree(self) -> None:
        (self.repo / "tracked.txt").write_text("reviewed final\n", encoding="utf-8")
        (self.repo / "deleted.txt").unlink()
        (self.repo / "binary.bin").write_bytes(b"\x00reviewed\xff")
        (self.repo / "new.txt").write_text("new\n", encoding="utf-8")
        (self.repo / "empty.txt").touch()
        before_status = self.run_cmd("git", "status", "--porcelain=v1").stdout
        before_files = self.worktree_snapshot()

        result = self.run_cmd("bash", str(SCRIPT), "--workspace", str(self.repo), check=False)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("at least one exact relative path is required", result.stdout)
        self.assertNotIn("PERSISTED", result.stdout)
        self.assertEqual(before_files, self.worktree_snapshot())
        self.assertEqual(before_status, self.run_cmd("git", "status", "--porcelain=v1").stdout)

    def test_script_has_no_reverse_or_forward_apply_mutation(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('git apply --reverse --check --binary "$patch_file"', source)
        self.assertNotIn('git apply --reverse --binary "$patch_file"', source)
        self.assertNotIn('git apply --binary "$patch_file"', source)
        self.assertNotIn("replay", source.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
