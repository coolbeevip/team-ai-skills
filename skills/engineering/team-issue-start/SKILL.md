---
name: team-issue-start
description: 在实现前为单个 issue 准备干净工作区与 issue 分支，确认依赖已满足并可安全开工。触发词：开始 issue、准备分支、同步主干。Prepare a clean workspace and issue branch before implementation. Keywords: start issue, prepare branch, clean workspace.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# Issue 开始

可选技能：只做开工准备，不写实现代码。

## 通用规则（引用）

- [COMMON-RULES.md](../../COMMON-RULES.md)

## 输入物

- `team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.md`（主输入）。
- `team-spec/prd/{slug}.md`、`team-spec/spec/reviews/{slug}.md`（参考）。
- 当前 git 状态与分支规则。

## 输出物

- 已确认可开始的 issue 分支信息。
- 可选记录：`team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.start.md`。
- 下一步建议：`team-issue-implement`。

## 执行步骤

1. 校验唯一 issue 路径与 `{slug}`。
2. 检查 `Blocked by`、HITL 决策点、验收标准完整性。
3. 检查工作区是否干净，确认主干同步策略。
4. 按团队规则创建 issue 分支（若用户授权且需要自动执行）。
5. 输出分支名与开工摘要。

## 规则清单（必须/禁止）

- 必须一个 issue 对应一个分支。
- 必须在脏工作区时先暂停并让用户决策。
- 必须遵守团队既有分支命名与流程。
- 禁止在依赖未满足时开工。
- 禁止把本技能用于代码实现。

## 失败与回退

- issue 不唯一：停止并要求提供 issue 路径或编号。
- 依赖未满足：回退 `team-issue-next` 或上游决策。
- 用户不希望自动 Git 操作：只输出建议命令与检查清单。

## 最小输出模板

```md
## Issue
{path}

## Branch
issue-{number}-{short-slug}

## Next Step
Run team-issue-implement
```

## 完成前检查

- 当前 issue 与分支映射明确。
- 依赖状态已确认。
- 工作区状态可安全进入实现阶段。
