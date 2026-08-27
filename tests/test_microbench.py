#!/usr/bin/env python3
"""Low-credit staged microbenchmark contract and decision tests."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "microbench.py"
MANIFEST = ROOT / "tests" / "fixtures" / "microbench-v1.json"
ABORTED_SCREEN = ROOT / "tests" / "fixtures" / "microbench-screen-20260827.json"


def load_module():
    spec = importlib.util.spec_from_file_location("microbench", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load microbench.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MicrobenchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.manifest = cls.module.validate_manifest(json.loads(MANIFEST.read_text(encoding="utf-8")))
        cls.manifest_hash = cls.module.sha256(cls.manifest)

    def candidate(self, task_ids: list[str], *, historical_air: bool = False) -> dict:
        tasks = {task["id"]: task for task in self.manifest["tasks"]}
        cells = []
        for task_id in task_ids:
            task = tasks[task_id]
            source = task["historical_air"] if historical_air else task["historical_direct"]
            usage = {
                "gpt-5.6-sol": {
                    "sessions": 1,
                    "input_tokens": 100_000,
                    "cached_input_tokens": 90_000,
                    "output_tokens": 2_000,
                },
                "gpt-5.6-luna": {
                    "sessions": 1,
                    "input_tokens": 900_000,
                    "cached_input_tokens": 810_000,
                    "output_tokens": 18_000,
                },
            }
            for model, bucket in usage.items():
                bucket["pro_credits"] = self.module.priced_credits(self.manifest, model, bucket)
            credits = sum(bucket["pro_credits"] for bucket in usage.values())
            cells.append(
                {
                    "task_id": task_id,
                    "resolved": source["resolved"],
                    "partial": source["partial"],
                    "elapsed_seconds": source["elapsed_seconds"] * (1.05 if not historical_air else 1.0),
                    "pro_credits": credits,
                    "input_tokens": 1_000_000,
                    "cached_input_tokens": 900_000,
                    "output_tokens": 20_000,
                    "tool_calls": source.get("tool_calls", 40),
                    "short_polls": 0 if not historical_air else source.get("short_polls", 0),
                    "correction_count": 0,
                    "runtime": {
                        "worker_profile": "air-efficient-worker" if task["stage"] == "screen" else "air-complex-worker",
                        "controller_sessions": 1,
                        "worker_sessions": 1,
                        "challenger_sessions": 0,
                        "worker_actual_tier": "priority",
                        "terra_calls": 0,
                        "terra_tokens": 0,
                    },
                    "usage_by_model": usage,
                    "base_commit": task["base_commit"],
                    "image_digest": task["image_digest"],
                    "instruction_sha256": task["instruction_sha256"],
                    "tests_tree_sha256": task["tests_tree_sha256"],
                    "valid": True,
                }
            )
        return {
            "schema_version": 1,
            "evidence_class": "measured_candidate_cells",
            "manifest_sha256": self.manifest_hash,
            "candidate": {
                "repo_commit": "a" * 40,
                "skill_sha256": "b" * 64,
                "agent_bundle_sha256": "c" * 64,
                "codex_cli": "0.149.0",
                "runtime_contract": {
                    "controller_model": "gpt-5.6-sol",
                    "controller_effort": "xhigh",
                    "controller_requested_tier": "default",
                    "worker_model": "gpt-5.6-luna",
                    "worker_effort": "max",
                    "worker_requested_tier": "fast",
                    "fast_mode": True,
                    "terra_allowed": False,
                },
            },
            "cells": cells,
        }

    def test_manifest_freezes_four_discriminating_tasks_and_small_budget(self) -> None:
        self.assertEqual(4, len(self.manifest["tasks"]))
        self.assertEqual({"python", "go", "typescript"}, {task["language"] for task in self.manifest["tasks"]})
        self.assertLessEqual(self.manifest["budget"]["cumulative_credit_hard_cap"], 220)
        self.assertEqual(0.7, self.manifest["stages"][0]["gates"]["min_luna_token_share"])
        signals = " ".join(task["signal"] for task in self.manifest["tasks"])
        for marker in ("efficiency", "partial regression", "strict-resolution", "tool-loop"):
            self.assertIn(marker, signals)

    def test_no_results_starts_with_screen_only(self) -> None:
        decision = self.module.evaluate(self.manifest, self.candidate([]))
        self.assertEqual("CONTINUE", decision["decision"])
        self.assertEqual("screen", decision["next_stage"])
        self.assertEqual(
            ["sqlfmt-create-table-ddl-formatting", "termenv-preserve-ansi-resets"],
            decision["next_task_ids"],
        )

    def test_historical_air_stops_at_screen_quality_gate(self) -> None:
        screen = self.manifest["stages"][0]["task_ids"]
        decision = self.module.evaluate(self.manifest, self.candidate(screen, historical_air=True))
        self.assertEqual("STOP", decision["decision"])
        self.assertIsNone(decision["next_stage"])
        failed = set(decision["stage_results"]["screen"]["failed_gates"])
        self.assertIn("mean_partial_delta", failed)
        self.assertIn("min_task_partial_delta", failed)

    def test_confirmation_cells_cannot_bypass_screen_admission(self) -> None:
        confirm = self.manifest["stages"][1]["task_ids"]
        with self.assertRaisesRegex(self.module.ContractError, "out-of-order"):
            self.module.evaluate(self.manifest, self.candidate(confirm))

        all_tasks = [task["id"] for task in self.manifest["tasks"]]
        with self.assertRaisesRegex(self.module.ContractError, "later-stage"):
            self.module.evaluate(self.manifest, self.candidate(all_tasks, historical_air=True))

    def test_passing_screen_unlocks_confirmation_and_full_pass(self) -> None:
        screen = self.manifest["stages"][0]["task_ids"]
        screen_decision = self.module.evaluate(self.manifest, self.candidate(screen))
        self.assertEqual("CONTINUE", screen_decision["decision"])
        self.assertEqual("confirm", screen_decision["next_stage"])

        all_tasks = [task["id"] for task in self.manifest["tasks"]]
        final_decision = self.module.evaluate(self.manifest, self.candidate(all_tasks))
        self.assertEqual("PASS", final_decision["decision"])
        self.assertIsNone(final_decision["next_stage"])
        self.assertEqual([], final_decision["stage_results"]["confirm"]["failed_gates"])

    def test_provenance_mismatch_fails_closed(self) -> None:
        result = self.candidate(["sqlfmt-create-table-ddl-formatting"])
        result["cells"][0]["base_commit"] = "0" * 40
        with self.assertRaisesRegex(self.module.ContractError, "base_commit"):
            self.module.evaluate(self.manifest, result)

    def test_invalid_or_duplicate_cells_fail_closed(self) -> None:
        result = self.candidate(["sqlfmt-create-table-ddl-formatting"])
        result["cells"].append(dict(result["cells"][0]))
        with self.assertRaisesRegex(self.module.ContractError, "duplicate"):
            self.module.evaluate(self.manifest, result)

        result = self.candidate(["sqlfmt-create-table-ddl-formatting"])
        result["cells"][0]["elapsed_seconds"] = float("inf")
        with self.assertRaisesRegex(self.module.ContractError, "elapsed_seconds"):
            self.module.evaluate(self.manifest, result)

    def test_model_tier_terra_and_usage_proof_fail_closed(self) -> None:
        result = self.candidate(["sqlfmt-create-table-ddl-formatting"])
        result["candidate"]["runtime_contract"]["worker_effort"] = "high"
        with self.assertRaisesRegex(self.module.ContractError, "worker_effort"):
            self.module.evaluate(self.manifest, result)

        result = self.candidate(["sqlfmt-create-table-ddl-formatting"])
        result["cells"][0]["runtime"]["terra_calls"] = 1
        with self.assertRaisesRegex(self.module.ContractError, "Terra"):
            self.module.evaluate(self.manifest, result)

        result = self.candidate(["sqlfmt-create-table-ddl-formatting"])
        result["cells"][0]["input_tokens"] -= 1
        with self.assertRaisesRegex(self.module.ContractError, "input_tokens total"):
            self.module.evaluate(self.manifest, result)

    def test_unobserved_fast_tier_is_reported_as_a_warning(self) -> None:
        screen = self.manifest["stages"][0]["task_ids"]
        result = self.candidate(screen)
        result["cells"][0]["runtime"]["worker_actual_tier"] = "unobserved"
        decision = self.module.evaluate(self.manifest, result)
        self.assertIn("unobserved_fast_tier", decision["warnings"])

    def test_published_screen_is_explicitly_invalid_and_recomputable(self) -> None:
        evidence = json.loads(ABORTED_SCREEN.read_text(encoding="utf-8"))
        self.assertEqual("budget_aborted_diagnostic", evidence["evidence_class"])
        self.assertEqual("BUDGET_ABORTED", evidence["status"])
        self.assertFalse(evidence["budget"]["confirm_stage_launched"])
        self.assertTrue(all(cell["valid"] is False for cell in evidence["cells"]))
        self.assertTrue(all(cell["agent_exit_code"] == -2 for cell in evidence["cells"]))
        self.assertTrue(all(not cell["sol_final_review"] for cell in evidence["cells"]))
        self.assertEqual(0, evidence["candidate"]["terra_calls"])
        self.assertEqual(0, evidence["candidate"]["terra_tokens"])

        cells = evidence["cells"]
        direct = sum(cell["historical_direct"]["pro_credits"] for cell in cells)
        candidate = sum(cell["pro_credits"] for cell in cells)
        luna_tokens = sum(
            cell["usage_by_model"]["gpt-5.6-luna"]["input_tokens"]
            + cell["usage_by_model"]["gpt-5.6-luna"]["output_tokens"]
            for cell in cells
        )
        all_tokens = sum(
            bucket["input_tokens"] + bucket["output_tokens"]
            for cell in cells
            for bucket in cell["usage_by_model"].values()
        )
        aggregate = evidence["aggregate_diagnostic"]
        self.assertAlmostEqual(candidate, evidence["budget"]["credits_at_stop"])
        self.assertAlmostEqual(candidate / direct, aggregate["cost_ratio"])
        self.assertAlmostEqual(luna_tokens / all_tokens, aggregate["luna_token_share"])
        self.assertEqual(sum(cell["tool_calls"] for cell in cells), aggregate["tool_calls"])
        self.assertIn("valid_terminal_completion", aggregate["failed_conditions"])
        self.assertIn("median_time_ratio", aggregate["failed_conditions"])
        self.assertIn("tool_calls", aggregate["failed_conditions"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
