# {{manifest.title}}

{{manifest.subtitle}}

Prepared for: {{manifest.prepared_for}}
Prepared by: {{manifest.prepared_by}}
Corpus period: {{manifest.corpus_period}}
Citation style: {{manifest.citation_style}}
Retrieval cutoff: {{manifest.retrieval_cutoff}}
Classification: {{manifest.classification}}

> This report separates primary text, translation, paraphrase, interpretation, and
> secondary scholarship. Inline claim IDs map to `data/claims.csv`; source IDs map
> to `data/source_ledger.csv`; quotations map to `data/quotations.csv`.

## Abstract

State the research question, the corpus, the method, and the central argument in
one paragraph. Label the argument as interpretation.

## 1. Research question and scope

**Research question:** {{manifest.research_question}}

**Scope:** {{manifest.scope_definition}}

## 2. Corpus and edition selection

**Corpus:** {{manifest.corpus_summary}}

**Method:** {{manifest.methodology}}

State inclusion/exclusion rules, the edition rationale, and the locator scheme.
Use `data/corpus.csv`.

## 3. Historical and authorial context

Separate documented historical fact from inference; distinguish biography from
textual evidence.

## 4. Close reading and primary analysis

Every quotation must appear in `data/quotations.csv` with work_id, locator,
translation status, and verification state. Keep text, translation, paraphrase,
and interpretation distinct.

## 5. Critical reception and scholarship

Distinguish scholarly consensus, contested readings, and this report's argument.
Represent the strongest opposing reading before rebutting it.

## 6. Comparative analysis

When comparing works, state the tertium comparationis and avoid anachronistic
juxtaposition.

## 7. Interpretation and argument

Label interpretation as interpretation; do not present authorial intention as
textual fact.

## 8. Limitations and contested readings

Record textual variants, missing editions, translation loss, archival gaps, and
unresolved disputes.

## Bibliography

Render from `data/source_ledger.csv` in {{manifest.citation_style}} style; list
primary and secondary sources separately.
