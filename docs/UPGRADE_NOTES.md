# Fox reliability upgrade notes

Date: 23 October 2026

## Sources and decisions

The upgrade follows the Agent Skills specification plus current Anthropic and OpenAI authoring guidance: discovery depends on precise `name` and `description` metadata; `SKILL.md` should stay concise; deeper guidance belongs in directly linked references; and behavioral evaluations must start from representative tasks and a no-skill baseline.

Ponytail 5 contributed one useful constraint: optimize for the smallest **complete** change, not the fewest edited lines. Fox adapts this into a repair ladder while retaining its stronger requirements for reproduction, owning-layer diagnosis, counterexamples, and explicit partial or blocked outcomes.

Primary sources:

- https://agentskills.io/specification
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- https://developers.openai.com/codex/build-skills
- https://developers.openai.com/blog/eval-skills
- https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md

## Material changes

| Change | Reason | Verification |
| :--- | :--- | :--- |
| Precise positive and negative activation descriptions | Reduce overlap, trivial-edit activation, and unauthorized Explore edits | Metadata tests plus positive, combined, and negative activation fixtures |
| Fox boundary tracing for APIs, databases, native engines, generated code, and async execution | Improve owner identification across common failure boundaries | Instruction contracts and `references/diagnosis.md` link checks |
| Smallest-complete-change repair ladder | Reuse working code and avoid incomplete wrappers or new dependencies | Instruction contracts and `references/repair.md` link checks |
| Fox Explore fact/inference/unknown labels and consistent comparison criteria | Reduce speculative architectural advice | Explore contract tests and architecture-task rubrics |
| Two-skill architecture retained | Diff review and caller checks are part of repair verification, not a separate capability | Installer tests confirm exactly `fox` and `fox-explore` independently and together |
| Behavioral evaluation runner and fixtures | Separate real agent evidence from instruction-text checks | Repair fixtures must fail before agent work; invalid agent processes are excluded |

## Verification status

All deterministic tests pass. The live agent comparison is inconclusive because the available Codex CLI could not initialize its local state and Claude Code was not authenticated. See [`evals/RESULTS.md`](../evals/RESULTS.md). No reliability improvement is claimed until valid repeated baseline and Fox runs are collected.
