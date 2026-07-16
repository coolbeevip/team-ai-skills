---
name: team-spec-refine
description: 通过用户确认细化需求规格，澄清术语、边界、业务规则和验收口径。Refine product specs through user confirmation of terminology, scope, business rules, and acceptance criteria.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 细化需求
  - 需求不清楚
  - 打磨规格
  - 帮我想清楚这个需求
  - 需求还没想好
  - refine spec
  - clarify requirements
  - spec is unclear
  - help me think through this requirement
---

# 规格细化

这个技能用于把模糊需求打磨成团队共享、可验证的规格。一次只问一个问题。不要在关键假设尚未稳定时直接写 PRD。

## 触发边界

- 适合触发：用户的需求还不清楚，需要澄清术语、范围、业务规则、验收口径或关键假设。
- 不适合触发：规格已经稳定并需要风险评审时，转交 `team-spec-review`；规格已通过评审并要固化交付边界时，转交 `team-spec-to-prd`。

## 工作边界

本技能只用于需求规格细化，不进入代码实现。允许读取项目文档、设计稿、现有代码和测试来理解当前行为，但必须把这些读取视为只读调研。

严格禁止在本技能中修改业务代码、测试代码、配置文件、脚本、构建文件、依赖锁文件、数据库迁移、资源文件或其他非 `team-spec/` 规格产物。不得运行格式化、代码生成、依赖安装、迁移生成、批量替换、提交、推送等会改变代码库实现状态的操作。

本技能允许写入的路径仅限于“输出物”中列出的 `team-spec/` 文件。每次准备写文件前，先确认目标路径属于这些输出物；如果目标路径不在白名单内，停止写入，并把需求记录为开放问题、实现风险或后续交付建议。

如果用户在细化过程中要求“顺手实现”“直接改代码”“先修一下”等实现动作，必须暂停本技能并说明：当前阶段只确认规格；如需实现，应在规格确认后切换到交付实现技能或由用户另行明确发起实现任务。不要在同一轮 `team-spec-refine` 中同时细化需求和修改代码。

## 首轮动作

0. 启动检查：优先读取 `team-spec/config.yml`。若不存在，不报错，只询问一次语言偏好后创建配置；同时确认本轮只做规格细化，不修改代码实现。
1. 用一到两句话复述当前需求。
2. 找出最阻碍共识的一个未知点。
3. 提出一个聚焦问题，并给出你的推荐答案。
4. 等用户回答后再继续。

如果答案可以从现有项目文档或代码中获得，先只读查资料，不要把问题抛给用户，也不要为验证猜想而修改代码。

## 运行时配置

`team-spec/` 是运行时工作空间。项目级配置统一使用目标项目根目录的 `team-spec/config.yml`：

```yaml
language: zh-CN
version_control:
  system: git
  trunk_branch: main
  contribution_model: fork-pull
  source_remote: origin
  target_remote: upstream
access_policy:
  mode: default-readonly
  directory_file: team-spec/access_policy/default.md
  user_file_template: team-spec/access_policy/{user_name}.md
```

- `language`：统一语言设置（对话回复与 refine/review/prd/issues/design 产物文档）。
- `version_control.system`：版本管理系统，例如 `git`。
- `version_control.trunk_branch`：主干分支名，例如 `main`、`master` 或 `develop`。
- `version_control.contribution_model`：贡献方式，例如 `fork-pull` 或 `direct`。
- `version_control.source_remote`：贡献分支默认推送的 remote，`fork-pull` 常见为 `origin`。
- `version_control.target_remote`：PR/MR 或 issue 默认面向的上游 remote，`fork-pull` 常见为 `upstream`。
- `access_policy`：目录访问策略索引。`mode`、`directory_file` 和 `user_file_template` 只负责定位权限正文，不在这里写长篇规则。

