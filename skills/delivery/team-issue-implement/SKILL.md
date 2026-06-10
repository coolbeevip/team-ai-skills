---
name: team-issue-implement
description: 根据 team-spec/active/{slug}/issues/ 中的单个工程 issue 进行实现，优先采用行为测试和 TDD 的 red-green-refactor 循环，最终输出代码变更、测试变更和验证结果。Implement a single engineering issue from team-spec/active/{slug}/issues/ using behavior-focused tests and a red-green-refactor loop, producing code changes, tests, and verification results.
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

如果用户要连续处理多个可执行 `AFK` issue，应使用 `team-issue-batch-implement` 做批量编排。本技能仍只负责一个 issue 的实现与验证衔接。

## 运行时配置

在读取 issue、PRD、代码或测试前，先读取目标项目根目录的 `team-spec/config.yml`。如果存在 `access_policy`，必须先应用目录访问边界，再进入任何写入流程。

```yaml
language: zh-CN
version_control:
  system: git
  trunk_branch: main
  contribution_model: fork-pull
  source_remote: origin
  target_remote: upstream
access_policy:
  mode: default-readonly
  directory_file: team-spec/access_policy/default.md
  user_file_template: team-spec/access_policy/{user_name}.md
```

- `language`：issue 回复、实现说明和回写笔记的统一语言。
- `version_control`：仅在需要衔接 PR/MR 或发布时使用。
- `access_policy`：目录访问策略索引。缺失时默认只读；如果本次任务必须写入目标项目而配置又缺失，先询问是否创建最小配置。

## 输入物

主输入必须是一个明确的 issue：

- `team-spec/active/{slug}/issues/{issue-number}-{short-issue-slug}.md`
- 或外部 issue tracker 中的单个 issue。

参考输入可以包括：

- `team-spec/active/{slug}/prd/prd.md` 中的关联 PRD。
- `team-spec/CONTEXT.md` 中的全局规范术语、角色和通用业务规则。
- `team-spec/decisions/` 中的跨需求产品决策。
- `team-spec/active/{slug}/spec/CONTEXT.md` 中的规范术语和业务规则。
- `team-spec/active/{slug}/spec/decisions/` 中的产品决策。
- `team-spec/active/{slug}/spec/reviews.md` 中的风险评审。
- 当前代码库、测试、ADR、接口文档和现有实现。

如果 issue 没有验收标准、依赖未完成、或仍有 HITL 决策点，不要直接实现。先说明阻塞项，并要求回到 `team-prd-to-issues` 或人工决策。

必须先确定要实现的单个 issue，即明确的 `team-spec/active/{slug}/issues/{issue-number}-{short-issue-slug}.md` 或外部 issue 链接/编号。若无法从用户请求、当前分支、当前对话或文件路径中唯一判断，应停止并要求用户提供 issue 路径、issue 编号或链接，不要猜测要实现哪个 issue。

如果用户提供的是 slug、issue 目录或“批量/全部/下一批”这类多个 issue 诉求，不要在本技能里自行循环处理，应转入 `team-issue-batch-implement`。

## 输出物

- 代码变更。
- 测试变更。
- 验证结果，包括运行了哪些测试、是否通过。
- 默认保持变更停留在本地工作区，不要执行 `git commit`、`git push` 或任何会提前固化历史的操作；实现步骤完成后应立即自动执行 `team-issue-verify` 做确认和收尾。
- 优先回写原 issue 文件中的 `## Status`、`## Implementation Notes`、`## Acceptance Criteria Coverage` 或同类章节。
- 如果原 issue 文件不可修改，再写入 `team-spec/active/{slug}/issues/{issue-number}-{short-issue-slug}.implementation.md`，目录只在需要时创建。

不要修改 PRD、规格评审或产品决策，除非用户明确要求。发现需求问题时，应反馈给上游技能，而不是在实现中隐式改需求。

## 核心原则

- 测行为，不测实现细节。
- 通过公共接口验证，不直接测试私有方法或内部数据结构。
- 一次只实现一个 vertical slice。
- 不要一次性写完所有测试再实现。
- 不要在 RED 状态重构。
- 不要提前实现 speculative feature。
- 保持测试名称和领域术语一致，优先使用 `team-spec/CONTEXT.md` 与 `team-spec/active/{slug}/spec/CONTEXT.md` 中的规范语言。

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
12. 不要执行 `git commit`、`git push`、创建 PR/MR 或其他提交收尾动作；保持工作区可供 `team-issue-verify` 继续检查。
13. 完成本技能后应在同一会话自动衔接执行 `team-issue-verify`，无需等待用户再次下达验证指令。

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
- 如果已经完成实现和测试，也不要用提交来表示“完成”；把状态、说明和残余风险留给后续验证步骤。

## 完成标准

完成时输出：

- 实现了哪个 issue。
- 修改了哪些主要文件。
- 覆盖了哪些验收标准。
- 运行了哪些测试和命令。
- 是否还有未解决风险、跳过测试或需要人工确认的事项。
- 明确说明没有执行任何 `git commit` / `git push`，并保留了哪些待验证的本地变更。
- 明确说明已自动衔接到 `team-issue-verify`（或说明无法衔接的阻塞原因）。

如果不能完成，不要伪装成功。说明阻塞原因、已完成部分，并用有序号的“下一步可选”列表给出补救动作。
