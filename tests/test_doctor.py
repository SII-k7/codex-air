#!/usr/bin/env python3
"""Cross-platform, privacy-safe Codex AIR doctor contracts."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


class PosixDoctorTests(unittest.TestCase):
    def setUp(self) -> None:
        if os.name == "nt":
            self.skipTest("POSIX doctor execution is covered on macOS/Linux")
        self.temporary = tempfile.TemporaryDirectory(prefix="codex-air-doctor-private-")
        self.home = Path(self.temporary.name) / "private-user-home"
        self.environment = {**os.environ, "ORCHESTRATE_HOME": str(self.home)}
        installed = self.run_script("install.sh")
        self.assertEqual(0, installed.returncode, installed.stdout)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_script(self, script: str, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(SCRIPTS / script), *arguments],
            cwd=ROOT,
            env=self.environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def test_json_reports_versions_cli_and_bundle_without_local_paths(self) -> None:
        result = self.run_script("doctor.sh", "--json")
        self.assertEqual(0, result.returncode, result.stdout)
        report = json.loads(result.stdout)
        release = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

        self.assertEqual(1, report["schema_version"])
        self.assertEqual("pass", report["status"])
        self.assertEqual(release, report["source"]["release_version"])
        self.assertEqual(release, report["installed"]["release_version"])
        self.assertEqual("7", report["installed"]["state_format"])
        self.assertIsInstance(report["codex_cli"]["available"], bool)
        self.assertTrue(report["bundle"]["skills"]["canonical"])
        self.assertTrue(report["bundle"]["skills"]["compatibility"])
        self.assertTrue(report["bundle"]["all_visible_and_matching"])
        self.assertEqual(5, len(report["bundle"]["agents"]))
        self.assertNotIn(str(self.home), result.stdout)
        self.assertNotIn(self.home.name, result.stdout)

    def test_profile_mismatch_returns_parseable_redacted_failure(self) -> None:
        profile = self.home / ".codex/agents/air-efficient-worker.toml"
        profile.write_text(
            profile.read_text(encoding="utf-8").replace(
                'model = "gpt-5.6-luna"', 'model = "unexpected-model"', 1
            ),
            encoding="utf-8",
        )
        result = self.run_script("doctor.sh", "--json")
        self.assertNotEqual(0, result.returncode, result.stdout)
        report = json.loads(result.stdout)
        self.assertEqual("fail", report["status"])
        self.assertFalse(
            report["bundle"]["agents"]["air-efficient-worker.toml"]["profile_matches"]
        )
        self.assertNotIn(str(self.home), result.stdout)

    def test_state_without_optional_provenance_remains_supported(self) -> None:
        state_path = self.home / ".codex/codex-air/install-state"
        retained = [
            line
            for line in state_path.read_text(encoding="utf-8").splitlines()
            if not line.startswith(("release_version=", "source_commit=", "source_dirty="))
        ]
        state_path.write_text("\n".join(retained) + "\n", encoding="utf-8")
        result = self.run_script("doctor.sh", "--json")
        self.assertEqual(0, result.returncode, result.stdout)
        report = json.loads(result.stdout)
        self.assertEqual("unknown", report["installed"]["release_version"])
        self.assertIn(
            "installed release metadata predates provenance reporting", report["warnings"]
        )


class PowerShellDoctorSurfaceTests(unittest.TestCase):
    def test_windows_entrypoints_have_native_parity_and_redacted_json(self) -> None:
        doctor = (SCRIPTS / "doctor.ps1").read_text(encoding="utf-8")
        default = (SCRIPTS / "default.ps1").read_text(encoding="utf-8")
        uninstall = (SCRIPTS / "uninstall.ps1").read_text(encoding="utf-8")

        self.assertIn("#requires -Version 5.1", doctor)
        self.assertIn("ConvertTo-Json", doctor)
        self.assertIn("release_version", doctor)
        self.assertIn("source_commit", doctor)
        self.assertIn("codex_cli", doctor)
        self.assertIn("all_visible_and_matching", doctor)
        self.assertNotIn("$HOME", doctor)
        self.assertIn("status|check|disable", default)
        self.assertIn("default-routing-backups", default)
        self.assertIn("default.ps1 disable", uninstall)


class PowerShellDoctorRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = shutil.which("pwsh") or shutil.which("powershell")
        if self.engine is None:
            self.skipTest("PowerShell is unavailable")
        self.temporary = tempfile.TemporaryDirectory(prefix="codex-air-doctor-ps-")
        self.home = Path(self.temporary.name) / "private-windows-home"
        self.home.mkdir()
        self.environment = {**os.environ, "ORCHESTRATE_HOME": str(self.home)}

    def tearDown(self) -> None:
        if hasattr(self, "temporary"):
            self.temporary.cleanup()

    def run_script(self, script: str, *arguments: str) -> subprocess.CompletedProcess[str]:
        assert self.engine is not None
        return subprocess.run(
            [
                self.engine,
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-File",
                str(SCRIPTS / script),
                *arguments,
            ],
            cwd=ROOT,
            env=self.environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def test_native_install_doctor_default_and_help(self) -> None:
        for script in ("install.ps1", "uninstall.ps1", "doctor.ps1", "default.ps1"):
            helped = self.run_script(script, "--help")
            self.assertEqual(0, helped.returncode, helped.stdout)
            self.assertIn("Usage:", helped.stdout)

        installed = self.run_script("install.ps1")
        self.assertEqual(0, installed.returncode, installed.stdout)
        diagnosed = self.run_script("doctor.ps1", "-Json")
        self.assertEqual(0, diagnosed.returncode, diagnosed.stdout)
        report = json.loads(diagnosed.stdout)
        self.assertEqual("pass", report["status"])
        self.assertEqual(
            (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
            report["installed"]["release_version"],
        )
        self.assertTrue(report["bundle"]["all_visible_and_matching"])
        self.assertNotIn(str(self.home), diagnosed.stdout)

        instructions = self.home / ".codex/AGENTS.md"
        instructions.write_text(
            "<!-- codex-air-default:start -->\nlegacy\n<!-- codex-air-default:end -->\n",
            encoding="utf-8",
        )
        blocked = self.run_script("default.ps1", "check")
        self.assertNotEqual(0, blocked.returncode, blocked.stdout)
        disabled = self.run_script("default.ps1", "disable")
        self.assertEqual(0, disabled.returncode, disabled.stdout)
        self.assertFalse(instructions.exists())
        healthy = self.run_script("doctor.ps1", "-Json")
        self.assertEqual(0, healthy.returncode, healthy.stdout)

        removed = self.run_script("uninstall.ps1")
        self.assertEqual(0, removed.returncode, removed.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
