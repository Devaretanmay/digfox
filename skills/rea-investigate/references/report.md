# Report standard

The reporter compiles `case.json` and the `notes/*.md` authored by the investigator. **It does not generate conclusions.** Fill the exact note files below (Markdown allowed) after studying source Evidence. Empty notes remain explicit gaps in the rendered report and fail strict validation.

- `notes/overview.md`: decisive answer in 3-7 factual sentences; identification of the target, confidence and practical significance. Do not write an empty flourish.
- `notes/architecture.md`: investigated components, entry points, dependencies, trust boundaries and uncovered subsystems. Prefer a short plain-text flow diagram with evidence IDs on edges.
- `notes/trace.md`: trigger → entry → control/data flow → boundary → effect; for each hop include claim ID, source ID and exact locator. If target is non-interactive, use input/entry/method/observable side effect.
- `notes/verification.md`: actual commands, test environment, before/after results, negative controls, where assertions passed/failed, and independent reproduction steps. Differentiate performed tests from proposed experiments.
- `notes/limitations.md`: missing captures/providers, unsupported platform, ambiguity, redactions, incomplete coverage, untested conditions, security/authorization restrictions.
- `notes/audit.md`: challenge strongest claims with plausible alternatives and falsifying experiments; unresolved claims remain visible. The note is required even if the evidence is strong.

Optional notes (include meaningful text when relevant): `network.md`, `version-diff.md`, `implementation.md`, `appendix.md`.

`case.py render` builds `REPORT.md` in this order:

1. Verdict and scope.
2. Investigation coverage (all 13 capabilities, including N/A or blocked reasons).
3. Method and artifact identity.
4. Architecture and feature walkthrough.
5. Network/version/implementation sections when used.
6. Verification and test results.
7. Evidence-backed claim table and source register (with SHA-256 of each source).
8. Adversarial audit and unresolved risks.
9. Reproduction steps and limitations.

The report should be useful to an engineer unfamiliar with the target. Clearly state **what was found**, **why to believe it**, **what could disprove it**, and **what is not known**. Do not describe all 13 capabilities as executed when many are irrelevant; the complete 13-stage matrix documents applicability.

## Finishing command

```
python3 scripts/case.py render CASE_DIR
python3 scripts/case.py check CASE_DIR --strict
```

A strict failure is not a reason to erase incomplete work. Produce `REPORT.md` and report the failures as incomplete evidence. The validator checks structural/provenance coverage, not the actual truth of technical conclusions; a human should still review important decisions.
