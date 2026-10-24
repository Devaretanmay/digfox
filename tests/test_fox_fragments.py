"""Fragment packaging and safety contracts, not evidence of model compliance."""
from __future__ import annotations

import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import install
from evals.run import install_variant

SKILL = ROOT / "skills/fox-fragments"


class FragmentIntegrationTests(unittest.TestCase):
    def test_standalone_install_copies_every_reference_for_each_agent(self):
        for agent, relative in install.AGENTS.items():
            with self.subTest(agent=agent), tempfile.TemporaryDirectory() as tmp:
                workspace = Path(tmp)
                with contextlib.redirect_stdout(io.StringIO()):
                    dest = install.install(agent, workspace, skill="fox-fragments")[0]
                self.assertEqual(dest, (workspace / relative / "fox-fragments").resolve())
                self.assertEqual({p.name for p in dest.parent.iterdir()}, {"fox-fragments"})
                links = re.findall(r"\]\((references/[^)]+)\)", (dest / "SKILL.md").read_text())
                self.assertEqual(len(links), 5)
                for link in links:
                    self.assertEqual((dest / link).read_bytes(), (SKILL / link).read_bytes())

    def test_router_and_single_fragment_stay_within_small_read_budget(self):
        router = (SKILL / "SKILL.md").read_text()
        body = router.split("---\n", 2)[2]
        self.assertLessEqual(len(body.split()), 400)
        for fragment in (SKILL / "references").glob("*.md"):
            text = fragment.read_text()
            self.assertLessEqual(len(text.split()), 500, fragment.name)
            self.assertNotIn("../fox", text)
            self.assertLessEqual(len(body.split()) + len(text.split()), 900)

    def test_review_preserves_material_safety_and_evidence_contracts(self):
        review = (SKILL / "references/review.md").read_text()
        for required in (
            "specification compliance is unverified",
            "repository instructions", "pre-existing defects",
            "existing guards, tests and repository policy",
            "Severity measures impact and reach, not confidence",
            "No verified findings", "isolated copy",
            "Do not install packages, update snapshots",
            "Never edit, apply fixes, commit, push, approve, merge or post comments",
            "verified findings to repair.md",
        ):
            self.assertIn(required, review)

    def test_evaluation_variants_keep_their_installation_boundaries(self):
        selections = {
            "fox-fragments": {"fox-fragments"},
            "all": set(install.AVAILABLE_SKILLS),
            "both": {"fox", "fox-explore"},
            "baseline": set(),
        }
        for variant, expected in selections.items():
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as tmp:
                workspace = Path(tmp)
                install_variant(workspace, variant)
                for relative in (".agents/skills", ".claude/skills"):
                    parent = workspace / relative
                    actual = {p.name for p in parent.iterdir()} if parent.exists() else set()
                    self.assertEqual(actual, expected)

    def test_fragments_evaluation_smoke_retains_human_grading_and_unknown_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "results.json"
            # This checks runner plumbing only; the no-op command is not an agent benchmark.
            result = subprocess.run([
                sys.executable, str(ROOT / "evals/run.py"),
                "--variant", "fox-fragments", "--agent-command", sys.executable + ' -c "pass"',
                "--task", "review-tenant-regression", "--task", "review-clean-change",
                "--output", str(output),
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(output.read_text())
            self.assertEqual(payload["summary"]["automatically_scored"], 0)
            self.assertEqual(len(payload["results"]), 2)
            for record in payload["results"]:
                self.assertTrue(record["human_review_required"])
                self.assertEqual(record["changed_files"], [])
                for metric in ("tool_calls", "input_tokens", "output_tokens"):
                    self.assertIsNone(record[metric])

    def test_interactive_fragments_and_numeric_combination(self):
        for choice, expected in (("4", {"fox-fragments"}), ("1,4", {"fox", "fox-fragments"})):
            with self.subTest(choice=choice), tempfile.TemporaryDirectory() as tmp:
                inputs = iter(["4", choice, tmp])
                with patch("builtins.input", lambda *args: next(inputs)), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(install.main(["--interactive"]), 0)
                parent = Path(tmp) / ".agents/skills"
                self.assertEqual({p.name for p in parent.iterdir()}, expected)

    def test_original_explicit_three_skill_selection_still_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            destinations = install.install("codex", Path(tmp), skill="fox,fox-explore,fox-review")
            self.assertEqual({p.name for p in destinations}, {"fox", "fox-explore", "fox-review"})

    def test_cli_help_advertises_fragments(self):
        result = subprocess.run([sys.executable, str(ROOT / "install.py"), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r"fox-\s*fragments")


if __name__ == "__main__":
    unittest.main()
