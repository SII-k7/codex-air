#!/usr/bin/env python3
"""Codex AIR identity and compatibility-migration contracts."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / ".agents" / "skills" / "codex-air"
COMPAT = ROOT / ".agents" / "skills" / "codex-prove"
REPOSITORY = "https://github.com/SII-k7/codex-air"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class RenameMigrationContractTests(unittest.TestCase):
    def test_codex_air_is_the_only_full_skill(self) -> None:
        skill = read(CANONICAL / "SKILL.md")
        metadata = read(CANONICAL / "agents" / "openai.yaml")
        alias = read(COMPAT / "SKILL.md")

        self.assertIn("name: codex-air", skill)
        self.assertIn("# Codex AIR", skill)
        self.assertIn("Adaptive Intelligence Routing", skill)
        self.assertIn('display_name: "Codex AIR"', metadata)
        self.assertIn("$codex-air", metadata)
        self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertLess(len(alias.splitlines()), 30)
        self.assertIn("$codex-prove", alias)
        self.assertIn("$codex-air", alias)
        self.assertNotIn("## Plan", alias)

    def test_role_names_are_model_neutral(self) -> None:
        for name in (
            "air-controller.toml",
            "air-critical-controller.toml",
            "air-complex-worker.toml",
            "air-efficient-worker.toml",
            "air-challenger.toml",
        ):
            self.assertTrue((ROOT / ".codex" / "agents" / name).is_file(), name)
        active_names = {path.name for path in (ROOT / ".codex" / "agents").glob("*.toml")}
        self.assertNotIn("prove-controller.toml", active_names)
        self.assertNotIn("sol-controller.toml", active_names)
        self.assertNotIn("terra-high-worker.toml", active_names)
        self.assertNotIn("luna-max-worker.toml", active_names)

    def test_public_readmes_publish_identity_and_compatibility_window(self) -> None:
        release_tag = f"v{read(ROOT / 'VERSION').strip()}"
        for relative in ("README.md", "README.zh-CN.md"):
            text = read(ROOT / relative)
            self.assertIn(REPOSITORY, text, relative)
            self.assertIn(release_tag, text, relative)
            self.assertIn(f"releases/tag/{release_tag}", text, relative)
            self.assertIn("docs/release/runtime-surface-matrix.md", text, relative)
            self.assertIn("$codex-prove", text, relative)
            self.assertIn("$codex-air", text, relative)
            self.assertNotIn("github.com/yehyakin", text, relative)
            self.assertNotIn("github.com/SII-k7/codex-prove", text, relative)

        compatibility = read(ROOT / "README.en.md")
        self.assertIn("[Canonical English README](README.md)", compatibility)
        self.assertIn("[简体中文](README.zh-CN.md)", compatibility)
        self.assertIn(release_tag, compatibility)
        self.assertNotIn("github.com/yehyakin", compatibility)
        self.assertNotIn("github.com/SII-k7/codex-prove", compatibility)

    def test_installers_use_v1_state_and_preserve_old_state_migration(self) -> None:
        for relative in (
            "scripts/install.sh",
            "scripts/uninstall.sh",
            "scripts/install.ps1",
            "scripts/uninstall.ps1",
        ):
            text = read(ROOT / relative)
            self.assertIn("codex-prove", text, relative)
            self.assertIn("sol-control", text, relative)
            self.assertIn("codex-air", text, relative)
            self.assertIn("sol-luna", text, relative)
            self.assertIn("orchestrate-sol-luna", text, relative)
            self.assertIn("air-controller", text, relative)
            self.assertIn("air-critical-controller", text, relative)
            self.assertIn("air-challenger", text, relative)

    def test_custom_agent_launch_contract_requires_fresh_context(self) -> None:
        surfaces = (
            CANONICAL / "SKILL.md",
            CANONICAL / "references" / "orchestration.md",
            CANONICAL / "references" / "runtime-notes.md",
        )
        for surface in surfaces:
            text = read(surface)
            self.assertIn('fork_turns="none"', text, surface)
            self.assertIn("identity", text.lower(), surface)
            self.assertIn("launch", text.lower(), surface)
            self.assertIn("BLOCKED", text, surface)


if __name__ == "__main__":
    unittest.main(verbosity=2)
