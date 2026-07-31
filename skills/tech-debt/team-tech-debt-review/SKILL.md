---
name: team-tech-debt-review
description: 评审技术债规格的风险、优先级、阻塞项和工程 Task 拆解 ready 状态。Review technical debt specs for risk, priority, blockers, and readiness for Task breakdown.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 评审技术债
  - 技术债有没有风险
  - 技术债准备好了吗
  - 技术债 ready 了吗
  - 技术债能拆了吗
  - review tech debt
  - tech debt risk review
  - is tech debt ready for breakdown
  - ready to create tech debt tasks
---

# 技术债评审

这个技能用于评审技术债规格是否足够清晰、可执行、可验收，并判断是否可以进入工程 Task 拆解。

## 触发边界

- 适合触发：已有技术债规格或 refine 产物，需要评审风险、优先级、阻塞项和拆解 ready 状态。
- 不适合触发：债务诉求仍然模糊时，转交 `team-tech-debt-refine`；评审已 ready 且要拆 Task 时，转交 `team-tech-debt-to-tasks`。

## 运行时配置

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

- 对话回复与评审文档 `team-spec/active/{slug}/spec/reviews.md` 均使用 `language`。
- 用户临时切换语言时，本次立即生效，并询问是否回写配置。
- 在读取证据、日志、代码或写入评审文档前，先读取 `team-spec/config.yml`；如果存在 `access_policy`，先应用目录访问边界。

## 公共写作风格

生成或改写文档、用户可见说明或代码注释前，如果目标项目存在 `team-spec/config.yml`，检查其中的 `writing_style.guide`。该路径指向存在的文件时，写作前必须读取并应用；相对路径以目标项目根目录解析。

优先满足格式、状态、安全、证据和验收合同，再按“用户本轮要求 > 本技能的产物类型规则 > 项目风格指南 > 目标文件相邻内容”处理表达。指南缺失时继续使用本技能规则，不阻塞任务、不猜测路径；需要建立或调整统一风格时使用 `team-writing-style`。

## 输入物

- 当前对话中的技术债结论、证据和约束。
- `team-spec/active/{slug}/spec/refine.md`，这是主输入。
- `team-spec/CONTEXT.md` 与 `team-spec/decisions/`（如存在）。
- `team-spec/active/{slug}/spec/CONTEXT.md` 与 `team-spec/active/{slug}/spec/decisions/`（如存在）。
- 相关代码、监控、事故、缺陷、性能或运维材料。

必须先确定本次评审对应的 slug。技术债链路的 slug 必须包含 `debt`，如 `{yyyy-mm-dd}-debt-{short-english-slug}`。无法唯一判断时必须要求用户提供，不得猜测。

## 输出物

- 对话中的评审结论：`ready` / `needs-refinement` / `blocked`。
- `team-spec/active/{slug}/spec/reviews.md`：技术债评审报告。
- 给下游 `team-tech-debt-to-tasks` 的拆解前置结论（阻塞项、依赖、验收风险、HITL 决策点）。
- `team-spec/active/{slug}/STATUS.md`：评审结果为 `ready` 时可更新为工作区生命周期状态 `debt-ready`；不得把阶段评审结果直接写入工作区状态。

## 评审维度

- 问题与证据是否充分，是否存在“感受型”而非“证据型”结论。
- 范围、优先级和非目标是否清晰。
- 技术依赖、兼容性、回滚、迁移、发布策略是否可执行。
- 安全、合规、稳定性、性能和可维护性风险是否可控。
- 验收口径是否可观察、可测试、可复核。
- owner、依赖方、截止点是否明确。

## 处理原则

- 发现 P0 或关键 P1 时，输出 `needs-refinement` 或 `blocked`，并明确回到 `team-tech-debt-refine` 要补充的内容。
- 不编造风险；证据不足时明确指出缺口。
- 每个重要风险都要落到建议动作、owner 和截止点。

## 完成标准

- 生成 `team-spec/active/{slug}/spec/reviews.md`。
- 明确是否可进入 `team-tech-debt-to-tasks`。
- 如果不可进入，明确 Required Refinement 与 Questions For User。

## 最终回复

每次完成评审后，最终回复必须包含：

- 评审报告路径：`team-spec/active/{slug}/spec/reviews.md`，如果本次已保存。
- `Status`：`ready`、`needs-refinement` 或 `blocked`。这是阶段评审结果，写入 `spec/reviews.md`，不得写入工作区 `STATUS.md`。
- 下一步可选：必须使用有序号的列表选项输出，方便用户直接回复序号继续推进。
  - 当 `Status: ready` 时，选项 1 必须是 `team-tech-debt-to-tasks`，用于把通过评审的技术债规格拆解为工程 Task。
  - 当 `Status: needs-refinement` 时，选项 1 必须是 `team-tech-debt-refine`，并说明需要补充或修订哪些关键内容。
  - 当 `Status: blocked` 时，选项 1 必须是解除阻塞动作；如能判断解除后技能，再作为后续编号选项列出。

推荐结尾：

```text
技术债评审已完成，Status: ready。
下一步可选：
1. team-tech-debt-to-tasks：将通过评审的技术债规格拆解为工程 Task。
```
