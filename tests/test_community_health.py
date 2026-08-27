#!/usr/bin/env python3
"""Community-health contracts that should remain stable across releases."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class CommunityHealthTests(unittest.TestCase):
    def test_workflows_are_read_only_and_cancel_redundant_runs(self) -> None:
        for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
            workflow = path.read_text(encoding="utf-8")
            self.assertRegex(workflow, r"(?m)^permissions:\n  contents: read$")
            self.assertRegex(
                workflow,
                r"(?m)^concurrency:\n  group: \$\{\{ github\.workflow \}\}-"
                r"\$\{\{ github\.event_name \}\}-"
                r"\$\{\{ github\.event\.pull_request\.number \|\| github\.ref \}\}\n"
                r"  cancel-in-progress: true$",
            )
            self.assertNotRegex(workflow, r"(?m)^\s+[a-z-]+: write$")
            self.assertIn("persist-credentials: false", workflow)

        windows = read(".github/workflows/windows-validation.yml")
        for script in ("scripts/doctor.ps1", "scripts/default.ps1"):
            self.assertEqual(2, windows.count(f'"{script}"'), script)

    def test_bug_form_requests_release_independent_diagnostics(self) -> None:
        form = read(".github/ISSUE_TEMPLATE/bug_report.yml")
        self.assertNotRegex(form, r"placeholder:\s*v\d+\.\d+\.\d+")
        self.assertIn("vX.Y.Z or full commit SHA", form)
        self.assertIn("scripts/doctor.sh --json", form)
        self.assertIn("scripts/doctor.ps1 -Json", form)
        for relative in ("scripts/doctor.sh", "scripts/doctor.ps1"):
            self.assertTrue((ROOT / relative).is_file(), relative)
        self.assertIn("--json)", read("scripts/doctor.sh"))
        self.assertIn("[switch]$Json", read("scripts/doctor.ps1"))
        for marker in ("Command:", "Exit code:", "Relevant output (redacted):"):
            self.assertIn(marker, form)

    def test_contributor_policy_separates_free_scoring_from_paid_runs(self) -> None:
        guide = read("CONTRIBUTING.md")
        for marker in (
            "consume zero Codex credits",
            "do not call a model",
            "explicit maintainer approval",
            "credit cap",
            "good first issue",
            "Terra is not a routing option",
            "only the Sol controller can issue the overall completion verdict",
        ):
            self.assertIn(marker, guide)
        self.assertIn("canonical `README.md` and `README.zh-CN.md`", guide)
        self.assertIn("`README.en.md` as a compatibility pointer", guide)

    def test_support_policy_tracks_channels_instead_of_version_numbers(self) -> None:
        policy = read("SECURITY.md")
        self.assertIn("Latest tagged release", policy)
        self.assertIn("Current `main`", policy)
        self.assertNotRegex(policy, r"`\d+\.\d+\.x`")

        support = read("SUPPORT.md")
        self.assertIn("Do not spend credits on a live benchmark", support)
        self.assertIn("Maintainers will not ask for API keys", support)


if __name__ == "__main__":
    unittest.main(verbosity=2)
