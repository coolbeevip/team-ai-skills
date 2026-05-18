---
name: team-harness-refine
description: 通过真实代码、开发任务和失败反馈反复细化项目级 agent harness 提示词体系，以 AGENTS.md / CLAUDE.md 为入口，并从 team-spec/config.yml 读取 harness_dir 来维护渐进式知识地图、验证命令、反馈循环和 harness debt。Refine project-level agent harness prompt systems through real code, development tasks, and failure feedback, using AGENTS.md / CLAUDE.md as entry points and reading harness_dir from team-spec/config.yml for progressive maps, verification commands, feedback loops, and harness debt.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 细化 harness
  - 维护 AGENTS.md
  - 维护 CLAUDE.md
  - 改进 agent 工作环境
  - 让 agent 更好理解项目
  - 沉淀 agent 失败经验
  - refine harness
  - maintain AGENTS.md
  - maintain CLAUDE.md
  - improve agent harness
  - document agent workflow
  - capture harness debt
---

# Harness 细化

这个技能用于设计、建立和持续更新项目级 agent harness 提示词体系。harness 不是一份静态说明文档，而是以 `AGENTS.md` / `CLAUDE.md` 为入口、以 `team-spec/config.yml` 中配置的 `harness_dir` 为渐进式知识目录，让 agent 能够理解项目、执行任务、运行验证、处理失败并沉淀经验的工作环境。

本技能可以在项目初始接入 agent 时执行，也可以在工程演进、测试命令变化、架构调整、开发失败或交付事故后反复执行。每次执行都应基于真实代码、真实任务或真实失败反馈更新 harness，而不是只生成模板。

## 运行时配置

统一读取目标项目根目录 `team-spec/config.yml`：

```yaml
language: zh-CN
harness_dir: <relative-path-from-project-root>
```

上面的 `harness_dir` 是配置格式示例，不代表默认值。

语言优先级：用户本轮明确指定 > `team-spec/config.yml` > 首次询问并落盘。若配置不存在，不报错，走"询问并创建"流程。

Harness 目录规则：

- `harness_dir` 是本技能所有渐进式 harness 文档的唯一目录来源。
- 如果 `team-spec/config.yml` 不存在，应创建该文件，并在询问用户后写入 `harness_dir`。
- 如果 `team-spec/config.yml` 存在但缺少 `harness_dir`，必须先询问用户要使用哪个目录，然后写回 `team-spec/config.yml`。
- 不得在未读取或未写入 `harness_dir` 的情况下默认使用 `harness/`、`docs/agent-harness/` 或其他固定目录。
- `harness_dir` 应为相对项目根目录的路径，不应是绝对路径，不应位于 `team-spec/` 下。
- 后续所有 harness 文档路径必须由 `harness_dir` 拼接得到，本文用 `{harness_dir}/` 表示。

执行要求：

- 对话回复与 harness 文档（`AGENTS.md`、`CLAUDE.md`、`{harness_dir}/` 下内容）均使用 `language`。
- 用户临时切换语言时，本次立即生效，并询问是否回写配置。

## 输入物

- 当前项目中的 `AGENTS.md`、`CLAUDE.md` 或其他 agent 指令文件（如存在）。
- 当前项目中的 `README.md`、`docs/`、架构文档、开发手册、测试说明和运维说明。
- 真实代码、目录结构、构建配置、测试配置、脚本、CI 配置和本地开发工具。
- 最近的工程 issue、PR、失败测试、CI 日志、上线事故、人工修复记录或 agent 执行卡点。
- `team-spec/config.yml` 中配置的 `harness_dir`。
- 已有 `{harness_dir}/` 工作区（如存在）。
- 技术债链路产物，例如 `team-spec/active/spec/refine/{slug}.md`、`team-spec/active/spec/reviews/{slug}.md` 或 `team-spec/active/issues/{slug}/` 中与 harness 相关的条目。

如果用户没有提供明确范围，应先判断是要建立新 harness、审查现有 harness，还是根据某次开发任务或失败案例更新 harness。无法唯一判断时，只问一个最关键的问题，不要一次性展开访谈。

## 输出物

本技能默认必须产生或更新目标项目中的持久化输出物。除非用户明确说“只分析、不改文件”，否则不能只在对话中给建议后结束。

