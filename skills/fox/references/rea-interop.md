# Interoperability with REA Investigator

**REA Investigator remains a distinct specialist skill.** Do not silently replace its 13 capabilities with a shallow generic research checklist. Fox is the orchestration and handoff layer; REA handles authorized software-focused Plan -> Trace -> Verify -> Report investigation. Detailed domain analysis relies on tools and providers available to the agent, not on Fox's standard-library CLI.

Source: https://github.com/Devaretanmay/rea-investigate (user's independent MIT-licensed project).

## Routes

| Task | Route |
|---|---|
| Existing business process or text/doc workflow | Fox investigation with source and example run; no REA required |
| Repo code navigation only | Read source, tests, logs; use REA if a genuine multi-layer behavioral trace is needed |
| Electron/JS bundle, native binary, APK/.NET, firmware, HAR, process, version diff | REA Investigator if installed and authorized, with its own 13-capability routing |
| Behavior reconstruction | REA evidence contract and clean-room discipline; Fox builds/tests only when explicitly authorized |

## Install REA alongside Fox

If the REA repository is cloned locally:

```sh
python3 install.py --agent codex --project /path/to/project --rea-path /path/to/rea-investigate
```

This installs both `fox` and the original `rea-investigate` as **separate** Agent Skills. They are linked by a case handoff, not copied verbatim into a fragile combined monolith. Preserve REA's own `SKILL.md`, case.py and references. Installers will not silently overwrite either skill.

## Handoff contract

1. Within REA, set the authorized target and run `python3 scripts/case.py init ...` as its own instructions specify.
2. Complete relevant REA capabilities. Mark each `done`, `not-applicable` (with reason), or `blocked` (with reason). Do not mark blocked capabilities as inapplicable.
3. For the original REA investigation, run `case.py render` then `case.py check --strict`. Preserve its status, even if strict validation cannot pass.
4. In Fox, use `python3 scripts/proof.py import-rea <fox-case> --rea-case <REA-CASE-PATH>`. It imports the original case manifest and rendered report by SHA-256, **not** the underlying raw evidence blobs.
5. Fox's imported report is attributed, **not independently verified**. Read REA's cited evidence where permitted before turning its conclusions into Fox claims. Link any downstream decision to specific claims, not generic confidence in the report.
6. Keep REA raw evidence in the original REA case (may contain sensitive material). Cite `REA case / evidence ID / locator` in Fox's own claim locator fields.

## Stop/approval boundaries

No active captures, unknown executable launch, authentication, access-control bypass, secret extraction, firmware flashing, or third-party redistribution by default. Require explicit authority and environment-specific tool availability. Recorded file metadata is not proof that dynamic analysis occurred. Do not execute arbitrary imported cases.
