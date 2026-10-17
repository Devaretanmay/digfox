# Proofwork: Make coding agents investigate before they build

Most AI coding agents jump straight to editing code before they understand what broke. Proofwork gives agents a simple, disciplined workflow: trace real evidence, challenge assumptions, choose the simplest fix, and verify with actual tests before calling the job done.

Works with Codex, Claude Code, and Cursor. Built with standard Python 3.10+ (no external dependencies, no required cloud accounts).

---

## What Proofwork does

1. **Investigate first, code second**: Stops agents from writing speculative fixes before they read the relevant files and trace actual inputs to outputs.
2. **Challenge assumptions**: Forces the agent to document an alternative explanation and a way to disprove its hypothesis before treating a claim as fact.
3. **Pick the simplest fix**: Requires the agent to justify why a simple script or function isn't enough before introducing complex abstractions or new libraries.
4. **Local evidence snapshot ledger**: Copies cited files into a local folder and hashes them with SHA-256 to catch accidental edits, file drift, and stale test outputs.
5. **Decoupled forensic depth**: Works out of the box for routine coding; connects cleanly with the specialized REA Investigator (`Devaretanmay/rea-investigate`) for deep binary, IPC, and network forensics without bloating your everyday prompts.

---

## 60-second quickstart

Everything runs locally with Python standard library tools:

```bash
# 1. Check your local environment
python3 skills/proofwork/scripts/proof.py doctor

# 2. Start a new investigation case
python3 skills/proofwork/scripts/proof.py init \
  --out ./cases/auth-demo \
  --question "Why does token refresh fail?" \
  --target "src/auth" \
  --intent build

# 3. Save a snapshot of the code you inspected
python3 skills/proofwork/scripts/proof.py evidence \
  --file src/auth/token.py \
  --kind source \
  --locator "token.py:15-30" \
  --note "Token expiration check logic" \
  ./cases/auth-demo

# 4. Record what you found, plus an alternative explanation and a test to disprove it
python3 skills/proofwork/scripts/proof.py claim \
  --statement "Token validation fails due to 2-second client clock skew" \
  --evidence E001 \
  --confidence observed \
  --locator "token.py:22" \
  --alternative "Token is genuinely expired on server" \
  --falsifier "Test validation with simulated clock skew" \
  ./cases/auth-demo

# 5. Record your decision, what you rejected, and when to change your mind
python3 skills/proofwork/scripts/proof.py decision \
  --choose "Add 5-second clock skew tolerance window" \
  --instead-of "Bypass expiration check completely" "Force user re-authentication" \
  --why "Minimal standard-compliant fix with zero breaking API changes" \
  --claims C001 \
  --reversible \
  --revisit-when "Auth specification deprecates skew window" \
  ./cases/auth-demo

# 6. Verify case integrity and generate a readable markdown report
python3 skills/proofwork/scripts/proof.py check ./cases/auth-demo
python3 skills/proofwork/scripts/proof.py report ./cases/auth-demo
```

The resulting `REPORT.md` provides an auditable summary of inspected files, SHA-256 hashes, competing explanations, chosen approaches, and test results.

---

## The six-stage workflow

Proofwork guides agents through six sequential stages:

| Stage | Goal | What is required | What blocks progress |
|---|---|---|---|
| **1. Scope** | Define boundaries and goals | Clear question, target path, and intent | Unbounded or unauthorized work |
| **2. Investigate** | Trace actual sources | Evidence snapshots with SHA-256 digests | Speculative claims lacking citations |
| **3. Decide** | Choose the minimal approach | Documented alternatives and revisit rules | Unjustified single-option complexity |
| **4. Build** | Implement the minimal slice | Smallest working change with no side effects | Unreviewed mutations or scope creep |
| **5. Verify** | Run actual tests | Real test logs with both positive and negative checks | Missing failure or boundary test logs |
| **6. Deliver** | Summarize the results | Verified evidence hashes and declared risks | Unchecked hashes or unproven claims |

---

## Installation

Install Proofwork into your active coding agent directory:

```bash
# Codex (.agents/skills/proofwork)
python3 install.py --agent codex --project /path/to/your/project

# Claude Code (.claude/skills/proofwork)
python3 install.py --agent claude --project /path/to/your/project

# Cursor (.cursor/skills/proofwork)
python3 install.py --agent cursor --project /path/to/your/project

# Preview what will be installed without touching files
python3 install.py --agent codex --project /path/to/your/project --dry-run

# Optional: Install alongside an existing local REA checkout
python3 install.py --agent codex --project /path/to/your/project \
  --rea-path /path/to/rea-investigate
```

---

## Honest limits: what Proofwork does and does not do

We believe in being upfront about what this tool actually guarantees:

* **Snapshot ledger vs blockchain**: Files are copied into a local folder and hashed with SHA-256 in `case.json`. This catches accidental file edits, drift, and stale test outputs. It is not an immutable distributed ledger; anyone with write access to the filesystem can edit both the files and the JSON.
* **Test recording vs test execution**: The `test` command saves test logs and records exit codes that you or the agent provide. It does not run test binaries inside an isolated sandbox.
* **Documentary approval**: The `approve` command logs human sign-off for an audit record. It does not grant operating system permissions or API access.
* **Status**: 22 automated unit and smoke tests pass locally. Measuring how much Proofwork improves agent success on real GitHub issues is an open benchmarking plan described in [EVALUATION.md](EVALUATION.md).

For design rationale and tradeoffs, see [DESIGN.md](DESIGN.md).

---

## Repository structure

```text
proofwork/
├── install.py                             Agent skill installer (Codex, Claude, Cursor)
├── skills/
│   └── proofwork/
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
