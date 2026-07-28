---
name: team-spec-to-prd
description: 将已细化并通过评审的规格固化为结构化 PRD，形成需求到工程的交接边界。Turn refined and reviewed specs into a structured PRD as the product-to-engineering handoff boundary.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 写 PRD
  - 生成 PRD
  - 规格转 PRD
  - 固化 PRD
  - 规格已经 ready 了
  - 需求 ready 写 PRD
  - write PRD
  - generate PRD
  - turn spec into PRD
  - spec is ready produce PRD
  - produce PRD from reviewed spec
---

# 规格转 PRD

这个技能用于把当前对话、需求上下文和项目现状综合成 PRD。不要进行大范围访谈。只有当缺失信息会导致 PRD 误导研发或无法落地时，才向用户追问。

## 触发边界

- 适合触发：需求规格已经细化并通过必要评审，需要固化为结构化 PRD 作为工程交接边界。
- 不适合触发：需求还需要继续问答时，转交 `team-spec-refine`；PRD 已完成且要拆工程任务时，转交 `team-prd-to-issues`。

## 运行时配置

统一读取目标项目根目录 `team-spec/config.yml`：

```yaml
language: zh-CN
access_policy:
  mode: default-readonly
  directory_file: team-spec/access_policy/default.md
  user_file_template: team-spec/access_policy/{user_name}.md
```

语言优先级：用户本轮明确指定 > `team-spec/config.yml` > 首次询问并落盘。若配置不存在，不报错，走“询问并创建”流程。

执行要求：

- 对话回复与 PRD 文档 `team-spec/active/{slug}/prd/prd.md` 均使用 `language`。
- 用户临时切换语言时，本次立即生效，并询问是否回写配置。
- 在读取需求上下文、规格、评审或代码前，先读取 `team-spec/config.yml`；如果存在 `access_policy`，先确认当前协作者的读写边界，再决定是否允许进入写入流程。

## 公共写作风格

生成或改写文档、用户可见说明或代码注释前，如果目标项目存在 `team-spec/config.yml`，检查其中的 `writing_style.guide`。该路径指向存在的文件时，写作前必须读取并应用；相对路径以目标项目根目录解析。

优先满足格式、状态、安全、证据和验收合同，再按“用户本轮要求 > 本技能的产物类型规则 > 项目风格指南 > 目标文件相邻内容”处理表达。指南缺失时继续使用本技能规则，不阻塞任务、不猜测路径；需要建立或调整统一风格时使用 `team-writing-style`。

## 输入物

优先读取上游技能输出：

- `team-spec-refine` 的澄清结论。
- `team-spec/config.yml`（如果存在），用于确定统一语言设置。
- `team-spec/active/{slug}/spec/refine.md`。
- `team-spec/CONTEXT.md`。
- `team-spec/decisions/`。
- `team-spec/active/{slug}/spec/CONTEXT.md`。
- `team-spec/active/{slug}/spec/decisions/`。
- `team-spec/active/{slug}/spec/reviews.md`，或 `team-spec-review` 的阻塞项、风险清单和建议改写。
- 相关 PRD、规格、任务、设计稿、代码或项目文档。

如果没有澄清结论或需求上下文，先判断是否需要回到 `team-spec-refine`。如果存在未处理的 P0 或关键 P1 风险，先处理风险，不要直接固化到 PRD。

本技能是阶段性固化步骤，不是需求探索步骤。进入本技能前，`team-spec-refine` 与 `team-spec-review` 应已完成必要迭代，P0 和关键 P1 风险应已解决或被明确接受。

只允许基于 `Status: ready` 的 `team-spec/active/{slug}/spec/reviews.md` 生成 PRD。如果 review 状态为 `needs-refinement` 或 `blocked`，不要生成 PRD；应要求回到 `team-spec-refine` 或处理阻塞项，除非用户明确要求带风险草稿。

必须先确定本次 PRD 对应的 `{slug}`，以及明确的 `team-spec/active/{slug}/spec/refine.md` 和 `team-spec/active/{slug}/spec/reviews.md`。如果无法从用户请求、当前对话或文件路径中唯一判断，应停止并要求用户提供 slug、refine 文件路径或 review 文件路径，不要猜测要固化哪个规格。

## 输出物

- 结构化 PRD。
- 如果没有外部任务系统，默认保存到 `team-spec/active/{slug}/prd/prd.md`。
- PRD 中应保留开放问题、风险假设和验收标准，供 `team-prd-to-issues` 继续拆解工程任务。
- PRD 是需求到工程的正式交接边界。工程拆解技能应以 PRD 为主输入，而不是直接基于澄清过程材料拆任务。
- 若用户同意回写，更新 `team-spec/config.yml` 的语言设置。

## 流程

1. 阅读现有需求上下文：
   - `team-spec/CONTEXT.md`
   - `team-spec/decisions/`
   - `team-spec/active/{slug}/spec/CONTEXT.md`
   - `team-spec/active/{slug}/spec/decisions/`
   - `team-spec/active/{slug}/spec/refine.md`
   - `team-spec/active/{slug}/spec/reviews.md`
   - 相关 PRD、规格、任务或文档
