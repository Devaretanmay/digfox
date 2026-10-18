# Unseen Real-World Benchmark: Task Definitions & Operational Protocol

## Executive Summary

To establish whether Fox v1.1 provides generalizable improvements across diverse software defects, we designed two new benchmark tasks from unseen real-world GitHub issues. Neither issue was used in the formulation or testing of Fox v1.0 or v1.1.

In accordance with strict evaluation protocols:
- Both issues are real defects from `pydantic/pydantic` with fixed historical commits.
- Task definitions and hidden acceptance tests were completely frozen before agent invocation.
- All live agent execution relies exclusively on genuine OpenAI Codex CLI processes.

### Operational Notice Regarding Codex API Quota

During the execution of additional live trials, the Codex CLI encountered an external OpenAI ChatGPT account usage quota limit:
```
ERROR: You've hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro),
visit https://chatgpt.com/settings/usage to purchase more credits or try again at 6:23 PM.
```
To maintain absolute scientific integrity, **no runs were simulated, fabricated, or mocked**. The frozen manifests and harnesses are documented below, and the empirical evaluation synthesizes the 12 verified live trials completed prior to the quota threshold.

---

## 1. Unseen Task Definitions

### Task 7 (Architectural Boundary): Pydantic Issue #13074
- **Repository**: `pydantic/pydantic`
- **Target Starting Commit**: `54aca609` (parent of `000e823a`)
- **Category**: Architectural Boundary (Rust deserializer to Python validation callback)
- **Defect Description**:
  When validating models from JSON using `model_validate_json()`, `pydantic-core` parses JSON directly in native Rust. During this pass, `ValidationInfo.field_name` is omitted when invoking Python `@field_validator` functions, causing validation logic that relies on `info.field_name` to fail or raise AttributeErrors.
- **Why Selected**:
  It tests whether an agent can trace behavior across the native engine boundary (Rust `model_fields.rs` to Python `ValidationInfo`), or whether it attempts an incomplete Python wrapper around `model_validate_json`.
- **Reproduction**:
  ```python
  from pydantic import BaseModel, ValidationInfo, field_validator

  class Foo(BaseModel):
      field1: int
      field2: int

      @field_validator('field2')
      @classmethod
      def _validate(cls, v: int, info: ValidationInfo) -> int:
          assert info.field_name == 'field2'
          return v + info.data['field1']

  # Succeeded with model_validate:
  f1 = Foo.model_validate({'field1': 1, 'field2': 2})
  # Failed with model_validate_json (AssertionError: info.field_name is None):
  f2 = Foo.model_validate_json('{"field1": 1, "field2": 2}')
  ```
- **Frozen Acceptance Test**: `tests/test_task7_hidden.py` verifying `info.field_name`, `info.context`, and `info.data` across `model_validate_json`.
- **Regression Suite**: `pytest tests/test_validators.py` (3,145 tests).

---

### Task 8 (Conventional In-Tree Bug): Pydantic Issue #13051
- **Repository**: `pydantic/pydantic`
- **Target Starting Commit**: `e9888941` (parent of `b1bf1944`)
- **Category**: Conventional in-tree logic defect (Python only, zero native boundary)
- **Defect Description**:
  When a model is configured with `extra='allow'`, `self.__pydantic_extra__` initializes to `{}`. When validated with runtime override `extra='forbid'`, `__pydantic_extra__` is `None`. In `BaseModel.__eq__`, the check `self.__pydantic_extra__ == other.__pydantic_extra__` evaluates `{}` == `None` as `False`, causing identical models with identical data to report inequality.
- **Why Selected**:
  It provides an ideal conventional control task to test whether Fox's structured principles assist or overburden simple in-tree Python bug fixes.
- **Reproduction**:
  ```python
  from pydantic import BaseModel

  class MyModel(BaseModel, extra='allow'):
      a: int

  m1 = MyModel.model_validate({'a': 1})
  m2 = MyModel.model_validate({'a': 1}, extra='forbid')

  # Expected: m1 == m2
  # Actual: m1 != m2 (False)
  assert m1 == m2
  ```
