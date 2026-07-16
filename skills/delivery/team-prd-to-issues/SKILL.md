---
name: team-prd-to-issues
description: 将 PRD 拆解为可独立领取、可验证、按依赖排序的端到端工程 issue。Break PRDs into independently grabbable, verifiable, dependency-ordered engineering issues.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 拆 issue
  - 把 PRD 拆成任务
  - 工程 issue 拆解
  - PRD 已经确认了开始拆工程任务
  - 生成工程任务
  - break PRD into issues
  - create issues from PRD
  - PRD is approved start issue breakdown
  - write engineering issues
---

# PRD 转工程 Issues

这个技能用于把 PRD 拆成工程团队可以直接领取的 issue。拆解目标是让每个 issue 都能独立实现、独立验证，并尽量减少跨 issue 的隐藏耦合。

## 触发边界

- 适合触发：结构化 PRD 已确认，需要拆成可独立领取、可验证、按依赖排序的工程 issue 草稿。
- 不适合触发：PRD 还未固化时，转交 `team-spec-to-prd`；issue 已生成且要发布远端时，转交 `team-issue-publish-github` 或 `team-issue-publish-gitlab`；要直接实现时，转交 `team-issue-implement` 或 `team-issue-batch-implement`。

## 运行时配置

统一读取目标项目根目录 `team-spec/config.yml`：

```yaml
language: zh-CN
version_control:
  system: git
  trunk_branch: main
  contribution_model: fork-pull
  source_remote: origin
  target_remote: upstream
access_policy:
  mode: default-readonly
  directory_file: team-spec/access_policy/default.md
  user_file_template: team-spec/access_policy/{user_name}.md
```

语言优先级：用户本轮明确指定 > `team-spec/config.yml` > 首次询问并落盘。若配置不存在，不报错，走“询问并创建”流程。

执行要求：

- 对话回复与 issue 草稿文档 `team-spec/active/{slug}/issues/` 下内容均使用 `language`。
- 用户临时切换语言时，本次立即生效，并询问是否回写配置。
- 生成“下一步可选”或判断发布平台时，优先参考 `version_control`；缺失时先通过 git 命令推断，无法唯一判断再询问用户，并在用户确认后回写 `team-spec/config.yml`。
- 在读取 PRD、规格、代码或写入 issue 草稿前，先读取 `team-spec/config.yml`；如果存在 `access_policy`，先应用目录访问边界，再进入拆解和写入流程。

## 输入物

优先使用当前对话已有材料。如果用户提供 issue 编号、URL、PRD 路径或文档路径，先读取完整内容和相关评论。

主输入必须是 `team-spec-to-prd` 生成的 PRD，默认来自 `team-spec/active/{slug}/prd/prd.md`。没有 PRD 时，不要直接基于澄清记录或风险清单拆工程任务；应先要求执行 `team-spec-to-prd`，除非用户明确要求生成临时工程草案。

- `team-spec/config.yml`（如果存在），用于确定统一语言设置、版本管理系统、主干分支和贡献方式。

必须先确定要拆解的 PRD，即明确的 `{slug}` 或 `team-spec/active/{slug}/prd/prd.md`。如果无法从用户请求、当前对话或文件路径中唯一判断，应停止并要求用户提供 slug 或 PRD 文件路径，不要猜测要拆哪个 PRD。

参考输入可以包括：

- `team-spec-review` 输出的阻塞项、HITL 决策点、风险清单和建议改写。
- `team-spec-refine` 产出的全局和局部规格上下文、产品决策记录，尤其是 `team-spec/CONTEXT.md`、`team-spec/decisions/`、`team-spec/active/{slug}/spec/CONTEXT.md` 与 `team-spec/active/{slug}/spec/decisions/`。
- 默认读取同 slug 参考材料：`team-spec/active/{slug}/spec/refine.md`、`team-spec/active/{slug}/spec/reviews.md`、`team-spec/active/{slug}/spec/CONTEXT.md` 和 `team-spec/active/{slug}/spec/decisions/`；同时读取全局 `team-spec/CONTEXT.md` 与 `team-spec/decisions/`。

