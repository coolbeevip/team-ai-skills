---
name: team-task-batch-implement
description: 在同一 Spec 分支批量实现多个 Task，开始前选择逐项确认或限定范围内自动提交。Batch implement tasks on one shared spec branch with an upfront choice between per-task review and bounded automatic local commits.
license: MIT
metadata:
  author: coolbeevip
  version: "0.9.1"
triggers:
  - 批量实现 Task
  - 连续处理多个工程任务
  - 在同一分支完成所有任务
  - batch implement tasks
  - implement multiple tasks
  - complete tasks on one branch
---

# Task 批量实现编排

在同一个 `{slug}` 分支上按依赖顺序处理多个 Task。分支名严格等于 slug，不添加 `spec/` 或其他前缀。开始前确定 Task 范围并选择提交模式。每个 Task 都完整执行实现、独立验证并形成一个本地 commit；任何失败或暂停都保留可恢复边界。

核心原则：一个 Spec 分支，多个 Task commits，最后一个 Spec PR/MR。

## 触发边界

- 适合触发：用户要求连续处理同一 slug 的多个 Task，并选择逐 Task 确认或在限定范围内自动执行。
- 不适合触发：单个 Task 使用 `team-task-implement`；只验证一个 Task 使用 `team-task-verify`；创建远端合并请求使用 Spec 级技能。

## 运行时配置

先读取 `team-spec/config.yml`。文件不存在或批量实现、提交所需字段缺失时，先使用 `team-config-init` 创建或增量补全；本技能不得自行回写配置。应用语言、访问策略、`trunk_branch`、`contribution_model`、`source_remote` 和 `target_remote`。无法确认唯一 slug、写权限或主干分支时停止。

每个 Commit message 统一使用“用户对本次批次的明确指定 > `version_control.language` > 顶层 `language` > `en-US`”确定的版本控制交付语言。交付语言与 Task 文档语言不同时，只转换变更摘要，不修改 Task 原文；代码标识符和专有名词保持原样。Commit message 不添加 `T001` 等 Task ID 前缀或后缀，Task 关联只记录在 Task 文件和 Task/commit 映射中。

## 公共写作风格

生成或改写 Task、汇总、用户可见说明或代码注释前，读取配置中的 `writing_style.guide`（如果存在）。

## 输入物

主输入必须能唯一定位同一个 slug 的 Task 集合：

- `team-spec/active/{slug}/tasks/`
- 或用户显式指定的同 slug Task 文件。

参考同 slug 的 PRD、规格、评审、上下文、决策、代码和测试。

不同 slug 的 Task 不得进入同一批次。HITL、缺少验收、依赖未提交或已 `committed` 的 Task 不进入实现队列。

## 输出物

- 依赖排序后的批量计划。
- 每个已处理 Task 的实现、验证、所选模式的提交控制和独立 commit。
- 可选汇总：`team-spec/active/{slug}/tasks/batch-implementation.md`。
- 最终共享分支和剩余队列。

不 push，不创建远端 Issue、PR 或 MR。

## 固定脚本

优先运行：

```text
./scripts/plan_task_batch.py
```

默认只规划，不修改代码：

```sh
python3 {skill_dir}/scripts/plan_task_batch.py --slug {slug}
python3 {skill_dir}/scripts/plan_task_batch.py --slug {slug} --limit 3 --json
```

脚本读取 Task ID、类型、状态、验收标准和依赖，识别缺失依赖、循环、HITL、已提交 Task 和可执行队列。

## 共享分支合同

- 单任务、批量任务和 PR/MR 统一使用与 slug 完全同名的 `{slug}` 分支，不添加前缀、不提供分支名覆盖例外。已有非标准分支时停止并说明差异，不自动重命名。
- 先区分产品代码与 `team-spec/` 运行时文档。仅有可归因、未暂存的 `team-spec/` 变化时允许继续，不要求暂存、提交或 stash；文档已暂存或存在未解决的 Git 操作时停止，不自行清理。
- 当前已在 Spec 分支时，可保留明确属于当前 Task 的未暂存代码变化；通过 `--task-path` 逐个传入已核对的路径。其他代码变化仍阻塞。需要切分支时，任何非 `team-spec/` 变化都阻塞，不能用该参数放行。
- Spec 分支已存在时直接切换，不同步主干。创建新分支时先 fetch：`direct` 使用 source remote，`fork-pull` 使用 target remote；本地主干必须可快进到所取提交。然后切换主干、以 `--ff-only` 同步并创建 Spec 分支；主干超前或分叉时停止，不自动产生 merge commit 或 rebase。
- 切换和同步必须保留 Git 覆盖保护，包括未跟踪和被忽略文件；禁止 autostash。若文件会被覆盖，则停止，报告具体路径、当前分支和已完成步骤，不强制切换、不自动回滚或丢弃变化。
- 每个 Task commit 后重新确认分支和变化归属；`team-spec/` 回写继续保持未暂存，不加入代码 commit。

## 分支准备脚本

