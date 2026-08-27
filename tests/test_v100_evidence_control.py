#!/usr/bin/env python3
"""Historical benchmark integrity plus current evidence-control boundaries."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "tests" / "deepswe-v11-hardest10-results.md"
MANIFEST = ROOT / "tests" / "fixtures" / "v100-ab-benchmark.json"
MICROBENCH = ROOT / "tests" / "deepswe-v11-microbench.md"
PUBLIC_READMES = (ROOT / "README.md", ROOT / "README.zh-CN.md")


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

    def test_readmes_separate_v100_history_invalid_v12_screen_and_unrun_rerun(self) -> None:
        for path in PUBLIC_READMES:
            text = read(path)
            self.assertRegex(text, r"(?i)historical|历史")
            for marker in ("v1.0", "BUDGET_ABORTED", "INVALID", "66.85", "39.7%", "1.198", "170", "3.17"):
                self.assertIn(marker, text, path.name)
            self.assertRegex(text, r"(?i)NOT RUN|未运行")

    def test_v12_screen_is_budget_aborted_invalid_diagnostic_only(self) -> None:
        text = read(MICROBENCH)
        for marker in (
            "66.85 of the 70-credit cap",
            "invalid and unscored",
            "39.7%",
            "1.198",
            "170 tool calls",
            "Short polls and Terra usage were zero",
            "actual Fast tier was unobserved",
            "`BUDGET_ABORTED`",
        ):
            self.assertIn(marker, text)
        self.assertNotIn("The result is `PASS`", text)


class V12EvidenceControlTests(unittest.TestCase):
    def test_final_review_uses_real_artifacts_and_verifier(self) -> None:
        skill = read(ROOT / ".agents" / "skills" / "codex-air" / "SKILL.md")
        normalized = " ".join(skill.casefold().split())
        for marker in (
            "real final files",
            "the complete in-scope diff",
            "Requirement coverage",
            "must verify the verifier",
            "Verdict: PASS | FIX | BLOCKED",
        ):
            self.assertIn(marker.casefold(), normalized)

    def test_worker_pass_cannot_be_overall_pass(self) -> None:
        for name in ("air-efficient-worker.toml", "air-complex-worker.toml"):
            text = read(ROOT / ".codex" / "agents" / name)
            self.assertIn("PASS is only a leaf result", text)
            self.assertIn("VISIBLE_CANDIDATE", text)
            self.assertIn("Final file SHA256", text)

    def test_v12_todo_keeps_low_credit_and_matched_rerun_gates(self) -> None:
        todo = read(ROOT / "TODO.md")
        for marker in (
            "v1.2 low-credit iteration gate",
            "Sol-control / Luna-execution matched rerun",
            "Terra calls and tokens must remain zero",
            "1,800-credit absolute cap",
            "0.85–1.15",
            "55%",
            "70%",
            "1.10×",
        ):
            self.assertIn(marker, todo)

    def test_runtime_matrix_does_not_promote_invalid_or_historical_runs(self) -> None:
        matrix = read(ROOT / "docs" / "release" / "runtime-surface-matrix.md")
        for marker in (
            "BUDGET_ABORTED / INVALID",
            "Candidate files and partial telemetry are diagnostic only",
            "v1.2 DeepSWE hardest-10 matched A/B",
            "NOT RUN",
            "v1.0 DeepSWE hardest-10 matched A/B",
            "RETAINED HISTORICAL",
            "does not establish quality equivalence",
        ):
            self.assertIn(marker, matrix)


if __name__ == "__main__":
    unittest.main(verbosity=2)
