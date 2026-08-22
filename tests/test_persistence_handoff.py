#!/usr/bin/env python3
"""Behavior tests for Git-generated visible-candidate persistence."""

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

    def run_cmd(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            args,
            cwd=self.repo,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

    def test_replays_tracked_added_deleted_empty_and_binary_paths_exactly(self) -> None:
        (self.repo / "tracked.txt").write_text("reviewed final\n", encoding="utf-8")
        (self.repo / "deleted.txt").unlink()
        (self.repo / "binary.bin").write_bytes(b"\x00reviewed\x10final\xff")
        (self.repo / "new file.txt").write_text("new candidate\n", encoding="utf-8")
        (self.repo / "empty.txt").touch()
        before = self.run_cmd("git", "status", "--porcelain=v1").stdout
        expected = {
            "tracked.txt": (self.repo / "tracked.txt").read_bytes(),
            "binary.bin": (self.repo / "binary.bin").read_bytes(),
            "new file.txt": (self.repo / "new file.txt").read_bytes(),
            "empty.txt": b"",
        }

        result = self.run_cmd(
            "bash",
            str(SCRIPT),
            "--workspace",
            str(self.repo),
            "tracked.txt",
            "deleted.txt",
            "binary.bin",
            "new file.txt",
            "empty.txt",
        )

        self.assertIn("PERSISTENCE_PASS\tpaths=5", result.stdout)
        self.assertFalse((self.repo / "deleted.txt").exists())
        for relative, content in expected.items():
            self.assertEqual(content, (self.repo / relative).read_bytes())
        self.assertEqual(before, self.run_cmd("git", "status", "--porcelain=v1").stdout)

    def test_rejects_noncanonical_path_before_replay(self) -> None:
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

    def test_auto_discovers_the_complete_visible_dirty_path_set(self) -> None:
        (self.repo / "tracked.txt").write_text("reviewed final\n", encoding="utf-8")
        (self.repo / "new.txt").write_text("new\n", encoding="utf-8")
        result = self.run_cmd("bash", str(SCRIPT), "--workspace", str(self.repo))
        self.assertIn("PERSISTED\ttracked.txt\t", result.stdout)
        self.assertIn("PERSISTED\tnew.txt\t", result.stdout)
        self.assertIn("PERSISTENCE_PASS\tpaths=2", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
