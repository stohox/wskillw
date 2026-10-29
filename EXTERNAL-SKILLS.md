# 外部 Skill 精选

> 收录经过筛选的外部 Skill / Plugin / 工具，记录用途、适用场景、安装方式与使用边界。
> 最后核对：2026-10-29。
>
> 收录标准：能明显提升 Agent 工作流；有可读文档；许可证清晰；不要求提交敏感数据。
> 说明：本仓库只记录链接与使用笔记，不复制第三方代码；安装前请阅读上游 README 与 LICENSE。

## 索引

| 名称 | 形态 | 一句话 | 链接 |
|------|------|--------|------|
| **Archify** | Agent Skill + CLI | 把想法、方案或代码库变成可交互的单文件 HTML 图表 | https://github.com/tt-a1i/archify |
| **Understand Anything** | Claude Code Plugin / 多平台 Skill 集 | 把代码库或知识库变成可探索、可提问的知识图谱 | https://github.com/Egonex-AI/Understand-Anything |
| **OpenSpec** | CLI + 规格驱动工作流 | 先写规格再写代码：proposal / specs / design / tasks / archive | https://github.com/Fission-AI/OpenSpec |
| **Brainstorm（Superpowers）** | Agent Skill | 动手前用提问把“真正想要什么”问清楚，并产出设计文档 | https://github.com/obra/superpowers/tree/main/skills/brainstorming |

---

## 1. Archify

**仓库**：https://github.com/tt-a1i/archify  
**官网**：https://archify.si  
**形态**：Agent Skill + 零依赖 CLI（Node.js ≥ 18）  
**许可证**：Apache-2.0（历史版本为 MIT）  
**热度参考**：GitHub 约 91k stars（2026-10-29；热度不等于适配度）

### 它解决什么问题

Archify 把"技术意图"变成"可沟通的视觉产物"：用户用自然语言描述系统、方案或代码库，Agent 生成一个**自包含、可交互的 HTML 图表**，可以继续在对话中精修（"加一个 Redis"、"把回滚路径高亮"），也可以导出 PNG/PDF 分享。

它不是通用绘图编辑器，也不是 Mermaid 主题；它的差异在于：

- **类型化 JSON IR**：每种图表都有 schema，源文件可复现；
- **原子化验证**：schema、布局、HTML/SVG、路由、标签避让全部通过才替换"上一已知良好"文件；
- **源码证据可选**：节点可标记 `SRC n`，打开 Git 验证过的文件与行范围；
- **单文件可移植**：输出是一个 HTML，离线可开，发给别人仍可交互。

### 适用场景

1. **架构/方案评审**：让 Agent 读取代码库，生成 8–12 个核心组件、主路径、外部依赖与信任边界的运行时架构图。
2. **PR / 设计文档沟通**：把变更方案画成 Workflow、Sequence 或 Data Flow，减少"文字说不清"的评审往返。
3. **事故复盘**：用 Timeline + Sequence + Waterfall 还原事件顺序、调用链与耗时分解。
4. **数据与领域建模**：ERD、Class、Tree 展示表结构、接口继承、模块分解。
5. **一页式解释（Explainer）**：让 Agent 以"结论先行 + 每问题一栏"的形式输出解释页，含表格、步骤、代码与编号来源。
6. **对外分享**：单文件 HTML、PNG/WebP/JPG 长图、PDF 打印、1200×630 分享卡。

### 不适用场景

- 数值图表、仪表盘、BI 报表；
- 通用 WYSIWYG 绘图编辑器；
- 自动解析 Mermaid（README 明确不在范围内）；
- 托管分享服务（输出是本地单文件，不提供云托管）。

### 安装与调用

```bash
# 安装为全局 Agent Skill
npx skills add tt-a1i/archify -g

# 试用但不安装（以 Codex 为例）
npx skills use tt-a1i/archify@archify --agent codex
```

常见安装位置：Claude Code `~/.claude/skills/` 或 `.claude/skills/`；Codex `~/.agents/skills/` 或 `.agents/skills/`；opencode `~/.config/opencode/skills/` 等。

调用示例：

```text
Use Archify to draw: Browser -> API -> Redis cache -> PostgreSQL fallback.
Analyze this repository, then use archify to create a high-level runtime
architecture diagram. Show 8–12 core components, one primary path,
external dependencies, and trust boundaries.
```

