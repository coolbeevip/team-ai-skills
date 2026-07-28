---
name: team-issue-implement
description: 实现单个工程 issue，优先使用行为测试、TDD、现有代码复用和最小实现模式。Implement one engineering issue with behavior-focused tests, TDD, existing-code reuse, and lean implementation.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 实现 issue
  - 开始写代码
  - 按 issue 编码
  - 实现这个功能
  - 最小改动实现
  - 不要过度设计
  - 简单实现
  - 优先复用现有代码
  - 少写代码
  - implement issue
  - start coding
  - implement this feature
  - code this issue
  - minimal implementation
  - avoid over-engineering
  - reuse existing code first
  - simplest correct change
---

# Issue 实现

这个技能用于把 `team-prd-to-issues` 产生的单个 issue 实现为可验证的代码变更。TDD 是默认实现策略，但不是形式主义；目标是通过公共接口验证外部行为，而不是测试实现细节。

如果用户要连续处理多个可执行 `AFK` issue，应使用 `team-issue-batch-implement` 做批量编排。本技能仍只负责一个 issue 的实现与验证衔接。

当用户说“最小改动实现”“不要过度设计”“优先复用现有代码”“minimal implementation”“avoid over-engineering”等表达时，启用最小实现模式：先判断是否需要新增实现，再查已有 helper、组件、服务、脚本和测试模式，再优先使用标准库、平台能力和已安装依赖，最后才写局部、直接、可验证的新代码。

## 触发边界

- 适合触发：用户给出单个明确 issue，要求实现代码变更、测试变更和验证结果。
- 不适合触发：用户要连续处理多个 issue 时，转交 `team-issue-batch-implement`；用户只要求验收或审查现有实现时，转交 `team-issue-verify`。

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

## 公共写作风格

生成或改写文档、用户可见说明或代码注释前，如果目标项目存在 `team-spec/config.yml`，检查其中的 `writing_style.guide`。该路径指向存在的文件时，写作前必须读取并应用；相对路径以目标项目根目录解析。

优先满足格式、状态、安全、证据和验收合同，再按“用户本轮要求 > 本技能的产物类型规则 > 项目风格指南 > 目标文件相邻内容”处理表达。指南缺失时继续使用本技能规则，不阻塞任务、不猜测路径；需要建立或调整统一风格时使用 `team-writing-style`。

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
- `./references/PLATFORM-STDLIB.md` 中的平台、标准库、数据库、Shell/OS 和项目内已有能力替代清单。

如果 issue 没有验收标准、依赖未完成、或仍有 HITL 决策点，不要直接实现。先说明阻塞项，并要求回到 `team-prd-to-issues` 或人工决策。

必须先确定要实现的单个 issue，即明确的 `team-spec/active/{slug}/issues/{issue-number}-{short-issue-slug}.md` 或外部 issue 链接/编号。若无法从用户请求、当前分支、当前对话或文件路径中唯一判断，应停止并要求用户提供 issue 路径、issue 编号或链接，不要猜测要实现哪个 issue。

如果用户提供的是 slug、issue 目录或“批量/全部/下一批”这类多个 issue 诉求，不要在本技能里自行循环处理，应转入 `team-issue-batch-implement`。

## 输出物

- 代码变更。
- 测试变更。
- 验证结果，包括运行了哪些测试、是否通过。
- 本地 issue 草稿中的生命周期状态：开始实现后更新为 `implementing`。
- 默认保持变更停留在本地工作区，不要执行 `git commit`、`git push` 或任何会提前固化历史的操作；实现步骤完成后应立即自动执行 `team-issue-verify` 做确认和收尾。
- 优先回写原 issue 文件中的 `## Status`、`## Implementation Notes`、`## Acceptance Criteria Coverage` 或同类章节。
- 如果原 issue 文件不可修改，再写入 `team-spec/active/{slug}/issues/{issue-number}-{short-issue-slug}.implementation.md`，目录只在需要时创建。

不要修改 PRD、规格评审或产品决策，除非用户明确要求。发现需求问题时，应反馈给上游技能，而不是在实现中隐式改需求。

## 核心原则

- 测行为，不测实现细节。
- 通过公共接口验证，不直接测试私有方法或内部数据结构。
- 一次只实现一个 vertical slice。
- 默认使用最小实现模式：先复用、先平台、先已有依赖，避免无请求抽象、框架、配置层或通用层。
- 不要一次性写完所有测试再实现。
- 不要在 RED 状态重构。
- 不要提前实现 speculative feature。
- 不为了少写代码牺牲输入校验、权限、安全、数据一致性、错误处理、可访问性或用户明确要求。
- 保持测试名称和领域术语一致，优先使用 `team-spec/CONTEXT.md` 与 `team-spec/active/{slug}/spec/CONTEXT.md` 中的规范语言。

## 最小实现模式

执行 issue 时按以下顺序判断：

1. 这个需求是否已经被现有流程、配置或代码覆盖；如果已覆盖，说明证据并停止新增代码。
2. 当前项目是否已有 helper、组件、服务、脚本、测试模式或调用流可复用。
3. 标准库、语言内建、数据库、浏览器、操作系统或框架原生能力是否足够。
4. 已安装依赖是否足够；不得为了小功能新增依赖，除非验收标准或代码证据证明必要。
5. 是否能用一个局部小改动完成；不得新增无请求抽象、框架、配置层或通用层。
6. 非平凡逻辑必须留下最小行为验证。
7. 安全、权限、数据一致性、错误处理、可访问性和用户明确要求不属于可裁剪范围。

