---
name: team-tech-debt-to-issues
description: 将已细化并通过评审的技术债规格拆解为可独立领取、可验证、按依赖排序的工程 issue，并写入 team-spec/active/issues。Break reviewed technical debt specs into independently grabbable, verifiable engineering issues ordered by dependencies and save under team-spec/active/issues.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 技术债拆 issue
  - 把技术债拆成任务
  - 技术债转工程任务
  - break tech debt into issues
  - create issues from tech debt
---

# 技术债转工程 Issues

这个技能用于把技术债规格拆解为工程可执行的 issue，确保每个 issue 都能独立启动、独立验收，并且依赖关系清晰。

## 运行时语言配置

统一读取目标项目根目录 `team-spec/config.yml`：

```yaml
language: zh-CN
```

语言优先级：用户本轮明确指定 > `team-spec/config.yml` > 首次询问并落盘。若配置不存在，不报错，走"询问并创建"流程。

执行要求：

- 对话回复与 issue 草稿 `team-spec/active/issues/{slug}/` 下内容均使用 `language`。
- 用户临时切换语言时，本次立即生效，并询问是否回写配置。

## 输入物

- 主输入：`team-spec/active/spec/refine/{slug}.md`。
- 必要前置：`team-spec/active/spec/reviews/{slug}.md`，且状态应为 `ready`（除非用户明确接受带风险拆解草案）。
- 参考输入：`team-spec/active/spec/CONTEXT.md`、`team-spec/active/spec/decisions/`、相关代码与运行证据。

必须先确定唯一 slug。技术债链路 slug 必须包含 `debt`，格式建议 `{yyyy-mm-dd}-debt-{short-english-slug}`。无法唯一判断时必须向用户确认，不得猜测。

## 输出物

- issue 拆解草案（标题、类型、依赖、验收标准、切片理由）。
- 本地 issue 草稿默认写入 `team-spec/active/issues/{slug}/{issue-number}-{short-issue-slug}.md`。

输出目录统一收敛到 `team-spec/active/issues/{slug}/`。

## 拆解原则

- 优先 vertical slice，避免“只改数据库/只改接口/只改 UI”这类横切任务。
- 每个 issue 完成后必须有可观察结果（稳定性、性能、复杂度、错误率、维护成本等）。
- 明确 blocker，先拆并先做阻塞 issue。
- 每个 issue 标注 `AFK` 或 `HITL`；若为 `HITL`，必须写清楚需要谁做什么决策。
- 用户可见输出中不要只写缩写。首次出现时写成 `AFK（可独立执行，无需人工决策）` 或 `HITL（需要人工介入）`。
- 使用项目已有术语，不引入新同义词。

## 最小 issue 模板

```md
## Parent

team-spec/active/spec/refine/{slug}.md

## What to build

描述一个可独立验证的技术债修复切片。

## Type

AFK（可独立执行，无需人工决策） / HITL（需要人工介入）

## Acceptance criteria

- [ ] Given {上下文}，When {动作}，Then {可观察结果}。
- [ ] Given {上下文}，When {动作}，Then {可观察结果}。

## Blocked by

- None - can start immediately

## Notes

- 风险、约束、迁移和发布注意事项。
```

## 完成标准

- 产出落地到 `team-spec/active/issues/{slug}/` 的可执行 issue 草稿。
- issue 可被工程或 agent 直接领取，并具备可验证验收标准。

## 下一步可选技能

完成 issue 拆解后，必须在最终回复中列出可选下一步，帮助用户继续推进：

- 如果已生成本地 issue 草稿但尚未发布到远端：
  - `team-github-issue-publish`：将本地 issue 草稿发布到 GitHub Issues，支持整目录批量发布或指定单个 issue。
  - `team-gitlab-issue-publish`：将本地 issue 草稿发布到 GitLab Issues，支持整目录批量发布或指定单个 issue。
- 如果不需要远端 issue tracker，或已有明确的本地 issue：
  - `team-issue-implement`：选择一个 `AFK（可独立执行，无需人工决策）` issue 开始实现。
- 如果 issue 中存在 `HITL（需要人工介入）`：
  - 先完成对应人工决策，再继续发布或实现。
