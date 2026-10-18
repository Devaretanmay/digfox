# Worked example: choose a script, not an agent swarm

Question: *Can a small invoice report be made repeatably without LLM ambiguity?*

Decision: use a deterministic CSV parser with exact decimal arithmetic and schema checks. Reject a multi-agent framework because there is no ambiguous reasoning, parallelism, or service state here.

Run:

```sh
python3 examples/invoice-report/report.py examples/invoice-report/input.csv
# {"Design": "175.25", "Engineering": "225.00"}
```

`examples/invoice-report/demo-case/` records a generated Fox case, source hashes, a challenged claim, the architecture decision, recorded output test and an explicit limitation. The fixture is small and synthetic. It demonstrates ledger mechanics, **not** real production quality or an independently attested benchmark.
