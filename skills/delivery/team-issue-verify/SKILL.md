---
name: team-issue-verify
description: 独立验证单个 issue 的实现是否满足验收标准、关联 PRD、风险约束和最小实现模式，支持 diff 级简化审查，输出验证报告、遗漏项、回归风险、过度设计检查和是否 ready for PR 的结论。Verify whether a single issue implementation satisfies acceptance criteria, the linked PRD, risk constraints, and lean implementation expectations, including diff-level simplification review and over-engineering checks.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 验证实现
  - 检查 issue 是否完成
  - 能提 PR 了吗
  - 实现完了帮我验一下
  - 检查是否过度设计
  - 看看有没有写复杂
  - 最小实现验收
  - 简化审查
  - 审查 diff 有没有过度设计
  - 看看能删掉什么
  - verify issue
  - check implementation
  - ready for PR
  - is this implementation complete
  - over-engineering review
  - check lean implementation
  - review unnecessary complexity
  - simplify review
  - review diff complexity
  - what can be deleted
---

# Issue 验证

这个技能用于确认 `team-issue-implement` 的结果是否真的满足 issue 和 PRD，而不是只确认“代码写完了”。它应尽量独立于实现过程进行判断，优先检查外部行为、验收标准和回归风险。

当用户说“检查是否过度设计”“看看有没有写复杂”“最小实现验收”“over-engineering review”等表达时，除验收标准外，还要检查实现是否存在无请求抽象、无用依赖、重复封装、可复用现有代码却没有复用、或本可使用标准库/平台能力却新增实现的问题。

当用户说“简化审查”“审查 diff 有没有过度设计”“看看能删掉什么”“simplify review”等表达时，进入简化审查模式：只审当前 diff 的复杂度，不替代安全、正确性、验收标准或回归风险验证。

## 运行时配置

在读取 issue、实现结果、PRD 或测试前，先读取目标项目根目录的 `team-spec/config.yml`。如果存在 `access_policy`，先应用目录访问边界，再决定能否继续读取或回写项目文件。

```yaml
language: zh-CN
version_control:
  system: git
  trunk_branch: main
  contribution_model: fork-pull
  source_remote: origin
  target_remote: upstream
access_policy:
  mode: default-readonly
  directory_file: team-spec/access_policy/default.md
  user_file_template: team-spec/access_policy/{user_name}.md
```

## 输入物

主输入：

- 已实现的单个 issue，来自 `team-spec/active/{slug}/issues/` 或外部 issue tracker。
- 当前代码变更和测试变更。
- `team-issue-implement` 的验证结果或实现总结，如果已有。

参考输入：

- `team-spec/config.yml` 中的语言与 `version_control` 配置，用于判断 ready 后应推荐 GitHub PR 还是 GitLab MR，以及默认主干分支和贡献方式。
- `team-spec/active/{slug}/prd/prd.md` 中的关联 PRD。
- `team-spec/CONTEXT.md` 中的全局规范术语、角色和通用业务规则。
- `team-spec/decisions/` 中的跨需求产品决策。
- `team-spec/active/{slug}/spec/CONTEXT.md` 中的规范术语和业务规则。
- `team-spec/active/{slug}/spec/decisions/` 中的产品决策。
- `team-spec/active/{slug}/spec/reviews.md` 中的风险评审。
- 项目现有测试、CI 配置、发布说明、迁移说明或操作文档。
- `../team-issue-implement/references/PLATFORM-STDLIB.md` 中的平台、标准库、数据库、Shell/OS 和项目内已有能力替代清单。

如果本技能在同一对话中紧接 `team-issue-implement` 执行，上述参考输入已在对话上下文中，无需重新读取文件。只有在独立执行或新对话中才需要从文件加载参考输入。

如果无法确认关联 issue 或验收标准，不要给出 ready 结论。先说明缺少的输入。

## 输出物

- 验证报告。
- Ready 状态：`ready for PR`、`needs changes`、`blocked`。
- 未覆盖验收标准。
- 回归风险和建议补测项。
- 实际运行的验证命令和结果。
- 优先回写原 issue 文件中的 `## Acceptance Criteria Coverage`、`## Status`、`## Findings`、`## Notes` 或同类章节。
- 如果原 issue 文件不可修改，或外部 issue tracker 不支持回写，再写入 `team-spec/active/{slug}/issues/{issue-number}-{short-issue-slug}.verification.md`。

## 验证原则

- 验证外部行为，不验证实现偏好。
- 先对照 issue 验收标准，再对照 PRD 目标和非目标。
- 不因为测试通过就自动判定 ready；还要检查验收标准是否覆盖完整。
- 检查是否符合最小实现模式：复用优先、平台能力优先、已安装依赖优先，避免过度设计。
- 不因为代码风格偏好阻塞，除非影响可维护性、正确性或团队约定。
- 不把必要的输入校验、权限、安全、数据一致性、错误处理、可访问性或用户明确要求判为过度设计。
- 发现需求不一致时，标记为上游问题，不在验证阶段隐式改需求。

## 最小实现检查

验证时增加以下检查：

