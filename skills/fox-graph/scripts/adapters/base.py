"""Base interface for Fox Graph providers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple

try:
    from ..models import Edge, PatchHunk, Symbol
except (ImportError, ValueError):
    from models import Edge, PatchHunk, Symbol


class GraphProvider(ABC):
    """Abstract interface for local code graph indexing and relationship queries."""

    name: str = "base"

    @abstractmethod
    def is_available(self, repo_path: Path) -> bool:
        """Check if this provider's runtime and requirements are available."""
        pass

    @abstractmethod
    def index_repo(self, repo_path: Path, force: bool = False) -> bool:
        """Build or refresh the local graph index for the repository."""
        pass

    @abstractmethod
    def get_symbols(self, repo_path: Path, file_path: str) -> list[Symbol]:
        """Extract all known symbols for a specific file."""
        pass

    @abstractmethod
    def get_changed_symbols(
        self, repo_path: Path, hunks: list[PatchHunk]
    ) -> list[Symbol]:
        """Map modified diff hunks to enclosing symbols."""
        pass

    @abstractmethod
    def get_incoming_edges(
        self, repo_path: Path, symbol: Symbol, max_depth: int = 3
    ) -> tuple[list[Edge], list[Edge]]:
        """Return (direct_callers, transitive_callers) for a target symbol."""
        pass

    @abstractmethod
    def get_entry_points(
        self, repo_path: Path, symbol: Symbol
    ) -> list[Symbol]:
        """Discover public entry points that reach this symbol."""
        pass

    @abstractmethod
    def get_limitations(self, repo_path: Path) -> list[str]:
        """Disclose statically unresolvable patterns detected in this repository."""
        pass
