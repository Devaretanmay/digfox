"""Graph provider adapters for Fox Graph."""
from __future__ import annotations

try:
    from .base import GraphProvider
    from .gitnexus_adapter import GitNexusProvider
    from .python_ast_adapter import PythonASTProvider
except (ImportError, ValueError):
    from adapters.base import GraphProvider
    from adapters.gitnexus_adapter import GitNexusProvider
    from adapters.python_ast_adapter import PythonASTProvider


def get_provider(name: str = "auto") -> GraphProvider:
    """Resolve graph provider based on name and environment availability."""
    if name == "gitnexus":
        return GitNexusProvider()
    if name == "python-ast":
        return PythonASTProvider()

    # auto resolution: Prefer GitNexus if available, fallback to python-ast
    gn = GitNexusProvider()
    from pathlib import Path
    if gn.is_available(Path.cwd()):
        return gn
    return PythonASTProvider()


__all__ = ["GraphProvider", "GitNexusProvider", "PythonASTProvider", "get_provider"]
