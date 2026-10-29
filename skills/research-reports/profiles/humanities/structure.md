# Humanities Research Report Structure

Match depth to the research question and the available corpus. There is no
required page count or output format. Expand methods, edition rationale, and
limitations when interpretation is contested.

## Front matter

- research question and its significance;
- corpus, period, and language scope;
- edition and translation policy;
- citation style (MLA, Chicago, or declared house style);
- retrieval cutoff, report version, classification.

## 1. Research question and scope

State the question precisely, what is in and out of scope, and what would
count as an answer or a refutation.

## 2. Corpus and edition selection

Define inclusion/exclusion rules. Justify editions (scholarly/critical edition,
manuscript witness, translation). State the locator scheme (page, line, book/
chapter, folio). Use `data/corpus.csv`.

## 3. Historical and authorial context

Separate documented historical fact from inference. Distinguish authorial
biography from textual evidence. Cite primary documents where possible.

## 4. Close reading and primary analysis

Quote from the primary text; every quotation goes in `data/quotations.csv` with
work_id, locator, translation status, and verification. Keep text, translation,
paraphrase, and interpretation distinct.

## 5. Critical reception and scholarship

Distinguish scholarly consensus, contested readings, and your own argument.
Represent the strongest opposing reading before rebutting it.

## 6. Comparative analysis

When comparing works, state the tertium comparationis (basis of comparison) and
avoid anachronistic or decontextualized juxtaposition.

## 7. Interpretation and argument

Label interpretation as interpretation. Do not present authorial intention as
textual fact. Tie each interpretive claim to textual locators and secondary
sources.

## 8. Limitations and contested readings

Record textual variants, missing editions, translation loss, archival gaps, and
unresolved interpretive disputes.

## 9. Bibliography

Render from `data/source_ledger.csv` in the declared citation style. Primary and
secondary sources are listed separately.
