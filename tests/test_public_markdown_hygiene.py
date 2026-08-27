#!/usr/bin/env python3
"""Privacy and routing-status contracts for public historical Markdown."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_INDEX = ROOT / "docs" / "README.md"
ARCHIVE_ROOT = ROOT / "docs" / "archive"
RUNTIME_MATRIX = ROOT / "docs" / "release" / "runtime-surface-matrix.md"
ROOT_POINTERS = (
    ROOT / "CODEX_AIR_MIGRATION_REPORT.md",
    ROOT / "CODEX_AIR_V1_IMPLEMENTATION_REPORT.md",
)

PRIVATE_MARKERS = (
    re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"/home/[A-Za-z0-9._-]+/"),
    re.compile(r"/data/(?:hdd/)?home/[A-Za-z0-9._-]+/"),
    re.compile(r"/root/[A-Za-z0-9._-]+"),
    re.compile(r"[A-Za-z]:[\\/]Users[\\/][A-Za-z0-9._-]+[\\/]"),
    re.compile(r"/var/folders/[A-Za-z0-9_./-]+"),
    re.compile(r"\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b", re.I),
    re.compile(r"backups/[0-9]{8}T[0-9]{6}Z-[0-9]+"),
    re.compile(r"\b(?:kin3|zhukq|yehyakin)\b", re.I),
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def managed_public_markdown() -> tuple[Path, ...]:
    archive = tuple(sorted(ARCHIVE_ROOT.rglob("*.md")))
    legacy_pointers = tuple(sorted((ROOT / "docs" / "superpowers").rglob("*.md")))
    return (DOCS_INDEX, RUNTIME_MATRIX, *ROOT_POINTERS, *archive, *legacy_pointers)


class PublicMarkdownHygieneTests(unittest.TestCase):
    def test_managed_public_markdown_contains_no_machine_or_session_identity(self) -> None:
        for path in managed_public_markdown():
            self.assertTrue(path.is_file(), path)
            source = read(path)
            for pattern in PRIVATE_MARKERS:
                self.assertIsNone(pattern.search(source), f"{path}: {pattern.pattern}")

    def test_every_archived_record_declares_that_current_routing_does_not_apply(self) -> None:
        for path in sorted(ARCHIVE_ROOT.rglob("*.md")):
            notice = read(path)[:400].lower()
            self.assertTrue(notice.startswith("> **archive"), path)
            self.assertRegex(notice, r"not (?:the )?current (?:codex air contract|routing)")

    def test_legacy_public_paths_are_pointers_not_parallel_routing_contracts(self) -> None:
        pointers = (*ROOT_POINTERS, *sorted((ROOT / "docs" / "superpowers").rglob("*.md")))
        for path in pointers:
            source = read(path)
            self.assertLessEqual(len(source.splitlines()), 12, path)
            self.assertIn("archive", source[:300].lower(), path)
            self.assertRegex(source[:400].lower(), r"not current|not the current|do not define current")

    def test_docs_index_routes_current_and_historical_readers_separately(self) -> None:
        source = read(DOCS_INDEX)
        for target in (
            "../.agents/skills/codex-air/SKILL.md",
            "../.agents/skills/codex-air/references/orchestration.md",
            "../.agents/skills/codex-air/references/runtime-notes.md",
            "archive/README.md",
        ):
            self.assertIn(target, source)
        self.assertIn("Do not infer current model routing", source)

    def test_runtime_matrix_keeps_current_invalid_and_historical_evidence_separate(self) -> None:
        source = read(RUNTIME_MATRIX)
        for marker in (
            "Current v1.2 static contract",
            "BUDGET_ABORTED / INVALID",
            "v1.2 DeepSWE hardest-10 matched A/B",
            "NOT RUN",
            "v1.0 DeepSWE hardest-10 matched A/B",
            "RETAINED HISTORICAL",
            "does not establish quality equivalence",
            "actual Fast response tier remains unobserved",
        ):
            self.assertIn(marker, source)
        for stale_role in ("sol-controller", "terra-high-worker", "luna-max-worker"):
            self.assertNotIn(stale_role, source)
        self.assertNotRegex(source, r"(?i)passed\s+\d+\s+tests")


if __name__ == "__main__":
    unittest.main(verbosity=2)
