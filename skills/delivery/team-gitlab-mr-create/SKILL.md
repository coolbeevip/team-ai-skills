---
name: team-gitlab-mr-create
description: 将已完成的单个 issue 分支推送到 GitLab，并创建标题和正文都关联 issue 编号的 Merge Request。Create a GitLab Merge Request for a completed issue branch, pushing the branch and linking the issue number in both title and body.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 创建 GitLab MR
  - 创建合并请求
  - 给这个 issue 建 MR
  - 推送分支并创建 MR
  - create GitLab MR
  - open merge request
  - create merge request for issue
  - push branch and open MR
---

# 创建 GitLab Merge Request

这个技能用于在 `team-issue-implement` 和 `team-issue-verify` 后，把已经提交好的当前 issue 分支推送到 GitLab，并创建关联 issue 的 Merge Request。它关注“少出错、可预览、可追踪”，避免手动复制 issue 编号、标题和正文时遗漏关联。

v1 仅支持 GitLab Merge Request。GitHub Pull Request 应使用独立技能。

## 语言约定

统一读取目标项目根目录 `team-spec/config.yml`：

```yaml
language: zh-CN
```

语言优先级：用户本轮明确指定或脚本 `--language` > `team-spec/config.yml` > `en-US` 兜底。若配置不存在，技能执行时应先按团队规范询问语言偏好并创建配置；固定脚本独立运行时不交互，使用 `en-US` 兜底。

远端 GitLab Merge Request 正文模板标题、兜底文案和检查项必须使用 `language`；本地 issue 草稿已有内容保持原文。

## 固定脚本

创建 GitLab MR 时，优先使用本技能目录下的固定脚本，不要临时重写 GitLab API 调用代码：

```text
./scripts/create_gitlab_mr.py
```

脚本依赖同目录下的公共辅助模块 `./scripts/_team_common.py`（vendored copy，与仓库根目录 `scripts/_team_common.py` 保持同步）。复制本技能目录时需一并复制该文件。

脚本能力：

- 读取当前 git 分支，默认从分支名推断 issue IID。
- 从显式参数或 git remote 推断 source project 与 target project。
- 默认 dry-run，只输出将推送的分支和将创建的 MR。
- `--execute` 时先做执行前确认，再 push 当前分支并创建 GitLab Merge Request。
- 默认只推送已有提交；如果用户明确要求收尾提交，可通过 `--commit-message` 搭配 `--commit-all`、`--commit-path` 或 `--commit-staged` 在 push 前创建本地提交。
- 执行收尾提交时，绝对不得对 `team-spec/` 下的文件执行 `git add`；如果发现 `team-spec/` 文件已经在暂存区，必须停止并要求先取消暂存。
- MR 标题默认不包含 issue IID，只描述变更本身；正文使用 `./scripts/templates/mr_body.md.tpl` 按 `language` 渲染，并保留 `Closes #{issue_iid}` 以便 GitLab 自动关联并在合并后关闭 issue。
- 可指定 target branch、source remote、target remote、title、draft、label、assignee 和 reviewer。
- 执行前会检查被 Git 追踪但又命中 `.gitignore` 规则的文件，并要求人类确认是否继续。
- 正式请求 GitLab API 前会把 method、URL 和 payload 打印到 stderr，便于失败排查；token 不会输出。

推荐 dry-run：

```sh
GITLAB_URL=https://gitlab.example.com python3 {skill_dir}/scripts/create_gitlab_mr.py
```

用户确认后正式执行：

```sh
GITLAB_URL=https://gitlab.example.com GITLAB_TOKEN=... python3 {skill_dir}/scripts/create_gitlab_mr.py --execute
```

如果当前工作区存在已验证但尚未提交的变更，并且用户明确要求由本技能完成提交，可在正式执行时指定提交范围。`--commit-all` 只会暂存非 `team-spec/` 文件：

```sh
GITLAB_URL=https://gitlab.example.com GITLAB_TOKEN=... python3 {skill_dir}/scripts/create_gitlab_mr.py --execute --commit-message "Resolve #123: add export filter" --commit-all
```

也可以只提交指定路径或已暂存内容；指定路径不得位于 `team-spec/` 下，已暂存内容中也不得包含 `team-spec/` 文件：

