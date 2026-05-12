---
name: team-spec-review
description: 评审已细化规格的风险与 ready 状态，输出阻塞项、风险分级和补救动作。 触发词：规格评审、ready gate、风险检查。Review refined specs for readiness, blockers, and mitigations. Keywords: spec review, readiness gate, risk assessment.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# 规格评审

用于判断规格是否可进入 PRD 固化。

## 通用规则（引用）

- [COMMON-RULES.md](../../COMMON-RULES.md)

## 输入物

- `team-spec/spec/refine/{slug}.md`（主输入）。
- `team-spec/spec/CONTEXT.md`、`team-spec/spec/decisions/`。
- `team-spec/spec/reviews/{slug}.md`（历史评审，如存在）。
- 相关 PRD、代码或文档证据。

## 输出物

- `team-spec/spec/reviews/{slug}.md`（主输出）。
- 对话短结论：`ready` / `needs refinement` / `blocked`。
- 给下游 `team-spec-to-prd` 的前置检查结论。

## 执行步骤

1. 校验唯一 `{slug}` 或明确 refine 文件路径；不唯一则停止。
2. 读取 refine 主文件并做 P0/P1 优先评审。
3. 输出阻塞项、风险清单、问题清单与建议动作（含 owner 与截止点）。
4. 写入 `reviews/{slug}.md`，状态明确为 `ready`、`needs refinement` 或 `blocked`。
5. 若非 `ready`，明确要求回到 `team-spec-refine`。

## 规则清单（必须/禁止）

- 必须优先报告会导致返工或事故的高等级风险。
- 必须给出可执行补救动作，不只说“需要明确”。
- 必须区分“证据不足”与“风险确认”。
- 禁止编造风险证据。
- 禁止直接修改 `refine/{slug}.md` 内容。

## 失败与回退

- 缺少关键输入：只输出可判断部分与缺失项。
- slug 不明确：停止并索要 slug 或 refine 路径。
- 发现 P0/关键 P1：回退到 `team-spec-refine` 修订。

## 最小输出模板

```md
# Review: {slug}

## Status
{ready | needs refinement | blocked，三选一}

## Blockers
- [P0/P1] ...

## Risks
- [P1/P2/P3] ...

## Questions For User
- ...
```

## 完成前检查

- 状态字段存在且合法。
- 阻塞项仅列 P0 与关键 P1。
- 输出路径为 `team-spec/spec/reviews/{slug}.md`。
- 下游 `team-spec-to-prd` 可直接使用结论。
