# Stage contracts and handoffs

## Stage contract minimum

Each stage should state:

- **Purpose**: One job, described as a verb plus object.
- **Allowed inputs**: Specific relative files or sources; clarify source trust and freshness requirements.
- **Read scope**: Sections actually needed. Don't load the whole workspace by default.
- **Executor**: Script, agent, human, or external approved action.
- **Steps**: Short ordered procedure. Stable rules belong in references, not per-run artifacts.
- **Outputs**: Named files with an explicit format and minimum schema.
- **Acceptance**: Verifiable tests/criteria and evidence.
- **Review**: Human sign-off point if judgment or side effects are involved.
- **On failure**: Stop, record blocker, or re-run safely; do not silently improvise.

A working run folder may use `runs/<run-id>/01-discover/`, `02-transform/`, `03-verify/` with actual outputs. Keep instructions in `stages/` and mutable outputs in `runs/` so reruns never overwrite reusable guidance.

## Minimal interface for a handoff

A `manifest.json` can contain:

```json
{
  "run_id": "demo-001",
  "stage": "02-transform",
  "status": "needs_review",
  "inputs": ["runs/demo-001/01-discover/evidence.md"],
  "outputs": ["runs/demo-001/02-transform/draft.md"],
  "checks": [{"name":"citations_present","passed":true}],
  "blockers": ["Unconfirmed figure in paragraph 3"]
}
```

Treat the example as a convention, not an executable schema. `status` must distinguish draft, verified, needs_review, blocked, and approved when relevant. Validate actual file existence in code rather than trusting only the manifest. Record version/hash information when evidence integrity or reproducibility matters.

## Review design

Use checkpoints where the next action would propagate an error or create an external effect. Example: verify research sources before drafting a public report; verify customer identity before emailing; review a plan before running a destructive migration. Every stage should permit resuming from the last trustworthy output.
