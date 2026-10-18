# Fox case report

**Question:** Prevent alias and extra field collisions from overwriting validated fields during serialization
**Target:** pydantic/main.py
**Mode:** build
**Phase:** deliver
**Recorded authorization:** True

## Evidence (integrity-checked records)

| ID | Kind | Captured item | Locator |
|---|---|---|---|
| E001 | source | `evidence/E001.py` SHA256 `376436a90c5f…` | benchmarks/task1_pydantic_12884/reproduce_issue.py:1-42 |
| E002 | test-log | `evidence/E002.log` SHA256 `b5861b74360f…` | test: test_solution |
| E003 | test-log | `evidence/E003.log` SHA256 `3d387aac66d4…` | test: unpatched_raw_pydantic_failure |

## Claims (claims are not automatically verified by hashes)

| ID | Status | Assertion | Evidence | Competing explanation | Falsifier |
|---|---|---|---|---|---|
| C001 | observed | extra='allow' allows input field names that match declared fields to overwrite validated values in model_dump() when fields use aliases | E001 | Collision is intended behavior under extra='allow' | If model_dump preserves model.x without overwriting, the claim is falsified |

## Decisions and rejected alternatives

### D001: Enforce declared field precedence during output dictionary assembly so validated fields cannot be overwritten by extra fields on name collision
- Alternatives: Disallow extra fields matching declared field names at validation time, Strip extra fields from output entirely
- Reasoning: Disallowing at validation time breaks backwards compatibility where extra keys are intentionally allowed; stripping breaks extra field retention. Precedence during dump preserves both requirements.
- Supported claims: C001
- Reversible: False
- Revisit if: Pydantic V3 implements strict duplicate key rejection during validation

## Tests (operator-recorded execution)

| ID | Test | Exit code | Log | Coverage |
|---|---|---|---|---|
| T001 | test_solution | 0 | E002 | Task 1 regression and validation tests |
| T002 | unpatched_raw_pydantic_failure | 1 | E003 | Baseline failure detection for raw Pydantic v2 collision |

## Approvals on record (not proof of user identity)


## Limitations and unresolved risks

- Resolution operates at serialization layer via safe_model_dump; deep C-extension or pydantic-core serializer modifications require compiling Rust pydantic-core extensions

## Integrity and quality gates

- No structural or evidence-integrity findings.

**Scope of verification:** SHA-256 checks establish saved-file integrity only; they do not certify source authenticity, semantic truth, authorization, or actual runtime execution.
