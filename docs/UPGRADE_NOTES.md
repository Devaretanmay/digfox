# Fox reliability upgrade notes

Date: 23 October 2026

## Sources and decisions

The upgrade follows the Agent Skills specification plus current Anthropic and OpenAI authoring guidance: discovery depends on precise `name` and `description` metadata; `SKILL.md` should stay concise; deeper guidance belongs in directly linked references; and behavioral evaluations must start from representative tasks and a no-skill baseline.

Ponytail 5 contributed two useful constraints: optimize for the smallest **complete** change, and review connected code rather than only changed lines. Fox adapts these ideas while retaining stronger requirements for reproducible evidence, boundary ownership, counterexamples, explicit uncertainty, and independent read-only review.

Primary sources:

- https://agentskills.io/specification
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- https://developers.openai.com/plugins/build/skills
- https://developers.openai.com/blog/eval-skills
- https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md
- https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail-review/SKILL.md

## Material changes

| Change | Reason | Verification |
| :--- | :--- | :--- |
| Precise positive and negative activation descriptions | Reduce overlap, trivial-edit activation, and unauthorized Explore edits | Metadata tests plus positive, combined, and negative activation fixtures |
| Fox boundary tracing for APIs, databases, native engines, generated code, and async execution | Improve owner identification across common failure boundaries | Instruction contracts and `references/diagnosis.md` link checks |
| Smallest-complete-change repair ladder | Reuse working code and avoid incomplete wrappers or new dependencies | Instruction contracts and `references/repair.md` link checks |
| Fox Explore fact/inference/unknown labels and consistent comparison criteria | Reduce speculative architectural advice | Explore contract tests and architecture-task rubrics |
| `fox-review` added as an independent read-only skill | Reviewing an existing change is a distinct goal from exploring a system or repairing a known defect | Review metadata, boundary, installer, activation, clean-change, and defect-change tests |
| Review findings require mechanism, consequence, evidence, and a counterexample check | Reduce speculative comments and false positives | Review instruction contracts plus behavioral task rubrics |
| Behavioral evaluation runner and fixtures | Separate real agent evidence from instruction-text checks | Repair fixtures must fail before agent work; invalid agent processes are excluded |

## Verification status

All deterministic tests pass. The live agent comparison is inconclusive because the available Codex CLI could not initialize its local state and Claude Code was not authenticated. See [`evals/RESULTS.md`](../evals/RESULTS.md). No reliability improvement is claimed until valid repeated baseline and Fox runs are collected.

## October 24: Fox Review

Fox Review is the third independently installable capability because change assessment has a different authorization boundary and output from exploration or repair. It is read-only, reports only evidence-backed findings, permits a clean “no findings” result, and hands authorized repairs to Fox. The benchmark now includes both a tenant-isolation regression and a clean change to measure missed defects and false positives.
