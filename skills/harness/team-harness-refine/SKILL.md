---
name: team-harness-refine
description: 规范项目级 agent harness 的 AGENTS.md 入口和深层知识目录命名，再基于真实代码、开发任务和失败反馈检查这些知识是否能帮助 agent 理解项目、执行任务和完成验证。Plan AGENTS.md entry points and deep harness knowledge directory naming, then verify against real code, development tasks, and failure feedback that the knowledge helps agents understand the project, execute tasks, and validate work.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 细化 harness
  - 维护 AGENTS.md
  - 维护 CLAUDE.md
  - 改进 agent 工作环境
  - 让 agent 更好理解项目
  - 沉淀 agent 失败经验
  - refine harness
  - maintain AGENTS.md
  - maintain CLAUDE.md
  - improve agent harness
  - document agent workflow
  - keep harness updated
---

# Harness 细化

这个技能用于设计、建立和持续更新项目级 agent harness 提示词体系。第一职责是规范 `AGENTS.md` / `CLAUDE.md` 入口和 harness 深层知识的目录、文件名、职责边界与索引关系；第二职责是根据真实代码事实、开发任务和失败反馈检查这些知识是否真的能帮助 agent 理解项目、执行任务、运行验证、处理失败并沉淀经验。

本技能可以在项目初始接入 agent 时执行，也可以在工程演进、测试命令变化、架构调整、开发失败或交付事故后反复执行。每次执行都必须先保证 harness 结构清晰、命名稳定、入口可发现，再用真实代码、真实任务或真实失败反馈校验内容，而不是只生成模板。

Harness 维护是一种持续活动，不是一次性建档。每次真实任务暴露出 agent 理解、执行、验证或恢复失败的缺口，都应回到本技能更新入口、目录、规则或深层知识。

## 运行时配置

Harness 独立于需求、PRD、issue 拆解或技术债流程，不读取、不创建、不修改这些流程的运行时工作区。

Harness 目录识别规则：

- 优先从现有 `AGENTS.md`、`CLAUDE.md` 或其他 agent 入口文件中识别已链接的 harness 目录。
- 如果项目没有现成目录，应使用项目内独立目录保存 harness 文档；目录必须是相对项目根目录的路径，不应是绝对路径，不应位于需求、PRD、issue 或归档工作区下。
- 如果无法从现有文件唯一判断目录，必须只问用户一个问题来确认 harness 目录；不要为了配置目录展开多轮访谈。
- 后续所有 harness 文档路径必须由确认后的目录拼接得到，本文用 `{harness_dir}/` 表示。

执行要求：

- 对话回复与 harness 文档（`AGENTS.md`、`CLAUDE.md`、`{harness_dir}/` 下内容）默认沿用项目现有语言；若无法判断，优先使用用户本轮语言。
- 用户临时切换语言时，本次立即生效；只有用户明确要求持久化语言偏好时，才写入 harness 文档。

## 输入物

- 当前项目中的 `AGENTS.md`、`CLAUDE.md` 或其他 agent 指令文件（如存在）。
- 当前项目中的 `README.md`、`docs/`、架构文档、开发手册、测试说明和运维说明。
- 真实代码、目录结构、构建配置、测试配置、脚本、CI 配置和本地开发工具。
- 最近的工程 issue、PR、失败测试、CI 日志、上线事故、人工修复记录或 agent 执行卡点。
- 已有 `{harness_dir}/` 工作区（如存在）。

如果用户没有提供明确范围，应先判断是要建立新 harness、审查现有 harness，还是根据某次开发任务或失败案例更新 harness。无法唯一判断时，只问一个最关键的问题，不要一次性展开访谈。

## 输出物

本技能默认必须产生或更新目标项目中的持久化输出物。除非用户明确说“只分析、不改文件”，否则不能只在对话中给建议后结束。

- 更新后的项目级 agent 入口文件：
  - `AGENTS.md`
  - `CLAUDE.md`（仅当项目使用 Claude 或用户要求时维护）
