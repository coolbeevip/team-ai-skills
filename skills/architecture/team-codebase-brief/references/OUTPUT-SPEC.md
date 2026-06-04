# 输出规范

## 目录

- 1. 输出目录
- 2. 模板映射
- 3. 文档要求
- 4. 来源和追溯
- 5. 完成校验

## 1. 输出目录

默认写入：

```text
team-spec/active/{slug}/brief/codebase-brief/
```

目录结构：

```text
codebase-brief/
├── executive-summary.md
├── business-capability-map.md
├── scenario-walkthrough.md
├── product-impact.md
├── risk-and-constraints.md
├── stakeholder-qa.md
└── alignment-outline.md
```

## 2. 模板映射

| 输出文件 | 模板 |
| --- | --- |
| `executive-summary.md` | `assets/templates/executive-summary.md` |
| `business-capability-map.md` | `assets/templates/business-capability-map.md` |
| `scenario-walkthrough.md` | `assets/templates/scenario-walkthrough.md` |
| `product-impact.md` | `assets/templates/product-impact.md` |
| `risk-and-constraints.md` | `assets/templates/risk-and-constraints.md` |
| `stakeholder-qa.md` | `assets/templates/stakeholder-qa.md` |
| `alignment-outline.md` | `assets/templates/alignment-outline.md` |

## 3. 文档要求

每个文档必须包含：

- 目标受众。
- 数据来源范围。
- 核心结论。
- 业务/产品表达。
- 来源和置信度。
- `[TODO]` 未确认事实。
- `[ASK USER]` 需要业务/产品确认的问题。

不得把函数、类、调用栈、源码路径作为主要叙述方式。源码路径可以出现在“来源”区。

## 4. 来源和追溯

来源表建议：

| 来源 | 类型 | 支撑结论 | 置信度 | 备注 |
| --- | --- | --- | --- | --- |

来源类型：

- 用户指定来源。
- onboarding 文档。
- walk 记录。
- 源码/配置/测试证据。
- 仓库 docs/README。
- 推断。

如果用户指定了数据来源，必须在每份文档的“来源范围”中列出，并说明是否使用了补充证据。

## 5. 完成校验

完成前检查：

- 输出路径位于 `team-spec/active/{slug}/brief/codebase-brief/`。
- 已记录用户指定来源；若无指定，已记录默认来源。
- 已明确目标受众和分享目标。
- 技术事实已转译为业务能力、场景、影响、风险或决策问题。
- 每个关键结论有来源或被标注为 `[TODO]` / `[ASK USER]`。
- 没有修改业务源码或上游产物。
