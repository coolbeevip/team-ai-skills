# Skills For Real Teams

团队协作使用的大语言模型技能库，覆盖需求、产品和工程协作流程。

## Quickstart

安装全部技能：

```bash
npx skills@latest add coolbeevip/team-ai-skills --all
```

## Workflow

这些技能可以串联使用。下游技能会读取上游技能的输出物：

```mermaid
flowchart TD
    A[team-spec-refine] --> B[team-spec-review]
    B --> C{存在 P0 或关键 P1 风险?}
    C -- 是 --> A
    C -- 否 --> D[team-spec-to-prd]
    D --> E[team-prd-to-issues]
    E --> F[team-issue-next]
    F --> G[team-issue-implement]
    G --> H[team-issue-verify]
    H --> F
    F -. optional .-> S[team-issue-start]
    H -. optional .-> P[team-issue-pr]
```

`team-spec-refine` 和 `team-spec-review` 可以反复迭代。只有当 P0 和关键 P1 风险被解决或明确接受后，才进入 `team-spec-to-prd` 固化 PRD。

`team-spec/prd/` 中的 PRD 是需求到工程的正式交接边界。`team-prd-to-issues` 应以 PRD 为主输入；`CONTEXT.md`、`decisions/` 和 `reviews/` 只能作为背景参考，不能绕过 PRD 直接拆工程任务。

`team-spec-to-prd` 完成后，应明确提示下一步执行 `team-prd-to-issues`，并把 `team-spec/prd/{slug}.md` 作为主输入。

每个 `SKILL.md` 都声明了 `输入物` 和 `输出物`，用于说明它会读取哪些上游产物，以及会为哪些下游技能提供材料。

每个需求使用一个唯一 slug 串联全流程，格式为 `{yyyy-mm-dd}-{short-english-slug}`，例如 `2026-05-10-export-filter`。

## Workspace

技能默认在目标项目根目录的 `team-spec/` 下协作。`team-spec/` 是运行时工作空间，不属于本技能库的固定内容；它会在安装技能后的业务项目中按需创建。

```text
team-spec/
├── spec/
│   ├── CONTEXT.md
│   ├── decisions/
│   ├── refine/
│   └── reviews/
├── prd/
└── issues/
```

单个需求的产物链路：

```text
team-spec/spec/refine/{slug}.md
team-spec/spec/reviews/{slug}.md
team-spec/prd/{slug}.md
team-spec/issues/{slug}/
```

`CONTEXT.md` 和 `decisions/` 是长期共享上下文，不替代单次需求的 `refine/{slug}.md`。

`team-prd-to-issues` 默认以 `team-spec/prd/{slug}.md` 为主输入，并参考规格上下文、产品决策和评审报告，再将工程 issue 草稿写入 `team-spec/issues/{slug}/`。

`team-issue-next` 从 `team-spec/issues/{slug}/` 中选择下一个可开始的 issue。

`team-issue-start` 是可选工程协作技能，用于团队希望 AI 协助管理 issue 分支时准备干净分支。

`team-issue-implement` 默认以 `team-spec/issues/{slug}/` 中的单个 issue 为主输入，通过行为测试和 red-green-refactor 循环完成实现。

`team-issue-verify` 独立检查实现是否满足 issue、PRD 和风险约束，并输出是否 `ready for PR`。

`team-issue-pr` 是可选工程协作技能，用于团队允许 AI 协助提交、推送分支并创建 PR 时使用。
