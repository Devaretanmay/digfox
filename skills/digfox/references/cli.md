# Digfox CLI cookbook

Works on macOS, Linux, Windows with Python 3.10+; no third-party dependencies.

The CLI does **not** research on its own, evaluate claims semantically, run submitted code, or independently attest a test run. It maintains an inspectable integrity ledger.

```sh
SKILL=/path/to/digfox/skills/digfox
python3 "$SKILL/scripts/proof.py" doctor
python3 "$SKILL/scripts/proof.py" init \
  --out ./cases/sample --intent build \
  --question 'Can the weekly report be reproduced reliably?' \
  --target './inputs and report specification' --authorized
python3 "$SKILL/scripts/proof.py" phase ./cases/sample investigate
python3 "$SKILL/scripts/proof.py" evidence ./cases/sample \
  --file ./inputs/example.csv --kind source \
  --locator 'rows 2-21' --note 'Authorized example inputs, redacted'
python3 "$SKILL/scripts/proof.py" claim ./cases/sample \
  --statement 'The existing report groups sales by region' \
  --evidence E001 --confidence inferred --locator 'report.py:45-70'
python3 "$SKILL/scripts/proof.py" phase ./cases/sample decide
python3 "$SKILL/scripts/proof.py" decision ./cases/sample \
  --choose 'Python script plus review' --instead-of 'Multi-agent service' \
  --why 'Deterministic schema and no concurrency need' \
  --claims C001 --reversible --revisit-when 'Input semantics change'
python3 "$SKILL/scripts/proof.py" phase ./cases/sample build
# Implement and independently execute tests, saving the real command log.
python3 "$SKILL/scripts/proof.py" test ./cases/sample \
  --label 'golden report fixture' --log ./actual-test-output.txt \
  --exit-code 0 --scope 'Example input, output schema and totals'
python3 "$SKILL/scripts/proof.py" phase ./cases/sample verify
python3 "$SKILL/scripts/proof.py" limit ./cases/sample \
  --text 'Only one representative fixture tested; production inputs not covered'
python3 "$SKILL/scripts/proof.py" report ./cases/sample
python3 "$SKILL/scripts/proof.py" phase ./cases/sample deliver
python3 "$SKILL/scripts/proof.py" report ./cases/sample
python3 "$SKILL/scripts/proof.py" check ./cases/sample
```

## Additional commands

- `claim --confidence observed` requires `--locator`, `--alternative`, and `--falsifier`. This raises the standard for claimed direct observation but does not automatically prove it.
- `approve <case> --operation publish --reason 'Owner approved publication on <date>'` adds an audit statement; the agent must obtain actual human permission separately.
- `import-rea <case> --rea-case <path>` copies the original REA case manifest and report by hash. Source files remain in the source case; an imported report is not silently upgraded to verified evidence.
- `check --strict` fails on warnings such as missing negative tests, no evidence, or no documented decision. It is a documentation/integrity gate only.
- `report` rewrites `REPORT.md` deterministically from current `case.json`; run it after adding tests or limits.

For a simple repeated workflow, skip the ledger entirely and run `scripts/scaffold.py` / `scripts/audit.py` directly. Avoid generating case bureaucracy for one-off work.
