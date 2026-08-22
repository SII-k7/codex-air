#!/usr/bin/env python3
"""Evidence-gate contracts for the Codex AIR v1.0 candidate."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit("tests require Python 3.11+ for tomllib") from exc


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / ".agents" / "skills" / "codex-air"
CONTRACT_PATHS = (
    SKILL_ROOT / "SKILL.md",
    SKILL_ROOT / "references" / "orchestration.md",
    SKILL_ROOT / "references" / "runtime-notes.md",
)
AGENTS = {
    "controller": ROOT / ".codex" / "agents" / "air-controller.toml",
    "critical_controller": ROOT / ".codex" / "agents" / "air-critical-controller.toml",
    "complex": ROOT / ".codex" / "agents" / "air-complex-worker.toml",
    "efficient": ROOT / ".codex" / "agents" / "air-efficient-worker.toml",
    "challenger": ROOT / ".codex" / "agents" / "air-challenger.toml",
}
FORWARD_CASES = ROOT / "tests" / "fixtures" / "forward-cases.json"
AB_MANIFEST = ROOT / "tests" / "fixtures" / "v100-ab-benchmark.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def contract_text() -> str:
    return "\n".join(read(path) for path in CONTRACT_PATHS)


class EvidenceGraphContractTests(unittest.TestCase):
    def test_requirement_graph_is_evidence_bound(self) -> None:
        text = contract_text()
        for marker in (
            "done_when:",
            "id: REQ-1",
            "requirements: [REQ-1]",
            "required_evidence",
            "requirements_coverage",
        ):
            self.assertIn(marker, text)
        self.assertIn("every requirement id", text.casefold())
        self.assertIn("final candidate", text)

    def test_worker_packet_and_result_are_complete(self) -> None:
        text = contract_text()
        for marker in (
            "Task ID:",
            "Requirement IDs:",
            "Read scope:",
            "Write scope:",
            "Do not touch:",
            "Passing condition:",
            "Required evidence:",
            "Requirement coverage:",
            "Failure class:",
        ):
            self.assertIn(marker, text)

    def test_artifact_first_review_and_closed_verdict(self) -> None:
        text = " ".join(contract_text().split())
        self.assertIn("Review artifact-first", text)
        self.assertIn("verifies the verifier", text)
        self.assertIn("PASS | FIX | BLOCKED", text)
        self.assertIn("A worker approves only its task", text)
        self.assertIn("Verdict: PASS | REVIEW_REQUIRED | BLOCKED", text)
        self.assertIn("residual_suggestions", text)

    def test_selective_challenge_is_bounded_read_only(self) -> None:
        text = " ".join(contract_text().split())
        self.assertIn("zero challenge calls for ordinary low-risk", text)
        self.assertIn("at most one bounded read-only challenge", text)
        self.assertIn("write_scope: []", text)
        self.assertIn("cannot become a second reviewer", text)

    def test_continuity_has_timebox_resume_and_partial_delivery(self) -> None:
        text = " ".join(contract_text().split()).casefold()
        for marker in (
            "bounded planning timebox",
            "earlier stage",
            "run_id",
            "candidate_identity",
            "attempts",
            "do not redispatch completed tasks",
        ):
            self.assertIn(marker, text)


class RuntimeIdentityContractTests(unittest.TestCase):
    def test_default_profiles_are_exact_and_model_neutral(self) -> None:
        expected = {
            "controller": ("air-controller", "gpt-5.6-luna", "max", "read-only"),
            "critical_controller": ("air-critical-controller", "gpt-5.6-sol", "max", "read-only"),
            "complex": ("air-complex-worker", "gpt-5.6-terra", "max", "workspace-write"),
            "efficient": ("air-efficient-worker", "gpt-5.6-luna", "max", "workspace-write"),
            "challenger": ("air-challenger", "gpt-5.6-sol", "max", "read-only"),
        }
        for role, path in AGENTS.items():
            with path.open("rb") as handle:
                data = tomllib.load(handle)
            name, model, effort, sandbox = expected[role]
            self.assertEqual(name, data["name"])
            self.assertEqual(model, data["model"])
            self.assertEqual(effort, data["model_reasoning_effort"])
            self.assertEqual(sandbox, data["sandbox_mode"])
            self.assertNotIn(model, data["name"])

    def test_single_turn_host_authoritative_proof_fails_closed(self) -> None:
        text = " ".join(contract_text().split())
        for marker in (
            'fork_turns="none"',
            "authoritative Host/tool role mapping",
            "launch record",
            "do not ask the child to self-report",
            "return `BLOCKED`",
        ):
            self.assertIn(marker.casefold(), text.casefold())
        self.assertIn("send the complete packet in the first", text.casefold())
        self.assertIn("never spend an identity-only model turn", text.casefold())

    def test_capability_does_not_widen_authorization(self) -> None:
        text = " ".join(contract_text().split())
        self.assertIn("Keep capability separate from authorization", text)
        self.assertIn("Broader technical access does not widen", text)
        self.assertIn("Authorization boundary", text)
        self.assertIn("record its own baseline before writes", text)

    def test_workers_accept_complete_first_turn_packets_without_handshake(self) -> None:
        for role in ("complex", "efficient"):
            with AGENTS[role].open("rb") as handle:
                instructions = tomllib.load(handle)["developer_instructions"]
            self.assertIn("Do not spend a turn on an identity handshake", instructions)
            self.assertIn("complete", instructions)
            self.assertTrue("first turn" in instructions or "first-turn" in instructions)
            self.assertIn("Do not", instructions)
            self.assertIn("create any subagent", instructions)

    def test_lean_primary_owns_final_review_without_host_duplication(self) -> None:
        text = " ".join(contract_text().split())
        self.assertIn("single-semantic-context invariant", text)
        self.assertIn("Host does not reread file contents", text)
        self.assertIn("deterministic candidate persistence", text)
        self.assertIn("Verdict: PASS | REVIEW_REQUIRED | BLOCKED", text)
        with AGENTS["efficient"].open("rb") as handle:
            instructions = tomllib.load(handle)["developer_instructions"]
        self.assertIn("sole task-context owner and final reviewer", instructions)
        self.assertIn("Host will not repeat", instructions)
        self.assertIn("shared with the Host or isolated", instructions)
        self.assertIn("VISIBLE_CANDIDATE", instructions)
        self.assertIn("Never serialize", instructions)

    def test_coordinated_controller_is_single_read_only_graph_owner(self) -> None:
        with AGENTS["controller"].open("rb") as handle:
            instructions = tomllib.load(handle)["developer_instructions"]
        for marker in (
            "read-only Codex AIR controller",
            "sole graph decision owner",
            "operationally read-only",
            "Review artifact-first",
            "Verify the verifier",
        ):
            self.assertIn(marker, instructions)


class RoutingAndFailureContractTests(unittest.TestCase):
    def test_roles_are_capabilities_not_model_brands(self) -> None:
        text = contract_text()
        self.assertIn("capability roles, not permanent model brands", text)
        self.assertIn("Model replacement", text)
        self.assertIn("Do not rename Codex AIR for a model generation", text)

    def test_native_and_compatibility_share_contract(self) -> None:
        text = " ".join(contract_text().split())
        self.assertIn("Native Nested", text)
        self.assertIn("Compatibility", text)
        self.assertIn("Both modes use the same requirement graph", text)
        self.assertIn(
            "Never claim Native Nested succeeded without both a real nested launch record and a persisted active-workspace candidate",
            text,
        )

    def test_failure_taxonomy_and_retry_are_bounded(self) -> None:
        text = " ".join(contract_text().split())
        allowed = (
            "runtime | timeout | model_identity | permission | dependency | scope | "
            "verification | evidence_quality | conflict | none"
        )
        self.assertIn(allowed, text)
        self.assertIn("at most one focused Correction Packet", text)
        self.assertIn("Do not relaunch an identical packet without new evidence", text)
        self.assertIn("Never transfer an owned file after its logical owner writes it", text)
        self.assertRegex(text, r"one (?:material )?Recovery Re-plan per affected Requirement chain")
        self.assertIn("task renaming does not reset", text.lower())

    def test_forward_fixture_covers_evidence_failures(self) -> None:
        cases = json.loads(read(FORWARD_CASES))
        prompts = "\n".join(case["prompt"] for case in cases)
        self.assertIn("Requirement", prompts)
        self.assertIn("verification", prompts.lower())
        self.assertIn("shared integration file", prompts)
        self.assertIn("times out", prompts.lower())
        self.assertTrue(any(case["expected"].get("challenge") == "required" for case in cases))
        self.assertTrue(any(case["expected"].get("challenge") == "none" for case in cases))

    def test_ab_protocol_is_reproducible_and_claim_free(self) -> None:
        data = json.loads(read(AB_MANIFEST))
        self.assertEqual(1, data["schema_version"])
        self.assertEqual("protocol_only", data["evidence_class"])
        self.assertEqual({"baseline", "candidate"}, {arm["id"] for arm in data["arms"]})
        self.assertGreaterEqual(data["repetitions"], 3)
        self.assertTrue(data["counterbalanced_order"])
        self.assertTrue(data["fresh_isolated_checkout"])
        self.assertTrue(data["hidden_grader_after_run"])
        self.assertNotIn("winner", data)
        self.assertNotIn("results", data)

    def test_validators_cover_v1_evidence_files(self) -> None:
        required = (
            "tests/fixtures/v100-ab-benchmark.json",
            "tests/test_v100_benchmark.py",
            "tests/test_v100_evidence_control.py",
            "tests/v100-live-smoke.md",
            "CODEX_AIR_V1_IMPLEMENTATION_REPORT.md",
        )
        for path in (ROOT / "scripts" / "validate.sh", ROOT / "scripts" / "validate.ps1"):
            text = read(path)
            for marker in required:
                self.assertIn(marker, text, f"{path.name}: {marker}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
