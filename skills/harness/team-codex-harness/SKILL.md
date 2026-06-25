---
name: team-codex-harness
description: 为具体代码项目维护 Codex 运行时检索层、入口约束、失败记忆和验证 harness。Maintain a Codex runtime retrieval layer, entry constraints, failure memory, and verification harness for a concrete code project.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 维护 Codex harness
  - 改进 AGENTS.md
  - Codex 不知道怎么验证
  - 沉淀 Codex 失败记忆
  - Codex 找不到任务入口
  - Codex 需要入口约束
  - Codex 需要配置引导
  - maintain Codex harness
  - improve AGENTS.md
  - Codex failure memory
  - Codex verification harness
  - Codex task entry points
  - Codex entry constraints
  - Codex runtime config
---

# Codex Harness 维护

这个技能用于维护具体代码项目里的 Codex 运行时检索层。它不是项目制度文档，也不是架构说明书，而是在 Codex 执行任务时提供少量、稳定、可检索的辅助信息，帮助 Codex 快速查到自己推不出来但会影响正确性的项目事实。

Codex harness 应该优先“检索友好”，而不是“阅读友好”。不要写长篇说明，不要追求完整叙事，不要把项目文档重写一遍。每条内容都应回答一个运行时问题：Codex 现在该避开什么、先查什么、跑什么、从哪里开始。

## 触发边界

- 适合触发：用户要为某个业务代码项目维护 Codex 入口约束、失败记忆、验证 harness、任务入口或最小运行时配置。
- 不适合触发：用户要改进本团队技能库本身时，转交 `team-skill-evolve`；用户要生成完整架构或业务说明时，转交对应架构技能。

## 职责边界

本技能只维护 4 类高价值信息：

1. 入口约束（Entry Constraints）：Codex 进入项目后必须立即知道、且无法靠浏览代码稳定推断的硬约束。
2. 失败记忆（Failure Memory）：真实发生过、可复用、会影响后续任务判断的失败模式。
3. 验证 Harness（Verification Harness）：不同变更类型完成后，如何证明没有破坏项目行为。
4. 项目任务入口（Task Entry）：常见任务应该从哪些代码、测试、脚本或文档入口开始。

本技能不负责：

- 维护本团队技能库自身；技能定义、触发词、脚本和流程演进应使用 `team-skill-evolve`。
- 写 PRD、拆 issue、实现 issue、验证 issue 或发布 issue。
- 生成完整架构设计说明书；需要面向评审的功能设计时应使用架构类技能。
- 整理普通项目文档、会议纪要、一次性任务日志或人类知识库。
- 维护完整编码规范、评审制度、团队流程或长期决策记录。
- 在没有真实代码、命令、任务或失败证据时凭空编写注意事项。
- 维护 `CLAUDE.md` 作为核心输出；如果项目已有 `CLAUDE.md`，只能作为兼容入口链接到同一套 Codex harness。

## 运行时配置

Codex harness 独立于需求、PRD、issue 拆解或技术债流程，但可以读取目标项目根目录下的 `team-spec/config.yml` 作为运行时配置入口。该配置只服务于 Codex 的运行时决策，不替代需求文档，也不承载业务知识库。

当目标项目需要统一语言、版本管理信息或目录访问策略时，优先按 `team-spec/config.yml` 汇总这些机器可读入口，再把它们注入后续技能的提示词和执行上下文。

如果 `team-spec/config.yml` 不存在，且本轮任务涉及需要稳定复用的运行时偏好或访问边界，先询问用户是否要创建最小配置文件；只收集本轮必须的最少字段，不把一次性偏好写成长期规则。

推荐的最小结构如下：

```yml
language: zh-CN
version_control:
  system: git
access_policy:
  mode: default-readonly
  directory_file: team-spec/access_policy/default.md
  user_file_template: team-spec/access_policy/{user_name}.md
```

`access_policy` 只作为目录访问策略的索引，不把长篇规则直接塞进 `config.yml`。具体权限正文建议拆到 `team-spec/access_policy/default.md` 和按协作者命名的策略文件中。

Harness 目录识别规则：

- 优先从现有 `AGENTS.md` 中识别已链接的 Codex harness 目录。
- 如果项目没有现成目录，应使用项目内独立目录保存 harness 文件，优先选择 `docs/codex-harness/`。
- 如果项目已经有 `docs/agent-harness/` 等等价目录，可以继续沿用，不为改名而制造迁移。
- 目录必须是相对项目根目录的路径，不应是绝对路径，不应位于需求、PRD、issue 或归档工作区下。
- 如果无法从现有文件唯一判断目录，只问用户一个问题确认 harness 目录，不展开多轮访谈。

执行要求：

- 对话回复与 harness 文件默认沿用项目现有语言；若无法判断，优先使用用户本轮语言。
- 用户临时切换语言时，本次立即生效；只有用户明确要求持久化语言偏好时，才写入 harness 文件。
- 除非用户明确说“只分析、不改文件”，否则本技能默认应该产出或更新目标项目中的持久化 harness 输出物，或给出最小运行时配置建议。

