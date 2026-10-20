# Fox

**Better fixes. Less guesswork. Clear exploration.**

Fox is a suite of three independent Agent Skills for AI coding assistants (Google Antigravity, Claude Code, Cursor, and OpenAI Codex):

- **Fox**: Fix what's broken (root-cause debugging and verified repairs).
- **Fox Graph**: Know what else might break (dependency graphs and patch blast radius).
- **Fox Explore**: Understand your code. Explore what's possible (architecture, research, and recommendations).

Each skill works completely on its own with zero dependencies on the others. You can install one, any combination, or all three.

---

## Choose Your Skill

| Skill | What It Does | When to Choose It |
| :--- | :--- | :--- |
| **Fox** | **Fix what's broken.**<br>Investigates bugs, identifies root causes, applies focused repairs, and verifies results. | You have a bug to fix, an unexpected test failure, or code to debug. |
| **Fox Graph** | **Know what else might break.**<br>Maps code relationships, identifies potentially affected paths, and selects targeted regression checks. | You are reviewing a pull request or checking how an edit impacts other files. |
| **Fox Explore** | **Understand your code. Explore what's possible.**<br>Explains unfamiliar code, researches external open-source alternatives, compares architectures, and advises on trade-offs. | You are onboarding to a repository, evaluating an architectural choice, or researching technical options. |
| **Combinations** | **Mix and match freely.**<br>Install any combination. Skills cooperate smoothly without cross-dependencies. | You want to explore architectural options (`fox-explore`), check blast radius (`fox-graph`), and fix defects (`fox`). |

---

## Get Started

### 1. Install to Your Project

Run the installer inside your project directory. It requires only standard Python (version 3.10 or newer) with zero external dependencies.

#### Interactive Setup (Recommended)
Run the wizard in your terminal to select your coding agent and skills:
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

#### Install Specific Skills or Combinations
```bash
# Install only Fox Explore
python3 install.py --agent claude --skill fox-explore

# Install only Fox
python3 install.py --agent cursor --skill fox

# Install a custom combination (Fox + Fox Explore)
python3 install.py --agent antigravity --skill fox,fox-explore
```

---

## Your First Task

Once installed, start a new chat in your AI coding agent and try one of these beginner-friendly examples:

### If You Installed Fox
> "Investigate why this function returns the wrong result. Find the cause, fix it, and verify the change."

### If You Installed Fox Graph
> "Analyze this change and show which other parts of the codebase might be affected."

### If You Installed Fox Explore
> "Explain this repository to someone seeing it for the first time. Walk me through the request flow and explain what you would improve and what you would leave alone."

### If You Installed All Three
> "Explore architectural alternatives for our caching layer, check the blast radius across dependent handlers, and implement the verified change."

### How to Confirm It Loaded
- **Fox**: Your agent writes a reproduction test first, traces execution to the owning component, applies a minimal fix, and runs verification checks.
- **Fox Graph**: Your agent maps changed symbols from the Git diff, displays caller hierarchies, and highlights untested public paths.
- **Fox Explore**: Your agent answers directly, grounds local explanations in real repository paths, separates facts from inferences, and provides practical recommendations.

If your agent does not recognize a skill, restart the chat session or tell the agent:
`Use instructions in .agents/skills/fox-explore/SKILL.md`. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more tips.

---

## Real Example

Consider a shared authentication header parser in a web framework:

```python
# A client sends a parameterless challenge
wa = WWWAuthenticate("bearer")
header = wa.to_header()
```

- **The bug**: `to_header()` returns `'Bearer '` with an illegal trailing space. Downstream HTTP parsers reject the request.
- **With Fox**: The agent traces execution to the owning serializer (`auth.py`), fixes formatting at the source, and ensures that `from_header("Bearer") == WWWAuthenticate("bearer")` holds true in both directions.
- **With Fox Graph**: The agent inspects the blast radius across the repository, flagging that `Response.www_authenticate` and `Unauthorized.get_headers()` also call this code and require test coverage.
- **With Fox Explore**: The agent explains the header specification RFC, compares the framework's token validation with standard libraries (such as `PyJWT` or `authlib`), and advises on backward compatibility trade-offs before changes are made.

For step-by-step walkthroughs of real defects and pull request audits, see the [Adoption Guide](examples/ADOPTION_GUIDE.md).

---

## How It Works

### Plain English Concepts
- **Root cause**: The underlying reason something went wrong, rather than just the symptom you noticed.
- **Blast radius**: The other parts of a project potentially affected when code changes.
- **Regression**: Something that worked before but breaks after an edit.
- **Grounding**: Proving claims using concrete repository files or primary documentation instead of guessing.

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

### Fox Explore Lifecycle
Fox Explore provides read-only codebase understanding and technical research:
1. **Understand the question**: Clarify scope and match investigation depth to the question.
2. **Investigate the evidence**: Inspect repository files, tests, configs, and verified external sources.
3. **Connect and evaluate**: Relate implementation details to documented practices, separating facts from inference.
4. **Explain and recommend**: Answer directly, cite exact paths, evaluate trade-offs, and suggest next steps.

---

## Advanced Setup

### Global Installation (Antigravity)
To make skills available across all projects on your machine for Google Antigravity:
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
- **Read-only exploration**: Fox Explore is read-only by default and will not modify repository files or scaffold architectures unless explicitly requested.
- **Static code graphs**: Fox Graph uses static code analysis. Dynamic calls (such as runtime `getattr` or dependency injection) cannot be traced statically and are reported as limitations.
- **Multi-language projects**: Fox Graph defaults to Python AST with zero external dependencies. For TypeScript, JavaScript, Go, or Rust, Fox Graph can optionally use GitNexus if Node.js (`npx`) is available.

For common errors, reinstallation fixes, and agent setup tips, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## Contributing & License

Contributions, defect reports, and discussions are welcome. Please open an issue or pull request on GitHub:
https://github.com/Devaretanmay/fox

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