`version_control` 是可选配置。首次创建 `team-spec/config.yml` 时，若当前任务只涉及产品规格，不要为了补齐版本管理信息打断用户；只写入已确认的 `language`。当后续技能涉及 issue 发布、实现收尾、PR 或 MR 时，再补充版本管理配置。
如果本轮任务涉及访问边界、写入目标项目文件或需要稳定复用的运行时偏好，`access_policy` 应与 `language` 一起作为最小配置的一部分；配置缺失时，先询问是否创建最小配置，再继续写入。

语言优先级必须固定为：

1. 用户本轮明确指定。
2. `team-spec/config.yml`。
3. 首次询问用户并落盘到 `team-spec/config.yml`。

显式覆盖规则：

- 用户在单次会话临时要求切换语言时，本次立即生效。
- 临时切换后，应询问是否回写 `team-spec/config.yml`；用户同意才更新配置。

兼容性兜底：

- 旧项目没有 `team-spec/config.yml` 时，不得报错或中断；走“询问一次并创建配置”的流程。
- 旧项目没有 `version_control` 时，相关交付技能应先通过 `git remote -v`、`git branch --show-current`、`git branch -r`、`git symbolic-ref refs/remotes/{remote}/HEAD` 和 `git config --get branch.{branch}.remote` 等轻量命令推断。
- 如果命令推断仍无法唯一确定版本管理系统、主干分支或贡献方式，只问用户缺失的最小问题；得到用户确认后再回写 `team-spec/config.yml`。

## 需求上下文

探索时优先寻找已有需求语言和产品决策：

```text
/
├── REQUIREMENTS.md
├── team-spec/
│   ├── CONTEXT.md
│   ├── decisions/
│   ├── active/
│   │   └── {slug}/
│   │       ├── spec/
│   │       │   ├── CONTEXT.md
│   │       │   ├── decisions/
│   │       │   ├── refine.md
│   │       │   └── reviews.md
│   │       ├── prd/
│   │       ├── issues/
│   │       ├── design/
│   │       └── STATUS.md
│   └── archive/
└── docs/
```

默认只把本轮需求细化结论写入 `team-spec/active/{slug}/spec/refine.md`。`CONTEXT.md` 不是需求记录的默认容器，只用于沉淀可复用的稳定产品语言。

发现候选上下文时，先轻量确认适用范围：`全局`、`当前需求` 或 `暂不确定`。推荐问题格式为：“这个{术语/角色/流程/规则}后续适用范围是所有相关需求通用、只限当前需求，还是暂不确定？”不要为了收集上下文专门打断主线；只在正常追问中发现复用信号时顺手确认。

如果用户确认候选上下文会跨多个需求复用，且属于产品术语、角色、通用流程或通用业务规则，再创建或更新 `team-spec/CONTEXT.md`。不要提前创建空文件。

如果用户确认候选上下文只属于当前需求，但会在 PRD、任务拆解、功能设计或后续研发讨论中反复复用，再创建或更新 `team-spec/active/{slug}/spec/CONTEXT.md`。不要提前创建空文件。

如果用户选择 `暂不确定`，或该信息只是当前需求的一次性摘要、范围、验收口径、页面草稿、字段草稿或未确认假设，只写入 `team-spec/active/{slug}/spec/refine.md`，不要创建或更新 `CONTEXT.md`。

如果 `team-spec/decisions/` 不存在，等第一个跨多个需求长期有效、值得保留的产品决策出现后再创建。

如果 `team-spec/active/{slug}/spec/decisions/` 不存在，等第一个只影响当前需求的产品决策出现后再创建。

需求上下文使用 [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md)，产品决策记录使用 [DECISION-FORMAT.md](./DECISION-FORMAT.md)。

## 输入物

