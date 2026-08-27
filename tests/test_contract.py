#!/usr/bin/env python3
"""Core Sol-control/Luna-execution contract tests."""

from __future__ import annotations

import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / ".agents" / "skills" / "codex-air"
AGENT_ROOT = ROOT / ".codex" / "agents"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def contract() -> str:
    return "\n".join(
        read(path)
        for path in (
            SKILL_ROOT / "SKILL.md",
            SKILL_ROOT / "references" / "orchestration.md",
            SKILL_ROOT / "references" / "runtime-notes.md",
        )
    )


def agent(name: str) -> dict:
    with (AGENT_ROOT / f"{name}.toml").open("rb") as handle:
        return tomllib.load(handle)


class RepositoryAndInvocationTests(unittest.TestCase):
    def test_release_version_matches_current_changelog(self) -> None:
        version = read(ROOT / "VERSION").strip()
        self.assertRegex(version, r"^[0-9]+\.[0-9]+\.[0-9]+$")
        changelog = read(ROOT / "CHANGELOG.md")
        self.assertIn(f"## [{version}]", changelog)
        self.assertIn(
            f"[{version}]: https://github.com/SII-k7/codex-air/releases/tag/v{version}",
            changelog,
        )

    def test_canonical_skill_is_explicit_only(self) -> None:
        skill = read(SKILL_ROOT / "SKILL.md")
        metadata = read(SKILL_ROOT / "agents" / "openai.yaml")
        self.assertRegex(skill, r"(?m)^name: codex-air$")
        self.assertIn("explicitly invokes $codex-air", skill)
        self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertIn("Sol", metadata)
        self.assertIn("Luna", metadata)
        self.assertIn("Fast requested", metadata)

    def test_compatibility_alias_redirects_without_a_second_protocol(self) -> None:
        alias = read(ROOT / ".agents" / "skills" / "codex-prove" / "SKILL.md")
        self.assertLess(len(alias.splitlines()), 30)
        self.assertIn("$codex-prove", alias)
        self.assertIn("$codex-air", alias)
        self.assertNotIn("## Planning", alias)

    def test_runtime_defaults_to_chinese(self) -> None:
        text = contract()
        self.assertIn("Use the language of the user's visible request", text)
        self.assertIn("无法判断时默认使用中文", text)


class FixedProfileTests(unittest.TestCase):
    def test_sol_profiles_are_xhigh_standard_read_only(self) -> None:
        for name in ("air-controller", "air-critical-controller", "air-challenger"):
            data = agent(name)
            self.assertEqual("gpt-5.6-sol", data["model"], name)
            self.assertEqual("xhigh", data["model_reasoning_effort"], name)
            self.assertEqual("default", data["service_tier"], name)
            self.assertEqual("read-only", data["sandbox_mode"], name)

    def test_luna_profiles_are_max_fast_write_capable(self) -> None:
        for name in ("air-efficient-worker", "air-complex-worker"):
            data = agent(name)
            self.assertEqual("gpt-5.6-luna", data["model"], name)
            self.assertEqual("max", data["model_reasoning_effort"], name)
            self.assertEqual("fast", data["service_tier"], name)
            self.assertTrue(data["features"]["fast_mode"], name)
            self.assertEqual("workspace-write", data["sandbox_mode"], name)
            self.assertFalse(data["agents"]["enabled"], name)
            self.assertEqual("low", data["model_verbosity"], name)
            self.assertEqual("none", data["model_reasoning_summary"], name)
            self.assertEqual(4000, data["tool_output_token_limit"], name)
            self.assertEqual("none", data["personality"], name)

    def test_every_profile_pins_isolated_context_defaults(self) -> None:
        for path in AGENT_ROOT.glob("*.toml"):
            with path.open("rb") as handle:
                data = tomllib.load(handle)
            self.assertEqual(272_000, data["model_context_window"], path.name)
            self.assertEqual(244_800, data["model_auto_compact_token_limit"], path.name)

    def test_current_profiles_contain_no_terra_model(self) -> None:
        models = {agent(path.stem)["model"] for path in AGENT_ROOT.glob("*.toml")}
        self.assertEqual({"gpt-5.6-sol", "gpt-5.6-luna"}, models)

    def test_workers_cannot_spawn_or_approve_overall_completion(self) -> None:
        for name in ("air-efficient-worker", "air-complex-worker"):
            instructions = agent(name)["developer_instructions"].lower()
            self.assertRegex(instructions, r"(?:do not|never).*(?:create|spawn).*subagent")
            self.assertIn("approve completion", instructions)
            self.assertIn("pass is only a leaf result", instructions)


