# Proofwork case report

**Question:** Can invoice totals be reproduced without a language model?
**Target:** examples/invoice-report
**Mode:** build
**Phase:** deliver
**Recorded authorization:** True

## Evidence (integrity-checked records)

| ID | Kind | Captured item | Locator |
|---|---|---|---|
| E001 | source | `evidence/E001.csv` SHA256 `4879c5901e51…` | input.csv:2-5 |
| E002 | source | `evidence/E002.py` SHA256 `f9a6bf1d555e…` | report.py:summarize |
| E003 | observation | `evidence/E003.log` SHA256 `4b66a63808e5…` | golden-test.log:3 |
| E004 | test-log | `evidence/E004.log` SHA256 `4b66a63808e5…` | test: Golden invoice totals |
| E005 | test-log | `evidence/E005.log` SHA256 `2fcd34450232…` | test: Reject negative amount |

## Claims (claims are not automatically verified by hashes)

| ID | Status | Assertion | Evidence | Competing explanation | Falsifier |
|---|---|---|---|---|---|
| C001 | observed | Synthetic example groups monetary totals by department | E001,E002,E003 | Output might be hardcoded, not computed | Change one input amount and rerun; output should change by that amount |

## Decisions and rejected alternatives

### D001: Deterministic Python CSV parser
- Alternatives: Multiple LLM agents, Prompt-only calculation
- Reasoning: Decimal arithmetic and strict columns provide reproducible checks without ambiguous interpretation
- Supported claims: C001
- Reversible: True
- Revisit if: Input formats become highly variable or require ambiguous judgment

## Tests (operator-recorded execution)

| ID | Test | Exit code | Log | Coverage |
|---|---|---|---|---|
| T001 | Golden invoice totals | 0 | E004 | 4 invoices, exact totals: Design 175.25, Engineering 225.00 |
| T002 | Reject negative amount | 1 | E005 | Expected failure: negative input should raise ValueError |

## Approvals on record (not proof of user identity)


## Limitations and unresolved risks

- Only synthetic 4-row fixture and one malformed negative input were executed; not a production benchmark.
- Recorded process exit codes reflect the demo script invocations only; this ledger cannot attest general runtime integrity.

## Integrity and quality gates

- No structural or evidence-integrity findings.

**Scope of verification:** SHA-256 checks establish saved-file integrity only; they do not certify source authenticity, semantic truth, authorization, or actual runtime execution.
