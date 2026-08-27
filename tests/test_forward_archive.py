from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "docs" / "archive" / "testing"
ACTIVE_SKILL = ROOT / ".agents" / "skills" / "codex-air"


class ForwardArchiveTests(unittest.TestCase):
    def test_superseded_forward_assets_are_not_active_test_contracts(self) -> None:
        self.assertFalse((ROOT / "tests" / "forward-tests.md").exists())
        self.assertFalse((ROOT / "tests" / "fixtures" / "forward-cases.json").exists())

        docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8").lower()
        self.assertNotIn("forward-test", docs_index)
        self.assertNotIn("forward-cases", docs_index)

        for validator in (ROOT / "scripts" / "validate.sh", ROOT / "scripts" / "validate.ps1"):
            self.assertNotIn("forward-cases", validator.read_text(encoding="utf-8").lower())

    def test_archive_preserves_and_labels_the_historical_evidence(self) -> None:
        narrative = (ARCHIVE / "2026-08-20-forward-tests.md").read_text(encoding="utf-8")
        archive_index = (ARCHIVE / "README.md").read_text(encoding="utf-8")
        fixture_path = ARCHIVE / "2026-08-20-forward-cases.json"

        self.assertIn("Archived historical test contract", narrative.splitlines()[0])
        self.assertIn("not the current Codex AIR contract", narrative.splitlines()[0])
        self.assertIn("Archive index", archive_index.splitlines()[0])
        root_archive_index = (ROOT / "docs" / "archive" / "README.md").read_text(encoding="utf-8")
        self.assertIn("not a v1.2 routing specification", root_archive_index)

        fixture_bytes = fixture_path.read_bytes()
        self.assertEqual(
            "bf11b82c6ef19d1e6cb8174a9d624f4555b1d43f74d355fe27eddd5bbcdf70ee",
            hashlib.sha256(fixture_bytes).hexdigest(),
        )
        cases = json.loads(fixture_bytes)
        self.assertEqual(43, len(cases))
        self.assertTrue(any(case["expected"].get("controller") == "none" for case in cases))
        self.assertTrue(
            any(str(case["expected"].get("route", "")).startswith("controller_then_") for case in cases)
        )

    def test_current_skill_surface_has_no_superseded_route_markers(self) -> None:
        sources = [
            path.read_text(encoding="utf-8")
            for path in ACTIVE_SKILL.rglob("*")
            if path.is_file() and path.suffix in {".md", ".yaml"}
        ]
        current = "\n".join(sources).lower()
        for marker in ("lean air", "full air", "parallel air", "controller_then_", "lean_efficient"):
            self.assertNotIn(marker, current)


if __name__ == "__main__":
    unittest.main()
