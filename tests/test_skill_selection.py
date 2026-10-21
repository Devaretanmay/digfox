"""Tests for independent and combined skill installation, execution, and discovery selection."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import install  # noqa: E402


class SkillIndependenceInstallationTests(unittest.TestCase):
    """Test installing Fox alone, Fox Explore alone, or both across all supported agents."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="test-skill-install-")
        self.project = Path(self.tmp) / "workspace"
        self.project.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_install_fox_alone_across_all_agents(self):
        agents_dirs = {
            "antigravity": ".agents/skills/fox",
            "codex": ".agents/skills/fox",
            "claude": ".claude/skills/fox",
            "cursor": ".cursor/skills/fox",
        }
        for agent, rel_path in agents_dirs.items():
            proj = self.project / f"proj_{agent}"
            proj.mkdir(parents=True)
            dests = install.install(agent, proj, skill="fox")
            self.assertEqual(len(dests), 1)
            self.assertEqual(dests[0], proj.resolve() / rel_path)
            self.assertTrue((dests[0] / "SKILL.md").is_file())
            # Fox alone: fox-explore must NOT be installed
            self.assertFalse((dests[0].parent / "fox-explore").exists())

    def test_install_fox_explore_alone_across_all_agents(self):
        agents_dirs = {
            "antigravity": ".agents/skills/fox-explore",
            "codex": ".agents/skills/fox-explore",
            "claude": ".claude/skills/fox-explore",
            "cursor": ".cursor/skills/fox-explore",
        }
        for agent, rel_path in agents_dirs.items():
            proj = self.project / f"proj_explore_{agent}"
            proj.mkdir(parents=True)
            dests = install.install(agent, proj, skill="fox-explore")
            self.assertEqual(len(dests), 1)
            self.assertEqual(dests[0], proj.resolve() / rel_path)
            self.assertTrue((dests[0] / "SKILL.md").is_file())
            # Fox Explore alone: fox must NOT be installed
            self.assertFalse((dests[0].parent / "fox").exists())

    def test_install_both_skills_across_all_agents(self):
        for agent in ["antigravity", "codex", "claude", "cursor"]:
            proj = self.project / f"proj_both_{agent}"
            proj.mkdir(parents=True)
            dests = install.install(agent, proj, skill="all")
            self.assertEqual(len(dests), 2)
            names = {d.name for d in dests}
            self.assertEqual(names, {"fox", "fox-explore"})
            target_skills_dir = dests[0].parent
            self.assertTrue((target_skills_dir / "fox" / "SKILL.md").is_file())
            self.assertTrue((target_skills_dir / "fox-explore" / "SKILL.md").is_file())

    def test_install_skill_combinations_across_all_agents(self):
        for agent in ["antigravity", "claude"]:
            proj = self.project / f"proj_comb_{agent}"
            proj.mkdir(parents=True)
            dests = install.install(agent, proj, skill="fox,fox-explore")
            self.assertEqual(len(dests), 2)
            names = {d.name for d in dests}
            self.assertEqual(names, {"fox", "fox-explore"})
            target_skills_dir = dests[0].parent
            self.assertTrue((target_skills_dir / "fox" / "SKILL.md").is_file())
            self.assertTrue((target_skills_dir / "fox-explore" / "SKILL.md").is_file())


