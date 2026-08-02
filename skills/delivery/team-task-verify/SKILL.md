---
name: team-task-verify
description: 独立验证单个 Task 实现是否满足验收、PRD、风险和最小实现要求。Independently verify one task implementation against its acceptance criteria, parent spec, risks, and commit boundary.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 验证 Task
  - 检查工程任务是否完成
  - 这个任务可以提交了吗
  - verify task
  - review task implementation
  - is this task ready to commit
---

# Task 验证

独立判断一个 Task 的实现是否满足验收标准、父 Spec/PRD、风险和单 commit 边界。本技能验证，不创建 commit、push、远端 Issue、PR 或 MR。

## 触发边界

- 适合触发：单个 Task 已有实现，需要判断 `verified`、`needs-changes` 或 `blocked`。
- 不适合触发：尚未实现时使用 `team-task-implement`；多个 Task 连续执行时使用 `team-task-batch-implement`；创建 PR/MR 时使用 Spec 级技能。

## 运行时配置

先读取 `team-spec/config.yml` 并应用语言、访问策略和版本管理配置。文件不存在时可继续纯只读验证；准备回写 Task 验证结果且配置缺失或缺少必需字段时，先使用 `team-config-init` 创建或增量补全，本技能不得自行回写配置。独立执行时必须确认允许读取 Task、代码和测试。

## 公共写作风格

写入验证结果、用户可见说明或代码评论前，读取配置中的 `writing_style.guide`（如果存在）。证据、验收和安全合同优先。

## 输入物

- 唯一 Task 文件：`team-spec/active/{slug}/tasks/T{nnn}-{short-task-slug}.md`。
- 当前未提交实现，或 Task 已记录的 commit。
- 同 slug 的 PRD、规格、评审、上下文和决策。
- 测试、静态检查、代码差异和 `../team-task-implement/references/PLATFORM-STDLIB.md`。

无法确认 Task、验收标准、实现范围或父 slug 时不得给出 `verified`。

## 输出物

- Task 验证状态：`verified`、`needs-changes` 或 `blocked`。
- 验收标准覆盖、验证命令、发现和残余风险。
- 原 Task 文件的状态与验证记录回写。

若 Task 已经是 `committed`，验证通过时保持 `committed`，不得降回 `verified`；同时确认记录的 SHA 存在且内容属于该 Task。

## 验证原则

- 先对照 Task 验收标准，再对照父 PRD 的目标、约束和非目标。
- 优先验证用户可观察行为和真实公共路径。
- 检查正常、错误、边界、权限、兼容性和回归风险。
- 检查改动是否混入其他 Task、无关重构或 speculative feature。
- 检查实现能否形成一个含义完整、可审查和可回滚的逻辑 commit。
- 测试通过不自动等于验收通过。
- 无法运行关键验证时，不得伪装成功。

## 工作流

1. 读取配置、Task 和所有验收标准。
2. 读取父 PRD、风险评审和必要上下文。
3. 确定验证对象是当前未提交变化还是已记录 commit。
4. 检查改动范围与 Task 边界。
5. 运行最小必要测试、静态检查和回归验证。
6. 逐项记录验收证据。
7. 检查平台/标准库复用和过度设计。
8. 检查是否满足单 commit 边界。
9. 回写状态、发现、命令和覆盖情况。

## 状态判定

只有同时满足以下条件才能给出 `verified`：

- 所有必需验收标准有直接证据。
- 关键测试通过且无未解释失败。
- 安全、权限、兼容和数据风险已覆盖。
- 改动范围与 Task 匹配。
- 没有依赖未完成的后续 Task 假设。
- 实现适合形成一个逻辑 commit。

存在可修复问题时使用 `needs-changes`；外部依赖或 HITL 阻塞时使用 `blocked`。

## 完成标准

- 给出唯一明确状态和证据。
- 通过的验收项已勾选，未通过项保留并说明原因。
- 记录实际执行的命令、结果和跳过项。
- 未创建 commit、push、远端 Issue、PR 或 MR。
- 结果可供 `team-task-implement` 进入提交前确认；验证本身不授权创建 Task commit。

## 最终回复

必须包含：

- Task 路径、ID、slug 和状态。
- 验收覆盖和主要发现。
- 实际验证命令、结果和跳过项。
- 单 commit 边界结论。
- 原 Task 回写路径。
- `verified` 时说明应先由用户检查实际差异并确认，再由实现流程创建本地 commit；其他状态给出补救动作。