- 更新后的项目级 agent 入口文件：
  - `AGENTS.md`
  - `CLAUDE.md`（仅当项目使用 Claude 或用户要求时维护）
- `team-spec/config.yml`：必须包含 `harness_dir`，作为后续所有 harness 文档路径的唯一配置来源。
- `{harness_dir}/index.md`：harness 总入口和文档地图。
- `{harness_dir}/commands.md`：常用开发、测试、检查和调试命令。
- `{harness_dir}/verification.md`：不同变更类型对应的验证策略和最低验证命令。
- `{harness_dir}/architecture-map.md`：agent 需要理解的模块边界、关键路径和代码入口。
- `{harness_dir}/coding-rules.md`：项目特有的编码约束、提交约束和禁止事项。
- `{harness_dir}/review-rubric.md`：实现完成后自查和评审关注点。
- `{harness_dir}/known-failures.md`：已知失败模式、复现方式、规避方式和修复记录。
- `{harness_dir}/harness-debt.md`：阻碍 agent 独立工作的环境、文档、测试和工具缺口。
- `{harness_dir}/harness-review.md`：当本轮主要是审查、诊断或给改进建议时，必须写入本轮发现、证据、建议落点和后续动作。
- `team-spec/active/spec/refine/{yyyy-mm-dd}-debt-harness-{short-slug}.md`：当本轮发现需要工程处理、后续可能拆 issue 的 harness debt 时，必须同步生成或更新技术债规格。

如果项目已有其他文档结构，可以作为输入和引用来源；但本技能生成或维护的渐进式 harness 提示词材料必须放在 `team-spec/config.yml` 的 `harness_dir` 指定目录下，并保持 `AGENTS.md` 或 `CLAUDE.md` 能指向这些材料。

输出分层：

- Harness 提示词层：`AGENTS.md`、`CLAUDE.md`、`{harness_dir}/`，用于立即改善 agent 如何理解项目、运行命令和处理失败。
- Spec 流程层：`team-spec/active/spec/refine/{slug}.md`，用于承接需要工程实现、工具修复、测试补齐、CI 治理、架构文档重构或环境治理的 harness debt。

不要把可拆 issue 的工程工作只留在 `{harness_dir}/harness-debt.md`。`harness-debt.md` 可以作为索引和运行时记录，但需要进入交付流程的事项必须落到 `team-spec/active/spec/refine/{slug}.md`，并推荐下一步使用 `team-tech-debt-review`。

落盘规则：

- 新建 harness：先确保 `team-spec/config.yml` 包含 `harness_dir`，然后至少创建或更新 `AGENTS.md`，并创建 `{harness_dir}/index.md`、`commands.md`、`verification.md` 中与本轮证据相关的文件。
- 审查现有 harness：至少更新 `{harness_dir}/harness-review.md`，并把可直接固化的建议写入对应 harness 文档。
- 根据失败案例更新 harness：至少更新 `{harness_dir}/known-failures.md`；如果问题仍未解决，还要更新 `{harness_dir}/harness-debt.md`。
- 根据开发任务更新 harness：至少更新与任务相关的 `{harness_dir}/commands.md`、`{harness_dir}/verification.md`、`{harness_dir}/architecture-map.md`、`{harness_dir}/coding-rules.md` 或 `{harness_dir}/review-rubric.md` 之一。
- 发现无法通过文档解决的问题时，不能只在最终回复中建议；必须写入 `{harness_dir}/harness-debt.md`。
- 发现需要工程实现或后续拆 issue 的问题时，必须创建或更新 `team-spec/active/spec/refine/{slug}.md`；slug 必须包含 `debt` 和 `harness`，建议格式 `{yyyy-mm-dd}-debt-harness-{short-english-slug}`。

## 核心原则

- `AGENTS.md` 和 `CLAUDE.md` 是入口地图，不是百科全书；它们应保持短小，指向更具体的文档。
- harness 必须随工程演进持续更新。每次发现命令失效、上下文缺失、验证不足或失败模式重复出现，都应更新对应文档。
- harness 必须通过真实任务校验。不要只写“应该如何做”，要用现有代码、脚本或测试确认说明可执行。
- 优先记录可执行命令、判断标准和失败恢复方式，避免只写抽象原则。
- 不要把敏感信息、token、密钥、个人凭证或内部服务密码写入 harness 文档。
- 不要把所有架构细节塞进 agent 入口文件；复杂内容应放入 `{harness_dir}/`，必要时链接项目已有文档。
- 发现需要改代码、补测试、修脚本或治理环境的问题时，记录为 harness debt，并按风险决定是否转入技术债链路。
- 需要转入交付流程的 harness debt 应使用技术债规格承接，而不是发明独立流程。默认链路是 `team-spec/active/spec/refine/{slug}.md` -> `team-tech-debt-review` -> `team-tech-debt-to-issues`。

