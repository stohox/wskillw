#!/usr/bin/env python3
"""Generate a bounded local evidence-first report scaffold for a research profile."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

from _common import (
    ValidationError,
    error_exit,
    parse_iso_date,
    parse_year,
    read_json,
    require_identifier,
    require_object,
    require_text,
    write_json_report,
)
from render_output import render_report

SKILL_ROOT = Path(__file__).resolve().parents[1]
PROFILES_DIR = SKILL_ROOT / "profiles"
BASE_SCHEMA = SKILL_ROOT / "core" / "schemas" / "base_ledgers.json"
STANDARDS = SKILL_ROOT / "core" / "standards.json"

PERIOD_RE = re.compile(r"^\d{4}-\d{4}$")
CLASSIFICATION_ENUM = {"public", "internal", "confidential"}
PLACEHOLDER_RE = re.compile(r"\{\{\s*([^}]+?)\s*\}\}")


def _period(value: Any, context: str) -> str:
    text = require_text(value, context, maximum=9)
    if not PERIOD_RE.fullmatch(text):
        raise ValidationError(f"{context} must be YYYY-YYYY")
    start, end = (int(part) for part in text.split("-"))
    if start > end:
        raise ValidationError(f"{context} start year must not exceed end year")
    parse_year(start, context)
    parse_year(end, context)
    return text


def _load_profile(profile_id: str | None, profile_file: str | None) -> tuple[dict, Path]:
    if profile_file:
        path = Path(profile_file).expanduser()
        if not path.is_file():
            raise ValidationError(f"profile file not found: {path}")
        return require_object(read_json(path), "profile"), path.parent
    pid = profile_id or "market"
    profile_dir = PROFILES_DIR / pid
    profile_path = profile_dir / "profile.json"
    if not profile_path.is_file():
        raise ValidationError(f"unknown profile '{pid}' (missing {profile_path})")
    return require_object(read_json(profile_path), "profile"), profile_dir


def _base_schemas() -> dict:
    if not BASE_SCHEMA.is_file():
        return {}
    return require_object(read_json(BASE_SCHEMA), "base schema")


def _load_standards(mode: str) -> dict:
    if not STANDARDS.is_file():
        raise ValidationError(f"standards file not found: {STANDARDS}")
    data = require_object(read_json(STANDARDS), "standards")
    modes = require_object(data.get("modes", {}), "standards.modes")
    if mode not in modes:
        raise ValidationError(f"unknown length mode: {mode}")
    return dict(require_object(modes[mode], f"standards.modes.{mode}"))


def _derived(manifest: dict) -> dict:
    values: dict[str, Any] = {}
    hist = manifest.get("historical_period")
    fc = manifest.get("forecast_period")
    try:
        if hist:
            values["historical_end"] = int(str(hist).split("-")[1])
        if hist and fc:
            values["forecast_horizon"] = int(str(fc).split("-")[1]) - int(
                str(hist).split("-")[1]
            )
    except (ValueError, IndexError):
        pass
    return values


def _lookup(key: str, manifest: dict, derived: dict) -> Any:
    if key.startswith("manifest."):
        return manifest.get(key[len("manifest.") :])
    if key.startswith("derived."):
        return derived.get(key[len("derived.") :])
    return manifest.get(key)


def _substitute(text: str, manifest: dict, derived: dict) -> str:
    def repl(match: re.Match) -> str:
        key = match.group(1).strip()
        if key.endswith("_block"):
            value = manifest.get(key[: -len("_block")])
            if isinstance(value, list):
                return "\n".join(f"- {item}" for item in value)
            return "" if value is None else str(value)
        value = _lookup(key, manifest, derived)
        if isinstance(value, list):
            return "; ".join(str(item) for item in value)
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        return "" if value is None else str(value)

    return PLACEHOLDER_RE.sub(repl, text)


def _bind(value: Any, manifest: dict, derived: dict) -> Any:
    if isinstance(value, str):
        match = PLACEHOLDER_RE.fullmatch(value.strip())
        if match:
            resolved = _lookup(match.group(1).strip(), manifest, derived)
            return "" if resolved is None else resolved
        return _substitute(value, manifest, derived)
    if isinstance(value, list):
        return [_bind(item, manifest, derived) for item in value]
    if isinstance(value, dict):
        return {key: _bind(item, manifest, derived) for key, item in value.items()}
    return value


def _validate_manifest(payload: dict, profile: dict) -> dict:
    spec = require_object(profile.get("manifest", {}), "profile.manifest")
    required = spec.get("required", [])
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValidationError("manifest is missing: " + ", ".join(missing))
    out = dict(payload)
    out["report_id"] = require_identifier(payload.get("report_id"), "report_id")
    for key in ("title", "subtitle", "prepared_for", "prepared_by"):
        if key in payload:
            out[key] = require_text(payload[key], key, maximum=300)
    classification = require_text(
        payload.get("classification"), "classification", maximum=20
    )
    if classification not in CLASSIFICATION_ENUM:
        raise ValidationError("classification must be public, internal, or confidential")
    out["classification"] = classification
    out["retrieval_cutoff"] = parse_iso_date(
        payload.get("retrieval_cutoff"), "retrieval_cutoff"
    )
    for period_field in spec.get("period_fields", []):
        if period_field in payload:
            out[period_field] = _period(payload[period_field], period_field)
    if spec.get("forecast_after_history"):
        hist = out.get("historical_period")
        fc = out.get("forecast_period")
        if hist and fc:
            hist_end = int(hist.split("-")[1])
            fc_start, fc_end = (int(year) for year in fc.split("-"))
            if fc_start != hist_end + 1:
                raise ValidationError(
                    "forecast_period must begin the year after historical_period ends"
                )
            horizon_cap = int(spec.get("max_forecast_horizon", 50))
            if fc_end - hist_end > horizon_cap:
                raise ValidationError(
                    f"forecast horizon must not exceed {horizon_cap} years"
                )
    return out


def _field_list(spec: dict, base: dict) -> tuple[str, ...]:
    if "fields" in spec:
        return tuple(spec["fields"])
    fields: list[str] = list(base.get(spec.get("base", ""), []))
    for extra in spec.get("extra", []):
        if extra not in fields:
            fields.append(extra)
    return tuple(fields)


def _resolve_template(raw: str, profile_dir: Path) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate
    local = profile_dir / raw
    if local.is_file():
        return local
    root = SKILL_ROOT / raw
    if root.is_file():
        return root
    raise ValidationError(f"template not found: {raw}")


def _safe_new_directory(raw_path: str | Path) -> Path:
    path = Path(raw_path).expanduser()
    if path.exists() or path.is_symlink():
        raise ValidationError(f"output directory already exists: {path}")
    try:
        parent = path.parent.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ValidationError(f"output parent does not exist: {path.parent}") from exc
    if not parent.is_dir():
        raise ValidationError(f"output parent is not a directory: {parent}")
    if path.name in {"", ".", ".."}:
        raise ValidationError("output directory name is invalid")
    return parent / path.name


def _detect_language(manifest: dict, explicit: str | None) -> str:
    if explicit in {"zh", "en"}:
        return explicit
    value = str(manifest.get("language", "")).strip().lower()
    if value in {"zh", "en"}:
        return value
    text = " ".join(
        str(manifest.get(key, ""))
        for key in (
            "title",
            "subtitle",
            "scope_definition",
            "market_definition",
            "research_question",
            "corpus_summary",
        )
    )
    return "zh" if re.search(r"[\u4e00-\u9fff]", text) else "en"


def generate(
    profile: dict,
    profile_dir: Path,
    manifest: dict,
    output_dir: str | Path,
    fmt: str = "markdown",
    language: str | None = None,
    pdf_engine: str = "auto",
    length_mode: str = "standard",
) -> dict:
    base = _base_schemas()
    derived = _derived(manifest)
    lang = _detect_language(manifest, language)
    destination = _safe_new_directory(output_dir)
    destination.mkdir(mode=0o755)
    (destination / "data").mkdir()
    (destination / "analysis").mkdir()
    (destination / "sources").mkdir()

    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    minimums = _load_standards(length_mode)
    contract = {
        "schema_version": "1.0",
        "profile": profile.get("profile_id", ""),
        "length_mode": length_mode,
        "label": minimums.get("label", ""),
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
        "language": lang,
        "created_at": manifest.get("retrieval_cutoff", ""),
        "check_command": (
            f"python3 scripts/check_report_standard.py report.md --length {length_mode}"
        ),
    }
    (destination / "report_contract.json").write_text(
        json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    run_manifest = {
        "schema_version": "1.0",
        "run_id": (
            f"{manifest.get('report_id', 'report')}-"
            f"{manifest.get('retrieval_cutoff', '')}"
        ),
        "created_at": manifest.get("retrieval_cutoff", ""),
        "query": manifest.get("title", ""),
        "profile": profile.get("profile_id", ""),
        "length_mode": length_mode,
        "format": fmt,
        "language": lang,
        "pdf_engine": pdf_engine,
        "manifest": "manifest.json",
        "contract": "report_contract.json",
        "assumptions": [],
        "agent": "WorkBuddy research-reports",
        "skill_version": "2.1-evidence",
    }
    (destination / "run_manifest.json").write_text(
        json.dumps(run_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    template = profile.get("report_template")
    if isinstance(template, dict):
        template = template.get(lang) or template.get("en")
    if template:
        source = _resolve_template(template, profile_dir)
        text = _substitute(source.read_text(encoding="utf-8"), manifest, derived)
        (destination / "report.md").write_text(text, encoding="utf-8")

    for filename, spec in require_object(
        profile.get("data_files", {}), "data_files"
    ).items():
        fields = _field_list(require_object(spec, f"data_files.{filename}"), base)
        with (destination / "data" / filename).open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            csv.writer(handle, lineterminator="\n").writerow(fields)

    for filename, template in require_object(
        profile.get("analysis_files", {}), "analysis_files"
    ).items():
        source = _resolve_template(template, profile_dir)
        payload = _bind(json.loads(source.read_text(encoding="utf-8")), manifest, derived)
        (destination / "analysis" / filename).write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    checklist = profile.get("review_checklist", [])
    if lang == "zh" and profile.get("review_checklist_zh"):
        checklist = profile["review_checklist_zh"]
    lines = ["# 审校清单" if lang == "zh" else "# Review checklist", ""]
    if checklist:
        lines.extend(f"- [ ] {item}" for item in checklist)
        lines.append("")
    lines.append("## 交付下限 / Deliverable standard")
    lines.append("")
    lines.append(
        f"- [ ] 页数 ≥ {minimums['min_pages']} / pages ≥ {minimums['min_pages']}"
    )
    lines.append(
        f"- [ ] 章节 ≥ {minimums['min_chapters']} / chapters ≥ {minimums['min_chapters']}"
    )
    lines.append(
        f"- [ ] 图表 ≥ {minimums['min_figures']} / figures ≥ {minimums['min_figures']}"
    )
    lines.append(
        f"- [ ] 表格 ≥ {minimums['min_tables']} / tables ≥ {minimums['min_tables']}"
    )
    lines.append(
        f"- [ ] 中文字数 ≥ {minimums['min_chars_zh']} / English words ≥ {minimums['min_words_en']}"
    )
    lines.append(f"- [ ] 运行检查 / run: `{contract['check_command']}`")
    lines.append("")
    (destination / "review_checklist.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    if fmt and fmt != "markdown":
        render_result = render_report(
            destination / "report.md",
            destination,
            fmt,
            title_fallback=str(manifest.get("title", "Report")),
            pdf_engine=pdf_engine,
        )
    else:
        render_result = {"format": "markdown", "rendered": []}

    page_count = None
    pdf_path = destination / "report.pdf"
    if pdf_path.is_file():
        blob = pdf_path.read_bytes()
        page_count = blob.count(b"/Type /Page") - blob.count(b"/Type /Pages")

    created = sorted(
        str(path.relative_to(destination))
        for path in destination.rglob("*")
        if path.is_file()
    )
    return {
        "created": True,
        "profile": profile.get("profile_id", ""),
        "output_directory": str(destination),
        "format": fmt,
        "language": lang,
        "length": length_mode,
        "contract": contract,
        "run_manifest": run_manifest,
        "page_count": page_count,
        "files": created,
        "validators": profile.get("validators", []),
        "render": render_result,
        "next_step": (
            "Populate the empty ledgers, then run the profile validators and "
            "check_report_standard.py before drafting conclusions."
        ),
    }


def _list_profiles() -> list[dict]:
    rows: list[dict] = []
    if PROFILES_DIR.is_dir():
        for entry in sorted(PROFILES_DIR.iterdir()):
            profile_path = entry / "profile.json"
            if profile_path.is_file():
                data = read_json(profile_path)
                rows.append(
                    {
                        "profile": entry.name,
                        "display_name": data.get("display_name", ""),
                        "description": data.get("description", ""),
                    }
                )
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a new local evidence-first report scaffold for a research "
            "profile. Existing directories are never overwritten."
        )
    )
    parser.add_argument("manifest", nargs="?", help="Local .json report manifest")
    parser.add_argument("output_dir", nargs="?", help="New local output directory")
    parser.add_argument(
        "--profile", default="market", help="Profile id under profiles/ (default: market)"
    )
    parser.add_argument("--profile-file", help="Path to an explicit profile.json")
    parser.add_argument(
        "--format",
        default="markdown",
        choices=["markdown", "html", "latex", "pdf"],
        help=(
            "Render target: markdown (default), html (self-contained), "
            "latex (report.tex), or pdf (report.tex, compiled when a LaTeX engine exists)"
        ),
    )
    parser.add_argument(
        "--language",
        choices=["zh", "en"],
        help="Report template language (default: auto-detect from manifest)",
    )
    parser.add_argument(
        "--pdf-engine",
        default="auto",
        choices=["auto", "skill", "browser", "latex"],
        help=(
            "PDF route: auto (usable host PDF skill, then headless Chrome/Edge, "
            "then LaTeX), skill (delegate to a detected host PDF skill), "
            "browser (Chrome/Edge HTML print), or latex (xelatex/lualatex/pdflatex)"
        ),
    )
    parser.add_argument(
        "--length",
        default="standard",
        choices=["brief", "standard", "deep"],
        help=(
            "Minimum deliverable standard: brief (8 pages), standard (20), "
            "deep (45). Writes report_contract.json and checklist floors."
        ),
    )
    parser.add_argument(
        "--list-profiles", action="store_true", help="List available profiles"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.list_profiles:
            write_json_report({"profiles": _list_profiles()}, None)
            return 0
        if not args.manifest or not args.output_dir:
            raise ValidationError(
                "manifest and output_dir are required unless --list-profiles is used"
            )
        profile, profile_dir = _load_profile(args.profile, args.profile_file)
        manifest = _validate_manifest(
            require_object(read_json(args.manifest), "root"), profile
        )
        write_json_report(
            generate(
                profile,
                profile_dir,
                manifest,
                args.output_dir,
                args.format,
                args.language,
                args.pdf_engine,
                args.length,
            ),
            None,
        )
        return 0
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
