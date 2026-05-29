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

## 语言约定

统一读取目标项目根目录 `team-spec/config.yml`：

```yaml
language: zh-CN
version_control:
  system: git
  trunk_branch: main
  contribution_model: fork-pull
  source_remote: origin
  target_remote: upstream
```

语言优先级：用户本轮明确指定或脚本 `--language` > `team-spec/config.yml` > `en-US` 兜底。若配置不存在，技能执行时应先按团队规范询问语言偏好并创建配置；固定脚本独立运行时不交互，使用 `en-US` 兜底。

远端 GitHub Pull Request 正文模板标题、兜底文案和检查项必须使用 `language`；本地 issue 草稿已有内容保持原文。

版本管理优先级：用户显式参数 > `team-spec/config.yml` 的 `version_control` > git 命令推断 > 询问用户。若缺少 `version_control`，先用 `git remote -v`、`git branch --show-current`、`git branch -r`、`git symbolic-ref refs/remotes/{remote}/HEAD` 和 `git config --get branch.{branch}.remote` 推断 source remote、target remote、主干分支和贡献方式；无法唯一判断时再询问用户，并在用户确认后回写 `team-spec/config.yml`。

## 固定脚本

创建 GitHub PR 时，优先使用本技能目录下的固定脚本，不要临时重写 GitHub API 调用代码：

```text
./scripts/create_github_pr.py
```

脚本依赖同目录下的公共辅助模块 `./scripts/_team_common.py`（vendored copy，与仓库根目录 `scripts/_team_common.py` 保持同步）。复制本技能目录时需一并复制该文件。

脚本能力：

- 读取当前 git 分支，默认从分支名推断 issue 编号。
- 从显式参数、`team-spec/config.yml` 或 git remote 推断 source repo 与 target repo。
- 默认 dry-run，只输出将推送的分支和将创建的 PR。
- `--execute` 时先做执行前确认，再 push 当前分支并创建 GitHub Pull Request。
- 脚本只允许推送已有提交，不负责 `git add`、`git commit`、自动暂存或自动生成本地提交。
- PR 标题默认不包含 issue 编号，只描述变更本身；正文使用 `./scripts/templates/pr_body.md.tpl` 按 `language` 渲染，并保留 `Closes #{issue_number}` 以便 GitHub 自动关联并在合并后关闭 issue。
- 创建 PR 成功后，如果能定位到本地 issue 草稿，会把该文件回写为 `Status: PR created`，并记录 `PR:` 和 `Pushed Branch:`；该回写只修改本地文件，不会自动 `git add` 或提交 `team-spec/`。
- 可指定 target branch、source remote、target remote、title、draft 和 assignee；未指定 target branch 时优先使用 `version_control.trunk_branch`。
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
- `--target-branch main`：指定目标分支；如果不传，脚本优先读取 `team-spec/config.yml` 的 `version_control.trunk_branch`，再通过 remote HEAD 推断。
- `--source-remote origin`：指定推送当前分支的 remote。
- `--target-remote upstream`：指定 PR 目标项目 remote。
- `--target-repo owner/repo`：显式指定目标仓库，优先级高于 remote 推断。
- `--source-repo owner/repo`：显式指定 source repo，用于 fork 工作流。
- `--title "Add export filter"`：显式指定 PR 标题；不建议在标题中包含 issue 编号。
- `--issue-file team-spec/active/{slug}/issues/123-short-title.md`：显式指定本地 issue 草稿，用其中的 `# 标题` 或 `## Title` 首行生成 PR 标题和标准正文。
- `--body-file path/to/body.md`：显式指定 PR 正文；如未指定，脚本使用 `./scripts/templates/pr_body.md.tpl` 生成标准正文。
- `--language zh-CN`：显式覆盖 PR 正文模板语言；不传时读取 `team-spec/config.yml`。
- `--draft`：创建 Draft PR。
- `--assignee octocat`：可重复传入多个 assignee login。
- `--json`：输出机器可读 JSON。

## 输入物

优先读取：

- 当前 git 分支名，通常应包含或等于 issue 编号，例如 `123`、`issue-123`、`123-add-export-filter`。
- 当前提交历史；工作区必须干净，不能包含未提交变更。
- `team-spec/active/{slug}/issues/{issue-number}-{short-issue-slug}.md`，如果能从分支、用户输入或对话中确定。
- GitHub issue 编号或 URL，如果用户提供。
- `team-spec/config.yml` 的 `version_control` 配置，以及 Git remote 信息，用于推断 source repo、target repo、target branch 和贡献方式。

必须参数或可推断信息：

- GitHub 平台地址（默认 `https://github.com`；GitHub Enterprise 必须提供自定义地址）。
- 认证 token（必须通过环境变量提供，不写入任何文件）。
- 当前分支名。
- issue 编号。
- source repo 与 target repo。
- target branch，优先来自用户显式参数，其次来自 `version_control.trunk_branch`，再其次来自 remote HEAD。

如果无法唯一确定 issue 编号、source repo、target repo、token 来源或 target branch，必须停止并向用户确认，不得猜测。

## 仓库定位规则

当用户没有显式提供 GitHub repo 时，按以下规则推断：

