# Fox & Fox Explore Adoption Guide

This guide provides practical examples showing when to use Fox, when to use Fox Explore, or when to use both skills together.

---

## Decision Matrix: Which Skill Should You Use?

| Task or Objective | Recommended Skill | Why |
| :--- | :--- | :--- |
| **Fix a localized defect or logic error** (regex parsing, off-by-one errors, math bugs) | **Fox alone** | Isolates the owning layer and fixes it minimally. Builds reproducer first, tests counterexamples, and verifies zero regressions. |
| **Investigate an unfamiliar bug across system boundaries** (CLI to backend, client to server) | **Fox alone** | Traces input through execution to observable output, builds a reproducer, and repairs the owning layer directly. |
| **Onboard to an unfamiliar repository or component** | **Fox Explore alone** | Explains the request flow, identifies architectural patterns, and provides a clear map of the codebase without editing files. |
| **Evaluate trade-offs or compare external alternatives** | **Fox Explore alone** | Researches standard open-source libraries and protocols, compares architectural options, and advises on trade-offs. |
| **Plan an architectural refactor and implement it safely** | **Both (Fox Explore + Fox)** | Fox Explore evaluates alternatives and advises on design trade-offs first; Fox implements the minimal complete fix with verification. |

---

## Example 1: Localized Defect (Fox Alone)

### Scenario
An input validation regex rejects valid inputs. For instance, `validate.URL` rejects URLs with a fragment directly following an empty path, such as `https://example.com#frag`.

The defect is entirely localized to a single regular expression generator inside `src/marshmallow/validate.py`.

### Why Fox Alone?
- The root cause lives at one specific owning location.
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

## Example 2: Architecture Review & Technical Research (Fox Explore Alone)

### Scenario
A developer wants to evaluate an authentication module before expanding it:
- How does the token validation lifecycle work?
- How does our custom token decoding compare to standard libraries like PyJWT or Authlib?
- What are the architectural trade-offs?

### Why Fox Explore Alone?
- No code needs to be modified or debugged.
- The objective is understanding, comparative research, and architectural evaluation.
- Fox Explore is strictly read-only and cites verified repository paths and external documentation.

### Sample Prompt
```text
/fox-explore Review our authentication architecture:
1. Trace the token validation lifecycle from incoming HTTP request to handler execution.
2. Compare our custom token decoding with standard libraries (e.g. PyJWT or Authlib).
3. Identify trade-offs in our current implementation and advise what to improve and what to leave alone.
```

### Agent Workflow with Fox Explore
1. **Understand Question**: Identify scope (authentication middleware and token decoder) and classify as an architectural comparison.
2. **Investigate Evidence**: Trace `src/middleware/auth.py` and `src/auth/jwt.py`. Research standard RFC 7519 specifications and popular library patterns.
3. **Connect & Evaluate**: Separate implementation facts from design inference. Weigh simplicity of stdlib-only implementation against security benefits of external token libraries.
4. **Explain & Recommend**: Deliver a structured explanation with exact line references and clear advice on what to improve and what to leave alone.

---

## Example 3: Explore First, Fix with Proof (Combined Fox + Fox Explore)

### Scenario
A service experiences intermittent authentication failures during slight server time drift. The team wants to research standard clock skew handling, decide on a design, and implement a verified fix.

### Why Use Both Skills?
- **Fox Explore** conducts the read-only technical research and evaluates architectural alternatives before any code is modified.
- **Fox** enforces engineering discipline: builds a reproducer, repairs the owning layer directly, and verifies the outcome with empirical evidence.

### Sample Prompt
```text
1. Use Fox Explore to investigate standard clock-skew tolerance in token validation and recommend an approach.
2. Once the design is clear, use Fox to ground the issue, apply the minimal complete fix in src/auth/jwt.py, and verify with tests.
```

### Sequential Combined Workflow

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

---

## Best Practices for Prompting Coding Agents

Coding agents choose skills based on the terminology in user requests:

1. **To trigger Fox**: Use action words related to diagnosis and repair: `investigate root cause`, `fix defect`, `minimal fix`, `reproduce bug`, `verify regressions`.
2. **To trigger Fox Explore**: Use words related to understanding and analysis: `explain architecture`, `walk me through`, `explore alternatives`, `compare implementations`, `advise on trade-offs`.
3. **To trigger Both**: Explicitly ask to evaluate or explore first, followed by implementing and verifying the fix.
