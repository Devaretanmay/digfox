#!/usr/bin/env python3
"""Fox Graph CLI: Detect architectural dependencies and coverage gaps for code changes."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Support running directly or as module
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from adapters import get_provider
    from analyzer import analyze_patch
    from models import GraphAnalysisResult
else:
    from .adapters import get_provider
    from .analyzer import analyze_patch
    from .models import GraphAnalysisResult


def get_git_diff(repo_path: Path, scope: str = "unstaged", base_ref: str | None = None) -> str:
    """Retrieve git diff from repository according to requested scope."""
    cmd = ["git", "diff"]
    if scope == "staged":
        cmd.append("--cached")
    elif scope == "compare" and base_ref:
        cmd.append(base_ref)
    elif scope == "head":
        cmd.append("HEAD~1")

    try:
        res = subprocess.run(
            cmd,
            cwd=str(repo_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return res.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error fetching git diff: {e.stderr}", file=sys.stderr)
        return ""


def format_markdown_report(result: GraphAnalysisResult) -> str:
    """Render a clean, developer-focused Markdown report."""
    lines: list[str] = []
    lines.append("# Fox Graph Impact & Coverage Report")
    lines.append("")
    lines.append(f"**Repository**: `{result.repository}`")
    lines.append(f"**Provider**: `{result.provider_name}`")
    lines.append(f"**Changes**: {result.diff_summary}")
    lines.append("")

    # 1. Changed Symbols
    lines.append("## 1. Changed Components")
    if result.changed_symbols:
        for s in result.changed_symbols:
            vis = "public" if s.is_public else "internal"
            lines.append(f"- `{s.name}` ({s.kind}, {vis}) in `{s.file_path}:{s.start_line}-{s.end_line}`")
    else:
        lines.append("- No specific function or class symbols enclosed by the diff hunks.")
    lines.append("")

    # 2. Callers & Blast Radius
    lines.append("## 2. Upstream Callers & Blast Radius")
    if result.direct_callers:
        lines.append(f"**Direct Callers ({len(result.direct_callers)})**:")
        for edge in result.direct_callers[:10]:
            lines.append(
                f"- `{edge.source.name}` (`{edge.source.file_path}`) -> `{edge.target.name}` [{edge.relation}] (evidence: `{edge.evidence}`)"
            )
    else:
        lines.append("- No direct callers detected in the indexed codebase.")

    if result.transitive_callers:
        lines.append("")
        lines.append(f"**Transitive Callers ({len(result.transitive_callers)})**:")
        for edge in result.transitive_callers[:8]:
            lines.append(
                f"- `{edge.source.name}` (`{edge.source.file_path}`) -> `{edge.target.name}` (via `{edge.evidence}`)"
            )
    lines.append("")

    # 3. Public Entry Points
    lines.append("## 3. Public Entry Points Reaching Changes")
    if result.public_entry_points:
        for ep in result.public_entry_points[:8]:
            lines.append(f"- `{ep.name}` in `{ep.file_path}:{ep.start_line}`")
    else:
        lines.append("- No external public entry points found calling the modified components.")
    lines.append("")

    # 4. Coverage Gaps
    lines.append("## 4. Detected Coverage Gaps")
    if result.coverage_gaps:
        for gap in result.coverage_gaps:
            lines.append(f"### Gap [{gap.risk_level}]: `{gap.entry_point.name}`")
            lines.append(f"- **Path**: `{' -> '.join(gap.call_path)}`")
            lines.append(f"- **Finding**: {gap.reason}")
            lines.append(f"- **Suggested Action**: {gap.suggested_check}")
            lines.append("")
    else:
        lines.append("- No unverified alternate entry points detected.")
        lines.append("")

    # 5. Prioritized Verification Plan
    lines.append("## 5. Prioritized Verification Plan")
    if result.proposed_checks:
        for chk in result.proposed_checks:
            lines.append(f"### Priority {chk.priority}: `{chk.entry_point}`")
            lines.append(f"- **Relationship**: {chk.relationship}")
            lines.append(f"- **Suspected Failure Mode**: {chk.suspected_failure_mode}")
            lines.append(f"- **Recommended Check**: `{chk.suggested_test}`")
            lines.append(f"- **Why It Matters**: {chk.why_it_matters}")
            lines.append("")
    else:
        lines.append("- Standard regression test run recommended; no additional high-risk paths identified.")
        lines.append("")

    # 6. Limitations Disclosures
    lines.append("## 6. Static Analysis Limitations")
    for lim in result.limitations:
        lines.append(f"- {lim}")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fox Graph: Detect architectural dependencies and coverage gaps for code changes."
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Target repository directory (default: current directory)",
    )
    parser.add_argument(
        "--diff",
        type=Path,
        help="Path to unified diff file (if omitted, reads from git)",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Analyze staged git changes",
    )
    parser.add_argument(
        "--base",
        type=str,
        help="Compare against git base commit or branch (e.g. main)",
    )
    parser.add_argument(
        "--provider",
        choices=["auto", "gitnexus", "python-ast"],
        default="auto",
        help="Code graph provider to query",
    )
    parser.add_argument(
        "--objective",
        type=str,
        default="",
        help="Optional bug report or task objective context",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output raw JSON instead of markdown",
    )

    args = parser.parse_args(argv)
    repo = args.repo.resolve()

    if args.diff:
        diff_text = args.diff.read_text(encoding="utf-8", errors="replace")
    else:
        scope = "staged" if args.staged else ("compare" if args.base else "unstaged")
        diff_text = get_git_diff(repo, scope=scope, base_ref=args.base)

    if not diff_text.strip():
        print(
            "No diff detected. Pass --diff <path>, stage changes with git add, or use --base <ref>.",
            file=sys.stderr,
        )
        return 1

    provider = get_provider(args.provider)
    result = analyze_patch(
        repo_path=repo,
        diff_text=diff_text,
        provider=provider,
        objective=args.objective,
    )

    if args.output_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(format_markdown_report(result))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
