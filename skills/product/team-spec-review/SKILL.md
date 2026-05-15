---
name: team-spec-review
description: 评审已细化的需求规格，检查产品、交付、数据、合规、运营和协作风险，并输出分级风险、阻塞项、补救动作和是否 ready 的结论。Review refined specs for product, delivery, data, compliance, operational, and collaboration risks, then produce readiness findings, blockers, mitigations, owners, and deadlines.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 评审规格
  - 规格准备好了吗
  - 检查需求风险
  - 这个需求有没有风险
  - 规格 ready 了吗
  - review spec
  - spec ready check
  - check requirement risks
  - is the spec ready
---

# 规格评审

这个技能用于找出会导致需求方向错误、返工、延期、线上事故、合规问题或协作失效的风险。不要只输出泛泛的风险列表；每个重要风险都必须落到处理动作、负责人和截止点。

## 触发时机

- `team-spec-refine` 阶段中：反复评审规格是否还有会阻塞 PRD 的明显缺口。
- `team-spec-to-prd` 开始前：作为 ready gate，先识别 P0/P1 风险，再决定是否可以固化 PRD。
- PRD 完成后：做完整评审，检查 PRD 是否足够支持研发、测试、运营和上线。
- 开发前或上线前：复查未关闭风险，确认是否仍然可接受。

不要在 `team-spec-refine` 的每一轮问答后自动执行完整评审。那会打断细化节奏，并且在信息尚不稳定时制造噪音。

## 输入物

优先读取：

- 当前对话中的需求、澄清结论或 PRD。
- `team-spec-refine` 的澄清结论。
- `team-spec/spec/refine/{slug}.md`，这是本技能的主输入。
- `team-spec-to-prd` 生成的 PRD，如果已经存在。
- `team-spec/spec/CONTEXT.md`。
- `team-spec/spec/decisions/`。
- 相关 PRD、任务、设计稿、接口说明、测试计划或上线计划。
- 当前仓库中能证明现状的代码或文档。

如果输入不足，不要编造风险。先说明缺少什么材料，并只基于已有证据输出可判断的风险。

必须先确定本次评审对应的 `{slug}` 或明确的 `team-spec/spec/refine/{slug}.md`。如果无法从用户请求、当前对话或文件路径中唯一判断，应停止并要求用户提供 slug 或 refine 文件路径，不要猜测要评审哪个规格。

## 输出物

- 对话中的规格评审报告：ready 结论、阻塞项、风险清单、需要补充的问题和建议改写。
- `team-spec/spec/reviews/{slug}.md`：与 refinement 使用同一个 slug 的规格评审报告。
- 可被 `team-spec-to-prd` 读取的 PRD 前置检查结果。
- 可被 `team-prd-to-issues` 参考的工程拆解风险提示，例如 blocker、HITL 决策点和验收风险。

如果项目需要沉淀评审报告，默认保存到 `team-spec/spec/reviews/{slug}.md`，目录只在需要时创建。

本技能可以与 `team-spec-refine` 反复迭代。发现 P0 或关键 P1 时，默认建议回到 `team-spec-refine` 修正规格；只有风险已解决或被明确接受后，才建议进入 `team-spec-to-prd`。

本技能不要直接修改 `team-spec/spec/refine/{slug}.md`。如果规格需要修订，输出 `Status: needs refinement`，并在 `Questions For User` 与 `Required Refinement` 中给出明确问题和修改方向，由 `team-spec-refine` 继续与用户确认并更新同一个 refine 文件。

## 分析维度

- 需求歧义：术语、目标、范围、验收是否清楚。
- 用户与场景：目标用户、操作角色、审核者、运营者、失败场景是否覆盖。
- 范围与非目标：必须交付、明确不做、延期事项是否可区分。
- 业务规则：审批、计费、状态流转、限制、优先级、异常处理是否完整。
- 权限与合规：可见性、操作权限、审计、隐私、数据保留、法律约束是否明确。
- 数据与状态：对象定义、字段、状态机、生命周期、迁移、删除和恢复是否清楚。
- 技术依赖：外部系统、接口契约、性能、稳定性、兼容性、历史数据是否有风险。
- 发布与运营：灰度、开关、监控、告警、客服、人工兜底、回滚是否可执行。
- 测试与验收：是否能用自动化或手工方式验证外部行为。
- 跨团队协作：owner、依赖团队、决策人、截止点是否明确。

## 风险分级

- `P0`：必须在进入开发或发布前解决。否则可能导致方向错误、线上事故、合规问题、大规模返工或无法验收。
- `P1`：建议在进入开发前解决。否则大概率导致延期、关键路径返工或核心体验失败。
- `P2`：可以进入开发，但必须明确跟踪。否则会增加局部复杂度、维护成本或体验瑕疵。
- `P3`：记录即可，不阻塞当前阶段。

如果无法判断等级，标为 `Unclear`，并说明缺少的证据。

## 输出格式

### 结论

用三句话以内说明：

- 是否 ready 进入 PRD 固化。
- 是否存在阻塞项。
- 最大风险来自哪个维度。

`Status` 只能使用：

- `ready`
- `needs refinement`
- `blocked`

### 阻塞项

只列 `P0` 和必须立即处理的 `P1`。

| 等级 | 阻塞项 | 为什么阻塞 | 建议动作 | Owner | 截止点 |
|---|---|---|---|---|---|

### 风险清单

| 等级 | 风险 | 触发条件 | 影响 | 证据/缺口 | 建议动作 | Owner | 截止点 |
|---|---|---|---|---|---|---|---|

### 需要补充的问题

只列真正影响判断的问题。不要列开放式访谈问题。

### Questions For User

当 `Status: needs refinement` 时必须填写。只列需要回到 `team-spec-refine` 继续确认的问题。

### Required Refinement

当 `Status: needs refinement` 时必须填写。说明需要更新 `team-spec/spec/refine/{slug}.md` 的哪些章节或规则。

### 建议改写

如果发现 PRD 或需求表述不清，直接给出更清晰的改写版本。改写应尽量可验证、可分工、可验收。

## 完成输出

每次完成评审后，最终回复必须包含：

- 评审报告路径：`team-spec/spec/reviews/{slug}.md`，如果本次已保存。
- `Status`：`ready`、`needs refinement` 或 `blocked`。
- 下一步推荐：
  - 当 `Status: ready` 时，明确推荐使用 `team-spec-to-prd` 固化 PRD。
  - 当 `Status: needs refinement` 时，明确推荐回到 `team-spec-refine`，并说明需要修订哪些关键内容。
  - 当 `Status: blocked` 时，明确说明阻塞项和解除阻塞后再使用哪个技能。

推荐结尾：

```text
规格评审已完成，Status: ready。
下一步请使用 team-spec-to-prd，将通过评审的规格固化为 PRD。
```

## 处理原则

- 优先报告会造成重大返工或上线事故的风险，不要平均用力。
- 不要把“不确定”伪装成“风险已确认”。明确写出证据缺口。
- 不要只说“需要明确”。必须说明要明确什么、谁来明确、何时必须明确。
- 不要输出无法行动的建议。每条 P0/P1 风险必须有建议动作、Owner 和截止点。
- 如果风险来自术语混乱，建议回到 `team-spec-refine` 继续细化。
- 如果风险可通过 PRD 明确表达解决，建议在 `team-spec-to-prd` 中直接补入对应章节。
