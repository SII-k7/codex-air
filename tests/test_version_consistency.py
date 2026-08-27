#!/usr/bin/env python3
"""Release-version consistency across public and packaging surfaces."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/SII-k7/codex-air"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class VersionConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.version = read("VERSION").strip()

    def test_version_is_semver_and_heads_the_changelog(self) -> None:
        self.assertRegex(self.version, r"^[0-9]+\.[0-9]+\.[0-9]+$")
        changelog = read("CHANGELOG.md")
        first_release = re.search(r"(?m)^## \[([^]]+)\] - ", changelog)
        self.assertIsNotNone(first_release)
        self.assertEqual(self.version, first_release.group(1))
        self.assertIn(
            f"[{self.version}]: {REPOSITORY}/releases/tag/v{self.version}",
            changelog,
        )

    def test_canonical_readmes_and_compatibility_pointer_use_current_tag(self) -> None:
        tag = f"v{self.version}"
        release_url = f"{REPOSITORY}/releases/tag/{tag}"
        for relative in ("README.md", "README.zh-CN.md", "README.en.md"):
            text = read(relative)
            self.assertIn(tag, text, relative)
            self.assertIn(release_url, text, relative)

    def test_community_surfaces_do_not_freeze_a_supported_release_line(self) -> None:
        security = read("SECURITY.md")
        self.assertIn("Latest tagged release", security)
        self.assertIn("Current `main`", security)
        self.assertNotRegex(security, r"`[0-9]+\.[0-9]+\.x`")

        bug_form = read(".github/ISSUE_TEMPLATE/bug_report.yml")
        self.assertIn("vX.Y.Z or full commit SHA", bug_form)
        self.assertNotRegex(bug_form, r"placeholder:\s*v[0-9]+\.[0-9]+\.[0-9]+")


if __name__ == "__main__":
    unittest.main(verbosity=2)
