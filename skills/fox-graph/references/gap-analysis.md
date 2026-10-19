# Patch Coverage and Gap Analysis Guide

This guide describes how Fox Graph identifies untested execution paths and coverage gaps surrounding proposed code changes.

## 1. What is a Coverage Gap?

A coverage gap occurs when a code change modifies an internal component or public API, but the test suite or pull request does not verify all reachable paths that exercise that modification.

### Common Gap Patterns:

1. **Untested Alternate Entry Points**:
   - An internal function `parse_url()` is modified.
   - The developer added a test for `Client.get()`.
   - The graph reveals that `AsyncClient.stream()`, `WebSocket.connect()`, and `Proxy()` also call `parse_url()`.
   - If those three entry points have no tests in the diff or test suite, Fox Graph flags them as high-priority gaps.

2. **Wrapper Bypass (Symptom Patching)**:
   - A defect is reported through a public function `fetch(url)`.
   - The developer adds an argument check inside `fetch()`.
   - The graph reveals that `batch_fetch()` calls the underlying `_execute_request()` directly, completely bypassing `fetch()`.
   - The patch is incomplete because sibling callers bypass the wrapper fix.

3. **Shared Dependency Regressions**:
   - A helper utility function in module `utils.py` is changed to accommodate Module A.
   - Module B imports the same helper and relies on its original return type, exception behavior, or default parameters.
   - Fox Graph traces downstream consumers to ensure Module B does not break silently.

---

## 2. Priority Scoring for Proposed Checks

Fox Graph ranks proposed checks from Priority 1 (highest) to Priority 5:

- **Priority 1**: Direct public entry points in the same package that route directly to the modified code and have no test coverage in the patch.
- **Priority 2**: Alternate entry points in separate consumer modules that cross module boundaries.
- **Priority 3**: Cross-module consumers relying on shared data formats or return types.
- **Priority 4**: Transitive callers (depth 2 or 3) where state mutations or error handling may propagate.
- **Priority 5**: General regression suite recommendations when high fanout makes full manual testing impractical.