class SolControlContractTests(unittest.TestCase):
    def test_host_is_reused_only_when_sol_xhigh_is_proved(self) -> None:
        text = contract()
        self.assertIn("Reuse the Host only", text)
        self.assertIn("gpt-5.6-sol", text)
        self.assertIn("xhigh", text)
        self.assertIn("Standard requested tier", text)
        self.assertIn("authoritative", text)
        self.assertIn("Fail Closed", text)

    def test_fallback_requires_proved_sol_and_non_sol_hosts_fail_closed(self) -> None:
        text = " ".join(contract().lower().split())
        self.assertIn("any other proved sol host", text)
        self.assertIn("exactly one read-only fallback `air-controller`", text)
        self.assertIn("exact profile/launch", text)
        self.assertIn("luna, terra, other, or unknown", text)
        self.assertIn("before air child calls", text)
        self.assertIn("actual effort/tier as sol overhead", text)
        self.assertIn("never switch controllers", text)

    def test_hidden_critical_risk_escalates_in_place(self) -> None:
        text = " ".join(contract().lower().split())
        self.assertIn("mode: critical in-place", text)
        self.assertIn("same sol", text)
        self.assertIn("rollback-verification", text)
        self.assertIn("unchanged run envelope", text)
        self.assertIn("never switch controllers", text)

    def test_sol_owns_exploration_solution_and_final_review(self) -> None:
        text = " ".join(contract().split())
        for marker in (
            "repository exploration",
            "solution selection",
            "stable Requirement IDs",
            "decisive repository observations",
            "same Sol controller",
            "complete diff",
            "verify the verifier",
        ):
            self.assertIn(marker.casefold(), text.casefold())
        self.assertIn("Only Sol can issue overall", text)

    def test_direct_admission_avoids_short_task_dispatch(self) -> None:
        text = read(SKILL_ROOT / "SKILL.md")
        self.assertIn("Direct:", text)
        self.assertIn("tiny edits", text)
        self.assertIn("dispatch overhead", text)


class PacketAndExecutionTests(unittest.TestCase):
    def test_task_packet_is_executable_and_context_isolated(self) -> None:
        text = read(SKILL_ROOT / "SKILL.md")
        for marker in (
            "Mode: Single Executor | Coordinated Leaf",
            "Task ID:",
            "Requirement IDs:",
            "Chosen solution:",
            "Decisive observations:",
            "Write scope:",
            "Read scope:",
            "Do not touch:",
            "Baseline:",
            "Verification:",
            "Run envelope:",
            "Efficiency budget:",
            "Parallel proof:",
            "Authorization boundary:",
            "Stop conditions:",
            'fork_turns="none"',
        ):
            self.assertIn(marker, text)

    def test_luna_replans_before_writes_on_material_packet_conflict(self) -> None:
        text = contract()
        self.assertIn("REPLAN_NEEDED", text)
        self.assertRegex(text, r"(?is)before (?:any )?write.*(?:observation|scope|approach)")
        for name in ("air-efficient-worker", "air-complex-worker"):
            instructions = agent(name)["developer_instructions"]
            self.assertIn("REPLAN_NEEDED", instructions)
            self.assertIn("before", instructions)

    def test_worker_result_is_artifact_bound(self) -> None:
        text = read(SKILL_ROOT / "SKILL.md")
        for marker in (
            "Status: PASS | REPLAN_NEEDED | BLOCKED",
            "Requirement coverage:",
            "Verification:",
            "Delivery: NONE | VISIBLE_CANDIDATE",
            "Final file SHA256:",
            "Budget used/remaining:",
            "Runtime tier: requested=fast",
        ):
            self.assertIn(marker, text)
        for counter in ("Sol phases", "Luna calls/launches", "replans", "corrections", "challengers"):
            self.assertIn(counter, text)

    def test_evaluation_isolation_and_python_hygiene_are_mandatory(self) -> None:
        text = contract()
        self.assertIn("evaluation isolation", text.lower())
        self.assertIn("PYTHONDONTWRITEBYTECODE=1", text)
        self.assertIn("sibling worktrees", text)


