---
name: team-issue-pr
description: 在单个 issue 实现并验证后，整理变更、提交、推送分支并创建 PR，确保 PR 描述关联 issue、验证结果和风险说明。After a single issue is implemented and verified, commit changes, push the issue branch, and open a PR with linked issue context, verification results, and risk notes.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# Issue 提交 PR

这个技能是可选工程协作技能，用于在 `team-issue-verify` 通过后，将当前 issue 分支提交并创建 PR。只有当团队允许 AI 协助提交、推送和创建 PR 时才使用。它不负责修复实现问题；如果验证未通过，应回到 `team-issue-implement`。

如果团队已有 commit、push、PR、review 或 merge 流程，必须优先遵守团队规则。不要为了使用本技能而改变团队既有习惯。

## 输入物

主输入：

- 当前 issue 分支上的代码和测试变更。
- `team-issue-verify` 的验证结果，状态应为 `ready for PR`。
- 当前 issue，来自 `team-spec/issues/{slug}/` 或外部 issue tracker。

参考输入：

- `team-spec/prd/{slug}.md` 中的关联 PRD。
- `team-spec/spec/reviews/{slug}.md` 中的风险评审。
- 原 issue 文件中的 `## Status`、`## Acceptance Criteria Coverage`、`## Findings`、`## Notes` 或同类章节。
- 项目 PR 模板、贡献指南、CI 要求和分支保护规则。

如果验证状态不是 `ready for PR`，或原 issue 文件中仍有未勾选的非延期验收项，不要提交 PR。先说明应回到 `team-issue-implement` 或 `team-issue-verify`。

## 输出物

- Git commit。
- 推送后的远程 issue 分支。
- PR 或 draft PR。
- PR 摘要，包括 issue、验证命令和风险说明。
- 原 issue 文件如可编辑，可补充 `## Status` 为 `pr-open` 或写入 PR 链接；如果不可编辑，至少在 PR 描述中体现。

## 工作流

1. 确认当前不在主干分支。
2. 检查 git diff，确认变更只围绕当前 issue。
3. 读取验证报告，确认 `ready for PR`。
4. 读取原 issue 文件，确认所有非延期验收项均已勾选，且没有新的未解决 findings。
5. 运行必要的最终测试或检查命令。
6. 暂存相关文件。
7. 创建清晰 commit。
8. 推送当前 issue 分支。执行 push 前必须确认团队允许 AI 推送，且用户已授权。
9. 创建 PR 或 draft PR。执行前必须确认目标远程、目标分支、PR 类型和团队规则。
10. 输出 PR 链接、验证结果和后续动作。

如果用户只想手动提交或开 PR，本技能应输出 PR 文案、commit message 和建议命令，不直接执行 Git 或 GitHub 操作。

## Commit 规则

提交信息应简洁说明 issue 结果：

```text
Implement {issue short title}
```

如果项目已有 commit 规范，优先遵守项目规范。

## PR 内容

PR 描述至少包含：

- Linked issue。
- What changed。
- How verified。
- Known risks。
- Screenshots 或录屏，如果涉及 UI。

## 完成标准

- PR 已创建或 draft PR 已创建。
- PR 描述包含验证结果。
- 原 issue 文件中的验收项已全部勾选，或已在 PR 描述中明确列出例外并获得用户确认。
- 当前分支已推送到远程。
- 用户知道下一步是 review、CI 或 merge。

不要自动合并 PR，除非用户明确要求并且项目规则允许。
