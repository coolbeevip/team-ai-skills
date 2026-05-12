---
name: team-issue-next
description: 从 team-spec/issues/{slug}/ 中选择下一个可开始 issue，基于状态、依赖和优先级输出明确下一步。触发词：下一个任务、选 issue、依赖排程。Pick the next actionable issue from team-spec/issues/{slug}/ using status, dependencies, and priority. Keywords: next issue, issue scheduling, dependency selection.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# 下一个 Issue

用于编排选择，不负责写代码或开分支。

## 通用规则（引用）

- [COMMON-RULES.md](../../COMMON-RULES.md)

## 输入物

- `team-spec/issues/{slug}/`（主输入）。
- `team-spec/prd/{slug}.md`（参考）。
- 可选：PR 状态或外部 tracker 状态。

## 输出物

- 下一个可开始 issue 路径（或链接）。
- 就绪列表、阻塞列表、已完成/进行中列表。
- 下一步建议：`team-issue-start` 或 `team-issue-implement`。

## 执行步骤

1. 校验唯一 `{slug}` 或明确 issue 目录路径。
2. 读取 issue 状态与依赖（`Blocked by`）。
3. 过滤完成态与阻塞态，按优先级/编号选择下一项。
4. 输出选择理由和剩余队列。

## 规则清单（必须/禁止）

- 必须显式说明“为何这个 issue 可开始”。
- 必须把 `ready for PR` 视为完成态（无反证时）。
- 必须遇到 `unknown` 状态就停下索要信息。
- 禁止猜测 issue 状态。
- 禁止标记 issue 完成或修改代码。

## 失败与回退

- slug 或 issue 集不明确：停止并要求路径/slug。
- 状态不可判定：返回缺失信息清单。
- 多个候选同优先级且不可区分：要求用户选择。

## 最小输出模板

```md
## Next Issue
{path}

## Why
- ...

## Blocked
- ...
```

## 完成前检查

- 已明确一个可开始 issue，或明确无法选择原因。
- 阻塞关系说明清晰。
- 输出不包含代码实现动作。
