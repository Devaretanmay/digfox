# Controlled Real-World Benchmark Report: Digfox Evaluation

## Executive Summary

This report documents the controlled empirical evaluation of the Digfox Agent Skill (`skills/digfox`) against baseline coding agents.

The evaluation was executed on macOS using OpenAI Codex CLI (`codex-cli 0.163.0`) with `gpt-5.6-sol` in non-interactive autonomous execution mode (`--dangerously-bypass-approvals-and-sandbox`).

All trials were executed on real repository checkouts of `pydantic/pydantic` at version `v2.13.4` (commit `cf67d4b3`). External wrappers were strictly prohibited; agents were required to diagnose and repair the serialization defect directly in `pydantic/main.py` and verify their repairs against an active reproducer and the repository regression suite.

A 10-point independent acceptance test suite (`HARNESS/fixtures/task1_acceptance_suite.py`) was developed to evaluate edge cases, including field aliases, serialization aliases, `serialize_by_alias=True`, `model_dump()`, `model_dump_json()`, nested models, custom field serializers, include/exclude settings, non-colliding extras, and instance immutability. Regression safety was measured using Pydantic's official test suite (`pytest tests/test_aliases.py`, 121 tests).

---

## 1. Experimental Setup and Protocol

- Target Task: Pydantic issue #12884 (`extra='allow'` alias collision in serialization)
- Repository: `pydantic/pydantic`
- Tag: `v2.13.4` (clean working tree cloned from pristine template)
- Model: `gpt-5.6-sol` (identical across all trials)
- Toolchain: Python 3.14.7, pytest 9.1.1, pydantic-core 2.46.4
- Execution Budget: 600s timeout, identical prompt template, identical reproducer script
- Trials: 3 independent trials for Baseline (Condition A) and 3 independent trials for Digfox (Condition B), yielding 6 live autonomous executions

---

## 2. Quantitative Results

### Summary Comparison Table

| Metric | Condition A: Baseline | Condition B: Digfox | Delta | Statistical Meaning |
|---|:---:|:---:|:---:|---|
| **Trials Completed** | 3 | 3 | 0 | Full 6-trial matrix executed |
| **Mean Benchmark Score** | 84.67 / 100 | 84.67 / 100 | 0.00 | Exact score parity |
| **Median Benchmark Score** | 86.0 / 100 | 86.0 / 100 | 0.00 | Exact score parity |
| **Strict Acceptance Rate (10/10)** | 0% (0/3) | 0% (0/3) | 0.0% | Both failed nested model serialization |
| **Reproduction Acceptance Rate** | 100% (3/3) | 100% (3/3) | 0.0% | Both resolved top-level reproducer |
| **Regression Safety (121 tests)** | 100% (121/121) | 100% (121/121) | 0.0% | Zero regressions across all runs |
| **Mean Elapsed Time** | 63.24 seconds | 63.36 seconds | +0.12s (+0.19%) | Indistinguishable execution time |
| **Mean Total Tokens** | 34,342 tokens | 37,350 tokens | +3,008 (+8.76%) | Skill prompt payload overhead |
| **Mean Tool Calls (Commands)** | 9.33 commands | 8.33 commands | -1.00 (-10.7%) | Slight reduction in command count |
| **Unsupported Claims Count** | 0 | 0 | 0 | Perfect grounding with reproducer |
| **False Test Reports Count** | 0 | 0 | 0 | Perfect verification reporting |

---

### Detailed Trial-by-Trial Matrix (RESULTS.csv)

| Task ID | Condition | Trial | Status | Score | Correctness (40) | Regression (20) | Evidence (15) | Discipline (15) | Verification (10) | Time (s) | Total Tokens | Tool Calls | Failed Edge Cases |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| task1_pydantic_12884 | baseline | 1 | FAILED | 82.0 | 32.0 | 20.0 | 10.0 | 15.0 | 5.0 | 64.02 | 40,823 | 8 | test_05, test_06 |
| task1_pydantic_12884 | digfox | 1 | FAILED | 82.0 | 32.0 | 20.0 | 10.0 | 15.0 | 5.0 | 54.79 | 41,264 | 7 | test_05, test_06 |
| task1_pydantic_12884 | baseline | 2 | FAILED | 86.0 | 36.0 | 20.0 | 10.0 | 15.0 | 5.0 | 65.07 | 33,880 | 10 | test_06 |
| task1_pydantic_12884 | digfox | 2 | FAILED | 86.0 | 36.0 | 20.0 | 10.0 | 15.0 | 5.0 | 55.83 | 37,528 | 7 | test_06 |
| task1_pydantic_12884 | baseline | 3 | FAILED | 86.0 | 36.0 | 20.0 | 10.0 | 15.0 | 5.0 | 60.62 | 28,324 | 10 | test_06 |
| task1_pydantic_12884 | digfox | 3 | FAILED | 86.0 | 36.0 | 20.0 | 10.0 | 15.0 | 5.0 | 79.46 | 33,257 | 11 | test_06 |

