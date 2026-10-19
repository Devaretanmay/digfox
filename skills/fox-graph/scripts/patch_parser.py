"""Unified diff parser for Fox Graph."""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

try:
    from ..models import PatchHunk
except (ImportError, ValueError):
    from models import PatchHunk

HUNK_HEADER_RE = re.compile(
    r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@"
)
OLD_FILE_HEADER_RE = re.compile(r"^---\s+(?:[ab]/)?(.*)$")
FILE_HEADER_RE = re.compile(r"^\+\+\+\s+(?:[ab]/)?(.*)$")


def parse_unified_diff(diff_text: str) -> list[PatchHunk]:
    """Parse a unified git diff into a list of PatchHunk objects.

    Tracks newly added or modified lines in the target file.
    """
    hunks: list[PatchHunk] = []
    old_file: str | None = None
    current_file: str | None = None
    is_deleted = False
    current_hunk: PatchHunk | None = None
    new_line_cursor = 0

    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            old_file = None
            current_file = None
            is_deleted = False
            current_hunk = None
            continue

        if line.startswith("--- "):
            m = OLD_FILE_HEADER_RE.match(line)
            if m:
                raw_path = m.group(1).strip()
                old_file = raw_path
            continue

        if line.startswith("+++ "):
            m = FILE_HEADER_RE.match(line)
            if m:
                raw_path = m.group(1).strip()
                if raw_path == "/dev/null":
                    current_file = old_file
                    is_deleted = True
                else:
                    current_file = raw_path
                    is_deleted = False
            continue

        if line.startswith("@@ "):
            m = HUNK_HEADER_RE.match(line)
            if m and current_file:
                old_start = int(m.group(1))
                old_lines = int(m.group(2)) if m.group(2) is not None else 1
                new_start = int(m.group(3))
                new_lines = int(m.group(4)) if m.group(4) is not None else 1
                current_hunk = PatchHunk(
                    file_path=current_file,
                    old_start=old_start,
                    old_lines=old_lines,
                    new_start=new_start,
                    new_lines=new_lines,
                    modified_lines=[],
                    is_deleted=is_deleted,
                )
                hunks.append(current_hunk)
                new_line_cursor = new_start
            continue

        if current_hunk is not None:
            if line.startswith("+"):
                # Newly added or modified line
                current_hunk.modified_lines.append(new_line_cursor)
                new_line_cursor += 1
            elif line.startswith("-"):
                # Deleted line, doesn't advance new_line_cursor
                pass
            else:
                # Context line
                new_line_cursor += 1

    return hunks
