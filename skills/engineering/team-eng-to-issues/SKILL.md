---
name: team-eng-to-issues
description: 将 PRD、技术方案、需求说明或开发计划拆解为可独立领取、可验证、按依赖排序的工程 issue，强调端到端 vertical slice，而不是按层拆任务。Break PRDs, specs, requirements, or implementation plans into independently grabbable engineering issues using end-to-end vertical slices instead of horizontal layer-based tasks.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# 工程任务拆解

这个技能用于把 PRD、技术方案或开发计划拆成工程团队可以直接领取的 issue。拆解目标是让每个 issue 都能独立实现、独立验证，并尽量减少跨 issue 的隐藏耦合。

## 输入物

优先使用当前对话已有材料。如果用户提供 issue 编号、URL、PRD 路径或文档路径，先读取完整内容和相关评论。

优先读取上游技能输出：

- `team-req-to-prd` 生成的 PRD。
- `team-req-risk-analysis` 输出的阻塞项、HITL 决策点、风险清单和建议改写。
- `team-req-clarify` 产出的需求上下文和产品决策记录，尤其是 `team-spec/requirements/CONTEXT.md` 与 `team-spec/requirements/decisions/`。
- 默认从需求人员工作空间读取输入：`team-spec/requirements/prd/`、`team-spec/requirements/risks/`、`team-spec/requirements/CONTEXT.md` 和 `team-spec/requirements/decisions/`。

必要时探索代码库，理解：

- 当前实现状态。
- 模块边界和 owner。
- 已有术语、ADR、测试模式和发布约束。
- 哪些改动可以作为端到端薄切片交付。

如果缺少足够上下文，不要直接创建 issue。先说明缺少的材料，并提出最少量的澄清问题。

## 输出物

- issue 拆解草案：标题、类型、依赖、覆盖的用户故事和切片理由。
- 正式 issue，如果用户确认并且 issue tracker 可用。
- 本地 Markdown issue 草稿，如果没有可用 issue tracker，默认保存到 `team-spec/engineering/issues/{yyyy-mm-dd}-{short-slug}.md`。

这些输出物通常是工程执行入口。下游 agent 或研发人员应能直接领取 `AFK` issue；`HITL` issue 必须先完成指定人工决策。

## 拆解原则

- 使用 vertical slice：每个 issue 覆盖一条窄但完整的端到端路径。
- 不按层拆分，例如“只做数据库”“只做 API”“只做 UI”通常不是好 issue。
- 每个 issue 完成后应可演示、可测试或可被产品验收。
- 优先拆成多个薄切片，而不是少量大任务。
- 明确依赖关系，阻塞项必须排在前面。
- 使用项目已有领域语言，不引入新术语。
- 不写易过期的文件路径或代码片段，除非原型片段比文字更能表达关键决策。

## HITL 与 AFK

每个 issue 必须标注类型：

- `AFK`：工程 agent 或研发可以独立完成，不需要中途人工决策。
- `HITL`：需要人工介入，例如产品确认、设计评审、架构决策、合规判断或跨团队排期。

优先把任务设计成 `AFK`。如果必须是 `HITL`，说明具体需要谁做什么决定。

## 流程

1. 汇总源材料的目标、用户故事、约束、验收标准和非目标。
2. 探索代码库或文档，确认当前系统边界。
3. 先草拟 issue 拆解，不要立即发布。
4. 用编号列表向用户确认粒度和依赖。
5. 根据用户反馈合并、拆分或重排。
6. 用户确认后，再发布到 issue tracker；如果没有可用 issue tracker，则生成本地 Markdown issue 草稿。

确认时每个候选 issue 都要展示：

- `Title`：短标题。
- `Type`：`AFK` 或 `HITL`。
- `Blocked by`：依赖哪些 issue，或 `None`。
- `User stories covered`：覆盖哪些用户故事或验收场景。
- `Why this slice`：为什么它是一个可独立验证的端到端切片。

## Issue 模板

```md
## Parent

{父 issue、PRD 或需求来源；如果没有则省略}

## What to build

用简洁语言描述这个 vertical slice 的端到端行为。描述用户可见行为和系统边界，不写分层任务清单。

## Type

AFK / HITL

如果是 HITL，说明需要谁做什么决定。

## Acceptance criteria

- [ ] Given {上下文}，When {动作}，Then {可观察结果}。
- [ ] Given {上下文}，When {动作}，Then {可观察结果}。
- [ ] 相关自动化或手工验证路径明确。

## Blocked by

- None - can start immediately

或：

- #{blocking-issue-id}

## Notes

- 关键约束、假设、测试建议或发布注意事项。
```

## 发布规则

- 按依赖顺序发布，先发布 blocker，再发布依赖它的 issue。
- 不要关闭、修改或重写父 issue，除非用户明确要求。
- 如果发布到 GitHub Issues，使用团队约定的 triage label；如果没有约定，先询问或生成草稿。
- 本地草稿默认保存到 `team-spec/engineering/issues/{yyyy-mm-dd}-{short-slug}.md`，目录只在需要时创建。

## 质量标准

- issue 能被工程师或 agent 独立领取。
- issue 完成后有可观察结果，而不是只有内部重构。
- 依赖关系清楚，没有循环依赖。
- HITL issue 的人工决策点具体、可执行。
- AFK issue 不需要额外产品、设计或架构判断即可开始。
