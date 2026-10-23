# Fox behavioral evaluations

These evaluations compare the same coding agent with no Fox skill (`baseline`) and with Fox installed. They measure task success, regression failures, unnecessary edits, elapsed time, and changed files. Architecture tasks also verify read-only behavior, but their reasoning quality requires blind human grading against the rubric in `tasks.json`.

Instruction-contract and metadata tests are not behavioral evidence. Do not combine their pass rate with these results.

## Run a comparison

Use an isolated, non-interactive agent command with `{workspace}` and `{prompt}` placeholders. Example for Codex:

```bash
python3 evals/run.py --variant baseline \
  --agent-command 'codex exec --ephemeral --skip-git-repo-check --sandbox workspace-write --cd {workspace} {prompt}' \
  --output baseline.json

python3 evals/run.py --variant fox \
  --agent-command 'codex exec --ephemeral --skip-git-repo-check --sandbox workspace-write --cd {workspace} {prompt}' \
  --output fox.json
```

Use the same agent model, version, effort, timeout, and task set for both variants. Run multiple trials because agent behavior is stochastic. Grade exploration outputs without knowing the variant.

The runner reads tool-call and token totals only from JSONL agent events. Add the agent's JSON-output flag when available, such as `codex exec --json`. It leaves unavailable metrics null and never estimates them from prose or terminal lines.

Runs where the agent process exits unsuccessfully are marked `valid_run: false` and excluded from scored totals. A fixture that remains failing after an infrastructure error is not evidence against either variant.
