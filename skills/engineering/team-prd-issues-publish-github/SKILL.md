---
name: team-prd-issues-publish-github
description: 将 team-spec/issues/{slug}/ 下的本地 issue 草稿按依赖顺序批量发布到 GitHub Issues，并回写发布结果，支持 dry-run、幂等检查与部分失败重试。Batch publish local issue drafts under team-spec/issues/{slug}/ to GitHub Issues in dependency order, with write-back status, dry-run, idempotency checks, and retry support.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# 批量发布 GitHub Issues

这个技能用于把 `team-prd-to-issues` 生成的本地 issue 草稿，批量发布到 GitHub Issues。它关注“可重复执行、可追踪、可恢复”，避免重复创建和依赖顺序错误。

v1 仅支持 GitHub。不要在同一个技能中混合 GitHub 与 GitLab 发布逻辑；GitLab 请使用独立技能。

## 输入物

主输入：

- `team-spec/issues/{slug}/` 下的 issue 草稿文件。

必须参数：

- 平台地址（默认 `https://github.com`；GitHub Enterprise 必须提供自定义地址）。
- 仓库定位：`owner/repo`。
- 认证 token（必须通过环境变量提供，不写入任何文件）。
- 目标 slug 或明确的 issue 目录路径（如 `team-spec/issues/{slug}/`）。

建议参数：

- 默认 labels。
- milestone。
- assignee 映射规则。
- `dry-run` 开关（默认建议先开）。

前置条件：

- PRD 交接评审已获得三方签字确认。
- 可追溯的交接文档已存在（通常为 `team-spec/prd/{slug}-handoff.md`）。
- `team-prd-to-issues` 已产出可发布草稿。
- 需要有效 token 且具备 GitHub Issues 写权限（常见为 `repo` 或等效最小权限）。

如果无法唯一确定 slug、仓库或 token 来源，必须停止并向用户确认，不得猜测。

## 输出物

- GitHub Issues（按依赖顺序批量创建）。
- 本地回写结果（每个 issue 草稿都应记录）：
  - 远端 issue 编号。
  - 远端 issue URL。
  - 发布状态（created / skipped / failed）。
  - 错误原因（如失败）。
  - 发布时间戳。
- 批量发布汇总：
  - 总数、成功数、跳过数、失败数。
  - 失败清单与重试建议。

优先回写原 issue 草稿；若原文件结构不便回写，再在同目录新增发布结果文件。

## 发布规则

- 按依赖顺序发布：先 blocker，再依赖它的 issue。
- 先做参数与权限检查，再执行真正发布。
- 默认先执行 `dry-run` 预览发布计划，用户确认后再正式发布。
- 幂等优先：重复执行时，不应重复创建同一 issue。
- 出现部分失败时继续处理可执行项，并保留失败清单用于补偿重试。

## 幂等策略

每个本地 issue 在发布前必须做唯一性检查。推荐组合键：

- 本地 issue 文件名（`team-prd-to-issues` 已生成的 `{local-seq}-{short-issue-slug}.md` 格式，其中 `local-seq` 直接取自现有文件名前缀，用作本地唯一标识，不是远端 GitHub issue 编号）。
- issue 标题（`Title`）。

若远端已存在匹配项，则标记为 `skipped` 并回写现有 issue URL，不重复创建。

推荐匹配逻辑：

- 第一步：按本地文件名键精确匹配（完全一致）。
- 第二步：在同一文件名键候选内按标题精确匹配（去除首尾空白后比较）。
- 第三步：若仍有多个候选，停止自动发布该条并标记为 `failed`，要求人工确认，避免误关联。

## 建议流程

1. 确认 slug、仓库、平台地址、token 来源与权限范围。
2. 读取 `team-spec/issues/{slug}/` 下所有待发布 issue 草稿。
3. 解析 `Blocked by` 关系并生成依赖有向图。
4. 检查循环依赖；若存在循环依赖，停止并输出冲突清单。
5. 生成拓扑顺序发布计划。
6. 先执行 `dry-run`，输出将创建/跳过的完整清单。
7. 用户确认后执行正式发布。
8. 每创建一个 issue 即刻回写本地结果，避免中断后丢失进度。
9. 对失败项按可配置策略重试；重试后仍失败则保留失败状态并汇总。
10. 输出批量发布报告和下一步建议（如补充权限、修复依赖或手动处理失败项）。

## 错误与恢复策略

- 认证失败：立即停止，不执行发布。
- 权限不足：立即停止，并提示所需权限范围。
- 单条数据错误（标题缺失、格式不合法等）：标记该条失败，继续其余可执行项。
- 网络或临时 API 错误：按重试策略处理，超过上限后标记失败。
- 已发布部分不回滚；使用回写状态与汇总清单做后续补偿。

## 安全要求

- token 只能从环境变量读取。
- 不记录、不回显 token。
- 不将 token 写入 `team-spec/` 或任何仓库文件。

## 完成标准

- 目标 slug 下 issue 已按依赖顺序处理完成（创建/跳过/失败均有记录）。
- 每个本地 issue 草稿都有可追踪的回写状态。
- 输出了可执行的失败重试清单。
- 结果可重复执行，且不会产生重复 issue。