必要时探索代码库，理解：

- 当前实现状态。
- 模块边界和 owner。
- 已有术语、ADR、测试模式和发布约束。
- 哪些改动可以作为端到端薄切片交付。

如果缺少足够上下文，不要直接创建 issue。先说明缺少的材料，并提出最少量的澄清问题。

## 输出物

- issue 拆解草案：标题、类型、依赖、覆盖的用户故事和切片理由。
- 正式 issue，如果用户确认并且 issue tracker 可用。
- 本地 Markdown issue 草稿，如果没有可用 issue tracker，默认保存到 `team-spec/active/{slug}/issues/{issue-number}-{short-issue-slug}.md`。
- 若用户同意回写，更新 `team-spec/config.yml` 的语言设置或已确认的 `version_control` 配置。

这些输出物通常是工程执行入口。下游 agent 或研发人员应能直接领取 `AFK` issue；`HITL` issue 必须先完成指定人工决策。

## 拆解原则

- 使用 vertical slice：每个 issue 覆盖一条窄但完整的端到端路径。
- 不按层拆分，例如“只做数据库”“只做 API”“只做 UI”通常不是好 issue。
- 每个 issue 完成后应可演示、可测试或可被产品验收。
- 优先拆成多个最小可验收薄切片，而不是少量大任务；但不要把同一验收闭环拆成无法独立验证的微任务。
- 明确依赖关系，阻塞项必须排在前面。
- 使用项目已有领域语言，不引入新术语。
- 不写易过期的文件路径或代码片段，除非原型片段比文字更能表达关键决策。

## 避免过度拆分

以下情况说明 issue 过薄，应优先合并到相邻 vertical slice：

- issue 完成后没有可演示、可测试或可被产品验收的观察结果，只能说明某个内部技术步骤完成。
- UI、API、数据、权限或日志改动共同服务同一个 Given/When/Then 验收场景，且没有独立风险、排期或 owner 边界。
- 拆出来的 issue 依赖另一个 issue 才能被人工或自动化验证，并且该依赖不是明确 blocker。
- issue 标题只能写成“新增字段”“调整接口”“补 UI”“改配置”等技术动作，无法表达用户可见行为或系统闭环。
- issue 预计实现和验证都很短，且没有单独回滚、并行或风险隔离价值。

允许拆得更薄的情况：

- 存在 HITL 决策、架构或合规 blocker、数据迁移、兼容性风险或跨团队排期。
- 先交付基础能力后，后续多个端到端切片会复用它，且基础能力本身有明确验证方式。
- 为了降低发布风险，需要把高风险变更与普通用户路径分开验证或回滚。
- 不同切片可以被不同 owner 并行实现，并且各自都有独立验收标准。

拆解后做一次合并检查：如果两个相邻 issue 共享同一用户故事、同一验收场景和同一发布边界，且拆开后没有并行、风险隔离或人工决策收益，应合并为一个 issue。

## HITL 与 AFK

每个 issue 必须标注类型：

- `AFK`：工程 agent 或研发可以独立完成，不需要中途人工决策。
- `HITL`：需要人工介入，例如产品确认、设计评审、架构决策、合规判断或跨团队排期。

优先把任务设计成 `AFK`。如果必须是 `HITL`，说明具体需要谁做什么决定。
用户可见输出中不要只写缩写。首次出现时写成 `AFK（可独立执行，无需人工决策）` 或 `HITL（需要人工介入）`。

## 流程