- `{harness_dir}/index.md`：harness 总入口、目录规划、文件命名规范和文档地图。
- `{harness_dir}/structure.md`：当 harness 文档较多或项目需要稳定约束时，用于明确目录职责、命名规则、增删文档标准和入口链接规则。
- `{harness_dir}/commands.md`：常用开发、测试、检查和调试命令。
- `{harness_dir}/verification.md`：不同变更类型对应的验证策略和最低验证命令。
- `{harness_dir}/architecture-map.md`：agent 需要理解的模块边界、关键路径和代码入口。
- `{harness_dir}/coding-rules.md`：项目特有的编码约束、提交约束和禁止事项。
- `{harness_dir}/review-rubric.md`：实现完成后自查和评审关注点。
- `{harness_dir}/known-failures.md`：已知失败模式、复现方式、规避方式和修复记录。

如果项目已有其他文档结构，可以作为输入和引用来源；但本技能生成或维护的渐进式 harness 提示词材料必须放在确认后的 `{harness_dir}/` 下，并保持 `AGENTS.md` 或 `CLAUDE.md` 能指向这些材料。

输出分层：

- Harness 结构层：`AGENTS.md`、`CLAUDE.md`、`{harness_dir}/index.md`、必要时的 `{harness_dir}/structure.md`，用于定义入口、目录、文件名、索引和职责边界。
- Harness 知识层：`{harness_dir}/commands.md`、`verification.md`、`architecture-map.md`、`coding-rules.md`、`review-rubric.md`、`known-failures.md` 等，用于改善 agent 如何理解项目、运行命令和处理失败。

落盘规则：

- 新建 harness：先确认 `{harness_dir}`，然后至少创建或更新 `AGENTS.md`，并创建 `{harness_dir}/index.md`、`commands.md`、`verification.md` 中与本轮证据相关的文件。
- 规划目录：至少更新 `AGENTS.md` 或 `{harness_dir}/index.md`，必要时更新 `{harness_dir}/structure.md`。
- 审查现有 harness：至少更新 `{harness_dir}/index.md`、`structure.md` 或被审查后确认需要修订的深层知识文件之一。
- 根据失败案例更新 harness：至少更新 `{harness_dir}/known-failures.md`；如果失败来自命令、验证、架构地图或规则缺口，还应同步更新对应文档。
- 根据开发任务更新 harness：至少更新与任务相关的 `{harness_dir}/commands.md`、`{harness_dir}/verification.md`、`{harness_dir}/architecture-map.md`、`{harness_dir}/coding-rules.md` 或 `{harness_dir}/review-rubric.md` 之一。

## 核心原则

- `AGENTS.md` 和 `CLAUDE.md` 是入口地图，不是百科全书；它们应保持短小，指向更具体的文档。
- 先规范结构，再验证内容。目录、文件名、职责边界和索引关系不清楚时，必须先修结构，再补知识。
- harness 深层知识必须按 agent 任务路径组织，而不是按作者习惯堆文档。agent 应能从入口快速判断“本任务该读哪些文件”。
- 每个 harness 文件都必须有明确职责；如果两个文件职责重叠，应合并、改名或在 `index.md` / `structure.md` 中划清边界。
- 文件名应稳定、可预测、语义具体；避免 `misc.md`、`notes.md`、`tips.md` 这类无法表达用途的名称。
- harness 必须随工程演进持续更新。每次发现命令失效、上下文缺失、验证不足或失败模式重复出现，都应更新对应文档。
- harness 必须通过真实任务校验。不要只写“应该如何做”，要用现有代码、脚本或测试确认说明可执行。
- 优先记录可执行命令、判断标准和失败恢复方式，避免只写抽象原则。
- 不要把敏感信息、token、密钥、个人凭证或内部服务密码写入 harness 文档。
- 不要把所有架构细节塞进 agent 入口文件；复杂内容应放入 `{harness_dir}/`，必要时链接项目已有文档。
- 生成型 harness 文档必须标注来源命令、生成时间、刷新方式和是否允许手改。
- 外部参考资料可以本地化为 agent 可读摘要，但必须标注来源、抓取日期、许可或使用边界。
- 文档不应无限增长。过期、重复、职责不清或不再适用的 harness 内容应被合并、删除、改名或标注废弃原因。

## 工作流