- target repo：优先使用 `--target-remote`；否则使用名为 `upstream` 的 GitHub remote；否则使用当前分支 tracking remote；仍不唯一时要求用户指定。
- source repo：优先使用 `--source-remote`；否则使用当前分支 tracking remote；否则使用 `origin`；如果只有一个 GitHub remote，则使用这个 remote。
- 如果 source repo 和 target repo 相同，创建普通 PR。
- 如果 source repo 和 target repo 不同，按 fork 工作流创建跨仓库 PR。
- 如果 `team-spec/config.yml` 已配置 `version_control.target_remote` 或 `version_control.source_remote`，在未传显式参数时优先使用配置值。
- 如果 `version_control.contribution_model: fork-pull`，默认 `target_remote` 为 `upstream`、`source_remote` 为 `origin`；如果配置或 remote 与该模式冲突，先 dry-run 展示冲突并要求人类确认。

自建 GitHub Enterprise 场景下，remote host 必须与平台地址一致；如果不一致，应要求用户确认平台地址和仓库。

## 输出物

- GitHub Pull Request。
- 最终回复中的 PR URL、source branch、target branch、关联 issue 编号。
- 如果项目有本地 issue 草稿，创建成功或发现已有打开 PR 后，会回写 PR URL、source branch 和状态。

## PR 标题与正文规则

- 标题默认不包含 issue 编号，默认格式为 `{clear change title}`，例如 `Add export filter`。
- 如果用户显式提供 `--title`，优先使用该标题；脚本不会自动向标题补 issue 编号。
- 如果没有显式标题，优先从 `--issue-file` 指定的本地 issue 草稿读取标题；其次从 `team-spec/active/*/issues/{issue-number}-*.md` 的唯一匹配文件读取标题，并兼容旧布局 `team-spec/active/issues/*/{issue-number}-*.md`。
- 本地 issue 草稿标题只允许来自明确的 `# 标题` 或 `## Title` 段首行，不得回退到文件名。
- 如果找不到本地 issue 标题，才从分支名生成标题；如果分支名去掉 issue 编号后没有语义，例如只剩 `implementation`，必须停止并要求用户提供 `--title` 或 `--issue-file`。
- 正文必须包含 GitHub closing keyword，例如 `Closes #123`。
- 默认正文必须使用 `./scripts/templates/pr_body.md.tpl`，并包含：
  - `Summary`：从 issue 的 `What to build` 映射；缺失时用分支和 issue 生成兜底摘要。
  - `Changes`：优先来自 issue 的 `Implementation Notes`。
  - `Acceptance criteria`：优先来自 `team-issue-verify` 回写的 `Acceptance Criteria Coverage`。
  - `Verification`：优先来自 `Commands Run`。
  - `Risks`：优先来自 `Regression Risks`。
  - `Reviewer notes`：优先来自 `Findings`。
  - `Checklist`：提交前人工检查清单。
- 如果用户传入 `--body-file`，也必须保留 issue closing keyword；脚本会在缺失时自动补 `Closes #{issue_number}`。

不要创建没有 issue 关联正文的 PR，除非用户明确要求。不要创建空泛标题的 PR，例如 `implementation` 或 `Resolve #123: implementation`。

## 建议流程

1. 确认当前分支、issue 编号、source remote、target repo、target branch 和贡献方式；优先读取 `team-spec/config.yml`，缺失时先用 git 命令推断。
2. 检查工作区状态；如果存在未提交变更，停止并要求用户先完成实现验证和人工提交，不得代替用户执行 `git add` 或 `git commit`。
3. 使用固定脚本执行默认 dry-run，预览 push 和 PR 创建计划。
4. 如果目标分支、source remote、target remote 或贡献方式不是来自用户显式参数或已确认的 `team-spec/config.yml`，或工作区里存在被追踪但命中 `.gitignore` 的文件，执行前必须向人类确认；确认后可回写 `team-spec/config.yml`。
5. 用户确认后，用固定脚本追加 `--execute` 推送分支并创建 PR。
6. 如果能定位到本地 issue 草稿，回写 `Status: PR created`、`PR:` 和 `Pushed Branch:`；不得自动暂存或提交 `team-spec/`。
7. 输出 PR URL、关联 issue、source/target branch、验证结果、已回写的 issue 文件和有序号的“下一步可选”列表，方便用户直接回复序号继续推进。

## 安全要求

- token 只能从环境变量读取。
- 不记录、不回显 token。
- 不把 token 写入仓库文件或 git 配置。
- 不执行 `git add`、`git commit`、`git stash` 或任何会改变本地提交历史的操作。
- 创建 PR 后允许回写本地 `team-spec/active/{slug}/issues/` 下对应 issue 草稿，但不得自动暂存或提交这些回写。
- 默认 dry-run，不应在用户确认前推送分支或创建 PR。

## 完成标准

- 当前分支已推送到正确 source remote。
- GitHub PR 已创建，标题和正文都关联 issue 编号。
- 如能定位本地 issue 草稿，已回写 `Status: PR created`、`PR:` 和 `Pushed Branch:`。
- 最终回复包含 PR URL。
- 若失败，输出失败阶段、错误原因和可重试命令。
