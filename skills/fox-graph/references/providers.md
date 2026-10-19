# Code Graph Providers in Fox Graph

Fox Graph supports two local providers for building and querying code knowledge graphs.

## 1. GitNexus Provider (`gitnexus`)

GitNexus is the primary multi-language graph engine. It runs locally using Tree-sitter WASM parsers and an embedded local LadybugDB/SQLite store inside `.gitnexus/`.

### Supported Languages
- Python, TypeScript, JavaScript, Go, Rust, Java, C#, PHP, Ruby, Swift, and C++.

### Capabilities
- `gitnexus analyze`: Builds local AST symbol nodes, import edges, and call relationships.
- `gitnexus impact -d upstream <symbol>`: Computes blast-radius and upstream dependency trees with confidence scores.
- `gitnexus context <symbol>`: Provides 360-degree callers, callees, and enclosing file locations.
- `gitnexus cypher <query>`: Executes direct graph queries across symbols and edges.

### Requirements
- Node.js (`node` and `npx`) available on the system PATH.
- Zero external database server or background daemon required.

---

## 2. Python AST Provider (`python-ast`)

The Python AST provider is a zero-dependency fallback engine built directly into Fox Graph using Python's standard library `ast` module.

### Supported Languages
- Python 3.10+

### Capabilities
- Scans all `.py` files in the repository.
- Extracts classes, functions, async functions, methods, decorators, and line numbers.
- Resolves direct `ast.Call` nodes to target symbols.
- Maps `import` and `from ... import ...` namespaces across modules.
- Recursively traverses upstream call chains up to depth 3 to find public entry points.
- Automatically flags dynamic function calls (`getattr`, `eval`, `__import__`).

### Requirements
- Standard Python 3.10+ runtime. Zero external pip or npm packages required.

---

## Provider Selection

By default, Fox Graph uses `auto` resolution:
1. If `npx` or `gitnexus` is installed, it uses GitNexus for multi-language graph coverage.
2. If `npx` is not installed or for pure Python repositories, it uses `python-ast`.

You can force a specific provider with:
```bash
python3 skills/fox-graph/scripts/fox_graph.py --repo . --provider gitnexus
python3 skills/fox-graph/scripts/fox_graph.py --repo . --provider python-ast
```
