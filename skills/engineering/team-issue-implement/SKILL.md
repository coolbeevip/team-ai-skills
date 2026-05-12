---
name: team-issue-implement
description: 基于单个工程 issue 实现代码与测试，优先行为测试和 TDD red-green-refactor 循环。 触发词：实现 issue、写代码、补测试。Implement one issue with behavior-focused tests and a red-green-refactor loop. Keywords: implement issue, TDD, behavior tests.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# Issue 实现

用于完成单个 issue 的最小可验证实现。

## 通用规则（引用）

- [COMMON-RULES.md](../../COMMON-RULES.md)

## 输入物

- `team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.md`（主输入）。
- `team-spec/prd/{slug}.md`（主业务边界参考）。
- `team-spec/spec/CONTEXT.md`、`team-spec/spec/decisions/`、`team-spec/spec/reviews/{slug}.md`（参考）。

## 输出物

- 代码变更与测试变更。
- issue 回写：`Status`、`Implementation Notes`、`Acceptance Criteria Coverage`（优先写回原 issue）。
- 如不可回写：`team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.implementation.md`。

## 执行步骤

1. 校验唯一 issue 路径，确认依赖与验收标准。
2. 制定最小行为清单，按验收项逐条实现。
3. 执行 red-green-refactor：先失败测试，再最小实现，再重构。
4. 运行相关测试并记录结果。
5. 回写实现覆盖与剩余风险，交给 `team-issue-verify`。

## 规则清单（必须/禁止）

- 必须测外部行为，不测实现细节。
- 必须一次只处理一个可验证切片。
- 必须优先使用 `CONTEXT.md` 术语。
- 禁止在依赖未满足或 HITL 未决时直接实现。
- 禁止顺手修改无关需求文档。

## 失败与回退

- issue 不明确：停止并索要 issue 路径/编号。
- 依赖未完成：回退上游处理阻塞项。
- 测试或实现受外部条件阻塞：输出阻塞原因与下一步建议，不伪装成功。

## 最小输出模板

```md
## Implemented Issue
{issue path}

## Files Changed
- ...

## Acceptance Coverage
- ...

## Tests
- {command}: passed/failed
```

## 完成前检查

- 变更范围与单个 issue 对齐。
- 验收项有对应实现或明确缺口。
- 测试结果已记录，可交给验证技能复核。
