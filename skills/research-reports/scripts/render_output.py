#!/usr/bin/env python3
"""Render a report.md scaffold to self-contained HTML or standalone LaTeX."""

from __future__ import annotations

import html
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
LABEL_RE = re.compile(r"^(?:\*\*[^*]{1,60}\*\*:|[A-Z][A-Za-z0-9 /&()\-]{1,40}:)")
LATEX_ESCAPE = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def _has_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text))


def _html_inline(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)
    return escaped


def _html_body(markdown: str) -> tuple[str, list[tuple[str, str]]]:
    lines = markdown.splitlines()
    out: list[str] = []
    toc: list[tuple[str, str]] = []
    paragraph: list[str] = []
    index = 0

    def flush() -> None:
        if paragraph:
            out.append("<p>" + _html_inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            flush()
            index += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            flush()
            level = len(heading.group(1))
            text = heading.group(2).strip()
            if level == 1:
                out.append(f"<h1>{_html_inline(text)}</h1>")
            else:
                anchor = f"sec-{len(toc) + 1}"
                out.append(
                    f'<h{level} id="{anchor}">{_html_inline(text)}</h{level}>'
                )
                if level == 2:
                    toc.append((anchor, text))
            index += 1
            continue
        image = re.match(r"^!\[(.*?)\]\((.*?)\)$", line.strip())
        if image:
            flush()
            alt = image.group(1).strip()
            src = image.group(2).strip()
            out.append(
                f'<figure><img src="{html.escape(src, quote=True)}" '
                f'alt="{html.escape(alt, quote=True)}">'
                f"<figcaption>{_html_inline(alt)}</figcaption></figure>"
            )
            index += 1
            continue
        if (
            line.strip().startswith("|")
            and index + 1 < len(lines)
            and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[index + 1])
            and "-" in lines[index + 1]
        ):
            flush()
            header = [cell.strip() for cell in line.strip().strip("|").split("|")]
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(
                    [
                        cell.strip()
                        for cell in lines[index].strip().strip("|").split("|")
                    ]
                )
                index += 1
            head = "".join(f"<th>{_html_inline(cell)}</th>" for cell in header)
            body = "".join(
                "<tr>"
                + "".join(f"<td>{_html_inline(cell)}</td>" for cell in row)
                + "</tr>"
                for row in rows
            )
            out.append(
                f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"
            )
            continue
        if line.startswith("> "):
            flush()
            quoted: list[str] = []
            while index < len(lines) and lines[index].startswith("> "):
                quoted.append(lines[index][2:].strip())
                index += 1
            out.append(
                "<blockquote><p>" + _html_inline(" ".join(quoted)) + "</p></blockquote>"
            )
            continue
        if line.startswith("- "):
            flush()
            items: list[str] = []
            while index < len(lines) and lines[index].startswith("- "):
                items.append(lines[index][2:].strip())
                index += 1
            body = "".join(f"<li>{_html_inline(item)}</li>" for item in items)
            out.append(f"<ul>{body}</ul>")
            continue
        if LABEL_RE.match(line.strip()):
            flush()
            out.append("<p>" + _html_inline(line.strip()) + "</p>")
            index += 1
            continue
        paragraph.append(line.strip())
        index += 1
    flush()
    return "\n".join(out), toc