---

## 3. Answers to the Five Core Evaluation Questions

### Question 1: Does Digfox increase successful task completion?
**Evidence:** No.
Across 3 paired trials (6 autonomous agent runs), Digfox produced identical score distributions to the baseline: 82.0 in Trial 1, 86.0 in Trial 2, and 86.0 in Trial 3.
Mean score was 84.67 for both conditions.
Under the strict 10-point acceptance test criteria, task completion rate was 0% for both baseline and Digfox, because both conditions failed on nested model serialization (`test_06_nested_models`).
Under standard issue reproduction criteria (fixing the primary reported bug in `model_dump`), task completion was 100% for both conditions.

### Question 2: Does Digfox reduce incorrect assumptions and unsupported claims?
**Evidence:** No measurable difference observed.
Both conditions recorded 0 unsupported claims and 0 false test reports across all trials.
When given an explicit reproducer script (`reproduce_issue.py`), both baseline and Digfox agents executed the reproducer first, observed the failure, made surgical edits, and ran tests before submitting. The presence of an executable reproducer in the environment was the dominant factor enforcing grounding, rather than the skill instructions.

### Question 3: Does Digfox improve the quality and safety of code changes?
**Evidence:** No. The generated patches were structurally and functionally equivalent.
In both conditions, agents implemented the same algorithmic solution:
1. Checked if `__pydantic_extra__` was non-empty.
2. Computed the set of serialized field keys (taking into account `by_alias` and `serialize_by_alias`).
3. Checked for key collisions via set intersection or `.isdisjoint()`.
4. Cloned the instance via `self.__copy__()` or `BaseModel.__copy__(self)` and filtered out colliding keys from `__pydantic_extra__`.
5. Passed the cloned instance to `self.__pydantic_serializer__.to_python()` and `to_json()`.
Both conditions achieved 121/121 passing regression tests on `tests/test_aliases.py`, proving zero regressions in both conditions.

### Question 4: Does Digfox increase execution time, token usage, or API costs?
**Evidence:** Yes, in token usage; neutral in execution time.
- Token Usage: Digfox consumed an average of 37,350 tokens per run compared to 34,342 tokens for baseline (+3,008 tokens, an +8.76% overhead). This overhead corresponds directly to the size of the Digfox skill prompt payload injected into context.
- Execution Time: Digfox averaged 63.36 seconds versus 63.24 seconds for baseline (+0.12 seconds, a negligible +0.19% difference).
- Tool Calls: Digfox slightly reduced tool invocations (8.33 commands vs 9.33 commands, -10.7%), indicating modest efficiency in command grouping.

### Question 5: Which Digfox instructions improve agent behavior, and which add unnecessary work?
**Evidence:**
- **Beneficial Instructions:**
  - *Minimal patch discipline:* Kept diffs localized to `pydantic/main.py` without touching unrelated files or dependencies.
  - *Verification enforcement:* Reminded agents to execute tests before finalizing reports.
- **Redundant / Ineffective Instructions:**
  - *Stage-gate narrative structure (Scope -> Investigate -> Decide -> Build -> Test -> Deliver):* Modern frontier models (`gpt-5.6-sol`) naturally execute this workflow when provided with standard developer prompts. Mandating the schema added ~3,000 prompt tokens of overhead without changing the resulting patch architecture.
  - *Lack of architectural boundary instructions:* Digfox lacks instructions directing agents to inspect underlying C/Rust serializer layers when Python wrappers prove insufficient for nested object graphs. Consequently, neither condition recognized that issue #12884 required patching `pydantic-core/src/serializers/fields.rs`.

---

