# Adversarial Acceptance Testing: Pydantic Serialization Collision

## Executive Summary

To rigorously evaluate whether agent patches resolved Pydantic issue #12884 or merely satisfied the initial benchmark fixture, we designed an independent 12-point adversarial test suite (`HARNESS/fixtures/task1_adversarial_suite.py`).

The suite was executed across eleven separate configurations:
1. Clean Pydantic repository (`v2.13.4`, commit `cf67d4b3`)
2. Baseline Trials 1, 2, 3
3. Fox v1.0 Trials 1, 2, 3
4. Fox v1.1 Trials 1, 2, 3, 4, 5 (Trials 4 and 5 conducted on the updated Fox skill)

### Core Empirical Finding

- **Clean Pydantic**: Passed 1 / 12 (only basic immutability passes without crashing).
- **Baseline (all 3 trials)**: Passed 4 to 6 / 12 (all fail T1 Deeply Nested, T2 Collections, T3 Shared Identity, T4 Recursive Structs, T7 Include/Exclude, T10 TypeAdapter).
- **Fox v1.0 (all 3 trials)**: Passed 4 to 6 / 12 (all fail T1 Deeply Nested, T2 Collections, T3 Shared Identity, T4 Recursive Structs, T7 Include/Exclude, T10 TypeAdapter).
- **Fox v1.1 Trial 1**: Passed 6 / 12.
- **Fox v1.1 Trial 2**: Passed 11 / 12 (passed T1-T9, T11, T12; failed only T10).
- **Fox v1.1 Trial 3**: Passed 11 / 12 (passed T1-T9, T11, T12; failed only T10).
- **Fox v1.1 Trial 4 (New Skill)**: Passed 11 / 12 (passed T1-T9, T11, T12; failed only T10).
- **Fox v1.1 Trial 5 (New Skill)**: Passed 6 / 12 (applied strict YAGNI, passed root T5, T6, T8, T9, T11, T12; explicitly documented nested boundary to pydantic-core).

Fox v1.1 achieved a peak 91.7% pass rate (11/12) on rigorous adversarial tests across Trials 2, 3, and 4, and demonstrated calibrated boundary reporting in Trial 5.

## 1. Adversarial Test Matrix

| Test ID | Test Name | Target Behavior Exercised |
|---|---|---|
| **T1** | `test_01_deeply_nested_models` | Depth-4 model hierarchy with alias collisions at alternating depths |
| **T2** | `test_02_models_in_collections` | Models nested inside lists, tuples, and dictionary values |
| **T3** | `test_03_shared_object_identity` | Two model fields referencing the identical child model instance |
| **T4** | `test_04_recursive_structures` | Self-referential linked list model (`Node(next_node=...)`) |
| **T5** | `test_05_custom_field_serializers` | Custom field serializer (`@field_serializer`) modifying output |
| **T6** | `test_06_computed_fields` | Model with computed fields (`@computed_field`) |
| **T7** | `test_07_nested_include_exclude_filtering` | Granular `include` and `exclude` path mappings |
| **T8** | `test_08_validation_alias_vs_serialization_alias` | Divergent validation and serialization aliases |
| **T9** | `test_09_model_dump_json_no_duplicate_keys` | Direct inspection of raw JSON output to verify no duplicate key emissions |
| **T10** | `test_10_direct_typeadapter_serialization` | Direct serialization via `TypeAdapter` bypassing `BaseModel.model_dump` |
| **T11** | `test_11_model_immutability` | Ensuring `model_dump` does not mutate original model state or identity |
| **T12** | `test_12_high_volume_extras_scalability` | Model with 500 extra keys serialized without data corruption |

## 2. Full Empirical Results Table

