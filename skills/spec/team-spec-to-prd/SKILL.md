---
name: team-spec-to-prd
description: 将已细化且通过评审的规格固化为结构化 PRD，作为需求到工程的正式交接边界。 触发词：生成 PRD、固化需求、进入工程。Convert ready refined specs into a structured PRD for engineering handoff. Keywords: generate PRD, requirement handoff, spec to PRD.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
---

# 规格转 PRD

用于把 `ready` 规格固化为 PRD，不重新做需求探索。

## 通用规则（引用）

- [COMMON-RULES.md](../../COMMON-RULES.md)

## 输入物

- `team-spec/spec/refine/{slug}.md`（主输入）。
- `team-spec/spec/reviews/{slug}.md`（必须可读，且优先 `Status: ready`）。
- `team-spec/spec/CONTEXT.md`、`team-spec/spec/decisions/`（参考）。

## 输出物

- `team-spec/prd/{slug}.md`（主输出）。
- 对话短结论：是否基于 `ready` review 生成、开放问题、已接受风险。
- 下一步指引：`team-prd-to-issues`。

## 执行步骤

1. 校验唯一 `{slug}`，并确认 refine 与 review 文件路径。
2. 检查 review 状态；若非 `ready`，默认停止并要求先修复风险。
3. 基于上游产物起草最小 PRD，覆盖目标、范围、行为、验收标准。
4. 写入 `team-spec/prd/{slug}.md`。
5. 输出下一步：使用 `team-prd-to-issues` 拆解工程 issue。

## 规则清单（必须/禁止）

- 必须以 `refine/{slug}.md` + `reviews/{slug}.md` 为主证据。
- 必须显式保留开放问题与风险假设。
- 必须保持术语与 `CONTEXT.md` 一致。
- 禁止在 review 为 `needs refinement/blocked` 时默认生成正式 PRD。
- 禁止引入与上游不一致的新需求。

## 失败与回退

- slug 或输入路径不唯一：停止并要求补充。
- review 非 `ready`：回退 `team-spec-refine` 或先处理阻塞项。
- 信息不足：生成“带风险草稿”前需用户明确确认。

## 最小输出模板

```md
# {需求名称}

## 目标
- ...

## 范围
- 范围内：...
- 范围外：...

## 功能需求
- ...

## 验收标准
- Given ... When ... Then ...

## 开放问题
- ...
```

## 完成前检查

- PRD 路径为 `team-spec/prd/{slug}.md`。
- 明确记录 review 状态来源。
- 术语与上游一致，无隐式新增需求。
- 已给出 `team-prd-to-issues` 下一步指引。
