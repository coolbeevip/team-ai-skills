---
name: team-task-batch-implement
description: 在同一 Spec 分支按依赖顺序批量实现、验证并逐个提交多个 Task。Batch implement tasks on one shared spec branch, verifying and committing each task in dependency order with fail-fast recovery.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 批量实现 Task
  - 连续处理多个工程任务
  - 在同一分支完成所有任务
  - batch implement tasks
  - implement multiple tasks
  - complete tasks on one branch
---

# Task 批量实现编排

在同一个 `{slug}` 分支上按依赖顺序处理多个 Task。分支名严格等于 slug，不添加 `spec/` 或其他前缀。每个 Task 都完整执行实现、验证和本地 commit，任何失败立即停止并保留可恢复边界。

核心原则：一个 Spec 分支，多个 Task commits，最后一个 Spec PR/MR。

## 触发边界

- 适合触发：用户要求连续处理同一 slug 的多个 AFK Task。
- 不适合触发：单个 Task 使用 `team-task-implement`；只验证一个 Task 使用 `team-task-verify`；创建远端合并请求使用 Spec 级技能。

## 运行时配置

先读取 `team-spec/config.yml`，应用语言、访问策略、主干、source remote 和 target remote。无法确认唯一 slug、写权限或主干分支时停止。

## 公共写作风格

生成或改写 Task、汇总、用户可见说明或代码注释前，读取配置中的 `writing_style.guide`（如果存在）。

## 输入物

主输入必须能唯一定位同一个 slug 的 Task 集合：

- `team-spec/active/{slug}/tasks/`
- 或用户显式指定的同 slug Task 文件。

参考同 slug 的 PRD、规格、评审、上下文、决策、代码和测试。

不同 slug 的 Task 不得进入同一批次。HITL、缺少验收、依赖未提交或已 `committed` 的 Task 不进入实现队列。

## 输出物

- 依赖排序后的批量计划。
- 每个已处理 Task 的实现、验证和独立 commit。
- 可选汇总：`team-spec/active/{slug}/tasks/batch-implementation.md`。
- 最终共享分支和剩余队列。

不 push，不创建远端 Issue、PR 或 MR。

## 固定脚本

优先运行：

```text
./scripts/plan_task_batch.py
```

默认只规划，不修改代码：

```sh
python3 {skill_dir}/scripts/plan_task_batch.py --slug {slug}
python3 {skill_dir}/scripts/plan_task_batch.py --slug {slug} --limit 3 --json
```

脚本读取 Task ID、类型、状态、验收标准和依赖，识别缺失依赖、循环、HITL、已提交 Task 和可执行队列。

## 共享分支合同

- 整个批次只使用与 slug 完全相同的 `{slug}` 分支。
- 创建分支时使用 `git switch -c {slug} {trunk_branch}`，不得添加 `spec/` 前缀。
- 开始前工作区不得有无法归因的变化。
- 分支不存在时从已确认主干创建；存在时继续使用。
- 每个 Task commit 后再次确认分支和工作区边界。
- 不为 Task 创建独立分支，不在批次中切换到其他 slug。

## 批量边界

默认最多处理 3 个 Task。用户明确要求全部时可以更多，但仍逐个验证和提交。

每个 Task 严格执行：

```text
team-task-implement
→ team-task-verify
→ verified
→ one local commit
→ Task status committed
```

只有当前 Task 达到 `committed`，才继续下一个。

## 工作流

1. 确定唯一 slug 和 Task 集合。
2. 读取配置、PRD、评审和必要上下文。
3. 检查工作区与共享分支。
4. 运行 `plan_task_batch.py`。
5. 展示队列、跳过项、阻塞项和批量上限。
6. 创建或进入与 slug 完全相同的 `{slug}` 分支。
7. 按顺序对每个 Task 执行完整实现、验证和 commit。
8. 每次 commit 后记录 Task ID、SHA、测试和残余风险。
9. 任何失败立即停止，保留已完成 commits 和剩余队列。
10. 只有所有必需 Task 均 `committed` 时，才推荐 Spec 级 PR/MR。

## 停止条件

- 当前 Task 验证结果不是 `verified`。
- commit 创建失败或范围混入其他 Task。
- 测试失败或缺少关键验证方法。
- 出现 HITL、缺失依赖或循环依赖。
- 需要修改 PRD、规格或产品决策。
- 分支发生切换或出现其他 slug 的 commit。
- 工作区出现无法归因的变化。

停止后不得回滚已验证 commits；应报告恢复入口。

## 完成标准

- 所有已处理 Task 都处于 `committed` 并记录唯一 SHA。
- 所有 commits 位于同一个 Spec 分支。
- 未处理、跳过和阻塞 Task 有明确原因。
- 没有 push、远端 Issue、PR 或 MR。
- 仅在整个必需队列完成时推荐 `team-spec-create-pr-github` 或 `team-spec-create-mr-gitlab`。

## 最终回复

必须包含：

- slug、共享分支和批量范围。
- 已完成 Task 与 commit SHA。
- 失败、跳过、阻塞和剩余队列。
- 关键验证命令和结果。
- 未提交的 `team-spec/` 回写。
- 有序号的下一步选项。
