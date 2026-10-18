# Prioritized Digfox Improvements

Based on empirical data from the 6-trial real-world benchmark on `pydantic/pydantic` (#12884), this document presents concrete, evidence-backed improvements to the Digfox Agent Skill (`skills/digfox`).

The benchmark demonstrated score parity (84.67/100 for both Baseline and Digfox) and revealed that Digfox adds an +8.76% prompt token overhead without improving task completion rates or preventing nested model failure modes.

The following improvements address these measured limitations.

---

## Priority 1 (High): Add Architectural Boundary Reconnaissance Instructions

### Problem Observed
In all 6 benchmark trials (3 Baseline, 3 Digfox), agents produced patches in `pydantic/main.py` that passed 9 out of 10 acceptance tests but consistently failed check 6 (`test_06_nested_models`).
Because `BaseModel.model_dump()` delegates to `self.__pydantic_serializer__.to_python()` (a compiled Rust extension in `pydantic-core`), Rust traverses child models directly in C/Rust without re-invoking `inner.model_dump()` in Python.
Neither agent investigated whether the serialization defect lived in Python or the underlying Rust engine. As confirmed by Pydantic PR #12918, the real fix required editing `pydantic-core/src/serializers/fields.rs` in Rust.

### Recommended Instruction
In Stage 1 (Scope) and Stage 2 (Investigate), add explicit architectural guidance:
- "Check runtime boundaries: Determine whether the component delegates to a compiled binary extension (such as Rust, C, or WebAssembly) or an external process."
- "If the component delegates to an underlying engine, check whether internal traversals (such as nested models or sub-expressions) bypass high-level Python wrappers."
- "If a high-level wrapper cannot intercept nested traversals, document the boundary constraint immediately rather than deploying a partial wrapper."

---

## Priority 2 (High): Eliminate Ceremonial Stage-Gate Narrative Bloat

### Problem Observed
The Digfox skill currently injects ~3,000 prompt tokens into context. On `gpt-5.6-sol`, this produced an +8.76% token overhead (37,350 tokens per run for Digfox vs 34,342 for baseline) with zero increase in benchmark score (84.67 vs 84.67).
Modern coding models already exhibit logical decomposition (scoping, reading, patching, and testing). Forcing verbose markdown stage-gate headers adds context clutter and cost without changing the resulting patch code.

### Recommended Instruction
- Compress `skills/digfox/SKILL.md` from ~2,500 words down to under 500 words.
- Remove rigid stage narrative requirements and replace them with a concise 4-step checklist:
  1. Ground: Reproduce the defect with a minimal standalone script.
  2. Inspect: Check the true engine boundary (Python vs compiled backend).
  3. Patch: Make the smallest necessary in-tree change.
  4. Verify: Run both the reproducer and existing regression suites.

---

## Priority 3 (Medium): Enforce Multi-Format and Composite Structure Testing

### Problem Observed
In Trial 1 of the benchmark, both baseline and Digfox agents patched `BaseModel.model_dump()` but completely missed `BaseModel.model_dump_json()`, resulting in invalid JSON output containing duplicate keys. Only when the reproducer explicitly asserted on `model_dump_json()` in Trials 2 and 3 did the agents patch both methods.

### Recommended Instruction
In Stage 5 (Verify), add specific verification rules for data transformation components:
- "When modifying serialization or formatting logic, verify all exposed output channels (for example: in-memory dictionary, string/JSON output, and binary serialization)."
- "Test nested and recursive instances, not only flat scalar models."

---

## Priority 4 (Medium): Mandate Executable Reproducer Creation

### Problem Observed
In the benchmark, both conditions achieved 0 unsupported claims and 0 false test reports. Qualitative analysis of agent execution traces showed that this high verification integrity was driven by the presence of `reproduce_issue.py` in the workspace. The agents repeatedly executed this file after each edit.
In unassisted real-world tasks where no reproducer is provided by the user, agents frequently declare victory prematurely.

### Recommended Instruction
In Stage 2 (Investigate), make reproducer creation mandatory:
- "Before writing or editing production code, create an isolated reproduction script (for example: `repro_defect.py`)."
- "Confirm that `repro_defect.py` fails on the unpatched codebase before making any code modifications."
- "A task cannot be marked completed unless `repro_defect.py` exits with code 0 on the patched codebase."

---

## Priority 5 (Low): Remove Unused Scaffolding and Ledger Tool References

### Problem Observed
`SKILL.md` currently references `python3 scripts/proof.py` and `python3 scripts/scaffold.py`. These tools were not utilized by the agent during real repository problem-solving, but their presence in the prompt distracted agents and wasted context tokens.

### Recommended Instruction
- Remove references to `proof.py` and `scaffold.py` from the primary coding instructions.
- Reserve ledger tooling strictly for compliance audit modes where external cryptographic verification is requested.

---

## Summary of Expected Impact

Applying these five improvements will:
- Cut prompt token overhead by ~2,500 tokens per request (-70% prompt reduction).
- Eliminate superficial Python-only wrappers on hybrid Python/Rust codebases.
- Guarantee dual-format serialization coverage (`model_dump` and `model_dump_json`).
- Ensure reproducible, evidence-backed fixes across all agent coding tasks.
