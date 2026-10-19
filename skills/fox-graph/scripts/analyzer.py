"""Core patch coverage and blast-radius analyzer for Fox Graph."""
from __future__ import annotations

from pathlib import Path
from typing import List, Set

try:
    from ..models import (
        CoverageGap,
        Edge,
        GraphAnalysisResult,
        PatchHunk,
        ProposedCheck,
        Symbol,
    )
    from ..patch_parser import parse_unified_diff
    from .adapters.base import GraphProvider
except (ImportError, ValueError):
    from models import (
        CoverageGap,
        Edge,
        GraphAnalysisResult,
        PatchHunk,
        ProposedCheck,
        Symbol,
    )
    from patch_parser import parse_unified_diff
    from adapters.base import GraphProvider


def analyze_patch(
    repo_path: Path,
    diff_text: str,
    provider: GraphProvider,
    objective: str = "",
) -> GraphAnalysisResult:
    """Analyze a proposed git diff to detect affected paths, blast-radius, and coverage gaps."""
    repo_path = repo_path.resolve()
    provider.index_repo(repo_path)

    hunks = parse_unified_diff(diff_text)
    changed_files = sorted(list({h.file_path for h in hunks}))

    # 1. Identify changed symbols
    changed_symbols = provider.get_changed_symbols(repo_path, hunks)

    # Fallback if no specific function was enclosed (e.g. module-level changes)
    if not changed_symbols and changed_files:
        for fpath in changed_files:
            changed_symbols.append(
                Symbol(
                    name=Path(fpath).stem,
                    kind="Module",
                    file_path=fpath,
                    start_line=1,
                    end_line=1,
                    is_public=True,
                )
            )

    # 2. Extract tested files / entry points mentioned in the diff
    tested_files: set[str] = set()
    for f in changed_files:
        if f.startswith("test") or "test" in f.lower():
            tested_files.add(f)

    # 3. Query incoming calls and public entry points
    direct_callers: list[Edge] = []
    transitive_callers: list[Edge] = []
    public_entry_points: list[Symbol] = []
    seen_callers: set[str] = set()
    seen_entry_points: set[str] = set()

    for sym in changed_symbols:
        d_callers, t_callers = provider.get_incoming_edges(repo_path, sym, max_depth=3)
        for edge in d_callers:
            if edge.source.uid not in seen_callers:
                seen_callers.add(edge.source.uid)
                direct_callers.append(edge)

        for edge in t_callers:
            if edge.source.uid not in seen_callers:
                seen_callers.add(edge.source.uid)
                transitive_callers.append(edge)

        e_points = provider.get_entry_points(repo_path, sym)
        for ep in e_points:
            if ep.uid not in seen_entry_points:
                seen_entry_points.add(ep.uid)
                public_entry_points.append(ep)

    # 4. Detect coverage gaps
    coverage_gaps: list[CoverageGap] = []
    proposed_checks: list[ProposedCheck] = []
    priority = 1

    # Check for untested public entry points
    for ep in public_entry_points:
        # Check if this entry point or its file is touched in the test diff
        is_covered_in_diff = any(ep.name.lower() in hunk.file_path.lower() for hunk in hunks if "test" in hunk.file_path)

        if not is_covered_in_diff:
            gap = CoverageGap(
                entry_point=ep,
                target_symbol=changed_symbols[0] if changed_symbols else ep,
                call_path=[ep.name, (changed_symbols[0].name if changed_symbols else "")],
                reason=(
                    f"Public entry point '{ep.name}' ({ep.file_path}:{ep.start_line}) "
                    f"routes to modified component but has no targeted test in the diff."
                ),
                risk_level="HIGH" if ep.is_public else "MEDIUM",
                suggested_check=f"Add test calling '{ep.name}()' to verify behavior remains intact under modified path.",
            )
            coverage_gaps.append(gap)

            if priority <= 3:
                check = ProposedCheck(
                    priority=priority,
                    entry_point=f"{ep.file_path}:{ep.name}",
                    relationship=f"Caller of {changed_symbols[0].name if changed_symbols else 'changed component'}",
                    suspected_failure_mode="Unhandled argument variation or regression in alternate public route.",
                    suggested_test=f"Execute {ep.name}() through its external interface with boundary inputs.",
                    why_it_matters="Verifies that fixing one entry point didn't silently regress other callers sharing the engine.",
                )
                proposed_checks.append(check)
                priority += 1

    # Check for wrapper vs engine disparity:
    # If a public wrapper was edited, but other callers use the engine directly
    for sym in changed_symbols:
        if sym.kind in ("Function", "Method") and not sym.name.startswith("_"):
            # Sibling check: find if the function delegates to an internal engine
            for edge in direct_callers:
                if edge.source.file_path != sym.file_path and not edge.source.file_path.startswith("test"):
                    check = ProposedCheck(
                        priority=min(priority, 5),
                        entry_point=f"{edge.source.file_path}:{edge.source.name}",
                        relationship=f"Cross-module consumer: calls {sym.name}",
                        suspected_failure_mode="Cross-module contract assumption broken by behavioral change.",
                        suggested_test=f"Run test suite covering {edge.source.file_path}.",
                        why_it_matters="Ensures downstream modules relying on return types or exception types continue to function.",
                    )
                    proposed_checks.append(check)
                    priority += 1
                    break

    limitations = provider.get_limitations(repo_path)

    return GraphAnalysisResult(
        repository=str(repo_path),
        diff_summary=f"{len(hunks)} hunks across {len(changed_files)} files ({', '.join(changed_files)})",
        changed_symbols=changed_symbols,
        direct_callers=direct_callers,
        transitive_callers=transitive_callers,
        public_entry_points=public_entry_points,
        tested_entry_points=sorted(list(tested_files)),
        coverage_gaps=coverage_gaps,
        proposed_checks=proposed_checks[:5],
        limitations=limitations,
        provider_name=provider.name,
    )


class PatchAnalyzer:
    """Object-oriented patch coverage analyzer."""

    def __init__(self, repo_path: Path, provider: GraphProvider):
        self.repo_path = Path(repo_path)
        self.provider = provider

    def analyze(self, diff_text: str, objective: str = "") -> GraphAnalysisResult:
        return analyze_patch(self.repo_path, diff_text, self.provider, objective=objective)

