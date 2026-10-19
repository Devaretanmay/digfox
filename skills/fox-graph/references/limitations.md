# Static Analysis Limitations in Fox Graph

Static call graphs provide valuable structural relationships, but they are not runtime execution proofs. This document outlines the fundamental boundaries of static code graph analysis.

## 1. What Static Graphs Cannot Guarantee

1. **Dynamic Method Dispatch**:
   - Python `getattr(obj, method_name)()`, JavaScript `obj[prop]()`, or Ruby `send(:symbol)` cannot be resolved statically when method names are dynamically computed at runtime.
   - Fox Graph flags occurrences of `getattr` / `eval` as dynamic limitations.

2. **Reflection and Dependency Injection**:
   - Frameworks using dependency injection containers (e.g. FastAPI dependencies, Spring beans, NestJS providers) construct call graphs dynamically based on runtime configuration.

3. **Untyped Callback Forwarding**:
   - Code that accepts `*args, **kwargs` and forwards them to arbitrary callables obscures the exact callee from static AST inspection.

4. **Decorator Rewriting**:
   - Decorators that wrap function execution can alter argument types, short-circuit execution, or dispatch asynchronously. Static call graphs treat the decorator wrapper as a direct call edge.

5. **Cross-Language Native Extensions**:
   - When Python calls into a C extension (e.g. CPython C-API) or Rust extension (PyO3), static AST tools cannot trace across the foreign-function boundary unless a specialized multi-language indexer like Joern or CodeQL is configured.

---

## 2. Epistemic Standard

In Fox Graph:
- **Confirmed Edge**: A call or import relationship directly observed in the static AST or symbol table with an exact `file:line` source anchor.
- **Inferred Relationship**: A transitive caller at depth 2 or 3 derived through multi-hop edge traversal.
- **Unresolved / Dynamic**: Any call site utilizing dynamic dispatch, reflection, or native foreign-function interfaces.

Fox Graph always states when relationships cannot be determined statically, rather than guessing or fabricating certainty.
