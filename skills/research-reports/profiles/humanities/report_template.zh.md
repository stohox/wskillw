# {{manifest.title}}

{{manifest.subtitle}}

编制对象：{{manifest.prepared_for}}
编制单位：{{manifest.prepared_by}}
语料时段：{{manifest.corpus_period}}
引注格式：{{manifest.citation_style}}
资料截止：{{manifest.retrieval_cutoff}}
密级：{{manifest.classification}}

> 本报告区分一手文本、译文、转述、阐释与二手研究。正文中的主张编号对应 `data/claims.csv`；来源编号对应 `data/source_ledger.csv`；引文对应 `data/quotations.csv`。

## 摘要

用一段话说明研究问题、语料、方法与核心论点。论点须标注为"阐释"，不得表述为文本事实。

## 1. 研究问题与范围

**研究问题：** {{manifest.research_question}}

**范围：** {{manifest.scope_definition}}

## 2. 语料与版本选择

**语料：** {{manifest.corpus_summary}}

**方法：** {{manifest.methodology}}

说明纳入与排除规则、版本选择理由、定位方案（页码、行号、卷次等）。使用 `data/corpus.csv`。

## 3. 历史与作者语境

区分有据可查的历史事实与推断；区分作者生平与文本证据。

## 4. 细读与一手分析

所有引文须登记于 `data/quotations.csv`，含作品编号、定位、译本状态与核验状态。文本、译文、转述与阐释须严格区分。

## 5. 批评史与研究现状

区分学界共识、争议性读法与本文论点。先呈现最强的对立读法，再作回应。

## 6. 比较分析

比较作品时须说明比较基准（tertium comparationis），避免时代错置与脱离语境的并置。

## 7. 阐释与论证

阐释须标注为阐释；不得将作者意图表述为文本事实。每一条阐释性主张须对应文本定位与二手文献。

## 8. 局限与争议

记录异文、版本缺失、翻译损失、档案缺口与未决的阐释争议。

## 参考文献

从 `data/source_ledger.csv` 按 {{manifest.citation_style}} 格式渲染；一手与二手文献分列。
