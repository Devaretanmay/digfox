# Proofwork: Epistemically Bounded Software Synthesis via Cryptographically Anchored Evidence Ledgers

## Abstract

Autonomous software engineering agents powered by large language models frequently suffer from stochastic divergence, ungrounded causal assertions, and unfalsifiable architectural modifications. When unconstrained, agents often construct speculative abstractions before establishing empirical system baselines, generating synthetic code paths that fail under operational boundary conditions. 

Proofwork formalizes an epistemic governance framework and runtime protocol for autonomous software engineering. Operating as a deterministic state machine over an immutable local evidence ledger, Proofwork enforces cryptographic content addressing (SHA-256), competing-hypothesis falsification, and monotonic progression through a six-stage verification gate pipeline: **Scope**, **Investigate**, **Decide**, **Build**, **Verify**, and **Deliver**. The framework unifies the empirical reverse-engineering rigor of deep forensic analysis with outcome-driven contract scaffolding, guaranteeing auditable provenance for every proposed modification while requiring zero external dependencies.

---

## 1. Theoretical Formulation

Proofwork models the interaction between an autonomous coding agent and an arbitrary software repository as a partially observable discrete-time transition system augmented with an append-only cryptographic ledger:

$$\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{O}, \mathcal{T}, \Omega, \mathcal{L} \rangle$$

Where:
* $\mathcal{S}$ denotes the latent space of repository states, dependencies, and execution contexts.
* $\mathcal{A}$ denotes the action alphabet available to the agent (file inspection, AST traversal, test execution, synthesis).
* $\mathcal{O}$ denotes the observation space emitted by environment processes and tools.
* $\mathcal{T}: \mathcal{S} \times \mathcal{A} \to \mathcal{S}$ represents state transition dynamics under operational modifications.
* $\Omega: \mathcal{S} \times \mathcal{A} \to \mathcal{O}$ denotes observation emission probabilities.
* $\mathcal{L}$ denotes the tamper-evident epistemic ledger.

### 1.1 Cryptographic Evidence Anchoring

Every discrete observation admitted into the agent reasoning trace must be registered in the ledger as a tuple:

$$\mathbf{e}_k = \langle \tau_k, \mathbf{uri}_k, \mathbf{h}_k, \mathbf{c}_k, \mathcal{V}_k \rangle$$

Where:
* $\tau_k \in \{\text{source}, \text{observation}, \text{test-log}, \text{artifact}\}$ denotes the artifact category.
* $\mathbf{uri}_k$ represents the immutable canonical locator within the case container.
* $\mathbf{h}_k = \text{SHA256}(\text{bytes}_k)$ represents the cryptographic digest computed at ingestion time $t_k$.
* $\mathbf{c}_k$ denotes the textual context or line-range bounds.
* $\mathcal{V}_k \in \{0, 1\}$ represents the verification state under cyclic integrity audits.

Let $\text{bytes}_k(t)$ be the state of file $k$ at evaluation time $t \ge t_k$. The integrity invariant enforced by the ledger verifier is:

$$\forall \mathbf{e}_k \in \mathcal{L}, \quad \text{SHA256}(\text{bytes}_k(t)) = \mathbf{h}_k$$

Any violation ($\mathbf{h}_k(t) \neq \mathbf{h}_k$) immediately halts pipeline execution, invalidating downstream claims.

### 1.2 Adversarial Falsification Invariant

An empirical claim $C_i \in \mathcal{C}$ asserting behavioral properties of target code is prohibited from entering status `observed` unless it satisfies Popperian falsifiability criteria:

$$\text{Status}(C_i) = \text{observed} \implies \left( E(C_i) \neq \emptyset \;\land\; H_{\text{alt}}(C_i) \neq \emptyset \;\land\; F(C_i) \neq \emptyset \right)$$

Where:
* $E(C_i) \subseteq \{\mathbf{e}_1, \dots, \mathbf{e}_n\}$ denotes non-empty supporting cryptographic evidence references.
* $H_{\text{alt}}(C_i)$ denotes an explicitly articulated counter-hypothesis or competing explanation.
* $F(C_i)$ denotes a concrete operational falsifier (a deterministic test or observation that would disprove the claim).

