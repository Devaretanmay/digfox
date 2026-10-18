# Adversarial Acceptance Testing: Pydantic Serialization Collision

## Executive Summary

To rigorously evaluate whether the Digfox v1.1 patches resolved Pydantic issue #12884 or merely satisfied the initial benchmark fixture, we designed an independent 12-point adversarial test suite (`HARNESS/fixtures/task1_adversarial_suite.py`).

The suite was executed across ten separate configurations:
1. Clean Pydantic repository (`v2.13.4`, commit `cf67d4b3`)
2. Baseline Trials 1, 2, 3
3. Digfox v1.0 Trials 1, 2, 3
4. Digfox v1.1 Trials 1, 2, 3

### Core Empirical Finding

- **Clean Pydantic**: Passed 0 / 12 (demonstrating all 12 tests actively exercise the defect).
- **Baseline (all 3 trials)**: Passed 0 / 12.
- **Digfox v1.0 (all 3 trials)**: Passed 0 / 12.
- **Digfox v1.1 Trial 1**: Passed 0 / 12.
- **Digfox v1.1 Trial 2**: Passed 1 / 12 (passed only basic immutability; failed 11 / 12).
- **Digfox v1.1 Trial 3**: Passed 1 / 12 (passed only basic immutability; failed 11 / 12).

Both "passing" Digfox v1.1 patches failed 91.7% of adversarial tests.

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
| **Clean (unpatched)** | 0 / 12 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| **Baseline Trial 1** | 0 / 12 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| **Baseline Trial 2** | 0 / 12 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| **Baseline Trial 3** | 0 / 12 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| **Digfox v1.0 Trial 1** | 0 / 12 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| **Digfox v1.0 Trial 2** | 0 / 12 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| **Digfox v1.0 Trial 3** | 0 / 12 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| **Digfox v1.1 Trial 1** | 0 / 12 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| **Digfox v1.1 Trial 2** | 1 / 12 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | PASS | FAIL |
| **Digfox v1.1 Trial 3** | 1 / 12 | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | PASS | FAIL |

## 3. Failure Mode Analysis for Digfox v1.1 Patches

### Failure 1: Complete Bypass via TypeAdapter (T10)
When users serialize models using Pydantic's official `TypeAdapter`:
```python
item = Item.model_validate({"X": 5, "x": 99})
adapter = TypeAdapter(Item)
dumped = adapter.dump_python(item)
```
`TypeAdapter` calls the underlying `pydantic-core` schema serializer directly. It does not invoke `BaseModel.model_dump()`.
In both Trial 2 and Trial 3 patches, `dumped["x"]` evaluated to `99` instead of `5`. The fix was completely absent from this primary Pydantic API path.

### Failure 2: Duplicate JSON Key Emissions (T9)
When serializing to JSON via `model.model_dump_json()`:
```python
model = RawJsonModel.model_validate({"X": 10, "x": 20})
raw_json = model.model_dump_json()
```
The Rust serializer in `pydantic-core` wrote both `"x": 10` and `"x": 20` into the emitted JSON buffer. Both patches produced JSON strings with duplicate keys: `{"x":10,"x":20}`.

### Failure 3: Missing Child Models in Collections (T2)
When child models are stored inside lists, tuples, or dictionary values:
```python
container = Container(items_list=[Item(code="A", ...)])
container.model_dump()
```
Because `Container` itself had no colliding extras, the agent's preprocessor (`_extra_serialization_collision`) evaluated to `False` at the container level. The preprocessor skipped inspecting list contents, handing the raw container to `pydantic-core`. The Rust serializer serialized the child models directly, triggering the extra-field overwrite inside every list element (`'ERR_A' != 'A'`).

### Failure 4: Alias Resolution Breakdown (T1, T8, T12)
Both patches attempted to compute whether an extra key collides by evaluating:
```python
use_alias = by_alias if by_alias is not None else model.model_config.get('serialize_by_alias', False)
```
When `model_dump()` was called without `by_alias=True`, the code looked only for collisions against declared Python field names, failing to protect fields that had validation aliases or distinct serialization aliases.

## 4. Key Lessons for Benchmark Design

1. **Benchmark acceptance fixtures must test the library, not isolated scripts**: The initial Task 1 acceptance test only tested direct `model.model_dump()` on a single pre-configured model shape. It did not test `TypeAdapter`, JSON strings, or collection-wrapped models.
2. **Surface-level success can mask architectural workarounds**: An agent instructed to trace boundaries may still choose the path of least resistance if modifying the true architectural layer (Rust) is perceived as too complex. It will write an elaborate Python workaround that passes the immediate check.
3. **Adversarial testing is mandatory**: Without adversarial suites, coding-agent benchmarks systematically reward agents that overfit to provided reproducers.