1. 汇总 PRD 的目标、用户故事、约束、验收标准和非目标。
2. 探索代码库或文档，确认当前系统边界。
3. 先草拟 issue 拆解，不要立即发布。
4. 对草稿做过度拆分检查；无法独立验收、共享同一验收场景且缺少拆分收益的 issue 应先合并。
5. 用编号列表向用户确认粒度和依赖。
6. 根据用户反馈合并、拆分或重排。
7. 用户确认后，再发布到 issue tracker；如果没有可用 issue tracker，则生成本地 Markdown issue 草稿。
8. 拆解完成后，必须输出有序号的“下一步可选”列表，按用户当前状态推荐后续动作，方便用户直接回复序号继续推进。
9. 输出“下一步可选”前，必须先判断当前项目更可能使用 GitHub 还是 GitLab，避免在信号明确时同时推荐两个发布技能。

确认时每个候选 issue 都要展示：

- `Title`：短标题。
- `Title example`：给出一个更自然、更具体的示例标题，尽量符合“动词 + 对象 + 范围”的结构。
- `Type`：`AFK（可独立执行，无需人工决策）` 或 `HITL（需要人工介入）`。
- `Blocked by`：依赖哪些 issue，或 `None`。
- `User stories covered`：覆盖哪些用户故事或验收场景。
- `Why this slice`：为什么它是一个可独立验证的端到端切片。

确认时先按下面顺序检查标题：

1. 先问自己：这个标题能不能脱离正文单独看懂。
2. 再问自己：标题里有没有动作、对象和范围。
3. 再检查：标题是不是退化成了文件名、模块名或 PRD 章节名。
4. 最后检查：是否只剩 `Fix`、`Update`、`Refactor`、`Improve` 这类空泛词。

## 标题规则

每个 issue 的标题必须足够清晰，拆解时就要满足下面约束：

- 标题必须一行内读完，不要带换行。
- 标题优先使用“动词 + 对象 + 范围”的结构。
- 标题必须能单独看懂，不依赖正文来补语义。
- 标题要避免空泛词，例如 `Fix`、`Update`、`Refactor`、`Improve`，除非后面紧跟明确对象和范围。
- 标题过长时，优先缩短范围而不是堆叠更多背景。
- 如果草拟标题退化成文件名、模块名或 PRD 章节名，说明切片不够具体，需要重写。
- 中文标题同样要具体，建议包含动作、对象和结果，不要只写“优化 XXX”或“处理 XXX”。

如果标题不满足这些规则，在确认候选 issue 时应直接重写，而不是把不清晰的标题带到发布阶段。

推荐展示格式：

- `Title`：`Allow CSV export to respect active row filters`
- `Title example`：`Export filtered rows to CSV`
- `Type`：`AFK（可独立执行，无需人工决策）`
- `Blocked by`：`None`
- `User stories covered`：`As a user, I can export only the rows I filtered in the table.`
- `Why this slice`：`This is a self-contained end-to-end export path with a clear verification step.`

如果检查结果不通过，优先重写标题，再决定这个 issue 是否要拆得更薄。

## Issue 模板

