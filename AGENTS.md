# Repository Guidelines

## 项目结构与模块组织

本仓库是团队大语言模型技能库。技能统一放在标准目录 `skills/` 下，`skills/` 的一级子目录代表团队角色或岗位类型。

- `skills/requirements/`：面向产品经理、需求负责人和业务方的需求类技能。
- `skills/requirements/team-req-clarify/`：用于澄清模糊需求，并沉淀需求上下文。
- `skills/requirements/team-req-to-prd/`：用于把已澄清需求整理成 PRD。
- `skills/requirements/team-req-risk-analysis/`：用于检查需求、PRD、上线前计划中的产品、交付、数据、合规和运营风险。
- `skills/engineering/`：预留给软件工程师的研发类技能。
- `skills/engineering/team-eng-to-issues/`：用于把 PRD、技术方案或开发计划拆解成可独立领取的工程 issue。

每个技能目录必须包含 `SKILL.md`。只有当辅助文件被 `SKILL.md` 明确引用时才添加，例如 `CONTEXT-FORMAT.md`、`DECISION-FORMAT.md`。

## Team Spec 工作空间

所有技能产物统一写入项目根目录下的 `team-spec/`。角色拥有独立工作空间：

- `team-spec/requirements/`：需求角色产物，包括 `CONTEXT.md`、`decisions/`、`prd/`、`risks/`。
- `team-spec/engineering/`：工程角色产物，包括 `issues/`。

下游技能应优先读取上游角色工作空间。例如 `team-eng-to-issues` 默认从 `team-spec/requirements/` 读取 PRD、风险报告、需求上下文和产品决策。

## 构建、测试与开发命令

当前仓库是 Markdown 技能库，没有构建系统和自动化测试配置。

所有 shell 命令都必须通过 `rtk` 执行：

- `rtk find skills -maxdepth 4 -type f`：列出技能文件。
- `rtk find team-spec -maxdepth 4 -type f`：列出技能产物。
- `rtk sed -n '1,120p' skills/requirements/team-req-clarify/SKILL.md`：查看技能内容。
- `rtk git status --short`：查看本地变更。
- `rtk git diff`：提交前检查修改。

## 编写风格与命名规范

所有技能内容使用 Markdown。说明应简洁、可执行，并聚焦该技能的实际工作流。

- 技能目录名必须与 `SKILL.md` frontmatter 中的 `name` 完全一致。
- 目录名使用 kebab-case，例如 `team-req-risk-analysis`。
- 所有技能名必须以 `team-` 开头。
- 需求人员技能必须以 `team-req-` 开头，例如 `team-req-clarify`。
- 软件工程师技能建议以 `team-eng-` 开头，例如 `team-eng-code-review`。
- 必需技能文件命名为 `SKILL.md`。
- `SKILL.md` 必须包含 YAML frontmatter，并提供 `name`、`description`、`license` 和 `metadata`。
- `description` 必须同时包含中文和英文描述，便于 AI 在不同语言上下文中识别触发场景。
- 每个技能必须声明 `license: MIT`。
- 每个技能必须包含 `metadata.author: coolbeevip` 和 `metadata.version: "1.0"`。
- 每个技能必须声明 `## 输入物` 和 `## 输出物`，明确会读取哪些上游技能产物，以及会给哪些下游技能使用。
- `skills/requirements/` 下的用户可见说明优先使用中文。
- 不要添加无关文档文件，例如 `README.md`，除非仓库规范发生变化。

最小 frontmatter 示例：

```yaml
---
name: team-req-clarify
description: 用结构化追问澄清模糊需求，适用于 PRD 前的需求访谈和边界确认。Clarify vague requirements through structured questioning before PRD creation, including scope, terminology, and acceptance boundaries.
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