使用 [prepare_spec_branch.py](./scripts/prepare_spec_branch.py) 检查工作区并准备共享分支；脚本通过本地 [_team_common.py](./scripts/_team_common.py) 读取保留状态列和完整路径的 Git 记录。仅依赖 Python 标准库和 Git，在目标项目根目录执行。

```sh
python3 {skill_dir}/scripts/prepare_spec_branch.py --slug {slug} --trunk-branch {trunk_branch} --contribution-model {direct|fork-pull} --source-remote {source_remote} --target-remote {target_remote}
```

默认 dry-run，仅检查本地状态并输出 JSON 计划，不 fetch、不写文件。准备正式进入开发分支时追加 `--execute`；只有新建分支才需要主干、贡献模式和对应 remote 参数，值来自已读取的配置或已确认的 Git 证据。已在目标分支时不执行 Git 变更。`--task-path relative/path` 可重复，仅供恢复同一分支上已明确归属于当前 Task 的未暂存变化。

脚本不执行 add、commit、stash、reset 或 push，不回写配置。dry-run 不代表远端最新状态或实际切换已验证；execute 时 Git 覆盖保护是最终检查。失败后检查当前分支与输出，保留现场后恢复，不盲目重复整个流程。

## 批量边界

默认最多处理 3 个 Task。用户明确要求全部时可以更多，但仍逐个验证和提交。

先展示 slug、分支、确定的 Task ID 与顺序、依赖、跳过和阻塞项、批量上限，并让用户选择：

1. `🔍 逐 Task 确认`：每个 Task 验证后展示实际 diff，等待用户确认再提交。
2. `🚀 批次自动执行`：授权本次已展示范围内的本地 Task commits；每个 Task 仍须独立验证和提交，正常完成后集中汇报。

用户在本次请求中已经明确指定 slug、Task 集合和模式时，展示核对后的队列即可采用，不重复询问。只指定模式或只说“批量实现”“全部完成”时，展示确定范围并等待用户选择或确认后再开始分支准备和实现；AFK 分类不能推断为自动模式。模式选择只对当前 slug、已展示的 Task 集合和本次批次有效；恢复中断批次时，只有范围和模式仍能从本次会话明确确认且没有范围变化，才可沿用，否则重新选择。新增 Task、改变已展示顺序或验收范围时停止并重新展示计划、取得模式选择。模式选择不授权 push、远端 Issue、PR 或 MR。

每个 Task 严格执行：

```text
team-task-implement
→ team-task-verify
→ verified
→ inspect current diff and exact commit scope
→ apply selected commit mode
→ one local commit
→ Task status committed
```

逐 Task 确认模式执行 `team-task-implement` 的完整“提交前确认”。批次自动执行模式使用本节的限定授权，不调用单任务的逐项确认；该 Task 达到 `committed` 后才继续下一个。两种模式都必须在暂存前审查实际 diff、核对验证证据和提交范围，不能提前暂存后续 Task 的变化。

## 批量测试合同

批量编排不得简化 `team-task-implement` 的“测试行为，不测试实现”“测试设计与契约维护”和 `team-task-verify` 的“测试契约审查”。每个 Task 都必须检查业务结果断言和重构敏感性，不得以内部调用次数或 Mock 预设结果代替验收证据。测试不是只增不减的队列产物；每个 Task 都应让测试集合收敛到该 Task 完成后的当前契约。

- 接口、参数、数据格式、配置项或命令行契约被替换时，在当前 Task 内修改或删除失效测试、fixture、Fake/Mock、快照和示例，不把旧测试留给未定义的后续清理 Task。
- 旧契约测试只有具备明确兼容、迁移或动态外部输入拒绝依据时才能保留，并记录依据和移除条件。没有依据的旧参数检查使当前 Task 保持 `needs-changes`，不得进入提交确认。
- 每个 Task 遵循 `team-task-implement` 的“真实依赖、Fake 与时间控制”和“E2E 优先与分级执行”：禁止 Mock，基础设施优先用真实实例，难以接入的外部系统才注入经过真实契约校验的 Fake，时间逻辑使用 fake timer，禁止固定 sleep。优先从用户入口验证可见结果；其他测试层级需有具体理由。
- 每个 Task 提交前运行快速冒烟、新增或修改的测试、Task 定向测试和覆盖已完成 Task 的受影响回归测试；按本次改动及直接、间接依赖选测，不逐 Task 重跑全量。批次结束时核对累计改动的回归覆盖，补跑尚无有效证据的受影响测试；完整测试集按项目周期和发布规则运行。
- 每个 Task 的摘要分别列出新增、改写和删除的测试，以及保留兼容测试的依据。测试数量下降本身不是失败。
- 如果旧测试清理无法与当前契约变更形成同一个可验证 commit，停止批次并返回 Task 拆解调整边界，不得用批量流程掩盖不完整契约。

## 工作流

