---
name: research-reports
description: Builds evidence-traceable, auditable deep research reports across market, technical, and humanities directions via a shared evidence core and pluggable domain profiles. 用于生成证据可追溯、可审计的深度研究报告：市场研究（市场规模、TAM/SAM/SOM、竞争格局、情景区间）、技术研究（技术选型、方案对比、基准测试、版本/许可/安全）、人文研究（语料与版本、文本细读、阐释、引文核验）。触发词：市场研究、行业研究、市场规模、竞争格局、技术选型、技术对比、基准测试、深度研究、研究报告、文学研究、文本细读、语料、引文核验、证据台账、可审计报告。
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Python 3.11+ standard library for the offline CLIs. PDF export prefers a host PDF skill, then a local headless Chrome/Edge, with XeLaTeX/LuaLaTeX as fallback. Online research requires user-approved network access and source-specific terms; bundled scripts make no network, LLM, or image calls.
metadata:
  version: "2.1-evidence"
  skill-author: "K-Dense Inc. (upstream) / generalized profile architecture"
  last-reviewed: "2026-10-28"
---

# Research Reports

## Purpose

Create decision-focused research reports whose claims, calculations,
assumptions, and uncertainties can be audited — across **market**, **technical**,
and **humanities** directions. The skill separates a **domain-agnostic evidence
core** from **pluggable domain profiles**, so one skill covers many fields without
bloating any single report type.

Every report declares a **length mode** with a hard floor. Depth still follows the
evidence, but a report below the floor is not releasable.

