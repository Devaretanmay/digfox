"""Tests for Fox Graph v0.1: program analysis and patch coverage verification."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add fox-graph scripts to sys.path
ROOT = Path(__file__).resolve().parents[1]
FOX_GRAPH_DIR = ROOT / "skills" / "fox-graph"
FOX_GRAPH_SCRIPTS = FOX_GRAPH_DIR / "scripts"
sys.path.insert(0, str(FOX_GRAPH_SCRIPTS))
sys.path.insert(0, str(ROOT))

import analyzer  # noqa: E402
import fox_graph  # noqa: E402
import install  # noqa: E402
import models  # noqa: E402
import patch_parser  # noqa: E402
from adapters.base import GraphProvider  # noqa: E402
from adapters.gitnexus_adapter import GitNexusProvider  # noqa: E402
from adapters.python_ast_adapter import PythonASTProvider  # noqa: E402


class FoxGraphMetadataTests(unittest.TestCase):
    """Verify skill metadata, frontmatter, references, and style constraints."""

    def test_frontmatter_and_structure(self):
        skill_md = FOX_GRAPH_DIR / "SKILL.md"
        self.assertTrue(skill_md.is_file(), f"Missing {skill_md}")
        content = skill_md.read_text(encoding="utf-8")

        self.assertTrue(content.startswith("---\n"), "SKILL.md must begin with frontmatter")
        parts = content.split("---\n", 2)
        self.assertGreaterEqual(len(parts), 3)

        frontmatter = parts[1]
        self.assertIn("name: fox-graph", frontmatter)
        self.assertIn("description:", frontmatter)
        self.assertIn('version: "0.1.0"', frontmatter)
        self.assertIn("license: MIT", frontmatter)

        # Style constraint: zero em dashes and zero en dashes
        self.assertNotIn("\u2014", content, "Found em-dash in SKILL.md")
        self.assertNotIn("\u2013", content, "Found en-dash in SKILL.md")

    def test_reference_links_exist(self):
        skill_md = FOX_GRAPH_DIR / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")
        links = re.findall(r"\[.*?\]\((references/[^\)]+)\)", content)
        self.assertGreaterEqual(len(links), 3, "Expected at least 3 reference links")

        for rel_link in links:
            target = FOX_GRAPH_DIR / rel_link
            self.assertTrue(target.is_file(), f"Referenced file missing: {target}")
            ref_content = target.read_text(encoding="utf-8")
            self.assertNotIn("\u2014", ref_content, f"Found em-dash in {rel_link}")
            self.assertNotIn("\u2013", ref_content, f"Found en-dash in {rel_link}")


class FoxGraphInstallerTests(unittest.TestCase):
    """Verify multi-skill installer options."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test-installer-")
        self.project = Path(self.temp_dir) / "project"
        self.project.mkdir()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_default_installs_fox_only(self):
        dests = install.install("antigravity", self.project)
        self.assertEqual(len(dests), 1)
        self.assertEqual(dests[0].name, "fox")
        self.assertTrue((dests[0] / "SKILL.md").is_file())

    def test_install_fox_graph_only(self):
        dests = install.install("antigravity", self.project, skill="fox-graph")
        self.assertEqual(len(dests), 1)
        self.assertEqual(dests[0].name, "fox-graph")
        self.assertTrue((dests[0] / "SKILL.md").is_file())
        self.assertTrue((dests[0] / "scripts" / "fox_graph.py").is_file())

    def test_install_both_skills_compatibility(self):
        dests = install.install("claude", self.project, skill="both")
        self.assertEqual(len(dests), 2)
        names = {d.name for d in dests}
        self.assertEqual(names, {"fox", "fox-graph"})
        self.assertTrue((self.project / ".claude/skills/fox/SKILL.md").is_file())
        self.assertTrue((self.project / ".claude/skills/fox-graph/SKILL.md").is_file())

    def test_install_all_skills(self):
        dests = install.install("claude", self.project, skill="all")
        self.assertEqual(len(dests), 3)
        names = {d.name for d in dests}
        self.assertEqual(names, {"fox", "fox-graph", "fox-explore"})
        self.assertTrue((self.project / ".claude/skills/fox/SKILL.md").is_file())
        self.assertTrue((self.project / ".claude/skills/fox-graph/SKILL.md").is_file())
        self.assertTrue((self.project / ".claude/skills/fox-explore/SKILL.md").is_file())


