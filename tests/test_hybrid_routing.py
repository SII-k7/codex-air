#!/usr/bin/env python3
"""Model-neutral routing and role-profile contracts for Codex AIR."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "codex-air"
FORWARD_CASES = ROOT / "tests" / "fixtures" / "forward-cases.json"
CONTROLLER = ROOT / ".codex" / "agents" / "air-controller.toml"
CRITICAL_CONTROLLER = ROOT / ".codex" / "agents" / "air-critical-controller.toml"
COMPLEX = ROOT / ".codex" / "agents" / "air-complex-worker.toml"
EFFICIENT = ROOT / ".codex" / "agents" / "air-efficient-worker.toml"
CHALLENGER = ROOT / ".codex" / "agents" / "air-challenger.toml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def contract() -> str:
    return "\n".join(
        read(path)
        for path in (
            SKILL / "SKILL.md",
            SKILL / "references" / "orchestration.md",
            SKILL / "references" / "runtime-notes.md",
        )
    )


class AgentProfileTests(unittest.TestCase):
    def assert_default_subagent_context(self, data: dict) -> None:
        self.assertEqual(272_000, data["model_context_window"])
        self.assertEqual(244_800, data["model_auto_compact_token_limit"])

    def test_coordinated_controller_is_luna_max_fast_and_read_only(self) -> None:
        with CONTROLLER.open("rb") as handle:
            data = tomllib.load(handle)
        self.assertEqual("air-controller", data["name"])
        self.assertEqual("gpt-5.6-luna", data["model"])
        self.assertEqual("max", data["model_reasoning_effort"])
        self.assert_default_subagent_context(data)
        self.assertEqual("fast", data["service_tier"])
        self.assertTrue(data["features"]["fast_mode"])
        self.assertEqual("read-only", data["sandbox_mode"])
        self.assertIn("replaceable capability profile", data["developer_instructions"])

    def test_complex_profile_uses_current_terra_default(self) -> None:
        with COMPLEX.open("rb") as handle:
            data = tomllib.load(handle)
        self.assertEqual("air-complex-worker", data["name"])
        self.assertEqual("gpt-5.6-terra", data["model"])
        self.assertEqual("max", data["model_reasoning_effort"])
        self.assert_default_subagent_context(data)
        self.assertEqual("default", data["service_tier"])
        self.assertEqual("workspace-write", data["sandbox_mode"])

    def test_efficient_profile_uses_current_luna_default(self) -> None:
        with EFFICIENT.open("rb") as handle:
            data = tomllib.load(handle)
        self.assertEqual("air-efficient-worker", data["name"])
        self.assertEqual("gpt-5.6-luna", data["model"])
        self.assertEqual("max", data["model_reasoning_effort"])
        self.assert_default_subagent_context(data)
        self.assertEqual("fast", data["service_tier"])
        self.assertTrue(data["features"]["fast_mode"])
        self.assertEqual("workspace-write", data["sandbox_mode"])

    def test_critical_controller_and_challenger_use_sol_max_read_only(self) -> None:
        for path, name in (
            (CRITICAL_CONTROLLER, "air-critical-controller"),
            (CHALLENGER, "air-challenger"),
        ):
            with path.open("rb") as handle:
                data = tomllib.load(handle)
            self.assertEqual(name, data["name"])
            self.assertEqual("gpt-5.6-sol", data["model"])
            self.assertEqual("max", data["model_reasoning_effort"])
            self.assert_default_subagent_context(data)
            self.assertEqual("default", data["service_tier"])
            self.assertEqual("read-only", data["sandbox_mode"])

    def test_workers_are_leaf_agents(self) -> None:
        for path in (COMPLEX, EFFICIENT, CHALLENGER):
            with path.open("rb") as handle:
                instructions = tomllib.load(handle)["developer_instructions"].lower()
            self.assertIn("do not", instructions)
            self.assertIn("subagent", instructions)
            self.assertTrue("spawn" in instructions or "create" in instructions)


class RoutingContractTests(unittest.TestCase):
    def test_lean_skips_controller_and_full_has_one_decision_owner(self) -> None:
        text = contract().lower()
        self.assertIn("lean primary", text)
        self.assertIn("lean has no controller", text)
        self.assertRegex(text, r"(?:only|one) controller")
        self.assertIn("sole graph decision owner", text)
        self.assertIn("controller is luna max fast, read-only", text)

    def test_luna_first_routing_uses_complex_only_for_explicit_triggers(self) -> None:
        text = contract().lower()
        for marker in (
            "lean primary — default",
            "diagnosis-and-fix",
            "ordinary multi-file work",
            "tests",
            "refactors",
        ):
            self.assertIn(marker, text)
        for marker in (
            "public/shared interface",
            "high-consequence",
            "irreducible broad context",
            "materially conflicting evidence",
        ):
            self.assertIn(marker, text)
        self.assertIn("not complex triggers by themselves", text)

    def test_native_nested_and_compatibility_share_the_protocol(self) -> None:
        text = read(SKILL / "references" / "runtime-notes.md")
        self.assertIn("Native Nested", text)
        self.assertIn("Compatibility", text)
        self.assertIn("same requirement graph", text)
        self.assertIn("max_depth >= 2", text)

    def test_model_identity_uses_single_turn_host_proof_and_fails_closed(self) -> None:
        text = contract()
        self.assertIn("Fail Closed", text)
        self.assertIn("authoritative Host/tool", text)
        self.assertIn('fork_turns="none"', text)
        self.assertIn("required configuration", text.lower())
        self.assertIn("complete packet in the first", text.lower())
        self.assertIn("never spend an identity-only", text.lower())

    def test_model_replacement_does_not_require_a_rename(self) -> None:
        runtime = read(SKILL / "references" / "runtime-notes.md")
        self.assertIn("Keep the brand, invocation, role names", runtime)
        self.assertIn(".codex/agents/air-*.toml", runtime)
        self.assertIn("Do not rename Codex AIR", runtime)

    def test_parallel_route_uses_same_level_luna_fast_workers(self) -> None:
        text = " ".join(contract().lower().split())
        self.assertIn("parallel air", text)
        self.assertIn("same gpt-5.6-luna / max / fast", text)
        self.assertIn("two or three air-efficient-worker", text)
        self.assertIn("never use complex merely to increase speed", text)


class ForwardRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = json.loads(read(FORWARD_CASES))
        cls.by_id = {case["id"]: case for case in cls.cases}

    def test_forward_cases_cover_direct_lean_controller_and_both_workers(self) -> None:
        routes = {case["expected"]["route"] for case in self.cases}
        self.assertEqual(
            {
                "direct", "lean_efficient", "controller", "controller_then_efficient",
                "controller_then_parallel_efficient", "controller_then_complex", "blocked",
            },
            routes,
        )

    def test_explicit_bounded_case_defaults_to_lean(self) -> None:
        case = self.by_id["explicit-codex-air"]
        self.assertEqual("lean_efficient", case["expected"]["route"])
        self.assertEqual("none", case["expected"]["controller"])
        self.assertEqual("required", case["expected"]["efficient"])

    def test_forward_cases_cover_parallel_accept_and_reject_gates(self) -> None:
        accept = self.by_id["parallel-high-yield-fast-luna"]
        reject = self.by_id["parallel-coupled-falls-back-lean"]
        self.assertEqual("controller_then_parallel_efficient", accept["expected"]["route"])
        self.assertEqual(3, accept["expected"]["concurrent_luna_workers"])
        self.assertEqual("fast", accept["expected"]["luna_tier"])
        self.assertEqual("lean_efficient", reject["expected"]["route"])
        self.assertEqual("LEAN_RECOMMENDED", reject["expected"]["parallel_gate"])

    def test_forward_cases_cover_zero_write_escalation(self) -> None:
        allow = self.by_id["efficient-first-failure-before-write-escalates-complex"]
        forbid = self.by_id["efficient-first-failure-after-write-keeps-efficient-owner"]
        self.assertEqual("controller_then_complex", allow["expected"]["route"])
        self.assertEqual("controller_then_efficient", forbid["expected"]["route"])
        self.assertIn("before", " ".join(allow["required_assertions"]).lower())
        self.assertIn("owner", " ".join(forbid["required_assertions"]).lower())

    def test_forward_cases_cover_one_file_one_owner(self) -> None:
        case = self.by_id["single-file-unique-owner"]
        assertions = " ".join(case["required_assertions"]).lower()
        self.assertIn("owner", assertions)
        self.assertTrue("one" in assertions or "唯一" in assertions)

    def test_forward_cases_cover_same_run_recovery_and_terminal_bound(self) -> None:
        recover = self.by_id["failed-focused-correction-same-run-replan"]
        terminal = self.by_id["recovery-replan-budget-exhausted"]
        self.assertEqual("same_run", recover["expected"]["recovery"])
        self.assertEqual("PASS", recover["expected"]["review"])
        self.assertEqual("exhausted", terminal["expected"]["recovery"])
        self.assertEqual("BLOCKED", terminal["expected"]["review"])
        self.assertIn("new $codex-air", " ".join(recover["required_assertions"]).lower())


class PosixRoleLifecycleTests(unittest.TestCase):
    def test_install_and_uninstall_preserve_unrelated_files(self) -> None:
        if os.name == "nt":
            self.skipTest("covered by tests/windows-lifecycle.ps1")
        with tempfile.TemporaryDirectory(prefix="codex-air-routing-") as raw:
            home = Path(raw)
            config = home / ".codex" / "config.toml"
            other = home / ".codex" / "agents" / "other-agent.toml"
            other.parent.mkdir(parents=True)
            config.write_text("# user config\n", encoding="utf-8")
            other.write_text('name = "other-agent"\n', encoding="utf-8")
            before = (config.read_bytes(), other.read_bytes())
            env = {**os.environ, "ORCHESTRATE_HOME": str(home)}
            install = subprocess.run(
                ["bash", "scripts/install.sh"], cwd=ROOT, env=env,
                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
            )
            self.assertEqual(0, install.returncode, install.stdout)
            self.assertTrue((home / ".codex/agents/air-complex-worker.toml").is_file())
            doctor = subprocess.run(
                ["bash", "scripts/doctor.sh"], cwd=ROOT, env=env,
                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
            )
            self.assertEqual(0, doctor.returncode, doctor.stdout)
            config.write_text("[features]\nmulti_agent = false\n", encoding="utf-8")
            disabled = subprocess.run(
                ["bash", "scripts/doctor.sh"], cwd=ROOT, env=env,
                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
            )
            self.assertNotEqual(0, disabled.returncode, disabled.stdout)
            self.assertIn("explicitly disables", disabled.stdout)
            config.write_bytes(before[0])
            uninstall = subprocess.run(
                ["bash", "scripts/uninstall.sh"], cwd=ROOT, env=env,
                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
            )
            self.assertEqual(0, uninstall.returncode, uninstall.stdout)
            self.assertEqual(before, (config.read_bytes(), other.read_bytes()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
