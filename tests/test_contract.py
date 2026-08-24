#!/usr/bin/env python3
"""Public repository and Skill contracts for Codex AIR v1.0."""

from __future__ import annotations

import json
import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "codex-air"
COMPAT = ROOT / ".agents" / "skills" / "codex-prove"
CONTROLLER = ROOT / ".codex" / "agents" / "air-controller.toml"
CRITICAL_CONTROLLER = ROOT / ".codex" / "agents" / "air-critical-controller.toml"
COMPLEX = ROOT / ".codex" / "agents" / "air-complex-worker.toml"
EFFICIENT = ROOT / ".codex" / "agents" / "air-efficient-worker.toml"
CHALLENGER = ROOT / ".codex" / "agents" / "air-challenger.toml"
REPO_URL = "https://github.com/SII-k7/codex-air"
VERSION = ROOT / "VERSION"


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


class RepositoryStructureTests(unittest.TestCase):
    def test_canonical_skill_structure_exists(self) -> None:
        for path in (
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "references" / "orchestration.md",
            SKILL / "references" / "runtime-notes.md",
            SKILL / "scripts" / "persist-visible-candidate.sh",
        ):
            self.assertTrue(path.is_file(), path)

    def test_compatibility_entry_is_small_and_has_no_second_protocol(self) -> None:
        self.assertTrue((COMPAT / "SKILL.md").is_file())
        self.assertTrue((COMPAT / "agents" / "openai.yaml").is_file())
        self.assertFalse((COMPAT / "references").exists())
        self.assertLess(len(read(COMPAT / "SKILL.md").splitlines()), 30)

    def test_only_model_neutral_agent_source_names_exist(self) -> None:
        names = sorted(path.name for path in (ROOT / ".codex" / "agents").glob("*.toml"))
        self.assertEqual(
            [
                "air-challenger.toml",
                "air-complex-worker.toml",
                "air-controller.toml",
                "air-critical-controller.toml",
                "air-efficient-worker.toml",
            ],
            names,
        )

    def test_public_docs_use_new_repository_url(self) -> None:
        for path in (ROOT / "README.md", ROOT / "README.en.md", ROOT / "SECURITY.md"):
            text = read(path)
            self.assertIn(REPO_URL, text, path.name)
            self.assertNotIn("github.com/yehyakin/codex-codex-air", text, path.name)

    def test_required_release_files_exist(self) -> None:
        for relative in (
            "VERSION", "tests/deepswe-v11-hardest10-results.md",
            "CODEX_AIR_V1_IMPLEMENTATION_REPORT.md",
            "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md", "SUPPORT.md",
            "scripts/install.sh", "scripts/uninstall.sh", "scripts/validate.sh",
            "scripts/default.sh", "scripts/doctor.sh",
            "scripts/install.ps1", "scripts/uninstall.ps1", "scripts/validate.ps1",
            ".agents/skills/codex-air/scripts/persist-visible-candidate.sh",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_release_version_is_1_0_0(self) -> None:
        self.assertEqual("1.0.0", read(VERSION).strip())

    def test_hard_benchmark_is_frozen_without_claiming_a_run(self) -> None:
        fixture = json.loads(read(ROOT / "tests/fixtures/deepswe-v11-ab.json"))
        self.assertEqual("FROZEN_NOT_RUN", fixture["status"])
        self.assertEqual("v1.1", fixture["source"]["benchmark_version"])
        self.assertEqual(113, fixture["source"]["task_count"])
        self.assertEqual(1, fixture["scope"]["attempts_per_arm_task"])
        self.assertLess(fixture["frontier_difficulty_evidence"]["gpt_5_6_sol_max_percent"], 100)
        self.assertLess(fixture["frontier_difficulty_evidence"]["claude_fable_5_max_percent"], 100)
        self.assertIn("passed", fixture["scoring"]["primary_quality"].lower())
        self.assertIn("greater than or equal", fixture["scoring"]["quality_gate"])


class InvocationAndLanguageTests(unittest.TestCase):
    def test_canonical_frontmatter_is_explicit_only(self) -> None:
        text = read(SKILL / "SKILL.md")
        frontmatter = text.split("---", 2)[1]
        self.assertRegex(frontmatter, r"(?m)^name:\s*codex-air\s*$")
        self.assertIn("$codex-air", frontmatter)
        self.assertIn("explicitly invokes", frontmatter)
        self.assertNotIn("AGENTS.md", frontmatter)

    def test_canonical_interface_forbids_implicit_invocation(self) -> None:
        text = read(SKILL / "agents" / "openai.yaml")
        self.assertIn('display_name: "Codex AIR"', text)
        self.assertIn("$codex-air", text)
        self.assertRegex(text, r"(?m)^\s*allow_implicit_invocation:\s*false\s*$")

    def test_legacy_alias_redirects_without_implicit_invocation(self) -> None:
        text = read(COMPAT / "SKILL.md") + read(COMPAT / "agents" / "openai.yaml")
        self.assertIn("$codex-prove", text)
        self.assertIn("$codex-air", text)
        self.assertIn("deprecated", text)
        self.assertRegex(text, r"(?m)^\s*allow_implicit_invocation:\s*false\s*$")

    def test_runtime_defaults_to_chinese(self) -> None:
        self.assertIn("默认使用中文", read(SKILL / "SKILL.md"))
        for path in (CONTROLLER, CRITICAL_CONTROLLER, COMPLEX, EFFICIENT, CHALLENGER):
            with path.open("rb") as handle:
                instructions = tomllib.load(handle)["developer_instructions"]
            self.assertIn("默认使用中文", instructions, path.name)
            self.assertIn("其他语言", instructions, path.name)

    def test_readme_default_is_chinese_with_english_peer(self) -> None:
        self.assertIn("运行时默认使用简体中文", read(ROOT / "README.md"))
        self.assertIn("Runtime output defaults to Simplified Chinese", read(ROOT / "README.en.md"))


class PlanningAndPacketTests(unittest.TestCase):
    def test_plan_has_requirements_tasks_stages_and_integration_owner(self) -> None:
        text = contract()
        for field in ("goal", "done_when", "tasks", "stages", "integration_owner"):
            self.assertRegex(text, rf"(?m)^\s*{field}:\s*", field)

    def test_task_graph_has_dependency_and_launch_fields(self) -> None:
        text = contract()
        for field in (
            "agent_profile", "routing_reason", "dependencies", "read_scope",
            "write_scope", "can_launch", "held_reason",
        ):
            self.assertRegex(text, rf"(?m)^\s*{field}:\s*", field)

    def test_task_packet_is_complete_and_context_is_optional(self) -> None:
        text = contract()
        for field in (
            "Task ID", "Task", "Requirement IDs", "Read scope", "Write scope",
            "Do not touch", "Dependencies", "Expected result", "Verification",
            "Required evidence", "Stop conditions", "Routing reason",
        ):
            self.assertRegex(text, rf"(?m)^\s*{re.escape(field)}:\s*", field)
        self.assertRegex(text, r"(?i)Context:\s*.*optional")

    def test_worker_result_is_structured_and_falsifiable(self) -> None:
        text = contract()
        for field in (
            "Status", "Summary", "Inspected", "Changed", "Requirement coverage",
            "Verification", "Evidence", "Assumptions", "Risks", "Failure class", "Blocker",
        ):
            self.assertRegex(text, rf"(?m)^\s*{re.escape(field)}:\s*", field)
        self.assertRegex(text, r"(?m)^\s*Status:\s*PASS\s*\|\s*BLOCKED\s*$")

    def test_requirement_ids_map_to_evidence(self) -> None:
        text = contract()
        self.assertRegex(text, r"(?is)done_when.{0,400}id:\s*REQ-1.{0,200}criterion:.{0,200}evidence:")
        self.assertRegex(text, r"(?is)tasks:.{0,500}requirements:\s*\[REQ-1\]")


class SchedulingAndOwnershipTests(unittest.TestCase):
    def test_one_file_has_one_owner(self) -> None:
        text = contract().lower()
        self.assertIn("one owner for the entire run", text)
        self.assertIn("shared interface", text)
        self.assertIn("preserve unrelated user changes", text)

    def test_disjoint_ready_tasks_parallelize_and_dependencies_wait(self) -> None:
        text = contract().lower()
        self.assertIn("dependencies are satisfied", text)
        self.assertIn("write scopes are disjoint", text)
        self.assertIn("run sequentially", text)

    def test_parallelism_uses_live_capacity_not_a_fixed_maximum(self) -> None:
        text = contract().lower()
        self.assertIn("live capacity", text)
        self.assertIn("two or three", text)
        self.assertIn("at most three concurrent", text)

    def test_parallel_route_has_a_quantified_latency_gate(self) -> None:
        text = " ".join(contract().lower().split())
        self.assertIn("parallelizable share", text)
        self.assertIn("at least 65%", text)
        self.assertIn("largest branch", text)
        self.assertIn("no more than 60%", text)
        self.assertIn("coordination and integration overhead", text)
        self.assertIn("no more than 15%", text)
        self.assertIn("lean_recommended", text)

    def test_parallel_batch_has_one_barrier_and_one_aggregate_review(self) -> None:
        text = " ".join(contract().lower().split())
        self.assertIn("single concurrent batch", text)
        self.assertIn("do not wait worker-by-worker", text)
        self.assertIn("one long wait", text)
        self.assertIn("deterministic task-id order", text)
        self.assertIn("one aggregate final review", text)

    def test_zero_write_escalation_preserves_ownership(self) -> None:
        text = " ".join(contract().lower().split())
        self.assertIn("before any owned write", text)
        self.assertRegex(text, r"unchanged task.{0,80}scope")
        self.assertIn("never transfer", text)


class EvidenceAndReviewTests(unittest.TestCase):
    def test_final_candidate_changes_invalidate_evidence(self) -> None:
        text = contract().lower()
        self.assertIn("evidence must bind to the final candidate", text)
        self.assertIn("candidate changes", text)
        self.assertIn("stale", text)

    def test_transport_completed_is_not_pass(self) -> None:
        text = " ".join(contract().lower().split())
        self.assertIn("completed", text)
        self.assertIn("delivery lifecycle completion only", text)
        self.assertIn("result-only follow-up", text)

    def test_controller_reviews_artifacts_before_summaries(self) -> None:
        text = contract().lower()
        start = text.index("review artifact-first")
        summary = text.index("worker summaries", start)
        diff = text.index("complete diff", start)
        self.assertLess(diff, summary)

    def test_controller_verifies_the_verifier(self) -> None:
        text = contract().lower()
        self.assertIn("verifies the verifier", text)
        self.assertIn("wrong-module", text)
        self.assertIn("existence-only", text)
        self.assertIn("evidence_quality", text)

    def test_final_verdict_is_closed(self) -> None:
        text = contract()
        self.assertIn("verdict: PASS | FIX | BLOCKED", text)
        self.assertIn("residual_suggestions", text)
        self.assertIn("evidence_quality", text)

    def test_selective_challenge_is_bounded_and_read_only(self) -> None:
        text = " ".join(contract().lower().split())
        self.assertIn("zero challenge calls", text)
        self.assertIn("at most one bounded read-only challenge", text)
        self.assertIn("write_scope: []", text)
        self.assertIn("cannot become a second reviewer", text)
        self.assertIn("air-challenger", text)

    def test_critical_controller_is_selected_only_at_entry(self) -> None:
        text = contract().lower()
        self.assertIn("air-critical-controller", text)
        self.assertIn("select", text)
        self.assertIn("do not switch controllers", text)

    def test_luna_is_the_default_with_explicit_complex_triggers(self) -> None:
        text = " ".join(contract().lower().split())
        for marker in (
            "choose the **efficient** profile by default",
            "bounded diagnosis",
            "ordinary multi-file changes",
            "initially unknown root cause",
            "choose the **complex** profile only",
            "routing_reason",
            "irreducible broad context",
        ):
            self.assertIn(marker, text)
        self.assertIn("cost never overrides safety", text)

    def test_host_and_controllers_do_not_fall_back_to_sol_implementation(self) -> None:
        text = " ".join(contract().lower().split())
        self.assertIn("keep the host and controller out of implementation", text)
        self.assertIn("exact custom worker profile", text)
        self.assertIn("never use a generic or built-in child", text)
        self.assertIn("air-efficient-worker", text)

    def test_correction_is_single_owner_and_same_scope(self) -> None:
        text = " ".join(contract().lower().split())
        self.assertIn("at most one focused correction packet", text)
        self.assertIn("original owner", text)
        self.assertIn("keep the same scope", text)
        self.assertIn("do not relaunch an identical packet", text)

    def test_exhausted_correction_can_replan_inside_the_same_run(self) -> None:
        text = " ".join(contract().lower().split())
        self.assertIn("recovery re-plan", text)
        self.assertIn("same run", text)
        self.assertIn("does not require a new `$codex-air` invocation", text)
        self.assertIn("one recovery re-plan per affected requirement chain", text)
        self.assertIn("must not return final `blocked`", text)

    def test_runtime_recovery_preserves_logical_ownership(self) -> None:
        text = contract().lower()
        self.assertIn("logical owner", text)
        self.assertIn("same exact custom profile", text)
        self.assertIn("is not an ownership transfer", text)
        self.assertIn("result-only recovery does not consume", text)


class LeanEfficiencyInvariantTests(unittest.TestCase):
    def test_host_uses_one_long_wait_without_status_poll_turns(self) -> None:
        text = " ".join(contract().lower().split())
        self.assertIn("timeout_ms=3600000", text)
        self.assertIn("do not short-poll", text)
        self.assertIn("two normal host model turns", text)

    def test_primary_avoids_redundant_discovery_and_bytecode_writes(self) -> None:
        text = read(EFFICIENT).lower()
        self.assertIn("do not search the whole repository, branches, or git history", text)
        self.assertIn("one changed-path baseline", text)
        self.assertIn("one final evidence pass", text)
        self.assertIn("complete-diff audit", text)
        self.assertIn("pythondontwritebytecode=1", text)

    def test_primary_preserves_evaluation_isolation(self) -> None:
        text = read(EFFICIENT).lower()
        for marker in (
            "sibling worktree",
            "previous run",
            "hidden test",
            "evaluation harness",
            "candidate solution",
            "evaluation isolation is a hard boundary",
        ):
            self.assertIn(marker, text)


class ContinuityAndSafetyTests(unittest.TestCase):
    def test_authorized_plan_is_not_a_stop_point(self) -> None:
        text = contract().lower()
        self.assertIn("a plan is not a stop point", text)
        self.assertRegex(text, r"status (?:inquiry|question)\s+does not pause")
        self.assertIn("urgency does not lower", text)

    def test_resume_packet_prevents_duplicate_dispatch(self) -> None:
        text = contract().lower()
        for field in ("run_id", "completed", "in_flight", "ownership", "candidate_identity", "attempts", "next_action"):
            self.assertIn(field, text)
        self.assertIn("do not redispatch completed tasks", text)
        self.assertIn("do not reset attempts", text)

    def test_capability_does_not_widen_authorization(self) -> None:
        text = contract().lower()
        self.assertIn("capability separate from authorization", text)
        self.assertRegex(text, r"broader technical access\s+does not\s+widen")
        self.assertIn("authorization boundary", text)
        self.assertIn("record its own baseline before writes", text)


class LunaPrimaryArchitectureTests(unittest.TestCase):
    def test_lean_has_one_luna_task_context_owner(self) -> None:
        text = " ".join(read(SKILL / "SKILL.md").lower().split())
        self.assertIn("single-semantic-context invariant", text)
        self.assertIn("sole task decision owner and final reviewer", text)
        self.assertIn("may approve the overall lean task", text)

    def test_host_is_transport_only_with_a_mechanical_persistence_gate(self) -> None:
        text = " ".join(read(SKILL / "SKILL.md").lower().split())
        for marker in (
            "thin dispatch-and-integration shim",
            "must not search the repository",
            "does not reread file contents",
            "semantically inspect the diff",
            "rerun verification",
            "second semantic review",
            "persist-visible-candidate.sh",
            "the model never receives or rewrites the patch body",
            "final file sha256",
        ):
            self.assertIn(marker, text)

    def test_isolated_worker_handoff_fails_closed_without_visible_candidate(self) -> None:
        text = " ".join(read(SKILL / "SKILL.md").lower().split())
        for marker in (
            "isolated worktree",
            "git-generated parent-owned replay",
            "never ask the model to serialize a patch",
            "workspace is not a git root",
            "result-only follow-up",
            "final file sha256",
            "failure class: runtime",
        ):
            self.assertIn(marker, text)

    def test_ordinary_lean_has_zero_expensive_children(self) -> None:
        text = " ".join(read(SKILL / "SKILL.md").lower().split())
        self.assertIn("zero sol child calls", text)
        self.assertIn("no sol reviewer", text)
        self.assertIn("no terra worker", text)
        self.assertIn("no challenge by default", text)

    def test_cost_latency_targets_are_measurable_and_quality_gated(self) -> None:
        text = " ".join(read(SKILL / "SKILL.md").lower().split())
        self.assertIn("no more than 55%", text)
        self.assertIn("between 0.8x and 1.2x", text)
        self.assertIn("at least 70%", text)
        self.assertIn("after quality parity is established", text)
        self.assertIn("do not lower verification", text)

    def test_efficient_profile_separates_primary_and_leaf_authority(self) -> None:
        with EFFICIENT.open("rb") as handle:
            instructions = tomllib.load(handle)["developer_instructions"]
        self.assertIn("Mode: Lean Primary", instructions)
        self.assertIn("sole task-context owner and final reviewer", instructions)
        self.assertIn("Mode: Coordinated Leaf", instructions)
        self.assertIn("controller owns the Full-run verdict", instructions)
        self.assertIn("shared with the Host or isolated", instructions)
        self.assertIn("Delivery: VISIBLE_CANDIDATE", instructions)
        self.assertIn("Never serialize, generate, or return forward/reverse patch bodies", instructions)
        self.assertIn("Final file SHA256", instructions)
        self.assertIn("reverse+forward replay it in one transaction", instructions)
        self.assertIn("every exact command, exit status, and exact result/output", instructions)

    def test_primary_avoids_non_falsifying_baseline_and_duplicate_verification(self) -> None:
        with EFFICIENT.open("rb") as handle:
            profile = tomllib.load(handle)
        instructions = profile["developer_instructions"]
        self.assertIn("implement before running a broad passing baseline suite", instructions)
        self.assertIn("one focused post-change behavior command", instructions)
        self.assertIn("one final hygiene/diff audit", instructions)
        self.assertIn("same-version implementation mirror", instructions)
        self.assertIn("After one failed large or blank-line-anchored patch", instructions)
        self.assertIn("rerun the smallest affected slice", instructions)
        self.assertIn("no result-only follow-up is needed", instructions)

        self.assertEqual("gpt-5.6-luna", profile["model"])
        self.assertEqual("max", profile["model_reasoning_effort"])
        self.assertEqual("fast", profile["service_tier"])
        self.assertEqual("low", profile["model_verbosity"])
        self.assertEqual("none", profile["model_reasoning_summary"])
        self.assertEqual(4000, profile["tool_output_token_limit"])
        self.assertEqual("none", profile["personality"])
        self.assertFalse(profile["agents"]["enabled"])
        self.assertTrue(profile["features"]["fast_mode"])

        controller = tomllib.loads(read(CONTROLLER))
        self.assertEqual("gpt-5.6-luna", controller["model"])
        self.assertEqual("max", controller["model_reasoning_effort"])
        self.assertEqual("fast", controller["service_tier"])
        self.assertEqual("low", controller["model_verbosity"])
        self.assertEqual("none", controller["model_reasoning_summary"])
        self.assertEqual(4000, controller["tool_output_token_limit"])
        self.assertEqual("none", controller["personality"])
        self.assertTrue(controller["features"]["fast_mode"])

    def test_every_luna_profile_is_permanently_max_fast(self) -> None:
        luna_profiles = []
        for path in (ROOT / ".codex" / "agents").glob("*.toml"):
            profile = tomllib.loads(read(path))
            if profile["model"] == "gpt-5.6-luna":
                luna_profiles.append(path.name)
                self.assertEqual("max", profile["model_reasoning_effort"], path.name)
                self.assertEqual("fast", profile["service_tier"], path.name)
                self.assertTrue(profile["features"]["fast_mode"], path.name)
        self.assertEqual(["air-controller.toml", "air-efficient-worker.toml"], sorted(luna_profiles))

    def test_skill_contains_no_business_project_terms(self) -> None:
        text = contract() + read(COMPAT / "SKILL.md")
        for forbidden in ("IPZOR", "Buzz", "DeepSeek", "OpenPencil"):
            self.assertNotRegex(text, re.compile(forbidden, re.I))


if __name__ == "__main__":
    unittest.main(verbosity=2)
