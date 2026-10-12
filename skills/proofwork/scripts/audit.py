#!/usr/bin/env python3
"""Audit declarative structure, not the quality of AI outcomes (stdlib-only)."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def audit(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not path.is_dir():
        return [f"Workspace does not exist: {path}"], warnings
    for name in ("OUTCOME.md", "WORKFLOW.md", "REVIEW.md", "workflow.json", "config/POLICY.md"):
        if not (path / name).is_file():
            errors.append(f"Missing {name}")
    manifest = path / "workflow.json"
    if not manifest.is_file():
        return errors, warnings
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        return errors + [f"Invalid workflow.json: {exc}"], warnings
    if not isinstance(data, dict):
        return errors + ["workflow.json must contain an object"], warnings
    stages = data.get("stages")
    if not isinstance(stages, list) or not stages:
        return errors + ["stages must be a non-empty list"], warnings
    if any(not isinstance(s, str) or not re.fullmatch(r"\d\d-[a-z][a-z0-9-]*", s) for s in stages):
        errors.append("All stages must be NN-lowercase-name strings")
        return errors, warnings
    if len(set(stages)) != len(stages):
        errors.append("Duplicate stage names")
    if stages != sorted(stages):
        errors.append("Stage entries out of order")
    for stage in stages:
        contract = path / "stages" / stage / "CONTRACT.md"
        if not contract.is_file():
            errors.append(f"Missing stages/{stage}/CONTRACT.md")
            continue
        text = contract.read_text(encoding="utf-8")
        for heading in ("## Purpose", "## Inputs", "## Executor", "## Steps", "## Output", "## Acceptance", "## Review and stop conditions"):
            if heading not in text:
                errors.append(f"stages/{stage}/CONTRACT.md lacks {heading}")
        if "<run-id>" in text or "One responsibility" in text:
            warnings.append(f"Stage {stage} still contains template placeholders")
    outcome = path / "OUTCOME.md"
    if outcome.is_file() and "Define the observable" in outcome.read_text(encoding="utf-8"):
        warnings.append("OUTCOME.md is still a blank template")
    if not (path / "runs").is_dir():
        errors.append("Missing runs/ directory")
    else:
        run_files = [p for p in (path / "runs").rglob("*") if p.is_file() and p.name != ".gitkeep"]
        if not run_files:
            warnings.append("No run artifacts found; end-to-end execution not verified")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    errors, warnings = audit(args.workspace)
    for err in errors:
        print(f"ERROR: {err}")
    for warning in warnings:
        print(f"WARN: {warning}")
    print(f"Structure audit: {len(errors)} errors, {len(warnings)} warnings")
    print("Note: this does not validate task execution or factual correctness.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
