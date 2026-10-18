"""
Performance Benchmark: Measure runtime serialization latency and memory allocations.
"""

import gc
import os
import shutil
import subprocess
import time
import tracemalloc
from typing import Dict, List

TEMPLATE_REPO = "/tmp/fox_eval/pydantic_repo"
BENCHMARK_SCRIPT = """
import time
import tracemalloc
import gc
from pydantic import BaseModel, ConfigDict, Field

class SimpleModel(BaseModel):
    model_config = ConfigDict(extra='allow')
    x: int = Field(alias='X')
    y: str = 'hello'

class NestedChild(BaseModel):
    model_config = ConfigDict(extra='allow')
    val: int = Field(alias='VAL')

class NestedRoot(BaseModel):
    model_config = ConfigDict(extra='allow')
    child1: NestedChild
    child2: NestedChild
    extra_field: str = 'root'

def benchmark_flat(n_iterations=5000):
    m = SimpleModel.model_validate({'X': 1, 'x': 2})
    # Warmup
    for _ in range(100):
        _ = m.model_dump()

    gc.collect()
    tracemalloc.start()
    t0 = time.perf_counter()
    for _ in range(n_iterations):
        _ = m.model_dump()
    t1 = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return (t1 - t0) * 1000, peak / 1024  # ms, KB

def benchmark_collection(n_items=1000):
    class Item(BaseModel):
        model_config = ConfigDict(extra='allow')
        val: int = Field(alias='V')
    
    class Container(BaseModel):
        items: list[Item]

    items = [Item.model_validate({'V': i, 'val': i * 2}) for i in range(n_items)]
    c = Container(items=items)

    gc.collect()
    tracemalloc.start()
    t0 = time.perf_counter()
    for _ in range(50):
        _ = c.model_dump()
    t1 = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return (t1 - t0) * 1000, peak / 1024

def benchmark_large_extras(n_extras=500, n_iterations=1000):
    data = {'X': 1, 'x': 2}
    for i in range(n_extras):
        data[f'extra_{i}'] = i
    m = SimpleModel.model_validate(data)

    gc.collect()
    tracemalloc.start()
    t0 = time.perf_counter()
    for _ in range(n_iterations):
        _ = m.model_dump()
    t1 = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return (t1 - t0) * 1000, peak / 1024

flat_time, flat_mem = benchmark_flat()
coll_time, coll_mem = benchmark_collection()
extra_time, extra_mem = benchmark_large_extras()

print(f"RESULT:flat_time={flat_time:.2f},flat_mem={flat_mem:.2f},coll_time={coll_time:.2f},coll_mem={coll_mem:.2f},extra_time={extra_time:.2f},extra_mem={extra_mem:.2f}")
"""


def run_benchmark_on_target(name: str, patch_file: str | None) -> Dict[str, float]:
    workdir = f"/tmp/fox_perf_{name.replace(' ', '_')}"
    if os.path.exists(workdir):
        shutil.rmtree(workdir)

    shutil.copytree(TEMPLATE_REPO, workdir)

    if patch_file and os.path.exists(patch_file):
        subprocess.run(
            ["git", "apply", "--ignore-whitespace", os.path.abspath(patch_file)],
            cwd=workdir,
            capture_output=True,
            text=True
        )

    bench_path = os.path.join(workdir, "bench.py")
    with open(bench_path, "w", encoding="utf-8") as f:
        f.write(BENCHMARK_SCRIPT)

    proc = subprocess.run(
        ["python3", "bench.py"],
        cwd=workdir,
        capture_output=True,
        text=True
    )

    out = proc.stdout + "\n" + proc.stderr
    res = {}
    for line in out.splitlines():
        if line.startswith("RESULT:"):
            parts = line.replace("RESULT:", "").split(",")
            for p in parts:
                k, v = p.split("=")
                res[k] = float(v)

    shutil.rmtree(workdir, ignore_errors=True)
    return res


def main():
    targets = [
        ("Clean (unpatched)", None),
        ("Baseline Trial 2", "HARNESS/patches/task1_pydantic_12884_baseline_trial2.patch"),
        ("Fox v1.0 Trial 2", "HARNESS/patches/task1_pydantic_12884_fox_trial2.patch"),
        ("Fox v1.1 Trial 2", "HARNESS/patches/task1_pydantic_12884_fox_v1.1_trial2.patch"),
        ("Fox v1.1 Trial 3", "HARNESS/patches/task1_pydantic_12884_fox_v1.1_trial3.patch"),
    ]

    print("Running repeatable performance benchmarks (3 runs averaged)...")
    results_table = {}
    for name, patch in targets:
        print(f"  Benchmarking {name}...")
        runs = [run_benchmark_on_target(name, patch) for _ in range(3)]
        avg = {}
        for k in runs[0].keys():
            avg[k] = sum(r[k] for r in runs) / len(runs)
        results_table[name] = avg

    print("\n\n=== PERFORMANCE BENCHMARK RESULTS TABLE ===")
    print("| Target | Flat Model (5k runs) | Peak Mem (KB) | Collection (1k items x 50) | Peak Mem (KB) | 500 Extras (1k runs) | Peak Mem (KB) |")
    print("|---|:---:|:---:|:---:|:---:|:---:|:---:|")
    for name, m in results_table.items():
        print(f"| {name} | {m.get('flat_time', 0):.2f} ms | {m.get('flat_mem', 0):.1f} KB | {m.get('coll_time', 0):.2f} ms | {m.get('coll_mem', 0):.1f} KB | {m.get('extra_time', 0):.2f} ms | {m.get('extra_mem', 0):.1f} KB |")


if __name__ == "__main__":
    main()
