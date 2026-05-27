---
name: team-tech-debt-review
description: 评审技术债规格的风险与可执行性，确认优先级、阻塞项、处理动作和是否可进入工程拆解。Review technical debt specs for risk and execution readiness, then output blockers, mitigations, and readiness for issue breakdown.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 评审技术债
  - 技术债有没有风险
  - 技术债准备好了吗
  - 技术债 ready 了吗
  - review tech debt
  - tech debt risk review
  - is tech debt ready for breakdown
---

# 技术债评审

这个技能用于评审技术债规格是否足够清晰、可执行、可验收，并判断是否可以进入工程 issue 拆解。

## 运行时语言配置

统一读取目标项目根目录 `team-spec/config.yml`：

```yaml
language: zh-CN
```

语言优先级：用户本轮明确指定 > `team-spec/config.yml` > 首次询问并落盘。若配置不存在，不报错，走"询问并创建"流程。

执行要求：

- 对话回复与评审文档 `team-spec/active/{slug}/spec/reviews.md` 均使用 `language`。
- 用户临时切换语言时，本次立即生效，并询问是否回写配置。

## 输入物

- 当前对话中的技术债结论、证据和约束。
- `team-spec/active/{slug}/spec/refine.md`，这是主输入。
- `team-spec/CONTEXT.md` 与 `team-spec/decisions/`（如存在）。
- `team-spec/active/{slug}/spec/CONTEXT.md` 与 `team-spec/active/{slug}/spec/decisions/`（如存在）。
- 相关代码、监控、事故、缺陷、性能或运维材料。

必须先确定本次评审对应的 slug。技术债链路的 slug 必须包含 `debt`，如 `{yyyy-mm-dd}-debt-{short-english-slug}`。无法唯一判断时必须要求用户提供，不得猜测。

## 输出物

- 对话中的评审结论：`ready` / `needs refinement` / `blocked`。
- `team-spec/active/{slug}/spec/reviews.md`：技术债评审报告。
- 给下游 `team-tech-debt-to-issues` 的拆解前置结论（阻塞项、依赖、验收风险、HITL 决策点）。

## 评审维度

- 问题与证据是否充分，是否存在“感受型”而非“证据型”结论。
- 范围、优先级和非目标是否清晰。
- 技术依赖、兼容性、回滚、迁移、发布策略是否可执行。
- 安全、合规、稳定性、性能和可维护性风险是否可控。
- 验收口径是否可观察、可测试、可复核。
- owner、依赖方、截止点是否明确。

## 处理原则

- 发现 P0 或关键 P1 时，输出 `needs refinement` 或 `blocked`，并明确回到 `team-tech-debt-refine` 要补充的内容。
- 不编造风险；证据不足时明确指出缺口。
- 每个重要风险都要落到建议动作、owner 和截止点。

## 完成标准

- 生成 `team-spec/active/{slug}/spec/reviews.md`。
- 明确是否可进入 `team-tech-debt-to-issues`。
- 如果不可进入，明确 Required Refinement 与 Questions For User。

## 完成输出

每次完成评审后，最终回复必须包含：

- 评审报告路径：`team-spec/active/{slug}/spec/reviews.md`，如果本次已保存。
- `Status`：`ready`、`needs refinement` 或 `blocked`。
- 下一步可选：必须使用有序号的列表选项输出，方便用户直接回复序号继续推进。
  - 当 `Status: ready` 时，选项 1 必须是 `team-tech-debt-to-issues`，用于把通过评审的技术债规格拆解为工程 issue。
  - 当 `Status: needs refinement` 时，选项 1 必须是 `team-tech-debt-refine`，并说明需要补充或修订哪些关键内容。
  - 当 `Status: blocked` 时，选项 1 必须是解除阻塞动作；如能判断解除后技能，再作为后续编号选项列出。

推荐结尾：

```text
技术债评审已完成，Status: ready。
下一步可选：
1. team-tech-debt-to-issues：将通过评审的技术债规格拆解为工程 issue。
```
