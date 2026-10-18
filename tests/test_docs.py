"""Smoke tests verifying every command documented in README.md executes successfully."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF_PY = ROOT / "skills/fox/scripts/proof.py"


class DocumentationSmokeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def test_readme_quickstart_pipeline(self):
        # 1. doctor
        res_doc = subprocess.run([sys.executable, str(PROOF_PY), "doctor"], capture_output=True, text=True)
        self.assertEqual(res_doc.returncode, 0, f"Doctor failed: {res_doc.stderr}")

        # 2. init
        case_dir = self.base / "auth-demo"
        res_init = subprocess.run([
            sys.executable, str(PROOF_PY), "init",
            "--out", str(case_dir),
            "--question", "Why does token refresh fail?",
            "--target", "src/auth",
            "--intent", "build"
        ], capture_output=True, text=True)
        self.assertEqual(res_init.returncode, 0, f"Init failed: {res_init.stderr}")
        self.assertTrue((case_dir / "case.json").exists())

        # Create dummy source file
        src_file = self.base / "token.py"
        src_file.write_text("def validate(token):\n    return token.is_valid()\n", encoding="utf-8")

        # 3. evidence
        res_ev = subprocess.run([
            sys.executable, str(PROOF_PY), "evidence",
            "--file", str(src_file),
            "--kind", "source",
            "--locator", "token.py:15-30",
            "--note", "Token expiration check logic",
            str(case_dir)
        ], capture_output=True, text=True)
        self.assertEqual(res_ev.returncode, 0, f"Evidence failed: {res_ev.stderr}")

        # 4. claim
        res_claim = subprocess.run([
            sys.executable, str(PROOF_PY), "claim",
            "--statement", "Token validation fails due to 2-second client clock skew",
            "--evidence", "E001",
            "--confidence", "observed",
            "--locator", "token.py:22",
            "--alternative", "Token is genuinely expired on server",
            "--falsifier", "Test validation with simulated clock skew",
            str(case_dir)
        ], capture_output=True, text=True)
        self.assertEqual(res_claim.returncode, 0, f"Claim failed: {res_claim.stderr}")

        # 5. decision
        res_dec = subprocess.run([
            sys.executable, str(PROOF_PY), "decision",
            "--choose", "Add 5-second clock skew tolerance window",
            "--instead-of", "Bypass expiration check completely", "Force user re-authentication",
            "--why", "Minimal standard-compliant fix with zero breaking API changes",
            "--claims", "C001",
            "--reversible",
            "--revisit-when", "Auth specification deprecates skew window",
            str(case_dir)
        ], capture_output=True, text=True)
        self.assertEqual(res_dec.returncode, 0, f"Decision failed: {res_dec.stderr}")

        # 6. check
        res_check = subprocess.run([
            sys.executable, str(PROOF_PY), "check",
            str(case_dir)
        ], capture_output=True, text=True)
        self.assertEqual(res_check.returncode, 0, f"Check failed: {res_check.stderr}")

        # 7. report
        res_rep = subprocess.run([
            sys.executable, str(PROOF_PY), "report",
            str(case_dir)
        ], capture_output=True, text=True)
        self.assertEqual(res_rep.returncode, 0, f"Report failed: {res_rep.stderr}")
        self.assertTrue((case_dir / "REPORT.md").exists())


if __name__ == "__main__":
    unittest.main()