def markdown_to_html(markdown: str, title: str) -> str:
    body, toc = _html_body(markdown)
    lang = "zh" if _has_cjk(markdown) else "en"
    toc_label = "目录" if lang == "zh" else "Contents"
    nav = ""
    if toc:
        links = "".join(
            f'<li><a href="#{anchor}">{html.escape(text)}</a></li>'
            for anchor, text in toc
        )
        nav = f'<nav class="toc"><h2>{toc_label}</h2><ul>{links}</ul></nav>'
    if nav:
        notice_end = body.find("</blockquote>")
        if notice_end != -1:
            body = body[: notice_end + 13] + "\n" + nav + body[notice_end + 13 :]
        else:
            heading_end = body.find("</h1>")
            if heading_end != -1:
                body = body[: heading_end + 5] + "\n" + nav + body[heading_end + 5 :]
            else:
                body = nav + body
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
  :root {{ --ink:#1f2328; --muted:#5b6570; --line:#d8dee4; --accent:#0c447c; --bg:#ffffff; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif;
    font-size:16px; line-height:1.65; }}
  main {{ max-width:860px; margin:0 auto; padding:56px 32px 96px; }}
  h1 {{ font-size:2rem; line-height:1.25; color:var(--accent); margin:0 0 1.2rem; font-weight:600; }}
  h2 {{ font-size:1.4rem; margin:2.4rem 0 .8rem; padding-bottom:.35rem;
    border-bottom:1px solid var(--line); color:var(--accent); font-weight:600; }}
  h3 {{ font-size:1.12rem; margin:1.6rem 0 .5rem; font-weight:600; }}
  p {{ margin:.7rem 0; }}
  ul {{ margin:.6rem 0 .9rem; padding-left:1.4rem; }}
  li {{ margin:.25rem 0; }}
  blockquote {{ margin:1.1rem 0; padding:.7rem 1rem; border-left:3px solid var(--accent);
    background:#f5f8fb; color:var(--muted); }}
  blockquote p {{ margin:0; }}
  code {{ background:#f1f3f5; padding:.1rem .3rem; border-radius:4px; font-size:.9em; }}
  table {{ width:100%; border-collapse:collapse; margin:1.1rem 0; font-size:.94em; }}
  th, td {{ border:1px solid var(--line); padding:.45rem .6rem; text-align:left; vertical-align:top; }}
  th {{ background:#f5f8fb; font-weight:600; }}
  tbody tr:nth-child(even) td {{ background:#fafbfc; }}
  figure {{ margin:1.4rem 0; text-align:center; }}
  figure img {{ max-width:100%; height:auto; border:1px solid var(--line); border-radius:8px; background:#fff; }}
  figcaption {{ margin-top:.5rem; font-size:.85em; color:var(--muted); }}
  .toc {{ margin:1.5rem 0 2.5rem; padding:1rem 1.25rem; border:1px solid var(--line);
    border-radius:10px; background:#fafbfc; }}
  .toc h2 {{ font-size:1rem; margin:0 0 .5rem; border:0; padding:0; }}
  .toc ul {{ margin:0; padding-left:0; list-style:none; }}
  .toc li {{ margin:.2rem 0; }}
  .toc a {{ color:var(--accent); text-decoration:none; }}
  .toc a:hover {{ text-decoration:underline; }}
  @media print {{ body {{ font-size:11pt; }} main {{ max-width:none; padding:0; }}
    .toc {{ break-after:page; }} h2 {{ break-after:avoid; }} }}
</style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""


def _tex_escape(text: str) -> str:
    return "".join(LATEX_ESCAPE.get(char, char) for char in text)


def _tex_inline(text: str) -> str:
    escaped = _tex_escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", escaped)
    escaped = re.sub(r"`(.+?)`", r"\\texttt{\1}", escaped)
    return escaped


def _tex_body(markdown: str) -> tuple[str, str]:
    lines = markdown.splitlines()
    title = ""
    out: list[str] = []
    paragraph: list[str] = []
    index = 0

    def flush() -> None:
        if paragraph:
            out.append(_tex_inline(" ".join(paragraph)) + "\n")
            paragraph.clear()

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            flush()
            index += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            flush()
            level = len(heading.group(1))
            text = heading.group(2).strip()
            if level == 1 and not title:
                title = text
            elif level == 2:
                out.append(f"\\section{{{_tex_inline(text)}}}")
            elif level == 3:
                out.append(f"\\subsection{{{_tex_inline(text)}}}")
            else:
                out.append(f"\\subsubsection{{{_tex_inline(text)}}}")
            index += 1
            continue
        image = re.match(r"^!\[(.*?)\]\((.*?)\)$", line.strip())
        if image:
            flush()
            alt = image.group(1).strip()
            src = image.group(2).strip()
            out.append(
                "\\begin{figure}[htbp]\n\\centering\n"
                f"\\includegraphics[width=0.9\\textwidth]{{{src}}}\n"
                f"\\caption{{{_tex_inline(alt)}}}\n\\end{{figure}}"
            )
            index += 1
            continue
        if (
            line.strip().startswith("|")
            and index + 1 < len(lines)
            and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[index + 1])
            and "-" in lines[index + 1]
        ):
            flush()
            header = [cell.strip() for cell in line.strip().strip("|").split("|")]
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(
                    [
                        cell.strip()
                        for cell in lines[index].strip().strip("|").split("|")
                    ]
                )
                index += 1
            spec = "l" * len(header)
            out.append(r"\begin{table}[htbp]")
            out.append(r"\centering")
            out.append(r"\begin{tabular}{@{}" + spec + r"@{}}")
            out.append(r"\toprule")
            out.append(" & ".join(_tex_inline(cell) for cell in header) + r" \\")
            out.append(r"\midrule")
            for row in rows:
                out.append(" & ".join(_tex_inline(cell) for cell in row) + r" \\")
            out.append(r"\bottomrule")
            out.append(r"\end{tabular}")
            out.append(r"\end{table}")
            continue
        if line.startswith("> "):
            flush()
            quoted: list[str] = []
            while index < len(lines) and lines[index].startswith("> "):
                quoted.append(lines[index][2:].strip())
                index += 1
            out.append(
                "\\begin{quote}\n" + _tex_inline(" ".join(quoted)) + "\n\\end{quote}"
            )
            continue
        if line.startswith("- "):
            flush()
            items: list[str] = []
            while index < len(lines) and lines[index].startswith("- "):
                items.append(lines[index][2:].strip())
                index += 1
            body = "\n".join(f"  \\item {_tex_inline(item)}" for item in items)
            out.append("\\begin{itemize}\n" + body + "\n\\end{itemize}")
            continue
        if LABEL_RE.match(line.strip()):
            flush()
            out.append(_tex_inline(line.strip()) + "\n")
            index += 1
            continue
        paragraph.append(line.strip())
        index += 1
    flush()
    return title, "\n\n".join(out)


def markdown_to_latex(markdown: str, fallback_title: str) -> str:
    title, body = _tex_body(markdown)
    title = title or fallback_title
    chinese = _has_cjk(markdown)
    preamble = [
        r"\documentclass[11pt]{article}",
        r"\usepackage[margin=1in]{geometry}",
        r"\usepackage{parskip}",
        r"\usepackage{enumitem}",
        r"\usepackage{xcolor}",
        r"\usepackage{hyperref}",
        r"\usepackage{booktabs}",
        r"\usepackage{graphicx}",
    ]
    if chinese:
        preamble.append(r"\usepackage[UTF8]{ctex}")
    preamble.extend(
        [
            r"\definecolor{mrnavy}{RGB}{0,68,100}",
            r"\hypersetup{colorlinks=true,linkcolor=mrnavy,urlcolor=mrnavy}",
            rf"\title{{{_tex_inline(title)}}}",
            r"\author{}",
            r"\date{}",
            r"\begin{document}",
            r"\maketitle",
        ]
    )
    tail = [r"\end{document}", ""]
    return "\n".join(preamble) + "\n\n" + body + "\n\n" + "\n".join(tail)


def _skill_roots() -> list[Path]:
    home = Path.home()
    return [
        home / ".qoder-cn" / "skills",
        home / ".workbuddy" / "skills",
        home / ".claude" / "skills",
        home / ".agents" / "skills",
    ]


def _frontmatter_meta(skill_md: Path) -> dict:
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    meta: dict[str, str] = {}
    for line in text.splitlines()[:60]:
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta


def _detect_pdf_skills() -> list[dict]:
    found: list[dict] = []
    for root in _skill_roots():
        if not root.is_dir():
            continue
        for skill_md in root.glob("*/SKILL.md"):
            meta = _frontmatter_meta(skill_md)
            name = meta.get("name") or skill_md.parent.name
            description = " ".join(
                filter(
                    None,
                    [meta.get("description", ""), meta.get("description_zh", "")],
                )
            ).lower()
            corpus = f"{name} {description}".lower()
            if "pdf" not in corpus or "do not use for pdf" in description:
                continue
            creation = any(
                keyword in description
                for keyword in ("create", "creating new pdf", "生成", "produce", "创建")
            )
            readonly = any(
                keyword in description
                for keyword in (
                    "reading only",
                    "read-only",
                    "not supported",
                    "cannot create",
                    "仅支持读取",
                    "不支持创建",
                )
            )
            if readonly:
                creation = False
            conversion = any(
                keyword in description
                for keyword in ("html", "markdown", "md 转", "convert", "render", "转换")
            )
            deps: dict[str, bool] = {}
            if name.lower() == "pdf":
                deps["reportlab"] = importlib.util.find_spec("reportlab") is not None
            deps_ok = all(deps.values()) if deps else True
            found.append(
                {
                    "name": name,
                    "path": str(skill_md.parent),
                    "creation_capable": creation,
                    "conversion_capable": creation and conversion,
                    "deps": deps,
                    "deps_ok": deps_ok,
                }
            )
    return found


def _delegate_pdf(
    html_path: Path, out_dir: Path, candidates: list[dict]
) -> dict:
    payload = {
        "delegated": True,
        "html": str(html_path),
        "markdown": str(out_dir / "report.md"),
        "pdf_target": str(out_dir / "report.pdf"),
        "detected_skills": candidates,
        "instructions": (
            "Use a detected PDF-capable host skill to convert the HTML or Markdown "
            "into pdf_target. If no skill is usable, rerun with "
            "--pdf-engine browser (headless Chrome/Edge)."
        ),
    }
    (out_dir / "pdf_delegation.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return payload


def _browser_candidates() -> list[Path]:
    candidates: list[Path] = []
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge", "chrome"):
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))
    if os.name == "nt":
        bases = [
            os.environ.get("PROGRAMFILES", ""),
            os.environ.get("PROGRAMFILES(X86)", ""),
            os.environ.get("LOCALAPPDATA", ""),
        ]
        for base in bases:
            if not base:
                continue
            candidates.append(Path(base) / "Google/Chrome/Application/chrome.exe")
            candidates.append(Path(base) / "Microsoft/Edge/Application/msedge.exe")
        candidates.extend(
            [
                Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
                Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
                Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
                Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
            ]
        )
    elif sys.platform == "darwin":
        candidates.extend(
            [
                Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
                Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
                Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
            ]
        )
    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            resolved = candidate
        key = str(resolved)
        if resolved.is_file() and key not in seen:
            seen.add(key)
            unique.append(resolved)
    return unique


def _html_to_pdf(
    html_path: Path, pdf_path: Path, notes: list[str]
) -> tuple[bool, str]:
    browsers = _browser_candidates()
    if not browsers:
        notes.append("no Chrome/Edge/Chromium found")
        return False, ""
    uri = html_path.resolve().as_uri()
    target = pdf_path.resolve()
    for browser in browsers:
        for headless in ("--headless=new", "--headless"):
            profile = Path(tempfile.mkdtemp(prefix="report-pdf-"))
            try:
                command = [
                    str(browser),
                    headless,
                    "--disable-gpu",
                    "--no-sandbox",
                    "--no-first-run",
                    f"--user-data-dir={profile}",
                    "--print-to-pdf-no-header",
                    "--virtual-time-budget=3000",
                    f"--print-to-pdf={target}",
                    uri,
                ]
                try:
                    proc = subprocess.run(
                        command, capture_output=True, text=True, timeout=120
                    )
                except (OSError, subprocess.TimeoutExpired) as exc:
                    notes.append(f"{browser.name} {headless}: {exc}")
                    continue
                if target.is_file() and target.stat().st_size > 1000:
                    return True, browser.name
                notes.append(
                    f"{browser.name} {headless}: exit {proc.returncode}, no pdf"
                )
            finally:
                shutil.rmtree(profile, ignore_errors=True)
    return False, ""


def _compile_pdf(tex_path: Path) -> tuple[bool, str]:
    engine = None
    for candidate in ("xelatex", "lualatex", "pdflatex"):
        if shutil.which(candidate):
            engine = candidate
            break
    if engine is None:
        return False, "no LaTeX engine found (xelatex/lualatex/pdflatex)"
    try:
        result = subprocess.run(
            [engine, "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
            cwd=str(tex_path.parent),
            capture_output=True,
            text=True,
            timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"{engine} failed: {exc}"
    if result.returncode != 0:
        tail = (result.stdout or "")[-600:]
        return False, f"{engine} exited {result.returncode}: {tail}"
    return True, f"compiled with {engine}"


def render_report(
    report_md: Path,
    out_dir: Path,
    fmt: str,
    title_fallback: str = "Report",
    pdf_engine: str = "auto",
) -> dict:
    markdown = report_md.read_text(encoding="utf-8")
    result: dict = {"format": fmt, "rendered": []}
    if fmt == "html":
        html_path = out_dir / "report.html"
        html_path.write_text(
            markdown_to_html(markdown, title_fallback), encoding="utf-8"
        )
        result["rendered"].append(str(html_path))
        return result
    if fmt == "latex":
        tex_path = out_dir / "report.tex"
        tex_path.write_text(
            markdown_to_latex(markdown, title_fallback), encoding="utf-8"
        )
        result["rendered"].append(str(tex_path))
        return result
    if fmt != "pdf":
        return result

    notes: list[str] = []
    html_path = out_dir / "report.html"
    html_path.write_text(markdown_to_html(markdown, title_fallback), encoding="utf-8")
    result["rendered"].append(str(html_path))

    candidates = _detect_pdf_skills() if pdf_engine in {"auto", "skill"} else []
    delegate = pdf_engine == "skill" or (
        pdf_engine == "auto"
        and any(
            candidate["conversion_capable"] and candidate["deps_ok"]
            for candidate in candidates
        )
    )
    if delegate:
        payload = _delegate_pdf(html_path, out_dir, candidates)
        result["pdf_compiled"] = False
        result["pdf_delegated"] = True
        result["pdf_delegation"] = payload
        result["pdf_note"] = "delegated to host PDF skill"
        return result

    if pdf_engine in {"auto", "browser"}:
        ok, engine = _html_to_pdf(html_path, out_dir / "report.pdf", notes)
        if ok:
            result["pdf_compiled"] = True
            result["pdf_engine"] = engine
            result["pdf_note"] = f"printed to PDF with {engine}"
            result["rendered"].append(str(out_dir / "report.pdf"))
            return result

    if pdf_engine in {"auto", "latex"}:
        tex_path = out_dir / "report.tex"
        tex_path.write_text(
            markdown_to_latex(markdown, title_fallback), encoding="utf-8"
        )
        result["rendered"].append(str(tex_path))
        compiled, note = _compile_pdf(tex_path)
        if compiled:
            result["pdf_compiled"] = True
            result["pdf_engine"] = "latex"
            result["pdf_note"] = note
            result["rendered"].append(str(out_dir / "report.pdf"))
            return result
        notes.append(note)

    result["pdf_compiled"] = False
    result["pdf_note"] = "; ".join(notes) or "no PDF engine available"
    return result
