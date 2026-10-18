# Performance and Memory Analysis: Digfox v1.1 Patches

## Executive Summary

To assess whether Digfox v1.1's recursive pre-serialization shims introduce runtime latency or memory bloat, we conducted controlled, repeatable microbenchmarks measuring serialization latency and heap memory allocations across five repository states:
1. Clean Pydantic repository (`v2.13.4`, commit `cf67d4b3`)
2. Baseline Trial 2 patch
3. Digfox v1.0 Trial 2 patch
4. Digfox v1.1 Trial 2 patch (`_model_for_serialization`)
5. Digfox v1.1 Trial 3 patch (`_without_extra_serialization_collisions`)

### Core Findings

1. **Negligible Latency on Small Models**: On flat models and small model graphs, serialization latency across all patches remained within 4.4ms to 4.5ms for 5,000 iterations (<0.001ms per call).
2. **Hidden Flaw Explains Collection Speed**: On collection-wrapped models (1,000 items), Digfox v1.1 exhibited no slowdown (24.96ms vs 25.10ms) solely because its collision scanner failed to inspect list items, bypassing the copy logic entirely (which caused the correctness failure in adversarial test T2).
3. **Algorithmic Inefficiency on Colliding Models**: When extra collisions are present, Digfox v1.1 Trial 3 unconditionally performs a deep graph copy of all dictionaries, lists, and model instances in Python before delegating to `pydantic-core`. This adds an unnecessary `O(V + E)` traversal pass in interpreted Python, allocating duplicate intermediate structures.

## 1. Benchmark Setup

- **Hardware & OS**: macOS, Apple Silicon
- **Runtime**: Python 3.14.7, `pydantic-core 2.46.4`
- **Instrumentation**: `time.perf_counter()` for high-resolution timing, `tracemalloc` for peak heap memory tracing, explicit `gc.collect()` before timed sections, and 100-500 warm-up runs.
- **Scenarios Evaluated**:
  - **Scenario A (Flat Model)**: Model with 2 declared fields, 1 colliding extra field, serialized 5,000 times.
  - **Scenario B (Collection Scaling)**: Container model with 1,000 child models in a list, serialized 50 times.
  - **Scenario C (High-Volume Extras)**: Model with 1 declared field and 500 extra dictionary keys, serialized 1,000 times.

## 2. Empirical Performance Results

| Configuration | Scenario A: Flat Model (5k runs) | Peak Heap (KB) | Scenario B: Collection (1k items x 50) | Peak Heap (KB) | Scenario C: 500 Extras (1k runs) | Peak Heap (KB) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Clean (unpatched)** | 4.39 ms | 0.4 KB | 25.10 ms | 188.1 KB | 19.72 ms | 19.6 KB |
| **Baseline Trial 2** | 4.45 ms | 0.4 KB | 25.20 ms | 188.1 KB | 19.70 ms | 19.6 KB |
| **Digfox v1.0 Trial 2** | 4.46 ms | 0.4 KB | 25.09 ms | 188.1 KB | 19.74 ms | 19.6 KB |
| **Digfox v1.1 Trial 2** | 4.49 ms | 0.4 KB | 24.96 ms | 188.1 KB | 20.25 ms | 19.6 KB |
| **Digfox v1.1 Trial 3** | 4.46 ms | 0.4 KB | 25.01 ms | 188.1 KB | 19.81 ms | 19.6 KB |

## 3. Algorithmic Complexity and Overhead Analysis

### Clean and Baseline: Single Native Pass
In unpatched Pydantic, calling `model.model_dump()` transfers execution immediately across the FFI boundary to `pydantic-core` in Rust:
$$\text{Time} = O(F + E)_{\text{Rust}}$$
where $F$ is the number of declared fields and $E$ is the number of extra fields. All loops execute at native compiled speed without intermediate Python dictionary allocations.

### Digfox v1.1: Double-Pass Python Shim
In Digfox v1.1 Trial 2 and Trial 3:
$$\text{Time} = O(V + E)_{\text{Python}} + O(V + E)_{\text{Rust}}$$
where $V$ is the total count of nested models, collections, and dictionaries.
1. **Pass 1 (Detection & Copy)**: The Python function walks the entire model graph. For every model node, it accesses `__dict__` and `__pydantic_extra__`, constructs new Python dictionaries, and sets attributes on cloned `BaseModel` instances via `_object_setattr()`.
2. **Pass 2 (Native Serialization)**: The cloned model graph is then passed to `pydantic-core`, which walks the entire graph a second time.

### The Collection Invariance Paradox
In Scenario B (Collection of 1,000 models), one would expect the recursive copier in Digfox v1.1 to show measurable latency overhead. The benchmark revealed that Digfox v1.1 ran in 24.96ms, virtually identical to Clean (25.10ms).
Investigation revealed that this parity was not an optimization:
- In `_extra_serialization_collision(c)`, the agent only checked `c.__pydantic_extra__`.
- Because the root container had no extra fields, the preprocessor evaluated to `False` and returned `c` without touching `c.items`.
- Thus, the preprocessor ran in $O(1)$ by failing to inspect the collection, causing the correctness regression in adversarial test T2 while maintaining deceptive performance parity.

## 4. Conclusion

The Python-level recursive shims in Digfox v1.1 do not cause noticeable latency degradation on toy models. However, they represent an architecturally flawed compromise:
1. They add redundant Python-level object cloning on colliding paths.
2. They achieve apparent performance neutrality on collections only because their traversal logic is buggy and skips nested structures in lists.
3. A true zero-overhead fix belongs in `pydantic-core`'s native serializer, where field tracking can occur in-place during the single native serialization pass.
