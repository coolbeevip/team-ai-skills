---
name: team-gitlab-mr-create
description: 将已完成的单个 issue 分支推送到 GitLab，并创建标题和正文都关联 issue 编号的 Merge Request。Create a GitLab Merge Request for a completed issue branch, pushing the branch and linking the issue number in both title and body.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 创建 GitLab MR
  - 提交合并请求
  - 给这个 issue 建 MR
  - 推送分支并创建 MR
  - create GitLab MR
  - open merge request
  - create merge request for issue
  - push branch and open MR
---

# 创建 GitLab Merge Request

这个技能用于在 `team-issue-implement` 和 `team-issue-verify` 后，把当前 issue 分支推送到 GitLab，并创建关联 issue 的 Merge Request。它关注“少出错、可预览、可追踪”，避免手动复制 issue 编号、标题和正文时遗漏关联。

v1 仅支持 GitLab Merge Request。GitHub Pull Request 应使用独立技能。

## 固定脚本

创建 GitLab MR 时，优先使用本技能目录下的固定脚本，不要临时重写 GitLab API 调用代码：

```text
./scripts/create_gitlab_mr.py
```

脚本能力：

- 读取当前 git 分支，默认从分支名推断 issue IID。
- 从显式参数或 git remote 推断 source project 与 target project。
- 默认 dry-run，只输出将推送的分支和将创建的 MR。
- `--execute` 时先 push 当前分支，再创建 GitLab Merge Request。
- MR 标题和正文都包含 issue 编号，正文默认使用 `Closes #{issue_iid}` 以便 GitLab 自动关联并在合并后关闭 issue。
- 可指定 target branch、source remote、target remote、title、draft、label、assignee 和 reviewer。

推荐 dry-run：

```sh
python3 {skill_dir}/scripts/create_gitlab_mr.py
```

用户确认后正式执行：

```sh
GITLAB_TOKEN=... python3 {skill_dir}/scripts/create_gitlab_mr.py --execute
```

其中 `{skill_dir}` 是当前技能目录。技能内部定位脚本时应使用相对 `SKILL.md` 的路径 `./scripts/create_gitlab_mr.py`，执行命令时再解析成实际文件路径。

常用参数：

- `--issue-iid 123`：显式指定要关联的 GitLab issue IID。
- `--target-branch main`：指定目标分支。
- `--source-remote origin`：指定推送当前分支的 remote。
- `--target-remote upstream`：指定 MR 目标项目 remote。
- `--target-project namespace/project`：显式指定目标项目，优先级高于 remote 推断。
- `--source-project namespace/project`：显式指定 source project，用于 fork 工作流。
- `--title "Resolve #123: ..."`：显式指定 MR 标题。
- `--draft`：创建 Draft MR。
- `--label label-name`：可重复传入多个 label。
- `--assignee-id 123`、`--reviewer-id 456`：可重复传入多个人员 ID。
- `--json`：输出机器可读 JSON。

## 输入物

优先读取：

- 当前 git 分支名，通常应包含或等于 issue 编号，例如 `123`、`issue-123`、`123-add-export-filter`。
- 当前代码变更与提交历史。
- `team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.md`，如果能从分支、用户输入或对话中确定。
- GitLab issue IID 或 URL，如果用户提供。
- Git remote 信息，用于推断 source project 和 target project。

必须参数或可推断信息：

- GitLab 平台地址（默认 `https://gitlab.com`；自建 GitLab 必须提供自定义地址）。
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

- 标题必须包含 issue 编号，例如 `Resolve #123: Add export filter`。
- 正文必须包含 GitLab closing keyword，例如 `Closes #123`。
- 正文应包含：
  - 关联 issue。
  - 主要变更摘要。
  - 验证命令与结果。
  - 风险、未覆盖测试或需要 reviewer 注意的事项。

如果用户没有提供标题，默认标题从 issue IID 和当前分支生成。不要创建没有 issue 关联的 MR，除非用户明确要求。

## 建议流程

1. 确认当前分支、issue IID、source remote、target project 和 target branch。
2. 检查工作区状态；如果存在未提交变更，先提示用户提交或确认是否继续。
3. 使用固定脚本执行默认 dry-run，预览 push 和 MR 创建计划。
4. 用户确认后，用固定脚本追加 `--execute` 推送分支并创建 MR。
5. 输出 MR URL、关联 issue、source/target branch、验证结果和下一步建议。

## 安全要求

- token 只能从环境变量读取。
- 不记录、不回显 token。
- 不把 token 写入仓库文件或 git 配置。
- 默认 dry-run，不应在用户确认前推送分支或创建 MR。

## 完成标准

- 当前分支已推送到正确 source remote。
- GitLab MR 已创建，标题和正文都关联 issue 编号。
- 最终回复包含 MR URL。
- 若失败，输出失败阶段、错误原因和可重试命令。
