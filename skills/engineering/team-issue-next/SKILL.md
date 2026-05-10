---
name: team-issue-next
description: 从 team-spec/issues/{slug}/ 中识别下一个可开始的 issue，基于状态、依赖和优先级输出明确的下一步，不写代码、不建分支。Select the next actionable issue from team-spec/issues/{slug}/ based on status, dependencies, and priority, without writing code or creating branches.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# 下一个 Issue

这个技能用于在一个 PRD 拆出的多个 issue 中选择下一个可开始的 issue。它只做编排判断，不实现代码、不创建分支、不提交 PR。

## 输入物

主输入：

- `team-spec/issues/{slug}/`。
- 或外部 issue tracker 中同一个 PRD / milestone / label 下的 issue 列表。

参考输入：

- `team-spec/prd/{slug}.md`。
- 已打开或已合并的 PR 状态。
- 当前 git 主干状态。

如果无法唯一确定 `{slug}` 或 issue 列表，应停止并要求用户提供 `team-spec/issues/{slug}/` 路径、slug、milestone 或 issue 列表，不要猜测。

## 输出物

- 下一个可开始 issue 的明确路径或链接。
- 选择理由。
- 被阻塞 issue 列表。
- 已完成 issue 列表。
- 下一步技能：`team-issue-start`。

## Issue 状态

优先读取 issue 文件中的状态：

```md
## Status

todo / in-progress / pr-open / merged / blocked
```

如果没有状态字段，按以下方式推断：

- `merged`：关联 PR 已合并，或用户明确说明已完成。
- `pr-open`：已有未合并 PR。
- `blocked`：`Blocked by` 中存在未完成依赖。
- `todo`：没有未完成依赖，且未开始。
- `unknown`：无法判断。

遇到 `unknown` 时，不要猜。要求用户提供 PR 或 issue 状态。

## 选择规则

1. 排除 `merged` 和 `pr-open`。
2. 排除仍有未完成依赖的 `blocked`。
3. 在 `todo` 中选择优先级最高的 issue。
4. 如果没有显式优先级，选择编号最小的 issue。
5. 如果多个 issue 同优先级且无编号，要求用户选择。

## 输出格式

```md
## Next Issue

{team-spec/issues/{slug}/{issue-file}.md}

## Why This Issue

- No unfinished dependencies.
- Lowest issue number among ready issues.

## Ready Issues

- ...

## Blocked Issues

- Issue: blocked by ...

## Done / In Progress

- ...

## Next Step

Run `team-issue-start` with {issue path}.
```

## 完成标准

- 明确给出一个可开始 issue，或明确说明为什么无法选择。
- 不创建分支。
- 不修改代码。
- 不标记 issue 完成。
- 不打开 PR。
