# Repository Guidelines

## 项目结构与模块组织

本仓库是团队大语言模型技能库。技能统一放在标准目录 `skills/` 下，`skills/` 的一级子目录代表团队职责域。

- `skills/product/`：产品定义职责，包括产品概念白皮书、机器人场景需求发现、需求细化、规格评审和 PRD 固化。
- `skills/product/team-concept-whitepaper/`：用于在产品规划阶段定义产品机会、定位、价值、能力边界和演进方向，并编写产品概念白皮书。
- `skills/product/team-discovery-robotics/`：用于通过同步逐问或异步批量的引导启发式访谈，把具身智能、服务机器人或工业机器人的模糊想法转化为有边界、可验证的场景需求。
- `skills/product/team-spec-refine/`：用于与用户反复确认并打磨规格。
- `skills/product/team-spec-review/`：用于评审规格风险和 ready 状态。
- `skills/product/team-spec-to-prd/`：用于把 ready 的规格固化成 PRD。
- `skills/product/team-spec-archive/`：用于把已完成、废弃或暂停的 active 需求产物归档，避免新需求误改旧规格。
- `skills/config/`：跨流程运行时配置职责，包括 `team-spec/config.yml` 的初始化、校验和增量补全。
- `skills/config/team-config-init/`：用于集中创建、校验和安全补全语言、版本控制、访问策略及写作风格入口配置。
- `skills/codebase/`：代码库理解与说明职责，包括第三方代码库接手、源码走读、能力简报和自有项目 README 编写。
- `skills/codebase/team-codebase-onboarding/`：用于从第三方或陌生代码库提取可追溯的功能清单、架构说明和 AI 接手上下文。
- `skills/codebase/team-codebase-walk/`：用于基于 onboarding 产物和源码进行功能走读、问答和证据追踪。
- `skills/codebase/team-codebase-brief/`：用于把代码库事实转化为面向业务、产品和管理者的能力说明与影响分析。
- `skills/codebase/team-codebase-readme/`：用于为团队自行开发和维护的项目创建、审阅和优化 `README.md`。
- `skills/delivery/`：交付执行职责，包括 PRD 评审简报、Task 拆解、实现、验证和 Spec 级远端交付。
- `skills/delivery/team-prd-to-brief/`：用于把 AI 结构化 PRD 转换为需求、研发和项目管理可评审的演示文稿式简报。
- `skills/delivery/team-prd-to-tasks/`：用于把 PRD 拆解成可独立实现、验证并提交的工程 Task。
- `skills/delivery/team-task-batch-implement/`：用于在同一 Spec 分支按依赖顺序批量实现和验证多个 Task，并在用户逐个检查差异、确认后提交。
- `skills/delivery/team-task-implement/`：用于按行为测试和 TDD 循环实现单个 Task，验证后等待用户检查差异并确认，再形成一个本地 commit。
- `skills/delivery/team-task-verify/`：用于验证单个 Task 实现是否满足验收标准、PRD 和 commit 边界。
- `skills/delivery/team-spec-create-issue-github/`：用于把完整 Spec 创建或同步为一个 GitHub Issue，Tasks 作为 checklist。
- `skills/delivery/team-spec-create-issue-gitlab/`：用于把完整 Spec 创建或同步为一个 GitLab Issue，Tasks 作为 checklist。
- `skills/delivery/team-spec-create-pr-github/`：用于推送 Spec 共享分支并为全部 Task commits 创建一个 GitHub Pull Request。
- `skills/delivery/team-spec-create-mr-gitlab/`：用于推送 Spec 共享分支并为全部 Task commits 创建一个 GitLab Merge Request。
- `skills/tech-debt/`：技术债治理职责，包括技术债分析、细化、评审和工程拆解。
- `skills/tech-debt/team-tech-debt-analyze/`：用于对项目或模块进行只读技术债分析，输出证据化债务候选清单。
- `skills/tech-debt/team-tech-debt-refine/`：用于把模糊技术债诉求细化为可评审规格。
- `skills/tech-debt/team-tech-debt-review/`：用于评审技术债风险、优先级和可执行性。
- `skills/tech-debt/team-tech-debt-to-tasks/`：用于把已评审技术债拆解为工程 Task。
- `skills/harness/`：从已归档 spec 中提炼可复用规则和决策模式，独立于主线交付流程。
- `skills/harness/team-archive-distill/`：用于从 `team-spec/archive/` 下已归档的 spec 中提取决策模式和工程惯例，高度抽象为规则后写入 `AGENTS.md`。
- `skills/writing/`：跨产品、代码库、交付和技术债流程复用的写作职责，包括公共语言风格和代码注释规范。
- `skills/writing/team-writing-style/`：用于建立和维护目标项目的统一写作风格，通过 `team-spec/config.yml` 为其他技能提供单一公共规则入口。

