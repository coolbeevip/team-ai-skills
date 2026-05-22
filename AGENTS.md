# Repository Guidelines

## 项目结构与模块组织

本仓库是团队大语言模型技能库。技能统一放在标准目录 `skills/` 下，`skills/` 的一级子目录代表团队职责域。

- `skills/product/`：产品定义职责，包括需求细化、规格评审和 PRD 固化。
- `skills/product/team-spec-refine/`：用于与用户反复确认并打磨规格。
- `skills/product/team-spec-review/`：用于评审规格风险和 ready 状态。
- `skills/product/team-spec-to-prd/`：用于把 ready 的规格固化成 PRD。
- `skills/product/team-spec-archive/`：用于把已完成、废弃或暂停的 active 需求产物归档，避免新需求误改旧规格。
- `skills/architecture/`：架构与方案设计职责。
- `skills/architecture/team-spec-to-functional-design/`：用于基于需求规格与代码生成企业级功能设计说明书。
- `skills/harness/`：Codex harness 职责，包括项目级 Codex 工作环境、知识地图、验证命令和失败反馈闭环。
- `skills/harness/team-codex-harness/`：用于随真实代码和工程演进维护 `AGENTS.md`、项目任务地图、验证命令和 Codex 失败反馈闭环。
- `skills/delivery/`：交付执行职责，包括 issue 拆解、发布、实现和验证。
- `skills/delivery/team-prd-to-issues/`：用于把 PRD 拆解成可独立领取的工程 issue。
- `skills/delivery/team-github-issue-publish/`：用于把本地 issue 草稿发布到 GitHub Issues，支持整目录批量发布或指定单个 issue。
- `skills/delivery/team-gitlab-issue-publish/`：用于把本地 issue 草稿发布到 GitLab Issues，支持整目录批量发布或指定单个 issue。
- `skills/delivery/team-issue-implement/`：用于按行为测试和 TDD 循环实现单个 issue。
- `skills/delivery/team-issue-verify/`：用于验证单个 issue 实现是否满足验收标准和 PRD。
- `skills/delivery/team-gitlab-mr-create/`：用于推送已完成的 issue 分支并创建关联 issue 的 GitLab Merge Request。
- `skills/delivery/team-github-pr-create/`：用于推送已完成的 issue 分支并创建关联 issue 的 GitHub Pull Request。
- `skills/tech-debt/`：技术债治理职责，包括技术债细化、评审和工程拆解。
- `skills/tech-debt/team-tech-debt-refine/`：用于把模糊技术债诉求细化为可评审规格。
- `skills/tech-debt/team-tech-debt-review/`：用于评审技术债风险、优先级和可执行性。
- `skills/tech-debt/team-tech-debt-to-issues/`：用于把已评审技术债拆解为工程 issue。
- `skills/documentation/`：文档质量与格式规范职责。
- `skills/documentation/team-prd-to-alignment/`：用于把 AI 结构化 PRD 转换为需求、研发和项目管理可评审的演示文稿式对齐材料。
- `skills/documentation/team-md-style-check/`：用于检查 Markdown 是否符合飞书文档导入后的样式映射规则。

每个技能目录必须包含 `SKILL.md`。只有当辅助文件被 `SKILL.md` 明确引用时才添加，例如 `CONTEXT-FORMAT.md`、`DECISION-FORMAT.md`。

如果技能需要稳定执行 API 调用、文件解析、批量发布、幂等检查、拓扑排序或其他容易因大模型临时生成代码而出错的操作，应在技能目录下新增 `scripts/` 目录沉淀固定脚本。脚本必须由 `SKILL.md` 明确引用，且路径按相对 `SKILL.md` 的形式书写，例如 `./scripts/publish_github_issues.py`，不要在技能说明中硬编码本仓库源码路径。

## Team Spec 工作空间

`team-spec/` 是技能安装到业务项目后的运行时工作空间，不是本技能库需要提交的业务产物。不要在本仓库沉淀真实需求、PRD、风险报告或工程 issue。

技能运行时，所有产物应统一写入目标项目根目录下的 `team-spec/`。`team-spec/active/` 是当前唯一活跃需求工作区，`team-spec/archive/` 保存已完成、废弃或暂停的历史需求。

