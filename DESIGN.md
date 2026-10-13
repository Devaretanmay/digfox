# Architecture Decision Record: Proofwork System Design

## 1. Architectural Options Considered

| Architecture | Advantage | Outcome |
|---|---|---|
| Merge REA and Systemcraft SKILL.md verbatim | Single large skill | **Reject.** REA specialized investigation demands dedicated instructions, 13-capability routing, and tool providers. Overlapping agent instructions produce brittle tool selection. |
| Replace REA with a generic checklist | Minimal footprint | **Reject.** Sacrifices binary, application, firmware, HAR, and provider depth, alongside structured evidence ledgers. |
| Always spawn a multi-agent team | Impressive demonstration | **Reject.** Adds latency, token expense, race conditions, and authority confusion where a single script or agent suffices. |
| Proofwork front door + integrated Systemcraft + decoupled REA specialist + provenance bridge | Focused default, deep opt-in capability, and compatible original source | **Adopt.** Lightweight path without REA; authorized specialist route when needed; separate verified scopes. |

---

## 2. Theoretical Formulation and State Model

Proofwork formalizes agent-environment interactions as a state-constrained transition system with an append-only evidence ledger:

$$\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{O}, \mathcal{T}, \Omega, \mathcal{L} \rangle$$

Where:
* $\mathcal{S}$ represents repository states and dependencies.
* $\mathcal{A}$ represents agent actions (file reads, AST traversal, script generation, test runs).
* $\mathcal{O}$ represents the observation space emitted by environment processes and tools.
* $\mathcal{T}: \mathcal{S} \times \mathcal{A} \to \mathcal{S}$ defines state transitions under modifications.
* $\Omega: \mathcal{S} \times \mathcal{A} \to \mathcal{O}$ defines observation emission probabilities.
* $\mathcal{L}$ represents the local evidence snapshot ledger.

### 2.1 Evidence Tuple Semantics

Every discrete observation admitted into the reasoning trace is captured as a tuple:

$$\mathbf{e}_k = \langle \tau_k, \mathbf{uri}_k, \mathbf{h}_k, \mathbf{c}_k, \mathcal{V}_k \rangle$$

Where:
* $\tau_k \in \{\text{source}, \text{observation}, \text{test-log}, \text{artifact}\}$ denotes the artifact category.
* $\mathbf{uri}_k$ represents the immutable canonical locator within the case container.
* $\mathbf{h}_k = \text{SHA256}(\text{bytes}_k)$ represents the cryptographic digest computed at ingestion time $t_k$.
* $\mathbf{c}_k$ denotes the textual context or line-range bounds.
* $\mathcal{V}_k \in \{0, 1\}$ represents the verification state under cyclic integrity audits.

### 2.2 Adversarial Falsification Invariant

An empirical claim $C_i \in \mathcal{C}$ asserting behavioral properties of target code is prohibited from entering status `observed` unless it satisfies Popperian falsifiability criteria:

$$\text{Status}(C_i) = \text{observed} \implies \left( E(C_i) \neq \emptyset \;\land\; H_{\text{alt}}(C_i) \neq \emptyset \;\land\; F(C_i) \neq \emptyset \right)$$

Where:
* $E(C_i) \subseteq \{\mathbf{e}_1, \dots, \mathbf{e}_n\}$ denotes non-empty supporting cryptographic evidence references.
* $H_{\text{alt}}(C_i)$ denotes an explicitly articulated counter-hypothesis or competing explanation.
* $F(C_i)$ denotes a concrete operational falsifier (a deterministic test or observation that disproves the claim).

---

## 3. Trust Boundaries and Limitations

1. **Snapshot Ledger vs Append-Only Chains**: Evidence files are copied into a local case folder and SHA-256 digests are recorded in `case.json`. This detects accidental drift or tampering on disk. It is not an immutable, externally anchored blockchain; an attacker with write access to the filesystem can modify both evidence and digests simultaneously.
2. **Recorded Test Logs vs Sandboxed Execution**: The `test` command registers operator-supplied test logs and checks reported exit codes. It does not independently sandbox or execute test binaries. A clean exit code ($0$) verifies that the recorded run completed, not that test coverage was semantically exhaustive.
3. **Documentary Approvals**: The `approve` command logs human consent for an audit trail. It does not generate operating system permissions or network credentials.
4. **REA Ingestion**: Provenance imported from REA via `import-rea` attributes upstream findings with SHA-256 digests; it does not automatically certify semantic truth.

---

## 4. Verification Status and Next Validation Steps

* **Verified locally**: Standard-library import, ledger validation, evidence hash tamper detection, invalid reference rejection, adversarial claim schema enforcement, overwrite protection, REA bridge attribution, and structural scaffold/audit checks.
* **Not yet verified**: Statistical model adherence across frontier clients, latency on large monorepos, and agent task completion lift on public benchmarks.
* **Next milestone**: Execute paired evaluations on 20-50 real GitHub issues with and without Proofwork to measure factual correctness, token efficiency, and regression rates.
