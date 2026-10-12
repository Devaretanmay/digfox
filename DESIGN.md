# Architecture decision record: why Proofwork is a system, not a concatenation

## What was considered

| Architecture | Advantage | Why it was rejected / accepted |
|---|---|---|
| Merge REA and Systemcraft SKILL.md verbatim | Apparently one skill | **Reject.** REA's deep specialized investigation demands dedicated instructions, 13-capability routing, and tool providers. Overlapping agent instructions would be large and brittle. |
| Replace REA with a general research checklist | Tiny download | **Reject.** Sacrifices binary/app/firmware/HAR/provider depth, original evidence ledger and strict quality gates. |
| Always spawn a team of agents | Impressive demo | **Reject.** Adds latency, cost, race conditions and authority confusion where a script or one agent suffices. |
| Proofwork front door + integrated Systemcraft + independent REA specialist + provenance handoff | Focused default, deep opt-in capability, and compatible original source | **Choose.** Small fast path without REA; authorized specialist route when needed; separate verified scopes. |

## Components

1. **Proofwork `SKILL.md`**: model-facing decision protocol (scope, investigate, decide, build, verify, deliver).
2. **Proofwork ledger (`proof.py`)**: local integrity and documentation gate; supports raw evidence + claims + alternatives + decisions + tests + report.
3. **Systemcraft-derived scaffold/audit/templates**: generates outcome contracts and staged workspaces only when appropriate.
4. **REA Investigator**: optionally installs from original local checkout without modifying source; retains its native case ledger, specialized references and 13 capability routing.
5. **Bridge (`proof.py import-rea`)**: hashes original REA case manifest and report, attributes them, and requires an actual evidence/claim review before downstream claims are made.

## Trust boundaries

- Evidence bytes are copied into a local case and SHA-256 protected against accidental change; the hash **does not** prove its origin or statement truth.
- Provenance from REA is not semantic verification by Proofwork. REA strict check remains the source of truth for its own case completeness.
- Test logs are operator-supplied; a log hash does not attest the command ran or that its expected behavior was correct. The included demo commands were actually run during packaging.
- `approve` is a documentary record, not a mechanism to obtain new rights. Host agent/user tooling enforces actual permissions.
- Unknown code, captures, publishing, spending, production mutations and third-party access require user approval and proper permissions. Installer only writes copied files to an explicitly selected project.

## Practical limitations and roadmap

**Already verified:** standard-library import, ledger validation, evidence hash tamper detection, bad refs, adversarial claim fields, no silent overwrite, REA-path copying, structural scaffold/audit and a controlled successful/negative fixture.

**Not yet verified:** actual model adherence to Proofwork instructions across clients, throughput with large repositories, cross-model quality gains, security of arbitrary user-supplied REA tools, production concurrency or external side effects.

**Next tests before a 'production-grade' claim:** compare baseline agents against Proofwork on 20–50 representative tasks; blind-grade evidence correctness, decision quality, run success, token/cost overhead, and rework. Include negative cases, permission boundaries and deliberately misleading source documents. Separate inter-rater agreement from test script pass rate.