1. 确定唯一 slug 和 Task 集合。
2. 读取配置、来源规格（产品 PRD 或已评审技术债）、评审和必要上下文。
3. 使用分支准备脚本检查工作区与共享分支，区分运行时文档和代码变化。
4. 运行 `plan_task_batch.py`。
5. 展示确定的队列、跳过项、阻塞项和批量上限，取得“批量边界”中的模式选择。
6. 正式执行分支准备脚本，创建或进入与 slug 完全相同的 `{slug}` 分支。
7. 按顺序实现并验证当前 Task，完成测试契约审查，不暂存代码。
8. 当前 Task 达到 `verified` 后检查修改文件、测试新增/改写/删除、保留兼容测试依据、实际 diff、拟提交范围、验证结果和残余风险。逐 Task 模式向用户展示并等待确认；自动模式记录摘要，按限定授权继续。
9. 逐 Task 模式下，用户要求继续修改时修改并重新验证；用户选择查看或暂停时停止批次并保留当前改动与剩余队列。自动模式下，出现停止条件时停止，不把异常当作已授权变更。
10. 按所选模式满足提交条件后，只暂存当前 Task 的代码、测试和必要配置，排除 `team-spec/` 与无关改动；复核暂存差异与已验证范围一致后创建一个本地 commit，记录 Task ID、SHA、测试和残余风险。
11. 当前 Task 达到 `committed` 后继续下一个；任何失败立即停止，保留已完成 commits 和剩余队列。
12. 只有所有必需 Task 均 `committed` 时，才推荐 Spec 级 PR/MR。

## 逐 Task 提交确认

每个 Task 验证通过后、执行任何暂存或 commit 前，完整执行 `team-task-implement` 的“提交前确认”合同。至少提供以下选择并等待用户回复：

1. `✅ 接受当前实现并提交`：只提交当前 Task 已展示的范围。
2. `🔍 暂不提交，我要先查看 diff`：停止批次，保持当前 Task 未暂存、未提交。
3. `🔄 继续修改当前 Task`：修改并重新验证，随后重新确认。
4. `⏸️ 暂停并保留当前改动`：停止批次，保留已完成 commits、当前未提交改动和剩余队列。

一次确认只覆盖一个 Task 的当前实际 diff，不能同时批准后续尚未实现的 Task。确认后出现任何实现变化时，当前确认失效；重新验证并确认后才能提交。

逐 Task 提交确认是代码交付控制点，不改变 Task 原有的 AFK/HITL 分类。

## 批次自动执行

用户明确选择自动模式后，已展示的 Task 范围和提交模式构成本批次的本地 commit 授权。每个 Task 验证通过后，先保持代码未暂存，检查实际 diff、未跟踪文件、验证结果、测试契约与拟提交范围；只在变化均可归于当前 Task 且符合已展示验收范围时暂存。复核暂存差异与已检查、已验证的范围一致后提交，不逐项等待用户回复。任何验证后发生的代码、测试或配置变化都要重新验证并检查差异。

不得因自动模式跳过 `team-task-verify`、合并多个 Task commit、扩大 Task 集合，或把 `team-spec/` 回写纳入代码 commit。出现 HITL、规格或设计决策、验收范围变化、无法归因的文件、验证失败、提交失败时立即停止；保留已完成 commits 和当前工作区现场，报告原因、暂存状态、可检查的 diff 和剩余队列，待用户处理后再恢复。批次结束时按 Task 汇总 commit SHA、主要 diff、测试变化、验证结果和残余风险。

## 停止条件

- 当前 Task 验证结果不是 `verified`。
- 逐 Task 模式下，当前 Task 已验证，但用户选择查看 diff、继续修改或暂停；此时不得 commit 或开始下一个 Task。
- commit 创建失败或范围混入其他 Task。
- 测试失败或缺少关键验证方法。
- 存在无兼容依据的旧契约测试，或测试无法识别合理错误实现。
- 出现 HITL、缺失依赖或循环依赖。
- 需要修改 PRD、规格或产品决策。
- 分支发生切换或出现其他 slug 的 commit。
- 工作区出现无法归因的变化。

停止后不得回滚已验证 commits；应报告恢复入口。

## 完成标准

- 所有已处理 Task 都按所选模式完成提交控制，处于 `committed` 并记录唯一 SHA。
- 每个已处理 Task 的测试集合反映提交后的当前契约，旧契约引用已删除或有明确兼容依据和移除条件。
- 所有 commits 位于同一个 Spec 分支。
- 未处理、跳过和阻塞 Task 有明确原因。
- 没有 push、远端 Issue、PR 或 MR。
- 仅在整个必需队列完成时推荐 `team-spec-create-pr-github` 或 `team-spec-create-mr-gitlab`。

## 最终回复

必须包含：

- slug、共享分支和批量范围。
- 本批次选择的提交模式。
- 已完成 Task 与 commit SHA。
- 当前 Task 的提交控制结果；如果尚未提交，明确说明可检查的 diff、当前状态和恢复入口。
- 失败、跳过、阻塞和剩余队列。
- 测试的新增、改写和删除、保留兼容测试的依据，以及关键验证命令和结果。
- 未提交的 `team-spec/` 回写。
- 有序号的下一步选项。
