#!/usr/bin/env python3
"""The unrun hard benchmark must track the current v1.2 routing contract."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "tests" / "deepswe-v11-ab.md"
FIXTURE = ROOT / "tests" / "fixtures" / "deepswe-v11-ab.json"


class HardBenchmarkProtocolTests(unittest.TestCase):
    def test_fixture_is_prospective_v12_and_not_a_result(self) -> None:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual("FROZEN_NOT_RUN", data["status"])
        self.assertEqual("prospective_protocol_only", data["evidence_class"])
        self.assertEqual("1.2", data["architecture_version"])
        self.assertEqual(113, data["source"]["task_count"])
        self.assertIn("gpt-5.6-sol / xhigh / default", data["arms"]["direct"])
        self.assertIn("one gpt-5.6-sol / xhigh / default semantic controller", data["arms"]["air"])
        self.assertIn("one gpt-5.6-luna / max worker with Fast requested", data["arms"]["air"])
        self.assertIn("same Sol controller", data["arms"]["review"])
        self.assertEqual("zero calls and zero tokens", data["arms"]["terra"])

    def test_human_protocol_contains_no_superseded_route(self) -> None:
        text = DOCUMENT.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        for marker in (
            "Sol / xhigh / Standard",
            "one Luna / max worker with Fast requested by default",
            "same AIR Sol controller",
            "Terra calls/tokens remain zero",
            "actual Fast tier as `unobserved`",
        ):
            self.assertIn(marker, normalized)
        for obsolete in ("Sol / max / Standard", "Lean Luna", "admitted Parallel AIR"):
            self.assertNotIn(obsolete, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
