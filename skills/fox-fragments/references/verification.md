# Fragment: focused verification

Read when the task has meaningful regression, compatibility or multi-path risk. Preserve the active task's authorization boundary; verification never permits a review or exploration task to edit.

- Confirm the reproducer fails before repair and passes after, when feasible.
- Check the owning-layer contract and relevant alternate public entry points, callers, failure paths and side effects.
- Test boundaries affected by change: tenant and permission checks, null/empty inputs, errors, retries, concurrency, cancellation, cleanup, migrations and serialization.
- Prefer targeted repository-native commands, then a proportionate existing suite. Do not run an irrelevant test matrix.
- During read-only work, do not install packages, update snapshots, regenerate source or use test update flags. Use an isolated copy for checks that write caches or artifacts when practical; otherwise disclose the limit and skip unsafe checks.
- Never state a test ran unless a real tool result confirms it. Report exact commands, outcomes and remaining uncertainty. Keep blocked or partial repairs explicit.
- Instruction-contract and installation tests establish packaging and stated rules, not agent compliance. Behavioral comparisons need matched model, settings, tasks and repeated trials; review accuracy and false positives need independent grading. Use measured structured usage events only; missing metrics stay unknown. Do not claim reliability, token or cost improvements from these checks.
