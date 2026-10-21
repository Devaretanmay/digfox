# Example 3: Explore First, Fix with Proof (Combined Fox + Fox Explore)

This example demonstrates using **Fox Explore and Fox together** to plan a refactor, explore technical alternatives, and then execute a verified repair.

---

## Scenario Overview

- **Context**: A service experiences intermittent token validation failures when client clocks drift slightly.
- **Goal**:
  1. Use **Fox Explore** to evaluate how standard protocols handle clock skew (e.g. leeway parameters in JWT specifications).
  2. Use **Fox** to ground the defect with a reproducer, implement the minimal complete fix, and verify zero regressions.

---

## Why Use Both Skills?

- **Fox Explore** conducts read-only technical research and evaluates architectural alternatives before any code is modified.
- **Fox** enforces engineering discipline: builds a reproducer, repairs the owning layer directly, and verifies the outcome with empirical evidence.

---

## Sample Agent Prompt

```text
1. Use Fox Explore to investigate standard clock-skew tolerance in token validation and recommend an approach.
2. Once the design is clear, use Fox to ground the issue, apply the minimal complete fix in src/auth/jwt.py, and verify with tests.
```

---

## Sequential Combined Workflow

```text
+-------------------------------------------------------------------+
| 1. Explore & Compare (Fox Explore)                                |
|    - Inspect src/auth/jwt.py:decode_token()                       |
|    - Research RFC 7519 leeway recommendations (default 5-30s)     |
|    - Recommend adding a 10s leeway parameter without breaking API |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| 2. Ground & Reproduce (Fox)                                       |
|    - Create a test proving failure when token expires by 2s       |
|    - Verify failure before touching production files              |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| 3. Minimal Complete Fix (Fox)                                     |
|    - Update src/auth/jwt.py with default leeway=10                |
|    - Repair the owning layer directly                             |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| 4. Verify & Deliver (Fox)                                         |
|    - Run reproducer to confirm it passes                          |
|    - Run full test suite to guarantee zero regressions            |
+-------------------------------------------------------------------+
```