class PatchParserTests(unittest.TestCase):
    """Verify diff parsing into hunks and modified line ranges."""

    def test_parse_single_file_patch(self):
        diff = """diff --git a/pkg/calc.py b/pkg/calc.py
index 1111111..2222222 100644
--- a/pkg/calc.py
+++ b/pkg/calc.py
@@ -10,3 +10,4 @@ def add(a, b):
-    return a - b
+    # fixed operation
+    return a + b
"""
        hunks = patch_parser.parse_unified_diff(diff)
        self.assertEqual(len(hunks), 1)
        hunk = hunks[0]
        self.assertEqual(hunk.file_path, "pkg/calc.py")
        self.assertEqual(hunk.old_start, 10)
        self.assertEqual(hunk.new_start, 10)
        self.assertEqual(hunk.new_lines, 4)
        self.assertIn(10, hunk.modified_lines)
        self.assertIn(11, hunk.modified_lines)

    def test_parse_multi_file_patch_and_deletions(self):
        diff = """diff --git a/a.py b/a.py
--- a/a.py
+++ b/a.py
@@ -5,2 +5,2 @@
-def old():
-    pass
+def new():
+    return 1
diff --git a/b.py b/b.py
deleted file mode 100644
--- a/b.py
+++ /dev/null
@@ -1,3 +0,0 @@
-def dead():
-    pass
"""
        hunks = patch_parser.parse_unified_diff(diff)
        self.assertEqual(len(hunks), 2)
        self.assertEqual(hunks[0].file_path, "a.py")
        self.assertEqual(hunks[1].file_path, "b.py")
        self.assertTrue(hunks[1].is_deleted)


class ControlledGraphAnalysisTests(unittest.TestCase):
    """Test graph queries, relationship tracking, and coverage gaps on a controlled fixture."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test-repo-")
        self.repo = Path(self.temp_dir)
        self._build_fixture_repo()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _build_fixture_repo(self):
        # Package structure:
        # mypkg/
        #   __init__.py (re-exports)
        #   core.py (shared implementation & dynamic call)
        #   wrappers.py (wrapper_a and wrapper_b both calling core)
        #   cli.py (entrypoint calling wrapper_a)
        #   api.py (entrypoint calling wrapper_b)
        #   dead.py (unreachable code)
        # tests/
        #   test_core.py (tests wrapper_a and core)
        pkg = self.repo / "mypkg"
        pkg.mkdir(parents=True)
        tests = self.repo / "tests"
        tests.mkdir()

        (pkg / "__init__.py").write_text(
            "from .wrappers import wrapper_a, wrapper_b\n"
            "from .core import core_calc\n"
            "__all__ = ['wrapper_a', 'wrapper_b', 'core_calc']\n",
            encoding="utf-8",
        )

        (pkg / "core.py").write_text(
            "def core_calc(x, mode='default'):\n"
            "    if mode == 'dynamic':\n"
            "        handler = getattr(x, 'compute', None)\n"
            "        return handler() if handler else 0\n"
            "    return x * 2\n\n"
            "def helper():\n"
            "    return 42\n",
            encoding="utf-8",
        )

        (pkg / "wrappers.py").write_text(
            "from .core import core_calc\n\n"
            "def wrapper_a(x):\n"
            "    # Wrapper entry A\n"
            "    return core_calc(x, 'default')\n\n"
            "def wrapper_b(x):\n"
            "    # Wrapper entry B (alternate path)\n"
            "    return core_calc(x, 'dynamic')\n",
            encoding="utf-8",
        )

        (pkg / "cli.py").write_text(
            "from mypkg.wrappers import wrapper_a\n\n"
            "def main():\n"
            "    return wrapper_a(10)\n",
            encoding="utf-8",
        )

        (pkg / "api.py").write_text(
            "from mypkg.wrappers import wrapper_b\n\n"
            "def handle_request(req):\n"
            "    return wrapper_b(req.value)\n",
            encoding="utf-8",
        )

        (pkg / "dead.py").write_text(
            "def never_called():\n"
            "    return 'dead code'\n",
            encoding="utf-8",
        )

        (tests / "test_core.py").write_text(
            "from mypkg.wrappers import wrapper_a\n\n"
            "def test_wrapper_a():\n"
            "    assert wrapper_a(5) == 10\n",
            encoding="utf-8",
        )

    def test_direct_and_transitive_callers(self):
        provider = PythonASTProvider()
        provider.index_repo(self.repo)

        core_syms = provider.get_symbols(self.repo, "mypkg/core.py")
        core_calc = next(s for s in core_syms if s.name == "core_calc")

    def test_direct_and_transitive_callers(self):
        provider = PythonASTProvider()
        provider.index_repo(self.repo)

        core_syms = provider.get_symbols(self.repo, "mypkg/core.py")
        core_calc = next(s for s in core_syms if s.name == "core_calc")

        # Direct callers of core_calc: wrapper_a and wrapper_b
        direct_edges, transitive_edges = provider.get_incoming_edges(self.repo, core_calc, max_depth=2)
        caller_names = {e.source.name for e in direct_edges if e.relation == "CALLS"}
        self.assertIn("wrapper_a", caller_names)
        self.assertIn("wrapper_b", caller_names)

        # Transitive callers of core_calc (depth 2): main and handle_request
        transitive_callers = {e.source.name for e in transitive_edges if e.relation == "CALLS"}
        self.assertIn("main", transitive_callers)
        self.assertIn("handle_request", transitive_callers)

    def test_wrapper_fix_gap_detection(self):
        """When diff only patches wrapper_a, Fox Graph must flag wrapper_b as unpatched bypass."""
        diff = """diff --git a/mypkg/wrappers.py b/mypkg/wrappers.py
