# Skills For Real Teams

团队大语言模型技能库，面向真实软件团队的产品定义、架构理解、交付执行和技术债治理工作，并保留少量实验性 Codex Harness 能力。

它的核心目标是把模糊输入沉淀为可评审、可拆解、可实现、可验证的协作产物，而不是只提供一次性的提示词。

## 快速开始

安装全部技能：

```bash
npx skills@latest add coolbeevip/team-ai-skills --all
```

安装后，技能会在目标项目中读写运行时工作空间 `team-spec/`。本仓库只维护技能本身，不提交真实业务需求、PRD、风险报告或工程 issue。

## 技能地图

### 产品定义

把模糊需求整理成可评审、可交付的产品规格。

- `team-spec-refine`：细化需求，澄清术语、边界、业务规则和验收口径。
- `team-spec-review`：评审需求规格中的产品、交付、数据、合规、运营和协作风险。
- `team-spec-to-prd`：把 ready 的规格固化成结构化 PRD。
- `team-spec-archive`：归档已完成、废弃或暂停的需求工作区。

### 架构理解

从已有代码库中提取可追溯的系统知识，并转化为开发者或业务可读的说明。

- `team-codebase-onboarding`：生成代码库功能清单、架构说明、模块地图、API/数据/配置文档和 AI 接手上下文。
- `team-codebase-walk`：基于 onboarding 产物和源码做功能走读、问答、证据追踪和学习路径沉淀。
- `team-codebase-brief`：把代码事实转化为面向业务、产品和管理者的系统能力说明。

### 交付执行

把 PRD 拆成可领取 issue，并推动实现、验证、发布到代码协作平台。

- `team-prd-to-alignment`：把 AI 结构化 PRD 转换为适合人类评审的对齐材料。
- `team-prd-to-issues`：把 PRD 拆解为可独立领取、可验证、按依赖排序的工程 issue。
- `team-issue-publish-github`：将本地 issue 草稿发布到 GitHub Issues，并回写发布结果。
- `team-issue-publish-gitlab`：将本地 issue 草稿发布到 GitLab Issues，并回写发布结果。
- `team-issue-batch-implement`：按依赖顺序批量编排多个 AFK issue 的实现与验证。
- `team-issue-implement`：围绕单个 issue 用行为测试和 TDD 循环完成代码与测试变更。
- `team-issue-verify`：独立验证实现是否满足 issue、PRD 和风险约束。
- `team-issue-create-pr-github`：推送已完成分支并创建关联 issue 的 GitHub Pull Request。
- `team-issue-create-mr-gitlab`：推送已完成分支并创建关联 issue 的 GitLab Merge Request。

### 技术债治理

把“需要重构”“系统不稳定”“维护成本高”等诉求转成有证据、有优先级、有验收口径的工程工作。

- `team-tech-debt-analyze`：只读分析项目或模块，输出证据化技术债候选清单。
- `team-tech-debt-refine`：细化技术债需求，明确证据、影响范围、风险等级和验收标准。
- `team-tech-debt-review`：评审技术债规格的风险、优先级、阻塞项和可执行性。
- `team-tech-debt-to-issues`：把已评审技术债拆解为可独立领取的工程 issue。

### 实验能力：Codex Harness

Codex Harness 仍处于实验阶段，用于探索 Codex 在具体项目中的运行时检索层和工程执行入口。默认不作为主线流程前置条件；只有当团队已经遇到入口约束、验证方式或失败记忆不清晰的问题时，再按需使用。

- `team-codex-harness`：沉淀项目入口约束、失败记忆、验证 harness、任务入口和最小运行时配置。
- `team-skill-evolve`：根据真实反馈复盘团队技能问题，并在授权后更新技能说明、脚本或触发条件。

## 推荐流程

产品需求链路：

```text
team-spec-refine
  -> team-spec-review
  -> team-spec-to-prd
  -> team-prd-to-alignment
  -> team-prd-to-issues
  -> team-issue-publish-github / team-issue-publish-gitlab
  -> team-issue-implement
  -> team-issue-verify
  -> team-issue-create-pr-github / team-issue-create-mr-gitlab
```

技术债链路：

```text
team-tech-debt-analyze
  -> team-tech-debt-refine
  -> team-tech-debt-review
  -> team-tech-debt-to-issues
  -> team-issue-implement
  -> team-issue-verify
```

代码库理解链路：

```text
team-codebase-onboarding
  -> team-codebase-walk
  -> team-codebase-brief
```

需求完成、暂停或废弃后，使用 `team-spec-archive` 归档对应 slug。Codex Harness 不在稳定主线内；当工程入口、验证方式、失败记忆或 Codex 运行约束不清晰时，可实验性使用 `team-codex-harness` 补齐项目级运行时上下文。

## 运行时工作空间

技能默认在目标项目根目录创建或维护 `team-spec/`：

```text
team-spec/
├── CONTEXT.md
├── decisions/
├── active/
│   └── {yyyy-mm-dd-short-slug}/
│       ├── spec/
│       │   ├── CONTEXT.md
│       │   ├── decisions/
│       │   ├── refine.md
│       │   └── reviews.md
│       ├── prd/
│       │   ├── prd.md
│       │   └── alignment.md
│       ├── issues/
│       ├── design/
│       │   └── functional-design.md
│       └── STATUS.md
└── archive/
    └── {slug}/
        ├── spec/
        ├── prd/
        ├── issues/
        ├── design/
        ├── STATUS.md
        └── ARCHIVE.md
```

每个需求使用唯一 slug 串联全流程，格式为 `{yyyy-mm-dd}-{short-english-slug}`，例如 `2026-05-10-export-filter`。`team-spec/active/` 可以同时存在多个未归档 slug；只有无法唯一确定目标 slug 或文件路径时，技能才应要求用户确认。

下游技能默认读取同一 slug 的上游产物。例如 `team-prd-to-issues` 以 `team-spec/active/{slug}/prd/prd.md` 为主输入，并参考全局上下文、产品决策、规格上下文和评审报告。
