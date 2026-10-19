"""GitNexus adapter for Fox Graph."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, List, Tuple

try:
    from ..models import Edge, PatchHunk, Symbol
    from .base import GraphProvider
except (ImportError, ValueError):
    from models import Edge, PatchHunk, Symbol
    from adapters.base import GraphProvider


class GitNexusProvider(GraphProvider):
    name = "gitnexus"

    def is_available(self, repo_path: Path) -> bool:
        """Check if npx or gitnexus binary is available."""
        if shutil.which("gitnexus") is not None:
            return True
        return shutil.which("npx") is not None

    def _run_cli(self, args: list[str], cwd: Path, timeout: int = 45) -> tuple[int, str, str]:
        cmd: list[str] = []
        if shutil.which("gitnexus") is not None:
            cmd = ["gitnexus"] + args
        else:
            cmd = ["npx", "--yes", "gitnexus"] + args

        try:
            res = subprocess.run(
                cmd,
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )
            return res.returncode, res.stdout, res.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout}s: {' '.join(cmd)}"
        except Exception as e:
            return -1, "", str(e)

    def index_repo(self, repo_path: Path, force: bool = False) -> bool:
        """Run gitnexus analyze to ensure index exists."""
        index_dir = repo_path / ".gitnexus"
        if index_dir.exists() and not force:
            return True

        args = ["analyze", str(repo_path)]
        if force:
            args.append("--force")

        code, out, err = self._run_cli(args, cwd=repo_path, timeout=60)
        return code == 0 and index_dir.exists()

    def get_symbols(self, repo_path: Path, file_path: str) -> list[Symbol]:
        """Query symbols for a given file via Cypher."""
        query = (
            f"MATCH (n) WHERE n.filePath = '{file_path}' AND n.startLine IS NOT NULL "
            "RETURN n.name, n.startLine, n.endLine"
        )
        code, out, err = self._run_cli(["cypher", query, "--repo", str(repo_path)], cwd=repo_path)
        symbols: list[Symbol] = []
        if code != 0 or not out.strip():
            return symbols

        try:
            json_start = out.find("{")
            if json_start != -1:
                payload = json.loads(out[json_start:])
                md = payload.get("markdown", "")
                lines = [l.strip() for l in md.splitlines() if l.strip()]
                if len(lines) >= 3:
                    for line in lines[2:]:
                        parts = [p.strip() for p in line.split("|") if p.strip()]
                        if len(parts) >= 3:
                            name, sline, eline = parts[:3]
                            try:
                                # Convert 0-indexed AST lines to 1-indexed diff lines
                                s_val = int(sline)
                                e_val = int(eline)
                                start = s_val + 1 if s_val >= 0 else 1
                                end = e_val + 1 if e_val >= 0 else start
                                symbols.append(
                                    Symbol(
                                        name=name,
                                        kind="Function",
                                        file_path=file_path,
                                        start_line=start,
                                        end_line=end,
                                        is_public=not name.startswith("_"),
                                    )
                                )
                            except ValueError:
                                continue
        except Exception:
            pass
        return symbols

    def get_changed_symbols(
        self, repo_path: Path, hunks: list[PatchHunk]
    ) -> list[Symbol]:
        """Detect changed symbols using gitnexus context or detect-changes."""
        changed: list[Symbol] = []
        seen: set[str] = set()

        for hunk in hunks:
            file_symbols = self.get_symbols(repo_path, hunk.file_path)
            for sym in file_symbols:
                # Check overlap between hunk lines and symbol lines
                if any(sym.start_line <= line <= sym.end_line for line in hunk.modified_lines):
                    if sym.uid not in seen:
                        seen.add(sym.uid)
                        changed.append(sym)

        return changed

    def get_incoming_edges(
        self, repo_path: Path, symbol: Symbol, max_depth: int = 3
    ) -> tuple[list[Edge], list[Edge]]:
        """Query callers using gitnexus impact."""
        direct: list[Edge] = []
        transitive: list[Edge] = []

        code, out, err = self._run_cli(
            ["impact", "--repo", str(repo_path), "-d", "upstream", symbol.name],
            cwd=repo_path,
        )
        if code != 0 or not out.strip():
            return direct, transitive

        try:
            # Strip preamble before JSON if any
            json_start = out.find("{")
            if json_start != -1:
                data = json.loads(out[json_start:])
                by_depth = data.get("byDepth", {})

                # Depth 1 = direct callers
                for item in by_depth.get("1", []):
                    src_sym = Symbol(
                        name=item.get("name", ""),
                        kind="Function",
                        file_path=item.get("filePath", ""),
                        start_line=0,
                        end_line=0,
                        is_public=not item.get("name", "").startswith("_"),
                    )
                    direct.append(
                        Edge(
                            source=src_sym,
                            target=symbol,
                            relation=item.get("relationType", "CALLS"),
                            confidence=float(item.get("confidence", 1.0)),
                            evidence=f"{item.get('filePath', '')} -> {symbol.name}",
                        )
                    )

                # Depth 2+ = transitive callers
                for depth_key, items in by_depth.items():
                    if depth_key != "1":
                        for item in items:
                            src_sym = Symbol(
                                name=item.get("name", ""),
                                kind="Function",
                                file_path=item.get("filePath", ""),
                                start_line=0,
                                end_line=0,
                                is_public=not item.get("name", "").startswith("_"),
                            )
                            transitive.append(
                                Edge(
                                    source=src_sym,
                                    target=symbol,
                                    relation=item.get("relationType", "CALLS"),
                                    confidence=float(item.get("confidence", 0.8)),
                                    evidence=f"depth_{depth_key}:{item.get('filePath', '')}",
                                )
                            )
        except Exception:
            pass

        return direct, transitive

    def get_entry_points(self, repo_path: Path, symbol: Symbol) -> list[Symbol]:
        """Find public callers or test entry points reaching this symbol."""
        direct, transitive = self.get_incoming_edges(repo_path, symbol, max_depth=3)
        all_callers = [e.source for e in direct + transitive]
        entry_points: list[Symbol] = []
        seen: set[str] = set()

        for s in all_callers:
            if s.is_public and s.uid not in seen:
                seen.add(s.uid)
                entry_points.append(s)

        return entry_points

    def get_limitations(self, repo_path: Path) -> list[str]:
        return [
            "Dynamic dispatch via getattr() or runtime reflection is not statically resolved.",
            "Decorators mutating function signatures or call paths require dynamic verification.",
            "Cross-language boundaries (e.g. C/Rust native extensions) may require manual inspection.",
        ]
