# Fragment: independent code review

Use for a defined diff, PR, commit or patch. Remain read-only.

1. Identify target and base. If not specified, inspect uncommitted changes, then the most recent commit and disclose the choice.
2. Read the diff, then affected callers, tests and contracts. Focus on introduced correctness, security, concurrency, data integrity, compatibility and meaningful performance defects.
3. For each suspected issue, state the changed location, triggering scenario, mechanism and consequence. Check competing explanations or run safe focused checks when possible.
4. Output only actionable findings ordered by severity (P0 blocker, P1 serious, P2 moderate, P3 minor). Each needs a path/line, evidence and smallest safe correction.
5. If no supported findings exist, say so. Distinguish unverified concerns and tests not run.

Never edit, approve, merge or manufacture findings. Explicitly authorized repair is a separate task routed to repair.md.
