# {{manifest.title}}

{{manifest.subtitle}}

编制对象：{{manifest.prepared_for}}
编制单位：{{manifest.prepared_by}}
核验日期：{{manifest.verified_date}}
资料截止：{{manifest.retrieval_cutoff}}
密级：{{manifest.classification}}

> 本报告区分有来源的事实、基准测试、假设、意见与建议。正文中的主张编号对应 `data/claims.csv`；来源编号对应 `data/source_ledger.csv`。本报告不构成采购、法律或安全建议。

## 执行摘要

先给结论与最强证据，并说明不确定性与可能推翻结论的条件。

## 1. 问题与决策背景

**范围：** {{manifest.scope_definition}}

**纳入系统：** {{manifest.systems_in_scope}}

**版本策略：** {{manifest.version_policy}}

## 2. 评估标准

{{manifest.evaluation_criteria}}

若使用打分，须先公布权重规则；标准须在比较前固定。

## 3. 方案全景

列出当前可选方案、相邻或替代方案，以及明确排除的方案，并附一手来源。

## 4. 对比矩阵

使用 `data/comparison_matrix.csv`。每格为 支持 / 部分支持 / 不支持 / 未知，并附证据来源编号。"未知"不等于"不支持"。

## 5. 基准与证据方法

在 `data/benchmark_runs.csv` 中记录每次运行的版本或提交、硬件、操作系统、运行时、工作负载、重复次数、测量方法与单位。区分厂商基准与独立运行，不得把不同环境的运行当作可直接比较。

## 6. 发现与权衡

区分实测结果、厂商声明与分析判断。

## 7. 风险与采用考量

覆盖许可证兼容性、安全公告、维护健康度、运维负担、锁定风险与迁移路径，并注明日期。

## 8. 建议与决策阈值

将建议与证据分开。说明反证，以及会改变决策的阈值。

## 9. 局限

缺失基准、环境不一致、版本漂移、无法获取的专有数据与残余不确定性。

## 参考文献

从 `data/source_ledger.csv` 渲染；不得引用未登记来源。