class SchedulingReviewAndCostTests(unittest.TestCase):
    def test_parallel_gate_is_quantified_and_bounded(self) -> None:
        text = contract()
        for marker in ("65%", "60%", "15%", "two or three", "disjoint ownership", "one long wait"):
            self.assertIn(marker.lower(), text.lower())
        self.assertIn("One executor is normal", text)
        self.assertIn("branch ceilings", text)

    def test_one_file_has_one_owner(self) -> None:
        text = " ".join(contract().lower().split())
        self.assertIn("every task has one owner", text)
        self.assertIn("must never own the same file", text)
        self.assertIn("never widen `write_scope`", text)

    def test_candidate_persistence_fails_closed(self) -> None:
        text = contract()
        normalized = " ".join(text.split())
        self.assertIn("deterministic candidate persistence", text.lower())
        self.assertIn("persist-visible-candidate.sh --workspace", text)
        self.assertIn("<exact-relative-path>", text)
        self.assertIn("PERSISTED", text)
        self.assertIn("never discovers paths", normalized)
        self.assertIn("transfers an isolated candidate", normalized)
        self.assertIn("mutates the worktree", normalized)
        self.assertIn("isolated-only candidate", text)
        self.assertIn("never ask an LLM to reconstruct", text)

    def test_final_verdict_and_correction_are_bounded(self) -> None:
        text = contract()
        self.assertIn("Verdict: PASS | FIX | BLOCKED", text)
        self.assertIn("one focused `FIX` total", text)
        self.assertIn("correction remaining >0", text)
        self.assertIn("at most one replan", text)
        self.assertIn("without reset", text)
        self.assertIn("further material miss", text)

    def test_cost_and_latency_targets_are_measurable(self) -> None:
        text = read(SKILL_ROOT / "SKILL.md")
        for marker in ("55%", "0.85x", "1.15x", "70%", "1.10x", "1.00x"):
            self.assertIn(marker, text)
        self.assertIn("Terra usage must remain zero", text)
        self.assertIn("quality parity first", text)


class EfficiencyContractTests(unittest.TestCase):
    def test_prompt_surface_has_a_regression_budget(self) -> None:
        paths = [
            SKILL_ROOT / "SKILL.md",
            SKILL_ROOT / "references" / "orchestration.md",
            SKILL_ROOT / "references" / "runtime-notes.md",
            *sorted(AGENT_ROOT.glob("*.toml")),
        ]
        self.assertLessEqual(sum(path.stat().st_size for path in paths), 32_000)
        self.assertLessEqual(sum(path.stat().st_size for path in paths[:3]), 21_000)
        self.assertLessEqual((AGENT_ROOT / "air-efficient-worker.toml").stat().st_size, 2_700)
        self.assertLessEqual((AGENT_ROOT / "air-complex-worker.toml").stat().st_size, 2_700)

    def test_controller_stops_at_decision_sufficiency(self) -> None:
        text = contract().lower()
        self.assertIn("decision sufficiency", text)
        self.assertIn("reversible local", text)
        self.assertIn("unresolved material decision", text)

    def test_workers_suppress_repeat_reads_tests_and_short_polls(self) -> None:
        for name in ("air-efficient-worker", "air-complex-worker"):
            instructions = agent(name)["developer_instructions"].lower()
            self.assertIn("reread unchanged", instructions)
            self.assertIn("equivalent passing", instructions)
            self.assertIn("waits of at least 30 seconds", instructions)
            self.assertIn("one-second polling", instructions)
            self.assertIn("convergence", instructions)
            self.assertIn("hard tool ceiling", instructions)
            self.assertIn("failure class budget", instructions)
            self.assertIn("branches or commit", instructions)

    def test_whole_run_budget_is_bounded_and_telemetry_honest(self) -> None:
        text = " ".join(contract().lower().split())
        for marker in (
            "absolute deadline",
            "priced cap/unit",
            "aggregate luna calls/launches",
            "replan <=1",
            "correction <=1 total",
            "challenger=0 normally",
            "share it without reset",
            "event-driven",
            "interrupt",
            "projected or cooperative",
            "mechanically enforced",
        ):
            self.assertIn(marker, text)
        skill = read(SKILL_ROOT / "SKILL.md")
        self.assertIn("48 calls | 80 calls | 30 minutes", skill)
        self.assertIn("96 calls | 180 calls | 60 minutes", skill)

    def test_fresh_evidence_is_reused_and_visible_paths_are_explicit(self) -> None:
        text = " ".join(contract().lower().split())
        self.assertIn("concrete freshness, coverage, or environment gap", text)
        self.assertIn("already be visible", text)
        self.assertIn("exact-relative-path", text)
        self.assertIn("read-only replayability check", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
