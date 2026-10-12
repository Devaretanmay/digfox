# Real investigation excerpt: Zettlr document export pipeline

**Target:** `Zettlr v4.8.0` (commit `0d2839e`)  
**Question:** Trace the document Export feature end to end from the renderer UI popover across the IPC preload bridge to main process Pandoc execution and file system output.

**Finding:** In `source/win-main/PopoverExport.vue`, clicking Export triggers `startExport()`, which dispatches `window.ipc.invoke('application', { command: 'export', payload: ... })`. The request crosses the preload context bridge (`source/common/modules/preload/index.ts`) into the main process where `CommandProvider` (`source/app/service-providers/commands/index.ts`) routes the action to `Export.run()` (`source/app/service-providers/commands/export.ts`). If the active document has unsaved buffer modifications in `DocumentManager`, a temporary snapshot is written to `app.getPath('temp')`. The main process resolves the target output directory, registers a background task with `lrt.registerTask`, and spawns Pandoc via `makeExport()`, triggering desktop notifications and file reveal upon success.

| ID | Capability | Result | Evidence / Reason |
| --- | --- | --- | --- |
| S01 | Scope and question | done | E0001 (target identity and directory manifest) |
| S02 | Artifact map | done | E0002 (architecture layers and component inventory) |
| S03 | JS/Electron trace | done | E0003, E0004, E0005, E0006, E0007 (end-to-end IPC trace) |
| S09 | Process capture | done | E0008 (build commit hash 0d2839e and pandoc CLI check) |
| S12 | Adversarial audit | done | notes/audit.md (renderer isolation, dirty buffers, Pandoc CLI boundaries) |

Generated using REA Investigator with SHA-256 cryptographic provenance and strict structural validation.