1. 识别本轮目标：新建 harness、规划目录、审查现有 harness、根据开发任务更新 harness，或根据失败案例更新 harness。
2. 读取现有 `AGENTS.md`、`CLAUDE.md`、已有 harness 目录、项目文档、目录结构、构建配置、测试配置和脚本。
3. 先建立 harness 结构快照：入口文件是否短小，是否能找到 `{harness_dir}`，深层知识目录是否有稳定命名，文件职责是否互斥，索引是否能指导 agent 选择阅读路径。
4. 规划或修正 `AGENTS.md` / `CLAUDE.md` 与 `{harness_dir}/` 的目录和文件名：明确保留、合并、拆分、新增或废弃哪些 harness 文件。
5. 将目录规划写入 `{harness_dir}/index.md`；如果规则较复杂，再写入 `{harness_dir}/structure.md`。
6. 再建立 harness 内容快照：命令是否可执行，验证策略是否明确，架构地图是否覆盖关键代码入口，编码规则是否来自项目事实，失败经验是否可复用。
7. 选择一个真实任务、真实失败案例或最小代码路径作为校验样本。
8. 按更新后的 harness 入口和索引尝试理解、执行或验证该样本，记录 agent 会卡住的位置。
9. 将卡点分类为结构缺口、命名缺口、索引缺口、上下文缺口、命令缺口、验证缺口、架构地图缺口、规则缺口、工具缺口或代码/测试债务。
10. 先修复结构类问题，再更新对应深层知识文档；已有内容应增量修订，不要无理由重写。
11. 对照证据等级、过期标记和冲突处理规则，修正或标注无法确认的内容。
12. 对更新后的 harness 做一次轻量复核：入口是否更短、更清晰，目录和文件名是否稳定，新增文档是否能被入口找到，命令和验证说明是否仍然可执行。

## 持续维护触发器

出现以下情况时，应重新执行本技能并更新 harness：

- agent 执行任务时卡在项目结构、模块边界、命令、验证方式、环境准备或失败恢复上。
- 命令失效、测试失败原因不明、CI 与本地结果不一致，或验证路径被证明不完整。
- agent 误读架构边界、改错模块、重复踩同一失败模式，或遗漏项目特有编码规则。
- 项目新增、删除或重命名关键模块、服务、入口、脚本、测试框架、构建系统、CI 流程或部署方式。
- 完成真实开发任务后，发现可复用的命令、验证策略、架构事实、失败经验或评审规则。
- 入口文件过长、深层文档职责重叠、索引不可用，或新文档无法从 `AGENTS.md` / `CLAUDE.md` 找到。

## AGENTS.md / CLAUDE.md 维护规则

- 入口文件建议控制在可快速阅读的长度，只包含：
  - 项目目标和主要技术栈。
  - 常用开发、测试、检查命令的索引。
  - 关键目录和文档地图。
  - 必须遵守的工作方式和禁止事项。
  - 遇到失败时应记录到哪里。
- 需要进一步阅读的 `{harness_dir}/` 文件。
- 如果 `AGENTS.md` 和 `CLAUDE.md` 同时存在，应避免两份文件长期分叉。优先让两者共享同一套 `{harness_dir}/` 文档。
- 如果项目已有成熟的 `docs/` 结构，应在入口文件中链接现有文档，不重复搬运内容。
- 如果命令依赖环境变量、服务、容器或外部账号，必须说明前置条件和安全边界，不得写入真实密钥。
- 入口文件建议控制在 100 行左右；超过后应拆分到 `{harness_dir}/` 下的具体文档。

## 最小阅读路径

`{harness_dir}/index.md` 必须按任务类型列出最小阅读路径，避免 agent 每次读取完整 harness：

- 新任务默认必读：`AGENTS.md` 或 `CLAUDE.md`，再读 `{harness_dir}/index.md`。
- 修改代码前：读取 `{harness_dir}/architecture-map.md`、`coding-rules.md` 和 `verification.md` 中相关部分。
- 运行或修复测试前：读取 `{harness_dir}/commands.md`、`verification.md` 和 `known-failures.md`。
- 处理失败时：先读 `{harness_dir}/known-failures.md`，再按失败类型回到 `commands.md`、`verification.md` 或 `architecture-map.md`。
- 评审或收尾前：读取 `{harness_dir}/review-rubric.md` 和本次变更类型对应的验证要求。

## 目录与命名规划规则

