# Fox

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(stdlib)-success.svg)]()
[![Platform: Codex | Claude | Cursor](https://img.shields.io/badge/Agents-Codex%20%7C%20Claude%20%7C%20Cursor-purple.svg)]()
[![Tests: 33 Passed](https://img.shields.io/badge/Tests-33%20Passed-success.svg)]()

Fox is an open-source agent skill that guides AI coding assistants through disciplined software investigation, root cause diagnosis, minimal justified changes, and empirical verification. It teaches agents to trace execution paths across system boundaries, repair defects at the component that actually owns the behavior, and confirm results with reproducible evidence before marking tasks complete.

---

## Why it exists

Most AI coding assistants struggle with complex, cross-boundary software problems. When faced with an unfamiliar codebase, they often jump directly into editing, guess root causes from prompt snippets, invent recursive wrappers or monkey patches to avoid lower-level subsystems, and claim tests passed without executing them.

Fox provides an engineering decision framework that stops superficial workarounds. It directs agents to ground assumptions in code, trace control flow down to the owning implementation layer, apply the simplest complete fix (YAGNI), and disprove candidate fixes with targeted counterexamples across all relevant public entry points.

---

## How it works

Fox organizes agent execution into four sequential phases:

1. **Ground**: State the requested outcome, constraints, and done criteria. Inspect code, configuration, history, and runtime behavior before proposing a fix. For reproducible defects, write or run the smallest executable reproducer and confirm failure before modifying anything.
2. **Trace**: Follow one representative input through execution to observable output. Identify the component that owns the behavior across boundaries (wrappers to native engines, clients to servers, handlers to databases). Determine component ownership, editability, and testability. Form competing explanations and test which one is supported by evidence.
3. **Decide and Change**: Apply YAGNI (the simplest complete solution, not an incomplete workaround). If the owning component is editable, authorized, and testable, prefer repairing that layer. Avoid recursive wrappers or monkey patches that merely bypass underlying subsystems. If blocked by environment limits, document the blocker and label the result partial or blocked.
4. **Verify and Deliver**: Re-run the reproducer, check regressions, and test alternative public entry points that share the underlying engine. Disprove superficial fixes with targeted counterexamples. Report exact facts, changed files, and test results without unneeded narration.

---

## Installation

Fox installs directly into standard skill directories for leading coding environments using Python 3.10+ and standard library modules only:

| Coding Environment | Target Directory | Command |
|---|---|---|
| **OpenAI Codex** | `.agents/skills/fox` | `python3 install.py --agent codex --project /path/to/project` |
| **Anthropic Claude Code** | `.claude/skills/fox` | `python3 install.py --agent claude --project /path/to/project` |
| **Cursor** | `.cursor/skills/fox` | `python3 install.py --agent cursor --project /path/to/project` |

### Installation flags

```bash
# Install to Codex workspace
python3 install.py --agent codex --project /path/to/project

# Install to Claude Code workspace
python3 install.py --agent claude --project /path/to/project

# Install to Cursor workspace
python3 install.py --agent cursor --project /path/to/project

# Dry-run inspection (shows planned file copies without writing)
python3 install.py --agent codex --project /path/to/project --dry-run

# Replace existing installation
python3 install.py --agent codex --project /path/to/project --force
```

---

## Basic usage

Here is how an agent applies Fox to resolve a real defect:

1. **Defect**: Model serialization drops extra attributes when custom field aliases are enabled.
2. **Ground**: The agent creates a minimal 15-line test reproducing the issue and confirms it fails against current code.
3. **Trace**: Stepping through execution, the agent observes that while the Python layer accepts the model, serialization is delegated to a compiled native engine. The agent checks whether the engine is editable and testable in the workspace.
4. **Decide and Change**: Because the native engine is editable and test tools are available, the agent patches the serialization logic directly at the owning layer rather than wrapping high-level Python methods in recursive dictionary mappers.
5. **Verify and Deliver**: The agent runs the reproducer, executes existing regression tests, and validates that alternative public entry points (such as `TypeAdapter`) also serialize correctly. It reports changed files, exact test commands, and passing outputs.

---

## Optional utilities

Fox functions out of the box as a pure skill (`skills/fox/SKILL.md`). For tasks requiring local evidence records or staged pipelines, optional Python standard library utilities are bundled in `skills/fox/scripts/`:

- `proof.py`: A local integrity ledger to track evidence files, hypotheses, architecture decisions, and test logs with SHA-256 validation.
- `scaffold.py`: Generates staged directory workspaces with explicit input and output contracts for recurring pipelines.
- `audit.py`: Validates workflow directory structures and checks that declared stage outputs exist.

---

## Limitations

- **Skill guidance, not deterministic sandboxing**: Fox provides instructions that direct LLM reasoning; it cannot physically prevent a model from making errors if the model ignores instructions.
- **Hash validation verifies file integrity, not semantic truth**: The `proof.py` utility verifies that recorded files and test logs have not changed on disk, but does not evaluate whether an assertion is scientifically sound.
- **Host environment boundaries**: When a defect resides in a compiled dependency or foreign subsystem and the host environment lacks required compilers or permissions, Fox instructs agents to report the boundary as a blocker rather than fabricate success.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
