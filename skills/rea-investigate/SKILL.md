---
name: rea-investigate
description: Run an end-to-end, evidence-led investigation of an application, website, package, binary, firmware image or software version change and deliver a verified technical report. Invoke explicitly for authorized reverse engineering.
disable-model-invocation: true
---

# REA investigate

**One entry point. Thirteen capabilities. One evidence-backed report.**

You are the **investigator**, not a checklist reader. Own the investigation from a concrete question to a reproducible report. REA is an instrument; the file system, build tools, test runner and careful reasoning are part of the job. Load only the references needed for the target. Do not invoke other REA skills.

## Steps

1. **Define the case.** Identify the exact target, feature/question, owner or authorization, available build(s), OS and expected answer. For a vague request, choose a bounded initial question and state it; ask only for an indispensable missing target or authorization. Read-only static analysis is the default. Active capture, process execution, network effects, authentication, state changes and reconstruction have separate approval gates. Identify secrets and sensitive material before submitting raw Evidence to models.

2. **Create the case.** From this skill directory run `python3 scripts/case.py init --target '<absolute path or URL>' --question '<question>' --out '<case directory>'`. Keep the original input untouched. The output directory is the single source of truth: `case.json`, `evidence/`, `notes/`, `REPORT.md`. Record file digests and directory manifests as applicable. A URL is not a hashed local file; record URL and observation time.

3. **Build the route.** Read `references/capabilities.md`. Assess all **13 capabilities**; apply every relevant one, and give a precise reason for each inapplicable one. S01 scope and S02 artifact mapping normally apply; S12 evidence audit always applies. At least one domain-specific investigation (S03–S10 or S13) must be attempted unless this is solely a report audit. A hardware, native, Electron, web or mobile target will not use every capability. Run `python3 scripts/case.py stage <case-dir> <ID> <status> --reason '<why>'` to update the ledger. Use `blocked` for missing tools/permission, never `not-applicable`.

4. **Prove, don't narrate.** Read `references/evidence.md`. Check actual `rea --help`, `rea capabilities --json`, `rea providers --json` **only when the investigation needs REA**; prefer a registered, working REA MCP endpoint when available. Use its advertised schemas, not assumed flags. Start with cheap inspection, then follow narrow seeds through callers/callees, modules, routes, IPC, imports and side effects. For each decisive finding, save the complete raw source under `evidence/`, register it in the ledger, and attach a precise locator (byte offset, address, function, record ordinal, JSON pointer, page, selector, file+line, or time interval). Separate direct observations from static inference, runtime inference and open hypotheses. Stop at an unverified boundary; write the next experiment rather than connecting fictional edges.

5. **Trace end to end.** Load the matching reference branch in `references/techniques/`: `applications.md` for JS/Electron/browser/HAR/process, `binaries.md` for native/managed/APK/firmware, and `change-and-rebuild.md` for versions or an explicitly requested implementation. For a feature, establish the path **trigger → entry point → control/data flow → boundary → external effect**. For a runtime claim, observe the before state, action and after state with a falsifiable assertion. For a comparison, independently establish both identities and paired coverage. A recorded request is not necessarily caused by a click; decompiled pseudocode is not the original source. Reconstruct behavior in the user's codebase **only when explicitly asked**, using independent code and verification tests.

6. **Adversarial audit.** Challenge each material conclusion: what else explains it, what would falsify it, is the cited Evidence from this build, and did a missing capability create a blind spot? Mark S12 `done` only with a written challenge in `notes/audit.md` and an Evidence-backed resolution or openly unresolved risk. A passing test with invented expected behavior is not parity.

7. **Write and validate the report.** Fill the notes under `notes/` using `references/report.md` (the generator combines them with the live evidence and the 13-capability ledger). Register claim rows with `python3 scripts/case.py claim ...`. Run `python3 scripts/case.py render <case-dir>` then `python3 scripts/case.py check <case-dir> --strict`. Fix substantive gaps; when blocked, report a qualified/incomplete result, not an invented success. The final answer must link `REPORT.md`, the case folder or archive, say what was verified, name the significant unknowns, and describe the next experiment. Do not claim it executed what was only planned.

## Completion criteria

The case is **complete** only when (a) all 13 stages have `done`, `not-applicable` with reasons, or `blocked` with reasons; (b) every `done` stage has registered evidence (S01 may use the target inventory; S12 must include the audit note); (c) at least one meaningful claim cites a valid evidence ID; (d) the report has nonempty overview, architecture, trace/behavior, verification, and limitation sections; and (e) the strict validator passes. `blocked` may still produce a useful report but cannot be described as fully verified. Treat any skipped relevant stage as a coverage defect.

## Invocation examples

- `/rea-investigate /Applications/Example.app — trace the Export action from UI to file output and report all evidence.`
- `/rea-investigate ./app.asar — determine how session search is implemented. Static only.`
- `/rea-investigate old.apk new.apk — compare sign-in behavior and generate a version-diff report.`

## Boundaries

Investigate only owned or authorized targets. Keep active experiments isolated and consented. Do not bypass access controls, harvest credentials, send sensitive captures to external services, flash devices or run untrusted executables by default. Do not redistribute proprietary code or protected assets in reports. REA's upstream tools and native providers must be installed independently; this skill does not bundle them or claim unsupported platform capabilities. For setup and command variability see `references/tooling.md`.
