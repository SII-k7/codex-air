#!/usr/bin/env python3
"""Adoption-entry contracts for the v1.2 public READMEs."""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "README.md"
CHINESE = ROOT / "README.zh-CN.md"
COMPATIBILITY = ROOT / "README.en.md"
PUBLIC_READMES = (CANONICAL, CHINESE)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class ReadmeContractTests(unittest.TestCase):
    def test_english_is_canonical_chinese_is_localized_and_old_english_redirects(self) -> None:
        switch = "[English](README.md) · [简体中文](README.zh-CN.md)"
        self.assertTrue(read(CANONICAL).startswith(switch))
        self.assertTrue(read(CHINESE).startswith(switch))

        compatibility = read(COMPATIBILITY)
        self.assertTrue(compatibility.startswith("[Canonical English README](README.md)"))
        self.assertIn("# English README moved", compatibility)
        self.assertIn("existing `README.en.md` links continue to work", compatibility)
        self.assertLessEqual(len(compatibility.splitlines()), 12)

    def test_architecture_has_bilingual_signal_parity(self) -> None:
        english, chinese = (read(path) for path in PUBLIC_READMES)
        for marker in (
            "Sol",
            "xhigh",
            "Luna",
            "max",
            "Fast",
            "Terra",
            'fork_turns="none"',
            "REPLAN_NEEDED",
            "BLOCKED",
            "$codex-air",
            "$codex-prove",
        ):
            self.assertIn(marker, english)
            self.assertIn(marker, chinese)
        self.assertIn("Terra has no AIR role", english)
        self.assertIn("Terra 不参与 AIR", chinese)

    def test_role_tables_publish_exact_models_efforts_and_requested_tiers(self) -> None:
        for path in PUBLIC_READMES:
            text = read(path)
            self.assertRegex(text, r"air-controller.*Sol / xhigh / Standard")
            self.assertRegex(text, r"air-critical-controller.*Sol / xhigh / Standard")
            self.assertRegex(text, r"air-efficient-worker.*Luna / max / Fast")
            self.assertRegex(text, r"air-complex-worker.*Luna / max / Fast")
            self.assertRegex(text, r"air-challenger.*Sol / xhigh / Standard")
            self.assertIn("unobserved", text)

    def test_stable_install_is_tag_pinned_and_cross_platform(self) -> None:
        for path in PUBLIC_READMES:
            text = read(path)
            self.assertIn("--branch v1.2.0 --depth 1", text)
            self.assertIn("releases/tag/v1.2.0", text)
            for marker in (
                "scripts/validate.sh",
                "scripts/install.sh --check",
                "scripts/doctor.sh --require-codex",
                "scripts/validate.ps1",
                "scripts/install.ps1 -Check",
                "scripts/doctor.ps1 -RequireCodex",
            ):
                self.assertIn(marker, text, path.name)
            self.assertRegex(text, r"(?i)development|开发")
            self.assertIn("`main`", text)

    def test_first_run_guidance_precedes_runtime_and_evidence(self) -> None:
        english = read(CANONICAL)
        chinese = read(CHINESE)
        self.assertLess(english.index("## First task"), english.index("## Runtime contract"))
        self.assertLess(english.index("## Runtime contract"), english.index("## Evidence"))
        self.assertLess(chinese.index("## 第一个任务"), chinese.index("## 运行契约"))
        self.assertLess(chinese.index("## 运行契约"), chinese.index("## 不使用营销缩写的证据台账"))

    def test_evidence_ledger_separates_history_invalid_diagnostic_and_unrun_rerun(self) -> None:
        for path in PUBLIC_READMES:
            text = read(path)
            for marker in (
                "v1.0",
                "0.8943",
                "0.8932",
                "919.34",
                "358.83",
                "3.17×",
                "BUDGET_ABORTED / INVALID",
                "66.85",
                "39.7%",
                "1.198",
                "170",
                "hardest-10",
            ):
                self.assertIn(marker, text, path.name)

        english = read(CANONICAL)
        chinese = read(CHINESE)
        self.assertIn("NOT RUN", english)
        self.assertIn("do **not** establish statistical non-inferiority", english)
        self.assertIn("does not promise", " ".join(english.split()))
        self.assertIn("未运行", chinese)
        self.assertIn("不能建立统计非劣性", chinese)
        self.assertIn("不承诺", chinese)

    def test_readmes_link_to_adopter_guides_and_evidence(self) -> None:
        expected = (
            "docs/getting-started",
            "docs/troubleshooting",
            "docs/examples/first-air-task",
            "docs/evidence/README",
            "tests/deepswe-v11-hardest10-results.md",
            "tests/deepswe-v11-microbench.md",
            "CONTRIBUTING.md",
            "SUPPORT.md",
            "SECURITY.md",
            "NOTICE",
            "CHANGELOG.md",
        )
        for path in PUBLIC_READMES:
            text = read(path)
            for marker in expected:
                self.assertIn(marker, text, path.name)

    def test_root_readmes_do_not_publish_projection_tables_as_results(self) -> None:
        forbidden = (
            "scenario_model_projection",
            "62.0%",
            "67.0%",
            "49.3%",
            "56.3%",
            "37.5%",
            "44.5%",
            "≤55%",
            "$4.00 | $0.40 | $20.00",
        )
        for path in PUBLIC_READMES:
            text = read(path)
            for marker in forbidden:
                self.assertNotIn(marker, text, path.name)

    def test_compatibility_redirect_contains_no_parallel_contract_or_evidence_table(self) -> None:
        compatibility = read(COMPATIBILITY)
        for marker in ("Runtime contract", "BUDGET_ABORTED", "66.85", "air-controller", "scenario_model_projection"):
            self.assertNotIn(marker, compatibility)

    def test_all_relative_markdown_links_resolve(self) -> None:
        link_pattern = re.compile(r"\]\((<[^>]+>|[^)\s]+)")
        for path in (*PUBLIC_READMES, COMPATIBILITY):
            for match in link_pattern.finditer(read(path)):
                target = match.group(1).strip("<>")
                if target.startswith(("#", "http://", "https://", "mailto:")):
                    continue
                relative = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if relative:
                    self.assertTrue((path.parent / relative).exists(), f"{path.name}: {relative}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
