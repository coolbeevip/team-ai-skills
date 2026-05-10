---
name: team-issue-verify
description: 独立验证单个 issue 的实现是否满足验收标准、关联 PRD 和风险约束，输出验证报告、遗漏项、回归风险和是否 ready for PR 的结论。Verify whether a single issue implementation satisfies acceptance criteria, the linked PRD, and risk constraints, producing a verification report, gaps, regression risks, and readiness status.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# Issue 验证

这个技能用于确认 `team-issue-implement` 的结果是否真的满足 issue 和 PRD，而不是只确认“代码写完了”。它应尽量独立于实现过程进行判断，优先检查外部行为、验收标准和回归风险。

## 输入物

主输入：

- 已实现的单个 issue，来自 `team-spec/issues/` 或外部 issue tracker。
- 当前代码变更和测试变更。
- `team-issue-implement` 的验证结果或实现总结，如果已有。

参考输入：

- `team-spec/prd/{slug}.md` 中的关联 PRD。
- `team-spec/spec/CONTEXT.md` 中的规范术语和业务规则。
- `team-spec/spec/decisions/` 中的产品决策。
- `team-spec/spec/reviews/{slug}.md` 中的风险评审。
- 项目现有测试、CI 配置、发布说明、迁移说明或操作文档。

如果无法确认关联 issue 或验收标准，不要给出 ready 结论。先说明缺少的输入。

## 输出物

- 验证报告。
- Ready 状态：`ready for PR`、`needs changes`、`blocked`。
- 未覆盖验收标准。
- 回归风险和建议补测项。
- 实际运行的验证命令和结果。
- 如需沉淀报告，写入 `team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.verification.md`。

## 验证原则

- 验证外部行为，不验证实现偏好。
- 先对照 issue 验收标准，再对照 PRD 目标和非目标。
- 不因为测试通过就自动判定 ready；还要检查验收标准是否覆盖完整。
- 不因为代码风格偏好阻塞，除非影响可维护性、正确性或团队约定。
- 发现需求不一致时，标记为上游问题，不在验证阶段隐式改需求。

## 工作流

1. 读取 issue，列出所有验收标准。
2. 读取关联 PRD 和风险评审，确认上下文和约束。
3. 检查当前代码变更是否只围绕该 issue，是否混入无关改动。
4. 运行相关自动化测试；如果测试命令未知，先查项目文档或 package 配置。
5. 做验收标准逐项映射：每项对应哪个测试、代码路径或手工验证。
6. 检查边界情况、权限、数据状态、错误路径和回归风险。
7. 输出 ready 判断和需要补充的具体行动。

## 输出格式

```md
# Verification Report: {issue title}

## Status

ready for PR / needs changes / blocked

## Acceptance Criteria Coverage

- [x] {criterion}: covered by {test or verification}
- [ ] {criterion}: missing because {reason}

## Commands Run

- `{command}`: passed / failed / not run

## Findings

- Severity: issue, evidence, recommended fix.

## Regression Risks

- Risk and suggested test or mitigation.

## Required Changes

- Actionable item, owner if known.

## Notes

- Assumptions, skipped checks, or manual verification needs.
```

## 完成标准

只有同时满足以下条件，才能给出 `ready for PR`：

- 所有非延期验收标准都有验证证据。
- 相关测试通过，或未运行测试的原因可接受且已说明。
- 没有未处理的 P0/P1 回归风险。
- 没有未解决的 HITL 决策点。
- 代码变更范围与 issue 匹配。

否则输出 `needs changes` 或 `blocked`，并给出具体补救动作。
