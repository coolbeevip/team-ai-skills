---
name: team-tech-debt-review
description: 评审技术债规格的风险与可执行性，确认优先级、阻塞项、处理动作和是否可进入工程拆解。Review technical debt specs for risk and execution readiness, then output blockers, mitigations, and readiness for issue breakdown.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# 技术债评审

这个技能用于评审技术债规格是否足够清晰、可执行、可验收，并判断是否可以进入工程 issue 拆解。

## 输入物

- 当前对话中的技术债结论、证据和约束。
- `team-spec/spec/refine/{slug}.md`，这是主输入。
- `team-spec/spec/CONTEXT.md` 与 `team-spec/spec/decisions/`（如存在）。
- 相关代码、监控、事故、缺陷、性能或运维材料。

必须先确定本次评审对应的 slug。技术债链路的 slug 必须包含 `debt`，如 `{yyyy-mm-dd}-debt-{short-english-slug}`。无法唯一判断时必须要求用户提供，不得猜测。

## 输出物

- 对话中的评审结论：`ready` / `needs refinement` / `blocked`。
- `team-spec/spec/reviews/{slug}.md`：技术债评审报告。
- 给下游 `team-tech-debt-to-issues` 的拆解前置结论（阻塞项、依赖、验收风险、HITL 决策点）。

## 评审维度

- 问题与证据是否充分，是否存在“感受型”而非“证据型”结论。
- 范围、优先级和非目标是否清晰。
- 技术依赖、兼容性、回滚、迁移、发布策略是否可执行。
- 安全、合规、稳定性、性能和可维护性风险是否可控。
- 验收口径是否可观察、可测试、可复核。
- owner、依赖方、截止点是否明确。

## 处理原则

- 发现 P0 或关键 P1 时，输出 `needs refinement` 或 `blocked`，并明确回到 `team-tech-debt-refine` 要补充的内容。
- 不编造风险；证据不足时明确指出缺口。
- 每个重要风险都要落到建议动作、owner 和截止点。

## 完成标准

- 生成 `team-spec/spec/reviews/{slug}.md`。
- 明确是否可进入 `team-tech-debt-to-issues`。
- 如果不可进入，明确 Required Refinement 与 Questions For User。
