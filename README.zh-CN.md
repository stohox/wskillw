# 地煞七十二变 skill

个人自建 Skill 归档仓库，用于版本管理、复用与跨环境迁移。

[English README](README.md) · [GitHub](https://github.com/stohox/wskillw)

## 目录结构

```
wskillw/
├── skills/
│   ├── research-reports/          # 证据优先的多领域研究报告
│   ├── web-ui-capture/            # 捕获网页状态，生成离线 HTML 原型
│   └── timesheet-batch-filling/   # 从考勤与 Git 证据生成工时草案（已脱敏）
├── collections/
│   └── nvwa-examples/             # 14 个公众人物/操盘手的思维框架蒸馏
├── ARCHIVE.md                     # 归档来源与清单
└── README.md / README.zh-CN.md
```

## Skill 清单

| Skill | 用途 | 来源 |
|-------|------|------|
| `research-reports` | 证据优先的多领域研究报告（市场 / 技术 / 人文），含来源台账、主张台账、领域校验器与 HTML/PDF 产出 | `D:\Alex\skill` |
| `web-ui-capture` | 捕获可观察的网页状态与截图，生成带模拟数据的离线可交互 HTML 原型 | `C:\Users\guoxi\.codex\skills\web-ui-capture` |
| `timesheet-batch-filling` | 从企业微信考勤、Git 提交与日报生成工时草案，并在明确授权后安全提交 | `C:\Users\guoxi\.codex\skills\timesheet-batch-filling`（脱敏副本） |
| `nvwa-examples` | 14 个公众人物/操盘手的思维框架、决策启发式与表达 DNA 蒸馏成果 | `C:\Users\guoxi\AppData\Roaming\devin\skills\nuwa-skill\examples` |

## 安装

把对应目录复制到目标 Agent 的 skill 根目录：

```bash
# WorkBuddy
cp -r skills/research-reports ~/.workbuddy/skills/

# Codex
cp -r skills/web-ui-capture ~/.codex/skills/
cp -r skills/timesheet-batch-filling ~/.codex/skills/

# nvwa 画像集合（作为参考库）
cp -r collections/nvwa-examples/* ~/.devin/skills/nuwa-skill/examples/
```

每个 Skill 目录根部保留自己的 `SKILL.md`。

## 脱敏与排除

- **`timesheet-batch-filling` 已脱敏。** 内网工时系统地址替换为 `${WORKLOG_BASE_URL}`，示例项目名替换为 `<PROJECT_NAME>`；不包含任何账号、令牌、Cookie 或密码。原始版本仍保留在 `C:\Users\guoxi\.codex\skills\timesheet-batch-filling`，见目录内 `REDACTION.md`。
- **`nvwa-examples` 未收录 1 个政治人物画像。** 该目录仍保留在源路径；公开仓库只收录其余 14 个画像。
- **`research-reports` 排除了非 Skill 文件。** `AGENTS.md` 与两份 `代码生成视频方法论-*.md` 不属于该 Skill，未纳入仓库；`SKILL.md`、`core/`、`profiles/`、`scripts/`、`assets/`、`references/`、`samples/` 均已收录。
- **缓存与本地状态**（`__pycache__`、`.pytest_cache`、`.env`、日志）由 `.gitignore` 排除。

## 约定

- 一个 Skill 一个目录，根目录放 `SKILL.md`。
- 不提交密钥、内网地址、客户数据或个人令牌。
- 示例产物仅在属于 Skill 文档的一部分时收录，仓库尽量控制在几 MB 以内。
- 每次变更用简短 commit message 说明 Skill 与改动内容。

## 所有权

个人归档仓库。未声明开源许可证；除 Skill 内另有说明外，权利归所有者。
