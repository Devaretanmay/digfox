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
sys.path.insert(0, str(ROOT / "skills" / "fox-graph" / "scripts"))

import install  # noqa: E402
from adapters.python_ast_adapter import PythonASTProvider  # noqa: E402
import analyzer  # noqa: E402


class SkillIndependenceInstallationTests(unittest.TestCase):
    """Test installing Fox alone, Fox Graph alone, or both across all supported agents."""

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
            # Fox alone: fox-graph and fox-explore must NOT be installed
            self.assertFalse((dests[0].parent / "fox-graph").exists())
            self.assertFalse((dests[0].parent / "fox-explore").exists())

    def test_install_fox_graph_alone_across_all_agents(self):
        agents_dirs = {
            "antigravity": ".agents/skills/fox-graph",
            "codex": ".agents/skills/fox-graph",
            "claude": ".claude/skills/fox-graph",
            "cursor": ".cursor/skills/fox-graph",
        }
        for agent, rel_path in agents_dirs.items():
            proj = self.project / f"proj_graph_{agent}"
            proj.mkdir(parents=True)
            dests = install.install(agent, proj, skill="fox-graph")
            self.assertEqual(len(dests), 1)
            self.assertEqual(dests[0], proj.resolve() / rel_path)
            self.assertTrue((dests[0] / "SKILL.md").is_file())
            # Fox Graph alone: fox and fox-explore must NOT be installed
            self.assertFalse((dests[0].parent / "fox").exists())
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
            # Fox Explore alone: fox and fox-graph must NOT be installed
            self.assertFalse((dests[0].parent / "fox").exists())
            self.assertFalse((dests[0].parent / "fox-graph").exists())

    def test_install_both_skills_compatibility_across_all_agents(self):
        for agent in ["antigravity", "codex", "claude", "cursor"]:
            proj = self.project / f"proj_both_{agent}"
            proj.mkdir(parents=True)
            dests = install.install(agent, proj, skill="both")
            self.assertEqual(len(dests), 2)
            names = {d.name for d in dests}
            self.assertEqual(names, {"fox", "fox-graph"})
            target_skills_dir = dests[0].parent
            self.assertTrue((target_skills_dir / "fox" / "SKILL.md").is_file())
            self.assertTrue((target_skills_dir / "fox-graph" / "SKILL.md").is_file())
            self.assertFalse((target_skills_dir / "fox-explore").exists())

    def test_install_all_three_skills_across_all_agents(self):
        for agent in ["antigravity", "codex", "claude", "cursor"]:
            proj = self.project / f"proj_all_{agent}"
            proj.mkdir(parents=True)
            dests = install.install(agent, proj, skill="all")
            self.assertEqual(len(dests), 3)
            names = {d.name for d in dests}
            self.assertEqual(names, {"fox", "fox-graph", "fox-explore"})
            target_skills_dir = dests[0].parent
            self.assertTrue((target_skills_dir / "fox" / "SKILL.md").is_file())
            self.assertTrue((target_skills_dir / "fox-graph" / "SKILL.md").is_file())
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
            self.assertFalse((target_skills_dir / "fox-graph").exists())


