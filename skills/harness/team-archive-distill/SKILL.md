---
name: team-archive-distill
description: 从已归档的 team-spec 中提取决策模式和工程惯例，高度抽象为规则后写入 AGENTS.md。Extract decision patterns and engineering conventions from archived team-specs, abstract them into high-level rules, and write them into AGENTS.md.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 从归档提取规则
  - 归档决策抽象
  - 更新 AGENTS.md 规则
  - 从历史需求提炼规则
  - 过去决策总结
  - 复盘历史 spec
  - extract rules from archive
  - abstract archived decisions
  - distill rules from past specs
  - update AGENTS.md from history
  - summarize past decisions
  - review archived specs
---

# 归档决策规则提取

这个技能用于从 `team-spec/archive/` 下已归档的 spec 中提取决策模式和工程惯例，高度抽象为可复用的规则后写入 `AGENTS.md`。它不是项目文档生成器，也不是架构说明书，而是从历史决策中提炼出能让 Codex 在新任务中做出正确判断的约束和模式。

本技能独立使用，不依赖产品需求链路（prd-to-tasks、task-implement 等），也不属于主线交付流程。

## 触发边界

- 适合触发：用户要从已归档的 spec 中提炼规则、更新 AGENTS.md 中的决策约束、复盘历史需求并沉淀惯例。
- 不适合触发：用户要维护代码级 harness（入口约束、失败记忆、验证策略、任务入口）时，这不属于本技能范围；用户要细化新需求、评审规格、生成 PRD 或拆 Task 时，转交对应产品/交付技能。

## 职责边界

本技能只做一件事：从 `team-spec/archive/` 中提取可复用的规则，写入 `AGENTS.md`。

适合提取的规则类型：

1. 架构规则：模块边界、技术选型约束、分层原则、依赖方向。
2. API/接口规则：命名惯例、版本策略、错误处理模式、向后兼容约束。
3. 数据规则：数据模型惯例、存储选择、迁移策略、schema 变更约束。
4. 测试规则：测试分层、覆盖率要求、验证策略、哪些变更必须跑哪些测试。
5. 流程规则：分支策略、代码评审要求、发布流程、部署约束。
6. 约束规则：已知不可触碰的边界、技术债务禁区、性能/安全红线。

本技能不负责：

- 维护 Codex 运行时检索层（入口约束、失败记忆、验证 harness、任务入口）。
- 写 PRD、拆 Task、实现 Task、验证 Task，或创建 Spec 级远端 Issue/PR/MR。
- 生成完整架构说明书或项目文档。
- 凭空编造规则；所有规则必须有归档 spec 中的证据支撑。
- 修改 `team-spec/archive/` 中的任何文件。

## 输入物

- 用户明确指定的一个或多个归档 slug，或 `team-spec/archive/{slug}/` 下的具体文件路径。只读取被指定的归档范围，不默认枚举或扫描整个 `team-spec/archive/`。
- 被指定归档 slug 的以下产物（如存在）：
  - `spec/refine.md`：细化过程中确认的需求和决策。
  - `spec/reviews.md`：评审中发现的风险、约束和修正。
  - `prd/prd.md`：固化的功能边界、验收标准和工程约束。
  - `design/functional-design.md`：架构设计决策和模块划分。
  - `DELIVERY.md`：交付过程中的经验教训和实际遇到的问题。
  - `ARCHIVE.md`：归档原因和生命周期总结。
- 目标项目根目录已有的 `AGENTS.md`。

如果用户没有明确指定归档 slug 或文件路径，停止并要求用户提供，不得通过扫描 archive 猜测范围。如果指定范围不存在或为空，停止并说明没有可提取内容。

## 输出物

- 更新后的 `AGENTS.md`：在现有内容基础上新增或更新 `## 从历史决策中提炼的规则` 章节，包含按类型分组的抽象规则。

不新增其他文件，不修改 `team-spec/archive/` 中的任何内容。

## 规则写法

每条规则必须是高度抽象的、可复用的判断依据，而不是原始决策的复述。规则格式：

```markdown
### {rule-title}

- 规则：{用一句话描述，Codex 在什么情况下应该遵守什么}
- 原因：{为什么这条规则是必要的，过去什么决策/问题导致了它}
- 例外：{什么情况下可以不遵守，如果没有则写 无}
- 来源：{引用归档 slug，可多个，如 `2025-03-15-user-auth`, `2025-06-01-api-gateway`}
- 最后更新：{YYYY-MM-DD}
```

规则必须满足：

- 抽象：不是“在 xxx spec 中我们决定用 PostgreSQL”，而是“新服务的默认数据库选型为 PostgreSQL，除非有明确的非关系型需求”。
- 可操作：Codex 读到后能直接用于决策。
- 有证据：每条规则至少引用一个归档 slug。
- 不重复：同一事实只写在一个规则里。

