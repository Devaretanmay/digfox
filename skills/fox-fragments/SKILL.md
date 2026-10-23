---
name: fox-fragments
description: Routes engineering requests to minimal, task-specific instruction fragments for debugging, architecture exploration, and code review. Use when the user wants Fox guidance without loading the complete Fox, Fox Explore, or Fox Review skills. Do not use for trivial questions or when a fully loaded specialist skill is already in control.
license: MIT
compatibility: Standalone Agent Skill; needs only host file-reading and normal repository tools.
metadata:
  version: "0.1.0"
---
# Fox Fragments

Load the smallest useful instructions, not an entire specialist skill.

1. Classify the task by requested *outcome*: repair a defect, understand or compare a design, or review an existing change. For mixed tasks, follow the user's authorized sequence. Never treat analysis as permission to edit.
2. Read **only** the matching fragment below. Each file is self-contained. Read a second fragment only when concrete evidence crosses that boundary. Do not read the original specialist SKILL.md files or every fragment by default.
3. Apply the instructions while using the host agent's normal tools. Reassess only when new evidence changes the task category. Avoid duplicate reads when content is already available.
4. Keep evidence honest and changes within authorized scope. Do not fabricate tests, expose secrets, run untrusted code, or take external/production actions without authorization.

## Fragment map

| Task or observed condition | Read exactly this file |
| --- | --- |
| Reproduce a bug, identify root cause, implement verified fix | [repair.md](references/repair.md) |
| Bug crosses HTTP, database, async, or native boundary | [boundaries.md](references/boundaries.md) additionally, only when needed |
| Explain a repository, trace code flow, compare architectures | [explore.md](references/explore.md) |
| Review a PR, diff, commit, or patch for defects | [review.md](references/review.md) |
| Test regression, compatibility, or complex failure paths | [verification.md](references/verification.md) additionally, only when needed |

If the question is a trivial typo, simple lookup, or formatting request, do not apply a fragment.

This is instruction routing, not a dynamic context-management engine: host agents decide when referenced files are read; Fox Fragments cannot erase previously loaded text. It works alone without installing the original three skills.
