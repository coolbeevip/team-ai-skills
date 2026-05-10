# Repository Guidelines

## 项目结构与模块组织

本仓库是团队大语言模型技能库。技能统一放在标准目录 `skills/` 下，`skills/` 的一级子目录代表工作流领域。

- `skills/spec/`：规格细化、评审和 PRD 固化相关技能。
- `skills/spec/team-spec-refine/`：用于与用户反复确认并打磨规格。
- `skills/spec/team-spec-review/`：用于评审规格风险和 ready 状态。
- `skills/spec/team-spec-to-prd/`：用于把 ready 的规格固化成 PRD。
- `skills/engineering/`：工程阶段技能。
- `skills/engineering/team-prd-to-issues/`：用于把 PRD 拆解成可独立领取的工程 issue。
- `skills/engineering/team-issue-start/`：用于同步主干、检查依赖并创建 issue 分支。
- `skills/engineering/team-issue-implement/`：用于按行为测试和 TDD 循环实现单个 issue。
- `skills/engineering/team-issue-verify/`：用于验证单个 issue 实现是否满足验收标准和 PRD。
- `skills/engineering/team-issue-pr/`：用于验证通过后提交、推送并创建 PR。

每个技能目录必须包含 `SKILL.md`。只有当辅助文件被 `SKILL.md` 明确引用时才添加，例如 `CONTEXT-FORMAT.md`、`DECISION-FORMAT.md`。

## Team Spec 工作空间

`team-spec/` 是技能安装到业务项目后的运行时工作空间，不是本技能库需要提交的业务产物。不要在本仓库沉淀真实需求、PRD、风险报告或工程 issue。

技能运行时，所有产物应统一写入目标项目根目录下的 `team-spec/`。阶段拥有独立工作空间：

- `team-spec/spec/`：规格阶段产物，包括 `CONTEXT.md`、`decisions/`、`refinements/`、`reviews/`。
- `team-spec/prd/`：PRD 固化产物，是需求到工程的正式交接边界。
- `team-spec/issues/`：PRD 拆解后的工程 issue 草稿。

每个需求使用唯一 slug 串联全流程，格式为 `{yyyy-mm-dd}-{short-english-slug}`。例如：`team-spec/spec/refinements/2026-05-10-export-filter.md`、`team-spec/spec/reviews/2026-05-10-export-filter.md`、`team-spec/prd/2026-05-10-export-filter.md`、`team-spec/issues/2026-05-10-export-filter/`。

下游技能应优先读取上游阶段工作空间。例如 `team-prd-to-issues` 默认以 `team-spec/prd/{slug}.md` 为主输入，评审报告、规格上下文和产品决策只能作为参考输入。

## 构建、测试与开发命令

当前仓库是 Markdown 技能库，没有构建系统和自动化测试配置。

所有 shell 命令都必须通过 `rtk` 执行：

- `rtk find skills -maxdepth 4 -type f`：列出技能文件。
- `rtk find team-spec -maxdepth 4 -type f`：列出技能产物。
- `rtk sed -n '1,120p' skills/spec/team-spec-refine/SKILL.md`：查看技能内容。
- `rtk git status --short`：查看本地变更。
- `rtk git diff`：提交前检查修改。

## 编写风格与命名规范

所有技能内容使用 Markdown。说明应简洁、可执行，并聚焦该技能的实际工作流。

- 技能目录名必须与 `SKILL.md` frontmatter 中的 `name` 完全一致。
- 目录名使用 kebab-case，例如 `team-spec-review`。
- 所有技能名必须以 `team-` 开头。
- 规格类技能使用 `team-spec-` 前缀，例如 `team-spec-refine`。
- 工程阶段技能可按输入产物使用 `team-prd-` 或 `team-issue-` 前缀，例如 `team-prd-to-issues`、`team-issue-implement`。
- 必需技能文件命名为 `SKILL.md`。
- `SKILL.md` 必须包含 YAML frontmatter，并提供 `name`、`description`、`license` 和 `metadata`。
- `description` 必须同时包含中文和英文描述，便于 AI 在不同语言上下文中识别触发场景。
- 每个技能必须声明 `license: MIT`。
- 每个技能必须包含 `metadata.author: coolbeevip` 和 `metadata.version: "1.0"`。
- 每个技能必须声明 `## 输入物` 和 `## 输出物`，明确会读取哪些上游技能产物，以及会给哪些下游技能使用。
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