每个技能目录必须包含 `SKILL.md`。只有当辅助文件被 `SKILL.md` 明确引用时才添加，例如 `CONTEXT-FORMAT.md`、`DECISION-FORMAT.md`。

`team-spec/config.yml` 的结构、初始化、校验和增量补全统一由 `team-config-init` 负责。其他技能只读取配置并声明当前操作所需字段；配置文件不存在或缺少必需字段时，先使用 `team-config-init`，不得在业务技能中复制完整配置模式或自行回写配置。纯对话、只读分析和不依赖稳定配置的预览不因配置缺失而阻塞。

如果技能需要稳定执行 API 调用、文件解析、批量发布、幂等检查、拓扑排序或其他容易因大模型临时生成代码而出错的操作，应在技能目录下新增 `scripts/` 目录沉淀固定脚本。脚本必须由 `SKILL.md` 明确引用，且路径按相对 `SKILL.md` 的形式书写，例如 `./scripts/publish_github_issues.py`，不要在技能说明中硬编码本仓库源码路径。

## Team Spec 工作空间

`team-spec/` 是技能安装到业务项目后的运行时工作空间，不是本技能库需要提交的业务产物。不要在本仓库沉淀真实需求、PRD、风险报告或工程 Task。

技能运行时，所有产物应统一写入目标项目根目录下的 `team-spec/`。`team-spec/active/` 是所有尚未归档需求的集合，不再表示唯一活跃需求；单个需求工作区必须放在 `team-spec/active/{slug}/`。`team-spec/archive/` 保存已完成、废弃或暂停的历史需求。

- `team-spec/CONTEXT.md`：跨多个需求复用的全局产品语境，包括规范术语、角色、通用流程和通用业务规则。
- `team-spec/STYLE.md`：可选的项目级公共写作风格，约束文档、用户可见说明和代码注释；路径由 `team-spec/config.yml` 的 `writing_style.guide` 指定。
- `team-spec/decisions/`：跨多个需求长期有效的产品决策记录，仅在决策影响后续多个需求且反悔成本较高时创建。
- `team-spec/active/{slug}/spec/`：单个需求的规格阶段产物，包括可选的机器人场景发现文档 `discovery.md`，以及 `CONTEXT.md`、`decisions/`、`refine.md`、`reviews.md`。
- `team-spec/active/{slug}/concept/`：单个产品或产品体系的概念阶段产物，默认白皮书为 `whitepaper.md`，作为规格细化和后续 PRD 的上游输入。
- `team-spec/active/{slug}/prd/`：单个需求的 PRD 固化产物，是需求到工程的正式交接边界，包括 `prd.md` 与可选 `brief.md`。
- `team-spec/active/{slug}/tasks/`：单个需求 PRD 或技术债规格拆解后的工程 Task。
- `team-spec/active/{slug}/DELIVERY.md`：可选的 Spec 级交付记录，包括共享分支、远端 Issue、Task/commit 映射和 PR/MR；不得加入产品代码 commit。
- `team-spec/active/{slug}/design/`：单个需求的功能设计说明书，默认文件为 `functional-design.md`。
- `team-spec/active/{slug}/STATUS.md`：可选状态文件，只记录整个工作区的生命周期状态，不记录阶段评审结果或单个 Task 的交付状态。
- `team-spec/archive/{slug}/`：单个历史需求的归档目录，包括 `spec/`、`prd/`、`tasks/`、`design/`、`DELIVERY.md`、`STATUS.md` 和 `ARCHIVE.md`。

### 状态合同

所有机器可读状态使用小写 kebab-case。状态按写入对象分为三类，不得混用：