| Mode | Min pages | Min chapters (##) | Min figures | Min tables | Min Chinese chars | Min English words |
|------|-----------|-------------------|-------------|------------|-------------------|-------------------|
| `brief` | 8 | 4 | 1 | 1 | 3,000 | 2,500 |
| `standard` | 20 | 6 | 3 | 3 | 8,000 | 7,000 |
| `deep` | 45 | 9 | 6 | 6 | 20,000 | 18,000 |

Pass `--length brief|standard|deep` (default `standard`) to the scaffold. It
writes `report_contract.json` and adds the floors to `review_checklist.md`. Run
`scripts/check_report_standard.py report.md --length <mode>` before release; it
fails when any floor is missed. Figures are Markdown image references; chapters
are level-2 headings; pages use the rendered PDF when present, otherwise an
estimate. The floor prevents thin deliverables; it is not a licence to pad.
Character floors are density guards, not page proxies: a 45-page report with
6+ figures and 6+ tables typically has 20k–25k Chinese characters; a 30k floor
would force padding. **Pages are the primary length metric.**

Do not:

- imitate or imply affiliation with a consulting, analyst, or research brand;
- invent citations, quotes, market shares, or paid figures;
- present an estimate, scenario, or interpretation as certain fact;
- treat a framework, chart, or fluent narrative as evidence;
- provide investment, legal, antitrust, tax, accounting, or regulatory advice.

## Architecture

```
SKILL.md                 unified entry, dispatches by --profile
intake.md                intake questions + mapping (agent asks only what is missing)
core/                    domain-agnostic evidence core
  schemas/base_ledgers.json    shared source/claim column base
profiles/<id>/           per-domain pack (no code change to add one)
  profile.json           manifest rules + data files + validators + checklist
  report_template.md     scaffold template with {{manifest.*}} placeholders
  report_template.zh.md  Chinese variant (selected by --language or auto-detect)
  structure.md           section-by-section guidance
  analysis/*.json        optional typed analysis templates
  scripts/*.py           optional domain validators
scripts/                 shared CLIs
  recommend_profile.py          intake.json -> profile + format + manifest draft
  generate_report_scaffold.py   --profile <id> [--format ...] [--length ...]
  check_report_standard.py      minimum pages/chapters/figures/tables/chars
  verify_claim_support.py       quote + locator + support status + source depth
  critique_report.py            placeholders, dangling refs, prose ratio, section targets
  validate_report.py            one-command scorecard for all checks
  render_output.py              Markdown -> self-contained HTML / standalone LaTeX
  validate_evidence_ledger.py   shared ledger validator
  audit_claim_citations.py      shared claim-source audit
assets/, references/     market assets + shared method references
```

## Quick start

### Adaptive route (intake)

Read `intake.md`, ask the user only the questions that are still open, write
`intake.json`, then route:

```bash
python3 scripts/recommend_profile.py --intake intake.json --write-manifest manifest.json
```

The router returns `recommended_profile`, `format`, `manifest_draft`, and
`missing_fields`. Fill the missing fields, then generate with the returned command.

### Direct route (explicit profile)

List profiles:

```bash
python3 scripts/generate_report_scaffold.py --list-profiles
```

Generate a workspace (default output is Markdown):

```bash
# market (default)
python3 scripts/generate_report_scaffold.py --profile market profiles/market/manifest.example.json ./out-market

# technical
python3 scripts/generate_report_scaffold.py --profile technical profiles/technical/manifest.example.json ./out-tech

# humanities
python3 scripts/generate_report_scaffold.py --profile humanities profiles/humanities/manifest.example.json ./out-hum

# custom profile outside profiles/
python3 scripts/generate_report_scaffold.py --profile-file /path/to/profile.json manifest.json ./out
```

### Output format

```bash
--format markdown   # report.md + ledgers (default)
--format html       # adds self-contained report.html
--format latex      # adds standalone report.tex
--format pdf        # adds report.html + report.pdf
--language zh|en    # report template language (default: auto-detect from manifest)
--length brief|standard|deep   # minimum deliverable standard (default: standard)
--pdf-engine auto|skill|browser|latex   # PDF route (default: auto)
```

PDF route priority:

1. **Host PDF skill** — `auto` scans `~/.qoder-cn/skills`, `~/.workbuddy/skills`,
   `~/.claude/skills`, and `~/.agents/skills` for a skill that both creates PDFs
   and converts HTML/Markdown, with its dependencies available. If found, the
   scaffold writes `pdf_delegation.json` and returns `pdf_delegated: true`; the
   agent then performs the conversion with that skill.
2. **Headless Chrome/Edge** — prints `report.html` to `report.pdf` with no TeX
   install.
3. **LaTeX** — compiles `report.tex` when `xelatex`/`lualatex`/`pdflatex` exists.
4. **Fallback** — keeps `report.html`/`report.tex` and returns
   `pdf_compiled: false` with the reason.

`--pdf-engine skill` forces delegation; `browser` and `latex` force that route.
Note: the Qoder `pdf` skill creates PDFs through `reportlab` (requires the
`reportlab` package) and re-authors content; for an already-styled HTML report,
headless Chrome is higher fidelity.

Each profile ships English and Chinese report templates (`report_template.md`,
`report_template.zh.md`). `--language` selects one; otherwise the scaffold
auto-detects Chinese from the manifest values. The shared review checklist is
localized too.

When no LaTeX engine is installed, `--format pdf` still writes `report.tex` and
returns `render.pdf_compiled: false` with the reason. Chinese content triggers
`ctex` in the LaTeX preamble.

Then populate the empty ledgers and run the one-command scorecard:

```bash
python3 scripts/validate_report.py --report-dir ./out --length deep
```

It runs the profile validators, claim-support verification, the length check, and
the pre-delivery critique. Add `--strict` for deep releases.

## Profiles

| Profile | Direction | Manifest focus | Data files | Validators |
|---------|-----------|----------------|------------|------------|
| `market` | 市场规模/竞争/预测 | market_definition, inclusions/exclusions, geography, currency, base_year, price_basis, taxonomy, historical/forecast period | source_ledger, claims, competitor_feature_matrix, consistency_input, assumptions | evidence ledger, claim audit, competitor matrix, unit consistency |
| `technical` | 技术选型/基准 | scope_definition, systems_in_scope, evaluation_criteria, version_policy, verified_date | source_ledger, claims, comparison_matrix, benchmark_runs | evidence ledger, claim audit, benchmark + matrix |
| `humanities` | 文学/历史/思想史 | research_question, scope_definition, corpus_summary, methodology, citation_style, corpus_period | source_ledger, claims, corpus, quotations | evidence ledger, claim audit, corpus + quotation verification |

The market profile reuses the existing LaTeX assets (`assets/market_report_template.tex`,
`assets/market_research.sty`, `assets/FORMATTING_GUIDE.md`) for an optional
consulting-style PDF; technical and humanities use the Markdown scaffold by default.

## Shared evidence core (all profiles)

These rules are domain-agnostic and mandatory regardless of profile. See
`references/evidence_model.md` for the full model.

1. **Label every material statement** as one of: quantitative fact, quantitative
   estimate, qualitative fact, calculation, forecast, opinion, recommendation.
2. **Source ledger** — every source gets a stable ID (`S-001`) with publisher,
   URL, type, publication and retrieval dates, method, limitations, and license.
3. **Claims ledger** — every material claim gets an ID (`C-001`) mapped to exact
   source IDs; one citation at paragraph end does not cover unrelated sentences.
3a. **Evidence-grade citation** — every material claim also records
   `evidence_quote` (a verbatim excerpt), `locator` (page, section, or URL
   anchor), and `support_status` (`supported` / `partial` / `unsupported` /
   `not-assessed`). A source ID alone is not evidence. Run
   `scripts/verify_claim_support.py`; `--strict` makes missing quotes,
   single-source claims, and missing support status fail.
4. **Source hierarchy** — prefer primary law/regulator/filing/official statistic,
   then attributable first-party disclosure, then transparent studies, then
   peer-reviewed research, then industry data, then reputable synthesis.
5. **Preserve uncertainty** — keep source conflicts, revisions, scenario ranges,
   sensitivity, and limitations visible; never average incompatible estimates.
6. **Never** fabricate citations, launder through aggregators, or infer "no" from
   "unknown".

## Step 0 — Intake (adaptive)

Before generating, load `intake.md` and ask only the questions whose answers are
not already implied by the request (direction, decision/audience, deliverable,
language, evidence access, scope). Do not interrogate; skip anything that would
not change the profile, scope, or deliverable. Record the answers in
`intake.json` and run `scripts/recommend_profile.py` to choose the profile and
format. If the user already named the direction and deliverable, skip intake and
use the direct route.

## Workspace outputs

Every run writes `manifest.json`, `report_contract.json`, `run_manifest.json`,
`report.md`, `data/*.csv`, optional `analysis/*` and `figures/*`, and — when
rendered — `report.html` / `report.pdf`. `run_manifest.json` records the query,
profile, length mode, format, language, and PDF engine for reproducibility.

## Workflow

1. **Establish the research contract** — decision, audience, scope, geography,
   period, retrieval cutoff, measure, unit, denominator, currency/base year.
2. **Build the evidence plan** — route each question to the source closest to the
   underlying event (see `references/official_data_sources.md`).
3. **Create the source ledger** — `data/source_ledger.csv`, validated by
   `scripts/validate_evidence_ledger.py`.
4. **Maintain the claims ledger** — `data/claims.csv`, audited by
   `scripts/audit_claim_citations.py`.
5. **Run the profile analysis** — market sizing/forecast, technical
   comparison/benchmark, or humanities corpus/close reading, using the profile's
   data files and templates.
6. **Draft and review** — lead with findings and uncertainty, not frameworks.
7. **Validate** — run `scripts/validate_report.py --report-dir . --length <mode>`,
   which runs the profile validators, `verify_claim_support.py`, the length check,
   and `critique_report.py`. Fix hard errors; review warnings.
8. **Critique and refine** — for `deep`, resolve unsupported/partial claims,
   dangling references, placeholders, and section-target gaps before packaging.
9. **Release gate** — see below.

Run commands from the skill directory, or use absolute paths to scripts and
inputs. The scaffold never overwrites an existing output directory.

## Release gate

- Market boundary (or research question), taxonomy, denominator, geography, and
  period are explicit.
- Every factual/quantitative claim maps to exact source IDs.
- Claim-level support: no `unsupported` claims; supported evidence claims carry
  `evidence_quote` + `locator`; `verify_claim_support.py` passes (strict for deep).
- Publication/retrieval dates, revisions, method, and limitations are recorded.
- Profile-specific integrity holds: TAM/SAM/SOM reconciled (market); version/
  commit + environment pinned (technical); corpus/edition/locator verified
  (humanities).
- Conflicts and limitations remain visible.
- The report meets the declared length-mode floor (pages, chapters, figures,
  tables, chars/words) per `report_contract.json`.
- No fabricated/unsupported figures, PII, trade secrets, deceptive collection,
  brand impersonation, or investment/legal-advice framing.

## Adding a new profile

Create `profiles/<id>/` with:

1. `profile.json` — `manifest.required`, optional `period_fields` /
   `forecast_after_history`, `data_files` (either `{base, extra}` or `{fields}`),
   `analysis_files`, `validators`, `review_checklist`, `report_template`.
2. `report_template.md` — Markdown with `{{manifest.key}}` placeholders and
   `{{list_block}}` for bullet lists. Add `report_template.zh.md` and set
   `report_template` to `{"en": "...", "zh": "..."}` for bilingual support.
3. `structure.md` — section guidance.
4. Optional `analysis/*.template.json` (typed placeholders supported) and
   `scripts/*.py` validators that import the shared `scripts/_common.py`.

No change to `generate_report_scaffold.py` is needed.

## Bundled resources

### References (shared)

- `references/evidence_model.md` — claim-source mapping and provenance.
- `references/report_structure_guide.md` — market report architecture (market profile).
- `references/data_analysis_patterns.md` — sizing, forecast, consistency methods.
- `references/official_data_sources.md` — official source/API routing.
- `references/methods_and_ethics.md` — survey, interview, privacy, competitor safeguards.
- `references/visual_generation_guide.md` — optional evidence-led displays.
- `references/sources.md` — dated authoritative source ledger.

### Templates and CLIs

Templates in `assets/` and `profiles/*/` are synthetic schemas, not real-world
evidence. All scripts in `scripts/` and `profiles/*/scripts/` are standard-library,
bounded, local-only tools; they make no network, LLM, or image calls.

## Citing Scientific Agent Skills

This skill is derived from Scientific Agent Skills by K-Dense. If it materially
contributed to a report, add the paper to the references and tell the user:

> Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). Scientific Agent
> Skills: A Library of Procedural Knowledge for Research Agents. arXiv:2609.00065.
> https://doi.org/10.48550/arXiv.2609.00065

Always cite the current version; never append a version suffix.