```sh
GITLAB_URL=https://gitlab.example.com GITLAB_TOKEN=... python3 {skill_dir}/scripts/create_gitlab_mr.py --execute --commit-message "Resolve #123: add export filter" --commit-path src/export.py --commit-path tests/test_export.py
GITLAB_URL=https://gitlab.example.com GITLAB_TOKEN=... python3 {skill_dir}/scripts/create_gitlab_mr.py --execute --commit-message "Resolve #123: add export filter" --commit-staged
```

其中 `{skill_dir}` 是当前技能目录。技能内部定位脚本时应使用相对 `SKILL.md` 的路径 `./scripts/create_gitlab_mr.py`，执行命令时再解析成实际文件路径。

常用参数：

- `--issue-iid 123`：显式指定要关联的 GitLab issue IID。
- `--target-branch master`：指定目标分支；如果不传，脚本会推断并在 `--execute` 前要求人类确认。
- `--source-remote origin`：指定推送当前分支的 remote。
- `--target-remote upstream`：指定 MR 目标项目 remote。
- `--target-project namespace/project`：显式指定目标项目，优先级高于 remote 推断。
- `--source-project namespace/project`：显式指定 source project，用于 fork 工作流。
- `--title "Add export filter"`：显式指定 MR 标题；不建议在标题中包含 issue IID。
- `--issue-file team-spec/active/issues/{slug}/123-short-title.md`：显式指定本地 issue 草稿，用其中的 `# 标题` 或 `## Title` 首行生成 MR 标题。
- `--body-file path/to/body.md`：显式指定 MR 正文；如未指定，脚本使用 `./scripts/templates/mr_body.md.tpl` 生成标准正文。
- `--language zh-CN`：显式覆盖 MR 正文模板语言；不传时读取 `team-spec/config.yml`。
- `--draft`：创建 Draft MR。
- `--label label-name`：可重复传入多个 label。
- `--assignee-id 123`、`--reviewer-id 456`：可重复传入多个人员 ID。
- `--commit-message "Resolve #123: ..."`：在 push 前提交本地未提交变更；必须搭配一个提交范围参数。
- `--commit-all`：用 `git add -A` 暂存整个工作区中除 `team-spec/` 以外的变更后提交。
- `--commit-path path`：只暂存并提交指定路径；可重复传入，但路径不得位于 `team-spec/` 下。
- `--commit-staged`：只提交已经暂存的内容，不额外暂存文件；如果暂存区包含 `team-spec/` 文件，必须停止。
- `--json`：输出机器可读 JSON。
- `GITLAB_URL=https://gitlab.example.com`：GitLab 平台地址，必须通过环境变量提供；脚本不提供命令行覆盖参数，也不会默认猜测平台地址。

## 输入物

优先读取：

- 当前 git 分支名，通常应包含或等于 issue 编号，例如 `123`、`issue-123`、`123-add-export-filter`。
- 当前提交历史；默认要求工作区干净。若用户明确要求由本技能完成收尾提交，可以提交非 `team-spec/` 的未提交变更，`team-spec/` 下未提交变更可留在工作区。
- `team-spec/active/issues/{slug}/{issue-number}-{short-issue-slug}.md`，如果能从分支、用户输入或对话中确定。
- GitLab issue IID 或 URL，如果用户提供。
- Git remote 信息，用于推断 source project 和 target project。

必须参数或可推断信息：

- GitLab 平台地址，必须从环境变量 `GITLAB_URL` 读取；不得通过命令行参数临时覆盖，未设置时脚本必须停止。
- 认证 token（必须通过环境变量提供，不写入任何文件）。
- 当前分支名。
- issue IID。
- source project 与 target project。
- target branch。

如果无法唯一确定 issue IID、source project、target project、token 来源或 target branch，必须停止并向用户确认，不得猜测。

## 仓库定位规则

当用户没有显式提供 GitLab project 时，按以下规则推断：

- target project：优先使用 `--target-remote`；否则使用名为 `upstream` 的 GitLab remote；否则使用当前分支 tracking remote；仍不唯一时要求用户指定。
- source project：优先使用 `--source-remote`；否则使用当前分支 tracking remote；否则使用 `origin`；如果只有一个 GitLab remote，则使用这个 remote。
- 如果 source project 和 target project 相同，创建普通 MR。
- 如果 source project 和 target project 不同，按 fork 工作流创建跨项目 MR。

自建 GitLab 场景下，remote host 必须与平台地址一致；如果不一致，应要求用户确认平台地址和项目。