### 1.3 Architectural Minimalism and Proportionality

To prevent speculative complexity (such as unnecessary multi-agent orchestration, redundant distributed brokers, or uncalled wrapper libraries), architectural decisions $D_j \in \mathcal{D}$ must fulfill:

$$\forall D_j \in \mathcal{D}, \quad |\text{Alternatives}(D_j)| \ge 1 \;\land\; \text{RevisitCondition}(D_j) \neq \emptyset \;\land\; \text{Reversibility}(D_j) \in \{\text{true}, \text{false}\}$$

---

## 2. The Six-Stage Gate Protocol

Progression through software synthesis is governed by a strictly ordered finite state automaton:

```text
+---------+     +-------------+     +----------+     +---------+     +----------+     +-----------+
|  Scope  | --> | Investigate | --> |  Decide  | --> |  Build  | --> |  Verify  | --> |  Deliver  |
+---------+     +-------------+     +----------+     +---------+     +----------+     +-----------+
```

Transitions are guarded by formal barrier invariants:

| Gate | Formal Barrier Invariant | Required Artifact | Rejection Condition |
|---|---|---|---|
| **1. Scope** | $B_{\text{scope}} \iff (\text{Question} \neq \emptyset) \land (\text{Target} \neq \emptyset) \land \text{Authorized}$ | `case.json` initialization | Open-ended exploration without boundary definition |
| **2. Investigate** | $B_{\text{inv}} \iff \forall C \in \mathcal{C}, (E(C) \neq \emptyset \land F(C) \neq \emptyset)$ | SHA-256 evidence snapshots + counter-hypotheses | Speculative narrative lacking byte-level citations |
| **3. Decide** | $B_{\text{dec}} \iff \forall D \in \mathcal{D}, (|\text{Alt}(D)| \ge 1 \land \text{Revisit}(D) \neq \emptyset)$ | Decision record with falsification boundary | Unexamined single-option architectures |
| **4. Build** | $B_{\text{bld}} \iff \text{SliceIsMinimal} \land \text{NoUnapprovedSideEffects}$ | Staged implementation patch | Unbounded scope expansion or external network calls |
| **5. Verify** | $B_{\text{ver}} \iff \exists T \in \mathcal{T}_{\text{exec}} \text{ s.t. } (T_{\text{golden}} \land T_{\text{negative}})$ | Captured runtime execution logs | Absence of negative or fault-injection test logs |
| **6. Deliver** | $B_{\text{del}} \iff \text{AllHashesValid} \land \text{AuditClean} \land \text{LimitationsDeclared}$ | Final validated report (`REPORT.md`) | Incomplete ledger, broken paths, or unqualified success claims |

---

## 3. System Architecture and Component Decoupling

Proofwork intentionally rejects monolithic instruction bundling in favor of cleanly decoupled, complementary modules:

```text
proofwork/
├── install.py                             Deterministic multi-agent skill installer
├── skills/
│   └── proofwork/
│       ├── SKILL.md                       Model-facing epistemic protocol
│       ├── scripts/
│       │   ├── proof.py                   Evidence ledger, hashing, and gate auditor
│       │   ├── scaffold.py                Contract and staged-workspace generator
│       │   └── audit.py                   Structural validation and compliance checker
│       ├── references/                    Formal specifications (CLI, interop, rules)
│       └── assets/                        Deterministic contract templates
├── tests/                                 Zero-dependency regression test suite
├── examples/                              Reproducible reference cases
├── DESIGN.md                              Architecture tradeoffs and trust boundaries
├── EVALUATION.md                          Empirical evaluation and benchmarking protocol
├── SOURCES.md                             Provenance, origin credits, and legal boundary
├── CITATION.cff                           Academic citation metadata
└── LICENSE                                MIT Open Source License
```

### 3.1 Separation of Concerns: Proofwork and REA Investigator

