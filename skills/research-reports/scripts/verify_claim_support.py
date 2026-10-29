#!/usr/bin/env python3
"""Verify claim-level evidence: quote, locator, support status, source depth."""

from __future__ import annotations

import argparse
from pathlib import Path

from _common import (
    ValidationError,
    error_exit,
    read_csv_records,
    split_ids,
    write_json_report,
)

REQUIRED = ("claim_id", "claim_text", "claim_type", "source_ids")
EVIDENCE_TYPES = {
    "quantitative_fact",
    "quantitative_estimate",
    "calculation",
    "forecast",
    "qualitative_fact",
}
VALID_STATUS = {"supported", "partial", "unsupported", "not-assessed"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify claim-level evidence. Missing columns are warnings for "
            "backward compatibility; --strict turns warnings into failures."
        )
    )
    parser.add_argument("claims", help="data/claims.csv")
    parser.add_argument("source_ledger", help="data/source_ledger.csv")
    parser.add_argument("--min-sources", type=int, default=2)
    parser.add_argument("--min-clusters", type=int, default=2)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    try:
        claims = read_csv_records(args.claims, required_fields=REQUIRED)
        sources = read_csv_records(
            args.source_ledger, required_fields=("source_id",)
        )
    except ValidationError as exc:
        return error_exit(exc)

    known_sources = {row["source_id"] for row in sources}
    has_cluster = bool(sources) and "source_cluster" in sources[0]
    clusters = {
        row["source_id"]: (row.get("source_cluster") or "").strip()
        for row in sources
    }

    issues: list[dict] = []
    support_counts: dict[str, int] = {}

    def add(severity: str, claim_id: str, message: str) -> None:
        issues.append(
            {"claim_id": claim_id, "severity": severity, "message": message}
        )

    for row in claims:
        claim_id = row["claim_id"]
        claim_type = row["claim_type"]
        status = (row.get("support_status") or "").strip().lower()
        quote = (row.get("evidence_quote") or "").strip()
        locator = (row.get("locator") or "").strip()
        source_ids = split_ids(
            row["source_ids"], f"{claim_id}.source_ids", allow_empty=True
        )

        missing = sorted(set(source_ids) - known_sources)
        if missing:
            add("error", claim_id, "source IDs missing from ledger: " + ", ".join(missing))

        support_counts[status or "missing"] = (
            support_counts.get(status or "missing", 0) + 1
        )

        if not status:
            add("warning", claim_id, "support_status is missing")
        elif status not in VALID_STATUS:
            add(
                "error",
                claim_id,
                "support_status must be one of: " + ", ".join(sorted(VALID_STATUS)),
            )
        elif status == "unsupported":
            add("error", claim_id, "claim is marked unsupported")
        elif status in {"partial", "not-assessed"}:
            add("warning", claim_id, f"claim support is {status}")

        if claim_type in EVIDENCE_TYPES:
            if not quote or not locator:
                severity = "error" if status == "supported" else "warning"
                add(
                    severity,
                    claim_id,
                    "supported evidence claims require evidence_quote and locator",
                )
            if status == "supported" and len(source_ids) < args.min_sources:
                add(
                    "warning",
                    claim_id,
                    f"only {len(source_ids)} source(s); target >= {args.min_sources}",
                )
            if has_cluster and source_ids:
                used = {
                    clusters.get(source_id, "")
                    for source_id in source_ids
                    if clusters.get(source_id, "")
                }
                if len(used) < args.min_clusters:
                    add(
                        "warning",
                        claim_id,
                        f"only {len(used)} independent source cluster(s); "
                        f"target >= {args.min_clusters}",
                    )

    errors = [item for item in issues if item["severity"] == "error"]
    warnings = [item for item in issues if item["severity"] == "warning"]
    result = {
        "valid": not errors,
        "strict": args.strict,
        "claim_count": len(claims),
        "support_counts": dict(sorted(support_counts.items())),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "issues": issues[:200],
        "notes": [
            "Missing support_status/evidence_quote/locator is a warning for old reports.",
            "--strict makes any warning fail the check.",
        ],
    }
    write_json_report(result, None)
    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