- **Frozen Acceptance Test**: `tests/test_task8_hidden.py` verifying model equality with runtime extra overrides, nested models, and private attributes.
- **Regression Suite**: `pytest tests/test_main.py` (2,871 tests).

---

## 2. Synthesis of Completed Live Benchmark Runs

Across the 12 verified live trials executed with Codex CLI (`gpt-5.6-sol`):

### Task 1: Pydantic #12884 (Serialization Boundary)
- **Baseline (3 trials)**: 0% complete pass rate. Mean score 84.67/100. Average time: 63.24s. Average tokens: 34,342. Agents patched top-level `model_dump()` dictionary output and failed on nested models.
- **Fox v1.0 (3 trials)**: 0% complete pass rate. Mean score 84.67/100. Average time: 63.36s. Average tokens: 37,350. Agents followed 6 formal stages but produced identical surface-level patches failing nested models.
- **Fox v1.1 (3 trials)**: 66.7% strict pass rate on initial benchmark (2/3 passed). Mean score 92.00/100 (+7.33 pts). Average time: 113.08s. Average tokens: 50,493. Agents recognized the nested boundary and wrote recursive sanitizers.
- **Adversarial Audit Outcome**: When tested against the 12-point adversarial suite, the Fox v1.1 patches failed 11/12 tests, exposing that the Python recursive sanitizer was an incomplete workaround that bypassed `TypeAdapter` and emitted duplicate JSON keys.

### Task 5: Setup-uv #1028 (Bundler Compiler Boundary)
- **Baseline (1 trial)**: 100% pass rate. Score 100.0/100. Time: 39.46s. Tokens: 21,568.
- **Fox v1.0 (1 trial)**: 100% pass rate. Score 100.0/100. Time: 80.25s (+103% time). Tokens: 34,471 (+60% tokens). Suffered severe latency and token inflation from ceremonial stage restatements.
- **Fox v1.1 (1 trial)**: 100% pass rate. Score 100.0/100. Time: 59.27s (-26.1% vs v1.0). Tokens: 31,836 (-7.6% vs v1.0). Successfully streamlined v1.0's overhead while maintaining 100% correctness and zero regressions.

---

## 3. Comparative Matrix & Statistical Reality

| Evaluation Dimension | Baseline (Codex) | Fox v1.0 | Fox v1.1 |
|---|:---:|:---:|:---:|
| **Initial Benchmark Pass Rate** | 25.0% (1 / 4) | 25.0% (1 / 4) | 75.0% (3 / 4) |
| **Adversarial Test Pass Rate** | 0.0% (0 / 12) | 0.0% (0 / 12) | 8.3% (1 / 12) |
| **Regression Safety Rate** | 100.0% (0 regressions) | 100.0% (0 regressions) | 100.0% (0 regressions) |
| **Average Task 5 Overhead vs Baseline** | 0% (Baseline) | +103% time, +60% tokens | +50% time, +48% tokens |
| **Diagnostic Depth** | Low (surface edits) | Low (ceremonial recitation) | High (boundary detection) |
| **Implementation Layer Discipline** | Low (patches wrapper) | Low (patches wrapper) | Low (patches wrapper) |

### Predictive Hypotheses for Unseen Tasks

1. **On Task 7 (Architectural Boundary, #13074)**:
   Because fixing `ValidationInfo.field_name` requires editing Rust `pydantic-core/src/validators/model_fields.rs` and compiling via `maturin`, Baseline and Fox v1.0 are predicted to attempt Python-level monkey-patching of `model_validate_json()`. Fox v1.1 is expected to identify the Rust FFI boundary, but whether it can compile and test the Rust extension or falls back to a Python wrapper will test the boundary guidance.

2. **On Task 8 (Conventional Bug, #13051)**:
   Because the fix is a single-line modification in `pydantic/main.py` (`(self.__pydantic_extra__ or {}) == (other.__pydantic_extra__ or {})`), Baseline will likely solve it rapidly in ~30 seconds. Fox v1.0 will incur ~80s of ceremonial overhead. Fox v1.1's Ground and Change steps should solve it with minimal overhead (~45s), demonstrating whether the streamlined workflow avoids penalizing simple tasks.
