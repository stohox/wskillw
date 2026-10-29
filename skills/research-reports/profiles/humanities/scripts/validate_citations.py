#!/usr/bin/env python3
"""Validate a humanities corpus and quotation ledger."""

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

CORPUS_FIELDS = (
    "work_id",
    "author",
    "title",
    "edition",
    "year",
    "publisher",
    "locator_scheme",
    "source_id",
)
QUOTE_FIELDS = (
    "quote_id",
    "text",
    "work_id",
    "locator",
    "translation_status",
    "source_id",
    "verified",
)
VALID_TRANSLATION = {"original", "translated", "paraphrase", "unknown"}
VALID_VERIFIED = {"yes", "no", "pending"}


def validate_corpus(path: str | Path) -> dict:
    rows = read_csv_records(path, required_fields=CORPUS_FIELDS)
    problems: list[str] = []
    seen: set[str] = set()
    for line, row in enumerate(rows, start=2):
        work_id = row.get("work_id", "").strip()
        if not work_id:
            problems.append(f"row {line}: missing work_id")
        elif work_id in seen:
            problems.append(f"row {line}: duplicate work_id '{work_id}'")
        seen.add(work_id)
        for field in ("author", "title", "edition", "year", "publisher", "locator_scheme", "source_id"):
            if not row.get(field, "").strip():
                problems.append(f"row {line} ({work_id or '?'}): missing {field}")
    if problems:
        raise ValidationError("corpus issues:\n" + "\n".join(problems))
    return {"corpus_rows": len(rows)}


def validate_quotations(path: str | Path) -> dict:
    rows = read_csv_records(path, required_fields=QUOTE_FIELDS)
    problems: list[str] = []
    for line, row in enumerate(rows, start=2):
        quote_id = row.get("quote_id", "").strip()
        for field in ("text", "work_id", "locator", "source_id"):
            if not row.get(field, "").strip():
                problems.append(f"row {line} ({quote_id or '?'}): missing {field}")
        translation = row.get("translation_status", "").strip().lower()
        if translation not in VALID_TRANSLATION:
            problems.append(
                f"row {line} ({quote_id or '?'}): translation_status must be one of "
                f"{sorted(VALID_TRANSLATION)}"
            )
        verified = row.get("verified", "").strip().lower()
        if verified not in VALID_VERIFIED:
            problems.append(
                f"row {line} ({quote_id or '?'}): verified must be yes/no/pending"
            )
        if verified == "no":
            problems.append(f"row {line} ({quote_id or '?'}): quotation marked unverified")
    if problems:
        raise ValidationError("quotation issues:\n" + "\n".join(problems))
    return {"quotation_rows": len(rows)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a humanities corpus ledger and quotation ledger."
    )
    parser.add_argument("corpus", help="data/corpus.csv")
    parser.add_argument("quotations", help="data/quotations.csv")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result: dict = {}
        result.update(validate_corpus(args.corpus))
        result.update(validate_quotations(args.quotations))
        write_json_report({"ok": True, **result}, None)
        return 0
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
