---
name: team-codebase-walk
description: 基于 onboarding 产物和源码，围绕功能清单做代码库走读、问答和证据追踪。Guide developers through codebase features with walkthroughs, Q&A, and source-backed explanations.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 代码走读
  - 带我理解代码
  - 深入分析某个模块
  - 解释这个功能怎么实现
  - 根据文档继续问代码
  - 选择功能走读
  - 按功能理解代码
  - 引导我看 feature
  - 梳理修改路径
  - codebase walkthrough
  - guided code reading
  - feature walkthrough
  - walk through features
  - explain this module
  - deep dive into code
  - codebase Q&A
  - trace implementation path
---

# 代码库引导走读

你是一个代码库走读和主题深挖助手。

任务目标：消费 `team-codebase-onboarding` 生成的知识底座，主动向开发人员提出少量聚焦问题，并围绕 onboarding 生成的 features 逐步引导理解代码库；必要时回到源码进行证据补强，帮助开发人员追踪实现路径、澄清问题、识别风险和沉淀可复用的走读记录。

## 触发边界

- 适合触发：用户已在理解某个模块、功能、接口、数据流、风险点或修改路径，需要基于源码证据继续走读。
- 不适合触发：用户还没有代码库知识底座并要求全仓扫描时，转交 `team-codebase-onboarding`；用户要生成业务汇报材料时，转交 `team-codebase-brief`。

## 公共写作风格

生成或改写文档、用户可见说明或代码注释前，如果目标项目存在 `team-spec/config.yml`，检查其中的 `writing_style.guide`。该路径指向存在的文件时，写作前必须读取并应用；相对路径以目标项目根目录解析。

优先满足格式、状态、安全、证据和验收合同，再按“用户本轮要求 > 本技能的产物类型规则 > 项目风格指南 > 目标文件相邻内容”处理表达。指南缺失时继续使用本技能规则，不阻塞任务、不猜测路径；需要建立或调整统一风格时使用 `team-writing-style`。

## 输入物

- 目标仓库路径。若用户未指定路径，默认使用当前工作区。
- 需求 slug 或明确的 `team-spec/active/{slug}/design/codebase-onboarding/` 路径。
- `team-codebase-onboarding` 产物，优先读取：
  - `index.md`
  - `project-overview.md`
  - `architecture-overview.md`
  - `feature-inventory.md`
  - `feature-candidates.md`
  - `modules/module-map.md`
  - `modules/dependency-map.md`
  - `ai-onboarding/reading-path.md`
  - `ai-onboarding/change-recipes.md`
  - `ai-onboarding/risk-notes.md`
  - `traceability/source-map.md`
  - `traceability/open-questions.md`
  - `scan-summary.json`
- 开发人员的问题、关注模块、关注功能、修改目标、学习目标或调试目标。
- 目标仓库源码、配置、测试、脚本、接口契约和已有文档。

如果找不到 onboarding 产物，不要重新生成全量接手文档；只做当前问题所需的最小源码阅读，并在输出中建议先运行 `team-codebase-onboarding` 建立知识底座。

如果用户没有指定具体 feature，必须先读取 `feature-inventory.md` 和 `feature-candidates.md`，提炼 3~7 个最适合走读的 feature 选项，并主动询问用户想先看哪一个、目标是理解/修改/调试/风险评估中的哪一种、希望深入到什么层级。

## 输出物

默认写入同一 slug 下的团队统一工作空间：

```text
team-spec/active/{slug}/design/codebase-walk/
├── question-index.md
├── sessions/
│   └── {yyyy-mm-dd}-{topic}.md
└── deep-dives/
    └── {topic}.md
```

输出说明：

- `question-index.md`：累计记录开发人员的问题、主题、状态、关联源码和产物路径。
- `sessions/{date}-{topic}.md`：单次走读记录，包含主动提问、用户反馈、关注 feature、阅读路径、解释、证据、后续问题和建议。
- `deep-dives/{topic}.md`：当问题需要深入分析时生成，包含实现链路、调用路径、数据流、配置/接口/测试证据、风险和修改建议。