- 当前对话中的初始需求、用户问题、业务背景或功能想法。
- 同一 slug 下由 `team-concept-whitepaper` 生成的 `team-spec/active/{slug}/concept/whitepaper.md`（如果存在），用于继承产品定位、价值、能力边界和已标注假设。
- `team-spec/config.yml`（如果存在），用于确定统一语言设置。
- 现有 `team-spec/CONTEXT.md` 和 `team-spec/decisions/`，如果项目已有跨需求产品语境或产品决策记录。
- 现有 `team-spec/active/{slug}/spec/CONTEXT.md` 和 `team-spec/active/{slug}/spec/decisions/`，如果该需求已有局部上下文或产品决策记录。
- 相关 PRD、业务文档、任务、设计稿或代码现状；代码和测试只能作为只读输入物，不得作为本技能输出目标。
- 如果存在 `team-spec/active/{slug}/spec/reviews.md` 且状态为 `needs-refinement`，必须优先读取它，并围绕其中的问题继续追问用户。

## 输出物

- 对话中的澄清结论：需求摘要、规范术语、范围内/范围外、开放问题和轻量风险扫尾。
- `team-spec/CONTEXT.md`：条件输出。仅当用户确认某个产品术语、角色、通用流程或通用业务规则会跨多个需求复用后，才创建或更新。
- `team-spec/decisions/{number}-{decision-slug}.md`：当出现跨多个需求长期有效且高成本回退的产品决策时创建。
- `team-spec/active/{slug}/spec/refine.md`：单次规格细化的主输出物。
- `team-spec/active/{slug}/spec/CONTEXT.md`：条件输出。仅当用户确认某个术语、角色、流程或业务规则只属于当前需求，但会被 PRD、任务拆解、功能设计或后续研发讨论反复复用后，才创建或更新。
- `team-spec/active/{slug}/spec/decisions/{number}-{decision-slug}.md`：当出现只影响当前需求的产品决策时创建。
- `team-spec/active/{slug}/STATUS.md`：可选状态文件，只记录工作区生命周期状态。当前技能使用 `refining`；规格通过评审后由评审流程更新为 `spec-ready`。跨阶段还可使用 `paused` 或 `blocked`。
- `team-spec/config.yml`：首次进入工作空间且缺失配置时创建；用户明确同意时可更新语言设置，相关交付技能在确认后可补充 `version_control` 配置。
- 在读取或写入 `team-spec/active/{slug}/` 之前，先读取 `team-spec/config.yml`；如果存在 `access_policy`，再据此判断当前协作者对目录的读取和写入边界。

本技能不得输出代码补丁、测试修改、配置修改、依赖变更、迁移文件或构建脚本变更。发现代码现状与需求目标不一致时，只能记录为当前行为、差异、风险、开放问题或后续实现建议。

下游技能会读取这些输出物：`team-spec-review` 用于规格评审，`team-spec-to-prd` 用于生成 PRD。

`team-spec-refine` 可以与 `team-spec-review` 反复迭代。如果评审发现 P0 或关键 P1，应回到本技能继续修正术语、范围、业务规则、异常路径或验收口径。

每个需求必须使用唯一 slug 串联全流程。格式为 `{yyyy-mm-dd}-{short-english-slug}`，例如 `2026-05-10-export-filter`。如果同一天同名，追加序号，例如 `2026-05-10-export-filter-2`。全局 `team-spec/CONTEXT.md` 和 `team-spec/decisions/` 只记录跨需求长期复用的信息；`active/{slug}/spec/CONTEXT.md` 和 `active/{slug}/spec/decisions/` 只记录当前需求局部信息，不替代 `spec/refine.md`。

开始新需求前，必须确定本次要使用的 slug，并检查 `team-spec/active/{slug}/` 是否已存在。如果不存在，可以创建该工作区；如果已存在，应判断是继续同一需求还是用户想创建新 slug。`team-spec/active/` 下允许同时存在多个 slug，不得因为其他 slug 未归档而要求用户先归档。`team-spec/archive/` 默认只读，除非用户显式指定历史 slug 或文件路径。

修订同一个需求时，不要新建 slug。继续更新 `team-spec/active/{slug}/spec/refine.md`，并在文件中的 `## Change Log` 记录本轮修订原因和日期。

## 细化原则