2. 执行 `team-spec-review` 风格的前置检查，只识别会阻塞 PRD 的 P0/P1 风险。
3. 检查 `team-spec/active/{slug}/spec/reviews.md` 的 `Status`。如果不是 `ready`，先向用户说明原因，不要继续写完整 PRD，除非用户明确要求带风险起草。
4. 探索仓库，理解当前产品行为和实现边界。
5. 使用上下文中的规范术语，并遵守已有产品决策。
6. 识别受影响的产品模块、流程、权限、数据对象和运营界面。
7. 寻找可由研发独立测试的深模块或清晰 ownership 边界。
8. 按下面模板起草 PRD。
9. 如果项目已配置 issue tracker 或任务系统，将 PRD 发布到对应系统，并打上团队约定的 `ready-for-agent` 或 `ready-for-engineering` 标签；如果没有外部系统，就按仓库惯例创建或更新本地 Markdown PRD。
10. PRD 成功固化后，必须明确给出 PRD 路径 `team-spec/active/{slug}/prd/prd.md`，并用有序号的“下一步可选”列表提示后续技能：需要人类评审对齐时使用 `team-prd-to-alignment`，准备工程拆解时使用 `team-prd-to-issues`。

## PRD 模板

```md
# {功能/需求名称}

## 问题陈述

从用户视角描述当前问题、业务需求或产品机会。

## 目标

- 可衡量目标 1
- 可衡量目标 2

## 非目标

- 明确不做的事项
- 延后处理的事项

## 用户与场景

1. 作为{用户或角色}，我希望{能力}，以便{结果}。
2. 作为{用户或角色}，我希望{能力}，以便{结果}。

## 当前状态

总结当前已有能力、相关流程、约束和缺口。

## 方案描述

从用户视角描述产品行为。包括主路径、重要变体，以及方案如何改变当前流程。

## 范围

### 范围内

- 包含的行为、用户群体、平台、流程或数据对象。

### 范围外

- 排除的行为、用户群体、平台、流程或数据对象。

## 功能需求

1. 系统必须……
2. 用户可以……
3. 管理员可以……

## 业务规则

- 带有角色、条件和预期结果的规则。

## 边界情况与错误状态

- 场景：预期行为。

## 数据与状态

- 对象：关键字段、生命周期状态、归属、保留或可见性。

## 权限与合规

- 谁可以查看、创建、更新、审批、导出或删除。
- 隐私、审计、法律或合规约束。

## 发布与运营

- 迁移、功能开关、发布分群、监控、客服支持和回滚预期。

## 实现决策

- 可能变更的模块或 ownership 区域。
- 需要存在的接口或契约。
- 已确认的架构或 schema 决策。
- 不要写容易过期的文件路径或代码片段；除非原型片段比文字更能准确表达决策。

## 测试决策

- 测外部行为，不测实现细节。
- 需要自动化测试的模块或流程。
- 研发应参考的现有测试模式。
- 产品可以手工验收的例子。

## 验收标准

- Given {上下文}，When {动作}，Then {可观察结果}。
- Given {上下文}，When {动作}，Then {可观察结果}。

## 开放问题

- 问题、负责人，以及不解决会造成的影响。

## 补充说明

- 链接、假设、依赖或参考材料。
```

## 质量标准

- 研发不看原始对话也能理解 PRD。
- 用户故事覆盖主要用户、运营人员、管理员、审核者和失败场景。
- 验收标准必须可观察、可测试。
- 规范术语保持一致，不在同一概念上引入新同义词。
- 区分“本次必须交付”和“以后可以做”。
- 明确写出假设，不把假设藏进需求描述。
- 优先使用具体例子，不只写抽象判断。

## 发布方式

如果无法发布到外部任务系统，就按仓库已有 PRD 规范保存到本地。若没有现成规范，使用：

```text
team-spec/active/{slug}/prd/prd.md
```

目录只在需要时创建。

## 完成标准

- PRD 基于同一 slug 下 `Status: ready` 的规格评审结果生成。
- `team-spec/active/{slug}/prd/prd.md` 已创建或更新。
- PRD 能独立表达问题、目标、范围、规则、边界情况、验收标准、风险和开放问题。
- 没有把未确认假设写成工程承诺，且下游 `team-prd-to-issues` 可以直接读取。

## 最终回复

完成时必须输出：

- PRD 路径：`team-spec/active/{slug}/prd/prd.md`。
- 是否基于 `Status: ready` 的 review 生成。
- 仍保留的开放问题或已接受风险。
- 下一步可选：必须使用有序号的列表选项输出，方便用户直接回复序号继续推进。

推荐结尾：

```text
PRD 已固化到 team-spec/active/{slug}/prd/prd.md。
下一步可选：
1. team-prd-to-alignment：生成需求和研发对齐材料。
2. team-prd-to-issues：将该 PRD 拆解为工程 issue。
```
