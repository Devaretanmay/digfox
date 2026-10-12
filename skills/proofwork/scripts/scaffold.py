#!/usr/bin/env python3
"""Create a minimal, inspectable workflow workspace (stdlib-only)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_DIR / "assets"
SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


def safe_path(value: str) -> Path:
    path = Path(value).expanduser()
    if path == Path("/") or path.resolve() == Path.home().resolve():
        raise ValueError("Refusing to write at filesystem or home root")
    return path


def render(filename: str, replacements: dict[str, str]) -> str:
    result = (TEMPLATES / filename).read_text(encoding="utf-8")
    for key, value in replacements.items():
        result = result.replace("{{" + key + "}}", value)
    return result


def scaffold(name: str, output: Path, stages: list[str]) -> Path:
    if not SLUG.fullmatch(name):
        raise ValueError("Workflow name must be a lowercase slug: example weekly-report")
    if not 1 <= len(stages) <= 8:
        raise ValueError("Provide between 1 and 8 stages")
    if len(set(stages)) != len(stages) or any(not SLUG.fullmatch(s) for s in stages):
        raise ValueError("Stages must be unique lowercase slugs")
    workspace = (output / name).resolve()
    if workspace.exists():
        raise FileExistsError(f"Refusing to overwrite existing path: {workspace}")
    workspace.mkdir(parents=True)
    try:
        (workspace / "OUTCOME.md").write_text(render("OUTCOME.md", {"NAME": name}), encoding="utf-8")
        (workspace / "REVIEW.md").write_text(render("REVIEW.md", {"NAME": name}), encoding="utf-8")
        (workspace / "stages").mkdir()
        for i, stage in enumerate(stages, 1):
            stage_id = f"{i:02d}-{stage}"
            folder = workspace / "stages" / stage_id
            folder.mkdir()
            (folder / "CONTRACT.md").write_text(render("STAGE.md", {
                "STAGE_ID": stage_id, "STAGE_NAME": stage.replace("-", " ").title()
            }), encoding="utf-8")
        (workspace / "runs").mkdir()
        (workspace / "runs" / ".gitkeep").write_text("", encoding="utf-8")
        (workspace / "config").mkdir()
        (workspace / "config" / "POLICY.md").write_text(
            "# Workflow policy\n\nStable preferences and allowed sources go here. "
            "Do not include secrets. External actions require approval.\n", encoding="utf-8")
        (workspace / "WORKFLOW.md").write_text(
            f"# {name}\n\nStart by completing `OUTCOME.md`.\n\n"
            "Run each stage using its `CONTRACT.md`; only load declared inputs. "
            "Save actual output under `runs/<run-id>/<stage-id>/`. "
            "Review outputs before moving to the next stage.\n\n"
            "## Ordered stages\n\n"
            + "".join(f"{i}. `stages/{i:02d}-{stage}/CONTRACT.md`\n" for i, stage in enumerate(stages, 1))
            + "\n## Verification\n\n"
            "Complete all acceptance criteria, then capture execution evidence in `REVIEW.md`. "
            "`audit.py` checks structure only, not task correctness.\n", encoding="utf-8")
        (workspace / ".gitignore").write_text("runs/*\n!runs/.gitkeep\n.env\n*.key\n", encoding="utf-8")
        (workspace / "workflow.json").write_text(json.dumps({
            "name": name, "version": 1,
            "stages": [f"{i:02d}-{stage}" for i, stage in enumerate(stages, 1)],
            "requires_approval_for": ["publish", "email", "spend", "delete", "deploy", "sensitive-data-sharing"]
        }, indent=2) + "\n", encoding="utf-8")
    except BaseException:
        # Never leave a half-created workspace after failure.
        import shutil
        shutil.rmtree(workspace)
        raise
    return workspace


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="Lowercase workflow slug")
    parser.add_argument("--output", type=safe_path, default=Path.cwd(), help="Parent output directory")
    parser.add_argument("--stages", default="collect,produce,verify", help="Comma-separated stage names")
    args = parser.parse_args(argv)
    try:
        stages = [s.strip() for s in args.stages.split(",")]
        print(scaffold(args.name, args.output, stages))
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"scaffold: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
