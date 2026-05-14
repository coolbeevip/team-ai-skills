# Repository Guidelines

## 项目结构与模块组织

本仓库是团队大语言模型技能库。技能统一放在标准目录 `skills/` 下，`skills/` 的一级子目录代表团队职责域。

- `skills/product/`：产品定义职责，包括需求细化、规格评审和 PRD 固化。
- `skills/product/team-spec-refine/`：用于与用户反复确认并打磨规格。
- `skills/product/team-spec-review/`：用于评审规格风险和 ready 状态。
- `skills/product/team-spec-to-prd/`：用于把 ready 的规格固化成 PRD。
- `skills/architecture/`：架构与方案设计职责。
- `skills/architecture/team-spec-to-functional-design/`：用于基于需求规格与代码生成企业级功能设计说明书。
- `skills/delivery/`：交付执行职责，包括 PRD 交接、issue 拆解、实现和验证。
- `skills/delivery/team-prd-handoff/`：用于把 AI 结构化 PRD 转换为人类可评审的三方交接文档。
- `skills/delivery/team-prd-to-issues/`：用于把 PRD 拆解成可独立领取的工程 issue。
- `skills/delivery/team-issue-implement/`：用于按行为测试和 TDD 循环实现单个 issue。
- `skills/delivery/team-issue-verify/`：用于验证单个 issue 实现是否满足验收标准和 PRD。
- `skills/tech-debt/`：技术债治理职责，包括技术债细化、评审和工程拆解。
- `skills/tech-debt/team-tech-debt-refine/`：用于把模糊技术债诉求细化为可评审规格。
- `skills/tech-debt/team-tech-debt-review/`：用于评审技术债风险、优先级和可执行性。
- `skills/tech-debt/team-tech-debt-to-issues/`：用于把已评审技术债拆解为工程 issue。
- `skills/documentation/`：文档质量与格式规范职责。
- `skills/documentation/team-md-style-check/`：用于检查 Markdown 是否符合飞书文档导入后的样式映射规则。

每个技能目录必须包含 `SKILL.md`。只有当辅助文件被 `SKILL.md` 明确引用时才添加，例如 `CONTEXT-FORMAT.md`、`DECISION-FORMAT.md`。

## Team Spec 工作空间

`team-spec/` 是技能安装到业务项目后的运行时工作空间，不是本技能库需要提交的业务产物。不要在本仓库沉淀真实需求、PRD、风险报告或工程 issue。

技能运行时，所有产物应统一写入目标项目根目录下的 `team-spec/`。阶段拥有独立工作空间：

- `team-spec/spec/`：规格阶段产物，包括 `CONTEXT.md`、`decisions/`、`refine/`、`reviews/`。
- `team-spec/prd/`：PRD 固化产物，是需求到工程的正式交接边界。
- `team-spec/issues/`：PRD 拆解后的工程 issue 草稿。

每个需求使用唯一 slug 串联全流程，格式为 `{yyyy-mm-dd}-{short-english-slug}`。例如：`team-spec/spec/refine/2026-05-10-export-filter.md`、`team-spec/spec/reviews/2026-05-10-export-filter.md`、`team-spec/prd/2026-05-10-export-filter.md`、`team-spec/issues/2026-05-10-export-filter/`。

下游技能应优先读取上游阶段工作空间。例如 `team-prd-to-issues` 默认以 `team-spec/prd/{slug}.md` 为主输入，评审报告、规格上下文和产品决策只能作为参考输入。

## 构建、测试与开发命令

当前仓库是 Markdown 技能库，没有构建系统和自动化测试配置。

所有 shell 命令都必须通过 `rtk` 执行：

- `rtk find skills -maxdepth 4 -type f`：列出技能文件。
- `rtk find team-spec -maxdepth 4 -type f`：列出技能产物。
- `rtk sed -n '1,120p' skills/product/team-spec-refine/SKILL.md`：查看技能内容。
- `rtk git status --short`：查看本地变更。
- `rtk git diff`：提交前检查修改。

## 编写风格与命名规范

所有技能内容使用 Markdown。说明应简洁、可执行，并聚焦该技能的实际工作流。

- 技能目录名必须与 `SKILL.md` frontmatter 中的 `name` 完全一致。
- 目录名使用 kebab-case，例如 `team-spec-review`。
- 所有技能名必须以 `team-` 开头。
- 产品规格类技能使用 `team-spec-` 前缀，例如 `team-spec-refine`。
- 交付执行类技能可按输入产物使用 `team-prd-` 或 `team-issue-` 前缀，例如 `team-prd-to-issues`、`team-issue-implement`。
- 技术债类技能使用 `team-tech-debt-` 前缀，例如 `team-tech-debt-refine`。
- 必需技能文件命名为 `SKILL.md`。
- `SKILL.md` 必须包含 YAML frontmatter，并提供 `name`、`description`、`triggers`、`license` 和 `metadata`。
- `description` 必须同时包含中文和英文描述，便于 AI 在不同语言上下文中识别触发场景。
- `triggers` 是一个自然语言短语列表，用于提升技能的可发现性。AI 可通过匹配用户输入与 `triggers` 自动推荐合适的技能，无需用户知道技能名称。每个技能至少包含 3 条中文短语和 3 条英文短语，覆盖用户最常见的表达方式。
- 每个技能必须声明 `license: MIT`。
- 每个技能必须包含 `metadata.author: coolbeevip` 和 `metadata.version: "1.0"`。
- 每个技能必须声明 `## 输入物` 和 `## 输出物`，明确会读取哪些上游技能产物，以及会给哪些下游技能使用。
- 依赖上游产物的技能必须先确定唯一 slug 或明确文件路径；无法唯一判断时必须要求用户提供，不得猜测。
- 用户可见说明优先使用中文。
- 不要添加无关文档文件，例如 `README.md`，除非仓库规范发生变化。

最小 frontmatter 示例：

```yaml
---
name: team-spec-refine
description: 通过与用户反复确认来细化需求规格，适用于 PRD 前的规格打磨。Refine product specs through iterative user confirmation before PRD creation.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 细化需求
  - 打磨规格
  - 需求不清楚
  - refine spec
  - clarify requirements
  - spec is unclear
---
```

## 测试与校验

当前没有自动化测试。修改后应手动检查：

- frontmatter 是否存在且格式正确。
- `description` 是否清楚说明技能的触发场景。
- 被引用的辅助文件是否存在，且路径相对于技能目录有效。
- 工作流是否能被执行，不依赖隐藏假设。

## 提交与 Pull Request 规范

仓库目前没有提交历史，因此尚无既有提交规范。提交信息使用简洁的祈使句，例如：

- `Add requirement risk analysis skill`
- `Refine PRD generation workflow`

PR 应包含：

- 修改了哪些技能。
- 为什么修改。
- 是否新增触发条件或工作流变化。
- 如有相关 issue 或讨论，附上链接。

## Agent 专用说明

所有 shell 命令必须加 `rtk` 前缀。不要运行裸命令，例如不要运行 `git status`，应运行 `rtk git status --short`。
