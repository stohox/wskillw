# Intake — research contract

Ask only what is not already clear from the user's request. Do not run a
questionnaire when the answer is already implied. Maximum six questions; skip any
that would not change the profile, scope, or deliverable.

## Questions

1. **Direction** — market, technical, or humanities? (`auto` lets the router infer
   from the decision text.)
2. **Decision and audience** — what decision will this report support, and for
   whom?
3. **Deliverable** — `markdown`, `html`, `latex`, or `pdf`?
4. **Language** — `zh` or `en`? (Chinese triggers `ctex` in the LaTeX preamble.)
5. **Evidence access** — primary official sources, secondary synthesis, paid
   estimates, or mixed? (Shifts the source hierarchy emphasis, not the schema.)
6. **Scope** — geography, period, systems/corpus, and explicit exclusions.
7. **Depth** — `brief` (≥8 pages), `standard` (≥20 pages), or `deep` (≥45 pages).
   Depth is a floor, not a target for padding.

## Mapping

| Answer | Effect |
|--------|--------|
| `direction` | selects `profiles/<id>/profile.json` |
| `decision` | fills `market_definition` / `scope_definition` / `research_question` |
| `audience` | fills `prepared_for` |
| `deliverable` | `--format markdown\|html\|latex\|pdf` |
| `language` | report language; `zh` triggers `ctex` in LaTeX |
| `length` | `--length brief\|standard\|deep`; writes `report_contract.json` |
| `evidence_access` | source-hierarchy emphasis (core rules unchanged) |
| `scope_notes` | scope narrative and exclusions |
| `geography` / `currency` | market manifest fields |
| `systems_in_scope` / `evaluation_criteria` | technical manifest fields |
| `corpus_period` | humanities manifest field |

## intake.json

```json
{
  "direction": "auto",
  "decision": "What decision this report supports",
  "audience": "Who reads it",
  "deliverable": "html",
  "language": "zh",
  "length": "standard",
  "evidence_access": "primary",
  "scope_notes": "Geography, period, exclusions",
  "report_title": "Optional explicit title",
  "geography": "China",
  "currency": "CNY",
  "historical_period": "2021-2025",
  "forecast_period": "2026-2030",
  "systems_in_scope": ["Option A", "Option B"],
  "evaluation_criteria": ["latency", "license", "operability"],
  "corpus_period": "1910-1935"
}
```

## Route

```bash
python3 scripts/recommend_profile.py --intake intake.json --write-manifest manifest.json
```

The router prints the recommended profile, format, manifest draft, and the
`missing_fields` that still need an answer. Then:

```bash
python3 scripts/generate_report_scaffold.py --profile <id> --format <fmt> manifest.json ./out
```
