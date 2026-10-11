# Example excerpt - fictional demonstration, not collected evidence

**Question:** What does the Export button do?

**Finding:** Static analysis suggests the renderer calls a preload-exposed export function, which sends a request to the main process. An authorized test then observed a file appear in a temporary output directory. **Do not state the observed part unless a real process/browser capture supports it.**

| ID | Capability | Result |
| --- | --- | --- |
| S03 | JS/Electron | done, graph cited with module ID and IPC edge |
| S06 | Native | not-applicable, no native module found in the investigated artifact |
| S09 | Process | done, reproducible local capture and output-file assertion |
| S10 | Versions | not-applicable, only one build supplied and no comparison requested |

Actual generated reports contain 13 rows, exact source hashes, evidence IDs, real trace notes, test outcomes, contradiction checks and limitations. This excerpt is not evidence.
