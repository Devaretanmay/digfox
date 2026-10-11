# Evidence ledger and claim discipline

**Single source of truth**: `case.json` holds stages, source IDs and claim IDs. Raw Evidence remains in `evidence/`. The ledger records a SHA-256 of each registered source. Never edit it manually; call `case.py`.

## Register a source

```
python3 scripts/case.py evidence CASE_DIR --stage S03 --file CASE_DIR/evidence/app.json \
  --locator '/normalized_result/modules/12' --kind static --summary 'Module linked to preload export'
```

`--kind`: `static`, `runtime`, `capture`, `artifact`, `test`, `document`.

## Register a claim

```
python3 scripts/case.py claim CASE_DIR --text 'Export click is wired to ipcRenderer.send(...)' \
  --class static-inference --evidence E0001 --locator '/normalized_result/edges/3'
```

Classes: `observation`, `static-inference`, `runtime-inference`, `hypothesis`. A meaningful non-hypothesis claim needs at least one source. Prefer specific source offsets, code locations and observed scenario steps; mere filename is insufficient for detailed behavioral assertions. Claims and sources are connected by ID, never positional guesses.

## Epistemic contract

| Class | May say | Must not say |
| --- | --- | --- |
| observation | These bytes/events were actually present in the cited material | The code necessarily executed because it is present |
| static-inference | Reachability, dataflow or a plausible contract inferred from recovered code | Original source, confirmed dynamic path |
| runtime-inference | This action plausibly caused that effect, supported by controlled observations | Causation from a single coincident timestamp |
| hypothesis | An unresolved possibility with an experiment to test it | A demonstrated implementation detail |

Register raw outputs without secrets. If a file contains tokens, cookies, PII, customer data or confidential code that the user cannot disclose, preserve a private original offline and register a redacted derivative. State the redaction/coverage limits in `notes/limitations.md`. Do not quote large decompiled snippets or ship credential-bearing HARs in ZIPs.

## Contradictions

If two sources conflict, keep both, describe the variant conditions (time, version, architecture, config), and record a follow-up experiment. Do not average them into a claim. Evidence from different builds must have separate source records.

## Reproducibility

For every tested claim record the exact input, test data, versions, command/tool/provider and any exit status, plus before/after assertion. Preserve command logs where lawful. A screenshot or graph that lacks provenance is visual context, not a verified behavior proof.
