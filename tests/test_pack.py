import json
import subprocess
import sys
import tempfile
import unittest
import contextlib
import importlib.util
import io
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/'skills'/'rea-investigate'
SCRIPT = SKILL/'scripts'/'case.py'
spec = importlib.util.spec_from_file_location('rea_case',SCRIPT)
case_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(case_module)
STAGES = list(case_module.STAGES)


class Result:
    def __init__(self, returncode, stdout='', stderr=''):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def cmd(*args, ok=True):
    out, err = io.StringIO(), io.StringIO()
    with patch.object(sys, 'argv', [str(SCRIPT), *map(str,args)]), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = case_module.main()
        except SystemExit as exc:
            rc = exc.code
    result = Result(rc, out.getvalue(), err.getvalue())
    if ok and rc:
        raise AssertionError(f'{rc} {result.stdout} {result.stderr}')
    return result

class TestOneSkill(unittest.TestCase):
    def test_only_one_skill_md(self):
        self.assertEqual([p.relative_to(ROOT).as_posix() for p in ROOT.glob('skills/**/SKILL.md')], ['skills/rea-investigate/SKILL.md'])
        body=(SKILL/'SKILL.md').read_text()
        self.assertIn('disable-model-invocation: true',body)
        for key in ('# REA investigate','references/capabilities.md','references/report.md'):
            self.assertIn(key,body)

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.target=self.base/'program.bin'
        self.target.write_bytes(b'fake-test-binary-do-not-execute')
        self.case=self.base/'case'
        cmd('init','--target',self.target,'--question','What is the test behavior?', '--authorization','local fake input only', '--out',self.case)

    def test_initial_case_is_not_falsely_complete(self):
        x=json.loads((self.case/'case.json').read_text())
        self.assertEqual(len(x['stages']),13)
        self.assertEqual(x['evidence'][0]['id'],'E0001')
        self.assertEqual(x['target_identity']['kind'],'file')
        self.assertEqual(cmd('check',self.case,'--strict',ok=False).returncode,1)

    def test_additional_target_is_hashed_independently(self):
        second=self.base/'second.bin'; second.write_bytes(b'second-synthetic-build')
        other_case=self.base/'comparison-case'
        cmd('init','--target',self.target,'--additional-target',second,
            '--question','What changed between two sample builds?', '--out',other_case)
        ledger=json.loads((other_case/'case.json').read_text())
        self.assertEqual(len(ledger['additional_target_identities']),1)
        self.assertNotEqual(ledger['target_identity']['sha256'],ledger['additional_target_identities'][0]['sha256'])
        self.assertEqual(ledger['evidence'][1]['stage'],'S10')

    def test_not_applicable_requires_reason(self):
        p=cmd('stage',self.case,'S04','not-applicable',ok=False)
        self.assertEqual(p.returncode,2)

    def test_done_requires_source(self):
        p=cmd('stage',self.case,'S06','done',ok=False)
        self.assertEqual(p.returncode,2)

    def test_claim_rejects_unregistered_id(self):
        p=cmd('claim',self.case,'--text','Function writes data to a buffer','--class','observation','--evidence','E9999',ok=False)
        self.assertEqual(p.returncode,2)

    def test_source_must_reside_inside_case(self):
        p=cmd('evidence',self.case,'--stage','S06','--file',self.target,
              '--locator','/','--kind','artifact','--summary','Target binary',ok=False)
        self.assertEqual(p.returncode,2)

    def _finish_case(self):
        evidence=self.case/'evidence'/'parsed.json'
        evidence.write_text('{"normalized_result":{"objects":[{"offset":42,"value":"test"}]}}')
        cmd('evidence',self.case,'--stage','S02','--file',evidence,'--locator','/normalized_result','--kind','static','--summary','Validated small static inventory')
        another=self.case/'evidence'/'function.json';another.write_text('{"offset":42,"assembly":"ret"}')
        cmd('evidence',self.case,'--stage','S06','--file',another,'--locator','/assembly','--kind','static','--summary','Synthetic test function')
        for stage in STAGES:
            if stage in ('S01','S02','S06','S12'):
                cmd('stage',self.case,stage,'done')
            else:
                cmd('stage',self.case,stage,'not-applicable','--reason',f'Not present in synthetic test target (mock-only): {stage}')
        cmd('claim',self.case,'--text','Test artifact contains a synthetic return instruction','--class','observation','--evidence','E0003','--locator','/assembly')
        for name in ('overview','architecture','trace','verification','limitations','audit'):
            (self.case/'notes'/f'{name}.md').write_text(f'{name.title()}: this is synthetic test fixture content and not a real target analysis. Evidence E0003 is merely a stub, not actual REA output.\n')
        cmd('render',self.case)

    def test_complete_fictional_fixture_passes_structural_validation(self):
        self._finish_case()
        report=(self.case/'REPORT.md').read_text()
        self.assertIn('S13',report)
        self.assertIn('E0003',report)
        self.assertIn('STRUCTURALLY COMPLETE',report)
        self.assertEqual(cmd('check',self.case,'--strict').returncode,0)

    def test_mutated_source_fails_integrity_check(self):
        self._finish_case()
        (self.case/'evidence'/'function.json').write_text('{"tampered":true}')
        self.assertEqual(cmd('check',self.case,'--strict',ok=False).returncode,1)

    def test_blocked_stage_is_qualified_not_pass(self):
        self._finish_case()
        cmd('stage',self.case,'S04','blocked','--reason','Browser not installed and runtime capture could not be verified')
        cmd('render',self.case)
        self.assertIn('QUALIFIED', (self.case/'REPORT.md').read_text())
        self.assertEqual(cmd('check',self.case,'--strict',ok=False).returncode,1)

    def test_installer_dry_run_does_not_write(self):
        project=self.base/'newproject'; project.mkdir()
        p=subprocess.run([sys.executable,str(ROOT/'install.py'),'--agent','codex','--project',str(project),'--dry-run'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertFalse((project/'.agents'/'skills'/'rea-investigate').exists())

    def test_payloads_reject_missing_evidence(self):
        p=subprocess.run([sys.executable,str(SKILL/'scripts'/'rea_payload.py'),'trace',str(self.target),'--seed-value','foo'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)

if __name__=='__main__':
    unittest.main()
