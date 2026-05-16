---
name: team-prd-to-alignment
description: 将 AI 结构化 PRD 转换为适合需求、研发和项目管理进行人类评审与共识对齐的演示文稿式材料。Turn AI-structured PRDs into slide-style alignment materials for product, engineering, and project management review.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - PRD 对齐材料
  - PRD 转评审材料
  - 生成需求研发对齐文档
  - PRD 给人看
  - 需求研发对齐
  - PRD alignment material
  - turn PRD into review material
  - create PRD alignment deck
  - make PRD human readable
  - product engineering alignment
---

# PRD 转对齐材料

这个技能用于把 `team-spec-to-prd` 生成的 AI 结构化 PRD，转译为适合需求、研发和项目管理人员阅读、评审和达成共识的对齐材料。它解决的问题是：PRD 可以作为 `team-prd-to-issues` 的机器输入，但不一定适合作为人类评审会的沟通材料。

默认输出是 Markdown，但内容组织应接近演示文稿或评审会材料：结论先行、信息分层、每一节都能支撑一次讨论。它不是 PRD 的替代品，也不是工程拆解技能。

## 输入物

主输入：

- `team-spec/active/prd/{slug}.md`。

参考输入：

- `team-spec/active/spec/refine/{slug}.md`：规格细化产物，用于理解原始诉求和关键背景。
- `team-spec/active/spec/reviews/{slug}.md`：规格评审报告，用于提取风险、阻塞项和待决问题。
- `team-spec/active/spec/CONTEXT.md`：长期共享上下文，用于保持术语一致。
- `team-spec/active/spec/decisions/`：产品决策记录，用于说明范围裁剪和重要决策。
- 相关设计稿、业务文档、历史 PRD、研发方案或讨论记录。

如果无法唯一确定 `{slug}`，应停止并要求用户提供 PRD 路径或 slug，不得猜测。

## 输出物

- `team-spec/active/prd/{slug}-alignment.md`：面向人类对齐的演示文稿式评审材料。
- 对话中的材料摘要：一句话结论、关键范围、待决问题和建议评审关注点。

对齐材料不修改 PRD 内容。PRD 仍是工程拆解的权威输入；对齐材料用于帮助人类快速理解、讨论和确认 PRD。

## 对齐材料结构

输出文档应使用清晰的章节编号，尽量做到每一节都像一页评审材料。

```md
# {需求名称} 对齐材料

## 1. 一句话结论

用 1-2 句话说明这个需求要解决什么问题，以及本次交付会带来什么变化。

## 2. 背景与现状

说明当前用户、业务或系统遇到的问题，以及为什么现在需要处理。

## 3. 本次做什么

- 范围内事项 1
- 范围内事项 2
- 范围内事项 3

## 4. 本次不做什么

- 明确非目标 1
- 延后事项 1

## 5. 用户路径变化

用用户视角说明体验、流程或操作路径会如何变化。

## 6. 研发需要关注什么

列出数据、权限、接口、状态流转、兼容性、迁移、监控、回滚等研发需要提前确认的事项。

## 7. 风险与待决问题

列出需要人类讨论或确认的问题，每条说明影响范围和建议决策人。

## 8. 对齐结论

记录本次评审后的结论、仍需补充的材料和下一步建议。
```

## 写作原则

- **面向人类对齐**：优先让需求、研发和项目管理能快速理解和讨论，不照搬 PRD 的机器化字段。
- **结论先行**：先讲这个需求为什么重要、要改变什么，再展开范围、路径和风险。
- **少字段，多叙述**：把 PRD 中的结构化内容转译成自然语言，不要堆砌模板字段。
- **保留分歧**：如果 PRD、规格细化和评审报告之间存在冲突，必须显式列入风险或待决问题。
- **不替代 PRD**：不要改变 PRD 的权威内容；发现 PRD 缺陷时，在对齐材料中指出，并建议回到对应上游技能修正。
- **适合会议使用**：每一节应能在评审会上直接展开讨论，避免长篇背景堆叠。

## 工作流

1. 确定 slug 或 PRD 文件路径。
2. 读取 PRD，提取目标、范围、非目标、用户场景、验收标准、风险和开放问题。
3. 读取同 slug 的规格细化、评审报告、上下文和产品决策记录。
4. 对比 PRD 与上游材料，识别裁剪、变化、冲突和仍需人类确认的问题。
5. 按演示文稿式结构生成对齐材料，优先使用短段落、列表和明确标题。
6. 将材料写入 `team-spec/active/prd/{slug}-alignment.md`。
7. 输出摘要，并建议用户用该材料组织需求、研发和项目管理对齐讨论。

生成过程中如发现 PRD 存在逻辑矛盾、范围不清、验收标准缺失或无法支撑工程拆解，应在 `## 7. 风险与待决问题` 中明确列出，不要自行补齐。

## 完成标准

- `team-spec/active/prd/{slug}-alignment.md` 已生成。
- 材料能让需求、研发和项目管理快速理解背景、范围、非目标、用户路径变化和研发关注点。
- 风险与待决问题已单独列出，并包含影响范围或建议决策人。
- 明确说明 PRD 仍是 `team-prd-to-issues` 的权威输入，对齐材料只服务于人类讨论。
- 如果发现 PRD 需要修正，已建议回到 `team-spec-to-prd` 或更上游技能处理。
