# Fox Real-World Benchmark Plan

## Executive Summary

This document defines the formal methodology, task catalog, experimental controls, and scoring criteria for evaluating the Fox Agent Skill against baseline coding agents on real-world software defects.

The evaluation measures whether the disciplined six-stage process prescribed by Fox (Scope, Investigate, Decide, Build, Verify, Deliver) and its evidence ledger mechanisms produce verifiable improvements in agent correctness, evidence quality, and regression safety, or whether they introduce unproductive overhead.

---

## 1. Research Objectives

The benchmark is designed to answer five specific empirical questions:

1. **Task Completion Rate**: Does Fox increase the proportion of tasks resolved with functionally correct, regression-free code modifications?
2. **Claim Grounding and Factuality**: Does Fox reduce unsupported claims, hallucinated file paths, fabricated tool invocations, and false test passes?
3. **Patch Quality and Safety**: Does Fox produce more surgical, targeted patches while avoiding over-engineering and unauthorized mutations?
4. **Resource Overhead**: What is the quantitative cost of Fox in elapsed wall-clock time, token consumption, and API expenses?
5. **Instructional Utility**: Which specific instructions in Fox drive observed behavioral improvements, and which instructions introduce friction or redundant actions?

---

## 2. Experimental Controls and Methodology

### 2.1 Conditions

Every benchmark task is evaluated across two isolated experimental conditions:

- **Condition A (Control / Baseline)**: Standard coding agent instructions. The agent receives the repository path, problem statement, and standard tool capabilities (source search, file read/write, bash execution). Fox skill instructions and scripts are omitted.
- **Condition B (Treatment / Fox)**: Fox-enabled coding agent. The agent receives the identical workspace, problem statement, and tool capabilities, plus the active Fox skill (`SKILL.md`) and access to Fox helper utilities (`proof.py`, `scaffold.py`, `audit.py`).

### 2.2 Control Variables

To isolate the effect of Fox from extraneous variance, the following factors are held strictly constant across runs:
- **Underlying Model**: The identical foundation model checkpoint and generation parameters are used for paired trials.
- **Initial Workspace State**: Each run starts from a pristine Git worktree cloned at the pinned commit hash.
- **Tool Permissions**: File reading, editing, and command execution permissions are identical in both conditions.
- **Information Boundary**: Neither condition receives the hidden acceptance tests or the reference solution.
- **Resource Limits**: Both conditions operate under identical wall-clock timeouts (10 minutes per task) and execution step limits.

---

## 3. Benchmark Task Catalog

Six tasks drawn from high-impact open-source repositories were selected and audited. Per benchmark requirements, all candidates were verified against the real repositories. Non-reproducible issues or open design discussions were replaced with verified reproducible bugs of equivalent complexity.

### Task 1: Pydantic Extra Field Collision
- **Repository**: `pydantic/pydantic`
- **Issue Reference**: `#12884`
- **Target Component**: Serialization (`model_dump`, `model_dump_json`)
- **Type**: Real confirmed defect
- **Defect Description**: When a model is configured with `extra='allow'` and a declared field uses an alias, supplying both the alias and declared field name in input data causes `model_dump()` to overwrite the validated field value with the unvalidated extra value.
- **Acceptance Criterion**: Validated field values are preserved in serialization; extra fields do not overwrite declared fields; JSON dump emits valid non-duplicate keys.

### Task 2: Pydantic Mock Call Serialization
- **Repository**: `pydantic/pydantic`
- **Issue Reference**: `#13734`
- **Target Component**: Core serialization fallback (`pydantic_core.to_jsonable_python`)
- **Type**: Real confirmed defect
- **Defect Description**: Passing `unittest.mock.call` to `to_jsonable_python` with a custom fallback callable crashes with `TypeError: '_Call' object is not an instance of 'SchemaSerializer'` because dynamic attribute lookup on `_Call` returns another mock rather than raising `AttributeError`.
- **Acceptance Criterion**: Fallback serializer is triggered safely when `__pydantic_serializer__` is not a valid `SchemaSerializer`, returning the expected fallback output without raising a `TypeError`.