```md
## Status

draft

## Parent

{父 PRD 或需求来源；如果没有则省略}

## What to build

用简洁语言描述这个 vertical slice 的端到端行为。描述用户可见行为和系统边界，不写分层任务清单。

## Type

AFK（可独立执行，无需人工决策） / HITL（需要人工介入）

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
- 本地草稿默认保存到 `team-spec/active/{slug}/issues/{issue-number}-{short-issue-slug}.md`，目录只在需要时创建。

## Issue Tracker 判断

生成“下一步可选”前，先基于目标项目根目录做轻量判断，给发布技能排序：

1. 用户本轮明确指定 GitHub 或 GitLab 时，用户指定优先于自动探测。
2. 优先读取 `team-spec/config.yml` 的 `version_control`。若 `target_remote` 存在，优先检查该 remote；若 `contribution_model: fork-pull` 且未配置 `target_remote`，优先检查 `upstream`；否则检查当前分支 tracking remote 或 `origin`。
3. 通过 git 命令读取 remote URL，例如 `git remote -v`、`git config --get branch.{branch}.remote`。URL 包含 `github.com`、`github.` 或明确的 GitHub Enterprise 域名时，优先推荐 `team-issue-publish-github`；URL 包含 `gitlab.com`、`gitlab.` 或明确的 GitLab 自托管域名时，优先推荐 `team-issue-publish-gitlab`。
4. 如果 remote 不存在或无法判断，再检查仓库文件：存在 `.github/` 时优先推荐 `team-issue-publish-github`；存在 `.gitlab-ci.yml` 或 `.gitlab/` 时优先推荐 `team-issue-publish-gitlab`。
5. 如果 remote 与文件信号一致，只输出对应平台的发布选项，不要同时输出另一个平台的发布选项。
6. 如果 remote 与文件信号冲突，在“下一步可选”中把置信度最高的发布选项放在第 1 项，并在描述中说明冲突信号；第 2 项才列另一个发布技能作为备选。
7. 如果版本管理配置缺失且 git 命令也无法唯一推断，询问用户缺失的最小信息，例如平台、主干分支或贡献方式；用户确认后再回写 `team-spec/config.yml`。
8. 如果完全无法判断平台，可以同时列出 `team-issue-publish-github` 和 `team-issue-publish-gitlab`，但必须说明“未检测到明确平台信号，需要用户选择”。

## 下一步可选

每次完成 issue 拆解后，必须在最终回复中列出有序号的可选下一步，帮助用户直接回复序号继续推进。不要只说“已完成拆解”。

根据当前状态推荐，并输出为单层有序列表：

- `team-issue-publish-github`：已生成本地 issue 草稿但尚未发布到远端，且 Issue Tracker 判断结果指向 GitHub 时，发布到 GitHub Issues。
- `team-issue-publish-gitlab`：已生成本地 issue 草稿但尚未发布到远端，且 Issue Tracker 判断结果指向 GitLab 时，发布到 GitLab Issues。
- `team-issue-batch-implement`：存在多个可执行 `AFK` issue，且用户希望连续处理时，按依赖顺序批量编排实现与验证。
- `team-issue-implement`：只需要处理单个明确 `AFK` issue，或批量执行被阻塞时，开始单 issue 实现。
- 完成人工决策：issue 中存在 `HITL` 时，先完成对应人工决策，再继续发布或实现。
- `team-codex-harness`：拆解过程中发现入口约束、验证策略、失败记忆或任务入口不清楚时，先完善 Codex harness。
- `team-tech-debt-refine`：拆解过程中发现需要先治理的工程基础问题时，先细化为技术债规格。

不要机械地同时输出 GitHub 和 GitLab 发布选项。只有在平台信号冲突或完全无法判断时，才允许同时出现两个发布技能，并必须说明原因。

推荐格式：

```md
## 下一步可选

1. `team-issue-publish-github`：检测到 GitHub remote，发布到 GitHub Issues。
2. `team-issue-batch-implement`：存在多个可执行 `AFK` issue 时，按依赖顺序连续实现并逐个验证。
3. `team-issue-implement`：只处理一个明确的 `AFK` issue。
4. `team-codex-harness`：如果入口约束、验证策略或任务入口不清楚，先完善 harness。
```

## 质量标准

- issue 能被工程师或 agent 独立领取。
- issue 完成后有可观察结果，而不是只有内部重构。
- 依赖关系清楚，没有循环依赖。
- HITL issue 的人工决策点具体、可执行。
- AFK issue 不需要额外产品、设计或架构判断即可开始。
- issue 标题清晰、具体、可一眼理解，且不会在发布阶段依赖兜底修正。
- 最终回复包含有序号的“下一步可选”列表，且推荐与当前输出状态一致。
- 存在多个可执行 `AFK` issue 时，最终回复优先提示 `team-issue-batch-implement`；只有单个明确 issue 时才优先提示 `team-issue-implement`。
- 若已生成本地 issue 草稿，最终回复已基于 `team-spec/config.yml`、Git remote、`.github/`、`.gitlab-ci.yml` 或 `.gitlab/` 判断发布平台；除非信号冲突或无法判断，否则不会同时推荐 GitHub 和 GitLab 发布技能。
