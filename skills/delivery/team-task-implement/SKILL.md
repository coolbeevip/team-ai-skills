---
name: team-task-implement
description: 在 Spec 共享分支实现单个工程 Task，验证通过并经用户检查差异、明确确认后创建本地逻辑 commit。Implement one task on its shared spec branch, pausing for user diff review and confirmation before the local commit.
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

实现 `team-prd-to-tasks` 或 `team-tech-debt-to-tasks` 生成的一个 Task。所有同 slug Task 共用与 slug 完全同名的 `{slug}` 分支，不添加 `spec/` 前缀；每个 Task 验证通过后，必须先让用户检查实际差异并确认，再形成一个本地逻辑 commit。

## 触发边界

- 适合触发：用户指定一个明确 Task，要求实现、验证并在本地提交。
- 不适合触发：多个 Task 连续执行时使用 `team-task-batch-implement`；只审查现有实现时使用 `team-task-verify`；创建 PR/MR 时使用 Spec 级创建技能。

## 运行时配置

在读取 Task、代码或测试前，先读取 `team-spec/config.yml`。文件不存在或实现、提交所需字段缺失时，先使用 `team-config-init` 创建或增量补全；本技能不得自行回写配置。应用 `language`、`version_control`（含 `trunk_branch`、`contribution_model`、`source_remote`、`target_remote`）和 `access_policy`；缺少写权限或无法确定主干分支时停止。

Commit message 语言按“用户对本次提交的明确指定 > `version_control.language` > 顶层 `language` > `en-US`”确定。交付语言与 Task 文档语言不同时，只转换变更摘要，不修改 Task 原文；代码标识符和专有名词保持原样。Commit message 只写简洁的变更摘要，不添加 `T001` 等 Task ID 前缀或后缀。

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
- 用户检查差异并明确确认后创建的一个本地逻辑 commit。
- 等待确认时 Task 文件中的 `Status: verified`；提交后更新为 `Status: committed`，并记录 commit SHA、实现和验证结果。

不得 push、创建远端 Issue、PR 或 MR。`team-spec/` 下的运行时文件不得加入代码 commit。

## 共享分支合同

1. 从 `team-spec/config.yml` 确定 `trunk_branch`、`contribution_model`、`source_remote` 和 `target_remote`。
2. 将 Spec 分支计算为 `{slug}`，不得添加 `spec/` 或其他前缀。
3. 当前分支不是 Spec 分支时：
   - 工作区有未提交变更则停止。
   - 分支已存在：切换到该分支，不执行主干同步。
   - 分支不存在：先同步主干，再从主干创建。
4. 同步主干规则（仅在创建新分支时执行）：
   - `contribution_model = direct`（source_remote 与 target_remote 相同）：`git switch {trunk_branch}`，然后 `git fetch {source_remote} {trunk_branch}`，再执行 `git pull --ff-only {source_remote} {trunk_branch}`。切换主干前必须确认工作区干净；无法 fast-forward 时停止，不自动 merge 或 rebase。
   - `contribution_model = fork-pull`（target_remote 为上游仓库）：`git fetch {target_remote} {trunk_branch}` 然后 `git switch {trunk_branch}` 然后 `git merge {target_remote}/{trunk_branch}`。
   - 同步后，`git switch -c {slug} {trunk_branch}` 创建新分支。
5. 后续 Task 必须继续使用同一分支。
6. 不创建 Task 独立分支，不把其他 slug 的 commit 混入当前分支。

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
9. 验证通过后、暂存任何文件之前，生成提交前检查摘要并进入“提交前确认”。
10. 用户选择继续修改时，完成修改、重新运行受影响验证并再次生成检查摘要；旧确认立即失效。
11. 只有用户明确选择“接受当前实现并提交”后，才暂存本 Task 的代码、测试和必要配置；排除 `team-spec/` 和无关改动。
12. 创建一个逻辑 commit，推荐信息为 `{concise localized change summary}`，例如 `Add filtered export support`；不得添加 Task ID，标题使用已确定的版本控制交付语言。
13. 确认 commit 已创建且工作区没有遗留的本 Task 代码变更。
14. 回写 Task：`Status: committed`、`Commit: {sha}`、实现、验证命令和残余风险；不得暂存该回写。

## TDD 循环

```text
RED：写一个行为测试并确认失败
GREEN：写最小实现让测试通过
REFACTOR：相关测试通过后再整理结构
```

测试应走真实公共路径；Mock 只用于外部系统、时间、随机性、网络或昂贵依赖。

## 提交前确认

验证通过后、暂存任何文件之前，必须暂停自动流程，让用户有机会在本地检查实际代码差异。不得先执行 `git add`，否则普通 `git diff` 无法直接展示待提交变化。

先向用户提供：

- 当前 Task、分支和验证状态。
- 修改及新增文件清单、`git diff --stat` 摘要和拟提交范围。
- 已运行的验证命令、结果、跳过项和残余风险。
- 可在本地使用的检查入口：`git status --short`、`git diff --stat` 和 `git diff`。这些命令只写在用户可复制的说明中，不添加环境专用执行包装器。

然后给出以下选择并等待用户明确回复：

1. `✅ 接受当前实现并提交`：按已展示范围暂存并创建本地 commit。
2. `🔍 暂不提交，我要先查看 diff`：保持所有实现未暂存、未提交，等待用户检查后再次决定。
3. `🔄 继续修改当前 Task`：询问或读取修改意见，修改并重新验证，再回到本确认节点。
4. `⏸️ 暂停并保留当前改动`：停止本轮，不提交、不回滚，保持 `Status: verified` 和当前工作区。

不得把用户在任务开始时说的“实现并提交”、AFK 授权或批量执行授权视为这次提交确认。确认只对当前已展示的 Task、文件范围和实际 diff 有效；确认后只要代码、测试或必要配置再次变化，就必须重新验证并再次确认。

提交前确认是代码交付控制点，不是产品或技术方案决策，不改变 Task 原有的 AFK/HITL 分类。

## Commit 合同

- 一个 Task 对应一个最终逻辑 commit。
- commit 只能在 Task 验证通过后创建。
- commit 只能在用户查看提交前摘要并明确确认当前实际 diff 后创建。
- commit 范围必须与 Task 验收标准一致。
- commit message 使用简洁的祈使句或变更摘要，不包含 `T001` 等 Task ID；Task 与 commit 的关联只通过 Task 文件中的 `Commit: {sha}` 和后续 Task/commit 映射维护。
- 不提交 `team-spec/`、无关格式化、顺手重构或其他 Task 的提前实现。
- 若实现无法安全形成一个 commit，应停止并回到拆解技能调整边界。
- 创建 commit 不代表允许 push；远端操作只由 Spec 级技能执行。

## 完成标准

- 当前分支是该 slug 的 Spec 共享分支。
- Task 的所有验收标准通过独立验证。
- 用户已基于当前实际 diff 明确确认提交。
- 已创建且只创建一个对应逻辑 commit。
- Task 文件记录 `committed` 和有效 commit SHA；如果用户选择查看、继续修改或暂停，则保持 `verified`，不得伪装为完成。
- 没有 push、远端 Issue、PR 或 MR。
- `team-spec/` 回写保持未暂存。

## 最终回复

必须包含：

- Task 路径、ID、slug 和共享分支。
- 主要代码和测试变化。
- 验收覆盖、验证命令和结果。
- 提交前确认结果；已提交时包含 commit SHA、commit 信息和范围，未提交时明确说明当前改动仍可用 `git diff` 检查。
- 未提交的 `team-spec/` 回写。
- 跳过项、残余风险和下一步。