- 是否有新增依赖、抽象层、配置层、通用框架或跨模块重构；如果有，是否由验收标准或代码证据证明必要。
- 是否忽略了项目已有 helper、组件、服务、脚本、测试模式或调用流。
- 是否本可用标准库、语言内建、数据库、浏览器、操作系统或框架原生能力解决。
- 对 URL query、日期、CSV、分组、深拷贝、格式化、分页、唯一性等常见场景，是否已对照 `../team-issue-implement/references/PLATFORM-STDLIB.md` 检查替代方案。
- 是否为了追求小 diff 删除或弱化了安全、权限、数据一致性、错误处理、可访问性或必要验证。
- 如果实现刻意保持简单，是否说明了未来升级条件和残余风险。

人工黄金用例：

- 小功能避免新增依赖：检查实现是否为了 URL、日期、CSV、列表分组、参数解析等局部需求新增依赖；若标准库、平台能力或已有依赖足够，应标记为 `needs changes`。
- 已有 helper 场景优先复用：检查权限、金额、分页、错误响应、表单校验等逻辑是否复用了项目既有 helper；重复造一套相似封装应标记为过度设计风险。
- 安全边界不可裁剪：检查实现是否为了少代码删除输入校验、权限、数据一致性、错误处理、可访问性、硬件校准或用户明确要求；这类问题优先按正确性或安全风险处理，而不是风格建议。

## 简化审查模式

简化审查只关注当前 diff 中可删除或可替换的复杂度：

- 单实现接口、单调用抽象、无请求配置层、未来扩展点或通用框架。
- 重复 helper、重复组件、重复错误响应、重复格式化或重复参数解析。
- 手写标准库、语言内建、数据库、浏览器、操作系统或框架原生能力已经覆盖的逻辑。
- 新增依赖、生成脚本或构建配置是否只服务于一个小功能。

不要在简化审查里替代安全 review、正确性 review、测试覆盖 review 或产品验收；如果发现安全或正确性问题，应转入常规验证 findings。

简化审查输出要求一行一个发现：

```md
- `{path}:{line}`：删除 {可删除内容}；改用 {已有 helper / 标准库 / 平台能力 / 直接局部实现}。
```

如果没有发现可删复杂度，输出：`未发现可安全删除的过度设计；保留当前实现的理由是 {证据}`。

## 工作流

1. 读取 issue，列出所有验收标准。
2. 读取关联 PRD 和风险评审，确认上下文和约束。
3. 检查当前代码变更是否只围绕该 issue，是否混入无关改动。
4. 运行相关自动化测试；如果测试命令未知，先查项目文档或 package 配置。
5. 做验收标准逐项映射：每项对应哪个测试、代码路径或手工验证。
6. 检查边界情况、权限、数据状态、错误路径和回归风险。
7. 检查最小实现模式：是否存在过度设计、无用依赖、无请求抽象或可删除复杂度。
8. 优先更新原 issue 文件，把通过的验收项勾选，未通过的验收项保留未勾选并写明原因。
9. 输出 ready 判断和需要补充的具体行动。

## 输出格式

```md
# Verification Report: {issue title}

## Status

ready for PR / needs changes / blocked

## Acceptance Criteria Coverage

- [x] {criterion}: covered by {test or verification}
- [ ] {criterion}: missing because {reason}

## Commands Run

- `{command}`: passed / failed / not run

## Findings

- Severity: issue, evidence, recommended fix.

## Regression Risks

- Risk and suggested test or mitigation.

## Required Changes

- Actionable item, owner if known.

## Notes

- Assumptions, skipped checks, or manual verification needs.
```

## 原 Issue 回写规则

- 通过的验收项应在原 issue 文件中勾选。
- 未通过的验收项应保留未勾选，并在对应条目后写明失败原因，或在 `## Findings` 中逐条说明。
- 如果 issue tracker 不允许编辑原内容，则用单独 verification 报告承载同样的信息。
- 不要因为验证失败而删除原 issue 内容，只能补充状态、原因和修订建议。

## 完成标准

只有同时满足以下条件，才能给出 `ready for PR`：

- 所有非延期验收标准都有验证证据。
- 相关测试通过，或未运行测试的原因可接受且已说明。
- 没有未处理的 P0/P1 回归风险。
- 没有未解决的 HITL 决策点。
- 代码变更范围与 issue 匹配。

否则输出 `needs changes` 或 `blocked`，并给出具体补救动作。

当输出 `ready for PR` 时，最终回复必须用有序号的列表选项推荐下一步，方便用户直接回复序号继续推进：

推荐前先读取 `team-spec/config.yml` 的 `version_control`。如果缺失，先用 `git remote -v`、`git branch --show-current`、`git branch -r`、`git symbolic-ref refs/remotes/{remote}/HEAD` 和 `git config --get branch.{branch}.remote` 推断平台、主干分支和贡献方式；无法唯一判断时，询问用户缺失的最小信息，并在用户确认后回写 `team-spec/config.yml`。平台信号明确时，只推荐对应的 PR/MR 创建技能，不要机械地同时列 GitHub 和 GitLab。

```md
## 下一步可选

1. `team-issue-create-mr-gitlab`：检测到 GitLab remote，推送当前 issue 分支并创建关联 issue 的 Merge Request。
2. 完成人工确认：如果主干分支或贡献方式无法唯一推断，先确认后回写 `team-spec/config.yml`。
```
