#!/usr/bin/env python3
"""Validate a technical comparison matrix and benchmark-run ledger."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from _common import (  # noqa: E402
    ValidationError,
    error_exit,
    read_csv_records,
    write_json_report,
)

BENCHMARK_FIELDS = (
    "run_id",
    "system",
    "version_or_commit",
    "benchmark",
    "metric",
    "value",
    "unit",
    "environment",
    "run_date",
    "source_id",
)
COMPARISON_FIELDS = (
    "system_id",
    "system_name",
    "criterion",
    "assessment",
    "status",
    "evidence_source_ids",
)
VALID_STATUS = {"supports", "partial", "no", "unknown"}


def validate_benchmarks(path: str | Path) -> dict:
    rows = read_csv_records(path, required_fields=BENCHMARK_FIELDS)
    problems: list[str] = []
    seen: set[str] = set()
    for line, row in enumerate(rows, start=2):
        run_id = row.get("run_id", "").strip()
        if not run_id:
            problems.append(f"row {line}: missing run_id")
        elif run_id in seen:
            problems.append(f"row {line}: duplicate run_id '{run_id}'")
        seen.add(run_id)
        for field in ("system", "version_or_commit", "benchmark", "metric", "environment", "source_id"):
            if not row.get(field, "").strip():
                problems.append(f"row {line} ({run_id or '?'}): missing {field}")
        try:
            float(row.get("value", ""))
        except ValueError:
            problems.append(f"row {line} ({run_id or '?'}): value is not numeric")
    if problems:
        raise ValidationError("benchmark ledger issues:\n" + "\n".join(problems))
    return {"benchmark_rows": len(rows)}


def validate_comparison(path: str | Path) -> dict:
    rows = read_csv_records(path, required_fields=COMPARISON_FIELDS)
    problems: list[str] = []
    for line, row in enumerate(rows, start=2):
        status = row.get("status", "").strip().lower()
        if status not in VALID_STATUS:
            problems.append(
                f"row {line}: status must be one of {sorted(VALID_STATUS)}"
            )
        evidence = row.get("evidence_source_ids", "").strip()
        if not evidence and status != "unknown":
            problems.append(
                f"row {line}: non-unknown status requires evidence_source_ids"
            )
        if not row.get("assessment", "").strip():
            problems.append(f"row {line}: missing assessment")
    if problems:
        raise ValidationError("comparison matrix issues:\n" + "\n".join(problems))
    return {"comparison_rows": len(rows)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a technical benchmark ledger and comparison matrix."
    )
    parser.add_argument("benchmark_runs", help="data/benchmark_runs.csv")
    parser.add_argument("comparison_matrix", help="data/comparison_matrix.csv")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result: dict = {}
        result.update(validate_benchmarks(args.benchmark_runs))
        result.update(validate_comparison(args.comparison_matrix))
        write_json_report({"ok": True, **result}, None)
        return 0
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
