#!/usr/bin/env python3
"""Explicit-only invocation and legacy default-routing cleanup contracts."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
START = "<!-- codex-air-default:start -->"
END = "<!-- codex-air-default:end -->"


class ExplicitOnlyStaticContractTests(unittest.TestCase):
    def test_skill_and_interface_reject_implicit_invocation(self) -> None:
        skill = (ROOT / ".agents/skills/codex-air/SKILL.md").read_text(encoding="utf-8")
        interface = (ROOT / ".agents/skills/codex-air/agents/openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("only when the user explicitly invokes $codex-air", skill)
        self.assertIn("allow_implicit_invocation: false", interface)


class ExplicitOnlyRoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        if os.name == "nt":
            self.skipTest("legacy global-routing cleanup targets Ubuntu/macOS Codex homes")
        self.temporary = tempfile.TemporaryDirectory(prefix="codex-air-explicit-")
        self.home = Path(self.temporary.name) / "home"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_script(self, script: str, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = {**os.environ, "ORCHESTRATE_HOME": str(self.home)}
        return subprocess.run(
            ["bash", str(ROOT / "scripts" / script), *arguments],
            cwd=ROOT,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    @property
    def agents(self) -> Path:
        return self.home / ".codex/AGENTS.md"

    def write_legacy_block(self, prefix: str = "", suffix: str = "") -> None:
        self.agents.parent.mkdir(parents=True, exist_ok=True)
        self.agents.write_text(
            f"{prefix}{START}\nlegacy forced routing\n{END}{suffix}",
            encoding="utf-8",
        )

    def test_enable_is_rejected_and_clean_status_passes(self) -> None:
        rejected = self.run_script("default.sh", "enable")
        self.assertNotEqual(0, rejected.returncode, rejected.stdout)
        self.assertIn("invoke $codex-air explicitly", rejected.stdout)

        status = self.run_script("default.sh", "status")
        self.assertEqual(0, status.returncode, status.stdout)
        self.assertIn("explicit-only routing: PASS", status.stdout)
        self.assertFalse(self.home.exists())

    def test_disable_preserves_unrelated_global_instructions_and_backs_up(self) -> None:
        original_prefix = "# My instructions\n\n- Preserve this rule.\n\n"
        original_suffix = "\n\n- Preserve this rule too.\n"
        self.write_legacy_block(original_prefix, original_suffix)

        blocked = self.run_script("default.sh", "check")
        self.assertNotEqual(0, blocked.returncode, blocked.stdout)
        self.assertIn("global default routing is enabled", blocked.stdout)

        disabled = self.run_script("default.sh", "disable")
        self.assertEqual(0, disabled.returncode, disabled.stdout)
        text = self.agents.read_text(encoding="utf-8")
        self.assertNotIn(START, text)
        self.assertNotIn(END, text)
        self.assertIn("Preserve this rule.", text)
        self.assertIn("Preserve this rule too.", text)
        backups = list(
            (self.home / ".codex/codex-air/default-routing-backups").glob("*/AGENTS.md")
        )
        self.assertEqual(1, len(backups))

    def test_malformed_legacy_markers_fail_closed(self) -> None:
        self.agents.parent.mkdir(parents=True)
        self.agents.write_text(f"{START}\npartial\n", encoding="utf-8")
        malformed = self.run_script("default.sh", "disable")
        self.assertNotEqual(0, malformed.returncode, malformed.stdout)
        self.assertIn("malformed", malformed.stdout)

    def test_doctor_rejects_legacy_default_and_passes_after_cleanup(self) -> None:
        installed = self.run_script("install.sh")
        self.assertEqual(0, installed.returncode, installed.stdout)

        self.write_legacy_block()
        blocked = self.run_script("doctor.sh")
        self.assertNotEqual(0, blocked.returncode, blocked.stdout)
        self.assertIn("global default routing is enabled", blocked.stdout)

        guarded = self.run_script("uninstall.sh")
        self.assertNotEqual(0, guarded.returncode, guarded.stdout)
        self.assertIn("default routing is enabled", guarded.stdout)

        self.assertEqual(0, self.run_script("default.sh", "disable").returncode)
        healthy = self.run_script("doctor.sh")
        self.assertEqual(0, healthy.returncode, healthy.stdout)
        self.assertIn("explicit-only routing: PASS", healthy.stdout)

        removed = self.run_script("uninstall.sh")
        self.assertEqual(0, removed.returncode, removed.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
