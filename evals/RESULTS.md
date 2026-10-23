# Evaluation results

Date: 24 October 2026

## Deterministic verification

- `python3 -m unittest discover -s tests -v`: 86 tests passed.
- Coverage includes installer compatibility for four supported agents, independent and combined installation of three skills, optional utilities, reference integrity, activation-label fixtures, review candidate setup, and failing repair-fixture validation.
- These results verify repository behavior and instruction contracts. They do not demonstrate that an AI agent follows the skills.

## Behavioral comparison

The repair comparison is inconclusive in this environment.

| Agent CLI | Variant attempted | Valid runs | Reason |
| :--- | :--- | ---: | :--- |
| Codex | Baseline | 0/2 | Local app-server initialization failed because its state database was read-only. |
| Claude Code | Baseline | 0/1 | CLI was not logged in. |
| Codex | Review baseline | 0/2 | The same read-only state database prevented both the flawed-change and clean-change runs from starting. |

No Fox-vs-baseline or Fox-Review-vs-baseline success, false-positive, regression, edit-count, tool-call, or token claim is made. The runner excludes failed agent processes from scored totals. The Fox Review variant was not run after both matched baseline runs failed before task execution. Run `evals/run.py` in an authenticated writable environment with the same model, version, effort, and repeated trials for each variant.
