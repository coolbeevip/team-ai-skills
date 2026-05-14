---
name: team-issue-implement
description: 根据 team-spec/issues/ 中的单个工程 issue 进行实现，优先采用行为测试和 TDD 的 red-green-refactor 循环，最终输出代码变更、测试变更和验证结果。Implement a single engineering issue from team-spec/issues/ using behavior-focused tests and a red-green-refactor loop, producing code changes, tests, and verification results.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 实现 issue
  - 开始写代码
  - 按 issue 编码
  - 实现这个功能
  - implement issue
  - start coding
  - implement this feature
  - code this issue
---

# Issue 实现

这个技能用于把 `team-prd-to-issues` 产生的单个 issue 实现为可验证的代码变更。TDD 是默认实现策略，但不是形式主义；目标是通过公共接口验证外部行为，而不是测试实现细节。

## 输入物

主输入必须是一个明确的 issue：

- `team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.md`
- 或外部 issue tracker 中的单个 issue。

参考输入可以包括：

- `team-spec/prd/{slug}.md` 中的关联 PRD。
- `team-spec/spec/CONTEXT.md` 中的规范术语和业务规则。
- `team-spec/spec/decisions/` 中的产品决策。
- `team-spec/spec/reviews/{slug}.md` 中的风险评审。
- 当前代码库、测试、ADR、接口文档和现有实现。

如果 issue 没有验收标准、依赖未完成、或仍有 HITL 决策点，不要直接实现。先说明阻塞项，并要求回到 `team-prd-to-issues` 或人工决策。

必须先确定要实现的单个 issue，即明确的 `team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.md` 或外部 issue 链接/编号。若无法从用户请求、当前分支、当前对话或文件路径中唯一判断，应停止并要求用户提供 issue 路径、issue 编号或链接，不要猜测要实现哪个 issue。

## 输出物

- 代码变更。
- 测试变更。
- 验证结果，包括运行了哪些测试、是否通过。
- 优先回写原 issue 文件中的 `## Status`、`## Implementation Notes`、`## Acceptance Criteria Coverage` 或同类章节。
- 如果原 issue 文件不可修改，再写入 `team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.implementation.md`，目录只在需要时创建。

不要修改 PRD、规格评审或产品决策，除非用户明确要求。发现需求问题时，应反馈给上游技能，而不是在实现中隐式改需求。

## 核心原则

- 测行为，不测实现细节。
- 通过公共接口验证，不直接测试私有方法或内部数据结构。
- 一次只实现一个 vertical slice。
- 不要一次性写完所有测试再实现。
- 不要在 RED 状态重构。
- 不要提前实现 speculative feature。
- 保持测试名称和领域术语一致，优先使用 `team-spec/spec/CONTEXT.md` 中的规范语言。

## 工作流

1. 读取单个 issue，确认 `What to build`、`Type`、`Acceptance criteria` 和 `Blocked by`。
2. 读取关联 PRD 和参考材料，只加载完成当前 issue 所需内容。
3. 探索代码库，找到公共接口、现有测试模式和模块边界。
4. 制定简短实现计划，列出要验证的行为。
5. 写一个失败的行为测试。
6. 写最小实现让该测试通过。
7. 运行相关测试。
8. 重复 red-green，直到验收标准覆盖完成。
9. 所有测试通过后再重构。
10. 汇总变更、测试和残余风险。
11. 不要勾选验收项；验收项的勾选应由 `team-issue-verify` 完成。

## TDD 循环

```text
RED: 写一个行为测试，确认一个验收点失败
GREEN: 写最小实现，让这个测试通过
REFACTOR: 所有相关测试通过后，再整理结构
```

正确切片方式：

```text
行为 1: test -> implementation -> green
行为 2: test -> implementation -> green
行为 3: test -> implementation -> green
```

错误切片方式：

```text
先写所有测试 -> 再写所有实现
```

## 测试标准

- 测试应该描述用户可观察行为。
- 测试应尽量走真实代码路径。
- Mock 只用于外部系统、时间、随机性、网络或昂贵依赖。
- 不为了覆盖率测试无意义分支。
- 测试失败时，应能说明哪个验收行为没有满足。

## 完成标准

完成时输出：

- 实现了哪个 issue。
- 修改了哪些主要文件。
- 覆盖了哪些验收标准。
- 运行了哪些测试和命令。
- 是否还有未解决风险、跳过测试或需要人工确认的事项。

如果不能完成，不要伪装成功。说明阻塞原因、已完成部分和下一步建议。
