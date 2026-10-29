#!/usr/bin/env python3
"""Run all report checks and emit a single scorecard."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def run(name: str, args: list[str], cwd: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {
            "valid": False,
            "errors": [proc.stderr.strip() or proc.stdout.strip() or "no output"],
        }
    return {"name": name, "returncode": proc.returncode, "payload": payload}


def summarize(check: dict) -> str:
    payload = check["payload"]
    if "source_count" in payload:
        return f"{payload['source_count']} sources"
    if "claim_count" in payload:
        return (
            f"{payload['claim_count']} claims, "
            f"{payload.get('error_count', 0)} errors, "
            f"{payload.get('warning_count', 0)} warnings"
        )
    if "row_count" in payload:
        return f"{payload['row_count']} rows"
    if "record_count" in payload:
        return f"{payload['record_count']} records"
    if "metrics" in payload:
        metrics = payload["metrics"]
        if "prose_ratio" in metrics:
            return (
                f"errors={len(payload.get('errors', []))}, "
                f"warnings={len(payload.get('warnings', []))}, "
                f"prose={metrics.get('prose_ratio')}"
            )
        return (
            f"pages={metrics.get('pages')}, chapters={metrics.get('chapters')}, "
            f"figures={metrics.get('figures')}, chars={metrics.get('chars_zh')}"
        )
    return f"valid={payload.get('valid')}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run every report check and emit a scorecard."
    )
    parser.add_argument("--report-dir", default=".")
    parser.add_argument(
        "--length", default="standard", choices=["brief", "standard", "deep"]
    )
    parser.add_argument("--pdf", help="Optional rendered PDF")
    parser.add_argument("--profile", help="Optional profile id for standard overrides")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    root = Path(args.report_dir).resolve()
    data = root / "data"
    checks: list[dict] = []

    if (data / "source_ledger.csv").is_file():
        checks.append(
            run(
                "validate_evidence_ledger.py",
                [str(data / "source_ledger.csv")],
                root,
            )
        )
    if (data / "claims.csv").is_file() and (data / "source_ledger.csv").is_file():
        checks.append(
            run(
                "audit_claim_citations.py",
                [str(data / "claims.csv"), str(data / "source_ledger.csv")],
                root,
            )
        )
        support_args = [
            str(data / "claims.csv"),
            str(data / "source_ledger.csv"),
        ]
        if args.strict:
            support_args.append("--strict")
        checks.append(run("verify_claim_support.py", support_args, root))
    if (
        (data / "competitor_feature_matrix.csv").is_file()
        and (data / "source_ledger.csv").is_file()
    ):
        checks.append(
            run(
                "validate_competitor_matrix.py",
                [
                    str(data / "competitor_feature_matrix.csv"),
                    "--source-ledger",
                    str(data / "source_ledger.csv"),
                ],
                root,
            )
        )
    if (data / "consistency_input.csv").is_file():
        checks.append(
            run(
                "check_unit_consistency.py",
                [str(data / "consistency_input.csv")],
                root,
            )
        )

    report = root / "report.md"
    if report.is_file():
        standard_args = [str(report), "--length", args.length]
        pdf = Path(args.pdf) if args.pdf else root / "report.pdf"
        if pdf.is_file():
            standard_args += ["--pdf", str(pdf)]
        if args.profile:
            standard_args += ["--profile", args.profile]
        checks.append(run("check_report_standard.py", standard_args, root))

        critique_args = [str(report)]
        if (data / "claims.csv").is_file():
            critique_args += ["--claims", str(data / "claims.csv")]
        if (data / "source_ledger.csv").is_file():
            critique_args += ["--source-ledger", str(data / "source_ledger.csv")]
        contract = root / "report_contract.json"
        if contract.is_file():
            critique_args += ["--contract", str(contract)]
        if args.strict:
            critique_args.append("--strict")
        checks.append(run("critique_report.py", critique_args, root))

    hard = {
        "validate_evidence_ledger.py",
        "audit_claim_citations.py",
        "validate_competitor_matrix.py",
        "check_unit_consistency.py",
        "check_report_standard.py",
        "critique_report.py",
    }
    if args.strict:
        hard.add("verify_claim_support.py")

    failures: list[str] = []
    for check in checks:
        check["valid"] = bool(
            check["payload"].get("valid", check["returncode"] == 0)
        )
        check["summary"] = summarize(check)
        if check["name"] in hard and not check["valid"]:
            failures.append(check["name"])

    result = {
        "valid": not failures,
        "strict": args.strict,
        "report_dir": str(root),
        "length_mode": args.length,
        "checks": [
            {
                "name": check["name"],
                "valid": check["valid"],
                "summary": check["summary"],
                "returncode": check["returncode"],
            }
            for check in checks
        ],
        "failures": failures,
        "summary": {
            "total": len(checks),
            "passed": sum(1 for check in checks if check["valid"]),
            "failed": sum(1 for check in checks if not check["valid"]),
        },
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
