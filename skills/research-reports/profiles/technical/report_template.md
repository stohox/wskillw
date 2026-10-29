# {{manifest.title}}

{{manifest.subtitle}}

Prepared for: {{manifest.prepared_for}}
Prepared by: {{manifest.prepared_by}}
Verification date: {{manifest.verified_date}}
Retrieval cutoff: {{manifest.retrieval_cutoff}}
Classification: {{manifest.classification}}

> This report separates sourced facts, benchmarks, assumptions, opinions, and
> recommendations. Inline claim IDs map to `data/claims.csv`; source IDs map to
> `data/source_ledger.csv`. It is not procurement, legal, or security advice.

## Executive synopsis

Lead with the recommendation and the strongest evidence behind it. State the
uncertainty and the conditions that would reverse it.

## 1. Problem and decision context

**Scope:** {{manifest.scope_definition}}

**Systems in scope:** {{manifest.systems_in_scope}}

**Version policy:** {{manifest.version_policy}}

## 2. Evaluation criteria

{{manifest.evaluation_criteria}}

State the weighting rule if a score is used. Criteria must be fixed before
comparison.

## 3. Alternatives landscape

List current options, adjacent or substitute approaches, and explicitly excluded
alternatives, with primary-source citations.

## 4. Comparison matrix

Use `data/comparison_matrix.csv`. Each cell is supports / partial / no / unknown
with evidence source IDs. `unknown` is not `no`.

## 5. Benchmark and evidence methodology

Record version/commit, hardware, OS, runtime, workload, repetitions, measurement
method, and unit for every run in `data/benchmark_runs.csv`. Separate vendor
benchmarks from independent runs.

## 6. Findings and trade-offs

Distinguish measured results, documented vendor claims, and analyst judgment.

## 7. Risks and adoption considerations

Cover license compatibility, security advisories, maintenance health,
operational burden, lock-in, and migration path, each with dates.

## 8. Recommendation and decision thresholds

Keep the recommendation separate from evidence. State disconfirming evidence and
the thresholds that would change the decision.

## 9. Limitations

Missing benchmarks, environment mismatch, version drift, inaccessible proprietary
data, and residual uncertainty.

## References

Render from `data/source_ledger.csv`; do not cite unmapped sources.
