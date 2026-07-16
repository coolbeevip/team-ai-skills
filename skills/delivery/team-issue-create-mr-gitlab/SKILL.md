---
name: team-issue-create-mr-gitlab
description: 为已完成的单个 issue 分支推送代码并创建关联 issue 的 GitLab Merge Request。Push a completed issue branch and create an issue-linked GitLab Merge Request.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 创建 GitLab MR
  - 创建合并请求
  - 给这个 issue 建 MR
  - 推送分支并创建 MR
  - 准备提 MR
  - create GitLab MR
  - open merge request
  - create merge request for issue
  - push branch and open MR
  - open MR for this issue
---

# 创建 GitLab Merge Request

这个技能用于在 `team-issue-implement` 和 `team-issue-verify` 后，把已经提交好的当前 issue 分支推送到 GitLab，并创建关联 issue 的 Merge Request。它关注“少出错、可预览、可追踪”，避免手动复制 issue 编号、标题规范和正文模板时遗漏关联。

v1 仅支持 GitLab Merge Request。GitHub Pull Request 应使用独立技能。

## 触发边界

- 适合触发：单个 issue 分支已经提交并验证通过，需要推送并创建 GitLab Merge Request。
- 不适合触发：目标平台是 GitHub 时，转交 `team-issue-create-pr-github`；实现尚未验证时，先转交 `team-issue-verify`。

## 运行时配置

统一读取目标项目根目录 `team-spec/config.yml`：

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

语言优先级：用户本轮明确指定或脚本 `--language` > `team-spec/config.yml` > `en-US` 兜底。若配置不存在，技能执行时应先按团队规范询问语言偏好并创建配置；固定脚本独立运行时不交互，使用 `en-US` 兜底。

远端 GitLab Merge Request 正文模板标题、兜底文案和检查项必须使用 `language`；本地 issue 草稿已有内容保持原文。

版本管理优先级：用户显式参数 > `team-spec/config.yml` 的 `version_control` > git 命令推断 > 询问用户。若缺少 `version_control`，先用 `git remote -v`、`git branch --show-current`、`git branch -r`、`git symbolic-ref refs/remotes/{remote}/HEAD` 和 `git config --get branch.{branch}.remote` 推断 source remote、target remote、主干分支和贡献方式；无法唯一判断时再询问用户，并在用户确认后回写 `team-spec/config.yml`。
- 在读取 issue 草稿、分支状态或目标项目内容前，先读取 `team-spec/config.yml`；如果存在 `access_policy`，先应用目录访问边界，再进入任何推送或写入流程。

## 固定脚本

创建 GitLab MR 时，优先使用本技能目录下的固定脚本，不要临时重写 GitLab API 调用代码：

```text
./scripts/create_gitlab_mr.py
```

脚本依赖同目录下的公共辅助模块 `./scripts/_team_common.py`（vendored copy，与仓库根目录 `scripts/_team_common.py` 保持同步）。复制本技能目录时需一并复制该文件。

脚本能力：

- 读取当前 git 分支，默认从分支名推断 issue IID。
- 从显式参数、`team-spec/config.yml` 或 git remote 推断 source project 与 target project。
- 默认 dry-run，只输出将推送的分支和将创建的 MR。
- `--execute` 时先做执行前确认，再 push 当前分支并创建 GitLab Merge Request。
- 默认只推送已有提交；如果工作区或暂存区存在未提交变更，技能必须先列出这些变更，并取得用户对提交范围和提交信息的确认。确认后可通过 `--commit-message` 搭配 `--commit-all`、`--commit-path` 或 `--commit-staged` 在 push 前创建本地提交。
- 执行收尾提交时，绝对不得对 `team-spec/` 下的文件执行 `git add`；如果发现 `team-spec/` 文件已经在暂存区，必须停止并要求先取消暂存。
- MR 标题推荐使用组件标签和祈使语气，例如 `[BugFix] Fix export filter`；正文使用 `./scripts/templates/mr_body.md.tpl` 按 `language` 渲染，并保留 `Fixes #{issue_iid}` 以便 GitLab 自动关联并在合并后关闭 issue。
- 创建 MR 成功后，如果能定位到本地 issue 草稿，会把该文件回写为 `Status: mr-created`，并记录 `MR:` 和 `Pushed Branch:`；该回写只修改本地文件，不会自动 `git add` 或提交 `team-spec/`。
- 可指定 target branch、source remote、target remote、title、draft、label、assignee 和 reviewer；未指定 target branch 时优先使用 `version_control.trunk_branch`。
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

