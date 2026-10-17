# Architecture and design decisions

Why Digfox is built as a lightweight skill, not a massive prompt or a cloud service.

---

## Why Digfox exists

Most AI coding agents fail in predictable ways:
1. They jump straight into editing files before reading how your system actually works.
2. They invent explanations that sound plausible but aren't supported by the code.
3. They reach for complex architectures (like five cooperating background agents) when a 20-line Python script solves the problem cleanly.
4. They tell you everything works without running a single test.

Digfox adds guardrails to stop that. It gives agents a simple sequence: understand the problem, check evidence, pick the simplest fix, write code, run tests, and report what actually happened.

---

## Decisions we made and options we rejected

| Option | What we chose | Why |
|---|---|---|
| Merge REA and Digfox into one massive file | **Rejected** | REA is built for deep reverse engineering (binaries, Electron apps, IPC, network traffic). Shoving all those instructions into every routine coding prompt adds token waste and confuses the model. |
| Replace REA with a generic research checklist | **Rejected** | A checklist is useless when you actually need deep binary decompilation or network traffic capture. Keeping REA as a decoupled optional tool gives you forensic depth without daily prompt bloat. |
| Spin up a swarm of background agents by default | **Rejected** | Multi-agent swarms look great in demos, but in production they burn tokens, introduce race conditions, and create confusing failure modes. Default to one capable agent and deterministic scripts. |
| Lightweight front door with an optional evidence ledger | **Accepted** | Digfox works out of the box with standard Python. If you want deep forensics, connect REA. If you want an audit trail, use the CLI ledger. |

---

## How the evidence ledger works

The evidence ledger (`proof.py`) is intentionally boring.

It is **not** a blockchain, a cloud database, or a tamper-proof cryptographic audit log. It is a local directory containing:
* A `case.json` file storing metadata (questions, targets, claims, decisions, test logs).
* An `evidence/` folder storing copies of files you referenced.
* SHA-256 hashes of every copied file.

When you run `python3 skills/digfox/scripts/proof.py check ./cases/your-case`, it hashes the files on disk and compares them against `case.json`. If you accidentally edited an evidence file, swapped a test log, or broke a path, the check fails.

### What it guarantees
* It catches accidental file modifications, file drift, and stale test outputs.
* It ensures claims link to real files with line numbers.
* It forces the agent to record an alternative hypothesis and a falsification test before marking a claim as observed.
* It stops directory traversal attacks by validating that paths stay inside the case directory.

### What it does not guarantee
* It does not prove a claim is factually true. A hash only proves the bytes haven't changed since they were saved.
* It does not execute tests. The `test` command stores logs that you or the agent provide.
* It does not grant permissions. The `approve` command is a notebook entry for humans reviewing the work, not an IAM role.
* It does not protect against someone with write access who deliberately edits both the file and the hash in `case.json`.

---

## The six-stage workflow

Digfox guides agents through six gates:

```text
Scope -> Investigate -> Decide -> Build -> Verify -> Deliver
```

1. **Scope**: Define the exact question, target directory, and boundaries. If an action needs human sign-off (like touching production databases), flag it here.
2. **Investigate**: Trace one real input to its output. Save evidence files with SHA-256 hashes. For every claim, require an alternative explanation and a way to disprove it.
3. **Decide**: Choose the simplest approach. Document at least one rejected alternative and a condition that would make you revisit the choice.
4. **Build**: Write a minimal vertical slice. If you need a multi-stage workflow, use `scaffold.py` to generate explicit contracts between steps.
5. **Verify**: Run tests and record the output. Check both success cases and failure cases.
6. **Deliver**: Summarize what was inspected, what changed, what was tested, and what risks remain.