### 使用建议

- 先让 Agent 画"主路径 + 边界"，细节放卡片，不要一开始堆几十条边；
- 每次只改一个结构（加节点、换布局、改主题），便于验证与回滚；
- 对外的图先导出 PDF/PNG，HTML 作为可交互附件；
- 架构图要标"证据来源/commit"，否则容易变成"看起来对"的示意图。

### 边界与风险

- 需要 Node.js ≥ 18；查看生成的 HTML 只需浏览器，不需要安装 Archify；
- 外部链接/地图跳转需要网络；更新检查可用 `ARCHIFY_UPDATE_CHECK_DISABLED=1` 关闭；
- 图表是"沟通产物"，不是运行时真相；关键结论仍要回到代码/监控验证。

---

## 2. Understand Anything

**仓库**：https://github.com/Egonex-AI/Understand-Anything  
**官网**：https://understand-anything.com/  
**形态**：Claude Code Plugin / 多平台 Skill 集（Codex、Cursor、Copilot、Gemini CLI、OpenCode、Kimi CLI 等）  
**许可证**：MIT  
**热度参考**：GitHub 约 89k stars（2026-10-29；热度不等于适配度）

### 它解决什么问题

Understand Anything 用多 Agent 流水线分析项目，构建**文件、函数、类、依赖关系的知识图谱**，再提供一个可交互的仪表盘，让你"先看全局，再读代码"。它也支持把知识库/文档（Karpathy-pattern wiki）转成带社区聚类的知识图谱。

它解决的是"接手陌生代码库/知识库时，从哪里开始"的问题，而不是替代 IDE 的跳转或精确调用图。

### 适用场景

1. **新代码库 onboarding**：面对 20 万行代码，先看知识图谱与核心模块，再有针对性地读文件。
2. **架构与依赖梳理**：看模块/文件/类的依赖关系，定位"改这里会影响哪里"。
3. **代码评审前快速理解**：在 Review 之前，先建立变更相关模块的全局图。
4. **知识库/文档理解**：把 wiki/文档转成实体、关系、主张的知识图谱，适合研究与写作前的资料梳理。
5. **团队分享**：把生成的 `.ua/` 数据目录提交到仓库，同事无需 LLM/API key，用 viewer 只读查看。

### 不适用场景

- 只想查一个符号/一个文件：用 grep、LSP 或 IDE 跳转更快；
- 需要精确调用图、性能剖析、运行时追踪：知识图谱不是 profiler；
- 不能把代码/文档交给 LLM 的隐私或合规场景；
- 需要实时 IDE 级补全/跳转：它是分析型工具，不是编辑器。

### 安装与调用

Claude Code（原生插件）：

```text
/plugin marketplace add Egonex-AI/Understand-Anything
/plugin install understand-anything
```

其他平台（以 Codex 为例）：

```bash
curl -fsSL https://raw.githubusercontent.com/Egonex-AI/Understand-Anything/main/install.sh | bash -s codex
```

Windows PowerShell：

```powershell
iwr -useb https://raw.githubusercontent.com/Egonex-AI/Understand-Anything/main/install.ps1 | iex
```

调用方式因平台而异：多数平台用 `/understand`，**Codex 用 `$understand`**；知识库分析用 `/understand-knowledge`。如果前缀不被识别，直接用自然语言："Use the understand skill to analyze this project."

只看图、不跑 LLM（Node.js ≥ 18）：

```bash
npx https://github.com/Egonex-AI/Understand-Anything/releases/latest/download/understand-anything-viewer.tgz /path/to/analyzed/project
```

### 使用建议

- 第一次分析先限定范围（核心服务/关键目录），不要一上来全仓库；
- 图谱用于"建立假设"，关键结论回到源码验证；
- 把 `.ua/`（或旧版 `.understand-anything/`）提交到仓库，方便团队共享；
- 在隐私敏感项目里，先确认模型提供方与数据流向，或改用本地模型。

### 边界与风险

- 多 Agent 分析会消耗较多 token/时间，仓库越大越明显；
- 图谱质量取决于代码结构、注释与语言支持；动态语言/生成代码可能噪声较大；
- 安装脚本会克隆仓库并创建符号链接，运行前先阅读 `install.sh` / `install.ps1`；
- 平台/命令更新较快，以仓库 README 为准。

