# Diagnosis guide

Read this file only when the defect crosses a system boundary or the owner is unclear.

## API and wrapper boundaries

- Trace serialized input, defaults, validation, transport, deserialization, and the final engine call.
- Compare wrapper behavior with the underlying implementation. A wrapper-level patch is incomplete when another entry point bypasses it.
- Check aliases, generated clients, retry behavior, status mapping, and error translation.

## Databases and state

- Capture the query or state transition that produces the symptom.
- Check transaction scope, isolation assumptions, ordering, uniqueness, null handling, pagination, and tenant filters.
- Distinguish application-state bugs from storage guarantees. Verify rollback and retry paths when writes are involved.

## Native engines and generated code

- Find the binding boundary and the source of truth. Do not edit generated output when its generator owns the behavior.
- Check type width, ownership, lifetime, encoding, platform differences, build flags, and error conversion.
- Run the smallest relevant build or binding test. If the native layer cannot be built, report that verification gap.

## Asynchronous and concurrent execution

- Trace task creation, scheduling, awaiting, cancellation, timeout, retry, and cleanup.
- Check shared mutable state, ordering assumptions, duplicate execution, lost exceptions, and work that outlives its request.
- Reproduce with controlled synchronization when possible. Do not treat timing delays as proof of correctness.

## Competing hypotheses

For each plausible cause, record:

1. Evidence it predicts.
2. One observation that would falsify it.
3. The cheapest safe check that distinguishes it from the leading cause.

Stop when evidence identifies the responsible component and failure mechanism. More tracing without a decision is not rigor.
