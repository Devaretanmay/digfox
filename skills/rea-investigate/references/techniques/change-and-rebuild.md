# Version differences and independent implementation

Load when S10 or S11 is relevant. These are separate gates: change investigation does not authorize writing code, and a request to understand does not authorize cloning.

## S10 — Build/version comparison

1. Hash both exact artifacts, record platform, version, architecture, signing context and release origin. Do not pair a release app with an unrelated developer build.
2. Produce **independent** complete analysis Evidence for each version. For JS:

   ```sh
   rea analyze-javascript-application /absolute/v1.asar --json > CASE/evidence/left.json
   rea analyze-javascript-application /absolute/v2.asar --json > CASE/evidence/right.json
   python3 scripts/rea_payload.py compare CASE/evidence/left.json CASE/evidence/right.json > CASE/evidence/comparison-input.json
   rea compare-application-versions CASE/evidence/comparison-input.json --json > CASE/evidence/comparison.json
   ```

3. Confirm structure, identities, matching rules and coverage. Stable minified names/ordinal numbers alone are poor cross-build identities. Mark `changed`, `unchanged`, `added`, `removed`, or `unknown` for each researched behavior. Partial inventory makes removal **unknown**.
4. For .NET, use installed `rea compare-managed-members` contract; token integers are not stable identities. For native, inspect byte and control-flow differences with matching provider and architecture, not semantic guesses.
5. If the result claims runtime behavioral change, reproduce a controlled scenario separately on both builds (only when authorized) and compare the observed states.

## S11 — Rebuild (explicit instruction only)

1. Write an **observable contract** from verified behavior: public interface, inputs, outputs, errors, permission/state transitions, timing expectations. Mark inferred and unobserved cases in a distinct column.
2. Build regression cases covering ordinary, boundary, malformed, stateful, failure and timing paths. Where original execution is approved, retain its fixtures and observations separately from new tests.
3. Implement **new** code at the smallest seam of the user's project. Avoid copying proprietary decompiled expression-by-expression source or assets. Use tests and code conventions of the host project.
4. Run tests and compare original/new observations. Report matched, mismatched and untested cases; successful invented expected outputs do not prove original parity.
5. User did not explicitly ask for implementation? Stage S11 is `not-applicable` with reason "investigation/report only".

## Test report columns

| Case | Original observation (source ID) | New implementation result (source ID) | Verdict | Gap |
| --- | --- | --- | --- | --- |
| Normal input | E0003 | E0009 | Match/mismatch/unknown | ... |