---

## 3. OpenSpec

**仓库**：https://github.com/Fission-AI/OpenSpec  
**文档**：https://openspec.dev/docs  
**形态**：CLI + 规格驱动开发（SDD）工作流，面向 30+ AI 编程助手（不是单一 `SKILL.md`）  
**许可证**：MIT  
**热度参考**：GitHub 约 73k stars（2026-10-29；热度不等于适配度）

### 它解决什么问题

AI 编程助手很强，但当需求只存在于聊天记录里，结果就不可预测。OpenSpec 在"写代码"之前加一层轻量规格：人和 AI 先对齐"要做什么"，再把变更拆成 proposal / specs / design / tasks，完成后归档。

核心产物：

- `proposal.md`：为什么做、改什么；
- `specs/`：需求与场景（普通 Markdown，无特殊语法）；
- `design.md`：技术方案；
- `tasks.md`：实现清单；
- `openspec/changes/archive/`：已完成的变更归档。

### 适用场景

1. **新功能/大改动前**：需要先对齐需求、验收场景与技术方案，再让 AI 写代码。
2. **Brownfield 项目**：在现有代码上做变更，需要明确"改哪里、为什么、影响什么"。
3. **团队/跨仓库规格**：Stores（beta）把 `openspec/` 放到独立仓库，多个代码仓共享同一份规格。
4. **需要可审计的变更记录**：每个 change 都有 proposal/spec/design/tasks，完成后归档。
5. **多工具协作**：Claude Code、Codex、Cursor、Copilot 等 30+ 工具使用同一套规格。

### 不适用场景

- 一行修复、快速调试、紧急故障：直接改更快；
- 团队需要重量级阶段门与大量文档：Spec Kit 等更合适；
- 不愿意维护 Markdown 规格：OpenSpec 的价值来自规格本身。

### 安装与调用

macOS / Linux（单文件，无需 Node）：

```bash
curl -fsSL https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/scripts/binary/install.sh | sh
```

Windows PowerShell：

```powershell
irm https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/scripts/binary/install.ps1 | iex
```

npm（Node.js ≥ 20.19）或 Homebrew：

```bash
npm install -g @fission-ai/openspec@latest
brew install openspec
```

初始化：

```bash
cd your-project
openspec init
```

默认 profile 的常用命令：

- `/opsx:explore`：还没想清楚时，先探索；
- `/opsx:propose <change>`：创建变更（proposal / specs / design / tasks）；
- `/opsx:apply`：按 tasks 实现；
- `/opsx:archive`：归档并更新 specs。

不同工具前缀不同：Cursor / Copilot 可能是 `/opsx-propose`，Codex 可能是 `$openspec-propose`；`openspec init` 会打印正确形式。

### 使用建议

- 一个 change 只做一件事；跨仓库用 Stores，不要把多个仓库的变更塞进一个 proposal。
- 先写"可验证的场景"（WHEN/THEN），再写技术方案；场景就是验收标准。
- 实现前清空上下文，按 tasks 逐项推进；完成后 archive，保持 specs 与代码同步。
- 高推理模型更适合规划；实现阶段可用更便宜的模型。

### 边界与风险

- 默认收集匿名命令名/版本遥测；`openspec config set telemetry.enabled false` 或 `OPENSPEC_TELEMETRY=0` 可关闭。
- Stores 仍是 beta；跨仓库方案先小范围验证。
- 规格是"意图"，不是运行时真相；关键行为仍要测试/监控验证。

---

## 4. Brainstorm（Superpowers `brainstorming` skill）

**仓库**：https://github.com/obra/superpowers  
**Skill 路径**：https://github.com/obra/superpowers/tree/main/skills/brainstorming  
**形态**：Superpowers 框架内的 Agent Skill（自动触发，不是独立仓库）  
**许可证**：MIT（父仓库）  
**热度参考**：父仓库约 307k stars（2026-10-29；热度不等于适配度）

> 说明：这里指 `obra/superpowers` 的 `brainstorming` skill；不是同名的独立仓库或低星分支。

### 它解决什么问题

在"动手做"之前，先把"真正想要什么、为什么"问清楚。它通过提问让用户描述意图，复述理解、让用户纠正，列出 2–3 个实现路径与取舍，最后写设计文档；**设计文档获批前，不允许写产品代码**（HARD-GATE）。

