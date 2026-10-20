# Fox

**Better fixes. Less guesswork.**

Fox helps AI coding agents find the root cause, make focused changes, and verify the result. Fox Graph helps them understand how changes affect the rest of a codebase.

---

## Choose Your Skill

Fox and Fox Graph are two standalone skills you install into your AI coding tool (Google Antigravity, Claude Code, Cursor, or OpenAI Codex). You can install either skill alone or both together.

| Skill | What It Does | When to Choose It |
| :--- | :--- | :--- |
| **Fox** | **Fix what's broken.**<br>Investigates bugs, identifies root causes, applies focused repairs, and verifies results. | You have a bug to fix, an unexpected test failure, or code to debug. |
| **Fox Graph** | **Know what else might break.**<br>Maps code relationships, identifies potentially affected paths, and helps select useful regression checks. | You are reviewing a pull request or checking how an edit impacts other files. |
| **Both** | **Fix the bug. Check the impact.**<br>Two independently installed skills that can be used together on complex tasks. | You are changing a shared core function or data structure used across multiple modules. |

*You do not need a third combined skill. Installing both skills allows your coding agent to use whichever capability your task needs.*

---

## Get Started

### 1. Install to Your Project

Run the installer inside your project directory. It requires only standard Python (version 3.10 or newer) with zero external dependencies.

#### Interactive Setup (Recommended)
Run the installer in your terminal to select your coding agent and skills:
```bash
python3 install.py
```

#### One-Line Command
Or specify your agent and skill directly:

```bash
# Google Antigravity or OpenAI Codex (installs to .agents/skills)
python3 install.py --agent antigravity --skill all

# Anthropic Claude Code (installs to .claude/skills)
python3 install.py --agent claude --skill all

# Cursor (installs to .cursor/skills)
python3 install.py --agent cursor --skill all
```

To install only Fox, pass `--skill fox`. To install only Fox Graph, pass `--skill fox-graph`.

---

## Your First Task

Once installed, start a new chat in your AI coding agent and try one of these prompts:

### If You Installed Fox
> "Investigate why this function returns the wrong result. Find the cause, fix it, and verify the change."

### If You Installed Fox Graph
> "Analyze this change and show which other parts of the codebase might be affected."

### If You Installed Both
> "Investigate this bug, check its impact across the codebase, implement a focused fix, and verify the relevant paths."

### How to Confirm It Loaded
- **Fox**: Your agent will first write a reproduction test to confirm the failure, trace the issue to the owning component, make a minimal fix, and run verification tests.
- **Fox Graph**: Your agent will map changed symbols, show caller hierarchies, and list regression tests to run.

If your agent does not recognize the skill, restart the chat session or tell the agent:
`Use instructions in .agents/skills/fox/SKILL.md`. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more details.

---

## Real Example

Consider a shared authentication header parser in a web framework:

```python
# A client sends a parameterless challenge
wa = WWWAuthenticate("bearer")
header = wa.to_header()
```

- **The bug**: `to_header()` returns `'Bearer '` with an illegal trailing space. Downstream HTTP parsers reject the request.
- **Without Fox**: An agent might patch the immediate caller or strip trailing spaces inside a wrapper. Sibling entry points (such as response headers and exception handlers) remain broken.
- **With Fox**: The agent traces execution to the owning serializer (`auth.py`), fixes the formatting at the source, and ensures that `from_header("Bearer") == WWWAuthenticate("bearer")` holds true in both directions.
- **With Fox Graph**: The agent inspects the blast radius across the repository, flagging that `Response.www_authenticate` and `Unauthorized.get_headers()` also call this code and require test coverage.

For step-by-step walkthroughs of real defects and pull request audits, see the [Adoption Guide](examples/ADOPTION_GUIDE.md).

---

## How It Works

### Plain English Concepts
- **Root cause**: The underlying reason something went wrong, rather than just the symptom you noticed.
- **Blast radius**: The other parts of a project potentially affected when code changes.
- **Regression**: Something that worked before but breaks after an edit.

### Fox Lifecycle
Fox guides your agent through four simple steps:
1. **Ground**: Inspect the code and build the smallest test that demonstrates the problem before touching production files.
2. **Trace**: Follow the input step-by-step through execution until finding the component that actually owns the behavior.
3. **Decide and Change**: Make the simplest complete fix at the owning layer. Avoid monkey-patches or wrapper workarounds.
4. **Verify and Deliver**: Re-run the reproducer, verify edge cases, and run the test suite to prove nothing else broke.

### Fox Graph Lifecycle
Fox Graph provides deterministic dependency analysis without requiring a server:
1. **Parse the patch**: Extracts modified functions, methods, and classes from the Git diff.
2. **Query relationships**: Uses local AST (Abstract Syntax Tree) parsing to trace direct and transitive callers up to depth 3.
3. **Detect coverage gaps**: Flags reachable code paths that lack tests in the proposed change.
4. **Suggest verification**: Generates a prioritized list of tests to run before merging.

---

## Advanced Setup

### Global Installation (Antigravity)
To make Fox available across all projects on your machine for Google Antigravity:
```bash
python3 install.py --agent antigravity --skill all --global
```
This installs skills to `~/.gemini/config/skills`.

### Non-Interactive CLI Automation
The installer supports automation flags for CI or setup scripts:
```bash
# Preview what would be installed without writing files
python3 install.py --agent antigravity --skill all --dry-run

# Safely replace an existing installation
python3 install.py --agent antigravity --skill all --force --project /path/to/project
```

### Advanced Fox Verification Utilities
Fox includes an optional evidence ledger (`proof.py`) located in `skills/fox/scripts/`:
```bash
# Verify your local environment
python3 skills/fox/scripts/proof.py doctor

# Initialize an evidence case
python3 skills/fox/scripts/proof.py init --out cases/auth --question "Why does token refresh fail?" --target src/auth --intent build

# Record an observed code claim
python3 skills/fox/scripts/proof.py claim --statement "Token validation fails due to 2-second client clock skew" --evidence E001 --confidence observed --locator token.py:22 --alternative "Token is genuinely expired on server" --falsifier "Test validation with simulated clock skew" cases/auth

# Record an architecture decision
python3 skills/fox/scripts/proof.py decision --choose "Add 5-second clock skew tolerance window" --instead-of "Bypass expiration check completely" "Force user re-authentication" --why "Minimal standard-compliant fix with zero breaking API changes" --claims C001 --reversible --revisit-when "Auth specification deprecates skew window" cases/auth

# Check case validity and export report
python3 skills/fox/scripts/proof.py check cases/auth
python3 skills/fox/scripts/proof.py report cases/auth
```

---

## Troubleshooting & Limitations

- **Skill guidance, not hard constraints**: Skills provide structured reasoning instructions for AI agents. They improve agent consistency, but cannot intercept models that ignore instructions.
- **Static code graphs**: Fox Graph uses static code analysis. Dynamic calls (such as runtime `getattr` or dependency injection) cannot be traced statically and are reported as limitations.
- **Multi-language projects**: Fox Graph defaults to Python AST with zero external dependencies. For TypeScript, JavaScript, Go, or Rust, Fox Graph can optionally use GitNexus if Node.js (`npx`) is available.

For common errors, reinstallation fixes, and agent setup tips, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## Contributing & License

Contributions, defect reports, and discussions are welcome. Please open an issue or pull request on GitHub:
https://github.com/Devaretanmay/fox

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
