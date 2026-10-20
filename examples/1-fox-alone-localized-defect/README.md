# Example 1: Localized Defect (Fox Alone)

This example demonstrates using **Fox alone** to diagnose and repair a localized defect without the overhead of code graph indexing.

---

## Scenario Overview

- **Problem**: A URL validation utility rejects valid absolute URLs where a fragment directly follows an empty path without query parameters (e.g., `https://example.com#frag`).
- **Standard**: RFC 3986 defines `path-abempty [ "#" fragment ]` as valid URL syntax.
- **Owning Component**: A single regex pattern generator in `validate.py`.

---

## Why Fox Alone?

For localized logic and parsing bugs:
1. The bug exists in one discrete location.
2. Generating a full AST or dependency graph adds unnecessary tool calls without finding new execution paths.
3. Fox provides disciplined debugging: build reproducer, trace to owning layer, make minimal complete fix, test edge cases and counterexamples.

---

## Sample Agent Prompt

```text
/fox Investigate and fix the issue where validate.URL rejects URLs with fragments directly following an empty path with no query parameters (e.g. 'https://example.com#frag').

1. Ground: Inspect the codebase and build a minimal reproducer.
2. Trace: Follow the regex logic to the owning line.
3. Decide and Change: Apply the minimal complete fix according to RFC 3986. Do not add workaround wrappers.
4. Verify: Test counterexamples (bare '#', empty queries, normal paths) and run the test suite.
```

---

## Expected Agent Output

```markdown
### 1. Root Cause
In `validate.py`, the URL regex memoizer required either a non-empty path (`/[^?#]*`) or a query string (`\?[^#]*`) before allowing a fragment (`#.*`). When a URL has an empty path and no query, the fragment was rejected.

### 2. Files Changed
- `src/marshmallow/validate.py`: Updated regex pattern in `_regex_generator` to permit an immediate fragment after host/port.

### 3. Verification & Counterexamples
- `https://example.com#frag` -> Valid (fixed)
- `https://example.com#` -> Valid (bare fragment allowed by RFC 3986)
- `https://example.com/#frag` -> Valid (regression check)
- `https://example.com?q=1#frag` -> Valid (regression check)
- `tests/test_validate.py`: 128 passed.
```
