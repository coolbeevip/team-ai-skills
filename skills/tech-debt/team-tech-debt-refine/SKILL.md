---
name: team-tech-debt-refine
description: 通过与用户反复确认来细化技术债需求，明确问题证据、影响范围、风险等级和验收口径，再进入评审。Refine technical debt requests through iterative confirmation, clarifying evidence, scope, risk, and acceptance criteria before review.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 技术债细化
  - 梳理技术债
  - 技术债需求说不清楚
  - 帮我想清楚这个技术债
  - refine tech debt
  - clarify tech debt
  - tech debt is unclear
---

# 技术债细化

这个技能用于把模糊的技术债诉求打磨成可评审、可拆解、可验收的技术债规格。

## 运行时语言配置

统一读取目标项目根目录 `team-spec/config.yml`：

```yaml
language: zh-CN
access_policy:
  mode: default-readonly
  directory_file: team-spec/access_policy/default.md
  user_file_template: team-spec/access_policy/{user_name}.md
```

语言优先级：用户本轮明确指定 > `team-spec/config.yml` > 首次询问并落盘。若配置不存在，不报错，走"询问并创建"流程。

执行要求：

- 对话回复与技术债细化文档 `team-spec/active/{slug}/spec/refine.md` 均使用 `language`。
- 用户临时切换语言时，本次立即生效，并询问是否回写配置。
- 在读取问题证据、代码、日志或写入技术债细化文档前，先读取 `team-spec/config.yml`；如果存在 `access_policy`，先确认当前协作者对相关目录的读写边界。

## 输入物

- 当前对话中的技术债诉求、背景、约束和目标。
- 相关代码、日志、告警、事故复盘、性能数据、缺陷记录或运维反馈。
- 现有 `team-spec/CONTEXT.md` 与 `team-spec/decisions/`（如存在）。
- 现有 `team-spec/active/{slug}/spec/CONTEXT.md` 与 `team-spec/active/{slug}/spec/decisions/`（如存在）。
- 如果存在 `team-spec/active/{slug}/spec/reviews.md` 且状态为 `needs refinement`，优先读取并围绕问题继续细化。

必须先确定唯一 slug。技术债链路的 slug 必须包含 `debt`，格式建议为 `{yyyy-mm-dd}-debt-{short-english-slug}`。如果无法唯一判断 slug，必须向用户确认，不得猜测。

开始新技术债需求前，必须确定本次要使用的 slug，并检查 `team-spec/active/{slug}/` 是否已存在。`team-spec/active/` 下允许同时存在多个技术债或产品需求 slug，不得因为其他 slug 未归档而要求用户先归档。无法唯一判断目标 slug 时，必须向用户确认。

## 输出物

- 对话中的澄清结论：问题定义、影响范围、优先级、验收口径、开放问题。
- `team-spec/active/{slug}/spec/refine.md`：技术债细化主文档。
- `team-spec/CONTEXT.md`：当需要沉淀跨多个需求长期有效的术语、角色或通用规则时更新。
- `team-spec/decisions/{number}-{decision-slug}.md`：当出现跨多个需求长期有效且高成本回退的决策时创建。
- `team-spec/active/{slug}/spec/CONTEXT.md`：当需要沉淀当前技术债局部语境时更新。
- `team-spec/active/{slug}/spec/decisions/{number}-{decision-slug}.md`：当出现只影响当前技术债的决策时创建。

下游技能读取这些输出物：`team-tech-debt-review` 用于风险评审，`team-tech-debt-to-issues` 用于工程拆解。

## 细化重点

- 证据：明确技术债由哪些事实触发（告警、故障、性能、复杂度、维护成本、交付风险）。
- 影响：明确影响的用户路径、系统模块、团队协作和发布稳定性。
- 边界：明确本轮处理范围与暂不处理范围。
- 验收：定义可观察、可验证的完成标准，不用“代码更好”这类不可验证表述。
- 约束：明确兼容性、迁移、发布窗口、回滚、合规或安全边界。

## 完成标准

- 形成可供评审的 `team-spec/active/{slug}/spec/refine.md`。
- 明确风险最高的未决问题和下一步评审建议。
- 下一步可选：必须使用有序号的列表选项输出，方便用户直接回复序号继续推进。

推荐格式：

```md
## 下一步可选

1. `team-tech-debt-review`：评审技术债规格的风险、优先级和可执行性。
```
