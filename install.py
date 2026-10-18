#!/usr/bin/env python3
"""Install the Fox agent skill into an agent workspace."""
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

AGENTS = {
    "codex": ".agents/skills",
    "claude": ".claude/skills",
    "cursor": ".cursor/skills",
}
ROOT = Path(__file__).resolve().parent


def install(agent: str, project: Path, force: bool = False, dry_run: bool = False) -> list[Path]:
    if agent not in AGENTS:
        raise ValueError(f"Unknown agent '{agent}'; choose from: {', '.join(AGENTS.keys())}")
    project = project.expanduser().resolve()
    if not project.is_dir():
        raise ValueError(f"Project directory must exist: {project}")

    source = ROOT / "skills" / "fox"
    target_dir = project / AGENTS[agent]
    dest = target_dir / "fox"

    if not (source / "SKILL.md").is_file():
        raise ValueError(f"Incomplete source: {source}")
    if source == dest or dest.is_relative_to(source):
        raise ValueError("Cannot install inside a source skill")
    if dest.exists() and not force:
        raise FileExistsError(f"{dest} already exists; pass --force to replace")
    if dest.is_symlink():
        raise ValueError(f"Refusing to replace symlink: {dest}")

    if dry_run:
        print(f"WOULD INSTALL {source} -> {dest}")
        return [dest]

    target_dir.mkdir(parents=True, exist_ok=True)
    # Staging copy avoids half-copied installs.
    stage = Path(tempfile.mkdtemp(prefix=".fox-stage-", dir=target_dir))
    backup = None
    try:
        shutil.rmtree(stage)
        shutil.copytree(
            source,
            stage,
            symlinks=False,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
        if dest.exists():
            backup = Path(tempfile.mkdtemp(prefix=".fox-backup-", dir=target_dir))
            shutil.rmtree(backup)
            dest.rename(backup)
        stage.rename(dest)
        if backup and backup.exists():
            shutil.rmtree(backup)
    except BaseException:
        if dest.exists():
            shutil.rmtree(dest)
        if backup and backup.exists():
            backup.rename(dest)
        raise
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return [dest]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--agent",
        required=True,
        choices=AGENTS,
        help="Target agent environment (codex, claude, cursor)",
    )
    p.add_argument(
        "--project",
        type=Path,
        default=Path.cwd(),
        help="Target project root directory (default: current directory)",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Replace existing skill installation",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned installation without modifying files",
    )
    args = p.parse_args(argv)
    try:
        dests = install(args.agent, args.project, args.force, args.dry_run)
        if not args.dry_run:
            for dest in dests:
                print("INSTALLED: " + str(dest))
            print("Invoke: /fox")
        return 0
    except (ValueError, FileExistsError, OSError) as ex:
        print("ERROR: " + str(ex), file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
