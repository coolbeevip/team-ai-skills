---
name: team-tech-debt-refine
description: 通过用户确认细化技术债和已明确对象的阶段性重构，明确证据、行为边界、风险及验收口径。Refine technical debt and scoped refactoring requests through confirmation of evidence, behavior boundaries, risks, and acceptance criteria.
license: PolyForm-Noncommercial-1.0.0
metadata:
  author: coolbeevip
  version: "0.9.1"
triggers:
  - 技术债细化
  - 梳理技术债
  - 技术债需求说不清楚
  - 帮我想清楚这个技术债
  - 技术债验收怎么定
  - 细化模块重构范围
  - 制定阶段性重构规格
  - refine tech debt
  - clarify tech debt
  - tech debt is unclear
  - define tech debt acceptance
  - refine module refactoring scope
  - specify an incremental refactor
---

# 技术债细化

这个技能用于把模糊的技术债诉求打磨成可评审、可拆解、可验收的技术债规格。

## 触发边界

- 适合触发：用户已经指出技术债方向，但证据、影响范围、风险等级或验收口径还不清楚。
- 不适合触发：用户只是想先发现项目债务时，转交 `team-tech-debt-analyze`；技术债规格已清楚并要判断 ready 时，转交 `team-tech-debt-review`。

用户已明确重构对象和目标时可直接进入本技能，无需先生成分析报告；只补查影响决策的证据。当前 Task 内为既定验收所需的局部整理仍由实现技能处理；超出范围的阶段性重构使用独立技术债 slug，不覆盖正在开发的产品规格。

## 运行时配置

开始前读取目标项目根目录的 `team-spec/config.yml`。文件不存在或缺少本技能写入所需字段时，先使用 `team-config-init` 创建或增量补全；本技能不得自行创建或回写配置。只读澄清可按用户本轮语言继续，但写入技术债规格前必须完成所需配置。

语言优先级：用户本轮明确指定 > 配置中的 `language`。

执行要求：

- 对话回复与技术债细化文档 `team-spec/active/{slug}/spec/refine.md` 均使用 `language`。
- 用户临时切换语言时，本次立即生效，并询问是否回写配置。
- 在读取问题证据、代码、日志或写入技术债细化文档前，先读取 `team-spec/config.yml`；如果存在 `access_policy`，先确认当前协作者对相关目录的读写边界。

## 公共写作风格

生成或改写文档、用户可见说明或代码注释前，如果目标项目存在 `team-spec/config.yml`，检查其中的 `writing_style.guide`。该路径指向存在的文件时，写作前必须读取并应用；相对路径以目标项目根目录解析。

优先满足格式、状态、安全、证据和验收合同，再按“用户本轮要求 > 本技能的产物类型规则 > 项目风格指南 > 目标文件相邻内容”处理表达。指南缺失时继续使用本技能规则，不阻塞任务、不猜测路径；需要建立或调整统一风格时使用 `team-writing-style`。

## 输入物

- 当前对话中的技术债诉求、背景、约束和目标。
- 用户已选定的分析候选及其来源报告（如有）；继承已有证据与确认结论，只澄清缺口，不重复全库扫描或逐项重复确认。
- 相关代码、日志、告警、事故复盘、性能数据、缺陷记录或运维反馈。
- 现有 `team-spec/CONTEXT.md` 与 `team-spec/decisions/`（如存在）。
- 现有 `team-spec/active/{slug}/spec/CONTEXT.md` 与 `team-spec/active/{slug}/spec/decisions/`（如存在）。
- 如果存在 `team-spec/active/{slug}/spec/reviews.md` 且状态为 `needs-refinement`，优先读取并围绕问题继续细化。

必须先确定唯一 slug。技术债链路的 slug 必须包含 `debt`，格式建议为 `{yyyy-mm-dd}-debt-{short-english-slug}`。如果无法唯一判断 slug，必须向用户确认，不得猜测。

开始新技术债需求前，必须确定本次要使用的 slug，并检查 `team-spec/active/{slug}/` 是否已存在。`team-spec/active/` 下允许同时存在多个技术债或产品需求 slug，不得因为其他 slug 未归档而要求用户先归档。无法唯一判断目标 slug 时，必须向用户确认。

