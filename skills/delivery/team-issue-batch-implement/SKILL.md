---
name: team-issue-batch-implement
description: 批量编排多个 AFK 工程 issue 的实现，按依赖顺序逐个调用单 issue 实现与验证流程，保留失败即停和可恢复续跑边界。Batch orchestrate multiple AFK engineering issues in dependency order while delegating each slice to single-issue implementation and verification workflows.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 批量实现 issue
  - 连续处理多个 issue
  - 批量跑工程任务
  - 一次实现多个 AFK issue
  - batch implement issues
  - implement multiple issues
  - run issue queue
  - process AFK issues in bulk
---

# Issue 批量实现编排

这个技能用于在 `team-prd-to-issues` 或 `team-tech-debt-to-issues` 产出多个工程 issue 后，恢复批量处理能力。它只做队列编排、依赖排序、停机条件和进度汇总；单个 issue 的实现仍必须交给 `team-issue-implement`，验证仍必须交给 `team-issue-verify`。

核心原则：批量选择，单个执行，逐个验证，失败即停，可恢复继续。

## 运行时配置

在读取 issue 目录、PRD、评审或代码前，先读取目标项目根目录的 `team-spec/config.yml`。如果存在 `access_policy`，必须先应用目录访问边界，再进入任何批量执行或写入流程。

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

- `language`：批量计划、对话回复和输出汇总的统一语言。
- `version_control`：仅在需要衔接发布技能或判断主干分支时使用。
- `access_policy`：目录访问策略索引。缺失时默认只读；如果本次任务必须写入目标项目而配置又缺失，先询问是否创建最小配置。

## 输入物

主输入必须能唯一定位一组 issue：

- `team-spec/active/{slug}/issues/`
- 或用户显式提供的多个本地 issue 文件路径。

参考输入可以包括：

- `team-spec/config.yml`，用于确定语言、版本管理系统、主干分支和贡献方式。
- `team-spec/active/{slug}/prd/prd.md`，用于确认父 PRD 与需求边界。
- `team-spec/active/{slug}/spec/reviews.md`，用于识别风险、HITL 决策点和 blocker。
- `team-spec/CONTEXT.md`、`team-spec/decisions/`、`team-spec/active/{slug}/spec/CONTEXT.md`、`team-spec/active/{slug}/spec/decisions/`。
- 当前代码库、测试、ADR、验证命令和现有实现。

必须先确定唯一 slug、issue 目录或明确的 issue 文件列表。如果无法唯一判断，要停止并要求用户提供 slug、目录或文件列表，不要扫描 `team-spec/archive/` 猜测。

## 输出物

- 批量执行计划：可执行队列、跳过项、阻塞项、依赖顺序和批量上限。
- 每个已处理 issue 的实现和验证结果，仍回写原 issue 文件。
- 可选批量汇总报告：`team-spec/active/{slug}/issues/batch-implementation.md`，用于记录本轮队列、完成项、停止原因、验证命令和剩余队列。

本技能不直接修改 PRD、规格评审或产品决策。发现需求问题时，应停止并反馈给上游技能或人工决策。

## 固定脚本

批量执行前，优先使用本技能目录下的固定脚本生成队列计划，不要临时手写依赖排序：

```text
./scripts/plan_issue_batch.py
```

脚本能力：

- 读取 `team-spec/active/{slug}/issues/` 或显式 `--issues-dir`。
- 解析 issue 标题、`Type`、`Status`、`Blocked by` 和文件名前缀。
- 按 `Blocked by` 做依赖排序，识别循环依赖、缺失依赖、HITL issue 和已完成 issue。
- 输出可批量处理的 AFK 队列；默认只生成计划，不执行代码变更。
- 支持 `--limit N` 限制本轮最多处理的 issue 数量。
- 支持 `--json` 输出机器可读计划。

推荐用法：

```sh
python3 {skill_dir}/scripts/plan_issue_batch.py --slug {slug}
python3 {skill_dir}/scripts/plan_issue_batch.py --slug {slug} --limit 3 --json
```

