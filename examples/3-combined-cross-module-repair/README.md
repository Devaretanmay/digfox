# Example 3: Cross-Module Shared Engine Defect (Combined Fox + Fox Graph)

This example demonstrates using **Fox and Fox Graph together** on a complex defect in a shared core data structure or engine reached by multiple public entry points.

---

## Scenario Overview

- **Defect**: `WWWAuthenticate.to_header()` produces illegal trailing whitespace (`Bearer `) when initialized without parameters.
- **Standards RFC**: RFC 9110 Section 11.6.1 requires challenges without parameters to consist strictly of the auth-scheme without whitespace. Downstream strict HTTP parsers reject the trailing space.
- **Architectural Scope**: The owning class lives in `src/werkzeug/datastructures/auth.py`, but is consumed by:
  1. `Response.www_authenticate` in `src/werkzeug/sansio/response.py`
  2. `Unauthorized.get_headers()` in `src/werkzeug/exceptions.py`
  3. `WWWAuthenticate.from_header()` round-trip parser

---

## Why Use Both Skills?

- **Fox** enforces engineering discipline: isolates the owning component, avoids superficial wrapper fixes, and enforces contract symmetry (round-trip equality).
- **Fox Graph** automates call-graph mapping: queries AST call paths, confirms all entry points that invoke `to_header()`, and provides a structured checklist of test files that must be verified before completing the repair.

---

## Sample Agent Prompt

```text
Diagnose, analyze, and repair the defect where WWWAuthenticate emits trailing whitespace for parameterless challenges:
1. Ground the defect with a reproducer and trace the root cause to the owning component using Fox.
2. Run a blast-radius analysis with Fox Graph to identify all callers and public entry points.
3. Apply a minimal complete fix at the owning layer using Fox.
4. Verify the repair across the owning component and all entry points flagged by Fox Graph.
```

---

## Sequential Combined Workflow

1. **Ground (Fox)**: Agent constructs a reproduction script proving `WWWAuthenticate("bearer").to_header()` outputs `'Bearer '`.
2. **Trace & Blast Radius (Fox + Fox Graph)**:
   - Fox traces the issue to `dump_header({})` returning `""` in string interpolation `f"{scheme} {dump_header(params)}"`.
   - Fox Graph indexes call hierarchies and maps consumers: `response.py` and `exceptions.py`.
3. **Decide & Change (Fox)**:
   - In `auth.py`, omit whitespace when parameters and tokens are absent.
   - In `from_header()`, ensure parameterless challenge strings parse as `token=None` so `from_header("Bearer") == WWWAuthenticate("bearer")`.
4. **Coverage Gaps & Verification Plan (Fox Graph)**:
   - Fox Graph identifies three test targets: `test_http.py`, `test_wrappers.py`, `test_exceptions.py`.
5. **Verify & Deliver (Fox)**:
   - Agent writes regression tests across all three test files.
   - Runs full pytest suite to verify zero regressions.

---

## Expected Agent Output

```markdown
### 1. Root Cause & Owning Layer
In `src/werkzeug/datastructures/auth.py`, `WWWAuthenticate.to_header()` used `f"{self.type.title()} {dump_header(self.parameters)}"`. For parameterless challenges, `dump_header` returned an empty string, leaving a trailing space.

### 2. Blast Radius & Entry Points (Fox Graph)
- `WWWAuthenticate.to_header()` (Direct)
- `Response.www_authenticate` in `src/werkzeug/sansio/response.py` (Property setter)
- `Unauthorized.get_headers()` in `src/werkzeug/exceptions.py` (Exception serialization)
- `WWWAuthenticate.from_header()` (Parser round-trip)

### 3. Files Changed
- `src/werkzeug/datastructures/auth.py`: Minimal fix at owning layer.
- `tests/test_http.py`: Added parameterless challenge serialization and equality tests.
- `tests/test_exceptions.py`: Added Unauthorized header tests.
- `tests/test_wrappers.py`: Added Response property setter tests.

### 4. Verification Output
- `uv run pytest tests/test_http.py tests/test_exceptions.py tests/test_wrappers.py` -> 309 passed.
```
