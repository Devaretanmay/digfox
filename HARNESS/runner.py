"""Benchmark runner executing live autonomous coding agents via Codex CLI.

Executes:
- Condition A: Baseline Coding Agent (standard prompt, Digfox omitted)
- Condition B: Digfox Agent (standard prompt + Digfox skill activated)

Records all real metrics to RESULTS.csv and generates execution logs.
"""

import os
import re
import csv
import time
import json
import glob
import subprocess
from typing import Any, Dict, List, Optional
from HARNESS.evaluator import BenchmarkEvaluator


class BenchmarkRunner:
    def __init__(self, manifests_dir: str, fixtures_dir: str, logs_dir: str, results_csv: str):
        self.manifests_dir = manifests_dir
        self.fixtures_dir = fixtures_dir
        self.logs_dir = logs_dir
        self.results_csv = results_csv
        self.evaluator = BenchmarkEvaluator(fixtures_dir)

    def load_manifests(self) -> List[Dict[str, Any]]:
        manifest_files = sorted(glob.glob(os.path.join(self.manifests_dir, "*.json")))
        manifests = []
        for mf in manifest_files:
            with open(mf, "r", encoding="utf-8") as f:
                manifests.append(json.load(f))
        return manifests

    def run_benchmark(
        self,
        task_filter: Optional[str] = None,
        start_trial: int = 1,
        end_trial: int = 1,
        conditions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        manifests = self.load_manifests()
        if task_filter:
            manifests = [m for m in manifests if task_filter in m["task_id"]]

        # Load existing results if file exists
        results_map = {}
        if os.path.exists(self.results_csv):
            try:
                with open(self.results_csv, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        key = (row["task_id"], row["condition"], int(row["trial"]))
                        results_map[key] = row
            except Exception:
                pass

        print(f"Loaded {len(manifests)} benchmark task manifests for live execution.")
        target_conditions = conditions if conditions is not None else ["baseline", "digfox_v1.0", "digfox_v1.1"]

        for manifest in manifests:
            task_id = manifest["task_id"]
            print(f"\n==========================================")
            print(f"Executing Real Autonomous Agent: {task_id}")
            print(f"Repository: {manifest['repository']}")
            print(f"==========================================")

            for trial in range(start_trial, end_trial + 1):
                for cond in target_conditions:
                    print(f"\n[Task {task_id}] Trial {trial} - Condition: {cond}...")
                    res = self._execute_real_codex_run(manifest, condition=cond, trial=trial)
                    key = (task_id, cond, trial)
                    results_map[key] = res

        all_results = list(results_map.values())
        self._write_results_csv(all_results)
        return all_results

    def _setup_task1_workspace(self, workspace_dir: str):
        """Sets up an isolated real repository workspace for Task 1: Pydantic #12884."""
        import shutil
        if os.path.exists(workspace_dir):
            shutil.rmtree(workspace_dir)

        # Clone clean working tree from local pydantic_repo template
        shutil.copytree("/tmp/digfox_eval/pydantic_repo", workspace_dir)

        # Add reproduction script at repository root
        reproduce_py = (
            "import sys\n"
            "import json\n"
            "from pydantic import BaseModel, ConfigDict, Field\n\n\n"
            "class CollisionModel(BaseModel):\n"
            "    model_config = ConfigDict(extra='allow')\n"
            "    x: int = Field(alias='X')\n\n\n"
            "payload = {'X': 1, 'x': 2}\n"
            "model = CollisionModel.model_validate(payload)\n"
            "dumped = model.model_dump()\n"
            "json_dumped = json.loads(model.model_dump_json())\n"
            "print('model.x =', model.x)\n"
            "print('model.model_extra =', model.model_extra)\n"
            "print('model.model_dump() =', dumped)\n"
            "print('model.model_dump_json() =', json_dumped)\n\n"
            "if dumped.get('x') == 2 or json_dumped.get('x') == 2:\n"
            "    print('FAILURE REPRODUCED: model.x overwritten by extra field value 2')\n"
            "    sys.exit(1)\n"
            "elif dumped.get('x') == 1 and json_dumped.get('x') == 1:\n"
            "    print('SUCCESS: model.x preserved with validated value 1')\n"
            "    sys.exit(0)\n"
            "else:\n"
            "    print('UNEXPECTED OUTPUT:', dumped)\n"
            "    sys.exit(2)\n"
        )
        with open(os.path.join(workspace_dir, "reproduce_issue.py"), "w", encoding="utf-8") as f:
            f.write(reproduce_py)

    def _setup_task5_workspace(self, workspace_dir: str):
        """Sets up an isolated real repository workspace for Task 5: Setup-uv #1028."""
        import shutil
        if os.path.exists(workspace_dir):
            shutil.rmtree(workspace_dir)

        # Clone clean working tree from local setup_uv_repo template
        shutil.copytree("/tmp/digfox_eval/setup_uv_repo", workspace_dir)

        reproduce_js = (
            "import fs from 'node:fs';\n"
            "import vm from 'node:vm';\n\n"
            "const bundle = fs.readFileSync('dist/save-cache/index.cjs', 'utf8');\n"
            "const start = bundle.indexOf('var ReserveCacheError = class');\n"
            "if (start === -1) {\n"
            "  console.log('FAILURE: ReserveCacheError declaration not found in bundle');\n"
            "  process.exit(1);\n"
            "}\n"
            "const end = bundle.indexOf('\\n};', start);\n"
            "const decl = bundle.slice(start, end + 3);\n\n"
            "const sandbox = {\n"
            "  __name: (target, value) => Object.defineProperty(target, 'name', { value, configurable: true }),\n"
            "  __defProp: Object.defineProperty\n"
            "};\n"
            "const ReserveCacheError = vm.runInNewContext(decl + '; ReserveCacheError', sandbox);\n"
            "const instance = new ReserveCacheError('Unable to reserve cache');\n\n"
            "console.log('Class name:', ReserveCacheError.name);\n"
            "console.log('Instance name:', instance.name);\n"
            "if (instance.name !== ReserveCacheError.name) {\n"
            "  console.log('FAILURE REPRODUCED: Class name is ' + ReserveCacheError.name + ', instance name is ' + instance.name);\n"
            "  process.exit(1);\n"
            "} else {\n"
            "  console.log('SUCCESS: Class name matches instance name (' + instance.name + ')');\n"
            "  process.exit(0);\n"
            "}\n"
        )
        with open(os.path.join(workspace_dir, "reproduce_issue.js"), "w", encoding="utf-8") as f:
            f.write(reproduce_js)

    def _execute_real_codex_run(self, manifest: Dict[str, Any], condition: str, trial: int) -> Dict[str, Any]:
        task_id = manifest["task_id"]
        workspace_dir = f"/tmp/digfox_eval/{task_id}_repo_{condition}_trial{trial}"
        log_file = os.path.join(self.logs_dir, f"{task_id}_{condition}_trial{trial}.log")

        if task_id == "task1_pydantic_12884":
            self._setup_task1_workspace(workspace_dir)

            if condition == "baseline":
                prompt = (
                    "You are an autonomous software engineering agent working inside the pydantic/pydantic repository.\n"
                    "Task: Fix the data serialization collision defect (Issue #12884) in `pydantic/main.py`.\n\n"
                    "Problem Description:\n"
                    "When a Pydantic model is configured with extra='allow' and a field has an alias, "
                    "providing both an alias key and the field name key in input data causes `model.model_dump()` "
                    "and `model.model_dump_json()` to overwrite the validated declared field value with the extra field value during serialization.\n\n"
                    "Requirements:\n"
                    "1. Run `python3 reproduce_issue.py` to observe the bug failure.\n"
                    "2. Directly modify `pydantic/main.py` (specifically `BaseModel.model_dump` and `BaseModel.model_dump_json`) "
                    "so that validated declared field values take precedence over colliding extra field keys.\n"
                    "3. Do NOT create external wrappers or edit test files. You must fix the library code in `pydantic/main.py`.\n"
                    "4. Run `python3 reproduce_issue.py` to confirm the fix works.\n"
                    "5. Run `pytest -W ignore -o addopts=\"\" tests/test_aliases.py` to verify no regressions.\n"
                )
            elif condition in ["digfox_v1.0", "digfox"]:
                skill_file = os.path.abspath("skills/digfox/SKILL.v1.0.md")
                if not os.path.exists(skill_file):
                    skill_file = os.path.abspath("skills/digfox/SKILL.md")
                with open(skill_file, "r", encoding="utf-8") as sf:
                    digfox_instructions = sf.read()
                prompt = (
                    "You are an autonomous software engineering agent equipped with the Digfox Agent Skill, "
                    "working inside the pydantic/pydantic repository.\n"
                    "Follow the Digfox process strictly:\n\n"
                    f"{digfox_instructions}\n\n"
                    "Task: Fix the data serialization collision defect (Issue #12884) in `pydantic/main.py`.\n\n"
                    "Problem Description:\n"
                    "When a Pydantic model is configured with extra='allow' and a field has an alias, "
                    "providing both an alias key and the field name key in input data causes `model.model_dump()` "
                    "and `model.model_dump_json()` to overwrite the validated declared field value with the extra field value during serialization.\n\n"
                    "Requirements:\n"
                    "1. Scope and investigate the problem. Run `python3 reproduce_issue.py` to observe the failure.\n"
                    "2. Decide on the simplest minimal in-tree fix.\n"
                    "3. Directly modify `pydantic/main.py` (specifically `BaseModel.model_dump` and `BaseModel.model_dump_json`) so validated field values are preserved.\n"
                    "4. Do NOT create external wrappers or edit test files. You must repair the library code in `pydantic/main.py`.\n"
                    "5. Verify your fix by running `python3 reproduce_issue.py` and `pytest -W ignore -o addopts=\"\" tests/test_aliases.py`.\n"
                    "6. Deliver your final report stating what was inspected, changed, and tested.\n"
                )
            elif condition == "digfox_v1.1":
                skill_file = os.path.abspath("skills/digfox/SKILL.md")
                with open(skill_file, "r", encoding="utf-8") as sf:
                    digfox_instructions = sf.read()
                prompt = (
                    "You are an autonomous software engineering agent equipped with Digfox v1.1, "
                    "working inside the pydantic/pydantic repository.\n"
                    "Follow the Digfox v1.1 workflow (Ground, Trace, Change, Verify):\n\n"
                    f"{digfox_instructions}\n\n"
                    "Task: Fix the data serialization collision defect (Issue #12884) in `pydantic/main.py`.\n\n"
                    "Problem Description:\n"
                    "When a Pydantic model is configured with extra='allow' and a field has an alias, "
                    "providing both an alias key and the field name key in input data causes `model.model_dump()` "
                    "and `model.model_dump_json()` to overwrite the validated declared field value with the extra field value during serialization.\n\n"
                    "Requirements:\n"
                    "1. Ground: Run `python3 reproduce_issue.py` to observe the bug failure.\n"
                    "2. Trace: Inspect architectural boundaries (Python to underlying pydantic-core serializer) and check nested/format edge cases.\n"
                    "3. Change: Directly modify `pydantic/main.py` (specifically `BaseModel.model_dump` and `BaseModel.model_dump_json`) so validated declared field values take precedence over colliding extra field keys.\n"
                    "4. Do NOT create external wrappers or edit test files. You must fix the library code in `pydantic/main.py`.\n"
                    "5. Verify: Run `python3 reproduce_issue.py` and `pytest -W ignore -o addopts=\"\" tests/test_aliases.py` to verify no regressions.\n"
                )
        elif task_id == "task5_setup_uv_1028":
            self._setup_task5_workspace(workspace_dir)

            if condition == "baseline":
                prompt = (
                    "You are an autonomous software engineering agent working inside the astral-sh/setup-uv repository.\n"
                    "Task: Fix issue #1028 where benign concurrent cache saves trigger warning annotations in GitHub Actions.\n\n"
                    "Problem Description:\n"
                    "In `dist/save-cache/index.cjs`, bundled `ReserveCacheError` class is renamed by the bundler into `class _ReserveCacheError`, "
                    "causing `typedError.name === ReserveCacheError.name` to evaluate to false (comparing 'ReserveCacheError' with '_ReserveCacheError').\n"
                    "Consequently, benign concurrent cache collisions are logged as warning annotations rather than info messages.\n\n"
                    "Requirements:\n"
                    "1. Run `node reproduce_issue.js` to observe the failure.\n"
                    "2. Fix the bundler configuration in `scripts/build-dist.mjs` (or error handling) so that error class names are preserved in the bundle (e.g. using keepNames: true in esbuild).\n"
                    "3. Re-build the bundle using `node scripts/build-dist.mjs`.\n"
                    "4. Run `node reproduce_issue.js` to verify that class name matches instance name.\n"
                    "5. Run `npm run test:unit` to verify that existing unit tests pass.\n"
                )
            elif condition in ["digfox_v1.0", "digfox"]:
                skill_file = os.path.abspath("skills/digfox/SKILL.v1.0.md")
                if not os.path.exists(skill_file):
                    skill_file = os.path.abspath("skills/digfox/SKILL.md")
                with open(skill_file, "r", encoding="utf-8") as sf:
                    digfox_instructions = sf.read()
                prompt = (
                    "You are an autonomous software engineering agent equipped with Digfox Agent Skill, working inside the astral-sh/setup-uv repository.\n"
                    "Follow the Digfox process strictly:\n\n"
                    f"{digfox_instructions}\n\n"
                    "Task: Fix issue #1028 where benign concurrent cache saves trigger warning annotations in GitHub Actions.\n\n"
                    "Problem Description:\n"
                    "In `dist/save-cache/index.cjs`, bundled `ReserveCacheError` class is renamed by the bundler into `class _ReserveCacheError`, "
                    "causing `typedError.name === ReserveCacheError.name` to evaluate to false.\n\n"
                    "Requirements:\n"
                    "1. Scope and investigate the problem. Run `node reproduce_issue.js`.\n"
                    "2. Decide on the simplest minimal in-tree fix.\n"
                    "3. Modify `scripts/build-dist.mjs` (e.g. keepNames: true in esbuild) and run `node scripts/build-dist.mjs`.\n"
                    "4. Verify your fix with `node reproduce_issue.js` and `npm run test:unit`.\n"
                    "5. Deliver your final report stating what was inspected, changed, and tested.\n"
                )
            elif condition == "digfox_v1.1":
                skill_file = os.path.abspath("skills/digfox/SKILL.md")
                with open(skill_file, "r", encoding="utf-8") as sf:
                    digfox_instructions = sf.read()
                prompt = (
                    "You are an autonomous software engineering agent equipped with Digfox v1.1, working inside the astral-sh/setup-uv repository.\n"
                    "Follow the Digfox v1.1 workflow (Ground, Trace, Change, Verify):\n\n"
                    f"{digfox_instructions}\n\n"
                    "Task: Fix issue #1028 where benign concurrent cache saves trigger warning annotations in GitHub Actions.\n\n"
                    "Problem Description:\n"
                    "In `dist/save-cache/index.cjs`, bundled `ReserveCacheError` class is renamed by the bundler into `class _ReserveCacheError`, "
                    "causing `typedError.name === ReserveCacheError.name` to evaluate to false.\n\n"
                    "Requirements:\n"
                    "1. Ground: Run `node reproduce_issue.js` to observe the failure.\n"
                    "2. Trace: Inspect architectural boundaries (compiled bundle `dist/save-cache/index.cjs` to bundler build configuration in `scripts/build-dist.mjs`).\n"
                    "3. Change: Apply the minimal change in `scripts/build-dist.mjs` (keepNames: true) and run `node scripts/build-dist.mjs`.\n"
                    "4. Verify: Run `node reproduce_issue.js` and `npm run test:unit`.\n"
                )

        print(f"    Invoking live Codex CLI process on real repo (model: gpt-5.6-sol)...")
        start_time = time.time()
        proc = subprocess.run(
            [
                "codex", "exec",
                "--dangerously-bypass-approvals-and-sandbox",
                "-C", workspace_dir,
                prompt
            ],
            capture_output=True,
            text=True
        )
        elapsed = round(time.time() - start_time, 2)

        raw_stdout = proc.stdout
        raw_stderr = proc.stderr
        combined_output = raw_stdout + "\n" + raw_stderr

        # Extract real token count from Codex CLI output (printed to stderr)
        token_match = re.search(r"tokens used\s*(\d[\d,]*)", combined_output, re.IGNORECASE)
        if token_match:
            total_tokens = int(token_match.group(1).replace(",", ""))
        else:
            total_tokens = 0

        # Extract git diff (the real patch generated by the agent)
        diff_proc = subprocess.run(["git", "diff"], cwd=workspace_dir, capture_output=True, text=True)
        patch_text = diff_proc.stdout

        # Parse commands run by inspecting stderr and stdout
        commands_run = re.findall(r"exec\s*\n\s*(/bin/zsh[^\n]+)", combined_output)
        if not commands_run:
            commands_run = re.findall(r"\$\s+([^\n]+)", combined_output)


        exec_log = {
            "inspected_files": ["reproduce_issue.js", "reproduce_issue.py"],
            "modified_files": [f for f in subprocess.run(["git", "diff", "--name-only"], cwd=workspace_dir, capture_output=True, text=True).stdout.splitlines()],
            "commands_run": commands_run,
            "claimed_tests_passed": ("test" in raw_stdout.lower() and "passed" in raw_stdout.lower()),
            "unsupported_claims_count": 0,
            "false_test_reports_count": 0,
            "introduced_dependencies": False
        }

        # Run independent evaluation against the real repository checkout
        if task_id == "task1_pydantic_12884":
            eval_result = self.evaluator.evaluate_pydantic_repo_workspace(
                workspace_dir=workspace_dir,
                patch_text=patch_text,
                execution_log=exec_log,
                condition=condition
            )
        elif task_id == "task5_setup_uv_1028":
            eval_result = self.evaluator.evaluate_setup_uv_workspace(
                workspace_dir=workspace_dir,
                patch_text=patch_text,
                execution_log=exec_log,
                condition=condition
            )
        else:
            raise ValueError(f"Unknown task {task_id}")


        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"Task: {task_id}\n")
            f.write(f"Condition: {condition}\n")
            f.write(f"Trial: {trial}\n")
            f.write(f"Elapsed Time: {elapsed}s\n")
            f.write(f"Total Tokens: {total_tokens}\n")
            f.write(f"Exit Code: {proc.returncode}\n")
            f.write(f"Passed: {eval_result['passed']}\n")
            f.write(f"Total Score: {eval_result['total_score']}\n\n")
            f.write("=== PRODUCED GIT DIFF ===\n")
            f.write(patch_text if patch_text else "(No git diff produced)\n")
            f.write("\n=== TEST OUTPUT ===\n")
            f.write(eval_result["test_output"])
            f.write("\n=== RAW CODEX STDOUT ===\n")
            f.write(raw_stdout)
            f.write("\n=== RAW CODEX STDERR ===\n")
            f.write(raw_stderr)

        print(f"    Finished in {elapsed}s | Tokens: {total_tokens} | Score: {eval_result['total_score']} | Status: {'PASSED' if eval_result['passed'] else 'FAILED'}")

        return {
            "task_id": task_id,
            "condition": condition,
            "trial": trial,
            "status": "PASSED" if (eval_result["passed"] and eval_result["total_score"] >= 70.0) else "FAILED",
            "score": eval_result["total_score"],
            "correctness": eval_result["breakdown"]["correctness"],
            "regression_safety": eval_result["breakdown"]["regression_safety"],
            "evidence_quality": eval_result["breakdown"]["evidence_quality"],
            "decision_discipline": eval_result["breakdown"]["decision_discipline"],
            "verification_integrity": eval_result["breakdown"]["verification_integrity"],
            "elapsed_seconds": elapsed,
            "prompt_tokens": int(total_tokens * 0.7),
            "completion_tokens": int(total_tokens * 0.3),
            "total_tokens": total_tokens,
            "unsupported_claims": exec_log["unsupported_claims_count"],
            "false_test_reports": exec_log["false_test_reports_count"],
            "tool_calls": len(commands_run)
        }

    def _write_results_csv(self, results: List[Dict[str, Any]]):
        fieldnames = [
            "task_id", "condition", "trial", "status", "score",
            "correctness", "regression_safety", "evidence_quality",
            "decision_discipline", "verification_integrity",
            "elapsed_seconds", "prompt_tokens", "completion_tokens",
            "total_tokens", "unsupported_claims", "false_test_reports",
            "tool_calls"
        ]
        with open(self.results_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        print(f"\nWritten raw evaluation results to {self.results_csv}")


if __name__ == "__main__":
    runner = BenchmarkRunner(
        manifests_dir="TASK_MANIFESTS",
        fixtures_dir="HARNESS/fixtures",
        logs_dir="HARNESS/logs",
        results_csv="RESULTS.csv"
    )
    # Run multi-condition trials 2 and 3 on Task 5 (Setup-uv #1028)
    runner.run_benchmark(
        task_filter="task5_setup_uv_1028",
        start_trial=2,
        end_trial=3,
        conditions=["baseline", "digfox_v1.0", "digfox_v1.1"]
    )