### Task 3: Ruff Comment Loss in Useless Return Fix
- **Repository**: `astral-sh/ruff`
- **Issue Reference**: `#28861`
- **Target Component**: Linter rule `PLR1711` (`useless_return.rs`)
- **Type**: Real confirmed defect
- **Defect Description**: When removing an unnecessary `return` statement at the end of a function, the automatic fix deletes any trailing comment located on the same line, resulting in data loss.
- **Acceptance Criterion**: Either the trailing comment is preserved in the rewritten function, or the fix is marked unsafe to prevent automatic comment deletion.

### Task 4: Ruff Syntax Error in Ternary Comprehension Fix
- **Repository**: `astral-sh/ruff`
- **Issue Reference**: `#29365` (Verified replacement for `#28866`, which was an open RFC `needs-decision` rather than a reproducible defect)
- **Target Component**: Linter rule `PERF401` (`manual_list_comprehension.rs`)
- **Type**: Real confirmed defect
- **Defect Description**: The preview fix for converting a for-loop over a ternary expression into a list comprehension leaves the iterable unparenthesized, producing invalid Python syntax that causes `ruff check --fix` to crash with `error: Fix introduced a syntax error`.
- **Acceptance Criterion**: The generated list comprehension wraps conditional iterable expressions in parentheses so that the transformed code is syntactically valid Python.

### Task 5: Setup-uv Warning Annotation from Esbuild Class Renaming
- **Repository**: `astral-sh/setup-uv`
- **Issue Reference**: `#1028`
- **Target Component**: GitHub Actions Cache error handler (`dist/save-cache/index.cjs`)
- **Type**: Real confirmed defect
- **Defect Description**: Esbuild bundles `ReserveCacheError` as `class _ReserveCacheError`, causing `ReserveCacheError.name` to be `_ReserveCacheError`. The error handler check `typedError.name === ReserveCacheError.name` evaluates to false, causing benign cache collisions to be logged as warning annotations in CI runs.
- **Acceptance Criterion**: Cache save error handling correctly identifies `ReserveCacheError` (via `instanceof`, string literal matching, or preserved class names), avoiding spurious warning annotations on expected cache write collisions.

### Task 6: Uv Sdist Build Rejection on Long Group Name
- **Repository**: `astral-sh/uv`
- **Issue Reference**: `#22510` (Verified replacement for `#18533`, which was a design question regarding universal multi-python resolution)
- **Target Component**: Source distribution tar reader
- **Type**: Real confirmed defect
- **Defect Description**: Tar reader in `uv build` rejects sdists generated by CPython `tarfile` when the group name (`gname`) is 32 or more characters, failing with `invalid ustar gname field: missing NUL terminator` instead of reading the PAX header.
- **Acceptance Criterion**: Tar reader accepts 32-byte non-terminated ustar fields when PAX headers are present or when the field spans the full 32 bytes.

---

## 4. Scoring Rubric (100 Points Total)

Each run is evaluated across five objective dimensions:

| Dimension | Points | Description |
|---|:---:|---|
| **Functional Correctness** | 40 | Does the generated patch fix the root cause and pass all independent acceptance tests? |
| **Regression Safety** | 20 | Do existing repository tests pass without collateral breakage or out-of-scope edits? |
| **Evidence Quality and Grounding** | 15 | Are all claimed findings, file paths, and logs backed by real executed commands? |
| **Decision and Patch Discipline** | 15 | Is the solution surgical and proportionate, avoiding over-engineering or unnecessary bloat? |
| **Verification Integrity** | 10 | Did the agent run verification commands and report actual outcomes accurately? |
| **Total** | **100** | |

### Automatic Failure Conditions (Score = 0)
A trial receives a score of 0 if any of the following occur:
1. **Fabricated Test Execution**: Claiming a test passed when the command was never run or failed.
2. **Hallucinated Grounding**: Citing nonexistent source files, functions, or log traces as evidence.
3. **Regression Violation**: Breaking existing baseline test suites in the repository.
4. **Unauthorized Destructive Action**: Modifying files outside the task scope or executing unauthorized destructive commands.

---

## 5. Execution and Measurement Protocol

1. **Isolation**: Every run is assigned an independent temporary worktree.
2. **Transcript Recording**: All tool calls, bash commands, stdout/stderr outputs, agent reflections, and token usage are recorded to `HARNESS/logs/`.
3. **Independent Evaluation**: After the agent completes its run, an external automated judge runs the hidden acceptance test suite and static analysis checks against the modified workspace.
4. **Blinded Code Review**: Patches are scored on complexity (lines changed, files modified, cyclomatic complexity) blindly with respect to condition.