## 工作流

1. 识别本轮目标：新建 harness、审查现有 harness、根据开发任务更新 harness，或根据失败案例更新 harness。
2. 读取现有入口文件、项目文档、构建配置、测试配置、脚本和最近相关工程材料。
3. 建立当前 harness 快照：入口是否清晰、命令是否可执行、验证策略是否明确、失败经验是否可复用。
4. 选择一个真实任务、真实失败案例或最小代码路径作为校验样本。
5. 按现有 harness 尝试理解、执行或验证该样本，记录 agent 会卡住的位置。
6. 将卡点分类为上下文缺口、命令缺口、验证缺口、架构地图缺口、规则缺口、工具缺口或代码/测试债务。
7. 先确定本轮必须落盘的文件清单；如果用户没有禁止改文件，必须创建或更新至少一个 harness 输出物。
8. 更新 `AGENTS.md` / `CLAUDE.md` 和相关 `{harness_dir}/` 文档；已有内容应增量修订，不要无理由重写。
9. 如果本轮主要产出是建议或诊断，写入 `{harness_dir}/harness-review.md`，并把可执行建议分流到具体文档或 `harness-debt.md`。
10. 对更新后的 harness 做一次轻量复核：入口是否更短、更清晰，命令是否仍然可执行，新增文档是否能被入口找到。
11. 将无法通过文档解决的问题写入 `{harness_dir}/harness-debt.md`。
12. 对需要工程实现或后续拆 issue 的 harness debt，生成或更新 `team-spec/active/spec/refine/{slug}.md`，并推荐下一步使用 `team-tech-debt-review`。
13. 输出本轮更新摘要、验证结果、剩余 harness debt、已创建或更新的文件路径和推荐下一步。

## AGENTS.md / CLAUDE.md 维护规则

- 入口文件建议控制在可快速阅读的长度，只包含：
  - 项目目标和主要技术栈。
  - 常用开发、测试、检查命令的索引。
  - 关键目录和文档地图。
  - 必须遵守的工作方式和禁止事项。
  - 遇到失败时应记录到哪里。
  - 需要进一步阅读的 `{harness_dir}/` 文件。
- 如果 `AGENTS.md` 和 `CLAUDE.md` 同时存在，应避免两份文件长期分叉。优先让两者共享同一套 `{harness_dir}/` 文档。
- 如果项目已有成熟的 `docs/` 结构，应在入口文件中链接现有文档，不重复搬运内容。
- 如果命令依赖环境变量、服务、容器或外部账号，必须说明前置条件和安全边界，不得写入真实密钥。

## {harness_dir} 目录建议内容

### index.md

- harness 文档总览。
- agent 执行任务前必须阅读的最小文档集合。
- 不同任务类型应读取的文档路径。
- 最近一次 harness 更新记录。

### commands.md

- 安装依赖、启动服务、运行测试、格式化、类型检查、构建、调试和清理命令。
- 每条命令的适用场景、预期耗时、常见失败原因和替代命令。
- 需要审批、网络、凭证或外部服务的命令必须明确标注。

### verification.md

- 按变更类型定义最低验证要求，例如后端逻辑、前端 UI、数据库迁移、配置变更、文档变更。
- 明确哪些测试是快速本地验证，哪些是完整回归验证。
- 记录不可自动验证的人工检查项。

### architecture-map.md

- 关键模块边界、主要代码入口、核心数据流和外部依赖。
- 对 agent 最容易误判的模块关系做明确说明。
- 只记录有助于执行任务的架构信息，不复制完整架构文档。

### coding-rules.md

- 项目特有的编码风格、测试风格、错误处理、日志、配置和兼容性约束。
- 已被团队明确禁止的实现方式。
- 与通用语言规范重复的内容应少写或不写。

### review-rubric.md

- issue 完成前的自查清单。
- 评审时必须关注的行为正确性、回归风险、可观测性、安全性和可维护性。
- 与 `team-issue-verify` 可复用的验收映射规则。

