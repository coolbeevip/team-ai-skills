---
name: team-prd-to-tasks
description: 将 PRD 拆解为可独立实现、验证并在用户确认差异后提交的工程 Task。Break a PRD into dependency-ordered tasks that each produce one user-confirmed local commit after verification.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 拆 Task
  - 把 PRD 拆成工程任务
  - 生成可提交的开发任务
  - break PRD into tasks
  - create engineering tasks
  - plan commit-sized tasks
---

# PRD 转工程 Tasks

把一个已确认 PRD 拆成可独立实现、独立验证，并在验证通过、用户检查差异且明确确认后形成一个逻辑 commit 的工程 Task。Task 是本地执行单元，不等同于 GitHub Issue 或 GitLab Issue。

## 触发边界

- 适合触发：PRD 已确认，需要生成有依赖顺序的工程执行计划。
- 不适合触发：PRD 尚未固化时使用 `team-spec-to-prd`；要实现 Task 时使用 `team-task-implement` 或 `team-task-batch-implement`；要创建远端 Spec Issue 时使用 `team-spec-create-issue-github` 或 `team-spec-create-issue-gitlab`。

## 运行时配置

在读取 PRD、规格、代码或写入 Task 前，先读取目标项目根目录的 `team-spec/config.yml`。如果存在 `access_policy`，先应用目录访问边界。

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

缺少配置时，不猜测写入权限、主干分支或远端；仅生成本地 Task 草稿不需要创建 git 分支。

## 公共写作风格

生成或改写 Task、用户可见说明或代码注释前，检查 `team-spec/config.yml` 的 `writing_style.guide`。路径存在时读取并应用；缺失时继续，不猜测路径。

格式、状态、安全、证据和验收合同优先于风格指南。

## 输入物

主输入必须是唯一 PRD：

- `team-spec/active/{slug}/prd/prd.md`
- 或用户显式指定的 PRD 文件。

必须先确定唯一 `{slug}` 或 PRD 路径。无法唯一判断时停止并要求用户提供，不扫描 `team-spec/archive/` 猜测。

默认参考同一 slug 的：

- `team-spec/active/{slug}/spec/refine.md`
- `team-spec/active/{slug}/spec/reviews.md`
- `team-spec/active/{slug}/spec/CONTEXT.md`
- `team-spec/active/{slug}/spec/decisions/`
- `team-spec/CONTEXT.md`
- `team-spec/decisions/`
- 当前代码库、测试、ADR 和已有实现。

## 输出物

- Task 拆解确认稿。
- 本地 Task 文件：`team-spec/active/{slug}/tasks/T{nnn}-{short-task-slug}.md`。
- Task 依赖顺序和 AFK/HITL 分类。
- 供 `team-task-implement`、`team-task-batch-implement` 和 Spec 级远端技能读取的执行计划。

本技能不创建 git 分支、commit、远端 Issue、PR 或 MR。

## Task 合同

每个 Task 必须：

- 覆盖一个窄而完整的工程行为切片。
- 有独立验收标准和明确依赖。
- 能在 Spec 共享分支上独立实现和验证。
- 验证通过并经用户检查实际差异、明确确认后形成一个逻辑 commit。
- 不要求独立分支、独立 PR 或独立 MR。
- 使用本地稳定标识 `T001`、`T002`、`T003`，不把远端 Issue 编号当成本地 Task ID。

Task 生命周期使用：

```text
draft → implementing → verified → committed
```

异常状态使用 `needs-changes` 或 `blocked`。`pr-created` 和 `mr-created` 属于 Spec 交付，不得写入 Task 状态。

## 拆解原则

- 优先 vertical slice，不按 UI、API、数据库等技术层机械拆分。
- 每个 Task 完成后必须有可观察、可测试的结果。
- 如果两个相邻 Task 共享同一验收场景和同一 commit 边界，且拆分没有并行、风险隔离或人工决策收益，应合并。
- 如果一个 Task 无法形成含义完整的逻辑 commit，应重新划分。
- 数据迁移、兼容性、高风险变更或 HITL 决策可以单独成 Task，但必须有明确验证方式。
- 不为未来可能需要的抽象提前创建 Task。

## AFK 与 HITL

- `AFK（可独立执行，无需人工决策）`：工程 agent 或研发可按验收标准完成。
- `HITL（需要人工介入）`：需要产品、设计、架构、合规或跨团队决策。

HITL Task 必须写清楚由谁决定什么；未完成决定前不得进入实现队列。

## 拆解确认交互

本技能所有需要用户介入的节点都应优先提供有序号的封闭选项，并给出推荐项及其影响。用户只需回复编号或简短自然语言，不得要求用户重述已有上下文或输入大段文字。

- 存在多个候选 slug 或 PRD 时，列出候选路径、简短标题和“取消”选项，让用户按编号选择。
- HITL 决策存在有限方案时，提炼为互斥选项并标注推荐项；只有缺少必要的新事实时，才要求用户补充一个短字段或一句短文本。
- 无法预先枚举的路径、范围或业务事实，才允许自由输入，并明确限制所需内容。

展示候选 Task 后，必须先让用户确认或调整，再写入 `tasks/`。不要只问“是否接受”，也不要要求用户先输入大段修改意见。

