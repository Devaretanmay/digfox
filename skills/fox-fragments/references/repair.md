# Fragment: defect repair

Use for a concrete malfunction with authorized repair.

1. Identify the symptom, expected behavior, constraints, and the smallest reproducer; confirm the failure when practical.
2. Trace the failing input to the component that owns the behavior, not merely the wrapper; check one competing explanation.
3. Make the smallest **complete** repair at the owning layer. Prefer existing functions and standard libraries over new wrappers or dependencies. Update affected callers and contracts.
4. Re-run the reproducer and targeted regressions. Inspect the diff; try a counterexample.
5. Report the cause, evidence, changed paths, actual tests and limitations. Mark partial or unverified work clearly.

Do not edit if repair was not authorized. For cross-layer diagnosis, read boundaries.md only when the trace demands it.