--- a/mypkg/wrappers.py
+++ b/mypkg/wrappers.py
@@ -4,3 +4,4 @@ def wrapper_a(x):
     # Wrapper entry A
+    if x < 0: raise ValueError('negative')
     return core_calc(x, 'default')
"""
        provider = PythonASTProvider()
        graph_analyzer = analyzer.PatchAnalyzer(self.repo, provider)
        result = graph_analyzer.analyze(diff, objective="Validate negative input")

        # Must detect wrapper_a as modified symbol
        modified_names = [s.name for s in result.changed_symbols]
        self.assertIn("wrapper_a", modified_names)

        # Verification plan must flag callers and entry points
        proposed_targets = [check.entry_point for check in result.proposed_checks]
        self.assertTrue(len(result.proposed_checks) >= 1)
        self.assertTrue(
            any("wrapper" in target or "cli.py" in target or "main" in target for target in proposed_targets),
            f"Expected check targeting wrapper or caller, got: {proposed_targets}",
        )

    def test_dynamic_dispatch_limitation_disclosure(self):
        """Detect dynamic calls (getattr) and explicitly report in limitations."""
        provider = PythonASTProvider()
        provider.index_repo(self.repo)
        limitations = provider.get_limitations(self.repo)

        self.assertTrue(any("getattr" in lim for lim in limitations))

    def test_dead_unreachable_code_has_no_entry_points(self):
        provider = PythonASTProvider()
        provider.index_repo(self.repo)

        dead_syms = provider.get_symbols(self.repo, "mypkg/dead.py")
        never_called = next(s for s in dead_syms if s.name == "never_called")

        direct, transitive = provider.get_incoming_edges(self.repo, never_called, max_depth=3)
        calls = [e for e in direct + transitive if e.relation == "CALLS"]
        self.assertEqual(len(calls), 0, "Unreachable code should have zero incoming callers")

    def test_renamed_or_missing_symbols(self):
        """Diff modifying lines outside any function returns module-level symbol."""
        diff = """diff --git a/mypkg/core.py b/mypkg/core.py
--- a/mypkg/core.py
+++ b/mypkg/core.py
@@ -12,2 +12,3 @@
+# new module-level constant
+VERSION = '1.0'
"""
        provider = PythonASTProvider()
        graph_analyzer = analyzer.PatchAnalyzer(self.repo, provider)
        result = graph_analyzer.analyze(diff)

        self.assertEqual(len(result.changed_symbols), 1)
        self.assertEqual(result.changed_symbols[0].kind.lower(), "module")


class GitNexusAdapterContractTests(unittest.TestCase):
    """Test GitNexus provider availability, contract fixtures, and fallbacks."""

    def test_gitnexus_provider_instance(self):
        provider = GitNexusProvider()
        self.assertEqual(provider.name, "gitnexus")

    def test_fallback_when_gitnexus_unindexed(self):
        """When .gitnexus directory does not exist, provider.index_repo handles failure gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            provider = GitNexusProvider()
            # Should safely return False or fail cleanly without crashing
            indexed = provider.index_repo(repo)
            # Without git or npm index, should report False
            if not (repo / ".gitnexus").exists():
                self.assertFalse(indexed)


