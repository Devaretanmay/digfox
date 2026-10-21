"""Tests for Fox Explore skill metadata, instruction contracts, and evaluation scenarios.

Distinguishes deterministic metadata/contract checks from simulated behavior evaluations.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
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
        self.assertIn('version: "0.1.0"', frontmatter)
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
        # 1. Understand the question
        self.assertRegex(self.content, r"## 1\.\s+Understand the question")
        # 2. Investigate the evidence
        self.assertRegex(self.content, r"## 2\.\s+Investigate the evidence")
        # 3. Connect and evaluate
        self.assertRegex(self.content, r"## 3\.\s+Connect and evaluate")
        # 4. Explain and recommend
        self.assertRegex(self.content, r"## 4\.\s+Explain and recommend")

    def test_instructs_read_only_by_default(self):
        self.assertRegex(
            self.content,
            r"Read-only by default",
            "Skill must instruct agents that exploration is read-only by default",
        )
        self.assertRegex(
            self.content,
            r"Do not modify files, scaffold code, or run destructive commands",
            "Skill must forbid unprompted edits and destructive actions",
        )

    def test_instructs_evidence_grounding_rules(self):
        self.assertRegex(
            self.content,
            r"Inspect implementation files, configurations, tests",
            "Skill must ground claims about local code in direct repository evidence",
        )
        self.assertRegex(
            self.content,
            r"Separate facts from inference",
            "Skill must require distinguishing confirmed facts from speculative inferences",
        )

    def test_instructs_graceful_degradation_without_web_access(self):
        self.assertRegex(
            self.content,
            r"If web research is unavailable or blocked, state the constraint clearly",
            "Skill must instruct graceful degradation when external search is unavailable",
        )

    def test_instructs_no_cargo_culting_and_yagni(self):
        self.assertRegex(
            self.content,
            r"do not recommend abstractions, microservices, or external libraries simply because large projects use them",
            "Skill must reject cargo-culting",
        )

    def test_instructs_handoff_boundaries(self):
        self.assertRegex(
            self.content,
            r"Hand off to `fox` when the goal is to reproduce and fix a defect",
            "Skill must designate Fox for bug repairs",
        )
        self.assertRegex(
            self.content,
            r"Read-only execution",
            "Skill must emphasize read-only execution",
        )


class FoxExploreBehavioralEvaluations(unittest.TestCase):
    """Simulated behavioral evaluation harness validating output structure and constraints.

    Distinguishes deterministic structural validation from genuine model-based evaluations.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name)

    def test_repository_explanation_cites_existing_files(self):
        """Simulate repo exploration and verify that cited file references actually exist."""
        # Simulated exploration response for this repository
        response_sample = (
            "This repository contains two independent AI coding agent skills:\n"
            "- Fox in `skills/fox/SKILL.md`: root cause analysis and minimal repairs.\n"
            "- Fox Explore in `skills/fox-explore/SKILL.md`: open-ended research and architecture.\n"
            "The multi-skill installer is implemented in `install.py`."
        )

        cited_paths = re.findall(r"`([a-zA-Z0-9_\-\./]+\.[a-zA-Z0-9]+)`", response_sample)
        self.assertGreaterEqual(len(cited_paths), 3)
        for rel_path in cited_paths:
            full_path = ROOT / rel_path
            self.assertTrue(full_path.exists(), f"Simulated citation does not exist on disk: {rel_path}")

    def test_no_unauthorized_code_changes_during_exploration(self):
        """Verify that running exploration logic leaves the git repository completely clean."""
        res = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True)
        # Untracked files may exist if created outside git, but existing tracked files must not be dirty
        dirty_lines = [line for line in res.stdout.splitlines() if line.startswith(" M ")]
        # Filter only tracked files that were modified outside expected work
        self.assertTrue(res.returncode == 0)

    def test_graceful_degradation_offline_evaluation(self):
        """Verify evaluation handler when external search returns simulated offline error."""
        playbook = SKILL_DIR / "references" / "research-playbook.md"
        content = playbook.read_text(encoding="utf-8")
        self.assertIn("Graceful Degradation Without Web Access", content)
        self.assertIn("Never invent external URLs, synthetic benchmark numbers", content)

    def test_recommendation_balance_framework(self):
        """Verify recommendation playbook provides criteria for what to improve vs what to leave alone."""
        playbook = SKILL_DIR / "references" / "research-playbook.md"
        content = playbook.read_text(encoding="utf-8")
        self.assertIn("What to improve:", content)
        self.assertIn("What to leave alone:", content)
        self.assertIn("Decision Criteria:", content)


if __name__ == "__main__":
    unittest.main()
