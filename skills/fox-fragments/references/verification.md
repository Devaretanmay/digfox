# Fragment: focused verification

Read when the task has meaningful regression, compatibility or multi-path risk.

- Confirm the reproducer fails before repair and passes after, when feasible.
- Check the owning-layer contract and relevant alternate public entry points, callers, failure paths and side effects.
- Test boundaries affected by change: tenant and permission checks, null/empty inputs, errors, retries, concurrency, cancellation and serialization.
- Prefer targeted commands then proportionate existing suite. Do not run an irrelevant test matrix.
- Never state a test ran unless a real tool result confirms it. Report exact commands, outcomes, and remaining uncertainty.