- `team-spec/active/spec/`：当前需求的规格阶段产物，包括 `CONTEXT.md`、`decisions/`、`refine/`、`reviews/`。
- `team-spec/active/prd/`：当前需求的 PRD 固化产物，是需求到工程的正式交接边界。
- `team-spec/active/issues/`：当前需求 PRD 拆解后的工程 issue 草稿。
- `team-spec/active/design/`：当前需求的功能设计说明书。
- `team-spec/archive/{slug}/`：单个历史需求的归档目录，包括 `spec/`、`prd/`、`issues/`、`design/` 和 `ARCHIVE.md`。

每个需求使用唯一 slug 串联全流程，格式为 `{yyyy-mm-dd}-{short-english-slug}`。例如：`team-spec/active/spec/refine/2026-05-10-export-filter.md`、`team-spec/active/spec/reviews/2026-05-10-export-filter.md`、`team-spec/active/prd/2026-05-10-export-filter.md`、`team-spec/active/issues/2026-05-10-export-filter/`。

开始新需求前，`team-spec-refine` 必须检查 `team-spec/active/` 是否已有未归档需求产物。如果 active 中存在其他 slug，应要求用户继续旧需求或先使用 `team-spec-archive` 归档，不得默认修改旧规格。

下游技能应默认只读取 `team-spec/active/` 中的上游阶段产物。例如 `team-prd-to-issues` 默认以 `team-spec/active/prd/{slug}.md` 为主输入，评审报告、规格上下文和产品决策只能作为参考输入。`team-spec/archive/` 默认只读；除非用户显式指定归档 slug 或文件路径，否则技能不得扫描或修改 archive 内容。

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
- Codex harness 类技能使用 `team-codex-` 前缀，例如 `team-codex-harness`。
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

### 辅助脚本规范

当技能需要 `scripts/` 辅助脚本时，遵守以下规则：

- `scripts/` 只能放在具体技能目录内，例如 `skills/delivery/team-github-issue-publish/scripts/`。
- 脚本用于沉淀确定性流程，例如远端 API 操作、批量文件处理、格式转换、依赖排序、幂等检查和回写状态。
- `SKILL.md` 必须说明脚本用途、主要参数、默认 dry-run 行为、正式执行开关和安全要求。
- `SKILL.md` 内引用脚本时必须使用相对 `SKILL.md` 的路径，例如 `./scripts/publish_gitlab_issues.py`。
- 如果给出 shell 命令示例，不要假设业务项目存在本技能库源码路径；应使用 `{skill_dir}/scripts/{script_name}` 或明确说明需要先解析当前技能目录。
- 脚本应优先使用标准库或目标项目已有依赖，避免为技能引入额外安装步骤；如必须依赖外部包，必须在 `SKILL.md` 写清安装和失败处理。
- 脚本不得把 token、密钥或用户数据写入仓库配置；敏感信息必须从环境变量或运行时参数读取，并且不得回显。
- 修改脚本后应至少执行语法检查或 `--help` 等轻量验证，并在最终回复中说明验证结果。

### Vendored 公共脚本规范

为了保持技能目录可独立复制，技能运行时不得依赖仓库根目录的公共 Python 模块。跨多个技能复用的稳定辅助代码采用 vendored copy 方式维护：

- 根目录 `scripts/_team_common.py` 是公共辅助代码的唯一源文件。
- 各技能如需使用公共辅助代码，应在本技能自己的 `scripts/` 目录下放置 `_team_common.py` 副本，例如 `skills/delivery/team-gitlab-mr-create/scripts/_team_common.py`。
- 修改公共辅助代码时，只修改根目录 `scripts/_team_common.py`，然后执行 `rtk python3 scripts/check_vendored_common.py`，用根目录源文件覆盖所有不一致的技能目录副本。
- 提交前执行 `rtk python3 scripts/check_vendored_common.py --check`，确保所有 vendored `_team_common.py` 与根目录源文件一致。
- 根目录 `scripts/check_vendored_common.py` 只用于仓库维护；技能 `SKILL.md` 中不得把它写成业务项目运行时依赖。
- `_team_common.py` 只放跨技能稳定基础能力，例如 HTTP 请求、`no_proxy` 处理、请求调试输出和通用错误包装；不要放 issue、PR、MR 的业务流程逻辑。

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
