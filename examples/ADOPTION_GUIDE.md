# Fox & Fox Graph Adoption Guide

This guide provides practical examples showing when to use Fox, when to use Fox Graph, or when to use both skills together.

---

## Decision Matrix: Which Skill Should You Use?

| Task or Objective | Recommended Skill | Why |
| :--- | :--- | :--- |
| **Fix a localized defect or logic error** (regex parsing, off-by-one errors, math bugs) | **Fox alone** | Isolates the owning layer and fixes it minimally. Running graph indexing on single-site defects adds tool overhead without finding new paths. |
| **Investigate an unfamiliar bug across system boundaries** (CLI to backend, client to server) | **Fox alone** | Traces input through execution to observable output, builds a reproducer, and repairs the owning layer directly. |
| **Audit a proposed Git diff or Pull Request** before merging | **Fox Graph alone** | Parses diff hunks, queries caller hierarchies, identifies unpatched alternate paths, and lists missing regression tests without touching code. |
| **Analyze change blast radius or impact** for a proposed refactor | **Fox Graph alone** | Answers which modules and entry points are affected and determines which existing tests exercise the changed symbols. |
| **Repair a shared internal engine or parser** used by multiple public entry points | **Both (Fox + Fox Graph)** | Fox drives the investigation, diagnosis, and minimal repair. Fox Graph maps upstream callers and generates regression targets across all entry points. |
| **High-stakes refactoring of core data structures or routing tables** | **Both (Fox + Fox Graph)** | Combines Fox root-cause rigor with deterministic graph impact analysis to verify that no sibling entry points are bypassed. |

---

## Example 1: Localized Defect (Fox Alone)

### Scenario
An input validation regex rejects valid inputs. For instance, `validate.URL` rejects URLs with a fragment directly following an empty path, such as `https://example.com#frag`.

The defect is entirely localized to a single regular expression generator inside `src/marshmallow/validate.py`.

### Why Fox Alone?
- The root cause lives at one specific owning location.
- Running code graph indexing adds unnecessary tool steps (~10-15 steps) and latency.
- Fox's four-step workflow ensures a reproducer is built first, counterexamples are tested (such as bare `#` and query strings), and the fix remains minimal.

### Sample Prompt
```text
Investigate and fix the issue where validate.URL rejects URLs with fragments directly following an empty path (e.g., 'https://example.com#frag').
1. Trace the defect to the owning component.
2. Build a reproduction script and test counterexamples.
3. Apply a minimal complete fix at the owning layer.
4. Verify with the project test suite.
```

### Agent Workflow with Fox
1. **Ground**: Inspect `src/marshmallow/validate.py` and run the existing test suite (`pytest tests/test_validate.py`). Create a minimal reproducer proving `validate.URL()("https://example.com#frag")` raises an unexpected ValidationError.
2. **Trace**: Follow the URL regex generator pattern down to the path/query/fragment boundary. Identify that the regex requires a trailing slash before a fragment when no query parameters are present.
3. **Decide and Change**: Modify only the regex pattern at the owning line in `src/marshmallow/validate.py`. Do not wrap the validator or add special-case string replaces.
4. **Verify and Deliver**: Run the reproducer to confirm it passes. Test edge cases: `https://example.com#`, `https://example.com/#frag`, and `https://example.com?query=1#frag`. Run the full validation test suite.

---

## Example 2: Diff Review & Blast-Radius Inspection (Fox Graph Alone)

### Scenario
A developer submits a pull request changing an authentication token parsing utility. Before approving the PR, the engineering team wants to know:
- Which callers and public entry points are affected by this change?
- Did the author miss any sibling entry points that also parse tokens?
- What tests should be run or written to verify this change?

### Why Fox Graph Alone?
- No code needs to be modified or debugged.
- The objective is analysis, blast-radius mapping, and test gap detection.
- Fox Graph parses the Git diff directly and queries static call graphs to output a structured verification plan.

### Sample Prompt
```text
Analyze the proposed changes in the current Git diff using Fox Graph:
1. Parse the changed symbols and affected files.
2. Map all direct and transitive callers up to depth 3.
3. Identify any public entry points that exercise the changed logic but lack test coverage in the diff.
4. Output a prioritized regression verification plan with up to five test targets.
```

