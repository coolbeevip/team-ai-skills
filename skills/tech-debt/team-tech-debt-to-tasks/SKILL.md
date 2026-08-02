---
name: team-tech-debt-to-tasks
description: 将已评审技术债拆为可独立实现、验证并在用户确认差异后提交的 Task。Break a reviewed technical-debt spec into tasks that each produce one user-confirmed local commit after verification.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 技术债拆 Task
  - 把技术债拆成工程任务
  - 生成技术债开发计划
  - break technical debt into tasks
  - create technical debt tasks
  - plan technical debt commits
---

# 技术债转工程 Tasks

把通过评审的技术债规格拆成可独立实现、验证，并在用户检查实际差异且明确确认后形成一个逻辑 commit 的工程 Task。Task 是本地执行单元，不等同于远端 Issue。

## 触发边界

- 适合触发：技术债规格已通过 `team-tech-debt-review`，需要形成工程执行队列。
- 不适合触发：证据和风险尚未明确时使用 `team-tech-debt-refine`；评审未 ready 时使用 `team-tech-debt-review`；开始编码时使用 `team-task-implement` 或 `team-task-batch-implement`。

## 运行时配置

先读取 `team-spec/config.yml`，应用其中的语言和访问策略。文件不存在或缺少写入 Task 所需字段时，先使用 `team-config-init` 创建或增量补全；本技能不得自行回写配置。存在 `access_policy` 时，必须先确定允许读取和写入的目录。本技能不创建 commit，因此不要求 `version_control` 完整。

## 公共写作风格

生成或改写 Task、用户可见说明或代码注释前，读取 `team-spec/config.yml`。若 `writing_style.guide` 指向存在文件，写作前读取并应用；缺失时继续。

## 输入物

必须先确定唯一技术债 slug 或明确文件路径，默认读取：

- `team-spec/active/{slug}/spec/refine.md`
- `team-spec/active/{slug}/spec/reviews.md`
- `team-spec/active/{slug}/spec/CONTEXT.md`
- 当前代码库、测试、监控证据和风险材料。

阶段评审结果必须是 `ready`，工作区生命周期应为 `debt-ready`。无法唯一判断 slug 或评审未通过时停止。

## 输出物

- `team-spec/active/{slug}/tasks/T{nnn}-{short-task-slug}.md`
- Task 依赖顺序、风险覆盖、回滚边界和 AFK/HITL 分类。
- 供 `team-task-implement`、`team-task-batch-implement` 和 Spec 级远端技能使用的执行计划。

本技能不创建分支、commit、远端 Issue、PR 或 MR。

## Task 合同

每个 Task 必须：

- 处理一个明确技术债风险或可独立验证的治理切片。
- 给出当前证据、预期改善、验证方法和回滚边界。
- 在与 slug 完全同名的 `{slug}` 分支上实现，不添加 `spec/` 前缀。
- 验证通过并经用户检查实际差异、明确确认后形成一个逻辑 commit。
- 使用 `T001` 等本地 ID，不复用远端 Issue 编号。

状态使用 `draft`、`implementing`、`needs-changes`、`blocked`、`verified`、`committed`。PR/MR 状态不得写入 Task。

## 拆解原则

- 优先按风险闭环拆分，不按文件或技术层机械拆分。
- blocker 先于依赖它的 Task。
- 行为保持、迁移、清理和删除旧路径应放在能独立验证和回滚的边界中。
- 若两个 Task 必须一起提交才能保持系统可用，应合并。
- 若一个 Task 混合多个可独立回滚的高风险变化，应拆分。
- 不把顺手重构、无证据抽象或未来扩展混入当前技术债 Task。

## 工作流

1. 读取配置、技术债规格、评审结论和代码证据。
2. 汇总风险、影响范围、优先级、验收和非目标。
3. 草拟 Task、依赖、回滚边界和验证命令。
4. 检查每个 Task 是否能形成含义完整的逻辑 commit。
5. 检查循环依赖、过度拆分和遗漏的兼容或迁移步骤。
6. 向用户确认 Task 粒度和执行顺序。
7. 写入 `tasks/`，不发布为远端 Issue。

## Task 模板

```md
# {Task title}

## Task ID

T001

## Status

draft

## Parent Spec

{slug}

## Risk addressed

{证据化风险}

## Type

AFK（可独立执行，无需人工决策）

## Acceptance criteria

- [ ] Given {当前状态}，When {治理动作}，Then {可验证改善}。

## Blocked by

- None

## Rollback

{回滚条件和步骤}

## Commit

Pending
```

## 完成标准

- 所有 Task 都能追溯到已评审技术债风险。
- 每个 Task 有独立验证、回滚和逻辑 commit 边界。
- Task 文件写入同一 slug 的 `tasks/`。
- 未创建分支、commit、远端 Issue、PR 或 MR。

## 最终回复

必须包含：

- 技术债 slug、规格和评审路径。
- Task 顺序、依赖、风险和回滚摘要。
- Task 文件路径。
- 未解决 HITL 或外部 blocker。
- 有序号的下一步选项。
