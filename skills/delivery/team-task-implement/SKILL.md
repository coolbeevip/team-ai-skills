---
name: team-task-implement
description: 在 Spec 共享分支上实现单个工程 Task，验证通过后形成一个本地逻辑 commit。Implement one engineering task on its shared spec branch and create one local logical commit after verification.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 实现 Task
  - 开始工程任务
  - 实现并提交这个任务
  - implement task
  - start task coding
  - implement and commit task
---

# Task 实现

实现 `team-prd-to-tasks` 或 `team-tech-debt-to-tasks` 生成的一个 Task。所有同 slug Task 共用与 slug 完全同名的 `{slug}` 分支，不添加 `spec/` 前缀；每个 Task 验证通过后形成一个本地逻辑 commit。

## 触发边界

- 适合触发：用户指定一个明确 Task，要求实现、验证并在本地提交。
- 不适合触发：多个 Task 连续执行时使用 `team-task-batch-implement`；只审查现有实现时使用 `team-task-verify`；创建 PR/MR 时使用 Spec 级创建技能。

## 运行时配置

在读取 Task、代码或测试前，先读取 `team-spec/config.yml`。应用 `language`、`version_control` 和 `access_policy`；缺少写权限或无法确定主干分支时停止。

默认 Spec 分支为 `{slug}`。用户显式指定且已确认的分支名可以覆盖默认值，但同一 slug 的所有 Task 必须使用同一个分支。

## 公共写作风格

生成或改写文档、用户可见说明或代码注释前，读取配置中的 `writing_style.guide`（如果存在）。格式、状态、安全、证据和验收合同优先。

## 输入物

主输入必须是唯一 Task：

- `team-spec/active/{slug}/tasks/T{nnn}-{short-task-slug}.md`
- 或用户显式指定的 Task 文件。

参考输入包括同 slug 的 PRD、规格、评审、上下文、决策、代码、测试和 `./references/PLATFORM-STDLIB.md`。

必须确认：

- Task 有 `Task ID`、验收标准、类型和依赖。
- HITL 决策已完成。
- `Blocked by` 中所有 Task 已 `committed`。
- Task 尚未对应其他 commit。
- 当前工作区没有无法归因的变更。

无法唯一定位 Task 或 slug 时停止，不扫描 archive 猜测。

## 输出物

- 满足 Task 验收标准的代码和测试。
- `team-task-verify` 的独立验证结果。
- 验证通过后的一个本地逻辑 commit。
- Task 文件中的 `Status: committed`、commit SHA、实现和验证记录。

不得 push、创建远端 Issue、PR 或 MR。`team-spec/` 下的运行时文件不得加入代码 commit。

## 共享分支合同

1. 从 `team-spec/config.yml` 确定主干分支。
2. 将 Spec 分支计算为 `{slug}`，不得添加 `spec/` 或其他前缀。
3. 当前分支不是 Spec 分支时：
   - 工作区有未提交变更则停止。
   - 分支已存在则切换到该分支。
   - 分支不存在则从已确认主干创建。
4. 后续 Task 必须继续使用同一分支。
5. 不创建 Task 独立分支，不把其他 slug 的 commit 混入当前分支。

## 最小实现模式

实现前写出真实入口、已有实现、最小修改路径、可复用能力、拒绝的复杂方案和验证命令。

涉及 URL、日期、CSV、分页、路径、CLI、数据库约束或 UI 原生控件时，读取 `./references/PLATFORM-STDLIB.md` 后再决定实现。

不得以最小实现为由删除权限、输入校验、错误处理、事务、幂等、迁移兼容、可访问性或用户明确要求。

## 工作流

1. 读取配置、Task、PRD 和必要上下文。
2. 校验依赖、工作区和 Spec 分支；创建或切换到共享分支。
3. 将本地 Task 状态更新为 `implementing`。
4. 输出最小路径检查和 commit 范围预览。
5. 按行为 TDD 执行 red-green-refactor。
6. 运行 Task 相关测试。
7. 自动衔接 `team-task-verify`，不在验证前提交。
8. 验证不是 `verified` 时停止，不创建 commit。
9. 验证通过后，只暂存本 Task 的代码、测试和必要配置；排除 `team-spec/` 和无关改动。
10. 创建一个逻辑 commit，推荐信息为 `T001: {task title}`。
11. 确认 commit 已创建且工作区没有遗留的本 Task 代码变更。
12. 回写 Task：`Status: committed`、`Commit: {sha}`、实现、验证命令和残余风险；不得暂存该回写。

## TDD 循环

```text
RED：写一个行为测试并确认失败
GREEN：写最小实现让测试通过
REFACTOR：相关测试通过后再整理结构
```

测试应走真实公共路径；Mock 只用于外部系统、时间、随机性、网络或昂贵依赖。

## Commit 合同

- 一个 Task 对应一个最终逻辑 commit。
- commit 只能在 Task 验证通过后创建。
- commit 范围必须与 Task 验收标准一致。
- 不提交 `team-spec/`、无关格式化、顺手重构或其他 Task 的提前实现。
- 若实现无法安全形成一个 commit，应停止并回到拆解技能调整边界。
- 创建 commit 不代表允许 push；远端操作只由 Spec 级技能执行。

## 完成标准

- 当前分支是该 slug 的 Spec 共享分支。
- Task 的所有验收标准通过独立验证。
- 已创建且只创建一个对应逻辑 commit。
- Task 文件记录 `committed` 和有效 commit SHA。
- 没有 push、远端 Issue、PR 或 MR。
- `team-spec/` 回写保持未暂存。

## 最终回复

必须包含：

- Task 路径、ID、slug 和共享分支。
- 主要代码和测试变化。
- 验收覆盖、验证命令和结果。
- commit SHA、commit 信息和范围。
- 未提交的 `team-spec/` 回写。
- 跳过项、残余风险和下一步。