- `{harness_dir}/index.md` 是深层知识的目录总表，必须说明每个文件的用途、适用任务、是否必读和主要证据来源。
- `{harness_dir}/structure.md` 只在目录规则需要稳定维护时创建；它记录命名约定、文件增删标准、迁移记录和禁止新增的含糊文件名。
- 深层知识文件名默认使用 kebab-case，优先使用职责名，例如 `architecture-map.md`、`review-rubric.md`、`known-failures.md`。
- 新增文件前必须先判断能否合并到现有职责文件；只有当内容有独立读者、独立更新频率或独立验证方式时才新增。
- 废弃或改名文件时，必须同步更新 `AGENTS.md` / `CLAUDE.md`、`index.md` 和所有内部链接。
- 不要把运行时临时笔记、一次性任务草稿或产品规格放入 harness 目录；harness 只保存可复用的 agent 工作知识。

## 删除与废弃规则

- 过期命令、废弃入口、已移除模块和不再适用的规则不能静默保留为有效说明。
- 可以直接删除明显错误且无历史价值的内容；如果删除会影响理解，应在相关文档中记录废弃原因和日期。
- 文件合并、改名或删除时，必须同步更新 `AGENTS.md` / `CLAUDE.md`、`index.md`、`structure.md` 和所有内部链接。
- `known-failures.md` 不应无限增长；长期不再复现的失败应标注为历史记录，保留最后确认日期和不再复现的证据。
- 不要新增 `misc.md`、`notes.md`、`todo.md` 等无法长期维护的兜底文件；无法归类的内容应先修正目录规划。

## 证据等级

写入 harness 的规则必须标注或能追溯到证据来源：

- 强证据：当前代码、测试、CI 配置、构建配置、脚本、锁文件、类型配置、lint/format 配置。
- 中证据：README、架构文档、开发手册、运维说明、团队维护的正式文档。
- 弱证据：历史对话、一次性任务记录、人工经验、未复现的失败描述。
- 未验证内容：无法从强证据或中证据确认的命令、路径、规则或判断，必须标注为 `待验证`，不得写成确定事实。

## 过期检测

- `commands.md` 中的关键命令应记录来源和最后验证日期；长期未验证的命令应标注为可能过期。
- `verification.md` 中的验证策略应记录对应测试、构建、CI 或人工检查入口；入口消失时必须更新。
- `architecture-map.md` 中的关键路径、模块边界和外部依赖应记录最后对照代码日期。
- `references/` 中的外部参考应记录来源 URL、抓取日期、适用范围和更新方式。
- `known-failures.md` 中的失败记录应记录最后复现、最后确认或最后判定为历史记录的日期。
- 生成型文档过期时，应优先刷新；无法刷新时标注原因，不要继续作为确定依据。

## 冲突处理

- 代码、配置、测试、脚本或 CI 与文档冲突时，优先相信当前工程事实，并修正 harness。
- 项目文档之间冲突时，应在相关 harness 文档中标注冲突来源、当前采用的判断和待确认项。
- 无法判断哪一方正确时，不要合并成模糊规则；应标注为 `待确认`，并说明需要用户或维护者确认的问题。
- 入口文件与深层文档冲突时，应以深层文档的最新事实为准，同时更新入口文件中的索引或摘要。

## Harness 变更自检

每次修改 harness 后，必须做一次轻量自检：

- `AGENTS.md` / `CLAUDE.md` 是否仍然短小，并能指向必要深层文档。
- 新增或改名文件是否已写入 `{harness_dir}/index.md`，并能从入口文件发现。
- 文件职责是否与已有文件重叠；如重叠，是否已合并或在 `structure.md` 中划清边界。
- 新增命令是否有来源、适用场景、前置条件和验证状态。
- 新增规则是否能追溯到代码、配置、测试、CI、正式文档或明确团队约束。
- 是否引入敏感信息、绝对本机路径、个人凭证或一次性任务噪音。
- 是否需要删除、废弃或标注过期内容，而不是只追加新内容。

## 内容事实校验规则

- `commands.md` 中的命令必须能从仓库配置、脚本或 CI 文件中找到来源；无法确认的命令必须标注为待验证。
- `verification.md` 的验证策略必须能对应到实际测试命令、构建命令、人工检查入口或 CI 检查。
- `architecture-map.md` 的模块边界和入口路径必须能被当前代码目录、导入关系、路由、配置或构建文件支持。
- `coding-rules.md` 的规则必须来自已有代码风格、lint/format 配置、测试写法、评审反馈或团队明确约束。
- `known-failures.md` 的失败记录必须包含可观察症状、复现或触发条件、根因判断、处理方式和最后确认日期。
- 如果文档说法与代码事实冲突，应优先修文档；如果代码或工具本身阻碍 agent 工作，应记录为 `待确认` 或 `待处理` 项，并说明证据和影响。

