"""Security, integrity and behavior tests for Fox's record-keeping tools."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

proof = load("proof", ROOT / "skills/fox/scripts/proof.py")
scaffold = load("scaffold", ROOT / "skills/fox/scripts/scaffold.py")
audit = load("audit", ROOT / "skills/fox/scripts/audit.py")
installer = load("installer", ROOT / "install.py")


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = proof.case_init(self.base / "case", "How can input A lead to output B?", "repo/test", True, "build")
        self.src = self.base / "source.txt"
        self.src.write_text("timestamp=2026-10-13\nhandler=run\n", encoding="utf-8")

    def evidence(self):
        return proof.add_file(self.root, self.src, "observation", "line 2", "Observed test handler in controlled fixture")

    def decision(self):
        eid = self.evidence()
        cid = proof.add_claim(self.root, "Handler calls local runner", [eid], "observed", "source.txt:2",
                              "Could be a comment only", "Run parser and prove call edge")
        did = proof.add_decision(self.root, "Single script", ["Multi-agent system"],
                                 "No concurrency, stable input", [cid], True, "Schema becomes dynamic")
        return eid, cid, did

    def test_case_created_without_reusing_existing_folder(self):
        self.assertTrue((self.root / "case.json").is_file())
        with self.assertRaises(FileExistsError):
            proof.case_init(self.root, "How can input A lead to output B?", "repo/test", True, "build")

    def test_hash_tamper_is_detected(self):
        eid = self.evidence()
        state = proof.read_case(self.root)
        saved = self.root / state["evidence"][0]["path"]
        self.assertEqual(proof.check(self.root)[0], [])
        saved.write_text("tampered", encoding="utf-8")
        self.assertTrue(any("SHA-256" in err for err in proof.check(self.root)[0]))

    def test_evidence_immutable_copy_on_source_change(self):
        eid = self.evidence()
        self.src.write_text("source modified", encoding="utf-8")
        state = proof.read_case(self.root)
        saved = self.root / state["evidence"][0]["path"]
        self.assertIn("handler=run", saved.read_text())
        self.assertFalse(proof.check(self.root)[0])

    def test_missing_evidence_is_rejected_for_claim(self):
        with self.assertRaises(ValueError):
            proof.add_claim(self.root, "Interesting claim", ["E999"], "inferred", "x:1", "", "")

    def test_observed_claim_requires_adversarial_challenge(self):
        eid = self.evidence()
        with self.assertRaises(ValueError):
            proof.add_claim(self.root, "Observed control path", [eid], "observed", "file:2", "", "")

    def test_gate_order_and_report(self):
        with self.assertRaises(ValueError):
            proof.phase_change(self.root, "build")
        self.decision()
        with self.assertRaises(ValueError):
            proof.phase_change(self.root, "decide")
        proof.phase_change(self.root, "investigate")
        proof.phase_change(self.root, "decide")
        proof.phase_change(self.root, "build")
        log = self.base / "run.log"
        log.write_text("PASS: sample test\n", encoding="utf-8")
        proof.record_test(self.root, "golden", log, 0, "Sample fixture totals")
        proof.phase_change(self.root, "verify")
        with self.assertRaises(ValueError):
            proof.phase_change(self.root, "deliver")
        state = proof.read_case(self.root)
        state["limitations"].append("One fixture only")
        proof.write_case(self.root, state)
        result = proof.report(self.root)
        proof.phase_change(self.root, "deliver")
        self.assertEqual(proof.check(self.root)[0], [])
        self.assertIn("One fixture only", result.read_text())

    def test_path_traversal_rejected_even_if_hash_looks_valid(self):
        self.evidence()
        state = proof.read_case(self.root)
        state["evidence"][0]["path"] = "../../source.txt"
        proof.write_case(self.root, state)
        self.assertTrue(proof.check(self.root)[0])

    def test_test_log_integrity_detects_tamper(self):
        log = self.base / "run.log"
        log.write_text("PASS\n")
        proof.record_test(self.root, "test", log, 0, "Fixture")
        saved = self.root / proof.read_case(self.root)["evidence"][0]["path"]
        saved.write_text("FAIL\n")
        self.assertTrue(proof.check(self.root)[0])

    def test_distinct_claims_and_decisions(self):
        eid, cid, did = self.decision()
        self.assertEqual((eid, cid, did), ("E001", "C001", "D001"))
        with self.assertRaises(ValueError):
            proof.add_decision(self.root, "script", ["agent"], "reason", ["C999"], True, "When changed")

    def test_invalid_approval_and_authorized_record(self):
        with self.assertRaises(ValueError):
            proof.add_approval(self.root, "grant-root-access", "yes")
        proof.add_approval(self.root, "publish", "Owner explicitly approved final publication")
        self.assertEqual(proof.read_case(self.root)["approvals"][0]["operation"], "publish")

    def test_import_rea_is_attributed_not_assumed_verified(self):
        rea = self.base / "source-rea"
        rea.mkdir()
        (rea / "case.json").write_text('{"some": "rea content"}')
        (rea / "REPORT.md").write_text("# Original REA report\nNot independently checked")
        refs = proof.import_rea(self.root, rea)
        self.assertEqual(refs, ["E001", "E002"])
        self.assertEqual(proof.read_case(self.root)["evidence"][1]["kind"], "rea-report")
        self.assertEqual(proof.read_case(self.root)["claims"], [])

    def test_strict_gate_warns_without_coverage(self):
        self.assertFalse(proof.check(self.root)[0])
        self.assertTrue(proof.check(self.root, strict=True)[0])


class SkillTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_scaffold_audit_and_overwrite_protection(self):
        p = scaffold.scaffold("research-to-video", self.root, ["research", "script", "verify"])
        errors, warnings = audit.audit(p)
        self.assertEqual(errors, [])
        self.assertTrue(warnings)  # Unimplemented on purpose
        with self.assertRaises(FileExistsError):
            scaffold.scaffold("research-to-video", self.root, ["research", "script", "verify"])

    def test_installer_project_dryrun_and_protection(self):
        project = self.root / "project"
        project.mkdir()
        dests = installer.install("codex", project, dry_run=True)
        self.assertFalse(dests[0].exists())
        dests = installer.install("codex", project)
        self.assertTrue((dests[0] / "SKILL.md").exists())
        with self.assertRaises(FileExistsError):
            installer.install("codex", project)
        sentinel = dests[0] / "settings.private"
        sentinel.write_text("retain old unless force")
        installer.install("codex", project, force=True)
        self.assertFalse(sentinel.exists())

    def test_installer_claude_and_cursor_targets(self):
        project = self.root / "project2"
        project.mkdir()
        dests_claude = installer.install("claude", project)
        self.assertEqual(dests_claude[0], project.resolve() / ".claude/skills/fox")
        self.assertTrue((dests_claude[0] / "SKILL.md").is_file())

        dests_cursor = installer.install("cursor", project)
        self.assertEqual(dests_cursor[0], project.resolve() / ".cursor/skills/fox")
        self.assertTrue((dests_cursor[0] / "SKILL.md").is_file())

    def test_installer_antigravity_target(self):
        project = self.root / "project_agy"
        project.mkdir()
        dests = installer.install("antigravity", project)
        self.assertEqual(dests[0], project.resolve() / ".agents/skills/fox")
        self.assertTrue((dests[0] / "SKILL.md").is_file())

    def test_installer_validation_and_errors(self):
        project = self.root / "project3"
        project.mkdir()
        with self.assertRaises(ValueError):
            installer.install("invalid-agent", project)
        with self.assertRaises(ValueError):
            installer.install("codex", self.root / "does-not-exist")

if __name__ == "__main__":
    unittest.main()
