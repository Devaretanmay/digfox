#!/usr/bin/env python3
"""Build REA CLI JSON requests from complete stored Evidence envelopes.

These payloads match public example schemas reviewed in October 2026.
Always compare with the installed REA command's help/schema.
"""
import argparse
import json
from pathlib import Path
import sys


def evidence(path):
    with open(path, encoding='utf-8') as f:
        obj = json.load(f)
    if not isinstance(obj, dict) or 'normalized_result' not in obj:
        raise ValueError(f'Not a complete REA Evidence envelope: {path}')
    return obj


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='task', required=True)
    tr = sub.add_parser('trace'); tr.add_argument('source', type=Path)
    tr.add_argument('--seed-kind', default='string'); tr.add_argument('--seed-value', required=True)
    tr.add_argument('--direction', choices=['both','forward','backward'], default='both')
    co = sub.add_parser('compare'); co.add_argument('left', type=Path); co.add_argument('right', type=Path)
    vw = sub.add_parser('view'); vw.add_argument('source', type=Path)
    vw.add_argument('--kind', choices=['summary','page'], default='summary')
    vw.add_argument('--collection', default='modules'); vw.add_argument('--offset', type=int, default=0)
    vw.add_argument('--limit', type=int, default=32)
    args = ap.parse_args()
    try:
        if args.task == 'trace':
            payload = {'application': evidence(args.source), 'seed': {'kind': args.seed_kind, 'value': args.seed_value}, 'direction': args.direction}
        elif args.task == 'compare':
            if args.left.resolve() == args.right.resolve():
                raise ValueError('Compare needs distinct left and right files')
            payload = {'left': evidence(args.left), 'right': evidence(args.right)}
        else:
            view = {'kind': 'summary'} if args.kind == 'summary' else {'kind': 'page', 'collection': args.collection, 'offset': args.offset, 'limit': args.limit}
            payload = {'source': {'kind':'inline', 'evidence': evidence(args.source)}, 'view': view}
        json.dump(payload, sys.stdout, ensure_ascii=False); print()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        ap.error(str(exc))

if __name__ == '__main__':
    main()