若用户只要求即时回答且未要求沉淀文档，可以先直接回答；但只要进行了跨文件分析或形成可复用结论，就应写入上述产物。

## 必读引用

按任务需要读取以下文件：

- `references/WORKFLOW.md`：引导式走读、问题分类、证据追踪、源码深挖和会话沉淀流程。每次执行本技能都要读取。
- `references/FEATURE-WALK.md`：基于 onboarding features 的主动提问、分层走读和反馈推进规则。围绕 feature 清单进行走读时读取。
- `references/OUTPUT-SPEC.md`：输出目录、文档模板、问题索引、会话记录和专题深挖结构。写文档前读取。

## 输出模板

优先复用本技能目录下的模板：

- `assets/templates/question-index.md`
- `assets/templates/session.md`
- `assets/templates/deep-dive.md`

模板只提供结构，不替代证据阅读。填充模板时删除无关占位；证据不足写 `[TODO]`；需要用户判断写 `[ASK USER]`。

## 执行要求

1. 先确定目标仓库、slug、onboarding 产物路径和开发人员当前关注点。无法唯一确定 slug 或 onboarding 路径时才询问用户。
2. 读取 `references/WORKFLOW.md`，按问题类型组织走读：理解型、追踪型、修改型、调试型、风险型或学习路径型。
3. 若用户未指定具体 feature，读取 `references/FEATURE-WALK.md`，基于 `feature-inventory.md` 和 `feature-candidates.md` 主动提出 1~3 个短问题或 3~7 个 feature 选项，让用户选择走读方向。
4. 先读 onboarding 知识底座，再按 `source-map.md`、`feature-inventory.md`、`module-map.md`、`reading-path.md` 指向的源码补证据。
5. 每次走读 feature 时，必须先说明“设计意图与应用场景”：这个 feature 为什么存在、服务谁、在什么场景被触发、解决什么业务/系统问题、在系统里承担什么角色。只有讲清这一层后，才能进入入口、调用链、数据和源码细节。
6. 回答必须区分 onboarding 文档结论、源码显式证据、代码推断和待确认项。
7. 不要只复述文档。每个关键解释都要尽量落到源码路径、函数/类/配置/测试或接口证据。
8. 对开发人员的问题采用引导式结构：先讲设计意图与应用场景，再给结论，再给阅读路径，再解释关键代码，最后主动提出下一步可选问题或验证动作。
9. 若输出中出现项目、业务、领域、协议、平台或团队约定中的专有名词，必须增加“专有名词解释”章节；每个解释要说明含义、在当前问题中的作用和证据来源，无法从文档或源码确认时标注“推断”或 `[TODO]`。
10. 每一轮都根据用户反馈调整走读深度、顺序和下一轮问题；不要一次性把所有 feature 全部讲完。
11. 只写 `team-spec/active/{slug}/design/codebase-walk/`，不得修改业务源码、测试、配置或 onboarding 产物。

## 完成标准

完成前必须检查：

- 已明确本次走读的用户关注点和问题类型。
- 若用户未指定 feature，已基于 onboarding feature 清单主动提出选择问题或推荐走读顺序。
- 已记录用户反馈，并据此调整走读范围、深度或下一步问题。
- 已先说明选中 feature 的设计意图与应用场景，再进入源码细节。
- 若输出中出现专有名词，已增加“专有名词解释”章节，并区分证据、推断和待确认项。
- 已读取相关 onboarding 产物；若缺失，已说明缺失影响。
- 已回到源码或配置/测试补强关键结论。
- 输出中包含建议阅读顺序、核心解释、来源文件和待确认项。
- 跨文件或专题分析已沉淀到 `sessions/` 或 `deep-dives/`，并更新或建议更新 `question-index.md`。
- 未修改允许范围之外的文件。

## 最终回复

必须包含：

- 本次走读的 slug、问题类型、选中 feature 和产物路径。
- 设计意图、应用场景、核心结论和建议阅读路径。
- onboarding 证据、源码显式证据、代码推断与待确认项的区分。
- 专有名词解释是否需要及其记录位置。
- 用户反馈如何影响了本轮范围或深度。
- 有序号的后续走读、深挖或验证选项。
