# Research and evaluation playbook

Read this file for repository-wide mapping, external comparisons, or architectural recommendations.

---

## 1. Evidence labels

When exploring a codebase or advising on technical decisions, maintain a strict distinction between observable facts and inferences:

| Category | Definition | Example |
| :--- | :--- | :--- |
| **Observed** | Directly verifiable in code, configuration, history, runtime output, or primary documentation. | *"`storage.py:14` opens SQLite and enables WAL."* |
| **Inferred** | A conclusion supported by named observations but not explicitly documented. | *"The single-process queue suggests deployment simplicity was favored over distributed throughput."* |
| **Unknown** | Information absent from the available evidence. | *"Expected production write concurrency is unknown."* |

Always surface unknowns explicitly rather than guessing or fabricating requirements.

---

## 2. Repository map

Map only what the question needs:

1. Entry points and public contracts.
2. Owning modules and state transitions.
3. Storage, network, generated-code, and asynchronous boundaries.
4. Tests and configuration that constrain behavior.
5. One representative end-to-end flow.

Verify paths and symbols. Use history to explain a design choice only when a commit or discussion actually records the reason.

## 3. External source quality

Prefer, in order: official specifications and documentation; source repositories and release notes; reproducible benchmarks; maintainer discussions; secondary analysis. Check the version, date, license, maintenance state, and benchmark method. Popularity is not evidence of fit.

## 4. Comparing architectures and technologies

When comparing local architecture with external frameworks (e.g., PostHog, Temporal, Sentry, or standard database alternatives):

Compare the current design, no change, and viable alternatives with the same criteria:

| Criterion | Question |
| :--- | :--- |
| Correctness fit | Does it meet the demonstrated requirement and preserve contracts? |
| Maintainability | Does it match team skills, repository conventions, and ownership? |
| Performance | Which measured bottleneck changes, and under what workload? |
| Complexity | What new services, failure modes, setup, and observability are required? |
| Migration cost | Which APIs, data, deployments, and tests must change? |
| Reversibility | Can the team roll back without data loss or a second migration? |
| Ecosystem | Is it maintained, governed, documented, and license-compatible? |

---

## 5. Graceful degradation without web access

When host web search or repository lookup tools are unavailable:
- Explicitly state that external research is limited to existing repository context and documented knowledge.
- Complete the local architectural and code exploration using repository files, test fixtures, and Git commit logs.
- Never invent external URLs, synthetic benchmark numbers, or version-specific claims without verification.

---

## 6. Recommendation structure

A high-value recommendation specifies what **not** to change as clearly as what to change:

- **What to improve:** Bottlenecks with clear return-on-investment, fragile coupling, missing test fixtures, or scalability cliffs.
- **What to leave alone:** Working components that satisfy current requirements, code where added abstraction would violate YAGNI, or mature libraries with stable maintenance.
- **Decision criteria:** Give an observable trigger only when evidence supports its value. Otherwise name the measurement needed instead of inventing a threshold.
- **Unknowns:** State which missing fact could reverse the recommendation.