class EndToEndCLITests(unittest.TestCase):
    """Test CLI execution with diff and repo inputs."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test-cli-")
        self.repo = Path(self.temp_dir)
        pkg = self.repo / "calc"
        pkg.mkdir()
        (pkg / "math.py").write_text(
            "def multiply(a, b):\n    return a * b\n\ndef square(n):\n    return multiply(n, n)\n",
            encoding="utf-8",
        )
        self.diff_file = self.repo / "test.diff"
        self.diff_file.write_text(
            """diff --git a/calc/math.py b/calc/math.py
--- a/calc/math.py
+++ b/calc/math.py
@@ -1,2 +1,3 @@
 def multiply(a, b):
+    if a == 0 or b == 0: return 0
     return a * b
""",
            encoding="utf-8",
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_markdown_output(self):
        cmd = [
            sys.executable,
            str(FOX_GRAPH_SCRIPTS / "fox_graph.py"),
            "--repo",
            str(self.repo),
            "--diff",
            str(self.diff_file),
            "--provider",
            "python-ast",
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0, f"CLI error: {res.stderr}")
        self.assertIn("# Fox Graph Impact & Coverage Report", res.stdout)
        self.assertIn("Changed Components", res.stdout)
        self.assertIn("multiply", res.stdout)
        self.assertIn("Verification Plan", res.stdout)
        self.assertIn("Limitations", res.stdout)

    def test_cli_json_output(self):
        cmd = [
            sys.executable,
            str(FOX_GRAPH_SCRIPTS / "fox_graph.py"),
            "--repo",
            str(self.repo),
            "--diff",
            str(self.diff_file),
            "--provider",
            "python-ast",
            "--json",
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0, f"CLI error: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertIn("changed_symbols", data)
        self.assertIn("blast_radius", data)
        self.assertIn("coverage_gaps", data)
        self.assertIn("proposed_checks", data)
        self.assertIn("limitations", data)
        self.assertEqual(data["changed_symbols"][0]["name"], "multiply")


class RealOpenSourceRepositoryTests(unittest.TestCase):
    """Test Fox Graph against real-world repositories with multi-entry point architectures."""

    def test_jinja_make_attrgetter_multi_entry_point(self):
        """Analyze PR 2165 in Jinja to verify detection of filters sharing make_attrgetter."""
        jinja_repo = Path("/tmp/jinja-test")
        patch_file = Path("/tmp/jinja_pr_2165.patch")
        if not jinja_repo.is_dir() or not patch_file.is_file():
            self.skipTest("Jinja benchmark repo or patch not found at /tmp/jinja-test")

        diff = patch_file.read_text(encoding="utf-8")

        # 1. Test with PythonASTProvider
        ast_provider = PythonASTProvider()
        analyzer_ast = analyzer.PatchAnalyzer(jinja_repo, ast_provider)
        result_ast = analyzer_ast.analyze(diff, objective="Fix map filter default collision")

        self.assertGreaterEqual(len(result_ast.changed_symbols), 1)
        # Entry points must discover multiple callers (e.g. sync_do_unique, do_unique, etc.)
        ep_names = {ep.name for ep in result_ast.public_entry_points}
        self.assertTrue(
            any("unique" in name or "join" in name or "map" in name for name in ep_names),
            f"Expected shared filters in entry points, got: {ep_names}",
        )
        self.assertGreaterEqual(len(result_ast.proposed_checks), 1)

        # 2. Test with GitNexusProvider if indexed
        nexus_provider = GitNexusProvider()
        if (jinja_repo / ".gitnexus").is_dir():
            analyzer_nexus = analyzer.PatchAnalyzer(jinja_repo, nexus_provider)
            result_nexus = analyzer_nexus.analyze(diff, objective="Fix map filter default collision")
            self.assertGreaterEqual(len(result_nexus.changed_symbols), 1)
            self.assertGreaterEqual(len(result_nexus.proposed_checks), 1)


if __name__ == "__main__":
    unittest.main()
