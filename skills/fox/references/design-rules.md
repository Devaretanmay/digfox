# Fox: design decisions

## Decision ladder

Choose the lowest-complexity form that meets the need:

1. **Answer or checklist**: one-off task, no durable state, few steps.
2. **Deterministic script**: stable inputs and objective transformations; little interpretation.
3. **Reusable skill**: repeated task requiring agent judgment, instructions and quality criteria; workflow not strongly stateful.
4. **Staged filesystem workflow**: sequential transformations, persisted intermediates, handoffs, iterative human review.
5. **Workflow engine / services**: parallel branches, SLA, durable job queues, external events, multi-user permissions, retries over distributed systems, or strict audit requirements.

A folder-based workflow is not a replacement for transactional storage, queuing, access control, sandboxing, or production observability. A skill describes behavior; a filesystem workflow represents state; code implements deterministic work; service infrastructure provides runtime guarantees.

## Before writing files

Write answers to these questions (assumptions are acceptable when low-risk):
- Outcome: What observable artifact or effect defines success?
- Frequency/trigger: How often and who initiates it?
- Inputs: What sources are authoritative? How are permissions granted?
- Consumer: Who uses the output, and what decisions do they make?
- Quality: What must be true, measurable and inspectable?
- Risk: What action cannot be undone? Which data is regulated/sensitive?
- Failure: What happens on incomplete/stale/conflicting evidence?
- Budget: Constraints on time, compute, tokens, access, and maintenance?

## Executor routing

| Work type | Default owner | Why |
|---|---|---|
| Parse known formats, math, sort, deduplicate | Script/library | Deterministic and testable |
| Validate shapes, allowed states and file paths | Schema/script | Cheap, consistent feedback |
| Route known conditions | Explicit policy | Traceable decisions |
| Summarize unfamiliar documents | LLM + evidence review | Requires interpretation |
| Choose business priorities | Human + LLM suggestions | Accountability and uncertainty |
| Publish, email, spend, delete, deploy | Human-approved action | External side effect |

Do not impose a numeric LLM-to-code ratio. Route based on error cost, uncertainty, and testability. Under uncertainty prefer a human checkpoint rather than fabricating confidence.

## Skill extraction

Extract a standalone skill when the process has been observed or tested at least once. Frontmatter says **when** to invoke it, not simply what it is. Keep instructions short; load examples and references only if needed. Avoid hardcoded absolute paths, vendor-only capabilities, secrets, and stale assumptions. Provide user-facing instructions and an evaluation fixture.

## Complexity warning signs

A design is probably too complex if it invents agents solely to mirror departments, introduces a database without durable concurrency needs, saves identical instructions in several places, includes irrelevant context at every step, or has no way to compare output with acceptance criteria.

It is also defective if it invents elaborate recursive wrappers, proxy layers, or monkey patches merely to avoid working in an underlying editable language or subsystem. If the owning layer is available and authorized, fix it there; if unavailable, document the blocker.
