# Skills For Real Teams

面向产品负责人、研发负责人、开发者和项目管理者的团队 AI 技能库，覆盖产品定义、代码库理解、交付执行和技术债治理，并保留少量实验性 Codex Harness 能力。

它不是一次性提示词合集，而是让不同 skills 按职责接力，把模糊输入沉淀为可评审、可拆解、可实现、可验证的文件化协作产物。

[项目网站](https://coolbeevip.github.io/team-ai-skills/) · [GitHub 仓库](https://github.com/coolbeevip/team-ai-skills)

## 快速开始

开始前需要：

- 可运行 `npx` 的 Node.js/npm 环境。
- 能够加载已安装 skill 的 AI 编码客户端。不同客户端的显式调用语法可能不同。

### 1. 安装技能

在目标项目中，选择正在使用的 AI 编码客户端安装全部技能。

Codex：

```bash
npx skills@latest add coolbeevip/team-ai-skills --agent codex -y
```

Claude Code：

```bash
npx skills@latest add coolbeevip/team-ai-skills --agent claude-code -y
```

安装命令需要访问网络并下载外部包。

### 2. 调用第一个技能

安装完成后，可以直接用自然语言指定技能和任务，避免绑定某个客户端的调用语法：

```text
使用 team-spec-refine，帮我细化“导出结果增加筛选条件”的需求。
```

`team-spec-refine` 会先确认语言、需求边界和唯一 slug。规格细化完成后，可以在目标项目中看到类似产物：

```text
team-spec/
├── config.yml
└── active/
    └── 2026-05-10-export-filter/
        └── spec/
            └── refine.md
```

产品、交付、代码库理解和技术债主线通常在目标项目的 `team-spec/` 中读写运行时产物；`team-codebase-readme` 等局部技能会直接处理用户指定的文件，不要求创建需求 slug。

> 本仓库只维护技能本身。真实业务需求、PRD、风险报告和工程 issue 应保留在安装技能的目标项目中，不要提交到本仓库。

## 推荐流程

### 产品需求主线

```text
team-spec-refine
  -> team-spec-review
  -> team-spec-to-prd
  -> team-prd-to-issues
  -> team-issue-implement / team-issue-batch-implement
  -> team-issue-verify
```

以下步骤按场景使用，不是主线的强制前置条件：

- 产品规划阶段需要先明确定位和能力边界时，在 `team-spec-refine` 前使用 `team-concept-whitepaper`。
- PRD 需要转成人类评审会材料时，使用 `team-prd-to-alignment`。
- 本地 issue 草稿需要发布到远端时，选择 `team-issue-publish-github` 或 `team-issue-publish-gitlab`。
- 实现验证通过后需要交付代码评审时，选择 `team-issue-create-pr-github` 或 `team-issue-create-mr-gitlab`。
- 需求完成、暂停或废弃后，使用 `team-spec-archive` 归档对应 slug。

### 技术债主线

```text
team-tech-debt-analyze
  -> team-tech-debt-refine
  -> team-tech-debt-review
  -> team-tech-debt-to-issues
  -> team-issue-implement / team-issue-batch-implement
  -> team-issue-verify
```

技术债生成 issue 后，可以复用产品需求主线中的远端发布和 PR/MR 交付技能。

### 代码库理解与说明

```text
team-codebase-onboarding
  -> team-codebase-walk
  -> team-codebase-brief
```

`team-codebase-readme` 是并列能力：它直接基于项目事实创建、审阅或优化项目 README，不依赖 onboarding 产物。

Codex Harness 不在稳定主线内。只有当项目的工程入口、验证方式、失败记忆或 Codex 运行约束不清晰时，再按需使用。

## 技能地图

技能按团队职责分为以下五组。

### 产品定义

从产品概念规划开始，把模糊想法逐步整理成可评审、可交付的产品规格。

- `team-concept-whitepaper`：定义产品机会、定位、价值、能力边界和演进方向，形成可评审的概念白皮书。
- `team-spec-refine`：通过用户确认细化需求，澄清术语、范围、业务规则和验收口径。
- `team-spec-review`：评审已细化规格的风险、阻塞项、补救动作和 ready 状态。
- `team-spec-to-prd`：把已细化并通过评审的规格固化成结构化 PRD。
- `team-spec-archive`：归档已完成、废弃或暂停的需求工作区。

### 代码库理解与说明

从代码和仓库事实中提取可追溯知识，并转化为开发者、业务或项目访问者需要的说明。

- `team-codebase-onboarding`：默认生成代码库功能清单、架构说明、模块地图和 AI 接手知识库；用户明确要求时可额外导出 `docs/` 文档集。
- `team-codebase-walk`：基于 onboarding 产物和源码进行功能走读、问答、证据追踪和学习路径沉淀。
- `team-codebase-brief`：把代码库事实转化为面向业务、产品和管理者的能力说明、场景材料和影响分析。
- `team-codebase-readme`：为团队自有项目创建、审阅和优化准确、易扫描的 README。

### 交付执行

把 PRD 拆成可领取的 issue，并推动实现、验证和代码协作平台交付。

- `team-prd-to-alignment`：把结构化 PRD 转换为适合需求、研发和项目管理评审的对齐材料。
- `team-prd-to-issues`：把 PRD 拆解为可独立领取、可验证、按依赖排序的端到端工程 issue。
- `team-issue-publish-github`：将本地 issue 草稿发布到 GitHub Issues，并回写发布结果。
- `team-issue-publish-gitlab`：将本地 issue 草稿发布到 GitLab Issues，并回写发布结果。
- `team-issue-batch-implement`：按依赖顺序批量编排多个可自主执行 issue 的实现与验证，并支持失败即停和恢复续跑。
- `team-issue-implement`：围绕单个 issue 使用行为测试、TDD、现有代码复用和最小实现模式完成变更。
- `team-issue-verify`：独立验证单个 issue 的实现是否满足验收标准、PRD、风险和最小实现要求。
- `team-issue-create-pr-github`：推送已完成的 issue 分支并创建关联 issue 的 GitHub Pull Request。
- `team-issue-create-mr-gitlab`：推送已完成的 issue 分支并创建关联 issue 的 GitLab Merge Request。

### 技术债治理

把“需要重构”“系统不稳定”“维护成本高”等诉求转换成有证据、有优先级、有验收口径的工程工作。

- `team-tech-debt-analyze`：只读分析项目或模块，输出有证据的维护性、稳定性、测试、架构和交付风险。
- `team-tech-debt-refine`：通过用户确认细化技术债需求，明确证据、影响范围、风险等级和验收口径。
- `team-tech-debt-review`：评审技术债规格的风险、优先级、阻塞项和工程拆解 ready 状态。
- `team-tech-debt-to-issues`：把已评审的技术债规格拆解为可独立领取、可验证、按依赖排序的工程 issue。

### 实验能力：Codex Harness

- `team-codex-harness`：维护具体项目的 Codex 运行时检索层、入口约束、失败记忆和验证 harness。
- `team-skill-evolve`：根据真实反馈、失败案例和执行日志提出可审核的技能进化建议。

## 运行时工作空间

`team-spec/` 是技能安装到业务项目后的运行时工作空间。下面展示的是可能出现的常见结构；目录和文件按任务需要创建，不会在安装时一次性全部生成。

```text
team-spec/
├── config.yml                              # 语言、版本管理和访问策略入口
├── access_policy/                          # 可选：目录访问策略
│   ├── default.md
│   └── {user_name}.md
├── CONTEXT.md                              # 可选：跨需求产品语境
├── decisions/                              # 可选：跨需求长期决策
├── active/
│   └── {yyyy-mm-dd}-{short-english-slug}/
│       ├── concept/
│       │   └── whitepaper.md               # 可选：产品概念白皮书
│       ├── spec/
│       │   ├── CONTEXT.md                  # 可选：当前需求语境
│       │   ├── decisions/                  # 可选：当前需求决策
│       │   ├── refine.md
│       │   └── reviews.md
│       ├── prd/
│       │   ├── prd.md
│       │   └── alignment.md                # 可选：人类评审材料
│       ├── issues/
│       ├── design/
│       │   ├── functional-design.md        # 按需创建
│       │   ├── codebase-onboarding/        # 代码库接手知识库
│       │   └── codebase-walk/              # 代码库走读记录
│       ├── brief/
│       │   └── codebase-brief/             # 面向干系人的能力材料
│       ├── tech-debt/
│       │   └── analysis.md                 # 技术债分析报告
│       └── STATUS.md                       # 可选：工作区生命周期
└── archive/
    └── {slug}/
        ├── ...
        └── ARCHIVE.md
```

每个需求或分析工作区使用唯一 slug 串联流程，格式为 `{yyyy-mm-dd}-{short-english-slug}`，例如 `2026-05-10-export-filter`。`team-spec/active/` 可以同时存在多个未归档工作区；只有无法唯一确定目标 slug 或文件路径时，技能才会要求用户确认。

下游技能默认读取同一 slug 的上游产物。例如：

- `team-spec-refine` 可以继承同一 slug 下的 `concept/whitepaper.md`。
- `team-spec-to-prd` 读取已细化规格和评审报告。
- `team-prd-to-issues` 以 `prd/prd.md` 为主输入，并参考全局语境、产品决策、规格语境和评审报告。
- `team-codebase-walk` 读取 `design/codebase-onboarding/`，并把走读记录写入 `design/codebase-walk/`。

机器可读状态按写入位置区分：

- `active/{slug}/STATUS.md` 只记录整个工作区的生命周期。
- `spec/reviews.md` 记录 `ready`、`needs-refinement` 或 `blocked` 等阶段评审结果。
- issue 草稿记录 `draft`、`published`、`implementing`、`verified`、`pr-created` 或 `mr-created` 等交付状态。

## 参与维护

本仓库是 Markdown 技能库，没有构建系统。技能正文以中文为主，frontmatter 中的 `description` 和 `triggers` 同时覆盖中文和英文，以支持不同语言上下文中的发现和触发。

参与技能开发、运行本地检查或提交变更前，请阅读 [贡献者指南](CONTRIBUTING.md) 和仓库级 `AGENTS.md`。

常用检查：

```bash
python3 scripts/check_skills.py
pre-commit run --all-files
```

修改根目录 `scripts/_team_common.py` 后，还需要同步并检查各技能目录中的 vendored 副本：

```bash
python3 scripts/check_vendored_common.py
python3 scripts/check_vendored_common.py --check
```

## 许可证

本项目使用 [MIT License](LICENSE)。
