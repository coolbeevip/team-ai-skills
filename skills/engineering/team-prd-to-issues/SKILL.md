---
name: team-prd-to-issues
description: 将 PRD 拆解成可独立领取、可验证、按依赖排序的工程 issues，优先端到端 vertical slice。 触发词：拆解任务、PRD 转 issue、工程切片。Break a PRD into independently actionable, testable issues using dependency-ordered vertical slices. Keywords: PRD to issues, task breakdown, vertical slice.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# PRD 转工程 Issues

用于把 PRD 转成可执行 issue 列表。

## 通用规则（引用）

- [COMMON-RULES.md](../../COMMON-RULES.md)

## 输入物

- `team-spec/prd/{slug}.md`（主输入，必需）。
- `team-spec/spec/reviews/{slug}.md`、`team-spec/spec/refine/{slug}.md`（参考）。
- `team-spec/spec/CONTEXT.md`、`team-spec/spec/decisions/`（参考）。

## 输出物

- `team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.md`（默认输出）。
- 对话中的 issue 草案清单：标题、类型、依赖、覆盖场景、切片理由。
- 下游可用的 issue 执行入口（供 `team-issue-next` 选择）。

## 执行步骤

1. 校验唯一 `{slug}` 或明确 PRD 路径；不唯一则停止。
2. 读取 PRD 主目标、范围、验收标准、约束。
3. 按 vertical slice 草拟 issue，并标注 `AFK/HITL` 与依赖。
4. 先向用户确认粒度与顺序，再落盘到 `team-spec/issues/{slug}/`。
5. 输出“下一步使用 `team-issue-next`”。

## 规则清单（必须/禁止）

- 必须以 PRD 为主输入，不绕过 PRD 直接使用澄清材料。
- 必须确保每个 issue 可独立验证，有可观察结果。
- 必须先发布 blocker，再发布被依赖 issue。
- 禁止按纯分层任务拆解（仅 DB/API/UI）。
- 禁止创建循环依赖。

## 失败与回退

- 无 PRD 或 PRD 不明确：停止并要求提供 `team-spec/prd/{slug}.md`。
- 关键上下文缺失：输出最少澄清问题后暂停，不直接发布 issue。
- 用户未确认粒度：保留草案，不进入正式输出。

## 最小输出模板

```md
## What to build
- ...

## Type
AFK | HITL

## Acceptance criteria
- [ ] Given ... When ... Then ...

## Blocked by
- None | #{id}
```

## 完成前检查

- 输出目录为 `team-spec/issues/{slug}/`。
- 每个 issue 都有类型与依赖。
- 依赖顺序可执行、无环。
- 下游 `team-issue-next` 可直接选择下一项。