## 输入物

- 目标项目根目录的 `AGENTS.md`，以及已有 `CLAUDE.md`、`README.md`、`docs/`、开发手册、测试说明和运维说明。
- 当前项目的真实代码、目录结构、构建配置、测试配置、脚本、CI 配置和本地开发工具。
- Codex 最近执行真实任务时遇到的卡点、失败测试、CI 日志、命令错误、人工修复记录或交付事故。
- 已有 Codex harness 目录，例如 `docs/codex-harness/` 或项目现有等价目录。
- 可选：来自 `team-prd-to-issues`、`team-issue-implement` 或 `team-issue-verify` 的真实工程任务反馈，但本技能只把其中与 Codex 运行时检索相关的部分写入 harness。

如果用户没有提供明确范围，应先判断本轮是在初始化检索层、补失败记忆、补验证策略、补任务入口，还是刷新入口约束。无法唯一判断时，只问一个最关键的问题。

## 输出物

本技能默认只维护 `AGENTS.md` 和 4 个核心检索文件。不要为了完整性新增其他制度性文档。

- `AGENTS.md`：Codex 的入口路由，只说明本项目必须遵守的最高优先级规则，以及 4 个检索文件在哪里。
- `{harness_dir}/entry-constraints.md`：入口约束，记录 Codex 自己推不出来的硬约束。
- `{harness_dir}/failure-memory.md`：失败记忆，记录真实失败模式和恢复方式。
- `{harness_dir}/verification-harness.md`：验证 harness，记录不同变更类型的最低验证路径。
- `{harness_dir}/task-entry.md`：任务入口，记录常见任务从哪里开始。
- `team-spec/config.yml`：最小运行时配置索引，记录语言、版本管理和目录访问策略的入口文件。

不建议新增：

- `project-map.md`：容易变成架构文档；必要内容应压缩进 `task-entry.md`。
- `commands.md`：普通命令价值低；只有约束型命令进入 `entry-constraints.md`，验证型命令进入 `verification-harness.md`。
- `coding-rules.md`：容易变成制度；只有不可推导的硬约束进入 `entry-constraints.md`。
- `review-rubric.md`：容易空泛；收尾检查应体现在 `verification-harness.md`。
- `decisions.md`：不是运行时检索核心；除非用户明确要求记录 harness 目录迁移取舍，否则不要创建。
- `{harness_dir}/index.md`：默认不需要；`AGENTS.md` 直接索引 4 个核心文件。如果项目已有 `index.md`，可以保留为兼容索引，但不要把它变成第五类知识。
- `team-spec/access_policy/*.md`：目录访问策略正文，如果项目需要按协作者区分读取/写入边界，可以在这里存放具体规则。

落盘规则：

- 初始化 Codex harness：至少创建或更新 `AGENTS.md`，并创建 4 个核心检索文件中有真实证据支撑的文件；没有证据的文件可以只放标题和“暂无记录”。
- 初始化运行时配置：如果用户同意创建配置，补写 `team-spec/config.yml` 的最小字段，并在需要时补充 `team-spec/access_policy/default.md` 或协作者策略文件的路径约定。
- 更新入口约束：只更新 `entry-constraints.md` 和 `AGENTS.md` 中必要的路由。
- 更新失败记忆：只更新 `failure-memory.md`；如果失败暴露验证缺口，再同步更新 `verification-harness.md`。
- 更新验证策略：只更新 `verification-harness.md`。
- 更新任务入口：只更新 `task-entry.md`。
- 只分析模式：用户明确要求不改文件时，只输出问题定位、建议改动和建议验证方式。

## 四类信息的写法

### 入口约束

`entry-constraints.md` 只放 Codex 必须提前知道的硬约束。每条建议使用短块格式：

```md
## {constraint-title}

- Scope: {适用目录、命令、文件或任务类型}
- Rule: {必须遵守或禁止事项}
- Reason: {为什么 Codex 不能靠推断得到}
- Source: {代码、配置、CI、README、人工确认或失败记录}
- Last checked: {YYYY-MM-DD 或 待验证}
```

适合写入：

- 哪些目录不能动。
- 哪些生成文件不要手改。
- 哪些命令必须在哪个目录运行。
- 哪些测试特别慢，不应默认全量跑。
- 哪些 CI 有本地不可见的隐藏依赖。

不适合写入：

- 通用编码风格。
- 可以从 lint、formatter、类型检查或代码惯例推断出的规则。
- 没有证据的偏好。

### 失败记忆

`failure-memory.md` 是最高价值文件，只记录真实失败。每条建议使用短块格式：

```md
## {observable-symptom}

- Trigger: {触发条件或命令}
- Symptom: {可观察现象}
- Root cause: {已确认根因；不确定时写 待确认}
- Fix or workaround: {正确处理方式}
- Check first next time: {下次优先检查点}
- Evidence: {日志、CI、PR、任务、人工修复记录}
- Last confirmed: {YYYY-MM-DD 或 待验证}
```

失败记忆必须来自真实任务、测试、CI、用户纠正或人工修复记录。不要写“可能会失败”“注意某某”这类泛化提醒。

