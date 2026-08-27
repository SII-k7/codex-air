#!/usr/bin/env python3
"""UI metadata and bundled-asset contracts for the canonical Skill."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "codex-air"
METADATA = SKILL / "agents" / "openai.yaml"


class SkillMetadataTests(unittest.TestCase):
    def test_metadata_exposes_local_brand_assets(self) -> None:
        text = METADATA.read_text(encoding="utf-8")
        for marker in (
            'display_name: "Codex AIR"',
            'icon_small: "./assets/icon-small.svg"',
            'icon_large: "./assets/icon-large.svg"',
            'brand_color: "#0F766E"',
            "$codex-air",
            "allow_implicit_invocation: false",
        ):
            self.assertIn(marker, text)

    def test_icons_are_local_accessible_svg_files(self) -> None:
        for name in ("icon-small.svg", "icon-large.svg"):
            path = SKILL / "assets" / name
            self.assertTrue(path.is_file(), name)
            tree = ET.parse(path)
            root = tree.getroot()
            self.assertEqual("{http://www.w3.org/2000/svg}svg", root.tag)
            self.assertEqual("img", root.attrib.get("role"))
            self.assertIsNone(root.attrib.get("href"))
            self.assertLess(path.stat().st_size, 5_000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
