---
name: team-issue-pr
description: 在单个 issue 验证通过后，提交变更、推送分支并创建 PR，确保 PR 描述包含 issue 关联与验证结果。 触发词：开 PR、提交 issue、推送分支。After issue verification passes, commit, push, and open a PR with linked issue context and verification evidence. Keywords: open PR, submit issue, push branch.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# Issue 提交 PR

可选技能：仅在验证通过后执行提交流程。

## 通用规则（引用）

- [COMMON-RULES.md](../../COMMON-RULES.md)

## 输入物

- 当前 issue 分支代码与测试变更。
- `team-issue-verify` 输出（应为 `ready for PR`）。
- `team-spec/issues/{slug}/...` 的当前 issue。
- 可选：`team-spec/prd/{slug}.md`、`team-spec/spec/reviews/{slug}.md`。

## 输出物

- Git commit 与远程 issue 分支。
- PR 或 draft PR。
- PR 摘要：关联 issue、变更说明、验证结果、已知风险。
- 可选回写 issue 状态为 `pr-open`。

## 执行步骤

1. 校验唯一 issue 与当前分支上下文。
2. 确认验证状态为 `ready for PR` 且验收项无未解释缺口。
3. 检查变更范围仅围绕当前 issue。
4. 提交并推送分支（按团队授权与规则）。
5. 创建 PR，并输出链接与下一步动作。

## 规则清单（必须/禁止）

- 必须在非主干 issue 分支执行。
- 必须在 PR 描述中给出验证命令与结果。
- 必须关联当前 issue。
- 禁止在验证未通过时创建正式 PR。
- 禁止自动合并 PR（除非用户明确要求且规则允许）。

## 失败与回退

- issue 不明确：停止并要求 issue 路径/编号。
- 验证未通过：回退 `team-issue-implement` 或 `team-issue-verify`。
- 用户不允许自动 Git/GitHub 操作：仅输出 commit/PR 文案建议。

## 最小输出模板

```md
## Linked Issue
- ...

## What Changed
- ...

## How Verified
- ...

## Known Risks
- ...
```

## 完成前检查

- 验证状态已满足提 PR 前置条件。
- PR 描述包含 issue、验证、风险三要素。
- 用户已知下一步是 review / CI / merge。
