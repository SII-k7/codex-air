#!/usr/bin/env python3
"""Public README contracts for the v1.1 architecture and claims."""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
READMES = (ROOT / "README.md", ROOT / "README.en.md")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class ReadmeContractTests(unittest.TestCase):
    def test_bilingual_readmes_start_with_language_switches(self) -> None:
        for path in READMES:
            self.assertTrue(read(path).startswith("[简体中文](README.md) · [English](README.en.md)"))

    def test_architecture_has_bilingual_signal_parity(self) -> None:
        zh, en = (read(path) for path in READMES)
        for marker in ("Sol", "xhigh", "Luna Max Fast", "Terra", "fork_turns", "REQ-ID", "REPLAN_NEEDED"):
            self.assertIn(marker, zh)
            self.assertIn(marker, en)
        self.assertIn("Terra 不参与任何 AIR 路由", zh)
        self.assertIn("Terra appears in no AIR route", en)

    def test_role_tables_publish_exact_models_efforts_and_tiers(self) -> None:
        for path in READMES:
            text = read(path)
            self.assertRegex(text, r"air-controller.*Sol\s*/\s*xhigh\s*/\s*Standard")
            self.assertRegex(text, r"air-critical-controller.*Sol\s*/\s*xhigh\s*/\s*Standard")
            self.assertRegex(text, r"air-efficient-worker.*Luna\s*/\s*max\s*/\s*Fast")
            self.assertRegex(text, r"air-complex-worker.*Luna\s*/\s*max\s*/\s*Fast")
            self.assertRegex(text, r"air-challenger.*Sol\s*/\s*xhigh\s*/\s*Standard")

    def test_projection_uses_luna_fast_not_standard_weight(self) -> None:
        expected = ("0.125", "62.0%", "67.0%", "49.3%", "56.3%", "37.5%", "44.5%")
        for path in READMES:
            text = read(path)
            for marker in expected:
                self.assertIn(marker, text, path.name)
            self.assertIn("scenario_model_projection", text)

    def test_projection_math_is_reproducible(self) -> None:
        scenarios = (
            (0.20, 0.80, 0.03, 0.08, 0.62, 0.67),
            (0.30, 0.70, 0.05, 0.12, 0.4925, 0.5625),
            (0.40, 0.60, 0.08, 0.15, 0.375, 0.445),
        )
        for sol, luna, low, high, saving_low, saving_high in scenarios:
            self.assertAlmostEqual(saving_low, 1 - (sol + luna * 0.125 + high))
            self.assertAlmostEqual(saving_high, 1 - (sol + luna * 0.125 + low))

    def test_rate_tables_publish_sol_and_luna_fast(self) -> None:
        for path in READMES:
            text = read(path)
            for row in (
                "$4.00 | $0.40 | $20.00",
                "$0.20 | $0.02 | $1.20",
                "$0.40 | $0.04 | $2.40",
                "100 | 10 | 500",
                "5 | 0.5 | 30",
                "12.5 | 1.25 | 75",
            ):
                self.assertIn(row, text, path.name)

    def test_readmes_separate_historical_measurement_from_v11_projection(self) -> None:
        for path in READMES:
            text = read(path)
            self.assertIn("0.8943", text)
            self.assertIn("0.8932", text)
            self.assertIn("919.34", text)
            self.assertIn("358.83", text)
            self.assertIn("3.17", text)
            self.assertRegex(text, r"(?i)historical|历史")
            self.assertRegex(text, r"(?i)not yet|尚未")
            self.assertRegex(text, r"(?i)not.*guarantee|不是.*保证")

    def test_api_dollars_and_credits_are_distinguished(self) -> None:
        for path in READMES:
            text = read(path)
            self.assertRegex(text, r"(?i)API.*(?:dollar|美元).*(?:credits|计费单位)")
            self.assertIn("actual", text if path.name.endswith(".en.md") else text.replace("真实", "actual"))

    def test_release_and_current_status_are_v1_1_2(self) -> None:
        for path in READMES:
            text = read(path)
            self.assertIn("v1.1.2", text)
            self.assertIn("releases/tag/v1.1.2", text)

    def test_quickstarts_cover_posix_and_windows(self) -> None:
        for path in READMES:
            text = read(path)
            for marker in ("scripts/validate.sh", "scripts/install.sh", "scripts/doctor.sh", "scripts/validate.ps1", "scripts/install.ps1"):
                self.assertIn(marker, text)

    def test_first_run_guidance_precedes_architecture_and_benchmark(self) -> None:
        zh, en = (read(path) for path in READMES)
        self.assertLess(zh.index("## 适合你吗"), zh.index("## 为什么是这个架构"))
        self.assertLess(zh.index("## 60 秒开始"), zh.index("## 为什么是这个架构"))
        self.assertLess(en.index("## Is AIR for you?"), en.index("## Why this architecture"))
        self.assertLess(en.index("## 60-second quickstart"), en.index("## Why this architecture"))
        for text in (zh, en):
            self.assertIn("docs/prompt-recipes.md", text)
            self.assertIn("CHANGELOG.md", text)

    def test_community_surface_has_no_stale_public_identity(self) -> None:
        paths = (
            ROOT / "CONTRIBUTING.md",
            ROOT / "SUPPORT.md",
            ROOT / "SECURITY.md",
            ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml",
            ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml",
        )
        for path in paths:
            text = read(path)
            self.assertNotIn("Codex Codex AIR", text, path.name)
            self.assertNotIn("v0.4.1", text, path.name)
        self.assertIn("1.1.x", read(ROOT / "SECURITY.md"))
        self.assertIn("discussions", read(ROOT / "SUPPORT.md").lower())

    def test_documentation_limitations_and_license_exist(self) -> None:
        for path in READMES:
            text = read(path)
            for marker in ("docs/release/runtime-surface-matrix.md", "CONTRIBUTING.md", "SECURITY.md", "Apache License 2.0"):
                self.assertIn(marker, text)
            self.assertRegex(text, r"(?m)^## (?:限制|Limitations)$")

    def test_all_relative_markdown_links_resolve(self) -> None:
        link_pattern = re.compile(r"\]\((<[^>]+>|[^)\s]+)")
        for path in READMES:
            for match in link_pattern.finditer(read(path)):
                target = match.group(1).strip("<>")
                if target.startswith(("#", "http://", "https://", "mailto:")):
                    continue
                relative = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if relative:
                    self.assertTrue((path.parent / relative).exists(), f"{path.name}: {relative}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
