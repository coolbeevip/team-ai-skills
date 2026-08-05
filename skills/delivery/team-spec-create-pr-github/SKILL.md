---
name: team-spec-create-pr-github
description: 推送一个 Spec 的共享分支，并为其全部已提交 Tasks 创建一个 GitHub Pull Request。Push one spec branch and create a single GitHub Pull Request covering all committed tasks in that spec.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 为 Spec 创建 GitHub PR
  - 所有 Task 完成后提 PR
  - 推送需求分支并创建 PR
  - create GitHub PR for spec
  - open PR after all tasks
  - push spec branch and create PR
---

# 为 Spec 创建 GitHub Pull Request

在同一 slug 的所有必需 Tasks 已验证并分别提交后，推送唯一 Spec 分支并创建一个 GitHub Pull Request。

## 触发边界

- 适合触发：与 slug 完全同名的 `{slug}` 分支已包含全部 Task commits，需要一次性创建 PR。
- 不适合触发：仍有未实现或未提交 Task 时继续使用 Task 实现技能；只创建远端跟踪 Issue 时使用 `team-spec-create-issue-github`。

## 运行时配置

先读取 `team-spec/config.yml`，应用语言、访问策略和版本管理配置。文件不存在或正式创建 PR 所需字段无法从参数与 Git 证据唯一确定时，先使用 `team-config-init` 创建或增量补全；本技能不得自行回写配置。PR 语言按“本次 `--language` 或用户明确指定 > `version_control.language` > 顶层 `language` > `en-US`”确定。source/target repo、remote 和主干优先级为：用户参数 > 已确认配置 > git 证据 > 询问用户。

## 公共写作风格

生成 PR 标题、正文和用户可见说明前，读取配置中的 `writing_style.guide`（如果存在）。Closing keyword、Task/commit 映射和安全合同优先。

## 输入物

主输入必须是唯一 `{slug}`，默认读取：

- `team-spec/active/{slug}/prd/prd.md`
- `team-spec/active/{slug}/tasks/T*.md`
- `team-spec/active/{slug}/DELIVERY.md`（如果存在）
- 当前 `{slug}` 分支及其提交历史
- `team-spec/config.yml`

不再接受单个 Task 作为 PR 聚合边界。缺少 PRD、Tasks、共享分支或唯一 slug 时停止。

## 输出物

- 一个覆盖该 Spec 全部 Task commits 的 GitHub PR。
- PR URL、source/target repo、source/target branch。
- `DELIVERY.md` 中的 branch、PR URL 和 Task/commit 汇总。

Task 状态保持 `committed`，不得回写为 `pr-created`。

## 固定脚本

优先使用：

```text
./scripts/create_github_pr.py
```

默认 dry-run：

```sh
python3 {skill_dir}/scripts/create_github_pr.py --slug {slug}
```

正式执行：

```sh
GITHUB_TOKEN=... python3 {skill_dir}/scripts/create_github_pr.py --slug {slug} --execute
```

常用参数：

- `--target-branch main`
- `--source-remote origin`
- `--target-remote upstream`
- `--source-repo owner/fork`
- `--target-repo owner/repo`
- `--github-url https://github.example.com`
- `--title "[Component] Add requirement"`
- `--body-file path/to/body.md`
- `--issue-number 123`
- `--draft`
- `--assignee login`
- `--language zh-CN`
- `--json`

脚本只推送已有 commits 和创建 PR，不执行 git add、commit、stash 或 rebase。

## 创建前检查

必须全部满足：

- 当前分支严格等于 `{slug}`，不得带 `spec/` 前缀。
- 所有 T-numbered Task 状态均为 `committed`。
- 每个 Task 都记录 commit SHA。
- 每个 SHA 存在、是当前 HEAD 的祖先，并位于目标主干到当前分支的提交范围。
- 分支至少包含一个 Task commit。
- 目标主干到当前分支之间不存在未映射到 Task 的额外 commit。
- 非 `team-spec/` 工作区和暂存区干净。
- source/target repo、remote 和主干明确。

任一条件不满足时停止，不允许用 PR 补救未完成 Task。

## PR 合同

- 一个 slug 最多一个打开的 GitHub PR。
- 标题来自显式参数或 PRD 一级标题。
- 正文从完整 Spec/PRD 生成。
- PRD/Task 语言与 PR 语言不同时，生成对应语言的标题和完整正文，并通过 `--title`、`--body-file` 传入；不修改源文档。Task ID、commit SHA、代码标识符、命令、路径和专有名词保持原样。
- 正文包含所有 Task ID、标题和 commit SHA。
- 如果 `DELIVERY.md` 或参数提供 Spec 级 GitHub Issue，正文使用 `Fixes #{number}`。
- 没有远端 Issue 时不强制 Closing keyword。
- PR 只覆盖一个 slug 的共享分支。

## 工作流

1. 读取配置、slug、PRD、Tasks 和 `DELIVERY.md`。
2. 校验共享分支、Task 状态、SHA、base 范围和工作区。
3. 推断 source/target repo、remote 和主干。
4. 生成标题、正文和 Task/commit 映射。
5. 运行 dry-run。
6. 用户已要求正式执行时追加 `--execute`。
7. 一次性 push 当前 Spec 分支。
8. 创建或返回已有打开 PR。
9. 回写 `DELIVERY.md`，不得暂存或提交。

## 安全要求

- token 只从环境变量读取。
- 默认 dry-run。
- 不自动生成任何收尾 commit。
- 不暂存或提交 `team-spec/`。
- 发现非 `team-spec/` 未提交变化时停止。
- 不修改历史，不自动 rebase、reset 或 stash。

## 合并后同步主干

PR 合并后，提醒用户同步本地主干，确保下次创建 Spec 分支时基于最新代码：

- `contribution_model = direct`：`git switch {trunk_branch} && git pull {source_remote} {trunk_branch}`
- `contribution_model = fork-pull`：`git switch {trunk_branch} && git pull {target_remote} {trunk_branch} && git push {source_remote} {trunk_branch}`

不得自动执行同步操作，只提供可复制命令供用户确认。

## 完成标准

- Spec 分支已推送到正确 source remote。
- 只创建一个覆盖全部 Task commits 的 PR。
- PR 正文包含完整 Task/commit 映射。
- Task 状态仍为 `committed`。
- `DELIVERY.md` 已记录 PR URL 和分支。

## 最终回复

必须包含：

- dry-run 或 execute 状态。
- slug、source/target repo 和分支。
- Task 数量与 commit SHA 汇总。
- PR URL和关联的 Spec Issue（如果有）。
- `DELIVERY.md` 回写和剩余未提交 `team-spec/` 变化。
- PR 合并后的主干同步命令（仅展示，不自动执行）。
- 失败阶段和安全重试入口。
