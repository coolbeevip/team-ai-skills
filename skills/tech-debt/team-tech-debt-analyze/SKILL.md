---
name: team-tech-debt-analyze
description: 对项目或指定模块进行只读技术债分析，识别维护性、稳定性、测试、架构和交付风险，输出证据化技术债分析报告。Analyze technical debt in a project or module through read-only codebase inspection, identifying maintainability, reliability, testing, architecture, and delivery risks with evidence.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 分析技术债
  - 代码健康检查
  - 找维护风险
  - 看看项目有哪些技术债
  - technical debt analysis
  - code health review
  - maintainability audit
  - find technical debt
---

# 技术债分析

这个技能用于对项目、模块或服务进行只读技术债分析，找出有源码证据支撑的技术债候选项，并按影响、风险和治理优先级形成分析报告。

本技能是技术债治理链路的前置入口。它不直接要求用户先提出明确技术债，而是从代码、测试、配置、构建、运行文档和变更历史中发现值得治理的问题。后续可把某个候选项交给 `team-tech-debt-refine` 继续细化。

## 运行时语言配置

统一读取目标项目根目录 `team-spec/config.yml`：

```yaml
language: zh-CN
access_policy:
  mode: default-readonly
  directory_file: team-spec/access_policy/default.md
  user_file_template: team-spec/access_policy/{user_name}.md
```

语言优先级：用户本轮明确指定 > `team-spec/config.yml` > 首次询问并落盘。若配置不存在，不报错，走"询问并创建"流程。

执行要求：

- 对话回复与批次级技术债分析报告 `team-spec/active/{analysis_slug}/tech-debt/analysis.md` 均使用 `language`。
- 用户临时切换语言时，本次立即生效，并询问是否回写配置。
- 在读取代码、测试、配置、日志、运行文档或写入分析报告前，先读取 `team-spec/config.yml`；如果存在 `access_policy`，先确认当前协作者对相关目录的读写边界。

## 输入物

- 当前对话中的分析目标、范围、重点模块、已知痛点、近期事故或维护问题。
- 目标项目中的源码、测试、配置、构建脚本、部署脚本、运行文档、架构说明、错误日志或监控材料。
- `team-spec/CONTEXT.md` 与 `team-spec/decisions/`（如存在）。
- 现有 `team-spec/active/{slug}/spec/`、`prd/`、`issues/` 或 `design/`（仅当用户指定同一 slug 或与分析范围直接相关时读取）。

必须先确定唯一分析批次 slug。技术债分析批次 slug 必须包含 `debt`，格式建议为 `{yyyy-mm-dd}-debt-{scope-slug}`，例如 `2026-06-10-debt-code-health`。如果用户没有提供 slug，可以根据本轮分析范围生成一个建议 slug；若目标项目中同名 slug 已存在，必须确认是继续已有分析还是创建新 slug。

分析批次 slug 只承载本次盘点报告。报告中每个 `Debt Candidate` 必须给出独立的 `Suggested Slug`，用于后续 `team-tech-debt-refine` 创建单个候选债务的闭环工作区，例如 `2026-06-10-debt-test-coverage`。除非用户明确说“就在当前分析 slug 继续细化”，否则不要把多个候选债务都写入分析批次 slug 的 `spec/refine.md`。

## 输出物

- 对话中的技术债摘要：高优先级债务、关键证据、建议下一步。
- `team-spec/active/{analysis_slug}/tech-debt/analysis.md`：批次级技术债分析报告。
- 可选更新 `team-spec/active/{analysis_slug}/STATUS.md`：仅记录 `analyzed`、`needs-refinement` 或 `blocked` 等状态，不记录业务细节。

下游技能读取这些输出物：`team-tech-debt-refine` 默认使用候选项的 `Suggested Slug` 创建独立工作区，并在 `spec/refine.md` 中反向引用来源分析；`team-tech-debt-review` 用于评审已细化债务，`team-tech-debt-to-issues` 用于工程拆解。

推荐链路：

```text
批次级分析：
team-spec/active/{analysis_slug}/tech-debt/analysis.md

单个候选债务闭环：
team-spec/active/{candidate_slug}/spec/refine.md
team-spec/active/{candidate_slug}/spec/reviews.md
team-spec/active/{candidate_slug}/issues/
```

## 分析范围

先确认分析范围，再决定扫描深度：

- 全项目：适合第一次技术债盘点，重点识别最高风险和最值得优先治理的 5 到 10 项。
- 指定模块：适合用户指出目录、服务、包、页面、接口或任务链路时，重点分析局部维护风险。
- 指定维度：适合用户只关心测试、性能、稳定性、架构、依赖、构建、发布或安全合规时，围绕该维度分析。
- 指定事件：适合从事故、线上缺陷、性能退化或交付延迟倒查技术债根因。

如果范围过大且时间不足，优先输出“高置信候选项”和“需要进一步扫描的区域”，不要假装已经完整覆盖。

## 分析维度

