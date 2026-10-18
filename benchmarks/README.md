# Digfox Real-World Benchmark Suite

This directory contains standalone benchmark fixtures for evaluating AI coding agents on real-world open-source defects.

Each task fixture reproduces a real GitHub issue with executable reproduction scripts, regression tests, and evaluation harnesses.

---

## Benchmark directory structure

```
benchmarks/
  README.md
  task1_pydantic_12884/
    TASK.md               # Task specification and acceptance criteria
    reproduce_issue.py    # Standalone reproduction script
    test_solution.py      # Automated regression test suite
    case/                 # Verified Digfox evidence ledger for this task
```

---

## Benchmark tasks

1. `task1_pydantic_12884`: Fix alias and extra-field collision overwrite during serialization (`pydantic/pydantic#12884`).
2. `task2_pydantic_13734`: Fix object serialization exception for mock.call objects (`pydantic/pydantic#13734`).
3. `task3_ruff_28861`: Fix linter autofix regression introducing F401 violations (`astral-sh/ruff#28861`).
4. `task4_ruff_28866`: Preserve code comments during PLR1711 useless-return autofix (`astral-sh/ruff#28866`).
5. `task5_setup_uv_1028`: Fix GitHub Action warning on renamed error class (`astral-sh/setup-uv#1028`).
6. `task6_uv_18533`: Investigate dependency resolver constraint version selection (`astral-sh/uv#18533`).

---

## How to run fixtures

To run the Task 1 reproduction script:
```bash
python3 benchmarks/task1_pydantic_12884/reproduce_issue.py
```

To run the Task 1 test suite:
```bash
python3 -m unittest benchmarks/task1_pydantic_12884/test_solution.py
```

To inspect the Task 1 Digfox evidence ledger:
```bash
python3 skills/digfox/scripts/proof.py check benchmarks/task1_pydantic_12884/case
python3 skills/digfox/scripts/proof.py report benchmarks/task1_pydantic_12884/case
```
