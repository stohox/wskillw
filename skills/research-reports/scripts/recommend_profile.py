#!/usr/bin/env python3
"""Recommend a research profile, output format, and manifest draft from intake answers."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
PROFILES_DIR = SKILL_ROOT / "profiles"
VALID_FORMATS = {"markdown", "html", "latex", "pdf"}

KEYWORDS = {
    "market": [
        "市场", "规模", "竞争", "增长", "份额", "定价", "营收", "用户量",
        "market", "sizing", "competitor", "cagr", "pricing", "revenue", "share",
    ],
    "technical": [
        "技术", "选型", "架构", "基准", "性能", "延迟", "吞吐", "数据库", "框架",
        "对比", "技术栈", "迁移", "benchmark", "latency", "throughput", "database",
        "framework", "architecture", "api", "gpu", "cuda",
    ],
    "humanities": [
        "文学", "诗", "文本", "作者", "版本", "阐释", "语料", "翻译", "修辞",
        "思想", "哲学", "小说", "戏剧", "历史", "corpus", "poetry", "literary",
        "novel", "author", "interpretation", "translation", "rhetoric",
    ],
}


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug or "research-report")[:60]


def _score(text: str, profile: str) -> int:
    lowered = text.lower()
    return sum(1 for keyword in KEYWORDS[profile] if keyword.lower() in lowered)


def _pick_profile(intake: dict) -> str:
    direction = str(intake.get("direction", "auto")).strip().lower()
    if direction in KEYWORDS:
        return direction
    text = " ".join(
        str(intake.get(key, ""))
        for key in ("decision", "scope_notes", "report_title", "audience")
    )
    scores = {profile: _score(text, profile) for profile in KEYWORDS}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "market"


def _manifest_draft(intake: dict, profile_id: str, profile: dict) -> dict:
    today = dt.date.today().isoformat()
    title = str(intake.get("report_title") or intake.get("decision") or "Research Report")
    decision = str(intake.get("decision", ""))
    draft: dict = {
        "schema_version": "1.0",
        "report_id": _slug(title),
        "title": title,
        "subtitle": str(intake.get("subtitle", "")) or "Evidence-first research report",
        "prepared_for": str(intake.get("audience", "")),
        "prepared_by": str(intake.get("prepared_by", "")) or "Research Team",
        "classification": str(intake.get("classification", "internal")),
        "retrieval_cutoff": today,
    }
    if profile_id == "market":
        draft.update(
            {
                "market_definition": decision,
                "inclusions": [],
                "exclusions": [],
                "geography": str(intake.get("geography", "")),
                "currency": str(intake.get("currency", "")),
                "base_year": dt.date.today().year,
                "price_basis": "nominal",
                "taxonomy": str(intake.get("taxonomy", "")),
                "taxonomy_version": str(intake.get("taxonomy_version", "")),
                "historical_period": str(intake.get("historical_period", "")),
                "forecast_period": str(intake.get("forecast_period", "")),
            }
        )
    elif profile_id == "technical":
        draft.update(
            {
                "scope_definition": decision,
                "systems_in_scope": [],
                "evaluation_criteria": [],
                "version_policy": "Pin to the latest stable release; record commit or image digest",
                "verified_date": today,
            }
        )
    elif profile_id == "humanities":
        draft.update(
            {
                "research_question": decision,
                "scope_definition": str(intake.get("scope_notes", "")),
                "corpus_summary": "",
                "methodology": "",
                "citation_style": str(intake.get("citation_style", "Chicago")),
                "corpus_period": str(intake.get("corpus_period", "")),
            }
        )
    return draft


def _missing(draft: dict, required: list[str]) -> list[str]:
    missing: list[str] = []
    for key in required:
        value = draft.get(key, "")
        if value is None or value == "" or value == []:
            missing.append(key)
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recommend a profile and output format from intake answers."
    )
    parser.add_argument("intake_path", nargs="?", help="Path to intake.json")
    parser.add_argument("--intake", dest="intake_opt", help="Path to intake.json")
    parser.add_argument("--write-manifest", help="Write the manifest draft to this path")
    args = parser.parse_args()

    intake_path = args.intake_opt or args.intake_path
    if not intake_path:
        parser.error("an intake.json path is required (positional or --intake)")
    intake = json.loads(Path(intake_path).read_text(encoding="utf-8"))
    profile_id = _pick_profile(intake)
    profile_path = PROFILES_DIR / profile_id / "profile.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    fmt = str(intake.get("deliverable", "html")).strip().lower()
    if fmt not in VALID_FORMATS:
        fmt = "html"
    draft = _manifest_draft(intake, profile_id, profile)
    missing = _missing(draft, profile.get("manifest", {}).get("required", []))
    language = str(intake.get("language", "zh")).strip().lower()
    if language not in {"zh", "en"}:
        language = "zh"
    length = str(intake.get("length", "standard")).strip().lower()
    if length not in {"brief", "standard", "deep"}:
        length = "standard"

    result = {
        "recommended_profile": profile_id,
        "display_name": profile.get("display_name", ""),
        "format": fmt,
        "language": language,
        "length": length,
        "manifest_draft": draft,
        "missing_fields": missing,
        "next_command": (
            f"python3 scripts/generate_report_scaffold.py --profile {profile_id} "
            f"--format {fmt} --language {language} --length {length} "
            f"manifest.json ./out-{profile_id}"
        ),
    }
    if args.write_manifest:
        Path(args.write_manifest).write_text(
            json.dumps(draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        result["manifest_written"] = args.write_manifest
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
