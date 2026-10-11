# App, browser, network and process techniques

Load for S03-S05 and S09. Commands shown here are examples from public REA docs; check the installed CLI help and MCP schemas for required arguments.

## S03 - JavaScript / Electron

1. Identify exact folder/ASAR, digest/manifest, Electron version and split between renderer, preload and main. Run `rea analyze-javascript-application /absolute/path/to/app --json > CASE/evidence/application.json`.
2. Review summary before heavy graph traversal. For large evidence, build a view request: `python3 scripts/rea_payload.py view application.json --kind summary > view-request.json`, then `rea inspect-analysis-view view-request.json --json`. Verify the installed command accepts file-based Evidence envelopes.
3. Seed an observed string/route/IPC/import/API: `python3 scripts/rea_payload.py trace application.json --seed-kind string --seed-value 'Export' > trace-request.json` and `rea trace-application-feature trace-request.json --json`. For non-`string` seeds, use exact accepted kinds from installed schema.
4. Produce entry-to-effect path with an evidence locator per edge. Document graph truncation, source maps, dynamic require/import, generated code, obfuscation and native addon gaps. Static reachability is not a runtime call.

## S04 - Browser observation

1. Determine permitted public/test URL, consent for interaction, and test account with dummy data. Define before-state, action, after-state, and a **changed** assertion; snapshot prior state to avoid false positives.
2. For passive debugging of an authorized loopback CDP browser, enumerate `rea list-browser-targets http://127.0.0.1:9222 --json` then inspect a selected target with `rea inspect-web-page` and `rea observe-web-session`; latter is a time-bounded observer, not a click executor.
3. For an isolated scenario, use an explicit scenario JSON following the installed `rea capture-browser-scenario` schema. Inspect `rea capture-browser-scenario --help`. Never invent selectors or mark clicks successful if no postcondition changed.
4. Repeat one controlled variable to test causality. Register DOM/accessibility/URL/network events and missing observations separately.

## S05 - Network / HAR

1. Check authorization and scrub credential/cookie/personal fields **before** handing a HAR to the model.
2. For saved HAR: `rea inspect-web-network-capture /absolute/path/to/session.har har --json > CASE/evidence/har.json`. Inspect local installed help for `.mitm` support and prerequisites.
3. Register a timeline: request, response, status, payload type, timestamps, source record ordinal, relative ordering, retries (observed vs inferred), and missing bodies.
4. A HAR proves recorded exchanges, not which UI handler emitted them. Correlate with S04 on controlled time windows to support runtime causal inference.

## S09 - Controlled process capture

1. Require explicit approval before executing a target that is untrusted, destructive or may affect state. Prefer disposable input/test environment. Capture is **not** a sandbox.
2. Document command, arguments, cwd, environment allowlist, stdin, timeouts and observed files in a schema-validated scenario. Inspect `rea capture-process --help` and upstream process-capture guide; save complete output.
3. Register stdout/stderr, exit code/signal, timing, observed file differences and missing state. A log is not a full syscall or network trace.
4. When comparing programs, run comparable isolated scenarios with identical inputs and check observable contracts, not superficial matching console text.

## Cross-boundary rule

A JS call into a native addon opens S06; a network call opens S05 only if there is actual approved capture; a web behavior claim opens S04 if the static graph does not establish execution. Mark new branches in `case.json` and update notes.
