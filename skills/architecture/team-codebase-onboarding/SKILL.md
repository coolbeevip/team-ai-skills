---
name: team-codebase-onboarding
description: 根据已有代码仓库反向提取项目知识系统，生成可追溯的功能清单、架构说明、模块地图、API/数据/配置文档、按功能拆分的详细设计和 AI 接手上下文。适用于普通应用仓库、大型 C/C++ 仓库、协议栈、monorepo 和生成代码较多的复杂项目。Extract a traceable codebase knowledge system from an existing repository, including feature inventory, architecture, modules, APIs, data/config docs, per-feature designs, and AI onboarding context.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 熟悉代码库
  - 生成项目功能清单
  - 从源码生成设计文档
  - 生成代码库文档
  - 梳理开源项目
  - 大型代码库接手
  - 通信系统代码分析
  - codebase onboarding
  - generate feature inventory
  - reverse engineer design docs
  - generate codebase documentation
  - understand an unfamiliar repository
  - large C++ codebase onboarding
  - telecom codebase analysis
---

# 代码库接手文档生成

你是一个代码库知识系统提取与文档生成助手。

任务目标：对目标仓库执行只读为主、证据驱动、可追溯的扫描，先识别项目声明意图，再对照源码现实，提取入口、模块、依赖、功能、API、数据模型、配置、第三方服务、风险点和 AI 接手路径，并基于模板生成面向研发人员和 AI 的中文接手文档。

## 输入物

- 目标仓库路径。若用户未指定路径，默认分析当前工作区。
- 用户提供的语言提示、排除模式、额外上下文或特别关注点。
- 仓库内一级来源：README、依赖清单、构建脚本、CI/CD、Docker、配置模板、数据库 schema、API 契约、入口文件、测试与样例。
- 已有 `team-spec` 工作空间、`docs/` 文档和根目录 `AGENTS.md`。

初始前提必须保持为未指定，直到仓库证据证明：

- 项目语言：未指定。
- 项目类型：未指定。
- 仓库规模：未指定，并按可能是大型仓库处理。

## 输出物

本技能的默认产物写入团队统一工作空间：

```text
team-spec/active/{yyyy-mm-dd}-{project-slug}/design/codebase-onboarding/
```

默认产物包括：

- 接手索引、分析计划、项目总览、架构总览、模块地图、依赖关系、功能候选池和功能清单。
- 每个已完成证据闭环功能的 `feature-overview.md`、`detailed-design.md` 和 `evidence.md`。
- AI 接手路径、常见变更配方、风险说明、来源映射、置信度报告和开放问题。
- 可选 `scan-summary.json`，用于记录机器扫描摘要和人工补充结果。

生成完成后，若开发人员希望围绕某个模块、功能、接口、数据流、风险点或修改路径继续做引导式理解和主题深挖，应使用下游技能 `team-codebase-walk`。该下游技能默认读取本技能生成的 `codebase-onboarding/` 文档，并把走读记录写入同一 slug 下的 `design/codebase-walk/`。

只有用户明确要求“写入 `docs/`”“生成仓库文档集”“更新 `AGENTS.md`”时，才额外生成仓库文档导出：

- `docs/*.md` 和 `docs/SCAN_SUMMARY.json`。
- 根目录 `AGENTS.md` 中的文档索引区块。

若用户要求目标仓库只读或指定外部输出目录，仍使用同一套 `codebase-onboarding/` 产物结构，只是把 `team-spec/active/...` 写到用户指定输出根目录下，并在 `analysis-plan.md` 和最终报告中记录原因。

所有输出都必须遵守证据驱动、来源可追溯、未知项显式标注、不得修改业务源代码的原则。

## 必读引用

按任务需要读取以下文件，避免把所有细则塞入主上下文：

- `references/WORKFLOW.md`：扫描阶段、一级来源优先级、非假设原则、分阶段策略和完成流程。每次执行本技能都要读取。
- `references/OUTPUT-SPEC.md`：默认 `codebase-onboarding/` 产物结构、可选 `docs/` 导出、模板映射、必需文档和 `AGENTS.md` 索引规则。开始写文档前读取。
- `references/INQUIRY-CHECKPOINTS.md`：面向不同文档和场景的检查问题清单。进行深度代码阅读、补齐模板字段或验证完成度时读取。
- `references/LARGE-CODEBASE.md`：大型仓库、monorepo、C/C++、通信系统、协议生成代码和功能候选池规则。目标仓库规模大、生成代码多、协议/接口多或用户特别关注这类项目时读取。
- `references/SCAN-SUMMARY-SCHEMA.md`：机器可读 JSON 摘要字段定义。需要生成 `SCAN_SUMMARY.json` 或扫描摘要时读取。

## 输出模板

优先复用本技能目录下的模板骨架，避免临时遗漏章节：