- 发现一词多义时立即指出。例如：“你说的账号，是登录账号、客户账户，还是计费账户？”
- 把模糊表述改成可观察行为。例如：把“审批要快”改成“95% 的审批在 2 分钟内完成”。
- 区分用户问题和解决方案。先确认要解决什么问题，再接受页面、流程或系统设计。
- 重点追问用户角色、权限、状态变化、异常路径和业务规则。
- 用具体场景压测边界。主动构造边缘案例，让概念边界暴露出来。
- 有多个方案时，给出推荐方案，再让用户确认或否定。
- 做上下文适用范围判断。发现可能复用的术语、角色、流程或规则时，先轻量询问它是 `全局`、`当前需求` 还是 `暂不确定`；只有用户确认后才写入对应 `CONTEXT.md`。未确认复用范围或一次性需求细节只写入 `spec/refine.md`。
- 把代码现状当作需求输入，而不是实现入口。若发现需要改代码才能满足需求，只记录“后续实现需要处理”，不得直接修改。

## 追问顺序

除非对话中有更高优先级，否则按这个顺序推进：

1. 问题：这个需求由什么用户痛点、业务机会或产品判断触发？
2. 用户：谁遇到问题，谁使用方案，谁运营或审批？
3. 结果：什么可衡量变化能证明需求有效？
4. 范围：哪些必须包含，哪些明确排除，哪些延期？
5. 流程：从触发到完成的主路径是什么？
6. 数据：涉及哪些对象、字段、状态和规则？
7. 异常：什么会失败、冲突、过期、取消或需要人工介入？
8. 约束：合规、隐私、性能、灰度、迁移、运营限制是什么？
9. 验收：哪些例子应该通过，哪些应该失败？

## 产品决策记录

只有同时满足以下三点，才建议创建产品决策记录：

1. 这个决策以后反悔成本较高。
2. 未来同事只看 PRD 或代码时不容易理解为什么这么选。
3. 当时确实存在多个备选方案，并且选择依赖产品判断。

不要为显而易见的措辞、临时备注或实现阶段很可能改变的细节创建决策记录。

决策记录位置按影响范围选择：

- 影响后续多个需求、术语体系、通用流程或通用业务规则的决策，写入 `team-spec/decisions/`。
- 只影响当前需求范围、取舍、验收或发布策略的决策，写入 `team-spec/active/{slug}/spec/decisions/`。

## 会话输出

每轮回答后，简短说明本轮解决了什么：

- 对话回复与文档落盘均使用 `language`；若用户本轮显式覆盖，按覆盖值执行。

- 已确认的术语、规则、角色或范围边界。
- 当前剩余风险最高的歧义。
- 下一个单一问题。

细化完成后，总结：

- 用自然语言描述需求。
- 规范术语。
- 范围内和范围外内容。
- 仍未解决的问题。
- 轻量风险扫尾：指出是否存在会阻塞 PRD 的明显 P0/P1 缺口。
- 写入或更新 `team-spec/active/{slug}/spec/refine.md`。
- 在 `## Change Log` 中记录本次澄清或修订。
- 下一步可选：必须使用有序号的列表选项输出，方便用户直接回复序号继续推进。

推荐格式：

```md
## 下一步可选

1. `team-spec-review`：没有明显阻塞时，评审当前规格是否 ready。
2. 继续细化：仍有高风险歧义时，继续补充关键问题。
```

## 完成标准

- 核心问题、目标用户、预期结果、范围、主流程、关键规则、异常路径和验收口径已达到可评审程度。
- 规范术语和仍未解决的开放问题已经显式记录。
- `team-spec/active/{slug}/spec/refine.md` 已创建或更新，并记录本轮 Change Log。
- 没有未说明的明显 P0/P1 缺口；存在风险时已明确标注，不把假设写成确认事实。

## 最终回复

细化完成时必须包含：

- 规格路径和 slug。
- 本轮确认的关键术语、范围与规则。
- 仍保留的开放问题和 P0/P1 风险扫尾。
- 是否建议进入 `team-spec-review`。
- 有序号的“下一步可选”列表。
