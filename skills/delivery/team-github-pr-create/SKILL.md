---
name: team-github-pr-create
description: 将已完成的单个 issue 分支推送到 GitHub，并创建标题和正文都关联 issue 编号的 Pull Request。Create a GitHub Pull Request for a completed issue branch, pushing the branch and linking the issue number in both title and body.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 创建 GitHub PR
  - 创建 Pull Request
  - 给这个 issue 建 PR
  - 推送分支并创建 PR
  - create GitHub PR
  - open pull request
  - create pull request for issue
  - push branch and open PR
---

# 创建 GitHub Pull Request

这个技能用于在 `team-issue-implement` 和 `team-issue-verify` 后，把已经提交好的当前 issue 分支推送到 GitHub，并创建关联 issue 的 Pull Request。它关注“少出错、可预览、可追踪”，避免手动复制 issue 编号、标题和正文时遗漏关联。

v1 仅支持 GitHub Pull Request。GitLab Merge Request 应使用独立技能。

## 固定脚本

创建 GitHub PR 时，优先使用本技能目录下的固定脚本，不要临时重写 GitHub API 调用代码：

```text
./scripts/create_github_pr.py
```

脚本能力：

- 读取当前 git 分支，默认从分支名推断 issue 编号。
- 从显式参数或 git remote 推断 source repo 与 target repo。
- 默认 dry-run，只输出将推送的分支和将创建的 PR。
- `--execute` 时先做执行前确认，再 push 当前分支并创建 GitHub Pull Request。
- 脚本只允许推送已有提交，不负责 `git add`、`git commit`、自动暂存或自动生成本地提交。
- PR 标题和正文都包含 issue 编号，正文默认使用 `Closes #123` 以便 GitHub 自动关联并在合并后关闭 issue。
- 可指定 target branch、source remote、target remote、title、draft 和 assignee。
- 执行前会检查被 Git 追踪但又命中 `.gitignore` 规则的文件，并要求人类确认是否继续。

推荐 dry-run：

```sh
python3 {skill_dir}/scripts/create_github_pr.py
```

用户确认后正式执行：

```sh
GITHUB_TOKEN=... python3 {skill_dir}/scripts/create_github_pr.py --execute
```

其中 `{skill_dir}` 是当前技能目录。技能内部定位脚本时应使用相对 `SKILL.md` 的路径 `./scripts/create_github_pr.py`，执行命令时再解析成实际文件路径。

常用参数：

- `--issue-number 123`：显式指定要关联的 GitHub issue 编号。
- `--target-branch main`：指定目标分支；如果不传，脚本会推断并在 `--execute` 前要求人类确认。
- `--source-remote origin`：指定推送当前分支的 remote。
- `--target-remote upstream`：指定 PR 目标项目 remote。
- `--target-repo owner/repo`：显式指定目标仓库，优先级高于 remote 推断。
- `--source-repo owner/repo`：显式指定 source repo，用于 fork 工作流。
- `--title "Resolve #123: ..."`：显式指定 PR 标题。
- `--draft`：创建 Draft PR。
- `--assignee octocat`：可重复传入多个 assignee login。
- `--json`：输出机器可读 JSON。

## 输入物

优先读取：

- 当前 git 分支名，通常应包含或等于 issue 编号，例如 `123`、`issue-123`、`123-add-export-filter`。
- 当前提交历史；工作区必须干净，不能包含未提交变更。
- `team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.md`，如果能从分支、用户输入或对话中确定。
- GitHub issue 编号或 URL，如果用户提供。
- Git remote 信息，用于推断 source repo 和 target repo。

必须参数或可推断信息：

- GitHub 平台地址（默认 `https://github.com`；GitHub Enterprise 必须提供自定义地址）。
- 认证 token（必须通过环境变量提供，不写入任何文件）。
- 当前分支名。
- issue 编号。
- source repo 与 target repo。
- target branch。

如果无法唯一确定 issue 编号、source repo、target repo、token 来源或 target branch，必须停止并向用户确认，不得猜测。

## 仓库定位规则

当用户没有显式提供 GitHub repo 时，按以下规则推断：

- target repo：优先使用 `--target-remote`；否则使用名为 `upstream` 的 GitHub remote；否则使用当前分支 tracking remote；仍不唯一时要求用户指定。
- source repo：优先使用 `--source-remote`；否则使用当前分支 tracking remote；否则使用 `origin`；如果只有一个 GitHub remote，则使用这个 remote。
- 如果 source repo 和 target repo 相同，创建普通 PR。
- 如果 source repo 和 target repo 不同，按 fork 工作流创建跨仓库 PR。

自建 GitHub Enterprise 场景下，remote host 必须与平台地址一致；如果不一致，应要求用户确认平台地址和仓库。

## 输出物

- GitHub Pull Request。
- 最终回复中的 PR URL、source branch、target branch、关联 issue 编号。
- 如果项目有本地 issue 草稿，可回写或提示用户记录 PR URL。

## PR 标题与正文规则

- 标题必须包含 issue 编号，例如 `Resolve #123: Add export filter`。
- 正文必须包含 GitHub closing keyword，例如 `Closes #123`。
- 正文应包含：
  - 关联 issue。
  - 主要变更摘要。
  - 验证命令与结果。
  - 风险、未覆盖测试或需要 reviewer 注意的事项。

如果用户没有提供标题，默认标题从 issue 编号和当前分支生成。不要创建没有 issue 关联的 PR，除非用户明确要求。

## 建议流程

1. 确认当前分支、issue 编号、source remote、target repo 和 target branch。
2. 检查工作区状态；如果存在未提交变更，停止并要求用户先完成实现验证和人工提交，不得代替用户执行 `git add` 或 `git commit`。
3. 使用固定脚本执行默认 dry-run，预览 push 和 PR 创建计划。
4. 如果目标分支是推断出来的，或工作区里存在被追踪但命中 `.gitignore` 的文件，执行前必须向人类确认。
5. 用户确认后，用固定脚本追加 `--execute` 推送分支并创建 PR。
6. 输出 PR URL、关联 issue、source/target branch、验证结果和下一步建议。

## 安全要求

- token 只能从环境变量读取。
- 不记录、不回显 token。
- 不把 token 写入仓库文件或 git 配置。
- 不执行 `git add`、`git commit`、`git stash` 或任何会改变本地提交历史的操作。
- 默认 dry-run，不应在用户确认前推送分支或创建 PR。

## 完成标准

- 当前分支已推送到正确 source remote。
- GitHub PR 已创建，标题和正文都关联 issue 编号。
- 最终回复包含 PR URL。
- 若失败，输出失败阶段、错误原因和可重试命令。