## {harness_dir} 目录建议内容

### index.md

- harness 文档总览。
- 目录规划、命名约定和深层知识职责边界。
- agent 执行任务前必须阅读的最小文档集合。
- 不同任务类型应读取的文档路径。
- 最近一次 harness 更新记录。
- 当前已知的待确认项和过期风险索引。

### structure.md

- harness 目录职责、文件命名规则和文档增删标准。
- 当前深层知识文件的保留、合并、拆分或废弃理由。
- 入口文件、索引文件和深层知识之间的链接维护规则。
- 当目录很小且规则已写入 `index.md` 时，可以不创建本文件。

### commands.md

- 安装依赖、启动服务、运行测试、格式化、类型检查、构建、调试和清理命令。
- 每条命令的适用场景、预期耗时、常见失败原因和替代命令。
- 每条关键命令的来源和最后验证日期。
- 需要审批、网络、凭证或外部服务的命令必须明确标注。

### verification.md

- 按变更类型定义最低验证要求，例如后端逻辑、前端 UI、数据库迁移、配置变更、文档变更。
- 明确哪些测试是快速本地验证，哪些是完整回归验证。
- 记录不可自动验证的人工检查项。
- 记录每类验证要求对应的测试、构建、CI 或人工检查入口。

### architecture-map.md

- 关键模块边界、主要代码入口、核心数据流和外部依赖。
- 对 agent 最容易误判的模块关系做明确说明。
- 只记录有助于执行任务的架构信息，不复制完整架构文档。
- 关键路径和模块边界应记录最后对照代码日期。

### coding-rules.md

- 项目特有的编码风格、测试风格、错误处理、日志、配置和兼容性约束。
- 已被团队明确禁止的实现方式。
- 与通用语言规范重复的内容应少写或不写。
- 每条项目特有规则应能追溯到代码事实、工具配置、评审反馈或明确团队约束。

### review-rubric.md

- agent 任务完成前的自查清单。
- 评审时必须关注的行为正确性、回归风险、可观测性、安全性和可维护性。
- 可复用的验收映射规则和任务完成判断标准。

### known-failures.md

- 失败症状、复现方式、根因、解决方式和最后确认日期。
- 区分一次性失败、环境问题、测试不稳定和真实缺陷。
- 长期不再复现的失败应标注为历史记录，并说明最后确认日期。

### references/

- 保存 agent 需要稳定引用的外部规范、框架约束、API 摘要或 `llms.txt`。
- 每个参考文件必须标注来源 URL、抓取日期、适用范围和更新方式。
- 不要无筛选复制大型外部文档；应保留对 agent 执行任务有直接帮助的摘要或片段索引。

## 完成标准

- 除非用户明确要求只分析不改文件，否则至少有一个 harness 输出物已创建或更新。
- `AGENTS.md` 或 `CLAUDE.md` 能作为清晰入口，指向必要的 `{harness_dir}/` 文档。
- `{harness_dir}/index.md` 已明确深层知识目录、文件名、职责边界和任务阅读路径；必要时已创建或更新 `structure.md`。
- 深层知识的目录和命名已经过一次结构复核，不存在明显职责重叠、孤岛文档或入口无法发现的文件。
- 常用命令、验证策略、架构地图、编码规则和失败记录至少覆盖本轮真实任务或失败案例。
- 关键 harness 内容已经根据当前代码、脚本、配置、测试或 CI 事实做过校验；未能确认的内容已标注为 `待验证` 或 `待确认`。
- 新增或更新内容经过一次轻量验证，能被 agent 按说明找到并执行。
- 本轮已执行 harness 变更自检，并处理或标注过期、冲突、重复和无法确认的内容。
- 最终回复必须列出已创建或更新的文件路径；如果没有落盘文件，本轮不能宣称完成。
- 明确说明本轮是新建、更新还是复核 harness，并列出后续应重复执行的触发条件。