### 适用场景

1. **新功能/新产品**：需求还模糊，需要先对齐 what/why。
2. **非软件创意**：演讲、业务、装修等"要先想清楚再动手"的事。
3. **设计文档**：需要一份能让别的工程师直接排期的 design doc。
4. **避免"AI 猜错意图就开写"**：强制在实现前确认设计。
5. **与 Superpowers 串联**：brainstorm → design → writing-plans → TDD 实现。

### 不适用场景

- 需求已经完全明确的小改动（例如"把图标改成矢车菊蓝"）；
- 紧急故障/线上事故：先止血，再复盘；
- 只想让 AI 直接改代码、不想参与设计讨论。

### 安装与调用

Superpowers 按平台安装，常见方式：

- **Claude Code**：`/plugin install superpowers@claude-plugins-official`；或 `/plugin marketplace add obra/superpowers-marketplace` 后 `/plugin install superpowers@superpowers-marketplace`
- **Codex**：在 Plugins 市场搜索 `superpowers` 安装
- **Cursor**：`/add-plugin superpowers`
- **其他平台**：见父仓库 README 的 Installation 段

安装后，`brainstorming` 会在"开始构建"前自动触发；也可以显式说"用 brainstorming 帮我梳理这个想法"。它位于 `skills/brainstorming/SKILL.md`。

### 工作流要点

1. 先读现有项目/上下文，不问已知信息；
2. 第一条消息复述请求、指出关键约束/冲突，只问一个最影响结果的问题；
3. 对话中每次只问一个问题，逐步回放理解；
4. 给出 2–3 个实现路径与取舍，推荐一个；
5. 写设计文档（小改动短版，项目完整版），项目版可让 fresh subagent 做 builder check；
6. 设计获批后才进入 writing-plans / 实现（HARD-GATE）。

### 边界与风险

- 对小任务可能显得"流程重"；如果用户明确说"直接做"，它会退场。
- 自动触发依赖 Superpowers 的 bootstrap；某些平台/长会话压缩后可能失效，重开会话或显式调用。
- 可选 visual companion 会从官网加载 logo（含版本号）；`SUPERPOWERS_DISABLE_TELEMETRY` 可关闭。

---

## 选型建议

| 目标 | 优先选择 | 原因 |
|------|----------|------|
| 需求模糊，先想清楚要做什么 | Brainstorm | 提问/回放/设计文档，锁定 what & why |
| 需求已清楚，要规格与变更管理 | OpenSpec | proposal/spec/design/tasks + archive |
| 接手陌生代码库/知识库 | Understand Anything | 知识图谱先看全局 |
| 把方案/架构"画出来"给人看 | Archify | 可交互 HTML，适合评审与分享 |
| 事故复盘 | Archify | Timeline/Sequence/Waterfall 组合 |
| 代码评审前建立全局图 | Understand Anything | 依赖/影响面探索 |
| 一页式解释/教学材料 | Archify（Explainer） | 结论先行 + 图表 + 来源 |
| 单符号/单文件查找 | grep / LSP / IDE | 这些工具都太重 |

**推荐链路（不是强绑定）**：

1. **Understand Anything**：先摸清现有代码/知识库，建立全局图；
2. **Brainstorm**：把 what/why 问清楚，产出设计文档；
3. **OpenSpec**：把设计拆成 proposal / specs / design / tasks；
4. **Archify**：把关键架构/流程画出来，用于评审或分享；
5. **实现**：进入编码；Superpowers 可继续接 writing-plans / TDD，OpenSpec 用 `/opsx:apply` 按 tasks 推进。

这套链路覆盖"理解现状 → 想清楚 → 写规格 → 画出来 → 实现"，四个工具各管一段，不互相替代。

## 维护约定

- 每个条目至少记录：名称、仓库链接、形态、用途、适用场景、不适用场景、安装方式、许可证、最后核对日期。
- 只记录链接与使用笔记，不复制第三方代码；不镜像第三方仓库。
- 新增前先核对：许可证、最近更新时间、是否仍在维护、是否要求上传代码/数据。
- 热度（stars）只作参考，不作为推荐依据。
- 安装第三方 Skill/Plugin 前，先阅读安装脚本与权限要求；生产环境建议锁定版本。
