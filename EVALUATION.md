# How we evaluate Digfox

Our unit tests prove that our Python scripts don't crash and that file hashes work. They don't prove that an AI agent using Digfox writes better code, hallucinates less, or builds simpler systems.

Here is how we measure whether Digfox actually improves agent performance on real tasks.

---

## The evaluation rule: measured, not claimed

Never claim a win rate without running paired, side-by-side agent runs on real problems.

When comparing a model with Digfox against the same model without Digfox:
1. **Freeze the inputs**: Use identical prompts, repositories, tools, and time budgets for both runs.
2. **Score objectively**: Track factual claims supported by actual files, whether code worked on the first try, tokens spent, and time taken.
3. **Check for regressions**: Did the agent break unrelated tests or introduce unneeded libraries?

---

## Five benchmark scenarios

We test Digfox across five realistic situations:

1. **Investigating an unfamiliar codebase**: Give the agent a bug report in a large repo. Can it trace the input to the exact line causing the issue without hallucinating nonexistent helper functions?
2. **Reverse engineering desktop or web apps**: Using the REA bridge, can the agent identify IPC channels and API endpoints without claiming to have run tools it didn't run?
3. **Data and document automation**: Ask the agent to automate a repetitive task (like cleaning CSVs or parsing PDFs). Does it write a clean Python script, or does it try to spin up a fragile multi-agent pipeline?
4. **Multi-stage workflows**: Ask the agent to build a multi-step pipeline. Does it define clear stage contracts with explicit input/output boundaries, or does it create a monolithic script that fails silently?
5. **Auditing and fixing existing code**: Inject subtle errors (like an expired token check, a missing edge case, or bad error handling). Does the agent spot the flaw, write a test for it, and fix it with the smallest possible change?

---

## What counts as a failure

A run fails if the agent:
* Claims a test passed when it never ran the command.
* Cites a file path or line number that does not exist in the repository.
* Makes an unauthorized external call (like hitting a production API or sending an email) without asking.
* Reaches for an over-engineered architecture when a simple script was enough.
* Silently overwrites files without a backup or user confirmation.