1. 工作区生命周期状态：写入 `team-spec/active/{slug}/STATUS.md`。产品需求链路使用 `concept-drafting`、`concept-review`、`concept-ready`、`refining`、`spec-ready`、`prd-ready`、`implementing`、`paused`、`blocked`；技术债链路使用 `debt-analyzed`、`debt-refining`、`debt-ready`、`implementing`、`paused`、`blocked`。
2. 阶段评审结果：写入 `team-spec/active/{slug}/spec/reviews.md` 或其他阶段报告，不写入工作区 `STATUS.md`。统一使用 `ready`、`needs-refinement`、`blocked`。
3. Task 状态：写入对应 Task 文件，不写入工作区 `STATUS.md`。统一使用 `draft`、`implementing`、`needs-changes`、`blocked`、`verified`、`committed`。`pr-created`、`mr-created` 不属于 Task 状态；Spec 级远端信息写入 `DELIVERY.md`。

同一个 `blocked` 可以出现在不同对象中，但只表示该对象被阻塞；读取方必须结合文件位置判断是工作区、阶段评审还是 Task 被阻塞。用户可见回复可以使用自然语言，写入文件的状态值必须使用上述机器值。

每个需求使用唯一 slug 串联全流程，格式为 `{yyyy-mm-dd}-{short-english-slug}`。例如：`team-spec/active/2026-05-10-export-filter/concept/whitepaper.md`、`team-spec/active/2026-05-10-export-filter/spec/discovery.md`、`team-spec/active/2026-05-10-export-filter/spec/refine.md`、`team-spec/active/2026-05-10-export-filter/spec/reviews.md`、`team-spec/active/2026-05-10-export-filter/prd/prd.md`、`team-spec/active/2026-05-10-export-filter/tasks/`。

同一个 slug 的所有 Task 必须在同一个 `{slug}` 本地分支上开发，分支名不得添加 `spec/` 前缀。每个 Task 验证通过后，必须先保持未暂存状态供用户检查实际差异；只有用户明确确认后才形成一个逻辑 commit。全部必需 Task 都达到 `committed` 后，才允许为该 Spec 一次性创建一个 PR 或 MR。

开始新需求前，`team-spec-refine` 只需检查目标 slug 是否已存在。若 `team-spec/active/` 下有其他 slug，不得要求用户归档；应允许多个未归档需求并行存在。只有当用户请求无法唯一确定 slug 或目标文件路径时，才要求用户指定 slug、继续某个已有需求或创建新的 slug。

下游技能应默认读取全局上下文和同一 slug 的上游阶段产物。例如 `team-spec-refine` 在同一 slug 存在 `spec/discovery.md` 时必须读取并继承已确认的场景结论；`team-prd-to-tasks` 默认以 `team-spec/active/{slug}/prd/prd.md` 为主输入，并参考 `team-spec/CONTEXT.md`、`team-spec/decisions/`、`team-spec/active/{slug}/spec/CONTEXT.md`、`team-spec/active/{slug}/spec/decisions/` 和评审报告。`team-spec/archive/` 默认只读；除非用户显式指定归档 slug 或文件路径，否则技能不得扫描或修改 archive 内容。

## 构建、测试与开发命令

当前仓库是 Markdown 技能库，没有构建系统。仓库使用 pre-commit 执行技能结构、暂存区空白、YAML、文件结尾和合并冲突标记检查；GitHub Actions 在 main push 和 pull request 上运行同一套检查。

所有 shell 命令都必须通过 `rtk` 执行：

- `rtk find skills -maxdepth 4 -type f`：列出技能文件。
- `rtk find team-spec -maxdepth 4 -type f`：列出技能产物。
- `rtk sed -n '1,120p' skills/product/team-spec-refine/SKILL.md`：查看技能内容。
- `rtk git status --short`：查看本地变更。
- `rtk git diff`：提交前检查修改。
- `rtk pre-commit run --all-files`：运行完整仓库检查。
- `rtk python3 scripts/check_skills.py`：只运行全部技能结构检查。
- `rtk python3 -m unittest discover -s tests -v`：运行 Spec/Task/PR/MR 交付工作流回归测试。

## 编写风格与命名规范

所有技能内容使用 Markdown。说明应简洁、可执行，并聚焦该技能的实际工作流。

