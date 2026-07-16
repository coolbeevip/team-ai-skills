---
name: team-tech-debt-to-issues
description: 将已评审的技术债规格拆解为可独立领取、可验证、按依赖排序的工程 issue。Break reviewed technical debt specs into independently grabbable, verifiable, dependency-ordered engineering issues.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 技术债拆 issue
  - 把技术债拆成任务
  - 技术债转工程任务
  - 技术债已经 ready 开始拆任务
  - break tech debt into issues
  - create issues from tech debt
  - split technical debt work
  - tech debt is ready create issues
---

# 技术债转工程 Issues

这个技能用于把技术债规格拆解为工程可执行的 issue，确保每个 issue 都能独立启动、独立验收，并且依赖关系清晰。

## 触发边界

- 适合触发：技术债规格已细化并通过评审，需要拆成可独立领取、可验证、按依赖排序的工程 issue。
- 不适合触发：技术债尚未评审 ready 时，转交 `team-tech-debt-review`；issue 已生成且要实现时，转交 `team-issue-implement` 或 `team-issue-batch-implement`。

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

语言优先级：用户本轮明确指定 > `team-spec/config.yml` > 首次询问并落盘。若配置不存在，不报错，走"询问并创建"流程。

执行要求：

- 对话回复与 issue 草稿 `team-spec/active/{slug}/issues/` 下内容均使用 `language`。
- 用户临时切换语言时，本次立即生效，并询问是否回写配置。
- 生成“下一步可选”或判断发布平台时，优先参考 `version_control`；缺失时先通过 git 命令推断，无法唯一判断再询问用户，并在用户确认后回写 `team-spec/config.yml`。
- 在读取技术债规格、评审、代码或写入 issue 草稿前，先读取 `team-spec/config.yml`；如果存在 `access_policy`，先应用目录访问边界，再进入拆解和写入流程。

## 输入物

- 主输入：`team-spec/active/{slug}/spec/refine.md`。
- 必要前置：`team-spec/active/{slug}/spec/reviews.md`，且状态应为 `ready`（除非用户明确接受带风险拆解草案）。
- 参考输入：`team-spec/config.yml`、`team-spec/CONTEXT.md`、`team-spec/decisions/`、`team-spec/active/{slug}/spec/CONTEXT.md`、`team-spec/active/{slug}/spec/decisions/`、相关代码与运行证据。

必须先确定唯一 slug。技术债链路 slug 必须包含 `debt`，格式建议 `{yyyy-mm-dd}-debt-{short-english-slug}`。无法唯一判断时必须向用户确认，不得猜测。

## 输出物

- issue 拆解草案（标题、类型、依赖、验收标准、切片理由）。
- 本地 issue 草稿默认写入 `team-spec/active/{slug}/issues/{issue-number}-{short-issue-slug}.md`。

输出目录统一收敛到 `team-spec/active/{slug}/issues/`。

`ready` 是 `spec/reviews.md` 中的阶段评审结果。进入 issue 拆解时，工作区 `STATUS.md` 应保持 `debt-ready`，直到实现流程将其更新为 `implementing`；本技能不得把评审结果写入工作区状态。

## 拆解原则

- 优先 vertical slice，避免“只改数据库/只改接口/只改 UI”这类横切任务。
- 每个 issue 完成后必须有可观察结果（稳定性、性能、复杂度、错误率、维护成本等）。
- 明确 blocker，先拆并先做阻塞 issue。
- 每个 issue 标注 `AFK` 或 `HITL`；若为 `HITL`，必须写清楚需要谁做什么决策。
- 用户可见输出中不要只写缩写。首次出现时写成 `AFK（可独立执行，无需人工决策）` 或 `HITL（需要人工介入）`。
- 使用项目已有术语，不引入新同义词。

## 最小 issue 模板

```md
## Status

draft

## Parent

team-spec/active/{slug}/spec/refine.md

## What to build

描述一个可独立验证的技术债修复切片。

## Type

AFK（可独立执行，无需人工决策） / HITL（需要人工介入）

## Acceptance criteria

- [ ] Given {上下文}，When {动作}，Then {可观察结果}。
- [ ] Given {上下文}，When {动作}，Then {可观察结果}。

## Blocked by

- None - can start immediately

## Notes

- 风险、约束、迁移和发布注意事项。
```

## 完成标准

- 产出落地到 `team-spec/active/{slug}/issues/` 的可执行 issue 草稿。
- issue 可被工程或 agent 直接领取，并具备可验证验收标准。
- 最终回复的“下一步可选”已基于 `team-spec/config.yml`、当前项目的 Git remote、`.github/`、`.gitlab-ci.yml` 或 `.gitlab/` 判断发布平台；除非信号冲突或无法判断，否则不会同时推荐 GitHub 和 GitLab 发布技能。

## Issue Tracker 判断

生成“下一步可选”前，先基于目标项目根目录做轻量判断，给发布技能排序：

1. 用户本轮明确指定 GitHub 或 GitLab 时，用户指定优先于自动探测。
2. 优先读取 `team-spec/config.yml` 的 `version_control`。若 `target_remote` 存在，优先检查该 remote；若 `contribution_model: fork-pull` 且未配置 `target_remote`，优先检查 `upstream`；否则检查当前分支 tracking remote 或 `origin`。
3. 通过 git 命令读取 remote URL，例如 `git remote -v`、`git config --get branch.{branch}.remote`。URL 包含 `github.com`、`github.` 或明确的 GitHub Enterprise 域名时，优先推荐 `team-issue-publish-github`；URL 包含 `gitlab.com`、`gitlab.` 或明确的 GitLab 自托管域名时，优先推荐 `team-issue-publish-gitlab`。
4. 如果 remote 不存在或无法判断，再检查仓库文件：存在 `.github/` 时优先推荐 `team-issue-publish-github`；存在 `.gitlab-ci.yml` 或 `.gitlab/` 时优先推荐 `team-issue-publish-gitlab`。
5. 如果平台信号明确，只输出对应平台的发布选项，不要同时输出另一个平台的发布选项。
6. 如果 remote 与文件信号冲突，在“下一步可选”中把置信度最高的发布选项放在第 1 项，并在描述中说明冲突信号；第 2 项才列另一个发布技能作为备选。
7. 如果版本管理配置缺失且 git 命令也无法唯一推断，询问用户缺失的最小信息，例如平台、主干分支或贡献方式；用户确认后再回写 `team-spec/config.yml`。
8. 如果完全无法判断平台，可以同时列出 `team-issue-publish-github` 和 `team-issue-publish-gitlab`，但必须说明“未检测到明确平台信号，需要用户选择”。

## 下一步可选

完成 issue 拆解后，必须在最终回复中列出有序号的可选下一步，帮助用户直接回复序号继续推进：

```md
## 下一步可选

1. `team-issue-publish-github`：检测到 GitHub remote，发布到 GitHub Issues。
2. `team-issue-batch-implement`：存在多个可执行 `AFK` issue 时，按依赖顺序连续实现并逐个验证。
3. `team-issue-implement`：只处理一个明确的 `AFK` issue。
4. 完成人工决策：issue 中存在 `HITL` 时，先完成对应人工决策，再继续发布或实现。
```
