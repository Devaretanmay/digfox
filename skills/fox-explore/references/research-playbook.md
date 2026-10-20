# Fox Explore: Research and Evaluation Playbook

This playbook provides evaluation patterns and inquiry techniques for understanding codebases, conducting technical research, and forming evidence-backed engineering recommendations.

---

## 1. Grounding Evidence vs. Inference

When exploring a codebase or advising on technical decisions, maintain a strict distinction between observable facts and inferences:

| Category | Definition | Example |
| :--- | :--- | :--- |
| **Confirmed Fact** | Directly verifiable in code, config, commit history, or primary documentation. | *"SQLite is used in `storage.py:14` with `PRAGMA journal_mode=WAL`."* |
| **Plausible Inference** | A logical deduction supported by facts, but not explicitly documented. | *"The single-writer lock in SQLite indicates this service was designed for low-concurrency internal tools rather than high-throughput public APIs."* |
| **Unknown / Assumption** | Information not present in the repository and unverified externally. | *"Expected production QPS and data retention requirements are unknown."* |

Always surface unknowns explicitly rather than guessing or fabricating requirements.

---

## 2. Comparing Architectures and Technologies

When comparing local architecture with external frameworks (e.g., PostHog, Temporal, Sentry, or standard database alternatives):

1. **Understand Current Context:** Identify current bottlenecks, scale, constraints, and team complexity.
2. **Evaluate External Projects:**
   - **Maturity & Maintenance:** Check GitHub release cadence, commit activity, and open issues.
   - **Operational Footprint:** Does it require external daemons, Redis, Kafka, or heavy cloud infrastructure?
   - **License & Governance:** Check if the license (MIT, Apache 2.0, AGPL, BSL) permits the intended commercial or private usage.
3. **Construct a Trade-Off Matrix:**
   - **Simplicity vs. Scalability:** Does the proposed alternative add distributed systems failure modes?
   - **Developer Experience:** Will local setup become difficult or require Docker orchestration?
   - **Migration Effort:** What data models, APIs, and tests must change?

---

## 3. Graceful Degradation Without Web Access

When host web search or repository lookup tools are unavailable:
- Explicitly state that external research is limited to existing repository context and documented knowledge.
- Complete the local architectural and code exploration using repository files, test fixtures, and Git commit logs.
- Never invent external URLs, synthetic benchmark numbers, or version-specific claims without verification.

---

## 4. Structuring Recommendations: What to Improve vs. What to Leave Alone

A high-value recommendation specifies what **not** to change as clearly as what to change:

- **What to improve:** Bottlenecks with clear return-on-investment, fragile coupling, missing test fixtures, or scalability cliffs.
- **What to leave alone:** Working components that satisfy current requirements, code where added abstraction would violate YAGNI, or mature libraries with stable maintenance.
- **Decision Criteria:** Provide observable thresholds (e.g., *"Stay with SQLite until concurrent write contention exceeds 50 req/sec or database file exceeds 10 GB"*).
