"""Deterministic Python AST graph provider for Fox Graph."""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple

try:
    from ..models import Edge, PatchHunk, Symbol
    from .base import GraphProvider
except (ImportError, ValueError):
    from models import Edge, PatchHunk, Symbol
    from adapters.base import GraphProvider


class PythonASTProvider(GraphProvider):
    name = "python-ast"

    def __init__(self) -> None:
        self._symbols_cache: dict[str, list[Symbol]] = {}
        self._calls_cache: dict[str, list[tuple[Symbol, str, int]]] = {}  # caller_symbol, callee_name, line
        self._imports_cache: dict[str, list[tuple[str, str]]] = {}  # imported_name, from_module
        self._dynamic_patterns: list[str] = []

    def is_available(self, repo_path: Path) -> bool:
        """Always available in any standard Python environment."""
        return True

    def index_repo(self, repo_path: Path, force: bool = False) -> bool:
        """Parse all Python files in repository into symbol and call index."""
        if self._symbols_cache and not force:
            return True

        self._symbols_cache.clear()
        self._calls_cache.clear()
        self._imports_cache.clear()
        self._dynamic_patterns.clear()

        # Skip typical non-source directories
        ignored_dirs = {".git", ".venv", "venv", "__pycache__", "build", "dist", ".pytest_cache", ".gitnexus", "node_modules"}

        for py_path in repo_path.rglob("*.py"):
            if any(part in ignored_dirs for part in py_path.parts):
                continue

            rel_str = str(py_path.relative_to(repo_path))
            try:
                content = py_path.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content, filename=rel_str)
                self._index_file(rel_str, tree)
            except Exception:
                continue

        return True

    def _index_file(self, rel_path: str, tree: ast.AST) -> None:
        symbols: list[Symbol] = []
        calls: list[tuple[Symbol, str, int]] = []
        imports: list[tuple[str, str]] = []

        class Visitor(ast.NodeVisitor):
            def __init__(self, outer: PythonASTProvider):
                self.outer = outer
                self.current_symbol_stack: list[Symbol] = []

            def visit_Import(self, node: ast.Import) -> None:
                for alias in node.names:
                    imports.append((alias.asname or alias.name, alias.name))
                self.generic_visit(node)

            def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
                mod = node.module or ""
                for alias in node.names:
                    imports.append((alias.asname or alias.name, f"{mod}.{alias.name}"))
                self.generic_visit(node)

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                self._handle_func(node, "Function")

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
                self._handle_func(node, "AsyncFunction")

            def _handle_func(self, node: ast.FunctionDef | ast.AsyncFunctionDef, kind: str) -> None:
                end_line = getattr(node, "end_lineno", node.lineno)
                parent_class = [s for s in self.current_symbol_stack if s.kind == "Class"]
                sym_kind = "Method" if parent_class else kind
                sym_name = f"{parent_class[-1].name}.{node.name}" if parent_class else node.name
                is_pub = not node.name.startswith("_") or node.name.startswith("__init__")

                sym = Symbol(
                    name=sym_name,
                    kind=sym_kind,
                    file_path=rel_path,
                    start_line=node.lineno,
                    end_line=end_line,
                    is_public=is_pub,
                )
                symbols.append(sym)
                self.current_symbol_stack.append(sym)
                self.generic_visit(node)
                self.current_symbol_stack.pop()

            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                end_line = getattr(node, "end_lineno", node.lineno)
                sym = Symbol(
                    name=node.name,
                    kind="Class",
                    file_path=rel_path,
                    start_line=node.lineno,
                    end_line=end_line,
                    is_public=not node.name.startswith("_"),
                )
                symbols.append(sym)
                self.current_symbol_stack.append(sym)
                self.generic_visit(node)
                self.current_symbol_stack.pop()

            def visit_Call(self, node: ast.Call) -> None:
                callee_name = ""
                if isinstance(node.func, ast.Name):
                    callee_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    callee_name = node.func.attr

                # Flag dynamic invocation
                if callee_name in ("getattr", "setattr", "eval", "exec", "__import__"):
                    self.outer._dynamic_patterns.append(
                        f"{rel_path}:{node.lineno} uses dynamic function '{callee_name}'"
                    )

                if callee_name and self.current_symbol_stack:
                    caller = self.current_symbol_stack[-1]
                    calls.append((caller, callee_name, node.lineno))

                self.generic_visit(node)

        v = Visitor(self)
        v.visit(tree)

        self._symbols_cache[rel_path] = symbols
        self._calls_cache[rel_path] = calls
        self._imports_cache[rel_path] = imports

    def get_symbols(self, repo_path: Path, file_path: str) -> list[Symbol]:
        self.index_repo(repo_path)
        return self._symbols_cache.get(file_path, [])

    def get_changed_symbols(
        self, repo_path: Path, hunks: list[PatchHunk]
    ) -> list[Symbol]:
        self.index_repo(repo_path)
        changed: list[Symbol] = []
        seen: set[str] = set()

        for hunk in hunks:
            file_symbols = self._symbols_cache.get(hunk.file_path, [])
            for sym in file_symbols:
                # Direct match: hunk modified lines overlap symbol boundaries
                if any(sym.start_line <= line <= sym.end_line for line in hunk.modified_lines):
                    if sym.uid not in seen:
                        seen.add(sym.uid)
                        changed.append(sym)

        return changed

    def get_incoming_edges(
        self, repo_path: Path, symbol: Symbol, max_depth: int = 3
    ) -> tuple[list[Edge], list[Edge]]:
        self.index_repo(repo_path)
        direct: list[Edge] = []
        transitive: list[Edge] = []
        visited: set[str] = {symbol.uid}

        # Target short name (e.g. "func" from "Class.func" or "func")
        target_short_name = symbol.name.split(".")[-1]

        # 1. Direct callers (Depth 1)
        depth1_callers: list[Symbol] = []
        for file_path, call_list in self._calls_cache.items():
            for caller, callee_name, line in call_list:
                if callee_name == target_short_name or callee_name == symbol.name:
                    if caller.uid not in visited:
                        visited.add(caller.uid)
                        edge = Edge(
                            source=caller,
                            target=symbol,
                            relation="CALLS",
                            confidence=1.0,
                            evidence=f"{file_path}:{line}",
                        )
                        direct.append(edge)
                        depth1_callers.append(caller)

        # 2. Transitive callers (Depth 2..max_depth)
        current_layer = depth1_callers
        for depth in range(2, max_depth + 1):
            next_layer: list[Symbol] = []
            for target_caller in current_layer:
                caller_short_name = target_caller.name.split(".")[-1]
                for file_path, call_list in self._calls_cache.items():
                    for caller, callee_name, line in call_list:
                        if callee_name == caller_short_name:
                            if caller.uid not in visited:
                                visited.add(caller.uid)
                                edge = Edge(
                                    source=caller,
                                    target=target_caller,
                                    relation="CALLS",
                                    confidence=0.85,
                                    evidence=f"{file_path}:{line} (depth {depth})",
                                )
                                transitive.append(edge)
                                next_layer.append(caller)
            current_layer = next_layer
            if not current_layer:
                break

        return direct, transitive

    def get_entry_points(self, repo_path: Path, symbol: Symbol) -> list[Symbol]:
        self.index_repo(repo_path)
        direct, transitive = self.get_incoming_edges(repo_path, symbol, max_depth=3)
        all_callers = [e.source for e in direct + transitive]

        entry_points: list[Symbol] = []
        seen: set[str] = set()

        for s in all_callers:
            # Considered entry point if public and not in test suite
            if s.is_public and not s.file_path.startswith("test") and "test" not in s.name.lower():
                if s.uid not in seen:
                    seen.add(s.uid)
                    entry_points.append(s)

        return entry_points

    def get_limitations(self, repo_path: Path) -> list[str]:
        self.index_repo(repo_path)
        limitations: list[str] = [
            "Dynamic dispatch via getattr(), setattr(), or eval() cannot be statically mapped.",
            "Higher-order functions passing callbacks via *args/**kwargs require runtime tracking.",
            "Decorators wrapping function invocation are treated as direct call boundaries.",
        ]
        if self._dynamic_patterns:
            limitations.append(f"Detected {len(self._dynamic_patterns)} dynamic calls in repository (e.g. {self._dynamic_patterns[0]}).")
        return limitations
