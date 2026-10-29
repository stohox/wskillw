#!/usr/bin/env python3
"""Check a drafted report against the minimum deliverable standard."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
STANDARDS = SKILL_ROOT / "core" / "standards.json"
PROFILES = SKILL_ROOT / "profiles"

TABLE_SEP = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")
CJK = re.compile(r"[\u4e00-\u9fff]")
EN_WORD = re.compile(r"[A-Za-z][A-Za-z'-]+")


def load_standards(mode: str, profile_id: str | None) -> tuple[dict, dict]:
    data = json.loads(STANDARDS.read_text(encoding="utf-8"))
    modes = data["modes"]
    if mode not in modes:
        raise SystemExit(f"unknown length mode: {mode}")
    minimums = dict(modes[mode])
    profile_note = None
    if profile_id:
        profile_path = PROFILES / profile_id / "profile.json"
        if profile_path.is_file():
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            override = (profile.get("minimums") or {}).get(mode)
            if override:
                minimums.update(override)
                profile_note = f"profile override applied: {profile_id}"
    return minimums, {"profile_note": profile_note, "modes": modes}


def count_metrics(text: str, pdf: Path | None, chars_per_page: int) -> dict:
    lines = text.splitlines()
    chapters = sum(1 for line in lines if re.match(r"^##\s+\S", line))
    figures = len(re.findall(r"^!\[[^\]]*\]\([^)]+\)\s*$", text, flags=re.MULTILINE))
    tables = 0
    for index, line in enumerate(lines):
        if (
            index > 0
            and lines[index - 1].strip().startswith("|")
            and TABLE_SEP.match(line)
            and "-" in line
        ):
            tables += 1
    chars_zh = len(CJK.findall(text))
    words_en = len(EN_WORD.findall(text))

    if pdf is not None and pdf.is_file():
        blob = pdf.read_bytes()
        pages = blob.count(b"/Type /Page") - blob.count(b"/Type /Pages")
        page_source = "pdf"
    else:
        text_pages = max(chars_zh / chars_per_page, words_en / 350)
        pages = math.ceil(text_pages + figures * 0.7 + tables * 0.5)
        page_source = "estimated"

    return {
        "pages": pages,
        "page_source": page_source,
        "chapters": chapters,
        "figures": figures,
        "tables": tables,
        "chars_zh": chars_zh,
        "words_en": words_en,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a report.md against the minimum deliverable standard."
    )
    parser.add_argument("report", help="Path to report.md")
    parser.add_argument(
        "--length", default="standard", choices=["brief", "standard", "deep"]
    )
    parser.add_argument("--language", choices=["zh", "en"])
    parser.add_argument("--pdf", help="Optional rendered PDF for exact page count")
    parser.add_argument("--profile", help="Optional profile id for minimum overrides")
    args = parser.parse_args()

    report = Path(args.report)
    if not report.is_file():
        raise SystemExit(f"report not found: {report}")
    text = report.read_text(encoding="utf-8")
    minimums, meta = load_standards(args.length, args.profile)

    pdf = Path(args.pdf) if args.pdf else report.with_name("report.pdf")
    metrics = count_metrics(text, pdf, int(minimums.get("chars_per_page", 600)))
    language = args.language or ("zh" if metrics["chars_zh"] > 0 else "en")

    checks = []
    deficits = {}

    def check(name: str, actual: int, minimum: int) -> None:
        ok = actual >= minimum
        checks.append({"metric": name, "actual": actual, "minimum": minimum, "ok": ok})
        if not ok:
            deficits[name] = minimum - actual

    check("pages", metrics["pages"], int(minimums["min_pages"]))
    check("chapters", metrics["chapters"], int(minimums["min_chapters"]))
    check("figures", metrics["figures"], int(minimums["min_figures"]))
    check("tables", metrics["tables"], int(minimums["min_tables"]))
    if language == "zh":
        check("chars_zh", metrics["chars_zh"], int(minimums["min_chars_zh"]))
    else:
        check("words_en", metrics["words_en"], int(minimums["min_words_en"]))

    result = {
        "valid": all(item["ok"] for item in checks),
        "mode": args.length,
        "label": minimums.get("label", ""),
        "language": language,
        "metrics": metrics,
        "minimums": {
            key: minimums[key]
            for key in (
                "min_pages",
                "min_chapters",
                "min_figures",
                "min_tables",
                "min_chars_zh",
                "min_words_en",
            )
        },
        "checks": checks,
        "deficits": deficits,
        "notes": [
            "Page count uses the rendered PDF when present; otherwise it is estimated.",
            "Figures are Markdown image references; tables are pipe tables.",
            "Chapters are level-2 headings (##).",
            meta["profile_note"],
        ],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
