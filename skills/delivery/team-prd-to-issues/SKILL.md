---
name: team-prd-to-issues
description: 将 PRD 拆解为可独立领取、可验证、按依赖排序的工程 issue，强调端到端 vertical slice，而不是按层拆任务。Break PRDs into independently grabbable engineering issues using end-to-end vertical slices instead of horizontal layer-based tasks.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 拆 issue
  - 把 PRD 拆成任务
  - 工程 issue 拆解
  - PRD 已经确认了开始拆工程任务
  - break PRD into issues
  - create issues from PRD
  - PRD is approved start issue breakdown
---

# PRD 转工程 Issues

这个技能用于把 PRD 拆成工程团队可以直接领取的 issue。拆解目标是让每个 issue 都能独立实现、独立验证，并尽量减少跨 issue 的隐藏耦合。

## 输入物

优先使用当前对话已有材料。如果用户提供 issue 编号、URL、PRD 路径或文档路径，先读取完整内容和相关评论。

主输入必须是 `team-spec-to-prd` 生成的 PRD，默认来自 `team-spec/prd/{slug}.md`。没有 PRD 时，不要直接基于澄清记录或风险清单拆工程任务；应先要求执行 `team-spec-to-prd`，除非用户明确要求生成临时工程草案。

必须先确定要拆解的 PRD，即明确的 `{slug}` 或 `team-spec/prd/{slug}.md`。如果无法从用户请求、当前对话或文件路径中唯一判断，应停止并要求用户提供 slug 或 PRD 文件路径，不要猜测要拆哪个 PRD。

参考输入可以包括：

- `team-spec-review` 输出的阻塞项、HITL 决策点、风险清单和建议改写。
- `team-spec-refine` 产出的规格上下文和产品决策记录，尤其是 `team-spec/spec/CONTEXT.md` 与 `team-spec/spec/decisions/`。
- 默认从规格工作空间读取同 slug 参考材料：`team-spec/spec/refine/{slug}.md`、`team-spec/spec/reviews/{slug}.md`、`team-spec/spec/CONTEXT.md` 和 `team-spec/spec/decisions/`。

必要时探索代码库，理解：

- 当前实现状态。
- 模块边界和 owner。
- 已有术语、ADR、测试模式和发布约束。
- 哪些改动可以作为端到端薄切片交付。

如果缺少足够上下文，不要直接创建 issue。先说明缺少的材料，并提出最少量的澄清问题。

## 输出物

- issue 拆解草案：标题、类型、依赖、覆盖的用户故事和切片理由。
- 正式 issue，如果用户确认并且 issue tracker 可用。
- 本地 Markdown issue 草稿，如果没有可用 issue tracker，默认保存到 `team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.md`。

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

1. 汇总 PRD 的目标、用户故事、约束、验收标准和非目标。
2. 探索代码库或文档，确认当前系统边界。
3. 先草拟 issue 拆解，不要立即发布。
4. 用编号列表向用户确认粒度和依赖。
5. 根据用户反馈合并、拆分或重排。
6. 用户确认后，再发布到 issue tracker；如果没有可用 issue tracker，则生成本地 Markdown issue 草稿。
7. 拆解完成后，必须输出“下一步可选技能”，按用户当前状态推荐后续动作。

确认时每个候选 issue 都要展示：

- `Title`：短标题。
- `Type`：`AFK` 或 `HITL`。
- `Blocked by`：依赖哪些 issue，或 `None`。
- `User stories covered`：覆盖哪些用户故事或验收场景。
- `Why this slice`：为什么它是一个可独立验证的端到端切片。

## Issue 模板

```md
## Parent

{父 PRD 或需求来源；如果没有则省略}

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
- 不要关闭、修改或重写父 PRD，除非用户明确要求。
- 如果发布到 GitHub Issues，使用团队约定的 triage label；如果没有约定，先询问或生成草稿。
- 本地草稿默认保存到 `team-spec/issues/{slug}/{issue-number}-{short-issue-slug}.md`，目录只在需要时创建。

## 下一步可选技能

每次完成 issue 拆解后，必须在最终回复中列出可选下一步，帮助用户继续推进。不要只说“已完成拆解”。

根据当前状态推荐：

- 如果已生成本地 issue 草稿但尚未发布到远端：
  - `team-prd-issues-publish-github`：将本地 issue 草稿批量发布到 GitHub Issues。
  - `team-prd-issues-publish-gitlab`：将本地 issue 草稿批量发布到 GitLab Issues。
- 如果用户不需要远端 issue tracker，或已经有明确的本地 issue：
  - `team-issue-implement`：选择一个 `AFK` issue 开始实现。
- 如果 issue 中存在 `HITL`：
  - 先完成对应人工决策，再继续发布或实现。
- 如果拆解过程中发现测试命令、项目入口、验证方式或 agent 工作环境不清楚：
  - `team-harness-refine`：更新项目 harness、验证命令、知识地图和失败反馈记录。
- 如果拆解过程中发现需要先治理的工程基础问题：
  - `team-tech-debt-refine`：把该问题细化为技术债规格，再进入技术债评审和拆解。

推荐格式：

```md
## 下一步可选

1. `team-prd-issues-publish-github`：发布到 GitHub Issues。
2. `team-prd-issues-publish-gitlab`：发布到 GitLab Issues。
3. `team-issue-implement`：从第一个可开始的 `AFK` issue 进入实现。
4. `team-harness-refine`：如果验证命令或 agent 工作环境不清楚，先完善 harness。
```

## 质量标准

- issue 能被工程师或 agent 独立领取。
- issue 完成后有可观察结果，而不是只有内部重构。
- 依赖关系清楚，没有循环依赖。
- HITL issue 的人工决策点具体、可执行。
- AFK issue 不需要额外产品、设计或架构判断即可开始。
- 最终回复包含“下一步可选技能”，且推荐与当前输出状态一致。
