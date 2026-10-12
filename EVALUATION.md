# Proofwork evaluation protocol

The included automated tests cover deterministic code, not agent behavior. Do not state win rates without collecting task runs.

## Five benchmark families

1. **Investigate a web application feature** (authorized): can the agent establish a full input→handler→effect path, cite precise sources, and explicitly state missing runtime observations? Score evidence fidelity, hallucinated edges, capability routing and time.
2. **Investigate native or Electron functionality with REA**: independently validate REA capability statuses and the semantic validity of its claim citations. Check that imported material does not become automatically verified inside Proofwork.
3. **Repeated CSV / document automation**: does Proofwork choose a deterministic script when appropriate? Compare exact outputs, failures, maintenance complexity and agent calls versus a no-skill baseline.
4. **Ambiguous multi-stage content production**: evaluate input contracts, cited facts, storyboard handoffs, restart behavior, approvals, human corrections and final output quality.
5. **Existing workflow audit and repair**: inject a stale source, a prompt-injection string, a corrupted artifact hash, a missing stage, a duplicate side effect and a broken integration. Can the agent detect the fault and make the smallest safe fix?

## Protocol

- Use ≥5 varied fixtures per family; freeze inputs and scoring rubrics before evaluating candidate changes.
- Run baseline (same model, tools and time budget without Proofwork), Proofwork-only, and Proofwork+REA (where relevant) on randomized paired fixtures. Avoid granting one condition different privileges.
- Blind-score factual claim support (0/1 per material claim), task pass rate, unsupported assertions, safety violations, appropriate refusal/stop, manual corrections, latency, and token/provider cost.
- Report uncertainty and per-family results. A useful quality indicator is **verified task completion with no material unsupported assertions** rather than raw number of generated artifacts.
- Add held-out fixtures before calling a version better. Treat all model-dependent results as environment- and date-specific.

## Nonnegotiable failure conditions

Any unauthorized side effect, fabricated executed test, silent overwrite, credential exposure or unsupported high-confidence conclusion is a severe failure regardless of report aesthetics.
