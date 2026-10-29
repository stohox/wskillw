# {{manifest.title}}

{{manifest.subtitle}}

编制对象：{{manifest.prepared_for}}
编制单位：{{manifest.prepared_by}}
资料截止：{{manifest.retrieval_cutoff}}
密级：{{manifest.classification}}

> 本报告区分有来源的事实、计算、假设、预测与建议。正文中的主张编号对应 `data/claims.csv`；来源编号对应 `data/source_ledger.csv`。本报告不构成投资、法律或财务建议。

## 执行摘要

仅陈述有主张编号支撑的结论。市场规模与预测须以情景区间呈现，不得表述为单一确定值。

## 1. 范围与市场定义

**定义：** {{manifest.market_definition}}

**地理范围：** {{manifest.geography}}
**币种/基期：** {{manifest.currency}}，{{manifest.price_basis}}，基年 {{manifest.base_year}}
**分类体系：** {{manifest.taxonomy}} {{manifest.taxonomy_version}}
**历史期间：** {{manifest.historical_period}}
**预测期间：** {{manifest.forecast_period}}

### 纳入范围

{{inclusions_block}}

### 排除范围

{{exclusions_block}}

## 2. 证据与方法

说明来源层级、检索日期、修订情况、冲突处理、换算方法、调研方法与局限。

## 3. 市场规模与口径校验

分别报告自上而下与自下而上的 TAM 估算。列明分母、覆盖键、排除类别、SAM 筛选条件、SOM 获取假设、情景区间、敏感性，以及两种方法的差异与残余差异。

## 4. 需求与客户证据

区分观察到的需求、调研估计、访谈主题与分析判断。不得将定性访谈推广为总体比例。

## 5. 竞争格局

在计算份额或集中度之前，先界定产品与地理范围。使用有证据链的竞品矩阵；证据缺失时标注为"未知"，不得推断为"没有"。

## 6. 预测情景

描述每个条件情景的增长率路径、假设、驱动与抑制因素及敏感性。不得将情景区间称为置信区间或预测区间。

## 7. 监管、风险与不确定性

区分已生效规则、拟议规则、分析判断与法律意见。

## 8. 结论与选项

将建议与有来源的发现严格分开。说明依赖条件、决策阈值与反证。

## 局限

列出数据缺口、来源冲突、分类断点、修订、抽样与无应答问题、模型局限与残余不确定性。

## 参考文献

从 `data/source_ledger.csv` 渲染；不得引用未登记来源。
