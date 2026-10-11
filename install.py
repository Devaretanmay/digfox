#!/usr/bin/env python3
"""Install the ONE rea-investigate Agent Skill into a local Claude Code or Codex project."""
import argparse
from pathlib import Path
import shutil
import sys


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--agent', choices=('codex','claude'), required=True)
    ap.add_argument('--project',type=Path,default=Path.cwd())
    ap.add_argument('--dry-run',action='store_true')
    ap.add_argument('--force',action='store_true',help='Replace existing destination skill after explicit opt-in')
    args=ap.parse_args()
    src=Path(__file__).resolve().parent/'skills'/'rea-investigate'
    dest=(args.project.expanduser().resolve() / ('.agents/skills' if args.agent=='codex' else '.claude/skills') / 'rea-investigate')
    if not (src/'SKILL.md').is_file(): ap.error('Bundled skill missing')
    if dest.exists() and not args.force:
        ap.error(f'Destination exists: {dest}. Use --force only if you intend to replace it.')
    print(f'{"WOULD INSTALL" if args.dry_run else "INSTALL"}: {src} → {dest}')
    if args.dry_run: return
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists(): shutil.rmtree(dest)
    shutil.copytree(src,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store'))
    print(f'Installed one skill at {dest}\nInvoke: /rea-investigate')

if __name__=='__main__':
    main()