* **Proofwork Core**: Provides lightweight, standard-library-only execution governance, contract scaffolding, local evidence hashing, and epistemic gate enforcement. Operates fully offline without external binaries or APIs.
* **REA Investigator (`Devaretanmay/rea-investigate`)**: An optional upstream forensic engine specialized in 13 authorized deep-investigation capabilities (IPC boundary analysis, binary decompilation, firmware telemetry, network HAR interception, and runtime memory tracing).
* **Provenance Bridge (`proof.py import-rea`)**: Instead of concatenating divergent prompt spaces, Proofwork ingests REA investigation manifests via cryptographic digest attribution. The bridge verifies source integrity without diluting either system's operational instructions.

---

## 4. Empirical Evaluation Framework

Proofwork includes an empirical evaluation protocol designed to measure agent adherence, hallucination suppression, and artifact integrity across standard benchmark families (e.g., SWE-bench, HumanEval-X, and synthetic reverse-engineering workloads).

### 4.1 Research Questions

* **RQ1 (Epistemic Grounding)**: Does cryptographic evidence anchoring reduce hallucinated file references and ungrounded causal explanations compared to unconstrained baseline agents?
* **RQ2 (Architectural Proportionality)**: Does mandatory counter-hypothesis and alternative analysis ($|\text{Alt}| \ge 1$) reduce over-engineering and premature multi-agent complexity?
* **RQ3 (Tamper Detection and Auditability)**: With what reliability does the SHA-256 verification harness detect modified artifacts, stale test outputs, or path traversal anomalies?
* **RQ4 (Computational and Token Overhead)**: What is the marginal execution latency and context-window consumption incurred by the six-gate protocol relative to end-to-end task completion?

### 4.2 Benchmark Families and Evaluation Setup

As specified in [EVALUATION.md](EVALUATION.md), evaluation tasks are partitioned into three primary regimes:
1. **Source Archaeology**: Tracing complex causal logic across heterogeneous legacy codebases.
2. **Deterministic Synthesis**: Implementing minimal vertical slices while resisting unnecessary dependency injection.
3. **Forensic Re-engineering**: Reconstructing closed or partially observed protocols from runtime logs and IPC dumps.

### 4.3 Reference Implementation: Deterministic Accounting Engine

The repository includes a complete, end-to-end reference case in `examples/invoice-report`:
* **Hypothesis**: Financial invoice aggregation can be computed deterministically without relying on probabilistic LLM token completion.
* **Evidence**: Input CSV records and implementation source files cryptographically hashed (`E001` through `E005`).
* **Test Harness**: Golden batch aggregation ($100\%$ precision) paired with explicit negative testing rejecting invalid monetary schemas.
* **Audit**: Verified with zero ledger warnings via `proof.py check`.

---

## 5. Threats to Validity

In accordance with standard empirical software engineering practices, we identify the following threats to validity:

* **Internal Validity**: The SHA-256 evidence ledger guarantees static byte-level integrity against post-capture tampering. It does not certify that the captured evidence was semantically true or that the recording process itself was free from instrumentation bias.
* **External Validity**: Model adherence to the six-gate protocol is subject to base model instruction-following fidelity. While tested against frontier models (Claude 3.7/Sonnet, OpenAI o1/o3-mini, GPT-4o), smaller quantized local models may exhibit stochastic drift around gate boundaries.
* **Construct Validity**: Passing unit test exit codes ($code = 0$) recorded in the ledger proves that a process returned cleanly, but does not guarantee complete semantic coverage of all edge cases. Proofwork mitigates this by mandating both golden and negative test logs.
* **Conclusion Validity**: Quantitative comparisons between gated and ungated agent runs require blinding and inter-rater agreement scoring across identical task seeds to avoid confirmation bias.

---

## 6. Formal Non-Claims and Epistemic Boundaries

To prevent misleading claims regarding automated verification, Proofwork explicitly delineates its operational boundaries:

