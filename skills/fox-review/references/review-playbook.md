# Fox Review: verification playbook

Use this reference only when a change crosses multiple components or a suspected finding needs more evidence.

## Determine the change boundary

- Compare the actual patch against its base revision, not only the PR description.
- Inspect consumers of changed exports, schema, configuration, and error contracts.
- Check alternate entry points, retries, concurrency, and migration sequences when affected.
- Do not presume every changed file is faulty or expand into unrelated code.

## Establish findings

1. State the exact behavior that was true before the patch or is required by an existing contract.
2. Identify the changed control/data flow that violates it.
3. Give the smallest realistic triggering input or sequence.
4. Check whether guards, callers, or tests already prevent the failure.
5. Classify confidence: confirmed by execution/contract, or plausible and requiring verification.
6. Recommend a narrow correction, without editing during review.

## Severity

- **P0:** release-blocking data loss, critical vulnerability, or broad outage under ordinary operation.
- **P1:** serious functional or security regression affecting important paths.
- **P2:** meaningful bug affecting a narrower supported scenario.
- **P3:** low-impact functional defect; omit style nitpicks.

Use severity based on actual exposure and reach, not on alarming terminology.

## Output example

**[P1] Retry can double-charge after a timeout** — `payments/charge.py:72-79`

A timed-out provider call can succeed remotely while the retry lacks an idempotency key. This causes a second charge when the caller retries after a network timeout. Check the provider response reconciliation path and reuse a stable operation key.

**Unverified:** Provider sandbox behavior could not be executed.

## Review limits

If there is no diff, no baseline, or no executable test environment, state precisely what was inspected and what remains unknown. Never invent test results or issues. Return “No substantiated findings” when appropriate.
