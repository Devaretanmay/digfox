# Digfox

> **TL;DR:** Digfox is an open-source agent skill that stops AI coding assistants from guessing. It forces them to trace actual evidence, challenge their own assumptions, pick the simplest fix, and verify it works with real tests before touching your code.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(stdlib)-success.svg)]()
[![Platform: Codex | Claude | Cursor](https://img.shields.io/badge/Agents-Codex%20%7C%20Claude%20%7C%20Cursor-purple.svg)]()
[![Tests: 22 Passed](https://img.shields.io/badge/Tests-22%20Passed-success.svg)]()

[Quickstart](#quickstart-in-60-seconds) | [Why This Exists](#why-this-exists-and-why-coding-agents-break-things) | [How It Works](#how-it-works-under-the-hood) | [Agent Compatibility](#installing-digfox-into-your-agent) | [Honest Trade-offs](#honest-trade-offs-and-gotchas)

---

## Why this exists (and why coding agents break things)

You paste a bug report into your AI coding assistant. Within five seconds, the model writes a 300-line refactor, invents helper functions that do not exist in your codebase, swaps your database queries for an unneeded multi-agent queue, and cheerfully announces that everything is fixed.

You run it. It crashes immediately.

We built Digfox because we got tired of babysitting agents that write code before they understand what broke. Most agents fail because they lack basic engineering discipline: they jump straight into generation without verifying facts.

| The Default Coding Agent | The Digfox-Grounded Agent |
|---|---|
| Guesses the root cause from a prompt snippet | Traces real code paths from input to output |
| Invents non-existent helper functions and APIs | Cites exact file locators with SHA-256 byte snapshots |
| Reaches for complex multi-agent architectures | Justifies why a 15-line script is not enough first |
| Claims tests passed without running them | Captures real test logs with both success and failure cases |
| Leaves you to debug a broken production branch | Delivers an auditable case report with documented risks |

---

## Quickstart in 60 seconds

Everything runs locally using Python's standard library. No `pip install`, no API keys, and no cloud accounts required.

```bash
# 1. Check your local environment
python3 skills/digfox/scripts/proof.py doctor

# 2. Start a new investigation case
python3 skills/digfox/scripts/proof.py init \
  --out ./cases/auth-demo \
  --question "Why does token refresh fail?" \
  --target "src/auth" \
  --intent build

# 3. Save an immutable snapshot of the code you inspected
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

When you run `report`, Digfox compiles a clean `REPORT.md` inside your case folder summarizing all consulted evidence, file hashes, competing theories, architectural choices, and test outputs.

---

## How it works under the hood

Digfox guides your agent through a strict six-stage sequence:

```text
Scope -> Investigate -> Decide -> Build -> Verify -> Deliver
```

| Stage | Goal | What is required | What blocks progress |
|---|---|---|---|
| **1. Scope** | Define boundaries and goals | Clear question, target path, and intent | Unbounded or unauthorized work |
| **2. Investigate** | Trace actual sources | Evidence snapshots with SHA-256 digests | Speculative claims lacking citations |
| **3. Decide** | Choose the minimal approach | Documented alternatives and revisit rules | Unjustified single-option complexity |
| **4. Build** | Implement the minimal slice | Smallest working change with no side effects | Unreviewed mutations or scope creep |
| **5. Verify** | Run actual tests | Real test logs with both positive and negative checks | Missing failure or boundary test logs |
| **6. Deliver** | Summarize the results | Verified evidence hashes and declared risks | Unchecked hashes or unproven claims |

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

## Installing Digfox into your agent

Digfox installs directly into standard agent skill directories across leading development environments:

| Coding Environment | Target Directory | Installer Flag |
|---|---|---|
| **OpenAI Codex** | `.agents/skills/digfox` | `--agent codex` |
| **Anthropic Claude Code** | `.claude/skills/digfox` | `--agent claude` |
| **Cursor** | `.cursor/skills/digfox` | `--agent cursor` |

Run the installer with your project path:

```bash
# Install to Codex workspace
python3 install.py --agent codex --project /path/to/your/project

# Install to Claude Code workspace
python3 install.py --agent claude --project /path/to/your/project

# Install to Cursor workspace
python3 install.py --agent cursor --project /path/to/your/project

# Dry-run inspection (shows planned file copies without writing)
python3 install.py --agent codex --project /path/to/your/project --dry-run

# Optional: Install alongside a local REA Investigator checkout
python3 install.py --agent codex --project /path/to/your/project \
  --rea-path /path/to/rea-investigate
```

---

## Repository layout

```text
digfox/
├── install.py                             Universal agent installer (Codex, Claude, Cursor)
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