1. **Hash Verification $\neq$ Truth**: A cryptographic hash confirms that bytes on disk match the recorded snapshot. It does not certify that the data represents authentic system reality.
2. **Recorded Test Log $\neq$ Absolute Correctness**: Capturing an exit code in `proof.py` attests to a command execution event; it does not replace formal software verification (e.g., TLA+, Coq, or symbolic execution).
3. **Documentary Approval $\neq$ Authorization**: The `approve` subcommand records human consent metadata for an audit trail; it does not generate OS-level permissions, bypass firewalls, or authorize legal compliance.
4. **Scaffolding $\neq$ Autonomous Execution**: `scaffold.py` creates structured contract templates; the agent or human engineer remains responsible for correct semantic implementation.

---

## 7. Installation and Reproducibility Harness

### 7.1 System Requirements

* Python 3.10 or higher.
* Operating System: Linux, macOS, or Windows (POSIX-compliant shell).
* Zero third-party Python packages required (standard library: `hashlib`, `json`, `argparse`, `pathlib`, `unittest`).

### 7.2 Installation via `install.py`

Proofwork installs directly into any designated agent workspace:

```bash
# Install to Codex agent workspace (.agents/skills/proofwork)
python3 install.py --agent codex --project /path/to/target/project

# Install to Claude Code workspace (.claude/skills/proofwork)
python3 install.py --agent claude --project /path/to/target/project

# Install to Cursor workspace (.cursor/skills/proofwork)
python3 install.py --agent cursor --project /path/to/target/project

# Dry-run inspection (verifies paths without mutating filesystem)
python3 install.py --agent codex --project /path/to/target/project --dry-run

# Combined installation with local REA Investigator checkout
python3 install.py --agent codex --project /path/to/target/project \
  --rea-path /path/to/rea-investigate
```

### 7.3 CLI Verification Suite

```bash
# Verify environment and system tools
python3 skills/proofwork/scripts/proof.py doctor

# Initialize a new evidence ledger case
python3 skills/proofwork/scripts/proof.py init --dir ./cases/case-01 \
  --question "Identify bottleneck in auth pipeline" \
  --target "src/auth" --mode build

# Capture cryptographically hashed evidence
python3 skills/proofwork/scripts/proof.py capture --dir ./cases/case-01 \
  --id E001 --file src/auth/token.py --kind source --locator "token.py:45-80"

# Register falsifiable claim with counter-hypothesis
python3 skills/proofwork/scripts/proof.py claim --dir ./cases/case-01 \
  --id C001 --statement "Token parsing causes quadratic latency" \
  --evidence E001 --confidence observed \
  --alternative "Database lock contention causes perceived latency" \
  --falsifier "Profile execution time with isolated mock database"

# Record architectural decision with rejected alternatives
python3 skills/proofwork/scripts/proof.py decide --dir ./cases/case-01 \
  --id D001 --selection "Replace regex with linear streaming tokenizer" \
  --alternatives "In-memory caching layer, Thread pool expansion" \
  --reasoning "Eliminates algorithmic complexity without adding memory overhead" \
  --claims C001 --revisit "Revisit if token schema requires lookahead"

# Run strict integrity check and compile report
python3 skills/proofwork/scripts/proof.py check --dir ./cases/case-01 --strict
python3 skills/proofwork/scripts/proof.py report --dir ./cases/case-01
```

### 7.4 Unit Test Suite

The test suite exercises ledger initialization, SHA-256 tamper detection, adversarial claim validation, path traversal defense, and installer isolation:

```bash
python3 -m unittest discover -s tests -v
```

Execution completes in under 0.1 seconds with all 21 tests passing.

---

## 8. Citation

If you utilize Proofwork or its evidence ledger protocol in academic research or industrial evaluations, please cite the framework as follows:

```bibtex
@software{proofwork2026,
  author = {Devare, Tanmay},
  title = {Proofwork: Epistemically Bounded Software Synthesis via Cryptographically Anchored Evidence Ledgers},
  year = {2026},
  url = {https://github.com/Devaretanmay/proofwork},
  version = {1.0.0}
}
```

---

## 9. License and Attribution

Proofwork is released under the MIT License. See [LICENSE](LICENSE) for terms.

This project synthesizes independent methodologies from outcome-first automation frameworks and deep reverse-engineering investigations. It is not affiliated with or endorsed by upstream tool authors. All third-party references are attributed in [SOURCES.md](SOURCES.md).
