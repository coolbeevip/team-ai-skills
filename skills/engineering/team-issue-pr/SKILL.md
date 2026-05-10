---
name: team-issue-pr
description: 在单个 issue 实现并验证后，整理变更、提交、推送分支并创建 PR，确保 PR 描述关联 issue、验证结果和风险说明。After a single issue is implemented and verified, commit changes, push the issue branch, and open a PR with linked issue context, verification results, and risk notes.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# Issue 提交 PR

这个技能用于在 `team-issue-verify` 通过后，将当前 issue 分支提交并创建 PR。它不负责修复实现问题；如果验证未通过，应回到 `team-issue-implement`。

## 输入物

主输入：

- 当前 issue 分支上的代码和测试变更。
- `team-issue-verify` 的验证报告，状态应为 `ready for PR`。
- 当前 issue，来自 `team-spec/issues/{slug}/` 或外部 issue tracker。

参考输入：

- `team-spec/prd/{slug}.md` 中的关联 PRD。
- `team-spec/spec/reviews/{slug}.md` 中的风险评审。
- 项目 PR 模板、贡献指南、CI 要求和分支保护规则。

如果验证状态不是 `ready for PR`，不要提交 PR。先说明应回到 `team-issue-implement` 或 `team-issue-verify`。

## 输出物

- Git commit。
- 推送后的远程 issue 分支。
- PR 或 draft PR。
- PR 摘要，包括 issue、验证命令和风险说明。

## 工作流

1. 确认当前不在主干分支。
2. 检查 git diff，确认变更只围绕当前 issue。
3. 读取验证报告，确认 `ready for PR`。
4. 运行必要的最终测试或检查命令。
5. 暂存相关文件。
6. 创建清晰 commit。
7. 推送当前 issue 分支。
8. 创建 PR 或 draft PR。
9. 输出 PR 链接、验证结果和后续动作。

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
- 当前分支已推送到远程。
- 用户知道下一步是 review、CI 或 merge。

不要自动合并 PR，除非用户明确要求并且项目规则允许。