全局 `team-spec/CONTEXT.md` 在本技能中只读，不创建或更新；文件缺失不阻塞细化。可能跨需求复用的术语、角色或通用规则，连同适用范围和确认状态记录在当前 `spec/refine.md`，归档后由 `team-archive-distill` 评估并沉淀。与既有全局上下文冲突时，在当前需求内列出冲突，不覆盖全局内容。局部 `spec/CONTEXT.md` 只记录当前需求内已确认且需要复用的语境，未确认内容留在 `spec/refine.md`。

## 输出物

- 对话中的澄清结论：问题定义、影响范围、优先级、验收口径、开放问题。
- `team-spec/active/{slug}/spec/refine.md`：技术债细化主文档。
- `team-spec/decisions/{number}-{decision-slug}.md`：当出现跨多个需求长期有效且高成本回退的决策时创建。
- `team-spec/active/{slug}/spec/CONTEXT.md`：当需要沉淀当前技术债局部语境时更新。
- `team-spec/active/{slug}/spec/decisions/{number}-{decision-slug}.md`：当出现只影响当前技术债的决策时创建。
- `team-spec/active/{slug}/STATUS.md`：可选，记录工作区生命周期状态 `debt-refining`；不得写入阶段评审结果。

下游技能读取这些输出物：`team-tech-debt-review` 用于风险评审，`team-tech-debt-to-tasks` 用于工程拆解。

## 细化重点

- 证据：明确技术债由哪些事实触发（告警、故障、性能、复杂度、维护成本、交付风险）。
- 影响：明确影响的用户路径、系统模块、团队协作和发布稳定性。
- 边界：明确本轮处理范围与暂不处理范围。
- 验收：定义可观察、可验证的完成标准，不用“代码更好”这类不可验证表述。
- 约束：明确兼容性、迁移、发布窗口、回滚、合规或安全边界。

## 重构规格补充

涉及重构时，将以下内容纳入同一 `spec/refine.md`，不新增重构专用产物或状态：

- 问题与收益：当前维护痛点、影响及非目标、降低理解/修改/测试/运行维护成本的验收证据。删除行数、模块数或测试数量不能作为成功标准。
- 行为边界：列明保持不变的业务规则、公共接口和可观察副作用，以及单独批准的行为变化及依据。历史测试和当前实现都不能代替契约；发现旧缺陷或意图冲突时单独澄清，不固化错误行为，也不擅自修改预期。
- 基线：记录代码版本、关键正常/边界/历史故障场景，按风险补充必要的性能与运行指标；明确可比输入、环境、依赖、已有结果和缺口。未执行项标为待验证；需要补齐的测试或测量交给后续前置 Task，不把计划写成通过证据。
- 结构边界：模块职责、接口、数据归属、上下游依赖和副作用；新增抽象应对应已经出现的同义重复或变化需求，说明收益与代价，避免为假想未来建框架。
- 风险与恢复：按改动风险覆盖权限、输入校验、事务、并发、幂等、错误处理、资源释放及可观测性。涉及接口、配置、数据格式或数据库时明确兼容范围、迁移顺序、失败处理和临时兼容层移除条件；代码回滚不等于数据恢复，不可逆变化需明确备份恢复或向前修复的验证安排。
- 开发衔接：记录关联 Task 和现有未提交变化，选择可分离的实施边界；本技能不替用户提交、stash、丢弃改动或切换分支。不以重构名义改变已确认验收、批次范围或授权。

已确认的重构约束由本规格作为来源，评审检查其可执行性，Task 引用并细化验证步骤；实际执行结果写回对应 Task，避免多处维护同一事实。

## 完成标准

- 形成可供评审的 `team-spec/active/{slug}/spec/refine.md`。
- 明确风险最高的未决问题和下一步评审建议。
- 下一步可选：必须使用有序号的列表选项输出，方便用户直接回复序号继续推进。

推荐格式：

```md
## 下一步可选

1. `team-tech-debt-review`：评审技术债规格的风险、优先级和可执行性。
```

## 最终回复

必须包含：

- 技术债规格路径和 slug。
- 已确认的证据、影响范围、优先级和验收口径。
- 仍保留的开放问题、约束和阻塞项。
- 工作区生命周期状态；写入时应为 `debt-refining`。
- 有序号的“下一步可选”列表，优先推荐 `team-tech-debt-review`。
