---
name: team-issue-verify
description: 独立验证单个 issue 的实现是否满足验收标准、关联 PRD 和风险约束，输出验证报告、遗漏项、回归风险和是否 ready for PR 的结论。Verify whether a single issue implementation satisfies acceptance criteria, the linked PRD, and risk constraints, producing a verification report, gaps, regression risks, and readiness status.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 验证实现
  - 检查 issue 是否完成
  - 能提 PR 了吗
  - 实现完了帮我验一下
  - verify issue
  - check implementation
  - ready for PR
  - is this implementation complete
---

# Issue 验证

这个技能用于确认 `team-issue-implement` 的结果是否真的满足 issue 和 PRD，而不是只确认“代码写完了”。它应尽量独立于实现过程进行判断，优先检查外部行为、验收标准和回归风险。

## 输入物

主输入：

- 已实现的单个 issue，来自 `team-spec/active/{slug}/issues/` 或外部 issue tracker。
- 当前代码变更和测试变更。
- `team-issue-implement` 的验证结果或实现总结，如果已有。

参考输入：

- `team-spec/config.yml` 中的语言与 `version_control` 配置，用于判断 ready 后应推荐 GitHub PR 还是 GitLab MR，以及默认主干分支和贡献方式。
- `team-spec/active/{slug}/prd/prd.md` 中的关联 PRD。
- `team-spec/CONTEXT.md` 中的全局规范术语、角色和通用业务规则。
- `team-spec/decisions/` 中的跨需求产品决策。
- `team-spec/active/{slug}/spec/CONTEXT.md` 中的规范术语和业务规则。
- `team-spec/active/{slug}/spec/decisions/` 中的产品决策。
- `team-spec/active/{slug}/spec/reviews.md` 中的风险评审。
- 项目现有测试、CI 配置、发布说明、迁移说明或操作文档。

如果本技能在同一对话中紧接 `team-issue-implement` 执行，上述参考输入已在对话上下文中，无需重新读取文件。只有在独立执行或新对话中才需要从文件加载参考输入。

如果无法确认关联 issue 或验收标准，不要给出 ready 结论。先说明缺少的输入。

## 输出物

- 验证报告。
- Ready 状态：`ready for PR`、`needs changes`、`blocked`。
- 未覆盖验收标准。
- 回归风险和建议补测项。
- 实际运行的验证命令和结果。
- 优先回写原 issue 文件中的 `## Acceptance Criteria Coverage`、`## Status`、`## Findings`、`## Notes` 或同类章节。
- 如果原 issue 文件不可修改，或外部 issue tracker 不支持回写，再写入 `team-spec/active/{slug}/issues/{issue-number}-{short-issue-slug}.verification.md`。

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
7. 优先更新原 issue 文件，把通过的验收项勾选，未通过的验收项保留未勾选并写明原因。
8. 输出 ready 判断和需要补充的具体行动。

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

## 原 Issue 回写规则

- 通过的验收项应在原 issue 文件中勾选。
- 未通过的验收项应保留未勾选，并在对应条目后写明失败原因，或在 `## Findings` 中逐条说明。
- 如果 issue tracker 不允许编辑原内容，则用单独 verification 报告承载同样的信息。
- 不要因为验证失败而删除原 issue 内容，只能补充状态、原因和修订建议。

## 完成标准

只有同时满足以下条件，才能给出 `ready for PR`：

- 所有非延期验收标准都有验证证据。
- 相关测试通过，或未运行测试的原因可接受且已说明。
- 没有未处理的 P0/P1 回归风险。
- 没有未解决的 HITL 决策点。
- 代码变更范围与 issue 匹配。

否则输出 `needs changes` 或 `blocked`，并给出具体补救动作。

当输出 `ready for PR` 时，最终回复必须用有序号的列表选项推荐下一步，方便用户直接回复序号继续推进：

推荐前先读取 `team-spec/config.yml` 的 `version_control`。如果缺失，先用 `git remote -v`、`git branch --show-current`、`git branch -r`、`git symbolic-ref refs/remotes/{remote}/HEAD` 和 `git config --get branch.{branch}.remote` 推断平台、主干分支和贡献方式；无法唯一判断时，询问用户缺失的最小信息，并在用户确认后回写 `team-spec/config.yml`。平台信号明确时，只推荐对应的 PR/MR 创建技能，不要机械地同时列 GitHub 和 GitLab。

```md
## 下一步可选

1. `team-issue-create-mr-gitlab`：检测到 GitLab remote，推送当前 issue 分支并创建关联 issue 的 Merge Request。
2. 完成人工确认：如果主干分支或贡献方式无法唯一推断，先确认后回写 `team-spec/config.yml`。
```