### Agent Workflow with Fox Graph
1. **Understand Patch**: Run `python3 skills/fox-graph/scripts/fox_graph.py --repo .` to parse modified functions and classes.
2. **Query Relationships**: Retrieve direct callers and upstream consumers across modules.
3. **Detect Coverage Gaps**: Compare callers against modified test files in the diff. Flag that `response.py` and `exceptions.py` invoke the changed function, but the PR only updated unit tests for the utility itself.
4. **Deliver Verification Plan**: Produce a prioritized checklist specifying:
   - Target 1: `Response.www_authenticate` setter
   - Target 2: `Unauthorized` exception header generator
   - Target 3: Bidirectional round-trip parsing equality

---

## Example 3: Cross-Module Shared Engine Defect (Combined Fox + Fox Graph)

### Scenario
A shared header serialization class (`WWWAuthenticate` in `src/werkzeug/datastructures/auth.py`) outputs trailing whitespace (`Bearer `) when initialized without realm or parameters.

This component is consumed across three distinct architectural layers:
1. Direct challenge formatting: `WWWAuthenticate("bearer").to_header()`
2. Response header properties: `response.www_authenticate = WWWAuthenticate("bearer")`
3. Exception serialization: `raise Unauthorized(www_authenticate=WWWAuthenticate("bearer"))`

A fix at the owning layer must not break existing callers, and every public entry point must be verified against downstream HTTP parsers.

### Why Use Both Skills?
- **Fox** governs engineering discipline: isolates the owning layer, refuses superficial workarounds, writes minimal code, and ensures contract symmetry (such as `from_header` round-trip equality).
- **Fox Graph** supplies deterministic caller and blast-radius intelligence: maps upstream callers, flags unverified public entry points, and ensures test coverage across all affected modules.

### Sample Prompt
```text
Diagnose, analyze, and repair the defect where WWWAuthenticate emits trailing whitespace for parameterless challenges:
1. Use Fox to investigate the root cause at the owning layer and implement a minimal complete fix.
2. Use Fox Graph to perform a blast-radius analysis mapping all callers, affected modules, and public entry points.
3. Verify the fix across the owning component and all public entry points discovered by Fox Graph.
```

### Sequential Combined Workflow

```text
+-------------------------------------------------------------------+
| 1. Ground & Reproduce (Fox)                                       |
|    - Create reproducer for WWWAuthenticate("bearer").to_header()   |
|    - Confirm trailing whitespace ('Bearer ')                      |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| 2. Trace & Blast Radius Mapping (Fox + Fox Graph)                 |
|    - Fox traces execution to auth.py:to_header()                  |
|    - Fox Graph indexes call hierarchy via local AST / GitNexus    |
|    - Fox Graph identifies callers: response.py, exceptions.py     |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| 3. Minimal Complete Fix (Fox)                                     |
|    - Patch auth.py to omit trailing whitespace                    |
|    - Patch from_header() to set token=None for scheme-only input  |
|    - No monkey-patching or wrapper workarounds                    |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| 4. Test Gap & Verification Plan (Fox Graph)                       |
|    - Fox Graph checks diff against caller graph                   |
|    - Generates target list: test_http.py, test_exceptions.py,     |
|      and test_wrappers.py                                         |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| 5. Multi-Point Verification (Fox)                                 |
|    - Add test assertions across all three target files            |
|    - Run full test suite to guarantee zero regressions            |
+-------------------------------------------------------------------+
```

---

## Best Practices for Prompting Coding Agents

Coding agents choose skills based on the terminology in user requests:

1. **To trigger Fox**: Use action words related to diagnosis and repair: `investigate root cause`, `fix defect`, `minimal fix`, `reproduce bug`, `verify regressions`.
2. **To trigger Fox Graph**: Use keywords related to impact analysis: `blast radius`, `dependency analysis`, `affected callers`, `code relationships`, `unpatched paths`, `coverage gaps`.
3. **To trigger Both**: Explicitly mention both goals: request a root-cause fix and a blast-radius analysis of affected callers and entry points.