统一使用以下一级选项：

```md
## 请选择下一步

1. ✅ 接受当前拆解并写入：按当前 Task 列表生成文件。
2. 🔄 粒度偏细，希望合并：合并缺少独立验收、并行、风险隔离或回滚价值的关联 Task。
3. 🔄 粒度偏粗，希望拆分：拆开同时覆盖多个独立行为、风险或回滚边界的 Task。
4. ⚠️ 依赖或顺序需要调整：保持 Task 范围，重新计算 `Blocked by` 和执行顺序。
5. 👤 局部调整某个 Task：选择一个 Task 后，再决定合并、拆分、改范围或改依赖。
6. ⛔ 取消本次拆解：保留当前预览，不写入任何 Task 文件。
```

用户只需回复选项编号。若用户直接回复“太细了”“合并一些”“太粗了”“需要拆开”等自然语言，也应映射到对应选项，不得强制用户重新输入编号。

各选项按以下规则执行：

- 选择 1：按当前预览写入 Task 文件；写入完成后报告文件路径。
- 选择 2：优先合并属于同一用户场景、验收链路或交付边界，且不具备独立并行、HITL、风险隔离或回滚价值的关联 Task。默认目标是将 Task 数量减少约三分之一，但不得为了减少数量破坏端到端交付、单次逻辑提交或独立验证边界。重新编号并更新依赖、覆盖关系后，再展示完整预览和同一组选项。
- 选择 3：拆分同时包含多个可独立观察行为、风险边界、回滚边界或逻辑提交的 Task。拆分后重新计算编号、依赖和验收覆盖，再展示完整预览和同一组选项。
- 选择 4：保持 Task 数量和范围不变，重新检查执行顺序、循环依赖、隐含前置条件与 `Blocked by`，然后展示修订预览和同一组选项。
- 选择 5：先仅要求用户选择一个 Task 编号；随后展示二级选项。
- 选择 6：停止本次写入，明确说明没有生成或修改 Task 文件。

局部调整统一使用以下二级选项；不存在前一个或后一个 Task 时，应省略或标记对应选项不可用：

```md
## 请选择如何调整该 Task

1. 🔄 与前一个 Task 合并。
2. 🔄 与后一个 Task 合并。
3. 🔄 拆分为更小的 Task。
4. 🔄 调整依赖或执行顺序。
5. 👤 修改标题或范围。
6. ↩️ 返回上一级。
```

除“修改标题或范围”外，二级选项也应由技能按拆解原则自动完成。只有选择“修改标题或范围”时，才要求用户用一句短文本说明目标；不得要求重写整个 Task。

任何调整完成后都必须重新展示候选 Task 和一级选项，只有用户选择“接受当前拆解并写入”后才能写文件。若用户在最初请求中已明确授权“直接生成”“按你的判断写入”等无须预览的操作，则可跳过确认，但仍须遵守 HITL、安全和路径唯一性要求。

## 工作流

1. 读取配置、PRD、同 slug 规格和必要代码证据。
2. 汇总目标、用户故事、约束、验收标准和非目标。
3. 草拟 Task 列表、依赖和覆盖关系。
4. 检查每个 Task 是否可独立验证并形成一个逻辑 commit。
5. 检查是否过度拆分、遗漏集成行为或存在循环依赖。
6. 向用户展示 Task 编号、标题、类型、依赖、验收覆盖和切片理由。
7. 按“拆解确认交互”展示一级选项；若用户要求调整，则修订并返回步骤 6。
8. 只有用户接受当前拆解，或已在最初请求中明确授权直接写入，才写入 `tasks/`；不得发布为远端 Issue。
9. 根据平台和队列规模推荐单 Task 或批量实现。

## Task 模板

```md
# {Task title}

## Task ID

T001

## Status

draft

## Parent Spec

{slug}

## What to build

{端到端行为和边界}

## Type

AFK（可独立执行，无需人工决策）

## Acceptance criteria

- [ ] Given {上下文}，When {动作}，Then {可观察结果}。

## Blocked by

- None

## Commit

Pending

## Notes

- {约束、风险或测试建议}
```

## 完成标准

- 所有 Task 都有唯一 `T{nnn}` 标识、明确标题、类型、依赖和验收标准。
- 每个 Task 都能形成一个可解释的逻辑 commit。
- Task 文件写入同一 slug 的 `tasks/`。
- 没有创建分支、commit、远端 Issue、PR 或 MR。
- 所有可枚举的用户介入都使用有序号的封闭选项，拆解调整后重新确认。
- 用户能从输出判断执行顺序和剩余 HITL 决策。

## 最终回复

等待用户确认时：

- 展示 PRD 路径、slug、候选 Task 摘要和“拆解确认交互”中的一级选项。
- 不使用“如果接受，请回复接受”或“请告诉我如何调整”等开放式提示。

写入完成后必须包含：

- PRD 路径和 slug。
- Task 数量、顺序、类型和依赖摘要。
- Task 文件路径。
- 过度拆分检查和未解决 HITL。
- 有序号的下一步选项：单 Task 实现、批量实现，或创建可选的 Spec 级远端 Issue。