如果当前工作区或暂存区存在已验证但尚未提交的变更，必须先列出变更文件、暂存状态和推荐提交范围；用户确认提交范围和提交信息后，可在正式执行时指定提交范围。`--commit-all` 只会暂存非 `team-spec/` 文件：

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
- `--target-branch master`：指定目标分支；如果不传，脚本优先读取 `team-spec/config.yml` 的 `version_control.trunk_branch`，再通过 remote HEAD 推断。
- `--source-remote origin`：指定推送当前分支的 remote。
- `--target-remote upstream`：指定 MR 目标项目 remote。
- `--target-project namespace/project`：显式指定目标项目，优先级高于 remote 推断。
- `--source-project namespace/project`：显式指定 source project，用于 fork 工作流。
- `--title "[Component] Add export filter"`：显式指定 MR 标题；推荐把组件标签放在最前面并用方括号，不建议在标题中包含 issue IID。
- `--issue-file team-spec/active/{slug}/issues/123-short-title.md`：显式指定本地 issue 草稿，用其中的 `# 标题` 或 `## Title` 首行生成 MR 标题。
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
- 当前提交历史，以及工作区和暂存区状态。默认推送已有提交；如果存在未提交变更，必须先列出变更，取得用户确认后才允许创建收尾提交。可以提交非 `team-spec/` 的未提交变更，`team-spec/` 下未提交变更可留在工作区。
- `team-spec/active/{slug}/issues/{issue-number}-{short-issue-slug}.md`，如果能从分支、用户输入或对话中确定。
- GitLab issue IID 或 URL，如果用户提供。
- `team-spec/config.yml` 的 `version_control` 配置，以及 Git remote 信息，用于推断 source project、target project、target branch 和贡献方式。

必须参数或可推断信息：

- GitLab 平台地址，必须从环境变量 `GITLAB_URL` 读取；不得通过命令行参数临时覆盖，未设置时脚本必须停止。
- 认证 token（必须通过环境变量提供，不写入任何文件）。
- 当前分支名。
- issue IID。
- source project 与 target project。
- target branch，优先来自用户显式参数，其次来自 `version_control.trunk_branch`，再其次来自 remote HEAD。

如果无法唯一确定 issue IID、source project、target project、token 来源或 target branch，必须停止并向用户确认，不得猜测。

## 仓库定位规则

当用户没有显式提供 GitLab project 时，按以下规则推断：

- target project：优先使用 `--target-remote`；否则使用名为 `upstream` 的 GitLab remote；否则使用当前分支 tracking remote；仍不唯一时要求用户指定。
- source project：优先使用 `--source-remote`；否则使用当前分支 tracking remote；否则使用 `origin`；如果只有一个 GitLab remote，则使用这个 remote。
- 如果 source project 和 target project 相同，创建普通 MR。
- 如果 source project 和 target project 不同，按 fork 工作流创建跨项目 MR。
- 如果 `team-spec/config.yml` 已配置 `version_control.target_remote` 或 `version_control.source_remote`，在未传显式参数时优先使用配置值。
- 如果 `version_control.contribution_model: fork-pull`，默认 `target_remote` 为 `upstream`、`source_remote` 为 `origin`；如果配置或 remote 与该模式冲突，先 dry-run 展示冲突并要求人类确认。

自建 GitLab 场景下，remote host 必须与平台地址一致；如果不一致，应要求用户确认平台地址和项目。

## 输出物

- GitLab Merge Request。
- 最终回复中的 MR URL、source branch、target branch、关联 issue IID。
- 如果项目有本地 issue 草稿，创建成功或发现已有打开 MR 后，会回写 MR URL、source branch 和状态。

## MR 标题与正文规则

- 标题推荐格式为 `[Component] Add clear change title`，例如 `[BugFix] Fix export filter`、`[CI] Add release check`、`[microTVM][CI] Fix board test workflow`。
- 组件标签必须放在标题最前面并使用方括号；多个标签使用多个方括号，例如 `[microTVM][CI]`。
- 标题正文使用祈使语气，例如 `Add ...`、`Fix ...`、`Update ...`，不要写 `Added ...`、`Fixed ...`、`Updated ...`。
- 首字母、专有名词和缩写大小写必须正确，例如 `API`、`CI`、`microTVM`。
- 标题末尾不要加句号；脚本会自动移除显式标题、issue 标题或分支标题末尾的 `.` / `。`。
- 如果用户显式提供 `--title`，优先使用该标题；脚本不会自动向标题补 issue IID，也不会猜测组件标签。
- 如果没有显式标题，优先从 `--issue-file` 指定的本地 issue 草稿读取标题；其次从 `team-spec/active/*/issues/{issue-iid}-*.md` 的唯一匹配文件读取标题，并兼容旧布局 `team-spec/active/issues/*/{issue-iid}-*.md`。
- 本地 issue 草稿标题只允许来自明确的 `# 标题` 或 `## Title` 段首行，不得回退到文件名。
- 如果找不到本地 issue 标题，才从分支名生成标题；如果分支名去掉 issue 编号后没有语义，例如只剩 `implementation`，必须停止并要求用户提供 `--title` 或 `--issue-file`。
- 如果标题缺少组件标签，或以 `Added`、`Fixed`、`Updated` 等过去式动词开头，脚本会在 dry-run 预览中输出 `Title style notes`，提示用户用 `--title` 覆盖。
- 正文必须包含 GitLab closing keyword，例如 `Fixes #123`。
- 默认正文必须使用 `./scripts/templates/mr_body.md.tpl`，并包含：
  - `What is the purpose of the change?`：简要说明为什么需要这个 MR；优先从 issue 的 `What to build` 映射，缺失时用分支和 issue 生成兜底摘要，并包含 `Fixes #{issue_iid}`。
  - `Brief change log`：优先来自 issue 的 `Implementation Notes`。
  - `How was this tested?`：优先来自 `Commands Run`，也兼容 `Acceptance Criteria Coverage`。
  - `Documentation`：文档更新检查项。
  - `Compatibility / impact`：优先来自 `Compatibility / impact`、`Impact` 或 `Regression Risks`。
  - `Reviewer notes`：优先来自 `Findings`。
