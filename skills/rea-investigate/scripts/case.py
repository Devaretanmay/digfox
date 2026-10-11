#!/usr/bin/env python3
"""REA investigate case ledger, claim provenance, report writer and structural auditor.

Standard-library only.  Does not run REA or execute the target.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

STAGES = {
    'S01': 'Question and scope',
    'S02': 'Artifact map',
    'S03': 'JS/Electron feature trace',
    'S04': 'Browser observation',
    'S05': 'Network reconstruction',
    'S06': 'Native function analysis',
    'S07': 'Android package analysis',
    'S08': '.NET analysis',
    'S09': 'Process capture',
    'S10': 'Build/version comparison',
    'S11': 'Behavioral reconstruction',
    'S12': 'Adversarial evidence audit',
    'S13': 'Firmware inventory',
}
NOTES_REQUIRED = ('overview','architecture','trace','verification','limitations','audit')
NOTES_OPTIONAL = ('network', 'version-diff', 'implementation', 'appendix')
STATUSES = ('pending', 'done', 'not-applicable', 'blocked')
CLASSES = ('observation', 'static-inference', 'runtime-inference', 'hypothesis')
KINDS = ('static', 'runtime', 'capture', 'artifact', 'test', 'document')


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')


def hash_file(path: Path) -> str:
    dig = hashlib.sha256()
    with path.open('rb') as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b''):
            dig.update(chunk)
    return dig.hexdigest()


def identify(target: str) -> dict:
    if urlsplit(target).scheme in ('http', 'https') and urlsplit(target).netloc:
        return {'kind':'url', 'value':target, 'sha256': None,
                'note':'URL supplied but not fetched. Observe content to establish its identity.'}
    path = Path(target).expanduser().resolve()
    if not path.exists():
        return {'kind':'unavailable', 'value':str(path), 'sha256': None,
                'note':'Local path not available during case initialization.'}
    if path.is_file():
        return {'kind':'file', 'value':str(path), 'sha256': hash_file(path), 'size':path.stat().st_size}
    if path.is_dir():
        # A reproducible digest of *file content and relative path*, not an inode or mtime.
        dig = hashlib.sha256(); files = 0; symlinks = 0; total = 0
        for item in sorted(path.rglob('*')):
            if item.is_symlink():
                symlinks += 1; continue
            if not item.is_file():
                continue
            rel = item.relative_to(path).as_posix(); blob = hash_file(item)
            dig.update(rel.encode('utf-8',errors='replace')+b'\x00'+blob.encode('ascii')+b'\n')
            files += 1; total += item.stat().st_size
        return {'kind':'directory', 'value':str(path), 'sha256':dig.hexdigest(),
                'file_count': files, 'symlinks_skipped': symlinks, 'total_bytes':total,
                'note':'Sorted relative-path and file-content digest, with symlinks skipped.'}
    return {'kind':'other', 'value':str(path), 'sha256':None}


def save(path: Path, doc: dict) -> None:
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def load(root: Path) -> dict:
    with (root / 'case.json').open(encoding='utf-8') as f:
        obj = json.load(f)
    if obj.get('format_version') != 1 or set(obj.get('stages',{})) != set(STAGES):
        raise ValueError('Invalid or unsupported case ledger')
    return obj


def init(args):
    root = args.out.expanduser().resolve()
    if root.exists() and any(root.iterdir()):
        raise ValueError(f'Output directory is not empty: {root}')
    ident = identify(args.target)
    additional = [identify(t) for t in args.additional_target]
    root.mkdir(parents=True, exist_ok=True)
    (root/'evidence').mkdir(exist_ok=True)
    (root/'notes').mkdir(exist_ok=True)
    for note in (*NOTES_REQUIRED, *NOTES_OPTIONAL):
        (root/'notes'/f'{note}.md').touch(exist_ok=True)
    (root/'evidence'/'target-identity.json').write_text(json.dumps(ident,indent=2)+'\n',encoding='utf-8')
    record = {'id':'E0001', 'stage':'S01','file':'evidence/target-identity.json',
              'sha256':hash_file(root/'evidence'/'target-identity.json'), 'kind':'artifact',
              'locator':'/', 'summary':'Target supplied to the investigation and its initial local identity',
              'created_at':now()}
    extra_records=[]
    for index, item in enumerate(additional, start=1):
        file = root/'evidence'/f'additional-target-{index}-identity.json'
        file.write_text(json.dumps(item,indent=2)+'\n', encoding='utf-8')
        extra_records.append({'id':f'E{index+1:04d}', 'stage':'S10',
                  'file':f'evidence/additional-target-{index}-identity.json',
                  'sha256':hash_file(file), 'kind':'artifact', 'locator':'/',
                  'summary':f'Identity of additional target {index} (not a comparison result)',
                  'created_at':now()})
    doc = {'format_version':1,'created_at':now(),'updated_at':now(),
           'target':args.target,'question':args.question,'authorization':args.authorization,
           'target_identity':ident,'additional_target_identities':additional,'stages':{sid:{'name':name, 'status':'pending', 'reason':''} for sid,name in STAGES.items()},
           'evidence':[record, *extra_records],'claims':[], 'tool_versions':{}}
    save(root/'case.json', doc)
    print(f'Created {root}\nNext: record scope/authorization, plan 13 stages and collect Evidence.')


def stage(args):
    root = args.case_dir.resolve(); obj = load(root)
    previous = obj['stages'][args.id]['status']
    if args.status in ('blocked','not-applicable') and not args.reason.strip():
        raise ValueError(f'{args.status} requires a concrete --reason')
    if args.status == 'done' and args.id not in ('S12',) and not any(e['stage']==args.id for e in obj['evidence']):
        raise ValueError(f'Cannot complete {args.id} without registered Evidence')
    obj['stages'][args.id] = {'name':STAGES[args.id],'status':args.status, 'reason':args.reason.strip()}
    obj['updated_at']=now(); save(root/'case.json',obj)
    print(f'{args.id}: {previous} → {args.status}')


def source(args):
    root=args.case_dir.resolve(); obj=load(root)
    src=args.file.expanduser().resolve()
    if not src.is_relative_to(root):
        raise ValueError('Store a safe, redacted Evidence copy inside the case directory before registering')
    if not src.is_file() or src.is_symlink():
        raise ValueError('Registered Evidence must be a regular existing file, not a symlink')
    if src.name=='case.json' or src.name=='REPORT.md':
        raise ValueError('Do not register the generated ledger or report as independent source Evidence')
    rel=src.relative_to(root).as_posix()
    if rel not in [e['file'] for e in obj['evidence']]:
        evid = f'E{len(obj["evidence"])+1:04d}'
        obj['evidence'].append({'id':evid,'stage':args.stage,'file':rel,
             'sha256':hash_file(src),'kind':args.kind,'locator':args.locator,
             'summary':args.summary,'created_at':now()})
        obj['updated_at']=now();save(root/'case.json',obj); print(f'{evid} {rel}')
    else:
        raise ValueError(f'The source {rel} already exists; register distinct extractions under unique files')


def claim(args):
    root=args.case_dir.resolve(); obj=load(root)
    ev_ids=set(args.evidence or [])
    known={e['id'] for e in obj['evidence']}
    if not ev_ids.issubset(known):
        raise ValueError('Unknown evidence IDs: '+', '.join(sorted(ev_ids-known)))
    if args.classification != 'hypothesis' and not ev_ids:
        raise ValueError('Supported claims must cite one or more Evidence IDs')
    item={'id':f'C{len(obj["claims"])+1:04d}', 'text':args.text.strip(),
          'class':args.classification, 'evidence':sorted(ev_ids), 'locator':args.locator,
          'counterexample':args.counterexample.strip()}
    if len(item['text'])<8:
        raise ValueError('Claims need a meaningful statement')
    obj['claims'].append(item); obj['updated_at']=now(); save(root/'case.json',obj)
    print(f'{item["id"]}: {item["text"]}')


def note_contents(root:Path, name:str)->str:
    p=root/'notes'/f'{name}.md'
    return p.read_text(encoding='utf-8').strip() if p.exists() else ''


def issues(root:Path, obj:dict)->list[str]:
    problems=[]
    for sid, stage_ in obj['stages'].items():
        st=stage_['status']
        if st=='pending': problems.append(f'{sid}: pending (not assessed)')
        if st in ('blocked','not-applicable') and len(stage_['reason'].strip()) < 8:
            problems.append(f'{sid}: missing specific {st} reason')
        if st=='done' and sid!='S12' and not any(e['stage']==sid for e in obj['evidence']):
            problems.append(f'{sid}: done without registered source evidence')
    if obj['stages']['S01']['status']!='done': problems.append('S01 must finish as done')
    if obj['stages']['S12']['status']!='done': problems.append('S12 audit must finish as done')
    if not any(obj['stages'][sid]['status']=='done' for sid in ('S03','S04','S05','S06','S07','S08','S09','S10','S13')):
        problems.append('No completed domain investigation (S03–S10 or S13)')
    for name in NOTES_REQUIRED:
        content=note_contents(root,name)
        if len(content)<30 or content.startswith('TODO') or content.startswith('[Fill'):
            problems.append(f'notes/{name}.md: missing meaningful content')
    if not obj['claims']:
        problems.append('No registered claims')
    elif not any(c['class']!='hypothesis' and c['evidence'] for c in obj['claims']):
        problems.append('No non-hypothesis claim backed by source evidence')
    for item in obj['evidence']:
        p=(root/item['file']).resolve()
        if not p.is_relative_to(root) or not p.is_file():
            problems.append(f'{item["id"]}: source missing or outside case')
        elif hash_file(p)!=item['sha256']:
            problems.append(f'{item["id"]}: SHA-256 mismatch')
    known={e['id'] for e in obj['evidence']}
    for c in obj['claims']:
        if not set(c['evidence']).issubset(known):
            problems.append(f'{c["id"]}: unknown evidence citation')
        if c['class']!='hypothesis' and not c['evidence']:
            problems.append(f'{c["id"]}: non-hypothesis claim without evidence')
    return problems


def esc(s):
    return str(s).replace('|','\\|').replace('\n',' ')


def generate(root:Path,obj:dict, problems:list[str])->str:
    blocked=sum(v['status']=='blocked' for v in obj['stages'].values())
    state = 'STRUCTURALLY COMPLETE' if not problems and not blocked else ('QUALIFIED — BLOCKED CAPABILITIES' if not problems else 'INCOMPLETE — EVIDENCE GAPS')
    out=['# Reverse-engineering investigation','',f'**Assessment:** {state}  ',
         f'**Target:** `{obj["target"]}`  ', f'**Question:** {obj["question"]}  ',
         f'**Case created (UTC):** {obj["created_at"]}  ',
         f'**Last updated (UTC):** {obj["updated_at"]}  ',
         f'**Authorization recorded:** {obj.get("authorization") or "Not specified"}', '',
         '## Findings at a glance', '', note_contents(root,'overview') or '*Not established.*','',
         '## Capability coverage', '', '| ID | Investigation capability | Outcome | Evidence or reason |',
         '| --- | --- | --- | --- |']
    for sid,s in obj['stages'].items():
        related=[e['id'] for e in obj['evidence'] if e['stage']==sid]
        detail=', '.join(related) if s['status']=='done' else (s['reason'] or 'Not assessed')
        if sid=='S12' and s['status']=='done': detail='notes/audit.md; ' + ', '.join(related)
        out.append(f'| {sid} | {esc(s["name"])} | {esc(s["status"])} | {esc(detail)} |')
    ident=obj['target_identity']
    out+=['','## Source identity','',f'- Kind: `{ident["kind"]}`',
          f'- SHA-256: `{ident.get("sha256") or "Not established"}`',
          f'- Source: `{ident["value"]}`']
    if 'size' in ident: out.append(f'- File size: {ident["size"]} bytes')
    if 'file_count' in ident: out.append(f'- Directory contents: {ident["file_count"]} files; {ident["symlinks_skipped"]} symlinks skipped')
    if ident.get('note'): out.append(f'- Identity caveat: {ident["note"]}')
    for index, other in enumerate(obj.get('additional_target_identities', []), 1):
        out.append(f'- Additional target {index}: `{other["value"]}`, SHA-256 `{other.get("sha256") or "Not established"}`')
    mapping=[('architecture','Architecture and boundaries'),('trace','Feature/data-flow trace'),
             ('network','Network behavior'),('version-diff','Version differences'),
             ('implementation','Independent implementation and parity'),('verification','Verification and reproducibility')]
    for key,title in mapping:
        content=note_contents(root,key)
        if content or key in NOTES_REQUIRED:
            out+=['',f'## {title}','',content or '*Not established.*']
    out+=['','## Evidence-backed claims','', '| Claim | Class | Supported statement | Sources | Locator |',
          '| --- | --- | --- | --- | --- |']
    for c in obj['claims']:
        out.append(f'| {c["id"]} | {esc(c["class"])} | {esc(c["text"])} | {", ".join(c["evidence"]) or "None (hypothesis)"} | {esc(c["locator"])} |')
    if not obj['claims']: out.append('| — | — | *No supported findings registered* | — | — |')
    out+=['','## Source register','', '| Source | Stage | Type | File | Source locator | SHA-256 |',
          '| --- | --- | --- | --- | --- | --- |']
    for e in obj['evidence']:
        out.append(f'| {e["id"]} | {e["stage"]} | {e["kind"]} | [{esc(e["file"])}]({e["file"]}) | {esc(e["locator"])} | `{e["sha256"]}` |')
    out+=['','## Adversarial audit','',note_contents(root,'audit') or '*No challenge performed.*',
          '', '## Limitations and next experiments','', note_contents(root,'limitations') or '*Not established.*']
    optional=note_contents(root,'appendix')
    if optional: out+=['','## Appendix','',optional]
    if problems: out+=['','## Structural validation findings','']+['- '+p for p in problems]
    out+=['','---','', 'Generated from the case ledger and investigator-authored notes; the generator does **not** validate technical truth.']
    return '\n'.join(out)+'\n'


def render(args):
    root=args.case_dir.resolve(); obj=load(root); problems=issues(root,obj)
    dest=root/'REPORT.md'; dest.write_text(generate(root,obj,problems),encoding='utf-8')
    print(f'Wrote {dest}; {len(problems)} validation issue(s), {sum(v["status"]=="blocked" for v in obj["stages"].values())} blocked stage(s).')


def check(args):
    root=args.case_dir.resolve(); obj=load(root); problems=issues(root,obj)
    if not (root/'REPORT.md').exists(): problems.append('REPORT.md missing: run render')
    blocked=[sid for sid,s in obj['stages'].items() if s['status']=='blocked']
    print(f'Case: {root}\nStages: {len(obj["stages"])}; sources: {len(obj["evidence"])}; claims: {len(obj["claims"])}')
    for line in problems: print(f'ISSUE: {line}')
    for sid in blocked: print(f'BLOCKED: {sid} — {obj["stages"][sid]["reason"]}')
    if not problems and not blocked: print('PASS: all structural completion gates satisfied (not a substantive truth audit).')
    elif not problems: print('QUALIFIED: structural gates satisfied, but blocked capabilities remain.')
    else: print(f'INCOMPLETE: {len(problems)} structural issue(s).')
    return 1 if args.strict and (problems or blocked) else 0


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('init'); a.add_argument('--target',required=True);a.add_argument('--question',required=True)
    a.add_argument('--out',type=Path,required=True);a.add_argument('--authorization',default='')
    a.add_argument('--additional-target',action='append',default=[], help='Second build or other separately identified input; repeatable')
    a=sub.add_parser('stage'); a.add_argument('case_dir',type=Path); a.add_argument('id',choices=STAGES)
    a.add_argument('status',choices=STATUSES);a.add_argument('--reason',default='')
    a=sub.add_parser('evidence');a.add_argument('case_dir',type=Path);a.add_argument('--stage',choices=STAGES,required=True)
    a.add_argument('--file',type=Path,required=True);a.add_argument('--locator',required=True)
    a.add_argument('--kind',choices=KINDS,required=True);a.add_argument('--summary',required=True)
    a=sub.add_parser('claim');a.add_argument('case_dir',type=Path);a.add_argument('--text',required=True)
    a.add_argument('--class',dest='classification',choices=CLASSES,required=True);a.add_argument('--evidence',action='append',default=[])
    a.add_argument('--locator',default='');a.add_argument('--counterexample',default='')
    for name in ('render','check'):
        a=sub.add_parser(name);a.add_argument('case_dir',type=Path)
        if name=='check':a.add_argument('--strict',action='store_true')
    args=p.parse_args()
    try:
        funcs={'init':init,'stage':stage,'evidence':source,'claim':claim,'render':render,'check':check}
        result=funcs[args.cmd](args)
        return result if isinstance(result,int) else 0
    except (ValueError,OSError,json.JSONDecodeError) as ex:
        print(f'ERROR: {ex}',file=sys.stderr);return 2

if __name__=='__main__':
    sys.exit(main())
