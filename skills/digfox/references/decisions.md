# Decision standard

## Choose proportionate architecture

Ask these five questions:

1. **Repeatability:** Does this happen often enough to justify maintenance? If no, perform once.
2. **Determinism:** Are correctness rules objective and stable? If yes, start with a script/test.
3. **Uncertainty:** Does it depend on interpretation or ambiguous sources? If yes, use LLM with evidence and review.
4. **State:** Does it require restartable intermediate artifacts or human handoffs? If yes, staged workflow.
5. **Concurrency and safety:** Does it have parallel agents, durable queues, tenant isolation, external effects or SLAs? If yes, an actual workflow/runtime engine with identity, access control and observability, not just folders.

The numeric 60/30/10 allocation sometimes associated with AI workflows is a mnemonic, not a target. Work must be assigned by risk, testability, cost and error tolerance.

## Required decision record

- Problem and measurable outcome
- Chosen option
- At least one serious rejected alternative and why it loses here
- Source claims / verified facts versus assumptions
- Complexity, cost, operational burden and failure modes
- Reversibility, migration plan and human review points
- An explicit condition under which this decision should be changed

Do not optimize for novelty. Design choices must be reasoned, not maximal. A lower-tech outcome is a success if it safely solves the task.

## Examples

**Invoice extraction**: select a parser + deterministic checks; LLM only for ambiguous exceptions. Reject autonomous orchestration because schema and calculation rules are stable. Revisit if document variability exceeds rules.

**Incident investigation**: prefer REA (when authorized) for binary/app runtime trace over speculation, then use Digfox to capture the evidence-backed cause and a regression test. Reject reconstructing behavior directly from a screenshot.

**Weekly content workflow**: favor a small folder workflow with script, storyboard, and review contracts. Reject a distributed multi-agent service because there's one operator and no concurrency requirement.
