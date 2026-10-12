#!/usr/bin/env python3
"""Small deterministic example: no agent needed to calculate invoice totals."""
import argparse
import csv
import json
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


def summarize(path: Path):
    result = defaultdict(lambda: Decimal("0"))
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["invoice", "department", "amount"]:
            raise ValueError("Expected exact invoice,department,amount columns")
        seen = set()
        for index, row in enumerate(reader, 2):
            if not row["invoice"] or not row["department"] or not row["amount"]:
                raise ValueError(f"Missing data at row {index}")
            if row["invoice"] in seen:
                raise ValueError(f"Duplicate invoice at row {index}")
            seen.add(row["invoice"])
            try:
                amount = Decimal(row["amount"])
            except InvalidOperation as error:
                raise ValueError(f"Invalid amount at row {index}") from error
            if not amount.is_finite() or amount < 0:
                raise ValueError(f"Negative or nonfinite amount at row {index}")
            result[row["department"]] += amount
    return {category: str(value.quantize(Decimal(".01"))) for category, value in sorted(result.items())}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    args = p.parse_args()
    print(json.dumps(summarize(args.input), sort_keys=True))

if __name__ == "__main__":
    main()
