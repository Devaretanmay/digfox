# Digfox

> **TL;DR:** Digfox is an open-source skill that stops AI coding agents from guessing. It forces them to trace actual evidence, challenge their own assumptions, pick the simplest fix, and prove it works with real tests before touching your code.

Works with Codex, Claude Code, and Cursor. Built with standard Python 3.10+ (zero third-party dependencies, zero required cloud accounts).

---

## Why this exists (and why coding agents break things)

You paste a bug report into your AI coding assistant. Within five seconds, the model writes a 300-line refactor, invents helper functions that do not exist in your codebase, swaps your database queries for an unneeded multi-agent queue, and cheerfully announces that everything is fixed.

You run it. It crashes immediately.

We built Digfox because we got tired of babysitting agents that write code before they understand what broke. Most agents fail because they lack basic engineering discipline: they jump straight into generation without verifying facts.

Digfox adds guardrails that turn your agent into a disciplined engineer:

* **Investigate first, code second:** The agent must inspect actual files and trace real inputs to outputs before modifying a single line of code.
* **Challenge assumptions:** The agent cannot treat a bug theory as fact without documenting an alternative explanation and a concrete way to disprove it.
* **Pick the simplest fix:** The agent must explain why a 15-line script or a simple function is not enough before reaching for complex architectures or new dependencies.
* **Catch drift with local evidence:** The agent saves local snapshots of consulted code with SHA-256 hashes, catching accidental edits, stale test runs, and broken paths.
* **Decoupled forensic depth:** Works out of the box for normal coding tasks; plugs into the optional REA Investigator (`Devaretanmay/rea-investigate`) when you need deep binary, IPC, or network packet analysis.

---

## Quickstart in 60 seconds

Everything runs locally with standard Python tools:

```bash
# 1. Check your local environment
python3 skills/digfox/scripts/proof.py doctor

# 2. Start a new investigation case
python3 skills/digfox/scripts/proof.py init \
  --out ./cases/auth-demo \
  --question "Why does token refresh fail?" \
  --target "src/auth" \
  --intent build

# 3. Save a snapshot of the code you inspected
python3 skills/digfox/scripts/proof.py evidence \
  --file src/auth/token.py \
  --kind source \
  --locator "token.py:15-30" \
  --note "Token expiration check logic" \
  ./cases/auth-demo

# 4. Record what you found, plus an alternative explanation and a test to disprove it
python3 skills/digfox/scripts/proof.py claim \
  --statement "Token validation fails due to 2-second client clock skew" \
  --evidence E001 \
  --confidence observed \
  --locator "token.py:22" \
  --alternative "Token is genuinely expired on server" \
  --falsifier "Test validation with simulated clock skew" \
  ./cases/auth-demo

# 5. Record your decision, what you rejected, and when to change your mind
python3 skills/digfox/scripts/proof.py decision \
  --choose "Add 5-second clock skew tolerance window" \
  --instead-of "Bypass expiration check completely" "Force user re-authentication" \
  --why "Minimal standard-compliant fix with zero breaking API changes" \
  --claims C001 \
  --reversible \
  --revisit-when "Auth specification deprecates skew window" \
  ./cases/auth-demo

# 6. Verify case integrity and generate a readable markdown report
python3 skills/digfox/scripts/proof.py check ./cases/auth-demo
python3 skills/digfox/scripts/proof.py report ./cases/auth-demo
```

When you run `report`, Digfox generates a clean `REPORT.md` inside your case folder summarizing all consulted evidence, file hashes, competing theories, architectural choices, and test outputs.

---

## How it works under the hood

Digfox guides your agent through a strict six-stage sequence:

```text
Scope -> Investigate -> Decide -> Build -> Verify -> Deliver
```

1. **Scope:** Define the exact question, target directory, and boundaries. If an action needs human approval (such as modifying production data or calling external APIs), flag it here first.
2. **Investigate:** Trace one real input through to its output. Save evidence files with SHA-256 hashes. Every observed claim requires an alternative hypothesis and a falsification test.
3. **Decide:** Choose the simplest fix that solves the problem. Document at least one rejected alternative and a condition that would make you revisit the choice.
4. **Build:** Write a minimal, working slice of code. If you are building a reusable workflow, use `scaffold.py` to create explicit input and output contracts between stages.
5. **Verify:** Run actual tests and record the output. Check both expected successes and deliberate failure cases.
6. **Deliver:** Summarize what was inspected, what changed, what tests ran, and what risks remain.

---

## How the evidence ledger works

The evidence ledger (`proof.py`) is intentionally dead simple.

It is **not** a blockchain, a cloud database, or a tamper-proof cryptographic audit log. It is a local directory containing:

* `case.json`: A plain JSON file storing your investigation question, claims, trade-offs, and test logs.
* `evidence/`: Local copies of the files you inspected.
* SHA-256 hashes: Cryptographic fingerprints of those copied files.

Whenever you run `proof.py check`, it recalculates the hashes on disk and compares them against `case.json`. If you accidentally edited an evidence file, swapped a test log, or broke a path, the check catches it immediately.

---

## Honest trade-offs and gotchas

We prefer to tell you what this tool does not do before you discover it in production:

* **File hashes check bytes, not truth:** A SHA-256 hash proves the file on disk has not changed since you saved it. It does not prove the code is bug-free or that the author wrote good logic.
* **Test recording is not sandboxed execution:** The `test` command saves test logs and records exit codes that you or the agent provide. It does not run test binaries inside an isolated container.
* **Documentary approval is not an IAM policy:** The `approve` command logs human consent for an audit record. It does not grant operating system permissions or network credentials.
* **Zero external dependencies:** The core tool runs entirely on Python's standard library. No `pip install`, no API keys, and no telemetry sent to outside servers.

---

## Installing Digfox

Install Digfox directly into your coding agent workspace:

```bash
# Codex (.agents/skills/digfox)
python3 install.py --agent codex --project /path/to/your/project

# Claude Code (.claude/skills/digfox)
python3 install.py --agent claude --project /path/to/your/project

# Cursor (.cursor/skills/digfox)
python3 install.py --agent cursor --project /path/to/your/project

# Preview what will be installed without touching files
python3 install.py --agent codex --project /path/to/your/project --dry-run

# Optional: Install alongside an existing local REA checkout
python3 install.py --agent codex --project /path/to/your/project \
  --rea-path /path/to/rea-investigate
```

---

## Repository layout

```text
digfox/
├── install.py                             Agent skill installer (Codex, Claude, Cursor)
├── skills/
│   └── digfox/
│       ├── SKILL.md                       Agent instructions and decision rules
│       ├── scripts/
│       │   ├── proof.py                   Evidence ledger CLI and report generator
│       │   ├── scaffold.py                Staged contract workspace generator
│       │   └── audit.py                   Structural validation checker
│       ├── references/                    Reference documentation and interop rules
│       └── assets/                        Outcome, stage, and review templates
├── tests/                                 Regression and documentation smoke tests
├── examples/                              Reference end-to-end case (invoice reporting)
├── DESIGN.md                              Architecture decisions and tradeoffs
├── EVALUATION.md                          Empirical benchmark plan
├── SOURCES.md                             Origin credits and legal boundaries
└── LICENSE                                MIT License
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
