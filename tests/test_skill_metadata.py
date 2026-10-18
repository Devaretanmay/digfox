"""Tests for Fox skill metadata, reference links, and tool availability."""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills/fox"
SKILL_MD = SKILL_DIR / "SKILL.md"
SCRIPTS_DIR = SKILL_DIR / "scripts"


class SkillMetadataAndIntegrityTests(unittest.TestCase):
    def test_skill_frontmatter_metadata(self):
        self.assertTrue(SKILL_MD.is_file(), f"Missing SKILL.md at {SKILL_MD}")
        content = SKILL_MD.read_text(encoding="utf-8")

        # Must start with YAML frontmatter
        self.assertTrue(content.startswith("---\n"), "SKILL.md must begin with YAML frontmatter")
        parts = content.split("---\n", 2)
        self.assertGreaterEqual(len(parts), 3, "Frontmatter must be enclosed in '---'")

        frontmatter = parts[1]
        body = parts[2].strip()

        # Check required fields
        self.assertIn("name: fox", frontmatter)
        self.assertIn("description:", frontmatter)
        self.assertIn('version: "1.1.0"', frontmatter)
        self.assertIn("license: MIT", frontmatter)

        # Word count check: aim for 350-500 words
        word_count = len(body.split())
        self.assertGreaterEqual(word_count, 350, f"Body has {word_count} words; expected >= 350")
        self.assertLessEqual(word_count, 550, f"Body has {word_count} words; expected <= 550")

    def test_required_reference_paths_exist(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        links = re.findall(r"\[.*?\]\((references/[^\)]+)\)", content)
        self.assertGreaterEqual(len(links), 3, "Expected at least 3 reference links in SKILL.md")

        for rel_link in links:
            target = SKILL_DIR / rel_link
            self.assertTrue(target.is_file(), f"Referenced file does not exist: {target}")

    def test_optional_tool_availability(self):
        proof_py = SCRIPTS_DIR / "proof.py"
        scaffold_py = SCRIPTS_DIR / "scaffold.py"
        audit_py = SCRIPTS_DIR / "audit.py"

        self.assertTrue(proof_py.is_file(), "proof.py must exist")
        self.assertTrue(scaffold_py.is_file(), "scaffold.py must exist")
        self.assertTrue(audit_py.is_file(), "audit.py must exist")

        # Test CLI help commands
        for script in [proof_py, scaffold_py, audit_py]:
            res = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"--help failed for {script.name}: {res.stderr}")

    def test_no_broken_cli_commands(self):
        proof_py = SCRIPTS_DIR / "proof.py"
        scaffold_py = SCRIPTS_DIR / "scaffold.py"
        audit_py = SCRIPTS_DIR / "audit.py"

        # 1. proof.py doctor
        res = subprocess.run([sys.executable, str(proof_py), "doctor"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"doctor failed: {res.stderr}")

        # 2. Workflow scaffold + audit pipeline
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            out_wf = tmp / "test-pipeline"

            res_scaff = subprocess.run([
                sys.executable, str(scaffold_py), "test-pipeline",
                "--output", str(tmp),
                "--stages", "collect,process,verify"
            ], capture_output=True, text=True)
            self.assertEqual(res_scaff.returncode, 0, f"scaffold.py failed: {res_scaff.stderr}")
            self.assertTrue((out_wf / "stages" / "01-collect").is_dir())
            self.assertTrue((out_wf / "stages" / "02-process").is_dir())
            self.assertTrue((out_wf / "stages" / "03-verify").is_dir())

            res_audit = subprocess.run([
                sys.executable, str(audit_py), str(out_wf)
            ], capture_output=True, text=True)
            # Audit returns warning since stubs have not been run, but command exits cleanly without crashing
            self.assertIn(res_audit.returncode, [0, 1])

    def test_no_accidental_removal_of_supported_capabilities(self):
        # Verify proof.py maintains full command set
        proof_py = SCRIPTS_DIR / "proof.py"
        res = subprocess.run([sys.executable, str(proof_py), "--help"], capture_output=True, text=True)
        help_text = res.stdout + res.stderr

        required_commands = [
            "doctor", "init", "phase", "evidence", "claim", "decision",
            "test", "limit", "approve", "import-rea", "report", "check"
        ]
        for cmd in required_commands:
            self.assertIn(cmd, help_text, f"Capability '{cmd}' was unexpectedly removed from proof.py")


if __name__ == "__main__":
    unittest.main()
