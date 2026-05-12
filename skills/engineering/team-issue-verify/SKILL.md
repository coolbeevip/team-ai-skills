---
name: team-issue-verify
description: 独立验证单个 issue 实现是否满足验收标准、PRD 约束与风险要求，并输出 ready 结论。 触发词：验证 issue、验收检查、ready for PR。Verify a single issue against acceptance criteria, PRD constraints, and risks, then decide readiness. Keywords: verify issue, acceptance check, ready for PR.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# Issue 验证

用于独立判断实现是否可进入 PR 阶段。

## 通用规则（引用）

- [COMMON-RULES.md](../../COMMON-RULES.md)

## 输入物

- 单个已实现 issue（`team-spec/issues/{slug}/...`）。
- 当前代码与测试变更。
- `team-spec/prd/{slug}.md`、`team-spec/spec/reviews/{slug}.md`（参考）。
- `team-issue-implement` 的实现总结（如有）。

## 输出物

- 验证结论：`ready for PR` / `needs changes` / `blocked`。
- 验收覆盖映射、回归风险、补救动作。
- issue 回写：`Status`、`Acceptance Criteria Coverage`、`Findings`。
- 如不可回写：`team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.verification.md`。

## 执行步骤

1. 校验唯一 issue 与 `{slug}`。
2. 列出全部验收标准并逐项映射测试/证据。
3. 运行相关验证命令并记录结果。
4. 识别回归风险与未覆盖项。
5. 输出状态并回写 issue。

## 规则清单（必须/禁止）

- 必须先看验收覆盖，再给 ready 结论。
- 必须报告实际执行命令与结果。
- 必须把需求不一致标记为上游问题。
- 禁止“测试通过=自动 ready”。
- 禁止删除原 issue 内容。

## 失败与回退

- issue 或验收标准不完整：停止并索要缺失输入。
- 关键验证无法运行：说明原因并输出 `needs changes` 或 `blocked`。
- 出现未解决 P0/P1 风险：不得给 `ready for PR`。

## 最小输出模板

```md
## Status
ready for PR | needs changes | blocked

## Acceptance Criteria Coverage
- [x] ...
- [ ] ...

## Commands Run
- ...
```

## 完成前检查

- 所有非延期验收项有证据或有明确缺失说明。
- 状态结论与证据一致。
- issue 已回写可执行的后续动作。
