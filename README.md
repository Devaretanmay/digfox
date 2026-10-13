# Proofwork: Make coding agents investigate before they build

An agent skill that traces evidence, challenges assumptions, chooses simple solutions, and verifies its work.

Most AI coding agents jump directly from a prompt to writing code. Proofwork adds disciplined investigation, competing hypotheses, architectural trade-offs, and verification checks before marking work complete.

Works with Codex, Claude Code, and Cursor. Zero third-party dependencies (Python 3.10+ standard library only).

---

## What Proofwork Does

1. **Enforces investigation before generation**: Prevents agents from writing speculative code before establishing empirical baselines on existing files and runtime traces.
2. **Challenges assumptions**: Requires agents to provide an alternative explanation and a concrete falsifier before treating any claim as observed fact.
3. **Picks proportional solutions**: Forces agents to document at least one simpler alternative (e.g. a deterministic script instead of a multi-agent framework) and define a revisit condition.
4. **Local evidence snapshot ledger**: Copies cited evidence files into a local case folder and hashes them with SHA-256 to detect accidental edits, stale test logs, or path traversal.
5. **Decoupled forensic capability**: Works out of the box for source-level codebases; cleanly connects with the specialized REA Investigator (`Devaretanmay/rea-investigate`) for deep binary, IPC, or network forensics without prompt bloat.

---

## 60-Second Quickstart

All commands run using Python standard library tools:

```bash
# 1. Verify system environment
python3 skills/proofwork/scripts/proof.py doctor

# 2. Initialize a new investigation case
python3 skills/proofwork/scripts/proof.py init \
  --out ./cases/auth-demo \
  --question "Why does token refresh fail?" \
  --target "src/auth" \
  --intent build

# 3. Capture an immutable local snapshot of the cited source file
python3 skills/proofwork/scripts/proof.py evidence \
  --file src/auth/token.py \
  --kind source \
  --locator "token.py:15-30" \
  --note "Token expiration check logic" \
  ./cases/auth-demo

# 4. Register an observed claim with an alternative hypothesis and falsifier
python3 skills/proofwork/scripts/proof.py claim \
  --statement "Token validation fails due to 2-second client clock skew" \
  --evidence E001 \
  --confidence observed \
  --locator "token.py:22" \
  --alternative "Token is genuinely expired on server" \
  --falsifier "Test validation with simulated clock skew" \
  ./cases/auth-demo

# 5. Record an architectural decision with rejected simpler/complex alternatives
python3 skills/proofwork/scripts/proof.py decision \
  --choose "Add 5-second clock skew tolerance window" \
  --instead-of "Bypass expiration check completely" "Force user re-authentication" \
  --why "Minimal standard-compliant fix with zero breaking API changes" \
  --claims C001 \
  --reversible \
  --revisit-when "Auth specification deprecates skew window" \
  ./cases/auth-demo

# 6. Audit integrity and compile a human-readable markdown report
python3 skills/proofwork/scripts/proof.py check ./cases/auth-demo
python3 skills/proofwork/scripts/proof.py report ./cases/auth-demo
```

The compiled `REPORT.md` contains an auditable summary of all captured evidence, SHA-256 digests, competing hypotheses, architectural choices, and recorded test outputs.

---

## The Six-Stage Workflow

Proofwork guides agents through six ordered stages:

| Stage | Goal | Required Invariant | Blocking Condition |
|---|---|---|---|
| **1. Scope** | Define boundaries and goals | Clear question, target, and intent | Unbounded or unauthorized work |
| **2. Investigate** | Trace actual sources | SHA-256 evidence snapshots and falsifiers | Speculative claims lacking citations |
| **3. Decide** | Choose minimal approach | Documented alternatives and kill criteria | Single-option over-engineering |
| **4. Build** | Implement minimal slice | Thin vertical slice without side effects | Unreviewed mutations or scope creep |
| **5. Verify** | Execute test checks | Real test logs with negative cases | Missing failure or boundary tests |
| **6. Deliver** | Publish audit report | Verified evidence digests and declared risks | Unchecked hashes or unproven claims |

---

## Installation

Install Proofwork into your active coding agent workspace:

```bash
# Codex (.agents/skills/proofwork)
python3 install.py --agent codex --project /path/to/target/project

# Claude Code (.claude/skills/proofwork)
python3 install.py --agent claude --project /path/to/target/project

# Cursor (.cursor/skills/proofwork)
python3 install.py --agent cursor --project /path/to/target/project

# Preview changes without modifying files
python3 install.py --agent codex --project /path/to/target/project --dry-run

# Optional: Install alongside an existing local REA checkout
python3 install.py --agent codex --project /path/to/target/project \
  --rea-path /path/to/rea-investigate
```

---

## Trust Boundaries and Realistic Guarantees

Proofwork emphasizes epistemic honesty. To avoid misleading assurances:

* **Snapshot Ledger vs Blockchains**: Evidence files are copied into the case directory and SHA-256 protected in `case.json`. This detects accidental edits, stale test runs, or local file tampering. It is not an append-only distributed ledger; anyone with direct write permissions to the filesystem can edit both files and digests.
* **Test Recording vs Test Execution**: The `test` command stores operator- or agent-supplied execution logs and validates reported exit codes. It does not independently sandbox or execute test binaries.
* **Documentary Approval**: The `approve` subcommand logs an audit trail of operator consent. It does not generate OS permissions, network credentials, or legal authorizations.
* **Verification Status**: 21 automated regression tests pass locally (`python3 -m unittest discover -s tests -v`). Empirical agent performance improvements across public benchmarks are an open evaluation protocol outlined in [EVALUATION.md](EVALUATION.md).

For formal POMDP state transitions and theoretical evidence tuple definitions, see [DESIGN.md](DESIGN.md).

---

## Repository Structure

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
├── tests/                                 Regression test suite (21 automated tests)
├── examples/                              Reference end-to-end case (invoice reporting)
├── DESIGN.md                              Architecture decision record and formal spec
├── EVALUATION.md                          Empirical benchmark protocol
├── SOURCES.md                             Origin credits and legal boundaries
├── CITATION.cff                           Academic citation metadata
└── LICENSE                                MIT License
```

---

## Citation

```bibtex
@software{proofwork2026,
  author = {Devare, Tanmay},
  title = {Proofwork: Make coding agents investigate before they build},
  year = {2026},
  url = {https://github.com/Devaretanmay/proofwork},
  version = {1.0.0}
}
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