### 验证 Harness

`verification-harness.md` 只回答“改完后如何证明没坏”。每条建议按变更类型组织：

```md
## {change-type}

- Applies when: {哪些文件、模块、接口或行为变化时适用}
- Minimum verification: {最低必须执行的命令或人工检查}
- Stronger verification: {高风险时追加的检查}
- Known blind spots: {本地验证覆盖不到但 CI 或线上会暴露的问题}
- Evidence: {测试配置、CI、脚本、历史失败或人工确认}
- Last checked: {YYYY-MM-DD 或 待验证}
```

适合写入：

- 改 API 必跑什么。
- 改 MQTT 必跑什么。
- 改数据库 migration 必查什么。
- 改配置、本地过测但 CI 可能失败的场景。
- 哪些验证很慢，应在什么风险级别才跑。

不要把所有测试命令平铺成命令列表。命令必须绑定到变更类型和证明目标。

### 项目任务入口

`task-entry.md` 只回答“这类任务从哪里开始”。每条建议使用短块格式：

```md
## {task-type}

- Start here: {首要代码、测试、脚本或文档入口}
- Then check: {第二层入口，最多 3 项}
- Avoid: {容易误入或不该先改的地方}
- Validation link: {对应 verification-harness.md 的章节}
- Evidence: {代码结构、测试、README、历史任务或人工确认}
- Last checked: {YYYY-MM-DD 或 待验证}
```

适合写入：

- 新增 API 从哪里开始。
- 新增 skill 从哪里开始。
- 新增 migration 从哪里开始。
- 修改某类配置、协议、任务队列、前端页面或部署流程从哪里开始。

不要写完整架构地图。任务入口最多给 Codex 第一跳和第二跳。

## 工作流

1. 识别本轮目标：初始化检索层、更新入口约束、记录失败记忆、补验证 harness、补任务入口，或刷新过期内容。
2. 读取 `AGENTS.md`、已有 harness 文件、相关代码、配置、脚本、测试、CI 和真实任务反馈。
3. 判断要写入的信息是否属于 4 类之一；不属于则不要写入 harness。
4. 判断 Codex 是否能靠代码和工具自己推出来；能推出来的普通信息不要写入。
5. 判断是否有证据；没有证据时只可标注 `待验证`，不得写成确定事实。
6. 用短块格式更新最小必要文件，避免长篇叙述和重复项目文档。
7. 更新 `AGENTS.md` 中的路由，确保 Codex 能找到 4 个核心检索文件。
8. 用一个真实任务或失败案例检查：Codex 是否能通过检索文件更快找到约束、失败、验证或任务入口。

## 检索友好规则

- 每个小节标题必须像查询词，而不是文章标题。
- 每条记录应短，优先使用固定字段，方便 Codex 扫描和匹配。
- 同一事实只放在一个文件；其他文件用章节名引用，不重复解释。
- 不写历史叙事、背景故事、制度解释或长篇原则。
- 不把所有命令集中成清单；命令必须服务于入口约束或验证策略。
- 不把所有模块集中成地图；路径必须服务于任务入口。
- 旧内容过期时直接改写、删除或标注历史状态，不无限追加。

## 证据规则

写入 Codex harness 的内容必须能追溯到证据来源：

- 强证据：当前代码、测试、CI 配置、构建配置、脚本、锁文件、类型配置、lint/format 配置。
- 中证据：README、架构文档、开发手册、运维说明、团队维护的正式文档。
- 弱证据：历史对话、一次性任务记录、人工经验、未复现的失败描述。
- 未验证内容：无法从强证据或中证据确认的命令、路径、规则或判断，必须标注为 `待验证`。

如果代码、配置、测试、脚本或 CI 与 harness 冲突，优先相信当前工程事实，并修正 harness。无法判断哪一方正确时，不要合并成模糊规则，应标注为 `待确认`，并说明需要用户或维护者确认的问题。

## 自检要求

每次修改 Codex harness 后，必须轻量自检：

- `AGENTS.md` 是否只做入口路由，并能指向 4 个核心检索文件。
- 新增内容是否属于入口约束、失败记忆、验证 harness 或任务入口之一。
- 新增内容是否是 Codex 难以自行推断、但会影响正确性的事实。
- 新增记录是否使用固定字段，适合快速检索。
- 新增命令是否绑定到约束或验证目标，而不是普通命令清单。
- 新增路径是否绑定到任务入口，而不是完整架构地图。
- 是否引入敏感信息、绝对本机路径、个人凭证或一次性任务噪音。
- 是否需要删除、废弃或标注过期内容，而不是只追加新内容。

## 与其他技能的关系

- `team-skill-evolve`：维护团队技能库自身。Codex harness 技能定义、触发词、脚本或流程需要修改时，使用它。
- `team-prd-to-issues`：拆 PRD 时如果发现入口约束、验证策略或任务入口不清楚，可以转入本技能补 harness。
- `team-issue-implement` / `team-issue-verify`：真实实现或验证暴露的失败记忆、验证盲区和任务入口缺口，可以反馈给本技能。
