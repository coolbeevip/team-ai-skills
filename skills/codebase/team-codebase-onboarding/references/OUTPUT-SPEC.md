# 输出规范

## 目录

- 1. 输出原则
- 2. 默认产物目录
- 3. 默认文档结构
- 4. 模板映射
- 5. 可选仓库文档导出
- 6. 通用 Markdown 合同
- 7. 来源文件引用规则
- 8. 完成校验

## 1. 输出原则

`team-spec/` 是团队所有技能共享的产物根路径，不是本技能的一个“模式”。本技能默认只在目标项目或用户指定输出根目录下写入：

```text
team-spec/active/{slug}/design/codebase-onboarding/
```

除非用户明确要求，否则不要写入目标仓库 `docs/` 或根目录 `AGENTS.md`。

输出必须遵守：

- 只写允许范围内的文档和扫描摘要，不修改业务源代码、测试、构建配置、部署配置或迁移脚本。
- 所有结论区分显式证据、代码推断、约定性猜测和待人工确认。
- 证据不足写 `[TODO]`、`未确认` 或 `证据不足`。
- 需要用户业务判断或外部系统信息时写 `[ASK USER]`。
- 命令示例必须来自仓库证据；推测命令必须标注“推测”。

## 2. 默认产物目录

默认写入：

```text
team-spec/active/{yyyy-mm-dd}-{project-slug}/design/codebase-onboarding/
```

若用户指定 slug，使用用户指定 slug。若用户未指定 slug，根据目标项目名称生成 `{yyyy-mm-dd}-{project-slug}`；无法唯一判断项目名称时询问用户。

若用户要求目标仓库只读、禁止写入目标仓库，或要求写到外部目录，则在用户指定输出根目录下创建同样的 `team-spec/active/{slug}/design/codebase-onboarding/` 结构，并在 `analysis-plan.md`、`index.md` 和最终回复中说明：

- 目标仓库路径。
- 外置输出根目录。
- 未向目标仓库写入文件的约束。
- 与默认输出位置不一致的原因。

## 3. 默认文档结构

默认产物结构：

```text
codebase-onboarding/
├── index.md
├── analysis-plan.md
├── project-overview.md
├── architecture-overview.md
├── feature-candidates.md
├── feature-inventory.md
├── scan-summary.json
├── domain/
│   ├── glossary.md
│   └── protocol-inventory.md
├── modules/
│   ├── module-map.md
│   └── dependency-map.md
├── features/
│   └── F001-{feature-slug}/
│       ├── feature-overview.md
│       ├── detailed-design.md
│       └── evidence.md
├── ai-onboarding/
│   ├── reading-path.md
│   ├── change-recipes.md
│   └── risk-notes.md
└── traceability/
    ├── source-map.md
    ├── confidence-report.md
    └── open-questions.md
```

`feature-candidates.md` 是候选层。候选功能只表示“值得展开”，不能冒充已完成详细设计。

`feature-inventory.md` 是完成层。每个进入 `feature-inventory.md` 的功能必须创建：

- `features/Fxxx-{feature-slug}/feature-overview.md`
- `features/Fxxx-{feature-slug}/detailed-design.md`
- `features/Fxxx-{feature-slug}/evidence.md`

`feature-inventory.md` 至少包含：

| 功能编号 | 功能域 | 功能名称 | 功能说明 | 入口 | 主要源码 | 详细设计 | 证据 | 可信度 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## 4. 模板映射

模板位于本技能目录的 `assets/templates/`，用于降低遗漏章节风险。模板是骨架，不是事实来源；填充时必须删除无关占位。

默认产物使用 `assets/templates/onboarding/`：

| 输出文件 | 模板 |
| --- | --- |
| `index.md` | `assets/templates/onboarding/index.md` |
| `analysis-plan.md` | `assets/templates/onboarding/analysis-plan.md` |
| `project-overview.md` | `assets/templates/onboarding/project-overview.md` |
| `architecture-overview.md` | `assets/templates/onboarding/architecture-overview.md` |
| `feature-candidates.md` | `assets/templates/onboarding/feature-candidates.md` |
| `feature-inventory.md` | `assets/templates/onboarding/feature-inventory.md` |
| `domain/glossary.md` | `assets/templates/onboarding/glossary.md` |
| `domain/protocol-inventory.md` | `assets/templates/onboarding/protocol-inventory.md` |
| `modules/module-map.md` | `assets/templates/onboarding/module-map.md` |
| `modules/dependency-map.md` | `assets/templates/onboarding/dependency-map.md` |
| `features/Fxxx-*/feature-overview.md` | `assets/templates/onboarding/feature-overview.md` |
| `features/Fxxx-*/detailed-design.md` | `assets/templates/onboarding/detailed-design.md` |
| `features/Fxxx-*/evidence.md` | `assets/templates/onboarding/evidence.md` |
| `ai-onboarding/reading-path.md` | `assets/templates/onboarding/reading-path.md` |
| `ai-onboarding/change-recipes.md` | `assets/templates/onboarding/change-recipes.md` |
| `ai-onboarding/risk-notes.md` | `assets/templates/onboarding/risk-notes.md` |
| `traceability/source-map.md` | `assets/templates/onboarding/source-map.md` |
| `traceability/confidence-report.md` | `assets/templates/onboarding/confidence-report.md` |
| `traceability/open-questions.md` | `assets/templates/onboarding/open-questions.md` |

