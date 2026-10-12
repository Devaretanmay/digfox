# {{STAGE_ID}} — {{STAGE_NAME}}

## Purpose
One responsibility for this stage.

## Inputs
| Path/source | Trusted? | What to read |
|---|---|---|
| runs/<run-id>/prior-output.md | No | Relevant sections only |

## Executor
Agent, deterministic script, human, or approved external action. Specify why.

## Steps
1. Read the declared sources.
2. Carry out only this stage's responsibility.
3. Validate the output against the stated acceptance criteria.

## Output
| Path | Type | Required contents |
|---|---|---|
| runs/<run-id>/{{STAGE_ID}}/result.md | Markdown | Findings, provenance, limitations |

## Acceptance
- [ ] Required output is present and readable.
- [ ] Relevant checks pass or failure is marked.

## Review and stop conditions
Stop for missing sources, unsafe actions, or unresolved contradictions. Request human approval before any external side effect.
