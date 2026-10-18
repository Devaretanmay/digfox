"""
Run adversarial evaluation of all agent patches against task1_adversarial_suite.py.
"""

import os
import shutil
import subprocess
from typing import Dict, List, Tuple

TEMPLATE_REPO = "/tmp/fox_eval/pydantic_repo"
ADVERSARIAL_SUITE = os.path.abspath("HARNESS/fixtures/task1_adversarial_suite.py")
PATCHES_DIR = "HARNESS/patches"


def evaluate_patch(name: str, patch_file: str | None) -> Dict[str, any]:
    workdir = f"/tmp/fox_adversarial_{name}"
    if os.path.exists(workdir):
        shutil.rmtree(workdir)

    shutil.copytree(TEMPLATE_REPO, workdir)

    # Apply patch if provided
    patch_applied = True
    patch_err = ""
    if patch_file and os.path.exists(patch_file):
        with open(patch_file, "r", encoding="utf-8") as pf:
            patch_content = pf.read()
        if "diff --git a/tests/pydantic_core" in patch_content:
            patch_content = patch_content.split("diff --git a/tests/pydantic_core")[0]
        res = subprocess.run(
            ["git", "apply", "--ignore-whitespace", "-"],
            input=patch_content,
            cwd=workdir,
            capture_output=True,
            text=True
        )
        if res.returncode != 0:
            patch_applied = False
            patch_err = res.stderr

    # Copy adversarial suite into workspace
    suite_dest = os.path.join(workdir, "test_adversarial.py")
    shutil.copy(ADVERSARIAL_SUITE, suite_dest)

    # Run adversarial test suite
    test_proc = subprocess.run(
        ["python3", "-m", "unittest", "-v", "test_adversarial.py"],
        cwd=workdir,
        capture_output=True,
        text=True
    )

    output = test_proc.stdout + "\n" + test_proc.stderr

    # Parse individual test results
    tests = [
        "test_01_deeply_nested_models",
        "test_02_models_in_collections",
        "test_03_shared_object_identity",
        "test_04_recursive_structures",
        "test_05_custom_field_serializers",
        "test_06_computed_fields",
        "test_07_nested_include_exclude_filtering",
        "test_08_validation_alias_vs_serialization_alias",
        "test_09_model_dump_json_no_duplicate_keys",
        "test_10_direct_typeadapter_serialization",
        "test_11_model_immutability",
        "test_12_high_volume_extras_scalability",
    ]

    import re
    results = {}
    for t in tests:
        if re.search(rf"{t}\s*\([^)]*\)\s*\n[^\n]*\.\.\. ok", output):
            results[t] = "PASS"
        else:
            results[t] = "FAIL"

    total_passed = sum(1 for v in results.values() if v == "PASS")

    # Clean up workspace
    shutil.rmtree(workdir, ignore_errors=True)

    return {
        "name": name,
        "patch_applied": patch_applied,
        "patch_err": patch_err,
        "passed_count": total_passed,
        "total_count": len(tests),
        "results": results,
        "raw_output": output
    }


def main():
    targets = [
        ("Clean (unpatched)", None),
        ("Baseline Trial 1", "HARNESS/patches/task1_pydantic_12884_baseline_trial1.patch"),
        ("Baseline Trial 2", "HARNESS/patches/task1_pydantic_12884_baseline_trial2.patch"),
        ("Baseline Trial 3", "HARNESS/patches/task1_pydantic_12884_baseline_trial3.patch"),
        ("Fox v1.0 Trial 1", "HARNESS/patches/task1_pydantic_12884_fox_trial1.patch"),
        ("Fox v1.0 Trial 2", "HARNESS/patches/task1_pydantic_12884_fox_trial2.patch"),
        ("Fox v1.0 Trial 3", "HARNESS/patches/task1_pydantic_12884_fox_trial3.patch"),
        ("Fox v1.1 Trial 1", "HARNESS/patches/task1_pydantic_12884_fox_v1.1_trial1.patch"),
        ("Fox v1.1 Trial 2", "HARNESS/patches/task1_pydantic_12884_fox_v1.1_trial2.patch"),
        ("Fox v1.1 Trial 3", "HARNESS/patches/task1_pydantic_12884_fox_v1.1_trial3.patch"),
        ("Fox v1.1 Trial 4", "HARNESS/patches/task1_pydantic_12884_fox_v1.1_trial4.patch"),
        ("Fox v1.1 Trial 5", "HARNESS/patches/task1_pydantic_12884_fox_v1.1_trial5.patch"),
        ("Fox v1.1 Trial 6", "HARNESS/patches/task1_pydantic_12884_fox_v1.1_trial6.patch"),
    ]

    all_res = []
    for name, patch in targets:
        print(f"Evaluating {name}...")
        res = evaluate_patch(name, patch)
        all_res.append(res)
        print(f"  Passed: {res['passed_count']}/{res['total_count']}")

    print("\n\n=== ADVERSARIAL EVALUATION RESULTS TABLE ===")
    test_keys = [
        ("T1: Deeply Nested", "test_01_deeply_nested_models"),
        ("T2: Collections", "test_02_models_in_collections"),
        ("T3: Shared Identity", "test_03_shared_object_identity"),
        ("T4: Recursive Structs", "test_04_recursive_structures"),
        ("T5: Custom Serializers", "test_05_custom_field_serializers"),
        ("T6: Computed Fields", "test_06_computed_fields"),
        ("T7: Include/Exclude", "test_07_nested_include_exclude_filtering"),
        ("T8: Dual Aliases", "test_08_validation_alias_vs_serialization_alias"),
        ("T9: Raw JSON Keys", "test_09_model_dump_json_no_duplicate_keys"),
        ("T10: TypeAdapter", "test_10_direct_typeadapter_serialization"),
        ("T11: Immutability", "test_11_model_immutability"),
        ("T12: Scalability 500x", "test_12_high_volume_extras_scalability"),
    ]

    header = ["Target", "Score"] + [k[0] for k in test_keys]
    print("| " + " | ".join(header) + " |")
    print("| " + " | ".join(["---"] * len(header)) + " |")
    for r in all_res:
        row = [r["name"], f"{r['passed_count']}/{r['total_count']}"]
        for _, tk in test_keys:
            row.append(r["results"].get(tk, "FAIL"))
        print("| " + " | ".join(row) + " |")


if __name__ == "__main__":
    main()
