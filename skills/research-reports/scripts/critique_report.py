#!/usr/bin/env python3
"""Critique a drafted report before delivery: placeholders, refs, figures, prose."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

from _common import write_json_report

PLACEHOLDER = re.compile(
    r"(?<!-)\b(TBD|TODO|FIXME|XXX)\b|\[citation needed\]|待补|待填", re.I
)
CJK = re.compile(r"[\u4e00-\u9fff]")
CLAIM_ID = re.compile(r"C-\d{3}")
SOURCE_ID = re.compile(r"S-\d{3}")
IMAGE = re.compile(r"^!\[[^\]]*\]\(([^)]+)\)\s*$", re.M)
TABLE_SEP = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")
EN_WORD = re.compile(r"[A-Za-z][A-Za-z'-]+")


def count_zh(text: str) -> int:
    return len(CJK.findall(text))


def count_words(text: str) -> int:
    return len(EN_WORD.findall(text))


def sections(text: str) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    title = ""
    body: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if title:
                result.append((title, "\n".join(body)))
            title = line[3:].strip()
            body = []
        elif title:
            body.append(line)
    if title:
        result.append((title, "\n".join(body)))
    return result


def table_count(text: str) -> int:
    lines = text.splitlines()
    count = 0
    for index, line in enumerate(lines):
        if (
            index > 0
            and lines[index - 1].strip().startswith("|")
            and TABLE_SEP.match(line)
            and "-" in line
        ):
            count += 1
    return count


def prose_ratio(text: str) -> float:
    total = count_zh(text)
    if total == 0:
        return 0.0
    prose = 0
    in_code = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if (
            not stripped
            or stripped.startswith("|")
            or stripped.startswith("- ")
            or stripped.startswith("* ")
            or stripped.startswith("> ")
            or stripped.startswith("!")
            or stripped.startswith("#")
        ):
            continue
        prose += count_zh(line)
    return round(prose / total, 3)


def load_claims(path: Path | None) -> tuple[set[str], dict[str, int], bool]:
    if path is None or not path.is_file():
        return set(), {}, False
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig")))
    ids = {row.get("claim_id", "") for row in rows if row.get("claim_id")}
    counts: dict[str, int] = {}
    has_status = bool(rows) and "support_status" in rows[0]
    for row in rows:
        status = (row.get("support_status") or "missing").strip().lower() or "missing"
        counts[status] = counts.get(status, 0) + 1
    return ids, counts, has_status


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Critique a report before delivery."
    )
    parser.add_argument("report", help="report.md")
    parser.add_argument("--claims", help="data/claims.csv")
    parser.add_argument("--contract", help="report_contract.json")
    parser.add_argument("--source-ledger", help="data/source_ledger.csv")
    parser.add_argument("--min-prose-ratio", type=float, default=0.6)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    report = Path(args.report)
    if not report.is_file():
        raise SystemExit(f"report not found: {report}")
    text = report.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []

    for match in PLACEHOLDER.finditer(text):
        line = text[: match.start()].count("\n") + 1
        errors.append(f"placeholder at line {line}: {match.group(0)}")

    claim_ids, support_counts, has_status = load_claims(
        Path(args.claims) if args.claims else None
    )
    if args.claims:
        refs = set(CLAIM_ID.findall(text))
        missing = sorted(refs - claim_ids)
        if missing:
            errors.append("claim refs missing from ledger: " + ", ".join(missing))

    if args.source_ledger:
        source_path = Path(args.source_ledger)
        if source_path.is_file():
            rows = list(csv.DictReader(source_path.open(encoding="utf-8-sig")))
            known = {row.get("source_id", "") for row in rows if row.get("source_id")}
            refs = set(SOURCE_ID.findall(text))
            missing = sorted(refs - known)
            if missing:
                errors.append("source refs missing from ledger: " + ", ".join(missing))

    figures = IMAGE.findall(text)
    for src in figures:
        if not (report.parent / src).is_file():
            errors.append(f"figure file not found: {src}")

    section_list = sections(text)
    if not section_list:
        errors.append("report has no level-2 sections")
    short_sections = [title for title, body in section_list if count_zh(body) < 100]
    if short_sections:
        warnings.append(
            "sections under 100 Chinese chars: " + ", ".join(short_sections[:10])
        )

    ratio = prose_ratio(text)
    if ratio < args.min_prose_ratio:
        warnings.append(
            f"prose ratio {ratio:.2f} below target {args.min_prose_ratio:.2f}"
        )

    contract_path = Path(args.contract) if args.contract else report.with_name(
        "report_contract.json"
    )
    section_targets = {}
    if contract_path.is_file():
        try:
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            section_targets = contract.get("section_targets", {}) or {}
        except json.JSONDecodeError:
            warnings.append("report_contract.json is not valid JSON")

    for key, target in section_targets.items():
        matched = [body for title, body in section_list if key in title]
        if not matched:
            warnings.append(f"section target '{key}' not found in report")
            continue
        body = "\n".join(matched)
        actual = count_zh(body)
        minimum = int(target.get("min_chars", 0))
        maximum = int(target.get("max_chars", 0))
        if minimum and actual < minimum:
            warnings.append(f"section '{key}' has {actual} chars; min {minimum}")
        if maximum and actual > maximum:
            warnings.append(f"section '{key}' has {actual} chars; max {maximum}")

    if has_status:
        if support_counts.get("unsupported"):
            errors.append(
                f"{support_counts['unsupported']} claim(s) marked unsupported"
            )
        if support_counts.get("partial"):
            warnings.append(
                f"{support_counts['partial']} claim(s) marked partial"
            )
        if support_counts.get("missing"):
            warnings.append(
                f"{support_counts['missing']} claim(s) have no support_status"
            )
    elif args.claims:
        warnings.append(
            "claims.csv has no support_status column; claim-level verification skipped"
        )

    chars_zh = count_zh(text)
    claims_count = len(claim_ids)
    density = round(claims_count / (chars_zh / 1000), 2) if chars_zh else 0
    if chars_zh >= 2000 and density < 1.0:
        warnings.append(f"claim density {density}/1k chars is low (< 1.0)")

    result = {
        "valid": not errors,
        "strict": args.strict,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "chars_zh": chars_zh,
            "words_en": count_words(text),
            "sections": len(section_list),
            "figures": len(figures),
            "tables": table_count(text),
            "prose_ratio": ratio,
            "claim_ids": claims_count,
            "claim_density_per_1k_chars": density,
            "support_counts": support_counts,
        },
    }
    write_json_report(result, None)
    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
