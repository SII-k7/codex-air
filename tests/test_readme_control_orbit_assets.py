#!/usr/bin/env python3
"""Structural and architecture checks for localized README SVG assets."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "docs" / "assets" / "readme"
ASSETS = (
    ASSET_ROOT / "hero-zh.svg",
    ASSET_ROOT / "hero-en.svg",
    ASSET_ROOT / "control-plane-zh.svg",
    ASSET_ROOT / "control-plane-en.svg",
)


class ControlOrbitAssetContractTests(unittest.TestCase):
    def test_assets_are_well_formed_accessible_and_local(self) -> None:
        for path in ASSETS:
            root = ET.parse(path).getroot()
            self.assertTrue(root.tag.endswith("svg"), path.name)
            children = list(root)
            self.assertTrue(any(child.tag.endswith("title") and (child.text or "").strip() for child in children), path.name)
            self.assertTrue(any(child.tag.endswith("desc") and (child.text or "").strip() for child in children), path.name)
            source = path.read_text(encoding="utf-8")
            self.assertNotRegex(source, r"(?:href|src)=[\"']https?://", path.name)
            self.assertNotIn("<image", source, path.name)

    def test_assets_describe_sol_control_and_luna_execution(self) -> None:
        for path in ASSETS:
            source = path.read_text(encoding="utf-8")
            self.assertIn("Sol", source, path.name)
            self.assertIn("Luna", source, path.name)
            self.assertNotIn("Luna Primary", source, path.name)
            self.assertNotIn("LEAN PRIMARY", source, path.name)

    def test_orbit_paths_return_to_the_single_controller(self) -> None:
        for path in ASSETS:
            root = ET.parse(path).getroot()
            ids = {element.attrib.get("id") for element in root.iter()}
            self.assertIn("air-controller", ids, path.name)
            task_paths = [element for element in root.iter() if element.attrib.get("data-flow") == "task"]
            evidence_paths = [element for element in root.iter() if element.attrib.get("data-flow") == "evidence"]
            self.assertEqual(3, len(task_paths), path.name)
            self.assertEqual(3, len(evidence_paths), path.name)
            for element in task_paths:
                self.assertEqual("air-controller", element.attrib.get("data-from"), path.name)
                self.assertTrue(element.attrib.get("data-to", "").startswith("efficient-worker-"), path.name)
            for element in evidence_paths:
                self.assertTrue(element.attrib.get("data-from", "").startswith("efficient-worker-"), path.name)
                self.assertEqual("air-controller", element.attrib.get("data-to"), path.name)

    def test_chinese_and_english_assets_share_geometry(self) -> None:
        for left, right in ((ASSETS[0], ASSETS[1]), (ASSETS[2], ASSETS[3])):
            left_root = ET.parse(left).getroot()
            right_root = ET.parse(right).getroot()
            self.assertEqual(left_root.attrib.get("viewBox"), right_root.attrib.get("viewBox"))
            self.assertEqual(len(list(left_root.iter())), len(list(right_root.iter())))


if __name__ == "__main__":
    unittest.main(verbosity=2)