- 技能目录名必须与 `SKILL.md` frontmatter 中的 `name` 完全一致。
- 目录名使用 kebab-case，例如 `team-spec-review`。
- 所有技能名必须以 `team-` 开头。
- 产品规格类技能使用 `team-spec-` 前缀，例如 `team-spec-refine`。
- 领域需求发现技能使用 `team-discovery-` 前缀，例如 `team-discovery-robotics`。
- 交付执行类技能按输入和聚合边界使用 `team-prd-`、`team-task-` 或 `team-spec-` 前缀，例如 `team-prd-to-tasks`、`team-task-implement`、`team-spec-create-pr-github`。
- 技术债类技能使用 `team-tech-debt-` 前缀，例如 `team-tech-debt-refine`。
- 归档决策提炼类技能使用 `team-archive-` 前缀，例如 `team-archive-distill`。
- 跨流程写作类技能使用 `team-writing-` 前缀，例如 `team-writing-style`。
- 必需技能文件命名为 `SKILL.md`。
- `SKILL.md` 必须包含 YAML frontmatter，并提供 `name`、`description`、`triggers`、`license` 和 `metadata`。
- `description` 必须同时包含中文和英文描述，便于 AI 在不同语言上下文中识别触发场景。
- `triggers` 是一个自然语言短语列表，用于提升技能的可发现性。AI 可通过匹配用户输入与 `triggers` 自动推荐合适的技能，无需用户知道技能名称。每个技能至少包含 3 条中文短语和 3 条英文短语，覆盖用户最常见的表达方式。
- 每个技能必须声明 `license: MIT`。
- 每个技能必须包含 `metadata.author: coolbeevip` 和 `metadata.version: "1.0"`。
- 每个技能必须声明 `## 输入物` 和 `## 输出物`，明确会读取哪些上游技能产物，以及会给哪些下游技能使用。
- 依赖上游产物的技能必须先确定唯一 slug 或明确文件路径；无法唯一判断时必须要求用户提供，不得猜测。
- 用户可见说明优先使用中文。
- 会生成或改写文档、Task、Issue/PR/MR 正文、用户可见说明或代码注释的技能，必须读取 `team-spec/config.yml`；如果 `writing_style.guide` 指向存在的文件，写作前必须读取并应用。公共规则只保存在风格指南中，各技能只保留本产物特有的补充规则。
- 公共风格不得覆盖格式、机器状态、安全、证据和验收合同。风格指南缺失时不阻塞业务技能，也不得猜测路径；需要建立或调整统一风格时使用 `team-writing-style`。
- 不要添加无关文档文件，例如 `README.md`，除非仓库规范发生变化。

### 辅助脚本规范

当技能需要 `scripts/` 辅助脚本时，遵守以下规则：

- `scripts/` 只能放在具体技能目录内，例如 `skills/delivery/team-spec-create-issue-github/scripts/`。
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
- 各技能如需使用公共辅助代码，应在本技能自己的 `scripts/` 目录下放置 `_team_common.py` 副本，例如 `skills/delivery/team-spec-create-mr-gitlab/scripts/_team_common.py`。
- 修改公共辅助代码时，只修改根目录 `scripts/_team_common.py`，然后执行 `rtk python3 scripts/check_vendored_common.py`，用根目录源文件覆盖所有不一致的技能目录副本。
- 提交前执行 `rtk python3 scripts/check_vendored_common.py --check`，确保所有 vendored `_team_common.py` 与根目录源文件一致。
- 根目录 `scripts/check_vendored_common.py` 只用于仓库维护；技能 `SKILL.md` 中不得把它写成业务项目运行时依赖。
- `_team_common.py` 只放跨技能稳定基础能力，例如 HTTP 请求、`no_proxy` 处理、请求调试输出和通用错误包装；不要放 Task、Issue、PR、MR 的业务流程逻辑。

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

提交前必须执行：

```bash
rtk pre-commit run --all-files
```

自动检查覆盖 frontmatter、双语 description、许可、作者、版本、触发词、标准章节、重复标题、Spec 交付工作流、YAML、空白和合并冲突标记。

自动检查不能替代语义验证。修改后仍应人工确认：

- `description` 和 triggers 是否准确覆盖真实触发场景。
- 被引用的辅助文件是否存在，且路径相对于技能目录有效。
- 输入、输出、状态和下游衔接是否一致。
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