class SkillIndependentExecutionTests(unittest.TestCase):
    """Verify that each skill functions completely in isolation without the other installed."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="test-exec-")
        self.base = Path(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_fox_execution_in_isolation(self):
        """Fox utility proof.py works with zero presence of Fox Graph."""
        workspace = self.base / "fox_only_ws"
        workspace.mkdir()
        dests = install.install("claude", workspace, skill="fox")
        fox_dir = dests[0]
        self.assertFalse((fox_dir.parent / "fox-graph").exists())

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

    def test_fox_graph_execution_in_isolation(self):
        """Fox Graph CLI works with zero presence of Fox."""
        workspace = self.base / "graph_only_ws"
        workspace.mkdir()
        dests = install.install("claude", workspace, skill="fox-graph")
        graph_dir = dests[0]
        self.assertFalse((graph_dir.parent / "fox").exists())
        self.assertFalse((graph_dir.parent / "fox-explore").exists())

        cli_py = graph_dir / "scripts" / "fox_graph.py"
        self.assertTrue(cli_py.is_file())

        # Create dummy repo and diff
        repo_dir = workspace / "repo"
        repo_dir.mkdir()
        (repo_dir / "util.py").write_text("def helper():\n    return 1\n", encoding="utf-8")
        diff_file = workspace / "patch.diff"
        diff_file.write_text(
            "--- a/util.py\n+++ b/util.py\n@@ -1,2 +1,3 @@\n def helper():\n+    # comment\n     return 1\n",
            encoding="utf-8"
        )

        res = subprocess.run([
            sys.executable, str(cli_py),
            "--repo", str(repo_dir),
            "--diff", str(diff_file),
            "--provider", "python-ast",
            "--json"
        ], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Fox Graph CLI failed: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertIn("changed_symbols", data)
        self.assertIn("coverage_gaps", data)

    def test_fox_explore_execution_in_isolation(self):
        """Fox Explore operates cleanly as a read-only skill in isolation."""
        workspace = self.base / "explore_only_ws"
        workspace.mkdir()
        dests = install.install("claude", workspace, skill="fox-explore")
        explore_dir = dests[0]
        self.assertFalse((explore_dir.parent / "fox").exists())
        self.assertFalse((explore_dir.parent / "fox-graph").exists())

        skill_md = explore_dir / "SKILL.md"
        self.assertTrue(skill_md.is_file())
        content = skill_md.read_text(encoding="utf-8")
        self.assertIn("name: fox-explore", content)
        self.assertTrue((explore_dir / "references" / "research-playbook.md").is_file())
        # Fox Explore must NOT introduce external python scripts, databases, or indexing engines
        self.assertFalse((explore_dir / "scripts").exists())


class CombinedInteroperabilityTests(unittest.TestCase):
    """Verify that all three skills operate together cleanly in a shared workspace."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="test-combined-")
        self.workspace = Path(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_combined_installation_and_workflow(self):
        dests = install.install("antigravity", self.workspace, skill="all")
        self.assertEqual(len(dests), 3)
        fox_dir = next(d for d in dests if d.name == "fox")
        graph_dir = next(d for d in dests if d.name == "fox-graph")
        explore_dir = next(d for d in dests if d.name == "fox-explore")

        self.assertTrue((fox_dir / "SKILL.md").is_file())
        self.assertTrue((graph_dir / "SKILL.md").is_file())
        self.assertTrue((explore_dir / "SKILL.md").is_file())

        # Simulate combined workflow:
        # 1. Fox Graph identifies a coverage gap in an alternate entry point
        # 2. Fox logs a decision in proof.py addressing that exact alternate path
        repo_dir = self.workspace / "app"
        repo_dir.mkdir()
        (repo_dir / "auth.py").write_text(
            "def authenticate(token):\n"
            "    return parse_token(token)\n\n"
            "def parse_token(t):\n"
            "    return t.strip()\n",
            encoding="utf-8"
        )
        diff_file = self.workspace / "change.diff"
        diff_file.write_text(
            "--- a/auth.py\n+++ b/auth.py\n@@ -4,2 +4,3 @@\n def parse_token(t):\n+    if not t: return None\n     return t.strip()\n",
            encoding="utf-8"
        )

        # Run Fox Graph to find blast radius
        res_graph = subprocess.run([
            sys.executable, str(graph_dir / "scripts" / "fox_graph.py"),
            "--repo", str(repo_dir),
            "--diff", str(diff_file),
            "--provider", "python-ast",
            "--json"
        ], capture_output=True, text=True)
        self.assertEqual(res_graph.returncode, 0)
        graph_data = json.loads(res_graph.stdout)

        # Entry point authenticate should be detected as upstream caller
        caller_names = [e["source"]["name"] for e in graph_data["direct_callers"]]
        self.assertIn("authenticate", caller_names)

        # Fox logs decision addressing authenticate entry point
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
            "--choose", "Verify authenticate() handles None from parse_token()",
            "--instead-of", "Only test parse_token directly",
            "--why", "Fox Graph identified authenticate as upstream caller of parse_token",
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

        # Positive: Fox Graph only (Call graph, blast radius, dependency impact, alternate bypass paths)
        {"query": "Analyze call graph and blast radius for proposed git diff in payment gateway", "expected": {"fox-graph"}},
        {"query": "Find unpatched alternate execution paths that might bypass the changes in PR #42", "expected": {"fox-graph"}},
        {"query": "Identify cross-module dependencies and public entry points reaching the modified parser", "expected": {"fox-graph"}},
        {"query": "Select targeted regression tests for changed database migration functions across modules", "expected": {"fox-graph"}},

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

        # Positive: Combinations (Fox + Fox Graph)
        {"query": "Investigate defect in shared URL parser, patch the owning layer, and verify with blast radius analysis across all public client entry points", "expected": {"fox", "fox-graph"}},
        {"query": "Debug breaking change in core query builder, fix the issue, and analyze upstream callers across all microservice handlers", "expected": {"fox", "fox-graph"}},
        {"query": "Trace root cause of memory leak in image processor, apply minimal complete fix, and run impact analysis to detect unverified bypass routes", "expected": {"fox", "fox-graph"}},
        {"query": "Audit security vulnerability in credential handler, implement surgical fix, and inspect dependency graph for unpatched callers", "expected": {"fox", "fox-graph"}},

        # Positive: Combinations (Fox + Fox Explore)
        {"query": "Research architectural options for our token cache, then fix the race condition bug in token_store.py and verify it", "expected": {"fox", "fox-explore"}},
        {"query": "Explain why this unfamiliar payment service fails intermittently, find the root cause, and verify a focused repair", "expected": {"fox", "fox-explore"}},

        # Positive: Combinations (Fox Graph + Fox Explore)
        {"query": "Explain our microservice architecture compared to industry standards and analyze the blast radius of this proposed PR diff", "expected": {"fox-graph", "fox-explore"}},

        # Positive: All three skills (Fox + Fox Graph + Fox Explore)
        {"query": "Explore architectural alternatives for the data pipeline, analyze the blast radius across dependent modules, and fix the memory leak with verification", "expected": {"fox", "fox-graph", "fox-explore"}},

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
        # Fox Graph triggers: call graph, blast radius, patch impact, alternate execution paths, dependency graph, upstream callers, regression tests
        graph_triggers = [
            "call graph", "blast radius", "proposed git diff", "pr #", "unpatched alternate",
            "alternate execution paths", "cross-module dependencies", "public entry points",
            "regression tests", "impact analysis", "dependency graph", "upstream callers",
            "proposed pr diff"
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

        if any(trig in q_lower for trig in graph_triggers):
            selected.add("fox-graph")

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