`assets/templates/common-document.md` 是通用 Markdown 骨架。只有用户明确要求仓库文档导出时，才使用 `assets/templates/docs/`。

## 5. 可选仓库文档导出

仓库文档导出只在用户明确要求以下任一项时执行：

- 将结果写入 `docs/`。
- 创建或更新根目录 `AGENTS.md`。
- 生成仓库文档集、文件索引、依赖图、配置参考或第三方服务文档。
- 使用“只允许修改 `docs/**` 和根目录 `AGENTS.md`”这类约束。

导出时只允许修改目标项目 `docs/**` 和根目录 `AGENTS.md`。默认 `codebase-onboarding/` 产物仍然是团队技能工作流的主产物；若用户只要求 `docs/`，必须在最终回复中说明未生成默认团队工作空间产物的原因。

建议导出文件：

- `docs/README-overview.md`
- `docs/ARCHITECTURE.md`
- `docs/MODULES.md`
- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/SETUP.md`
- `docs/DEBUGGING.md`
- `docs/CONTRIBUTING.md`
- `docs/CHANGELOG_GUIDE.md`
- `docs/FILE_INDEX.md`
- `docs/DEPENDENCY_GRAPH.md`
- `docs/CONFIG_REFERENCE.md`
- `docs/THIRD_PARTY_SERVICES.md`
- `docs/DOCS_GENERATION_REPORT.md`
- `docs/ACTION_LOG.md`
- `docs/SCAN_SUMMARY.json`

若某类内容不存在，例如没有第三方服务或没有数据库 schema，也要创建对应文档并写明“未检测到”“证据不足”或“待人工确认”。

若更新 `AGENTS.md`，只能新增或更新以下标记区块，保留其他内容：

```md
## Documentation Index
<!-- GENERATED_DOC_INDEX_START -->
| 文件名 | 路径 | 简短描述 | 最后更新 | 置信度 |
| --- | --- | --- | --- | --- |
<!-- GENERATED_DOC_INDEX_END -->
```

建议用 `./scripts/update_agents_doc_index.py --apply` 做确定性更新。

## 6. 通用 Markdown 合同

每个 Markdown 文档必须包含：

```md
# 文档标题

## 执行摘要
用 5~12 行说明本文件告诉读者什么、最重要结论是什么、哪些结论高置信、哪些仍待确认。

## 文档元信息
| 字段 | 内容 |
| --- | --- |
| 用途 | |
| 读者 | |
| 生成日期 | YYYY-MM-DD |
| 置信度 | 高 / 中 / 低 |
| 扫描范围 | |
| 是否包含推断 | 是 / 否 |
| 声明意图来源 | |
| 源码现实来源 | |

## 正文
按文档类型组织内容。

## 来源文件
| 路径 | 关键符号/对象 | 用途 | 备注 |
| --- | --- | --- | --- |

## TODO / 未知项
- [TODO] ...

## 需要用户确认
- [ASK USER] ...
```

能画图时优先使用 Mermaid。图中的关系也必须来自证据或标注为推断。

## 7. 来源文件引用规则

每个文档都必须有“来源文件”区，并尽量提供：

- 仓库相对路径。
- 关键符号名，例如类、函数、路由、schema、task 名。
- 引用用途。
- 稳定行号。若行号不稳定，只写路径与符号。

总览或报告类文档必须记录：

- `声明意图`：来自 README、docs、PRD/TRD/SPEC/DESIGN、ROADMAP、ADR 或发布说明。
- `源码现实`：来自入口、配置、构建、测试、API、数据模型、服务实现和运行脚本。
- `偏差`：声明意图和源码现实不一致、缺证据或需要用户确认的地方。

## 8. 完成校验

完成前逐项检查：

- 输出路径只在允许范围内。
- 默认 `codebase-onboarding/` 必需文档齐全。
- `scan-summary.json` 存在，或在最终回复中说明为何不需要机器摘要。
- 进入 `feature-inventory.md` 的每个功能都有 overview、detailed design 和 evidence。
- 候选功能只在 `feature-candidates.md` 中，不冒充完成层。
- 每个 Markdown 文档都有执行摘要、文档元信息、来源文件、TODO/未知项。
- 所有非平凡结论都有来源文件或明确标注为推断。
- 声明意图、源码现实和关键偏差已记录。
- 可选 `docs/` 导出若被要求，`docs/SCAN_SUMMARY.json`、`docs/ACTION_LOG.md`、`docs/DOCS_GENERATION_REPORT.md` 和 `AGENTS.md` 索引都已生成或更新。