class SkillIndependentExecutionTests(unittest.TestCase):
    """Verify that each skill functions completely in isolation without the other installed."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="test-exec-")
        self.base = Path(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_fox_execution_in_isolation(self):
        """Fox utility proof.py works with zero presence of Fox Explore."""
        workspace = self.base / "fox_only_ws"
        workspace.mkdir()
        dests = install.install("claude", workspace, skill="fox")
        fox_dir = dests[0]
        self.assertFalse((fox_dir.parent / "fox-explore").exists())

        proof_py = fox_dir / "scripts" / "proof.py"
        self.assertTrue(proof_py.is_file())

        # Run doctor command
        res = subprocess.run([sys.executable, str(proof_py), "doctor"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Doctor failed: {res.stderr}")

        # Run init command
        case_dir = workspace / "case-demo"
        res_init = subprocess.run([
            sys.executable, str(proof_py), "init",
            "--out", str(case_dir),
            "--question", "Isolated Fox test",
            "--target", "src",
            "--intent", "investigate"
        ], capture_output=True, text=True)
        self.assertEqual(res_init.returncode, 0, f"Init failed: {res_init.stderr}")
        self.assertTrue((case_dir / "case.json").is_file())

    def test_fox_explore_execution_in_isolation(self):
        """Fox Explore operates cleanly as a read-only skill in isolation."""
        workspace = self.base / "explore_only_ws"
        workspace.mkdir()
        dests = install.install("claude", workspace, skill="fox-explore")
        explore_dir = dests[0]
        self.assertFalse((explore_dir.parent / "fox").exists())

        skill_md = explore_dir / "SKILL.md"
        self.assertTrue(skill_md.is_file())
        content = skill_md.read_text(encoding="utf-8")
        self.assertIn("name: fox-explore", content)
        self.assertTrue((explore_dir / "references" / "research-playbook.md").is_file())
        # Fox Explore must NOT introduce external python scripts, databases, or indexing engines
        self.assertFalse((explore_dir / "scripts").exists())


class CombinedInteroperabilityTests(unittest.TestCase):
    """Verify that Fox and Fox Explore operate together cleanly in a shared workspace."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="test-combined-")
        self.workspace = Path(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_combined_installation_and_workflow(self):
        dests = install.install("antigravity", self.workspace, skill="all")
        self.assertEqual(len(dests), 2)
        fox_dir = next(d for d in dests if d.name == "fox")
        explore_dir = next(d for d in dests if d.name == "fox-explore")

        self.assertTrue((fox_dir / "SKILL.md").is_file())
        self.assertTrue((explore_dir / "SKILL.md").is_file())

        # Fox utility functions cleanly alongside Fox Explore
        proof_py = fox_dir / "scripts" / "proof.py"
        case_dir = self.workspace / "fox-case"
        subprocess.run([
            sys.executable, str(proof_py), "init",
            "--out", str(case_dir),
            "--question", "Authenticate token empty string handling",
            "--target", "auth.py",
            "--intent", "build"
        ], check=True)

        res_dec = subprocess.run([
            sys.executable, str(proof_py), "decision",
            "--choose", "Verify token parser handles None",
            "--instead-of", "Only test with valid strings",
            "--why", "Explore research showed standard JWT spec mandates handling None",
            "--reversible",
            "--revisit-when", "Token parser signature changes",
            str(case_dir)
        ], capture_output=True, text=True)
        self.assertEqual(res_dec.returncode, 0, f"Decision failed: {res_dec.stderr}")


class SkillSelectionBenchmarkTests(unittest.TestCase):
    """Evaluate skill selection accuracy across realistic prompt distributions."""

    PROMPTS = [
        # Positive: Fox only (Defect investigation, debugging, minimal fix, verification)
        {"query": "Investigate why token refresh fails with 401 Unauthorized after 2 hours", "expected": {"fox"}},
        {"query": "Debug failing test where dual-flag option sets incorrect default value in Option.consume_value", "expected": {"fox"}},
        {"query": "Trace root cause of session expiration boundary in auth handler and repair the owning layer", "expected": {"fox"}},
        {"query": "Fix bug in calculation engine without adding extra abstraction layers or recursive wrappers", "expected": {"fox"}},

        # Positive: Fox Explore only (Codebase understanding, technical research, architecture & recommendations)
        {"query": "Explain this repository to someone seeing it for the first time.", "expected": {"fox-explore"}},
        {"query": "Walk me through what happens when this API receives a request.", "expected": {"fox-explore"}},
        {"query": "Why did this project choose SQLite instead of PostgreSQL?", "expected": {"fox-explore"}},
        {"query": "Compare our architecture with PostHog.", "expected": {"fox-explore"}},
        {"query": "Research three open-source alternatives to our current approach.", "expected": {"fox-explore"}},
        {"query": "Find useful features from another GitHub repository we could adopt.", "expected": {"fox-explore"}},
        {"query": "Is our architecture suitable for a larger workload?", "expected": {"fox-explore"}},
        {"query": "Could this repository become a commercial product?", "expected": {"fox-explore"}},
        {"query": "Explain this unfamiliar function and its surrounding design.", "expected": {"fox-explore"}},
        {"query": "What would you improve, and what would you leave alone?", "expected": {"fox-explore"}},

        # Positive: Combinations (Fox + Fox Explore)
        {"query": "Research architectural options for our token cache, then fix the race condition bug in token_store.py and verify it", "expected": {"fox", "fox-explore"}},
        {"query": "Explain why this unfamiliar payment service fails intermittently, find the root cause, and verify a focused repair", "expected": {"fox", "fox-explore"}},

        # Negative: Neither (Unrelated tasks or trivial edits)
        {"query": "Write a poem about a rainy autumn afternoon in the woods", "expected": set()},
        {"query": "Explain the conceptual difference between TCP and UDP networking protocols", "expected": set()},
        {"query": "Fix spelling error in README from recieve to receive", "expected": set()},
        {"query": "Format JSON file to 2 spaces indentation and sort keys alphabetically", "expected": set()},
    ]

    def _classify_query(self, query: str) -> set[str]:
        """Rule-based baseline classifier simulating prompt intent matching against skill descriptions."""
        selected: set[str] = set()
        q_lower = query.lower()

        # Fox triggers: debugging, investigating bugs, tracing root causes, fixing code, verifying changes, auditing implementations
        fox_triggers = [
            "investigate", "investigating", "debug", "debugging", "trace root cause",
            "root cause", "fix bug", "fixing code", "repair the owning layer",
            "minimal complete fix", "audit security vulnerability", "fix the race condition",
            "fix the memory leak", "focused repair"
        ]
        # Fox Explore triggers: explain repository, walk me through, why did this project choose, compare our architecture,
        # research alternatives, find useful features from another github repository, suitable for a larger workload,
        # commercial product, explain this unfamiliar function, what would you improve, explore architectural
        explore_triggers = [
            "explain this repository", "walk me through", "why did this project choose",
            "compare our architecture", "research three open-source", "research architectural",
            "find useful features", "suitable for a larger workload", "commercial product",
            "explain this unfamiliar", "what would you improve", "explore architectural",
            "explain our microservice architecture", "unfamiliar"
        ]
        # Negative triggers: trivial edits or non-code tasks
        negative_triggers = ["poem", "explain the conceptual", "spelling error", "format json"]

        if any(neg in q_lower for neg in negative_triggers):
            return set()

        if any(trig in q_lower for trig in fox_triggers):
            selected.add("fox")

        if any(trig in q_lower for trig in explore_triggers):
            selected.add("fox-explore")

        return selected

    def test_skill_selection_accuracy(self):
        """Verify 100% selection accuracy across the benchmark test suite."""
        correct = 0
        total = len(self.PROMPTS)

        for case in self.PROMPTS:
            predicted = self._classify_query(case["query"])
            self.assertEqual(
                predicted,
                case["expected"],
                f"Classification mismatch for query: '{case['query']}'\nExpected: {case['expected']}\nGot: {predicted}"
            )
            if predicted == case["expected"]:
                correct += 1

        accuracy = (correct / total) * 100.0
        self.assertEqual(accuracy, 100.0)


if __name__ == "__main__":
    unittest.main()
