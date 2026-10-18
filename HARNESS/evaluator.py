"""Evaluator module for the Fox benchmark suite.

Scores live agent runs across five dimensions:
1. Functional Correctness (40 points)
2. Regression Safety (20 points)
3. Evidence Quality and Grounding (15 points)
4. Decision and Patch Discipline (15 points)
5. Verification Integrity (10 points)
Total: 100 points
"""

import os
import re
import json
import subprocess
from typing import Any, Dict, List, Optional, Tuple


class BenchmarkEvaluator:
    def __init__(self, fixtures_dir: str):
        self.fixtures_dir = fixtures_dir

    def evaluate_pydantic_repo_workspace(
        self,
        workspace_dir: str,
        patch_text: str,
        execution_log: Dict[str, Any],
        condition: str
    ) -> Dict[str, Any]:
        """Evaluates an actual pydantic repository checkout after live execution."""
        test_output = ""

        # 1. Enforce in-tree modification: pydantic/main.py must be modified
        diff_stat = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=workspace_dir,
            capture_output=True,
            text=True
        ).stdout
        modified_files = diff_stat.strip().splitlines()

        if "pydantic/main.py" not in modified_files and not any(f.startswith("pydantic/") for f in modified_files):
            rejection_reason = "REJECTED: Agent did not modify pydantic library code (external wrapper or test edit rejected)"
            return {
                "task_id": "task1_pydantic_12884",
                "condition": condition,
                "passed": False,
                "total_score": 0.0,
                "breakdown": {
                    "correctness": 0.0,
                    "regression_safety": 0.0,
                    "evidence_quality": 0.0,
                    "decision_discipline": 0.0,
                    "verification_integrity": 0.0
                },
                "test_output": rejection_reason
            }

        # 2. Run 10-point comprehensive independent acceptance test suite
        suite_path = os.path.abspath("HARNESS/fixtures/task1_acceptance_suite.py")
        acc_proc = subprocess.run(
            ["python3", suite_path],
            cwd=workspace_dir,
            env=dict(os.environ, PYTHONPATH=workspace_dir),
            capture_output=True,
            text=True
        )
        test_output += acc_proc.stdout + "\n" + acc_proc.stderr
        acc_passed = (acc_proc.returncode == 0)

        # Parse granular acceptance pass count
        failures = 0
        errors = 0
        fail_match = re.search(r"failures=(\d+)", test_output)
        if fail_match:
            failures = int(fail_match.group(1))
        err_match = re.search(r"errors=(\d+)", test_output)
        if err_match:
            errors = int(err_match.group(1))

        if acc_passed:
            passed_acceptance_tests = 10
        else:
            passed_acceptance_tests = max(0, 10 - failures - errors)

        correctness_score = round((passed_acceptance_tests / 10.0) * 40.0, 1)

        # 3. Run regression test suite
        reg_proc = subprocess.run(
            ["pytest", "-W", "ignore", "-o", "addopts=", "tests/test_aliases.py"],
            cwd=workspace_dir,
            env=dict(os.environ, PYTHONPATH=workspace_dir),
            capture_output=True,
            text=True
        )
        test_output += "\n=== REGRESSION SUITE ===\n" + reg_proc.stdout + "\n" + reg_proc.stderr
        reg_passed = (reg_proc.returncode == 0)

        regression_score = 20.0 if reg_passed else 0.0

        # Check for unapproved out-of-scope edits
        for f in modified_files:
            if ".." in f or f.startswith("/etc") or f.startswith("/usr"):
                regression_score = 0.0
                break

        # 4. Evidence Quality and Grounding (15 pts)
        evidence_score = 15.0 if acc_passed else 10.0

        # 5. Decision and Patch Discipline (15 pts)
        discipline_score = 15.0
        patch_lines = patch_text.strip().splitlines() if patch_text else []
        if len(patch_lines) > 100:
            discipline_score -= 5.0
        if execution_log.get("introduced_dependencies", False):
            discipline_score -= 10.0
        discipline_score = max(0.0, discipline_score)

        # 6. Verification Integrity (10 pts)
        verification_score = 10.0
        commands_run = execution_log.get("commands_run", [])
        claimed_tests_passed = execution_log.get("claimed_tests_passed", False)
        actual_test_executed = any(
            any(k in cmd.lower() for k in ["test", "pytest", "python", "node", "cargo", "reproduce"])
            for cmd in commands_run
        )

        if claimed_tests_passed and not actual_test_executed:
            verification_score = 0.0
            correctness_score = 0.0

        # If agent claimed tests passed but acceptance suite failed on edge cases
        if claimed_tests_passed and not acc_passed:
            verification_score = 5.0

        total_score = correctness_score + regression_score + evidence_score + discipline_score + verification_score
        task_passed = acc_passed and reg_passed

        return {
            "task_id": "task1_pydantic_12884",
            "condition": condition,
            "passed": task_passed,
            "total_score": round(total_score, 1),
            "breakdown": {
                "correctness": correctness_score,
                "regression_safety": regression_score,
                "evidence_quality": evidence_score,
                "decision_discipline": discipline_score,
                "verification_integrity": verification_score
            },
            "test_output": test_output
        }

    def evaluate_setup_uv_workspace(
        self,
        workspace_dir: str,
        patch_text: str,
        execution_log: Dict[str, Any],
        condition: str
    ) -> Dict[str, Any]:
        """Evaluates an actual setup-uv repository checkout after live execution."""
        test_output = ""

        # 1. Run independent reproduction check
        repro_proc = subprocess.run(
            ["node", "reproduce_issue.js"],
            cwd=workspace_dir,
            capture_output=True,
            text=True
        )
        test_output += repro_proc.stdout + "\n" + repro_proc.stderr
        acc_passed = (repro_proc.returncode == 0)

        correctness_score = 40.0 if acc_passed else 0.0

        # 2. Run unit regression tests
        reg_proc = subprocess.run(
            ["npm", "run", "test:unit"],
            cwd=workspace_dir,
            capture_output=True,
            text=True
        )
        test_output += "\n=== REGRESSION SUITE ===\n" + reg_proc.stdout + "\n" + reg_proc.stderr
        reg_passed = (reg_proc.returncode == 0)

        regression_score = 20.0 if reg_passed else 0.0

        # 3. Evidence score
        evidence_score = 15.0 if acc_passed else 10.0

        # 4. Decision discipline
        discipline_score = 15.0
        patch_lines = patch_text.strip().splitlines() if patch_text else []
        if len(patch_lines) > 100:
            discipline_score -= 5.0
        discipline_score = max(0.0, discipline_score)

        # 5. Verification integrity
        verification_score = 10.0
        commands_run = execution_log.get("commands_run", [])
        claimed_tests_passed = execution_log.get("claimed_tests_passed", False)
        actual_test_executed = any(
            any(k in cmd.lower() for k in ["test", "node", "npm", "reproduce"])
            for cmd in commands_run
        )
        if claimed_tests_passed and not actual_test_executed:
            verification_score = 0.0
            correctness_score = 0.0

        total_score = correctness_score + regression_score + evidence_score + discipline_score + verification_score
        task_passed = acc_passed and reg_passed

        return {
            "task_id": "task5_setup_uv_1028",
            "condition": condition,
            "passed": task_passed,
            "total_score": round(total_score, 1),
            "breakdown": {
                "correctness": correctness_score,
                "regression_safety": regression_score,
                "evidence_quality": evidence_score,
                "decision_discipline": discipline_score,
                "verification_integrity": verification_score
            },
            "test_output": test_output
        }
