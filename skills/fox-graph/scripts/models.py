"""Data models for Fox Graph analysis."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Symbol:
    name: str
    kind: str  # Function, Method, Class, Module
    file_path: str
    start_line: int
    end_line: int
    is_public: bool = True

    @property
    def uid(self) -> str:
        return f"{self.kind}:{self.file_path}:{self.name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "uid": self.uid,
            "name": self.name,
            "kind": self.kind,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "is_public": self.is_public,
        }


@dataclass(frozen=True)
class Edge:
    source: Symbol
    target: Symbol
    relation: str  # CALLS, IMPORTS, EXTENDS
    confidence: float = 1.0
    evidence: str = ""  # file:line or index source

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source.to_dict(),
            "target": self.target.to_dict(),
            "relation": self.relation,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }


@dataclass
class PatchHunk:
    file_path: str
    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    modified_lines: list[int] = field(default_factory=list)
    is_deleted: bool = False


@dataclass
class CoverageGap:
    entry_point: Symbol
    target_symbol: Symbol
    call_path: list[str]  # Symbol names or UIDs in call chain
    reason: str
    risk_level: str  # HIGH, MEDIUM, LOW
    suggested_check: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_point": self.entry_point.to_dict(),
            "target_symbol": self.target_symbol.to_dict(),
            "call_path": self.call_path,
            "reason": self.reason,
            "risk_level": self.risk_level,
            "suggested_check": self.suggested_check,
        }


@dataclass
class ProposedCheck:
    priority: int  # 1 (highest) to 5
    entry_point: str
    relationship: str
    suspected_failure_mode: str
    suggested_test: str
    why_it_matters: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "priority": self.priority,
            "entry_point": self.entry_point,
            "relationship": self.relationship,
            "suspected_failure_mode": self.suspected_failure_mode,
            "suggested_test": self.suggested_test,
            "why_it_matters": self.why_it_matters,
        }


@dataclass
class GraphAnalysisResult:
    repository: str
    diff_summary: str
    changed_symbols: list[Symbol] = field(default_factory=list)
    direct_callers: list[Edge] = field(default_factory=list)
    transitive_callers: list[Edge] = field(default_factory=list)
    public_entry_points: list[Symbol] = field(default_factory=list)
    tested_entry_points: list[str] = field(default_factory=list)
    coverage_gaps: list[CoverageGap] = field(default_factory=list)
    proposed_checks: list[ProposedCheck] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    provider_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "repository": self.repository,
            "diff_summary": self.diff_summary,
            "provider": self.provider_name,
            "changed_symbols": [s.to_dict() for s in self.changed_symbols],
            "direct_callers": [e.to_dict() for e in self.direct_callers],
            "transitive_callers": [e.to_dict() for e in self.transitive_callers],
            "blast_radius": [e.to_dict() for e in (self.direct_callers + self.transitive_callers)],
            "public_entry_points": [s.to_dict() for s in self.public_entry_points],
            "tested_entry_points": self.tested_entry_points,
            "coverage_gaps": [g.to_dict() for g in self.coverage_gaps],
            "proposed_checks": [c.to_dict() for c in self.proposed_checks],
            "limitations": self.limitations,
        }
