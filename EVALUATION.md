# How we evaluate Digfox: real-world benchmark plan

Our unit tests verify that Digfox scripts execute and that file hashes detect tampering. They do not prove that an AI agent using Digfox writes better code, hallucinates less, or builds simpler systems.

To measure whether Digfox actually improves agent accuracy and reliability, we test agents on real GitHub issues across major open-source repositories using actual source code, reported bugs, and executable tests. We do not use synthetic coding puzzles, generated bugs, or tasks with pre-supplied solutions.

---

## 1. Selected real-world tasks

We evaluate across six real-world issues from four active repositories:

### Task 1: Fix a data serialization bug
* **Repository**: `pydantic/pydantic`
* **Issue**: [#12884](https://github.com/pydantic/pydantic/issues/12884)
* **Difficulty**: Medium
* **Problem**: Under certain alias and extra-field settings, serialization can overwrite a validated field with an extra-field value or emit duplicate keys in JSON output.
* **Pass criteria**: Preserve the validated field value, resolve key collisions cleanly, and pass existing serialization regressions.
* **Evaluation focus**: Codebase investigation, root-cause analysis, and safe fixes without side effects.

### Task 2: Fix object serialization
* **Repository**: `pydantic/pydantic`
* **Issue**: [#13734](https://github.com/pydantic/pydantic/issues/13734)
* **Difficulty**: Medium
* **Problem**: Serializing Python `unittest.mock.call` objects can raise an unhandled exception during type inspection or recursive extraction.
* **Pass criteria**: Reproduce the error with mock call structures, correct supported behavior, and handle related inputs without breaking existing object serialization.
* **Evaluation focus**: Debugging unusual input types and boundary conditions.

### Task 3: Fix a linter autofix regression
* **Repository**: `astral-sh/ruff`
* **Issue**: [#28861](https://github.com/astral-sh/ruff/issues/28861)
* **Difficulty**: Hard
* **Problem**: An isort autofix pass can reorder or group imports in a way that introduces a secondary `F401` unused-import violation.
* **Pass criteria**: Reproduce the interaction, prevent the unwanted secondary violation, and pass relevant linter regression suites.
* **Evaluation focus**: Complex feature interactions, AST transformation safety, and regression prevention.

### Task 4: Preserve comments during autofix
* **Repository**: `astral-sh/ruff`
* **Issue**: [#28866](https://github.com/astral-sh/ruff/issues/28866)
* **Difficulty**: Medium
* **Problem**: The `PLR1711` useless-return autofix rule can inadvertently strip adjacent inline comments when removing redundant return statements.
* **Pass criteria**: Preserve all attached and surrounding comments, remove only the redundant return statement, and verify AST and formatting integrity.
* **Evaluation focus**: Surgical code edits and protecting non-executable syntax elements.

### Task 5: Fix a GitHub Action warning
* **Repository**: `astral-sh/setup-uv`
* **Issue**: [#1028](https://github.com/astral-sh/setup-uv/issues/1028)
* **Difficulty**: Medium
* **Problem**: Concurrent cache saves emit a warning because an upstream error class name changed in an action dependency.
* **Pass criteria**: Handle the updated error class correctly without suppressing unrelated cache or network failures.
* **Evaluation focus**: Dependency reconnaissance, error classification, and minimal blast radius.

### Task 6: Investigate a dependency resolver issue
* **Repository**: `astral-sh/uv`
* **Issue**: [#18533](https://github.com/astral-sh/uv/issues/18533)
* **Difficulty**: Hard
* **Problem**: A dependency constraint alters the version selected by the resolver despite an explicit highest-version resolution request.
* **Pass criteria**: Reproduce the reported dependency graph, determine whether the behavior is a genuine defect or expected SAT/PubGrub constraint resolution, and provide a tested fix only if a defect is confirmed.
* **Evaluation focus**: Avoiding unjustified code changes when an issue report describes expected behavior.

### Fixture validation rule
Before testing, each issue must be pinned to an exact Git commit where the behavior is observed. If an issue no longer reproduces on the default branch, the benchmark must check out the original affected commit or select an equivalent verified issue.

---

## 2. Controlled experimental protocol

We run a controlled A/B experiment for every task:

```
+-----------------------------------------------------------+
|                      Task Definition                      |
| (Pinned commit, problem statement, reproducible test case)|
+-----------------------------+-----------------------------+
                              |
              +---------------+---------------+
              |                               |
              v                               v
    +-------------------+           +-------------------+
    |     Control A     |           |      Test B       |
    |  Without Digfox   |           |    With Digfox    |
    |                   |           |                   |
    | Same model        |           | Same model        |
    | Same workspace    |           | Same workspace    |
    | Same tool access  |           | Same tool access  |
    | Same token budget |           | Same token budget |
    | No Digfox skill   |           | Digfox activated  |
    +---------+---------+           +---------+---------+
              |                               |
              +---------------+---------------+
                              |
                              v
             +----------------------------------+
             |      Independent Evaluation      |
             |  - Hidden regression tests       |
             |  - Blinded code diff review      |
             |  - Tool & token audit            |
             +----------------------------------+
```

### Protocol rules
1. **Freeze inputs**: Both conditions use the exact same foundation model, prompt, repository commit, tool permissions, and execution time budget.
2. **Isolate workspaces**: Runs execute in independent, clean working directories cloned from the target commit.
3. **No leakages**: Hidden regression tests and reference solutions are never provided to either agent.
4. **Blinded evaluation**: Diff scoring and evidence reviews are conducted without revealing whether the patch was generated with or without Digfox.
5. **No self-review**: The evaluating agent cannot be the agent that generated the patch.

---

## 3. Scoring rubric (100 points total)

Each run is evaluated on a 100-point rubric:

| Evaluation Dimension | Points | Description |
|----------------------|:------:|-------------|
| **Functional correctness** | 40 | Does the solution fix the issue and pass hidden regression tests? |
| **Regression safety** | 20 | Does existing repository behavior remain intact without collateral breakage? |
| **Evidence quality** | 15 | Are root-cause claims supported by inspected files, logs, or reproduced traces? |
| **Decision quality** | 10 | Did the agent make a surgical, proportionate change rather than over-engineering? |
| **Verification integrity** | 10 | Did the agent run tests and report true outcomes without fabrication? |
| **Resource efficiency** | 5 | Token spend, tool call volume, and wall-clock execution time within budget. |
| **Total** | **100** | |

### Hard failure rules
A run receives an automatic score of zero on correctness and fails the benchmark if:
* The agent claims a test passed when the test command was never run or failed.
* The agent introduces a regression to existing test suites.
* The agent makes unauthorized external network calls or destructive mutations outside the target scope.
* The agent invents non-existent functions, files, or API endpoints as evidence.

---

## 4. Benchmark matrix and sample size

* **Tasks**: 6 real open-source issues
* **Conditions**: 2 (Control A without Digfox, Test B with Digfox)
* **Replications**: 3 runs per condition to check consistency rather than single lucky passes
* **Total evaluation runs**: 36 runs (6 tasks * 2 conditions * 3 replications)
* **Model control**: The same underlying model and temperature settings are held constant across all 36 runs.

---

## 5. Benchmark scorecard

| Task | Issue Reference | Without Digfox (Avg / 100) | With Digfox (Avg / 100) | Status |
|------|-----------------|:--------------------------:|:-----------------------:|:------:|
| 1. Serialization collision | `pydantic/pydantic#12884` | Pending | Pending | Harness ready |
| 2. Mock serialization | `pydantic/pydantic#13734` | Pending | Pending | Queue |
| 3. Import autofix | `astral-sh/ruff#28861` | Pending | Pending | Queue |
| 4. Comment preservation | `astral-sh/ruff#28866` | Pending | Pending | Queue |
| 5. Cache warning | `astral-sh/setup-uv#1028` | Pending | Pending | Queue |
| 6. Dependency resolution | `astral-sh/uv#18533` | Pending | Pending | Queue |
| **Overall average** | | **Pending** | **Pending** | **0/6 Complete** |

---

## 6. Pre-declared success criteria

Before running the full 36-run matrix, we set concrete success thresholds:

1. **Correctness delta**: At least a 15-percentage-point higher rate of correct, regression-free completions with Digfox enabled.
2. **Zero false claims**: Zero instances of fabricated test executions or hallucinated evidence in the Digfox condition.
3. **Safety boundary**: Zero unauthorized writes or out-of-scope modifications.
4. **Efficiency budget**: No more than 30% additional median token overhead for the Digfox investigation and verification trail, justified by higher first-time correctness.

---

## 7. Current status: Task 1 pilot harness

Task 1 (`pydantic/pydantic#12884`) serves as the pilot benchmark fixture. The harness provides:
* A standalone reproduction script demonstrating the validated field overwrite bug.
* An isolated test harness assessing collision handling, alias preservation, and extra-field retention.
* An example Digfox case ledger recording the investigation, hypotheses, and verification checks.