## 输出物

- GitLab Merge Request。
- 最终回复中的 MR URL、source branch、target branch、关联 issue IID。
- 如果项目有本地 issue 草稿，可回写或提示用户记录 MR URL。

## MR 标题与正文规则

- 标题默认不包含 issue IID，默认格式为 `{clear change title}`，例如 `Add export filter`。
- 如果用户显式提供 `--title`，优先使用该标题；脚本不会自动向标题补 issue IID。
- 如果没有显式标题，优先从 `--issue-file` 指定的本地 issue 草稿读取标题；其次从 `team-spec/active/issues/*/{issue-iid}-*.md` 的唯一匹配文件读取标题。
- 本地 issue 草稿标题只允许来自明确的 `# 标题` 或 `## Title` 段首行，不得回退到文件名。
- 如果找不到本地 issue 标题，才从分支名生成标题；如果分支名去掉 issue 编号后没有语义，例如只剩 `implementation`，必须停止并要求用户提供 `--title` 或 `--issue-file`。
- 正文必须包含 GitLab closing keyword，例如 `Closes #123`。
- 默认正文必须使用 `./scripts/templates/mr_body.md.tpl`，并包含：
  - `Summary`：从 issue 的 `What to build` 映射；缺失时用分支和 issue 生成兜底摘要。
  - `Changes`：优先来自 issue 的 `Implementation Notes`。
  - `Acceptance criteria`：优先来自 `team-issue-verify` 回写的 `Acceptance Criteria Coverage`。
  - `Verification`：优先来自 `Commands Run`。
  - `Risks`：优先来自 `Regression Risks`。
  - `Reviewer notes`：优先来自 `Findings`。
  - `Checklist`：提交前人工检查清单。
- 如果用户传入 `--body-file`，也必须保留 issue closing keyword；脚本会在缺失时自动补 `Closes #{issue_iid}`。

不要创建没有 issue 关联正文的 MR，除非用户明确要求。不要创建空泛标题的 MR，例如 `implementation` 或 `Resolve #123: implementation`。

## 建议流程

1. 确认当前分支、issue IID、source remote、target project、target branch 和 MR 标题来源。
2. 检查工作区状态；如果存在未提交变更，先确认这些变更是否已经实现和验证完成。
3. 如果用户没有明确要求代为提交，停止并要求用户先完成提交或 stash。
4. 如果用户明确要求代为提交，必须确认提交信息和提交范围：`--commit-all`、`--commit-path` 或 `--commit-staged` 三选一。
5. 提交范围必须排除 `team-spec/`：不得对 `team-spec/` 下文件执行 `git add`；如果 `team-spec/` 文件已经在暂存区，必须停止并要求用户先取消暂存。
6. 使用固定脚本执行默认 dry-run，预览 push、MR 创建计划和待提交工作区状态。
7. 如果目标分支是推断出来的，或工作区里存在被追踪但命中 `.gitignore` 的文件，执行前必须向人类确认。
8. 用户确认后，用固定脚本追加 `--execute`；如提供提交参数，脚本会先创建本地提交，再推送分支并创建 MR。提交后如仅剩 `team-spec/` 下未提交变更，可以继续创建 MR。
9. 输出 MR URL、关联 issue、source/target branch、创建的提交、验证结果和下一步建议。

## 安全要求

- token 只能从环境变量读取。
- 不记录、不回显 token。
- 不把 token 写入仓库文件或 git 配置。
- 默认不执行 `git add`、`git commit`、`git stash` 或任何会改变本地提交历史的操作。
- 只有当用户明确要求并提供提交信息与提交范围时，才允许执行 `git add` 和 `git commit`；仍不得执行 `git stash`。
- 任何情况下都不得对 `team-spec/` 下文件执行 `git add`。如果自动提交前发现 `team-spec/` 文件已在暂存区，必须停止，不得提交。
- 默认 dry-run，不应在用户确认前推送分支或创建 MR。

## 完成标准

- 当前分支已推送到正确 source remote。
- GitLab MR 已创建，标题和正文都关联 issue 编号。
- MR 标题来自显式标题、本地 issue 草稿标题或有语义的分支名，不是 `implementation` 这类兜底词。
- 如果执行了收尾提交，最终回复包含创建的 commit SHA 和提交范围。
- 最终回复包含 MR URL。
- 若失败，输出失败阶段、错误原因和可重试命令。