按证据选择相关维度，不需要机械覆盖所有维度：

- 可维护性：重复逻辑、超大文件、超长函数、隐式约定、命名混乱、过深分支、过强耦合。
- 架构边界：模块职责混杂、跨层调用、循环依赖、领域模型泄漏、入口分散、扩展点不清晰。
- 测试与验证：关键路径缺测试、测试只覆盖实现细节、缺少回归用例、缺少集成或端到端验证。
- 稳定性与可观测性：错误处理薄弱、重试/超时缺失、日志不可定位、告警缺口、状态恢复不清晰。
- 性能与资源：重复查询、阻塞 IO、无界缓存、批处理退化、内存或连接生命周期不清楚。
- 数据与迁移：schema 演进风险、兼容性不明、迁移不可回滚、数据修复缺审计。
- 依赖与构建：过期高风险依赖、生成物混乱、构建入口不稳定、环境假设隐含。
- 交付风险：发布步骤手工化、回滚路径缺失、配置散落、部署环境差异大。

## 债务判定标准

只有满足以下条件之一，才把问题列为技术债候选：

- 有文件、函数、测试、配置、日志或历史变更作为证据。
- 能解释它如何影响维护成本、缺陷概率、交付速度、稳定性、性能或扩展性。
- 能提出可验证的治理方向，而不是只表达风格偏好。

不要把以下内容直接判为技术债：

- 只有个人审美差异的代码风格。
- 没有影响路径的“看起来不优雅”。
- 与当前业务规模不匹配的过度工程建议。
- 需要产品或架构决策但证据不足的问题；这类应标为开放问题。

## 报告结构

`analysis.md` 使用以下结构：

```md
# 技术债分析：{范围}

## Summary

- Scope: {本次分析范围}
- Status: analyzed / needs-refinement / blocked
- Top Risks: {最高风险摘要}

## Evidence Map

| Area | Evidence | Why It Matters |
| --- | --- | --- |
| {模块/目录} | `{path}` / `{symbol}` / `{command output}` | {影响说明} |

## Debt Candidates

### TD-1 {候选债务标题}

- Priority: P0 / P1 / P2 / P3
- Confidence: High / Medium / Low
- Suggested Slug: {yyyy-mm-dd}-debt-{candidate-slug}
- Source Analysis: team-spec/active/{analysis_slug}/tech-debt/analysis.md#td-1-{候选债务标题}
- Impact: {维护性/稳定性/性能/测试/交付影响}
- Evidence:
  - `{path}`：{具体事实}
- Recommended Direction: {治理方向，不写具体补丁}
- Suggested Next Skill: `team-tech-debt-refine`
- Open Questions: {如无则写 None}

## Non-Debt Findings

- {有证据但不建议作为技术债处理的问题}

## Follow-up Scan Areas

- {尚未覆盖但值得继续看的目录或维度}
```

## 优先级规则

- `P0`：已经造成严重线上事故、数据风险、安全合规风险，或正在阻塞关键交付。
- `P1`：高概率造成稳定性、性能、交付或维护风险，且影响核心路径。
- `P2`：明确增加维护成本或缺陷概率，但影响范围有限。
- `P3`：局部改善项，可等到相关功能迭代时顺手治理。

每个 `P0` 或关键 `P1` 必须给出明确证据、影响路径和下一步细化建议。

## 执行原则

- 只读分析，不修改业务代码、测试、配置、构建脚本、依赖锁文件或迁移文件。
- 可以写入 `team-spec/active/{analysis_slug}/tech-debt/analysis.md`，但不得把真实业务产物写入本技能库。
- 优先使用 `rg`、`find`、语言自带测试清单和项目已有文档进行证据收集。
- 发现无法读取的目录、权限边界或敏感区域时，记录为范围限制，不绕过访问策略。
- 结论必须和证据一一对应；低置信度判断必须标为 `Confidence: Low`，并列出需要补证的方向。
- 对全项目扫描，不追求穷尽所有问题，优先找最影响团队决策的债务。

## 完成标准

- 生成 `team-spec/active/{analysis_slug}/tech-debt/analysis.md`。
- 每个债务候选都有证据、影响、优先级、置信度、`Suggested Slug` 和建议下一步。
- 最终回复必须说明分析报告路径、最高优先级候选项和下一步可选。

## 完成输出

最终回复必须包含：

- 分析报告路径：`team-spec/active/{analysis_slug}/tech-debt/analysis.md`，如果本次已保存。
- Top Candidates：最多列 3 个最高优先级候选项。
- 下一步可选：必须使用有序号的列表选项输出，方便用户直接回复序号继续推进。

推荐结尾：

```text
技术债分析已完成，Status: analyzed。
下一步可选：
1. team-tech-debt-refine：选择 TD-1，使用其 Suggested Slug 创建独立技术债规格。
2. team-tech-debt-analyze：继续扫描 Follow-up Scan Areas 中尚未覆盖的模块。
```
