#!/usr/bin/env python3
"""Cross-surface routing invariants for the v1.1 hybrid architecture."""

from __future__ import annotations

import os
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "codex-air"
AGENTS = ROOT / ".codex" / "agents"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load(name: str) -> dict:
    with (AGENTS / name).open("rb") as handle:
        return tomllib.load(handle)


class RoutingInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = "\n".join(
            read(path)
            for path in (
                SKILL / "SKILL.md",
                SKILL / "references" / "orchestration.md",
                SKILL / "references" / "runtime-notes.md",
            )
        )

    def test_architecture_has_only_sol_control_and_luna_execution(self) -> None:
        self.assertIn("Sol xhigh", self.text)
        self.assertIn("Luna Max Fast", self.text)
        self.assertIn("Terra is forbidden", self.text)
        self.assertIn("Terra has no AIR role", self.text)

    def test_current_host_reuse_avoids_a_second_sol_context(self) -> None:
        self.assertIn("Prefer the current Host", self.text)
        self.assertIn("current conversation", self.text)
        self.assertIn("avoids paying for a second Sol context", self.text)

    def test_single_executor_is_default_and_parallelism_is_latency_gated(self) -> None:
        self.assertIn("One Luna executor is the default", self.text)
        self.assertIn("One executor is normal", self.text)
        self.assertIn("critical-path time", self.text)
        self.assertIn("quality remains non-inferior", self.text)

    def test_complex_is_instructional_not_a_different_model_tier(self) -> None:
        efficient = load("air-efficient-worker.toml")
        complex_worker = load("air-complex-worker.toml")
        for key in ("model", "model_reasoning_effort", "service_tier"):
            self.assertEqual(efficient[key], complex_worker[key])
        self.assertIn("same model and price", read(ROOT / "README.en.md").lower())

    def test_native_nested_and_compatibility_preserve_one_controller(self) -> None:
        runtime = read(SKILL / "references" / "runtime-notes.md")
        self.assertIn("Native Nested", runtime)
        self.assertIn("Compatibility", runtime)
        self.assertIn("same controller", runtime)
        self.assertIn("must not reinterpret", runtime)

    def test_actual_fast_tier_is_observed_not_assumed(self) -> None:
        self.assertIn("requested=fast", self.text)
        self.assertIn("unobserved", self.text)
        self.assertIn("actual response tier", self.text)

    def test_sol_implementation_is_an_accounted_tiny_exception(self) -> None:
        orchestration = " ".join(read(SKILL / "references" / "orchestration.md").split())
        self.assertIn("Never use Sol as a routine write worker", orchestration)
        self.assertIn("tiny integration edit", orchestration)
        self.assertIn("record those Sol implementation tokens separately", orchestration)


class InstalledProfileTests(unittest.TestCase):
    def test_doctor_expectations_match_source_profiles(self) -> None:
        doctor = read(ROOT / "scripts" / "doctor.sh")
        for filename in (
            "air-controller.toml",
            "air-critical-controller.toml",
            "air-complex-worker.toml",
            "air-efficient-worker.toml",
            "air-challenger.toml",
        ):
            self.assertIn(filename, doctor)
        self.assertNotIn('"gpt-5.6-terra"', doctor)

    def test_fresh_install_preserves_exact_profile_bytes(self) -> None:
        if os.name == "nt":
            self.skipTest("POSIX installer; Windows byte lifecycle is covered by windows-lifecycle.ps1")
        with tempfile.TemporaryDirectory(prefix="codex-air-v11-") as raw:
            home = Path(raw)
            result = subprocess.run(
                ["bash", "scripts/install.sh"],
                cwd=ROOT,
                env={**os.environ, "HOME": str(home), "ORCHESTRATE_HOME": str(home)},
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            for source in AGENTS.glob("*.toml"):
                installed = home / ".codex" / "agents" / source.name
                self.assertEqual(source.read_bytes(), installed.read_bytes(), source.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