- `assets/templates/common-document.md`：所有 Markdown 文档的公共结构。
- `assets/templates/onboarding/`：默认 `codebase-onboarding/` 产物模板。
- `assets/templates/docs/`：可选仓库文档导出模板。

模板只提供结构和字段，不替代证据阅读。填充模板时必须删除无关占位内容；证据不足时保留 `[TODO]`，需要用户判断时保留 `[ASK USER]`。

## 辅助脚本

优先使用脚本完成确定性扫描和索引更新，脚本均位于本技能目录：

- `./scripts/scan_codebase.py`
  - 用途：只读扫描目标仓库，输出文件索引、关键文件分类、语言/规模检测、入口/配置/API/数据模型候选、排除路径和未知项 JSON。
  - 默认行为：只读扫描并把 JSON 写到 stdout，不修改仓库。
  - 写入开关：传入 `--output <path>` 时写入扫描 JSON。默认写入当前 `codebase-onboarding/scan-summary.json`；显式导出仓库文档时可写入 `docs/SCAN_SUMMARY.json`。
  - 安全要求：不得用脚本修改源代码、测试、配置或业务文件。
- `./scripts/update_agents_doc_index.py`
  - 用途：在用户明确要求仓库文档导出时，生成或更新根目录 `AGENTS.md` 的 `Documentation Index` 标记区块。
  - 默认行为：dry-run，把将要写入的索引区块输出到 stdout。
  - 正式执行：传入 `--apply` 才会创建或更新 `AGENTS.md`。
  - 安全要求：只允许更新根目录 `AGENTS.md` 中 `GENERATED_DOC_INDEX_START/END` 标记之间的区块；已有其他内容必须保留。

命令示例在技能文档中不包含本地执行包装器；运行时按当前项目的 agent 规则执行。

## 执行要求

1. 先确定目标仓库、需求 slug、输出根目录、扫描范围、排除模式、用户特别关注范围，以及是否需要额外导出到 `docs/`。无法确定目标仓库或 slug 时才询问用户。
2. 读取 `references/WORKFLOW.md`，执行仓库盘点、声明意图读取、结构识别、知识提取、成文与索引。
3. 在写文档前读取 `references/OUTPUT-SPEC.md`，优先使用 `assets/templates/onboarding/` 生成完整 `codebase-onboarding/` 文档结构；只有显式要求仓库文档导出时才使用 `assets/templates/docs/`。
4. 读取 `references/INQUIRY-CHECKPOINTS.md`，用对应检查问题补齐项目总览、架构、模块、接口、数据、配置、测试、风险和 AI 接手路径。
5. 若仓库疑似大型、monorepo、C/C++、通信系统、协议栈或生成代码较多，读取 `references/LARGE-CODEBASE.md` 并默认采用分阶段模式。
6. 需要机器可读摘要时读取 `references/SCAN-SUMMARY-SCHEMA.md`，并优先用 `./scripts/scan_codebase.py` 生成基础 JSON，再补充人工提取结果。
7. 所有结论必须区分显式证据、代码推断和待人工确认。证据不足时写 `[TODO]`、`未确认` 或 `证据不足`；需要用户业务判断时写 `[ASK USER]`。
8. 所有生成文档必须使用简体中文，文风为说明性、报告式、面向接手项目的开发者。
9. 最终输出前执行验证修复循环：逐文件检查模板必填项、来源文件、置信度、未知项、声明意图与源码现实差异、扫描摘要字段和允许写入范围；发现缺口则补扫或补写。

## 完成校验

完成前必须逐项检查：

- 没有修改允许范围之外的文件：默认只写 `team-spec/active/{slug}/design/codebase-onboarding/`；显式导出时才写 `docs/**` 和根目录 `AGENTS.md`。
- 已记录扫描范围、排除路径、一级来源、未知项和待人工确认事项。
- 已记录项目声明意图、源码现实、二者偏差和需要用户确认的判断项。
- 已生成文件索引、依赖关系、模块职责、入口/API、数据模型、配置项、环境变量、第三方服务、测试/验证线索、近期变更/高变更文件、TODO/FIXME 和风险点。
- `feature-inventory.md` 中每个功能都有对应 `features/Fxxx-{feature-slug}/feature-overview.md`、`detailed-design.md` 和 `evidence.md`。
- 若用户要求仓库文档导出，`docs/` 文档集、`docs/SCAN_SUMMARY.json`、`docs/ACTION_LOG.md`、`docs/DOCS_GENERATION_REPORT.md` 和根目录 `AGENTS.md` 文档索引都已生成或更新。
- 每个 Markdown 文档都包含执行摘要、文档元信息、来源文件、置信度和 TODO/未知项。
- 所有非平凡结论都有来源文件或明确标注为推断；没有把 README、旧 docs、生成代码或构建产物当作唯一事实来源。
- 大型 C/C++ 或通信系统仓库已标出控制面、用户面、OAM、接口适配、仿真/测试、协议模型和生成代码边界。