其中 `{skill_dir}` 是当前技能目录。技能内部定位脚本时应使用相对 `SKILL.md` 的路径 `./scripts/plan_issue_batch.py`，执行命令时再解析成实际文件路径。

## 批量边界

默认只处理 `AFK（可独立执行，无需人工决策）` issue。以下 issue 必须跳过：

- `HITL（需要人工介入）` issue。
- 缺少验收标准的 issue。
- `Blocked by` 指向未完成、缺失、循环或 HITL issue 的任务。
- 已经处于 `ready for PR`、`PR created`、`MR created`、`done`、`completed` 或等价完成状态的 issue。
- 实现范围明显跨出父 PRD 或当前 slug 的 issue。

默认批量上限为 3 个 issue。用户明确要求“全部可执行 issue”时可以处理更多，但仍必须逐个验证，且任何失败都立即停止。

## 工作流

1. 确定 slug、issue 目录或用户指定的 issue 文件列表。
2. 读取 `team-spec/config.yml`、父 PRD、评审报告和必要上下文。
3. 检查工作区状态。若存在与本轮无关的未提交变更，先说明风险并停止，除非用户明确要求在当前工作区继续。
4. 运行 `./scripts/plan_issue_batch.py` 生成执行队列。
5. 向用户展示批量计划：本轮将处理哪些 issue、跳过哪些 issue、为什么跳过、批量上限是多少。
6. 如果用户已明确要求批量执行且队列规模不超过默认上限，可以继续；否则先等待用户确认。
7. 按队列顺序对每个 issue 执行 `team-issue-implement` 的完整工作流。
8. 每个 issue 实现结束后，立即执行 `team-issue-verify`。
9. 只有当前 issue 达到 `ready for PR` 或用户明确接受的完成状态，才继续下一个 issue。
10. 记录本轮完成项、验证命令、停止原因、未处理队列和需要人工介入的事项。

## 停止条件

遇到以下任一情况，必须停止批量执行：

- 当前 issue 验证结果不是 `ready for PR`。
- 测试失败、验证命令缺失且无法从项目文档推断。
- 发现未解决的 HITL 决策点。
- 依赖关系变化、循环依赖、缺失 blocker 或 blocker 未完成。
- 当前实现需要修改 PRD、规格评审或产品决策。
- 代码变更范围明显超出当前 issue 或混入无关重构。
- 工作区出现无法归因到本轮 issue 的新变更。

停止不是失败。停止后输出已完成进度、停止原因和下一步可选动作，确保用户可以修正后继续批量执行。

## 执行约束

- 不要把多个 issue 合并成一个实现说明；每个 issue 都必须保留独立实现记录和验证记录。
- 不要跳过 `team-issue-verify`。
- 不要自动执行 `git commit`、`git push`、创建 PR/MR 或发布 issue。
- 不要自动修改 `team-spec/archive/`。
- 不要为了跑完整批量而降低测试或验收标准。
- 如果批量过程中发现拆分过薄或依赖设计错误，应停止并建议回到 `team-prd-to-issues` 合并或重排。

## 完成标准

最终回复必须包含：

- 本轮批量范围和实际处理数量。
- 已完成 issue 列表及各自验证状态。
- 跳过或阻塞的 issue 及原因。
- 运行过的关键验证命令和结果。
- 是否保留未提交本地变更，以及没有执行 `git commit` / `git push`。
- 有序号的“下一步可选”，例如继续下一批、处理 HITL、回到拆解合并过薄 issue、进入 PR/MR 创建。

推荐“下一步可选”：

```md
## 下一步可选

1. `team-issue-batch-implement`：继续处理下一批可执行 AFK issue。
2. 完成人工决策：先处理被 HITL 或 blocker 卡住的 issue。
3. `team-prd-to-issues`：如果发现 issue 过薄或依赖不合理，回到拆解阶段合并或重排。
4. `team-issue-create-pr-github` / `team-issue-create-mr-gitlab`：当前批次已验证完成后，按项目平台创建 PR/MR。
```