## 规则分类

规则按以下类别组织，写入 `AGENTS.md` 的 `## 从历史决策中提炼的规则` 章节下：

1. `### 架构规则`：模块边界、技术选型、分层原则、依赖方向。
2. `### API/接口规则`：命名惯例、版本策略、错误处理、向后兼容。
3. `### 数据规则`：数据模型、存储选择、migration 策略。
4. `### 测试规则`：测试分层、覆盖率要求、验证策略。
5. `### 流程规则`：分支策略、评审要求、发布流程。
6. `### 约束规则`：不可触碰的边界、技术债务禁区、性能/安全红线。

如果某类规则暂无证据支撑，不创建空分类。

## 工作流

1. 确认用户明确指定的归档 slug 或文件路径，并拒绝自动扩大到其他归档。
2. 逐一读取指定 slug 的关键文件（`refine.md`、`reviews.md`、`prd.md`、`functional-design.md`、`DELIVERY.md`、`ARCHIVE.md`）。
3. 从每个文件中识别决策、约束、惯例、经验教训和模式。
4. 将相似决策归并，抽象为高层规则，消除重复。
5. 按 6 个分类组织规则，为每条规则标注来源 slug。
6. 读取已有 `AGENTS.md`，在 `## 从历史决策中提炼的规则` 章节下写入或更新规则。
7. 如果某个来源 slug 中找不到可提取的规则，跳过该 slug，不强行编造。
8. 自检：每条规则是否抽象、可操作、有证据、不重复。

## 汇总粒度

- 单条规则可以来自多个归档 slug 的共同模式。
- 同一归档 slug 可以贡献多条不同类型的规则。
- 如果某个归档 slug 的决策与现有规则冲突，标注为待确认，不自动覆盖。
- 如果某个归档 slug 的决策已被后续归档推翻，以最新归档为准，旧规则降级为历史记录或删除。

## 运行时配置

本技能读取目标项目根目录下的 `team-spec/config.yml` 作为运行时配置入口，主要用于获取 `writing_style.guide` 路径。

如果 `team-spec/config.yml` 不存在或缺少本轮需要的字段，先使用 `team-config-init` 创建或增量补全。本技能不得自行创建或回写配置；纯对话和只读分析可以继续，但写入 `AGENTS.md` 前必须完成所需配置。

如果配置存在 `access_policy`，读取指定 archive 内容和写入 `AGENTS.md` 前都必须先应用对应目录边界。访问策略不能被“只读提炼”或用户笼统要求扫描历史记录所绕过。

语言优先级为：用户本轮明确指定 > 配置中的 `language` > 目标 `AGENTS.md` 的既有主要语言。

## 公共写作风格

生成或改写 `AGENTS.md` 前，检查 `team-spec/config.yml` 中的 `writing_style.guide`。该路径指向存在的文件时，写作前必须读取并应用；相对路径以目标项目根目录解析。

优先满足格式、状态、安全、证据和验收合同，再按“用户本轮要求 > 本技能的产物类型规则 > 项目风格指南 > 目标文件相邻内容”处理表达。指南缺失时继续使用本技能规则，不阻塞任务、不猜测路径；需要建立或调整统一风格时使用 `team-writing-style`。

## 自检要求

每次更新 `AGENTS.md` 后，必须轻量自检：

- 每条规则是否属于 6 个分类之一。
- 每条规则是否抽象（不是原始决策复述）、可操作（Codex 能用于决策）、有证据（至少引用一个归档 slug）。
- 是否存在重复规则，或同一事实分散在多个规则中。
- 是否引用了不存在的归档 slug。
- 是否修改了 `team-spec/archive/` 中的任何文件。
- 是否需要降级、删除或标注被后续归档推翻的旧规则。

## 与其他技能的关系

- `team-spec-archive`：将 active 需求归档到 archive。本技能读取其产物。
- `team-writing-style`：建立或调整统一写作风格。本技能在生成 `AGENTS.md` 规则时应用其风格指南。
- 本技能独立于产品交付链路（refine、prd-to-tasks、task-implement 等），不依赖它们的输出，也不为它们提供输入。

## 完成标准

- `AGENTS.md` 中 `## 从历史决策中提炼的规则` 章节已更新。
- 每条规则抽象、可操作、有证据、不重复。
- 没有编造规则（每条规则都可追溯到至少一个归档 slug）。
- 没有修改 `team-spec/archive/` 中的任何文件。
- 规则分类清晰，没有空分类。

## 最终回复

必须包含：

- 扫描的归档 slug 数量和列表。
- 每个 slug 中提取到的决策/模式数量。
- 归并后生成的规则总数和各分类下的规则数。
- 每条规则的摘要和来源 slug。
- 未提取到规则的 slug 及原因。
- 待确认的冲突规则（如有）。
