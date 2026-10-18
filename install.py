#!/usr/bin/env python3
"""Install Fox, optionally alongside the original REA Investigator skill."""
from __future__ import annotations
import argparse
import os
import shutil
import tempfile
from pathlib import Path

AGENTS = {"codex": ".agents/skills", "claude": ".claude/skills", "cursor": ".cursor/skills"}
ROOT = Path(__file__).resolve().parent


def find_rea(root: Path) -> Path:
    root = root.expanduser().resolve()
    options = (root / "skills" / "rea-investigate", root / "rea-investigate")
    for path in options:
        if (path / "SKILL.md").is_file() and (path / "scripts" / "case.py").is_file():
            return path
    raise ValueError("REA source must be its local repository root or the rea-investigate skill folder")


def install(agent: str, project: Path, rea_path: Path | None = None, force: bool = False, dry_run: bool = False) -> list[Path]:
    if agent not in AGENTS:
        raise ValueError("Unknown agent; use codex, claude, or cursor")
    project = project.expanduser().resolve()
    if not project.is_dir():
        raise ValueError(f"Project directory must exist: {project}")
    src = ROOT / "skills" / "fox"
    sources = [(src, "fox")]
    if rea_path is not None:
        sources.append((find_rea(rea_path), "rea-investigate"))
    target_dir = project / AGENTS[agent]
    dests = [target_dir / name for _, name in sources]
    for source, dest in zip((x[0] for x in sources), dests):
        if not (source / "SKILL.md").is_file():
            raise ValueError(f"Incomplete source: {source}")
        if source == dest or dest.is_relative_to(source):
            raise ValueError("Cannot install inside a source skill")
        if dest.exists() and not force:
            raise FileExistsError(f"{dest} already exists; choose --force to replace")
        if dest.is_symlink():
            raise ValueError(f"Refusing to replace symlink: {dest}")
    if dry_run:
        for (source, _), dest in zip(sources, dests):
            print(f"WOULD INSTALL {source} -> {dest}")
        return dests
    target_dir.mkdir(parents=True, exist_ok=True)
    # Prepare all copies first. Renaming on the destination filesystem avoids half-copied installs.
    staged = []
    backups = []
    installed = []
    try:
        for source, name in sources:
            stage = Path(tempfile.mkdtemp(prefix=f".{name}-stage-", dir=target_dir))
            staged.append(stage)
            shutil.rmtree(stage)
            shutil.copytree(source, stage, symlinks=False,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
        for stage, dest in zip(staged, dests):
            if dest.exists():
                backup = Path(tempfile.mkdtemp(prefix=f".{dest.name}-backup-", dir=target_dir))
                shutil.rmtree(backup)
                dest.rename(backup)
                backups.append((dest, backup))
            stage.rename(dest)
            installed.append(dest)
        for _, backup in backups:
            shutil.rmtree(backup)
    except BaseException:
        for dest in installed:
            if dest.exists():
                shutil.rmtree(dest)
        for dest, backup in reversed(backups):
            if backup.exists():
                backup.rename(dest)
        raise
    finally:
        for stage in staged:
            if stage.exists():
                shutil.rmtree(stage)
    return dests


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--agent", required=True, choices=AGENTS)
    p.add_argument("--project", type=Path, default=Path.cwd())
    p.add_argument("--rea-path", type=Path, help="Optional local REA Investigator repository (original skill is preserved)")
    p.add_argument("--force", action="store_true", help="Explicitly replace existing skills after staged copy")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    try:
        dests = install(args.agent, args.project, args.rea_path, args.force, args.dry_run)
        if not args.dry_run:
            for dest in dests: print("INSTALLED: " + str(dest))
            print("Invoke: /fox (and /rea-investigate if included)")
        return 0
    except (ValueError, FileExistsError, OSError) as ex:
        print("ERROR: " + str(ex), file=__import__("sys").stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