- 如果用户传入 `--body-file`，也必须保留 issue closing keyword；脚本会在缺失时自动补 `Fixes #{issue_iid}`。

不要创建没有 issue 关联正文的 MR，除非用户明确要求。不要创建空泛标题的 MR，例如 `implementation` 或 `Resolve #123: implementation`。

## 建议流程

1. 确认当前分支、issue IID、source remote、target project、target branch、贡献方式和 MR 标题来源；优先读取 `team-spec/config.yml`，缺失时先用 git 命令推断。
2. 检查工作区和暂存区状态；如果存在未提交变更，列出变更文件、暂存状态和推荐提交范围。
3. 如果需要创建收尾提交，必须先取得用户对提交范围和提交信息的明确确认；确认后才允许执行 `git add` 和 `git commit`。用户未确认时停止，不得继续 push 或创建 MR。
4. 提交方式必须明确为 `--commit-all`、`--commit-path` 或 `--commit-staged` 三选一。
5. 提交范围必须排除 `team-spec/`：不得对 `team-spec/` 下文件执行 `git add`；如果 `team-spec/` 文件已经在暂存区，必须停止并要求用户先取消暂存。
6. 使用固定脚本执行默认 dry-run，预览 push、MR 创建计划和待提交工作区状态。
7. 如果目标分支、source remote、target remote 或贡献方式不是来自用户显式参数或已确认的 `team-spec/config.yml`，或工作区里存在被追踪但命中 `.gitignore` 的文件，执行前必须向人类确认；确认后可回写 `team-spec/config.yml`。
8. 用户确认后，用固定脚本追加 `--execute`；如提供提交参数，脚本会先创建本地提交，再推送分支并创建 MR。提交后如仅剩 `team-spec/` 下未提交变更，可以继续创建 MR。
9. 如果能定位到本地 issue 草稿，回写 `Status: mr-created`、`MR:` 和 `Pushed Branch:`；不得自动暂存或提交 `team-spec/`。
10. 输出 MR URL、关联 issue、source/target branch、创建的提交、验证结果、已回写的 issue 文件和有序号的“下一步可选”列表，方便用户直接回复序号继续推进。

## 安全要求

- token 只能从环境变量读取。
- 不记录、不回显 token。
- 不把 token 写入仓库文件或 git 配置。
- 默认不执行 `git add`、`git commit`、`git stash` 或任何会改变本地提交历史的操作。
- 只有在已经列出未提交变更，并且用户明确确认提交范围和提交信息后，才允许执行 `git add` 和 `git commit`；仍不得执行 `git stash`。
- 任何情况下都不得对 `team-spec/` 下文件执行 `git add`。如果自动提交前发现 `team-spec/` 文件已在暂存区，必须停止，不得提交。
- 创建 MR 后允许回写本地 `team-spec/active/{slug}/issues/` 下对应 issue 草稿，但不得自动暂存或提交这些回写。
- 默认 dry-run，不应在用户确认前推送分支或创建 MR。

## 完成标准

- 当前分支已推送到正确 source remote。
- GitLab MR 已创建，正文关联 issue 编号，标题符合组件标签和祈使语气规范或已在预览中提示需要调整。
- MR 标题来自显式标题、本地 issue 草稿标题或有语义的分支名，不是 `implementation` 这类兜底词。
- 如能定位本地 issue 草稿，已回写 `Status: mr-created`、`MR:` 和 `Pushed Branch:`。
- 如果执行了收尾提交，最终回复包含创建的 commit SHA 和提交范围。
- 最终回复包含 MR URL。
- 若失败，输出失败阶段、错误原因和可重试命令。
