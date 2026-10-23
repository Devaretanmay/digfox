"""Tests for Fox Explore skill metadata, instruction contracts, and evaluation scenarios.

Distinguishes deterministic metadata/contract checks from simulated behavior evaluations.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import install  # noqa: E402

SKILL_DIR = ROOT / "skills/fox-explore"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES_DIR = SKILL_DIR / "references"


class FoxExploreMetadataAndIntegrityTests(unittest.TestCase):
    """Verify metadata, concise word count, and reference integrity for Fox Explore."""

    def test_frontmatter_and_version(self):
        self.assertTrue(SKILL_MD.is_file(), f"Missing SKILL.md at {SKILL_MD}")
        content = SKILL_MD.read_text(encoding="utf-8")

        self.assertTrue(content.startswith("---\n"), "SKILL.md must begin with YAML frontmatter")
        parts = content.split("---\n", 2)
        self.assertGreaterEqual(len(parts), 3, "Frontmatter must be enclosed in '---'")

        frontmatter = parts[1]
        self.assertIn("name: fox-explore", frontmatter)
        self.assertIn("description:", frontmatter)
        self.assertIn('version: "0.2.0"', frontmatter)
        self.assertIn("license: MIT", frontmatter)

    def test_concise_word_count_under_500_words(self):
        """SKILL.md must be concise, under 500 words excluding YAML frontmatter."""
        content = SKILL_MD.read_text(encoding="utf-8")
        parts = content.split("---\n", 2)
        body = parts[2].strip()

        word_count = len(body.split())
        self.assertLessEqual(
            word_count,
            500,
            f"Fox Explore SKILL.md body has {word_count} words; must be <= 500 words for agent focus",
        )
        self.assertGreaterEqual(
            word_count,
            250,
            f"Fox Explore SKILL.md body has {word_count} words; expected >= 250 words",
        )

    def test_references_and_links_resolve(self):
        """All markdown links in SKILL.md must resolve to existing files."""
        content = SKILL_MD.read_text(encoding="utf-8")
        links = re.findall(r"\[.*?\]\((references/[^\)]+)\)", content)
        self.assertGreaterEqual(len(links), 1, "Expected at least 1 reference link in SKILL.md")

        for rel_link in links:
            target = SKILL_DIR / rel_link
            self.assertTrue(target.is_file(), f"Referenced file does not exist: {target}")

    def test_zero_extraneous_scripts_or_databases(self):
        """Fox Explore must remain a pure instruction skill with no custom Python scripts, databases, or daemons."""
        scripts_dir = SKILL_DIR / "scripts"
        self.assertFalse(
            scripts_dir.exists(),
            "Fox Explore must not bundle Python scripts; it relies on host tools and existing environment",
        )


class FoxExploreInstructionContractTests(unittest.TestCase):
    """Instruction contract tests verifying that SKILL.md explicitly instructs agents on explore behaviors."""

    @classmethod
    def setUpClass(cls):
        cls.content = SKILL_MD.read_text(encoding="utf-8")

    def test_instructs_four_workflow_stages(self):
        # 1. Scope
        self.assertRegex(self.content, r"## 1\.\s+Scope")
        # 2. Map
        self.assertRegex(self.content, r"## 2\.\s+Map")
        # 3. Compare
        self.assertRegex(self.content, r"## 3\.\s+Compare")
        # 4. Report
        self.assertRegex(self.content, r"## 4\.\s+Report")

    def test_instructs_read_only_by_default(self):
        self.assertRegex(
            self.content,
            r"Read-only by default",
            "Skill must instruct agents that exploration is read-only by default",
        )
        self.assertRegex(
            self.content,
            r"Do not edit files, scaffold code, install packages, or run destructive commands",
            "Skill must forbid unprompted edits and destructive actions",
        )

    def test_instructs_evidence_grounding_rules(self):
        self.assertRegex(
            self.content,
            r"Inspect implementations, callers, tests, configuration",
            "Skill must ground claims about local code in direct repository evidence",
        )
        self.assertRegex(
            self.content,
            r"Observed.*Inferred.*Unknown",
            "Skill must require distinguishing confirmed facts from speculative inferences",
        )

    def test_instructs_graceful_degradation_without_web_access(self):
        self.assertRegex(
            self.content,
            r"If research access is blocked, say so",
            "Skill must instruct graceful degradation when external search is unavailable",
        )

    def test_instructs_no_cargo_culting_and_yagni(self):
        self.assertRegex(
            self.content,
            r"Do not recommend a library, service, abstraction, or distributed component because a popular project uses it",
            "Skill must reject cargo-culting",
        )

    def test_instructs_handoff_boundaries(self):
        self.assertRegex(
            self.content,
            r"use `fox` for implementation and verification",
            "Skill must designate Fox for bug repairs",
        )
        self.assertRegex(
            self.content,
            r"Read-only execution",
            "Skill must emphasize read-only execution",
        )


class FoxExplorePlaybookContractTests(unittest.TestCase):
    """Check documented constraints only; behavioral results live under evals/."""

    def test_graceful_degradation_contract(self):
        playbook = SKILL_DIR / "references" / "research-playbook.md"
        content = playbook.read_text(encoding="utf-8")
        self.assertIn("Graceful degradation without web access", content)
        self.assertIn("Never invent external URLs, synthetic benchmark numbers", content)

    def test_recommendation_contract(self):
        playbook = SKILL_DIR / "references" / "research-playbook.md"
        content = playbook.read_text(encoding="utf-8")
        self.assertIn("What to improve:", content)
        self.assertIn("What to leave alone:", content)
        self.assertIn("Decision criteria:", content)
        self.assertIn("Migration cost", content)


if __name__ == "__main__":
    unittest.main()
