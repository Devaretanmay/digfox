# Fox & Fox Graph

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(stdlib)-success.svg)]()
[![Platform: Antigravity | Codex | Claude | Cursor](https://img.shields.io/badge/Agents-Antigravity%20%7C%20Codex%20%7C%20Claude%20%7C%20Cursor-purple.svg)]()
[![Tests: 51 Passed](https://img.shields.io/badge/Tests-51%20Passed-success.svg)]()

Fox and Fox Graph are two standalone, complementary agent skills for AI coding assistants.

- **Fox** (`/fox`): Investigates software defects, identifies root causes across boundaries, applies minimal complete fixes (YAGNI), and verifies outcomes with empirical evidence.
- **Fox Graph** (`/fox-graph`): Analyzes code relationships, maps patch diffs to upstream callers, identifies unpatched alternate execution paths, and generates prioritized regression verification plans.

Both skills can be installed and used independently. When used together, Fox handles engineering decisions and implementation, while Fox Graph supplies deterministic call-graph evidence and blast-radius coverage analysis.

---

## The Three Usage Modes

### Mode 1: Fox Alone (Investigation & Repair)
Use Fox when debugging issues, investigating root causes, fixing code, or auditing implementations.

Fox enforces a disciplined four-step engineering lifecycle:
1. **Ground**: Define outcomes, constraints, and done criteria. Inspect code and configuration. For reproducible defects, build the smallest reproducer and verify failure before modifying anything.
2. **Trace**: Follow one input through execution to observable output across boundaries (wrappers to engines, clients to servers). Identify the component that actually owns the behavior.
3. **Decide and Change**: Apply YAGNI (the simplest complete solution, not an incomplete workaround). Repair the owning component directly if accessible. Avoid superficial wrappers or monkey patches.
4. **Verify and Deliver**: Re-run the reproducer, check regressions, and test alternative public entry points. Report exact facts, changed files, and test commands.

### Mode 2: Fox Graph Alone (Impact & Coverage Analysis)
Use Fox Graph when analyzing proposed code changes, investigating blast radii, discovering unverified execution paths, or selecting regression tests across multi-module codebases.

Fox Graph provides graph-assisted patch analysis:
1. **Understand the patch**: Parse git diff hunks into concrete functions, methods, and classes.
2. **Query relationships**: Retrieve direct callers, transitive callers (up to depth 3), and cross-module consumers using local AST or GitNexus graphs.
3. **Detect coverage gaps**: Flag reachable entry points that exercise modified logic but lack targeted tests in the diff, and identify sibling entry points that bypass wrapper fixes.
4. **Generate verification plan**: Produce a prioritized list of up to five high-value regression checks explaining the entry point, suspected failure mode, and test intent.
5. **Report limitations**: Disclose statically unresolvable patterns (dynamic dispatch, reflection, native extensions).

### Mode 3: Combined Workflow (Fox + Fox Graph)
Use both skills on complex multi-module codebases where an internal engine or parser is shared by multiple public entry points:
- **Fox** governs the investigation, diagnosis, root-cause confirmation, and code modification.
- **Fox Graph** runs during the Trace and Verify phases to calculate the exact blast radius of the proposed fix, uncover sibling bypass routes, and generate regression checks.
- Fox incorporates these checks into its verification step before marking the repair complete.

Neither skill requires the other to be installed.

---

## Adoption Guide & Concrete Examples

For a detailed adoption guide with step-by-step walkthroughs, prompt recipes, and expected outputs, see [examples/ADOPTION_GUIDE.md](examples/ADOPTION_GUIDE.md).

| Guide / Walkthrough | When to Use | Key Advantage |
| :--- | :--- | :--- |
| **[Example 1: Localized Defect](examples/1-fox-alone-localized-defect/README.md)** | Single-site logic bugs, regex errors, off-by-one errors | **Fox alone**: Zero graph overhead; enforces reproducer-first fix and counterexample testing. |
| **[Example 2: Diff & PR Audit](examples/2-fox-graph-alone-diff-audit/README.md)** | Code reviews, PR blast-radius checks, test gap audits | **Fox Graph alone**: Non-destructive; parses diffs and generates prioritized regression targets. |
| **[Example 3: Cross-Module Repair](examples/3-combined-cross-module-repair/README.md)** | Core data structures, shared parsers, public entry points | **Both skills**: Fox drives root-cause repair while Fox Graph ensures all entry points are covered. |

---

## Installation

Install Fox alone, Fox Graph alone, or both skills together using `install.py`:

| Target Agent | Default Workspace Directory |
|---|---|
| **Google Antigravity** | `.agents/skills` (or `~/.gemini/config/skills` with `--global`) |
| **OpenAI Codex** | `.agents/skills` |
| **Anthropic Claude Code** | `.claude/skills` |
| **Cursor** | `.cursor/skills` |

### Installation Commands

```bash
# Install Fox alone (default)
python3 install.py --agent antigravity --skill fox --project /path/to/project

# Install Fox Graph alone
python3 install.py --agent antigravity --skill fox-graph --project /path/to/project

# Install both skills together
python3 install.py --agent antigravity --skill all --project /path/to/project

# Install globally for Antigravity (~/.gemini/config/skills)
python3 install.py --agent antigravity --skill all --global

# Install to Claude Code workspace
python3 install.py --agent claude --skill all --project /path/to/project

# Install to Cursor workspace
python3 install.py --agent cursor --skill all --project /path/to/project

# Preview installation without modifying files
python3 install.py --agent antigravity --skill all --dry-run
```

---

## Dependencies & Environment Support

### Fox Dependencies
- **Zero dependencies**: Fox runs using Python 3.10+ standard library modules only.
- Does not require Node.js, npm, or GitNexus.

### Fox Graph Dependencies
- **Default Python AST Provider (`python-ast`)**: Zero external dependencies. Uses Python 3.10+ standard library `ast` to parse repositories and trace call hierarchies locally.
- **Optional Multi-Language Provider (`gitnexus`)**: Optional engine for repositories containing TypeScript, JavaScript, Go, Rust, Java, C#, or C++. Requires Node.js (`npx`) on PATH. Runs embedded LadybugDB/SQLite locally inside `.gitnexus/`.
- GitNexus is completely optional and never required for basic Fox usage or Python Fox Graph usage.

---

## Bundled CLI Utilities

### Fox Utilities (`skills/fox/scripts/`)
- `proof.py`: Local integrity ledger to record hypotheses, architecture decisions, and test logs with SHA-256 validation.
- `scaffold.py`: Generates staged directory workspaces with explicit contracts for recurring workflows.
- `audit.py`: Validates workflow structures and verifies declared outputs.

Quickstart pipeline:
```bash
# Verify environment
python3 skills/fox/scripts/proof.py doctor

# Initialize a case record
python3 skills/fox/scripts/proof.py init --out cases/auth --question "Why does token refresh fail?" --target src/auth --intent build

# Record an observed code claim
python3 skills/fox/scripts/proof.py claim --statement "Token validation fails on clock skew" --evidence E001 --confidence observed --locator auth.py:22 --alternative "Token expired on server" --falsifier "Test with clock skew" cases/auth

# Record an architecture decision
python3 skills/fox/scripts/proof.py decision --choose "Add 5-second skew tolerance" --instead-of "Bypass check" --why "Minimal complete fix" --reversible --revisit-when "Auth spec changes" cases/auth

# Validate case integrity
python3 skills/fox/scripts/proof.py check cases/auth
```

### Fox Graph CLI (`skills/fox-graph/scripts/`)
- `fox_graph.py`: Standalone CLI to run patch coverage and blast-radius analysis.

```bash
# Analyze unstaged working tree diff using Python AST
python3 skills/fox-graph/scripts/fox_graph.py --repo . --provider python-ast

# Analyze staged changes with GitNexus
python3 skills/fox-graph/scripts/fox_graph.py --repo . --staged --provider gitnexus

# Output machine-readable JSON
python3 skills/fox-graph/scripts/fox_graph.py --repo . --diff patch.diff --json
```

---

## Limitations

- **Skill guidance, not sandboxing**: Skills provide structured reasoning instructions for LLMs; they cannot physically intercept models that ignore instructions.
- **Static call graphs are not runtime proofs**: Fox Graph maps statically visible AST call edges and imports. Dynamic dispatch (`getattr`, `eval`, dependency injection) and compiled extensions cannot be resolved statically. Fox Graph discloses these boundaries under Limitations.
- **Selective invocation**: Fox Graph is valuable for multi-module shared engines and cross-file refactors. For simple single-function logic bugs, Fox Graph adds unnecessary overhead; invoke Fox alone for localized fixes.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
