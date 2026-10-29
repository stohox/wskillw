# Technical Research Report Structure

Match depth to the decision. There is no required page count, figure count, or
output format. Omit irrelevant modules; expand methods and limitations when
uncertainty is high.

## Front matter

- subject and scope (what is being compared or investigated);
- systems/options in scope and explicitly excluded ones;
- version/commit policy and verification date;
- retrieval cutoff, report version, classification;
- nota bene: not procurement, legal, or security advice.

## 1. Problem and decision context

State the decision, constraints (latency, cost, team skills, compliance,
deployment target), and what would change the recommendation.

## 2. Scope and evaluation criteria

Define criteria before comparing: performance, maturity, ecosystem, licensing,
security, operability, migration cost. Weight them only if the decision needs a
score; publish the weighting rule.

## 3. Alternatives landscape

List current options, adjacent/substitute approaches, and explicitly out-of-scope
alternatives. Use primary sources (official docs, RFCs, specs, repositories).

## 4. Comparison matrix

Use `data/comparison_matrix.csv`. Every cell is `supports` / `partial` / `no` /
`unknown` with evidence source IDs. `unknown` is not `no`.

## 5. Benchmark and evidence methodology

For every benchmark run record version/commit, hardware, OS, runtime, workload,
repetitions, measurement method, and unit. Separate vendor benchmarks from
independent or self-run benchmarks. Do not compare runs with different
environments as if they were equivalent.

## 6. Findings and trade-offs

Lead with findings, then trade-offs. Distinguish measured results, documented
claims, and analyst judgment.

## 7. Risks and adoption considerations

Cover license compatibility, security advisories (CVE), maintenance/community
health, operational burden, vendor lock-in, and migration path. Cite dates.

## 8. Recommendation and decision thresholds

Keep the recommendation separate from evidence. State conditions that would
reverse it and the evidence that would trigger a revision.

## 9. Limitations

Missing benchmarks, environment mismatch, version drift, inaccessible proprietary
data, and residual uncertainty.

## References

Render from `data/source_ledger.csv`; every cited source must appear there.