| Target Configuration | Score | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Clean (unpatched)** | 1 / 12 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | PASS | FAIL |
| **Baseline Trial 1** | 4 / 12 | FAIL | FAIL | FAIL | FAIL | FAIL | PASS | FAIL | PASS | FAIL | FAIL | PASS | PASS |
| **Baseline Trial 2** | 6 / 12 | FAIL | FAIL | FAIL | FAIL | PASS | PASS | FAIL | PASS | PASS | FAIL | PASS | PASS |
| **Baseline Trial 3** | 6 / 12 | FAIL | FAIL | FAIL | FAIL | PASS | PASS | FAIL | PASS | PASS | FAIL | PASS | PASS |
| **Fox v1.0 Trial 1** | 4 / 12 | FAIL | FAIL | FAIL | FAIL | FAIL | PASS | FAIL | PASS | FAIL | FAIL | PASS | PASS |
| **Fox v1.0 Trial 2** | 6 / 12 | FAIL | FAIL | FAIL | FAIL | PASS | PASS | FAIL | PASS | PASS | FAIL | PASS | PASS |
| **Fox v1.0 Trial 3** | 6 / 12 | FAIL | FAIL | FAIL | FAIL | PASS | PASS | FAIL | PASS | PASS | FAIL | PASS | PASS |
| **Fox v1.1 Trial 1** | 6 / 12 | FAIL | FAIL | FAIL | FAIL | PASS | PASS | FAIL | PASS | PASS | FAIL | PASS | PASS |
| **Fox v1.1 Trial 2** | 11 / 12 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | FAIL | PASS | PASS |
| **Fox v1.1 Trial 3** | 11 / 12 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | FAIL | PASS | PASS |
| **Fox v1.1 Trial 4 (New)** | 11 / 12 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | FAIL | PASS | PASS |
| **Fox v1.1 Trial 5** | 6 / 12 | FAIL | FAIL | FAIL | FAIL | PASS | PASS | FAIL | PASS | PASS | FAIL | PASS | PASS |

## 3. In-Depth Comparative Analysis

### Why Baseline and Fox v1.0 Fail 6 to 8 Tests
Baseline agents and Fox v1.0 agents consistently implemented post-serialization dictionary filtering:
1. They called `super().model_dump()` or the default serializer first.
2. They received the serialized dict (already corrupted by `pydantic-core` where extra fields overwrote aliased values).
3. They attempted to patch the dictionary at root level.
This caused immediate failures on:
- T1 (Deeply Nested): Inner models were corrupted before root filtering ran.
- T2 (Collections): Models inside lists and sets were completely bypassed.
- T3 (Shared Identity): Shared references were corrupted.
- T4 (Recursive Structs): Circular or deep chains were either unhandled or crashed.
- T7 (Include/Exclude): Inner inclusion masks were bypassed.
- T9 (JSON Keys): Raw JSON generation did not pass through dict post-filtering.

### Why Fox v1.1 (Trials 2, 3, and 4) Passes 11 of 12 Tests
Guided by the Fox workflow ("Follow one representative input through the actual execution path to the observable output. Identify the component that owns the behavior, not merely the public API that exposes it. Cross boundaries when relevant: wrappers to native engines..."):
1. The agent realized that `pydantic-core` serializes directly from model fields.
2. In Trial 4, the agent implemented pre-serialization tree sanitization across all collections (`list`, `tuple`, `set`, `frozenset`, `dict`) and nested models.
3. It computed exact serialization keys against `by_alias`, `serialization_alias`, and exclusion sets.
4. When `model_dump_json()` was invoked, the sanitized model graph was handed to the native serializer, preventing duplicate key emission in the JSON buffer (T9 passed).
5. It maintained object immutability by cloning models during sanitization rather than in-place mutation (T11 passed).

### The Sole Remaining Boundary: T10 (`TypeAdapter`)
The only test that fails across all pure Python patches is T10:
```python
item = Item.model_validate({"X": 5, "x": 99})
adapter = TypeAdapter(Item)
dumped = adapter.dump_python(item)
```
`TypeAdapter` delegates directly to `pydantic-core`'s Rust serializer without ever calling `BaseModel.model_dump()` or `BaseModel.model_dump_json()`. Because the benchmark environment uses precompiled `pydantic-core` binaries, fixing T10 requires modifying and recompiling the Rust codebase (which is what upstream Pydantic PR #12918 ultimately did in `pydantic-core`).

## 4. Key Lessons for Benchmark Design

1. **Benchmark acceptance fixtures must test the library, not isolated scripts**: The initial Task 1 acceptance test only tested direct `model.model_dump()` on a single pre-configured model shape. It did not test `TypeAdapter`, JSON strings, or collection-wrapped models.
2. **Surface-level success can mask architectural workarounds**: An agent instructed to trace boundaries may still choose the path of least resistance if modifying the true architectural layer (Rust) is perceived as too complex. It will write an elaborate Python workaround that passes the immediate check.
3. **Adversarial testing is mandatory**: Without adversarial suites, coding-agent benchmarks systematically reward agents that overfit to provided reproducers.
