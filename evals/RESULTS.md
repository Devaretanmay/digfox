# Evaluation results

Date: 23 October 2026

## Deterministic verification

- `python3 -m unittest discover -s tests -v`: 70 tests passed.
- Coverage includes installer compatibility for four supported agents, independent and combined installation, optional utilities, reference integrity, activation-label fixtures, and failing evaluation-fixture validation.
- These results verify repository behavior and instruction contracts. They do not demonstrate that an AI agent follows the skills.

## Behavioral comparison

The repair comparison is inconclusive in this environment.

| Agent CLI | Variant attempted | Valid runs | Reason |
| :--- | :--- | ---: | :--- |
| Codex | Baseline | 0/2 | Local app-server initialization failed because its state database was read-only. |
| Claude Code | Baseline | 0/1 | CLI was not logged in. |

No Fox-vs-baseline success, regression, edit-count, tool-call, or token claim is made. The runner excludes failed agent processes from scored totals. Run `evals/run.py` in an authenticated environment with the same model, version, effort, and repeated trials for both variants.
