# REA tool setup and drift

Upstream: https://github.com/morluto/rea. The tool is evolving; take command names and JSON flags from the installed version (`rea --help`, `<command> --help`, MCP tool list). The descriptions below are **starting points**, not a pinned ABI.

- Requirements from upstream as checked October 2026: Node.js 22.x >= 22.19, 24.x >= 24.11 or 26+, plus npm. The local agent needs the `rea-agents` CLI or configured MCP connection. `npm install --global rea-agents` installs the CLI, not this skill. `npx rea-agents setup` may install its *own* skills, which this package deliberately does not call.
- JS static triage needs no native decompiler: `rea analyze-javascript-application /absolute/path --json`.
- Deep native analysis requires Hopper, Ghidra or IDA as compatible with your REA version/OS; check `rea providers --json` and `rea doctor --provider <actual-id> --json`. Never silently install an analysis engine or start a native process.
- Android static analysis depends on installed JDK/JADX per upstream docs. Browser scenarios need a compatible Chrome/Chromium host. Process capture is host-specific. Firmware extraction is platform-specific; do not claim universal support.
- Use read-only or passive modes unless the case authorizes active interaction. Save **complete Evidence envelopes** to `case/evidence/raw-*.json`, then register their local files, not a model-made summary, with `case.py evidence`.
- CLI examples are **not enough** when tools report `unavailable`, `partial`, or truncated data. Interpret the `normalized_result` and warnings; keep exact result paths and status codes in the ledger.

Official reference starting points:
- https://github.com/morluto/rea/blob/main/docs/cli.md
- https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md
- https://github.com/morluto/rea/blob/main/docs/browser-observation.md
- https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md
- https://github.com/morluto/rea/blob/main/docs/android-analysis.md
- https://github.com/morluto/rea/blob/main/docs/process-capture.md

## Principle

REA is a **measurement instrument**. Use the environment's own help and returned structured evidence as the source of truth, then the agent interprets, designs an experiment, and verifies. A missing engine means limited coverage and a qualified report, not automatic setup or a fabricated trace.
