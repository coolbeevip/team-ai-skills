---
name: team-spec-refine
description: 通过与用户反复确认来细化需求规格，澄清术语、边界、业务规则和验收口径，并更新需求上下文或产品决策记录。适用于 PRD 前的需求探索、规格打磨和用户访谈。Refine product specs through iterative user confirmation, clarifying terminology, scope, business rules, and acceptance criteria before PRD creation.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# 规格细化

这个技能用于把模糊需求打磨成团队共享、可验证的规格。一次只问一个问题。不要在关键假设尚未稳定时直接写 PRD。

## 首轮动作

1. 用一到两句话复述当前需求。
2. 找出最阻碍共识的一个未知点。
3. 提出一个聚焦问题，并给出你的推荐答案。
4. 等用户回答后再继续。

如果答案可以从现有项目文档或代码中获得，先查资料，不要把问题抛给用户。

## 需求上下文

探索时优先寻找已有需求语言和产品决策：

```text
/
├── REQUIREMENTS.md
├── team-spec/
│   ├── spec/
│   │   ├── CONTEXT.md
│   │   └── decisions/
│   │   └── refinements/
│   ├── prd/
│   └── issues/
└── docs/
```

如果 `team-spec/spec/CONTEXT.md` 不存在，等第一个产品术语、角色、流程或业务规则被确认后再创建。不要提前创建空文件。

如果 `team-spec/spec/decisions/` 不存在，等第一个长期有效、值得保留的产品决策出现后再创建。

需求上下文使用 [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md)，产品决策记录使用 [DECISION-FORMAT.md](./DECISION-FORMAT.md)。

## 输入物

- 当前对话中的初始需求、用户问题、业务背景或功能想法。
- 现有 `team-spec/spec/CONTEXT.md`，如果项目已有需求上下文。
- 现有 `team-spec/spec/decisions/`，如果项目已有产品决策记录。
- 相关 PRD、业务文档、任务、设计稿或代码现状。

## 输出物

- 对话中的澄清结论：需求摘要、规范术语、范围内/范围外、开放问题和轻量风险扫尾。
- `team-spec/spec/refinements/{yyyy-mm-dd}-{english-slug}.md`：单次规格细化的主输出物。
- `team-spec/spec/CONTEXT.md`：当产品术语、角色、流程或业务规则被确认后更新。
- `team-spec/spec/decisions/{number}-{slug}.md`：当出现长期有效的产品决策时创建。

下游技能会读取这些输出物：`team-spec-review` 用于规格评审，`team-spec-to-prd` 用于生成 PRD。

`team-spec-refine` 可以与 `team-spec-review` 反复迭代。如果评审发现 P0 或关键 P1，应回到本技能继续修正术语、范围、业务规则、异常路径或验收口径。

每个需求必须使用唯一 slug 串联全流程。格式为 `{yyyy-mm-dd}-{short-english-slug}`，例如 `2026-05-10-export-filter`。如果同一天同名，追加序号，例如 `2026-05-10-export-filter-2`。`CONTEXT.md` 和 `decisions/` 是长期共享上下文，不替代单次 `refinements/{slug}.md`。

## 细化原则

- 发现一词多义时立即指出。例如：“你说的账号，是登录账号、客户账户，还是计费账户？”
- 把模糊表述改成可观察行为。例如：把“审批要快”改成“95% 的审批在 2 分钟内完成”。
- 区分用户问题和解决方案。先确认要解决什么问题，再接受页面、流程或系统设计。
- 重点追问用户角色、权限、状态变化、异常路径和业务规则。
- 用具体场景压测边界。主动构造边缘案例，让概念边界暴露出来。
- 有多个方案时，给出推荐方案，再让用户确认或否定。
- 维护一套规范术语。术语一旦确认，立即更新 `team-spec/spec/CONTEXT.md`，不要攒到最后。

## 追问顺序

除非对话中有更高优先级，否则按这个顺序推进：

1. 问题：这个需求由什么用户痛点、业务机会或产品判断触发？
2. 用户：谁遇到问题，谁使用方案，谁运营或审批？
3. 结果：什么可衡量变化能证明需求有效？
4. 范围：哪些必须包含，哪些明确排除，哪些延期？
5. 流程：从触发到完成的主路径是什么？
6. 数据：涉及哪些对象、字段、状态和规则？
7. 异常：什么会失败、冲突、过期、取消或需要人工介入？
8. 约束：合规、隐私、性能、灰度、迁移、运营限制是什么？
9. 验收：哪些例子应该通过，哪些应该失败？

## 产品决策记录

只有同时满足以下三点，才建议创建产品决策记录：

1. 这个决策以后反悔成本较高。
2. 未来同事只看 PRD 或代码时不容易理解为什么这么选。
3. 当时确实存在多个备选方案，并且选择依赖产品判断。

不要为显而易见的措辞、临时备注或实现阶段很可能改变的细节创建决策记录。

## 会话输出

每轮回答后，简短说明本轮解决了什么：

- 已确认的术语、规则、角色或范围边界。
- 当前剩余风险最高的歧义。
- 下一个单一问题。

细化完成后，总结：

- 用自然语言描述需求。
- 规范术语。
- 范围内和范围外内容。
- 仍未解决的问题。
- 轻量风险扫尾：指出是否存在会阻塞 PRD 的明显 P0/P1 缺口。
- 写入或更新 `team-spec/spec/refinements/{slug}.md`。
- 推荐下一步：如果没有明显阻塞，使用 `team-spec-review`；如果仍有高风险歧义，继续细化。