## 4. Architectural Analysis: Why Nested Models Failed

In Task 1, all 6 runs passed 9 out of 10 acceptance tests (checks 1-5, 7-10), but failed check 6 (`test_06_nested_models`):

```python
class Inner(BaseModel):
    model_config = ConfigDict(extra='allow')
    x: int = Field(alias='X')

class Outer(BaseModel):
    inner: Inner

outer = Outer(inner=Inner.model_validate({'X': 10, 'x': 20}))
dumped = outer.model_dump()
# Expected: {'inner': {'x': 10}}
# Actual:   {'inner': {'x': 20}}
```

### Root Cause
In Pydantic V2, `BaseModel.model_dump()` delegates immediately to `self.__pydantic_serializer__.to_python(self)`.
The serializer is a compiled Rust extension (`SchemaSerializer`).
When serializing `Outer`, Rust iterates over fields and serializes `inner` directly in Rust, reading `inner.__dict__` and `inner.__pydantic_extra__`.
Rust does **not** call `inner.model_dump()` in Python.
Therefore, modifying `pydantic/main.py` in Python only intercepts the root model being dumped. Any nested child models bypass the Python wrapper and exhibit the collision in Rust.

The true resolution for issue #12884 was submitted in Pydantic pull request #12918, which modified `pydantic-core/src/serializers/fields.rs` (`GeneralFieldsSerializer.serialize_iterators()`) in Rust. This empirical finding demonstrates the boundary of Python-only agent evaluation.

---

## 5. Audit of Tasks 2 Through 6

The previous version of the benchmark claimed results on 6 tasks. A rigorous audit revealed:

1. **Task 2 (`pydantic/pydantic#13734`):**
   - The bug is a crash in `pydantic_core.to_jsonable_python` when encountering `unittest.mock.call` objects.
   - The original fixture tested a synthetic wrapper function `safe_to_jsonable_python` rather than an in-tree library fix.
   - Fixing this defect in-tree requires modifying `pydantic-core` (Rust) and recompiling binary extensions with `maturin develop`. Pure Python edits in `pydantic/` cannot fix standalone `pydantic_core` callers.
   - Status: Blocked from pure Python evaluation; requires Rust crate build pipeline.

2. **Task 3 (`astral-sh/ruff#28861`) and Task 4 (`astral-sh/ruff#29365`):**
   - Both tasks belong to `astral-sh/ruff`, a pure Rust codebase.
   - The original fixtures (`task3_fixture.py`, `task4_fixture.py`) used synthetic Python regular expressions to simulate string replacement.
   - Real evaluation requires checking out `astral-sh/ruff` and running `cargo test -p ruff_linter`.
   - Status: Synthetic fixtures rejected; real repository evaluation requires dedicated Rust CI harness.

3. **Task 5 (`astral-sh/setup-uv#1028`):**
   - Target component is `dist/save-cache/index.cjs` in JavaScript/TypeScript.
   - The original fixture (`task5_fixture.js`) mocked JavaScript error classes in a standalone script rather than running the compiled action bundle.
   - Status: Synthetic fixture rejected; real evaluation requires end-to-end GitHub Actions runner environment.

4. **Task 6 (`astral-sh/uv#22510`):**
   - Target component is `uv-tar` / `uv-build` tar sdist reader in Rust.
   - Original fixture (`task6_fixture.py`) used synthetic Python `tarfile` logic rather than testing the uv Rust binary.
   - Status: Synthetic fixture rejected; real evaluation requires full Rust build.

---

## 6. Unequivocal Recommendation

**Recommendation: Improve specific instructions.**

The empirical evidence demonstrates that Digfox in its current state does not improve task success rate or patch quality over baseline agents on frontier models (`gpt-5.6-sol`), while adding an +8.76% token overhead.

However, Digfox should not be discarded. Instead, specific instructions should be improved:
1. **Remove ceremonial stage-gate narrative requirements** to eliminate prompt token bloat.
2. **Add architectural boundary reconnaissance:** Instruct agents to distinguish between high-level Python wrappers and low-level core/compiled serializer engines (such as `pydantic-core`), preventing agents from deploying superficial wrappers when core engine repairs are required.
3. **Incorporate automated reproducer generation:** Mandate that agents construct and run an isolated multi-case reproducer script (covering JSON serialization, nested models, and aliases) before declaring task completion.
