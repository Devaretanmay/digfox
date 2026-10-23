---
name: fox-explore
description: Maps and explains codebases, traces execution flows, researches external technologies, compares architectural options, and gives evidence-backed recommendations. Use for repository onboarding, read-only architecture analysis, feasibility studies, technology comparisons, or questions about what to improve and retain. Do not use to repair defects, implement features, edit files, or answer a trivial lookup that needs no repository investigation.
license: MIT
compatibility: Works with coding agents; uses host tools for file inspection and research.
metadata:
  version: "0.2.0"
---
# Fox Explore

Understand the system, compare real options, and make the uncertainty visible.

Read-only by default. Use repository search, file reading, history, and available research tools. Do not edit files, scaffold code, install packages, or run destructive commands. Match depth to the decision; do not turn a direct lookup into a repository audit.

## 1. Scope

State the question, decision, target scope, constraints, and what evidence would answer it. Separate a direct code explanation from an architectural or comparative investigation. If the request also asks for implementation, finish the read-only analysis first and hand the authorized change to `fox`.

## 2. Map

Build the smallest repository map that supports the answer. Inspect implementations, callers, tests, configuration, history, and interfaces. For execution questions, trace one representative input from entry point through state, storage, network, native, or asynchronous boundaries to its output. Cite paths and symbols; do not infer architecture from filenames alone.

Record claims as **Observed**, **Inferred**, or **Unknown**. An inference must name its supporting evidence. An unknown must state what would resolve it.

## 3. Compare

For external claims, prefer current primary documentation, source repositories, release notes, benchmarks with disclosed methods, and license text. Check versions and publication dates. If research access is blocked, say so and do not invent URLs, adoption data, or benchmark results.

Compare only viable options against the same criteria: correctness fit, maintainability, performance, operational complexity, migration cost, reversibility, ecosystem health, and license constraints. Include the current design and the option to make no change. Do not recommend a library, service, abstraction, or distributed component because a popular project uses it.

## 4. Report

Lead with the answer. Then give the evidence, execution-flow map or comparison, trade-offs, and material unknowns. State what to improve, what to retain, and why. Recommend the least complex option that meets the demonstrated need. Keep speculative ideas separate and do not present them as work items.

## Boundaries and collaboration

- **Read-only execution:** Never edit code, create migrations, install dependencies, or run destructive commands.
- **Authorized implementation:** Explicit permission to change code ends the Explore phase; use `fox` for implementation and verification.
- **Sensitive sources:** Never transmit private code or proprietary data to an unauthorized external service.

## References

- [Research and evaluation playbook](references/research-playbook.md) for repository maps, source quality, trade-off matrices, and report templates.
