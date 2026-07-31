---
name: team-spec-create-mr-gitlab
description: 推送一个 Spec 的共享分支，并为其全部已提交 Tasks 创建一个 GitLab Merge Request。Push one spec branch and create a single GitLab Merge Request covering all committed tasks in that spec.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 为 Spec 创建 GitLab MR
  - 所有 Task 完成后提 MR
  - 推送需求分支并创建 MR
  - create GitLab MR for spec
  - open MR after all tasks
  - push spec branch and create MR
---

# 为 Spec 创建 GitLab Merge Request

在同一 slug 的所有必需 Tasks 已验证并分别提交后，推送唯一 Spec 分支并创建一个 GitLab Merge Request。

## 触发边界

- 适合触发：与 slug 完全同名的 `{slug}` 分支已包含全部 Task commits，需要一次性创建 MR。
- 不适合触发：仍有未实现或未提交 Task 时继续使用 Task 实现技能；只创建远端跟踪 Issue 时使用 `team-spec-create-issue-gitlab`。

## 运行时配置

先读取 `team-spec/config.yml`，应用语言、访问策略和版本管理配置。source/target project、remote 和主干优先级为：用户参数 > 已确认配置 > git 证据 > 询问用户。

GitLab 地址必须从 `GITLAB_URL` 读取。

## 公共写作风格

生成 MR 标题、正文和用户可见说明前，读取配置中的 `writing_style.guide`（如果存在）。Closing keyword、Task/commit 映射和安全合同优先。

## 输入物

主输入必须是唯一 `{slug}`，默认读取：

- `team-spec/active/{slug}/prd/prd.md`
- `team-spec/active/{slug}/tasks/T*.md`
- `team-spec/active/{slug}/DELIVERY.md`（如果存在）
- 当前 `{slug}` 分支及其提交历史
- `team-spec/config.yml`

不再接受单个 Task 作为 MR 聚合边界。缺少 PRD、Tasks、共享分支或唯一 slug 时停止。

## 输出物

- 一个覆盖该 Spec 全部 Task commits 的 GitLab MR。
- MR URL、source/target project、source/target branch。
- `DELIVERY.md` 中的 branch、MR URL 和 Task/commit 汇总。

Task 状态保持 `committed`，不得回写为 `mr-created`。

## 固定脚本

优先使用：

```text
./scripts/create_gitlab_mr.py
```

默认 dry-run：

```sh
GITLAB_URL=https://gitlab.example.com python3 {skill_dir}/scripts/create_gitlab_mr.py --slug {slug}
```

正式执行：

```sh
GITLAB_URL=https://gitlab.example.com GITLAB_TOKEN=... python3 {skill_dir}/scripts/create_gitlab_mr.py --slug {slug} --execute
```

常用参数：

- `--target-branch main`
- `--source-remote origin`
- `--target-remote upstream`
- `--source-project namespace/fork`
- `--target-project namespace/project`
- `--title "[Component] Add requirement"`
- `--body-file path/to/body.md`
- `--issue-iid 123`
- `--draft`
- `--label label`
- `--assignee-id id`
- `--reviewer-id id`
- `--language zh-CN`
- `--json`

脚本只推送已有 commits 和创建 MR，不执行 git add、commit、stash 或 rebase。

## 创建前检查

必须全部满足：

- 当前分支严格等于 `{slug}`，不得带 `spec/` 前缀。
- 所有 T-numbered Task 状态均为 `committed`。
- 每个 Task 都记录 commit SHA。
- 每个 SHA 存在、是当前 HEAD 的祖先，并位于目标主干到当前分支的提交范围。
- 分支至少包含一个 Task commit。
- 目标主干到当前分支之间不存在未映射到 Task 的额外 commit。
- 非 `team-spec/` 工作区和暂存区干净。
- source/target project、remote 和主干明确。

任一条件不满足时停止。

## MR 合同

- 一个 slug 最多一个打开的 GitLab MR。
- 标题来自显式参数或 PRD一级标题。
- 正文从完整 Spec/PRD 生成。
- 正文包含所有 Task ID、标题和 commit SHA。
- 如果存在 Spec 级 GitLab Issue，正文使用 `Fixes #{iid}`。
- 没有远端 Issue 时不强制 Closing keyword。
- MR 只覆盖一个 slug 的共享分支。

## 工作流

1. 读取配置、slug、PRD、Tasks 和 `DELIVERY.md`。
2. 校验共享分支、Task 状态、SHA、base 范围和工作区。
3. 推断 source/target project、remote 和主干。
4. 生成标题、正文和 Task/commit 映射。
5. 运行 dry-run。
6. 用户已要求正式执行时追加 `--execute`。
7. 一次性 push 当前 Spec 分支。
8. 创建或返回已有打开 MR。
9. 回写 `DELIVERY.md`，不得暂存或提交。

## 安全要求

- token 只从环境变量读取。
- 默认 dry-run。
- 正式 API 请求可输出无敏感信息的调试信息，不输出 token。
- 不自动生成收尾 commit。
- 不暂存或提交 `team-spec/`。
- 发现非 `team-spec/` 未提交变化时停止。
- 不修改历史，不自动 rebase、reset 或 stash。

## 完成标准

- Spec 分支已推送到正确 source remote。
- 只创建一个覆盖全部 Task commits 的 MR。
- MR 正文包含完整 Task/commit 映射。
- Task 状态仍为 `committed`。
- `DELIVERY.md` 已记录 MR URL 和分支。

## 最终回复

必须包含：

- dry-run 或 execute 状态。
- slug、source/target project 和分支。
- Task 数量与 commit SHA 汇总。
- MR URL和关联的 Spec Issue（如果有）。
- `DELIVERY.md` 回写和剩余未提交 `team-spec/` 变化。
- 失败阶段和安全重试入口。
