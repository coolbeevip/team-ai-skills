---
name: team-spec-refine
description: 通过与用户反复确认来细化需求规格，澄清术语、边界、业务规则和验收口径，并更新需求上下文或产品决策记录。适用于 PRD 前的需求探索、规格打磨和用户访谈。Refine product specs through iterative user confirmation, clarifying terminology, scope, business rules, and acceptance criteria before PRD creation.
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

## 首轮动作

0. 启动检查：优先读取 `team-spec/config.yml`。若不存在，不报错，只询问一次语言偏好后创建配置。
1. 用一到两句话复述当前需求。
2. 找出最阻碍共识的一个未知点。
3. 提出一个聚焦问题，并给出你的推荐答案。
4. 等用户回答后再继续。

如果答案可以从现有项目文档或代码中获得，先查资料，不要把问题抛给用户。

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
```

- `language`：统一语言设置（对话回复与 refine/review/prd/issues/design 产物文档）。
- `version_control.system`：版本管理系统，例如 `git`。
- `version_control.trunk_branch`：主干分支名，例如 `main`、`master` 或 `develop`。
- `version_control.contribution_model`：贡献方式，例如 `fork-pull` 或 `direct`。
- `version_control.source_remote`：贡献分支默认推送的 remote，`fork-pull` 常见为 `origin`。
- `version_control.target_remote`：PR/MR 或 issue 默认面向的上游 remote，`fork-pull` 常见为 `upstream`。

`version_control` 是可选配置。首次创建 `team-spec/config.yml` 时，若当前任务只涉及产品规格，不要为了补齐版本管理信息打断用户；只写入已确认的 `language`。当后续技能涉及 issue 发布、实现收尾、PR 或 MR 时，再补充版本管理配置。

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

如果 `team-spec/CONTEXT.md` 不存在，等第一个跨多个需求复用的产品术语、角色、通用流程或通用业务规则被确认后再创建。不要提前创建空文件。

如果 `team-spec/active/{slug}/spec/CONTEXT.md` 不存在，等第一个只属于当前需求的术语、角色、流程或业务规则被确认后再创建。不要提前创建空文件。

如果 `team-spec/decisions/` 不存在，等第一个跨多个需求长期有效、值得保留的产品决策出现后再创建。

如果 `team-spec/active/{slug}/spec/decisions/` 不存在，等第一个只影响当前需求的产品决策出现后再创建。

需求上下文使用 [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md)，产品决策记录使用 [DECISION-FORMAT.md](./DECISION-FORMAT.md)。

## 输入物

- 当前对话中的初始需求、用户问题、业务背景或功能想法。
- `team-spec/config.yml`（如果存在），用于确定统一语言设置。
- 现有 `team-spec/CONTEXT.md` 和 `team-spec/decisions/`，如果项目已有跨需求产品语境或产品决策记录。
- 现有 `team-spec/active/{slug}/spec/CONTEXT.md` 和 `team-spec/active/{slug}/spec/decisions/`，如果该需求已有局部上下文或产品决策记录。
- 相关 PRD、业务文档、任务、设计稿或代码现状。
- 如果存在 `team-spec/active/{slug}/spec/reviews.md` 且状态为 `needs refinement`，必须优先读取它，并围绕其中的问题继续追问用户。

## 输出物

- 对话中的澄清结论：需求摘要、规范术语、范围内/范围外、开放问题和轻量风险扫尾。
- `team-spec/CONTEXT.md`：当跨多个需求复用的产品术语、角色、通用流程或通用业务规则被确认后更新。
- `team-spec/decisions/{number}-{decision-slug}.md`：当出现跨多个需求长期有效且高成本回退的产品决策时创建。
- `team-spec/active/{slug}/spec/refine.md`：单次规格细化的主输出物。
- `team-spec/active/{slug}/spec/CONTEXT.md`：当只属于当前需求的术语、角色、流程或业务规则被确认后更新。
- `team-spec/active/{slug}/spec/decisions/{number}-{decision-slug}.md`：当出现只影响当前需求的产品决策时创建。
- `team-spec/active/{slug}/STATUS.md`：可选状态文件，用于记录当前需求处于 `refining`、`reviewed`、`prd-ready`、`paused` 或 `blocked` 等状态。
- `team-spec/config.yml`：首次进入工作空间且缺失配置时创建；用户明确同意时可更新语言设置，相关交付技能在确认后可补充 `version_control` 配置。

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
- 维护两层上下文。跨多个需求复用的术语、角色、通用流程和通用业务规则，立即更新 `team-spec/CONTEXT.md`；只属于当前需求的边界、流程或规则，更新 `team-spec/active/{slug}/spec/CONTEXT.md`。不要攒到最后。

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
