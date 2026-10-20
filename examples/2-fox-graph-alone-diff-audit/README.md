# Example 2: Diff Review & Blast-Radius Inspection (Fox Graph Alone)

This example demonstrates using **Fox Graph alone** to inspect a proposed code change, map upstream callers, and detect regression testing gaps before merging.

---

## Scenario Overview

- **Context**: A pull request modifies `src/auth.py:parse_token` to handle base64 URL-safe padding.
- **Objective**: Review the diff, identify all callers across the codebase, check whether the PR touched appropriate test suites, and generate a prioritized regression verification plan.

---

## Why Fox Graph Alone?

1. No code needs to be modified or debugged.
2. The user has an existing diff and wants structured impact analysis.
3. Fox Graph parses changed functions from git diff hunks and traces static call paths to produce a deterministic verification plan.

---

## Sample Agent Prompt

```text
/fox-graph Review the proposed Git diff in this branch:
1. Parse the changed symbols from the diff.
2. Trace all direct and transitive callers across modules.
3. Identify reachable public entry points that lack test coverage in the diff.
4. Generate a prioritized regression verification plan.
```

---

## CLI Execution Command

```bash
# Run Fox Graph on the current branch diff
python3 skills/fox-graph/scripts/fox_graph.py --repo . --provider python-ast
```

---

## Expected Agent Output

```markdown
### 1. Changed Symbols
- `src/auth.py`: `parse_token(raw: str) -> Token` (Modified)

### 2. Caller Hierarchy & Blast Radius
- `Direct Callers`:
  - `src/middleware.py`: `AuthMiddleware.authenticate()`
  - `src/client.py`: `APIClient.set_bearer_token()`
- `Transitive Callers (Depth 2)`:
  - `src/server.py`: `Application.handle_request()` (via `AuthMiddleware.authenticate()`)

### 3. Coverage Gaps Detected
- The PR diff updated `tests/test_auth.py`, but neither `tests/test_middleware.py` nor `tests/test_client.py` were modified.
- Alternate path risk: `APIClient.set_bearer_token()` accepts raw strings that bypass middleware sanitization.

### 4. Prioritized Regression Verification Plan
1. **Target**: `tests/test_middleware.py:test_malformed_padding`
   - *Failure Mode*: Middleware throws 500 instead of 401 on malformed base64 padding.
2. **Target**: `tests/test_client.py:test_url_safe_token`
   - *Failure Mode*: Client fails to serialize token when sending Authorization headers.
```
