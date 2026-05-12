---
name: team-spec-refine
description: 通过与用户迭代澄清需求规格，在 PRD 前固化术语、范围、规则和验收口径。 触发词：细化需求、澄清规格、补齐边界。Refine specs before PRD by clarifying terms, scope, rules, and acceptance criteria. Keywords: refine spec, clarify scope, requirement discovery.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# 规格细化

用于把模糊需求收敛为可评审、可固化的规格，不直接替代 PRD。

## 通用规则（引用）

- [COMMON-RULES.md](../../COMMON-RULES.md)

## 输入物

- 当前对话中的需求描述与业务背景。
- `team-spec/spec/refine/{slug}.md`（同一需求的历史版本，如存在）。
- `team-spec/spec/reviews/{slug}.md`（如存在且为 `needs refinement`，优先处理）。
- `team-spec/spec/CONTEXT.md`、`team-spec/spec/decisions/`（如存在）。
- 相关文档或代码证据。

## 输出物

- `team-spec/spec/refine/{slug}.md`（主输出，持续更新同一文件）。
- `team-spec/spec/CONTEXT.md`（术语/流程/规则确认后更新）。
- `team-spec/spec/decisions/{number}-{slug}.md`（仅长期有效且高反悔成本决策）。
- 对话中的短结论：已确认点、剩余最高风险、下一个问题。

## 执行步骤

1. 先校验唯一 `{slug}` 或明确 refine 文件路径；不唯一则停止并要求用户补充。
2. 复述需求并提出当前“最大不确定点”的单一问题（一次只问一个关键问题）。
3. 基于用户回答更新 refine 主文件，并同步术语到 `CONTEXT.md`（如已确认）。
4. 若出现高反悔成本产品判断，再记录到 `decisions/`。
5. 形成最小收敛结论并建议下一步：继续 refine 或进入 `team-spec-review`。

## 规则清单（必须/禁止）

- 必须把模糊表述改成可观察行为。
- 必须区分范围内、范围外、延期项。
- 必须优先查现有文档/代码，再向用户追问。
- 禁止在关键假设不稳定时直接产出 PRD。
- 禁止为同一需求重复新建 slug。

## 失败与回退

- 无法唯一确定 slug：停止并索要 slug 或 refine 路径。
- 缺少关键输入导致无法判断：仅输出已确认事实和缺失清单，不编造结论。
- 评审反馈为 `needs refinement`：回到本技能继续更新同一 `refine/{slug}.md`。

## 最小输出模板

```md
# Refine: {slug}

## 已确认
- ...

## 待确认
- ...

## 变更记录
- {date}: {reason}
```

## 完成前检查

- slug 与文件路径唯一且一致。
- 输出仅写入 `team-spec/spec/` 工作空间。
- 术语与规则已同步到可复用上下文（如适用）。
- 下游 `team-spec-review` 可直接读取本次输出。
