# The 13-capability coverage model

This is **one investigation workflow**, not thirteen invocable skills. Evaluate each capability for the case, mark `done`, `not-applicable`, or `blocked`, and ensure every active branch has its evidence and completion gate satisfied. An N/A decision must cite an objective target-specific fact; missing tooling, missing target files or lack of permission is `blocked`. S01, S02 and S12 are universal except an audit-only case may mark S02 N/A if no artifact is supplied.

| ID | Capability | Trigger | Evidence and exit gate |
| --- | --- | --- | --- |
| S01 | Question and scope | Every case | Exact question, target, authorization, permitted operations and falsifiable expected observation |
| S02 | Artifact and attack-surface map | Local app, package, firmware, build or website | Digest or source URL, type checked from bytes / observed page, key components, entry points and uncovered regions |
| S03 | JS/Electron feature trace | JS, ASAR, Electron or renderer/preload/main handoff | Reachable graph with precise evidence per module/IPC hop; runtime conclusions reserved for experiments |
| S04 | Browser observation | Actual page action, navigation, DOM or UI state question | Recorded before/action/after state with a changed-state assertion and observation window |
| S05 | Network reconstruction | User-supplied HAR/mitm trace or permitted capture | Request/response sequence tied to actual record ordinals; credentials redacted; inferred causality tested separately |
| S06 | Native function analysis | Mach-O, ELF, PE or embedded native boundary | Provider, symbols/strings, xrefs, control-flow, pseudocode corroborated by instructions and build digest |
| S07 | Android package analysis | APK/AAB-derived APK | Manifest, DEX/class/method reference, native/JNI handoffs, missing reflection/runtime boundaries |
| S08 | Managed .NET analysis | Valid PE/CLI metadata | Type/member/CIL and P/Invoke evidence; no guesses based only on DLL extension |
| S09 | Process/terminal behavior | CLI or local process behavior relevant and authorized | Input, stdout/stderr, exit state, before/after file state; recording is not confinement |
| S10 | Build/version comparison | Two exact versions requested/supplied | Independent build identity, comparable coverage and evidence-backed changed/unchanged/unknown decisions |
| S11 | Independent behavioral reconstruction | User **explicitly requests** new implementation | Verified contract, original observations or clearly labeled assumptions, tests and mismatch table |
| S12 | Evidence and alternative-hypothesis audit | Every case | `notes/audit.md`: strongest alternative per major claim, evidence challenges, gaps, residual uncertainties |
| S13 | Firmware inventory | Firmware image/embedded OS dump | Image digest, safe extraction map with offsets, parser limits and static candidate components; no flashing |

## Dispatch rule

1. Classify target and question, then assign the **minimum complete** branch graph. S01 → S02 → all relevant modality stages (S03–S10/S13) → optional S11 → S12 → report.
2. If tracing reveals a new boundary (Electron native addon, APK JNI, .NET P/Invoke, web API), **reopen** the corresponding stage; record that handoff in notes. No automatic traversal beyond authorization.
3. Use S04 and S09 only when actual execution is required and approved, never as casual dependency checks. Use S05 for an available/authorized capture, not imagined network events.
4. When the user says *everything*, examine all reachable and authorized subsystems relevant to the declared question. The 13 checkboxes are **types of investigation**, not an assertion that every app has all thirteen kinds of code.
5. Stage is `done` only after its exit gate is met and source Evidence is registered; otherwise choose `blocked` with the exact missing observation/tool/permission.

## Coverage traps

- `not-applicable`: e.g. verified ELF has no managed runtime; no second version exists and none was requested; no implementation was requested.
- `blocked`: e.g. a relevant APK needs JADX and it is missing; the target is dynamic but active capture is not authorized; a native provider is unavailable.
- `pending`: not yet investigated. Must not remain at report completion.
- `done`: an evidence-linked outcome. Never equate a command's success with a validated finding.
