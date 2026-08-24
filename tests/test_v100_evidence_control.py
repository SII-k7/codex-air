#!/usr/bin/env python3
"""Historical benchmark integrity plus v1.1 evidence-control boundaries."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "tests" / "deepswe-v11-hardest10-results.md"
MANIFEST = ROOT / "tests" / "fixtures" / "v100-ab-benchmark.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class HistoricalEvidenceTests(unittest.TestCase):
    def test_v100_protocol_remains_reproducible_and_claim_free(self) -> None:
        data = json.loads(read(MANIFEST))
        self.assertEqual(1, data["schema_version"])
        self.assertEqual("protocol_only", data["evidence_class"])
        self.assertEqual({"baseline", "candidate"}, {arm["id"] for arm in data["arms"]})
        self.assertGreaterEqual(data["repetitions"], 3)
        self.assertTrue(data["counterbalanced_order"])
        self.assertTrue(data["fresh_isolated_checkout"])
        self.assertTrue(data["hidden_grader_after_run"])
        self.assertNotIn("winner", data)

    def test_hardest10_result_keeps_exact_aggregate_values(self) -> None:
        text = read(RESULT)
        for marker in (
            "Direct: 2/10 resolved",
            "AIR: 1/10 resolved",
            "0.8943",
            "0.8932",
            "919.34",
            "358.83",
            "1.267",
        ):
            self.assertIn(marker, text)

    def test_readmes_label_v100_as_historical_and_v11_as_unbenchmarked(self) -> None:
        for name in ("README.md", "README.en.md"):
            text = read(ROOT / name)
            self.assertRegex(text, r"(?i)historical|历史")
            self.assertRegex(text, r"(?i)not yet|尚未")
            self.assertIn("61", text)
            self.assertIn("3.17", text)


class V11EvidenceControlTests(unittest.TestCase):
    def test_final_review_uses_real_artifacts_and_verifier(self) -> None:
        skill = read(ROOT / ".agents" / "skills" / "codex-air" / "SKILL.md")
        for marker in (
            "real final files",
            "complete in-scope diff",
            "Requirement coverage",
            "verify the verifier",
            "Verdict: PASS | FIX | BLOCKED",
        ):
            self.assertIn(marker.casefold(), skill.casefold())

    def test_worker_pass_cannot_be_overall_pass(self) -> None:
        for name in ("air-efficient-worker.toml", "air-complex-worker.toml"):
            text = read(ROOT / ".codex" / "agents" / name)
            self.assertIn("PASS is only a leaf result", text)
            self.assertIn("VISIBLE_CANDIDATE", text)
            self.assertIn("Final file SHA256", text)

    def test_v11_todo_freezes_rerun_quality_cost_and_latency_gates(self) -> None:
        todo = read(ROOT / "TODO.md")
        for marker in (
            "v1.1 Sol-control / Luna-execution matched rerun",
            "Terra calls and tokens must remain zero",
            "1,800-credit absolute cap",
            "0.85–1.15",
            "55%",
            "70%",
            "1.10×",
        ):
            self.assertIn(marker, todo)

    def test_runtime_matrix_does_not_claim_v11_live_proof(self) -> None:
        matrix = read(ROOT / "docs" / "release" / "runtime-surface-matrix.md")
        self.assertIn("Controlled AIR route", matrix)
        self.assertIn("UNVERIFIED", matrix)
        self.assertIn("v1.1 has not been rerun", matrix)


if __name__ == "__main__":
    unittest.main(verbosity=2)