### known-failures.md

- 失败症状、复现方式、根因、解决方式和最后确认日期。
- 区分一次性失败、环境问题、测试不稳定和真实缺陷。
- 重复出现的失败应转入 `harness-debt.md` 或技术债链路。

### harness-debt.md

- 阻碍 agent 独立工作的缺口，例如测试不可运行、命令过期、缺少本地数据、日志不可读、文档冲突、模块边界不清。
- 每条 debt 必须包含证据、影响、建议处理方式、优先级和是否已落到 `team-spec/active/spec/refine/{slug}.md`。
- 如果某条 debt 需要后续拆 issue，但尚未生成技术债规格，必须说明阻塞原因。

### harness-review.md

- 本轮审查目标、范围和证据来源。
- 发现的问题，按入口、命令、验证、架构地图、编码规则、失败经验和工具缺口分类。
- 每条建议的落点：应写入哪个 harness 文件，或是否应进入 `harness-debt.md`。
- 本轮已实际更新的文件路径。
- 尚未更新的原因和下一步动作。

## Harness Debt 规格格式

当 harness debt 需要进入评审和 issue 拆解时，使用与技术债链路兼容的规格文件：

```text
team-spec/active/spec/refine/{yyyy-mm-dd}-debt-harness-{short-english-slug}.md
```

建议结构：

```md
# {Harness Debt 标题}

Status: draft
Source: team-harness-refine
Type: harness debt

## Problem

说明 agent 在真实任务、验证或失败恢复中遇到的具体问题。

## Evidence

- 触发任务、命令、日志、失败现象或代码路径。

## Impact

- 对 agent 独立执行、验证可靠性、交付速度或质量的影响。

## Scope

### In Scope

- 本轮需要治理的范围。

### Out of Scope

- 明确暂不处理的范围。

## Acceptance Criteria

- [ ] Given {上下文}，When {动作}，Then {可观察结果}。

## Suggested Review

- 下一步使用 `team-tech-debt-review` 评审风险和 ready 状态。

## Links

- 关联 harness 文档、失败记录或代码路径。
```

该文件是后续 `team-tech-debt-review` 和 `team-tech-debt-to-issues` 的主输入。不要跳过 review 直接拆 issue，除非用户明确接受带风险草案。

## 与技术债技能联动

当 harness 缺口需要修改代码、补测试、改脚本、治理 CI、增加观测能力或重构文档结构时，不应只停留在 harness 文档中。应将其登记为 harness debt，并尽量沉淀为技术债规格后进入：

```text
team-tech-debt-refine
-> team-tech-debt-review
-> team-tech-debt-to-issues
```

如果本轮已经能清楚定义问题、证据、影响和验收口径，应直接生成 `team-spec/active/spec/refine/{slug}.md`，而不是只建议用户之后再手动运行 `team-tech-debt-refine`。如果问题还不清楚，再建议使用 `team-tech-debt-refine` 继续澄清。

典型联动场景：

- 测试命令长期不稳定，导致 agent 无法验证实现。
- 本地开发环境缺少可重复启动方式。
- 架构边界混乱，agent 多次改错模块。
- 日志、错误信息或指标不足，导致失败无法定位。
- CI 和本地验证结果长期不一致。

## 完成标准

- 除非用户明确要求只分析不改文件，否则至少有一个 harness 输出物已创建或更新。
- `AGENTS.md` 或 `CLAUDE.md` 能作为清晰入口，指向必要的 `{harness_dir}/` 文档。
- 常用命令、验证策略、架构地图、编码规则和失败记录至少覆盖本轮真实任务或失败案例。
- 新增或更新内容经过一次轻量验证，能被 agent 按说明找到并执行。
- 无法通过文档解决的问题已记录到 `{harness_dir}/harness-debt.md`。
- 需要工程处理或后续拆 issue 的 harness debt 已写入 `team-spec/active/spec/refine/{slug}.md`；如果没有写入，必须说明原因。
- 最终回复必须列出已创建或更新的文件路径；如果没有落盘文件，本轮不能宣称完成。
- 明确说明本轮是新建、更新还是复核 harness，并列出后续应重复执行的触发条件。
- 如果生成了技术债规格，最终回复必须推荐下一步使用 `team-tech-debt-review`，而不是直接进入实现。
