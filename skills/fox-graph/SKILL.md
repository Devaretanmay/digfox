---
name: fox-graph
description: Analyzes code graphs and patch blast-radii to detect architectural dependencies, identify unpatched alternate execution paths, and generate targeted regression verification plans. Use when analyzing code changes, checking patch impact, discovering unverified execution paths, auditing cross-module blast radii, or selecting regression tests in multi-file codebases. Skip for trivial single-file edits.
license: MIT
compatibility: Works with coding agents; Node.js/npx or Python 3.10+ for local analysis.
metadata:
  version: "0.1.0"
---
# Fox Graph

Find the paths your fix missed.

Fox Graph provides graph-assisted impact analysis for proposed code modifications. It maps git diff hunks to code symbols, traces incoming callers and dependencies, flags unverified public execution paths, and generates a prioritized verification plan.

Use local providers. Match traversal depth to risk. Do not speculate: distinguish confirmed graph edges from dynamic or unresolved relationships.

## 1. Understand the patch

Read the target repository and the proposed Git diff (staged, unstaged, or commit range).
Map changed line hunks to concrete symbols: functions, methods, classes, or modules.
Distinguish public API surfaces from internal engine implementations.

CLI invocation:
```bash
python3 skills/fox-graph/scripts/fox_graph.py --repo <path> [--staged | --base <branch>]
```

## 2. Query relationships

Query the local code graph provider (GitNexus or local AST) for the enclosing changed symbols.
Extract:
- Direct incoming callers and references.
- Transitive upstream callers up to depth 3.
- Module-level imports and consumers.
- Downstream dependencies shared with other components.

Record exact file paths and source lines for all confirmed edges.

## 3. Detect coverage gaps

Compare the graph callers against the test files modified in the diff.
Flag paths that:
- Route to the modified implementation but have no targeted test in the diff.
- Bypass a modified public wrapper by calling an underlying engine directly.
- Share a modified dependency or helper with unverified sibling entry points.
- Exercise alternative configurations or input types.

Never invent phantom paths to inflate a report. If all callers are covered by existing tests, report that no gaps were detected.

## 4. Generate verification plan

Produce a prioritized list of up to five targeted checks. For each check, specify:
- Entry point (file and symbol).
- Relationship to the changed component.
- Suspected failure mode or regression risk.
- Suggested test command or concrete input reproduction.
- Why this check matters to system reliability.

Prefer three high-value checks over thirty generic ones.

## 5. Report limitations

Explicitly disclose relationships that static analysis cannot resolve:
- Dynamic dispatch via `getattr()`, `setattr()`, reflection, or `eval()`.
- Untyped callback forwarding (`*args`, `**kwargs`).
- Decorators that intercept or rewrite calls at runtime.
- Native compiled extensions (C, Rust, C++) crossing foreign-function boundaries.

Never claim 100% call-graph completeness without runtime proof.

## Read only when needed

- [Provider setup and architecture](references/providers.md) for GitNexus and AST provider details.
- [Coverage gap analysis guide](references/gap-analysis.md) for identifying wrapper bypasses and sibling routes.
- [Static analysis limitations](references/limitations.md) for dynamic dispatch boundaries and fallbacks.
