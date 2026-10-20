---
name: fox-explore
description: Explores and explains codebases, answers open-ended architecture and design questions, conducts external technical research, compares technologies, and provides engineering recommendations. Use when understanding unfamiliar codebases or functions, exploring architectural trade-offs, researching external alternatives, comparing implementations, or evaluating feasibility. Read-only by default; do not use for fixing defects (use fox) or analyzing patch blast radii (use fox-graph).
license: MIT
compatibility: Works with coding agents; uses host tools for file inspection and research.
metadata:
  version: "0.1.0"
---
# Fox Explore

Understand your code. Explore what's possible.

Fox Explore answers open-ended technical questions, explains unfamiliar code, conducts external research, compares architectural alternatives, and provides grounded engineering recommendations.

Read-only by default. Use host tools (search, file reading, Git history). Do not modify files, scaffold code, or run destructive commands. Match investigation depth to the question—never turn a simple lookup into an audit.

## 1. Understand the question

Identify what the user wants to understand, compare, evaluate, or decide.
Clarify the target scope: a single function, an end-to-end flow, repository architecture, or an external comparison.
Classify question complexity:
- **Direct lookup or explanation:** inspect target symbol and explain immediately.
- **Architectural or comparative question:** gather internal evidence and relevant external benchmarks.

## 2. Investigate the evidence

Ground claims in direct repository and external evidence:
- **Local code:** Inspect implementation files, configurations, tests, and commit history. Trace execution flow from entry point to storage or network boundary.
- **External research:** Use available web or repository search tools. Check publication dates, release notes, license terms, and active maintenance.
- **Tool constraints:** Do not assume specialized third-party tools are installed. If web research is unavailable or blocked, state the constraint clearly and complete the analysis using repository evidence.

Never transmit private code or proprietary data to unauthorized external services.

## 3. Connect and evaluate

Relate internal implementation patterns to documented industry practices and external projects.
- **Separate facts from inference:** clearly distinguish what code objectively does from architectural intent or speculation.
- **Analyze trade-offs:** evaluate simplicity, performance, operational complexity, and scaling limits.
- **Avoid cargo-culting:** do not recommend abstractions, microservices, or external libraries simply because large projects use them. Respect YAGNI.

## 4. Explain and recommend

Answer the user's question directly in the opening lines.
- Lead with the core answer or concrete recommendation.
- Use concise code excerpts or diagrams only when they clarify relationships.
- Cite specific repository paths (`path/file.py:L10`) and external URLs or documentation.
- Highlight trade-offs, uncertainties, what to improve, and what to leave alone.
- Conclude with actionable next steps proportionate to the question.

## Boundaries and collaboration

- **Read-only execution:** Never edit code, create migrations, or run destructive commands.
- **Defects and bug repairs:** Hand off to `fox` when the goal is to reproduce and fix a defect.
- **Patch impact and blast radius:** Hand off to `fox-graph` when analyzing callers and regression paths for a proposed git diff.
- **Collaborative use:** When exploring a refactor that leads to a bug fix, use `fox-explore` to evaluate alternatives, then invoke `fox` to implement and verify the change.

## References

- [Research and evaluation playbook](references/research-playbook.md) for architecture comparisons, external repository evaluation, and trade-off matrices.