最终实现说明应包含：复用了什么、拒绝了什么复杂方案、什么时候才需要升级为更复杂方案。

当实现涉及 URL query、日期、CSV、分组、深拷贝、格式化、分页、唯一性、文件路径、CLI、临时文件、Shell 调用、数据库约束或 UI 原生控件时，必须读取 `./references/PLATFORM-STDLIB.md`，先列出可用的平台/标准库/数据库/项目内替代方案，再决定是否新增依赖或自定义抽象。

## Issue 最小路径检查清单

实现前必须先写出简短检查结论：

- 真实入口：当前 issue 会经过哪个路由、命令、组件、服务、任务或公共 API。
- 现有实现：同类行为已经在哪些 helper、组件、服务、脚本、测试或调用流里出现。
- 最小路径：本次只需要改哪些文件、函数或配置，为什么它们覆盖验收标准。
- 拒绝方案：明确拒绝哪些新增抽象、依赖、跨模块重构、配置层或未来扩展点，以及拒绝原因。
- 平台替代：是否可用 `./references/PLATFORM-STDLIB.md` 中的平台、标准库、数据库或项目内已有能力。
- 验证方式：改动后运行哪些最小测试或手工检查，如何证明用户可观察行为正确。

只有验收标准、风险评审或代码证据证明必要时，才允许新增抽象、依赖或跨模块重构；否则应把它们列为拒绝方案。

## 最小实现示例

- 小功能避免新增依赖：如果需求只是解析 URL query、格式化日期、分组列表或生成简单 CSV，先使用语言标准库、浏览器 API、数据库能力或项目已有工具；不要为了一个局部需求新增通用工具库。
- 已有 helper 优先复用：如果项目已有权限判断、金额格式化、分页参数解析、错误响应构造或表单校验 helper，应沿用现有 helper 和测试模式；不要创建第二套相似封装。
- 局部改动解决真实路径：如果 bug 根因在共享函数或唯一调用流，修复共享根因并补对应行为测试；不要顺手重构周边模块、改名、抽配置层或引入未来扩展点。

## Issue 级黄金用例

- 小 bug fix：先追到真实调用流和共享根因函数，只修根因并补回归测试；不要顺手重写调用方、改模块边界或清理无关命名。
- 小 UI / 接口需求：先找现有页面、表单、接口 handler、响应格式、错误处理和测试模式；新增字段、按钮或参数应贴合既有模式，不创建新的状态管理、组件体系或响应封装。
- 验收标准要求完整方案：如果 issue 明确要求权限、审计、迁移、兼容、批处理、可访问性或跨端一致性，不要强行极简；最小实现是满足完整验收标准的最小方案，不是删减需求。

## 安全边界反例

- 错误：为了少写代码删除输入校验、权限检查、CSRF/鉴权逻辑或敏感字段过滤。正确做法：保留安全边界，只在边界内寻找更小实现。
- 错误：为了小 diff 跳过事务、幂等、迁移兼容、数据一致性检查或回滚路径。正确做法：如果验收标准涉及数据状态，最小实现也必须覆盖一致性和失败路径。
- 错误：为了简单删掉错误处理、可访问性标签、国际化文案、硬件校准或用户明确要求的兼容行为。正确做法：这些属于产品和安全约束，不作为可删除复杂度。

## 工作流

1. 读取单个 issue，确认 `What to build`、`Type`、`Acceptance criteria` 和 `Blocked by`；如果是可写的本地 issue 草稿，将 `## Status` 更新为 `implementing`。
2. 读取关联 PRD 和参考材料，只加载完成当前 issue 所需内容。
3. 探索代码库，找到真实入口、公共接口、现有测试模式、同类实现和模块边界。
4. 制定简短实现计划，列出 issue 最小路径检查清单、可复用的现有代码、被拒绝的复杂方案和要验证的行为。
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
- Issue 最小路径检查清单：真实入口、现有实现、最小路径、拒绝方案、平台替代和验证方式。
- 复用了什么现有代码、平台能力或已安装依赖，以及跳过了什么复杂方案。
- 如果采用了刻意简化，说明未来什么时候需要升级为更完整方案。
- 运行了哪些测试和命令。
- 是否还有未解决风险、跳过测试或需要人工确认的事项。
- 明确说明没有执行任何 `git commit` / `git push`，并保留了哪些待验证的本地变更。
- 明确说明已自动衔接到 `team-issue-verify`（或说明无法衔接的阻塞原因）。

如果不能完成，不要伪装成功。说明阻塞原因、已完成部分，并用有序号的“下一步可选”列表给出补救动作。

## 最终回复

必须包含：

- issue 路径或远端编号，以及当前生命周期状态。
- 主要代码和测试变更、验收标准覆盖情况。
- Issue 最小路径检查、复用内容和被拒绝的复杂方案。
- 实际运行的验证命令、结果、跳过项和残余风险。
- 未执行 `git commit` / `git push` 的说明。
- 自动衔接 `team-issue-verify` 的结果，或无法衔接的阻塞原因。
