---
name: team-issue-start
description: 为单个 issue 开始开发前准备干净工作区、同步主干、检查依赖和创建 issue 分支，确保后续实现只围绕一个明确 issue。Prepare a clean workspace for a single issue by syncing the main branch, checking dependencies, and creating an issue branch before implementation.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# Issue 开始

这个技能用于在实现单个 issue 前建立清晰的开发边界。它不负责编写代码，只负责确认当前 issue 可以开始、工作区干净、分支正确。

## 输入物

主输入：

- `team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.md`
- 或外部 issue tracker 中的单个 issue。

参考输入：

- `team-spec/prd/{slug}.md` 中的关联 PRD。
- `team-spec/spec/reviews/{slug}.md` 中的风险评审。
- 当前 git 状态、主干分支、远程仓库和已有分支。

如果 issue 仍有未完成依赖、HITL 决策点或阻塞项，不要创建开发分支。先说明阻塞原因。

## 输出物

- 一个基于最新主干的 issue 分支。
- 开始记录，可选写入 `team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.start.md`。
- 明确的下一步：进入 `team-issue-implement`。

## 分支规则

- 一个 issue 一个分支。
- 一个分支只服务一个 PR。
- 不要直接在主干开发。
- 不要在脏工作区切换或创建分支，除非用户明确确认如何处理未提交变更。

推荐分支名：

```text
issue-{number}-{short-slug}
```

如果没有 issue 编号：

```text
issue-{yyyy-mm-dd}-{short-slug}
```

## 工作流

1. 读取 issue，确认 `Blocked by`、`Type` 和验收标准。
2. 检查当前 git 状态。
3. 如果工作区有无关变更，停止并要求用户决定如何处理。
4. 确认主干分支名称，通常是 `main`。
5. 同步最新主干。
6. 基于主干创建 issue 分支。
7. 输出分支名、issue 摘要和下一步。

## 完成标准

- 当前分支是 issue 分支。
- issue 依赖已满足。
- 工作区没有无关变更。
- 可以安全进入 `team-issue-implement`。
