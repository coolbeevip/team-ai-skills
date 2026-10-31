---
name: team-spec-create-issue-github
description: 将完整 Spec 创建或同步为一个 GitHub Issue，并用 checklist 汇总其所有 Tasks。Create or sync one GitHub Issue for a complete spec, with all local tasks represented as a checklist.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 为 Spec 创建 GitHub Issue
  - 发布完整需求到 GitHub
  - 同步 GitHub 需求跟踪 Issue
  - create GitHub issue for spec
  - publish spec to GitHub
  - sync GitHub spec tracking issue
---

# 为 Spec 创建 GitHub Issue

把一个完整 Spec 工作区创建或同步为一个 GitHub Issue。远端 Issue 表示整个 Spec；本地 Tasks 只作为 checklist，不逐个创建远端 Issue。

## 触发边界

- 适合触发：唯一 Spec/slug 已有产品 PRD 或已评审技术债规格，以及 Tasks，需要一个可选的远端跟踪 Issue。
- 不适合触发：拆解 Task 使用 `team-prd-to-tasks`；实现 Task 使用 `team-task-implement`；创建代码 PR 使用 `team-spec-create-pr-github`。

## 运行时配置

先读取 `team-spec/config.yml`，应用语言、访问策略和 `version_control`。文件不存在或正式发布所需字段无法从参数与 Git 证据唯一确定时，先使用 `team-config-init` 创建或增量补全；本技能不得自行回写配置。Issue 语言按“本次 `--language` 或用户明确指定 > `version_control.language` > 顶层 `language` > `en-US`”确定。目标仓库优先级：用户参数 > `target_remote` > `upstream` > 唯一 GitHub remote。

## 公共写作风格

生成远端 Issue 正文和用户可见说明前，读取配置中的 `writing_style.guide`（如果存在）。正文结构、slug 标记和安全合同不受风格覆盖。

## 输入物

必须先确定唯一 `{slug}`，默认读取：

- 产品需求：`team-spec/active/{slug}/prd/prd.md`
- 技术债：`team-spec/active/{slug}/spec/refine.md` 与 `team-spec/active/{slug}/spec/reviews.md`（`Status: ready`）
- `team-spec/active/{slug}/spec/refine.md`
- `team-spec/active/{slug}/tasks/T*.md`
- `team-spec/active/{slug}/DELIVERY.md`（如果存在）
- `team-spec/config.yml`

缺少对应类型的来源规格、slug 不唯一或 Tasks 目录不存在时停止。不得扫描 archive 猜测。

## 产品需求与技术债输入

产品需求以 `prd/prd.md` 为权威输入；技术债以同 slug 的 `spec/refine.md` 和 `spec/reviews.md` 为输入，评审 `Status` 必须为 `ready`（支持 `## Status` 章节或独立的 `Status: ready` 字段，冲突或缺失时停止），不要求生成 PRD。技术债即使存在旧 PRD，也不得用其替代技术债规格。

脚本默认 `--spec-type auto`：slug 中有独立的 `debt` 段时按技术债处理，否则按产品需求处理。旧项目或命名不能表达类型时，先确认类型，再显式传入 `--spec-type product` 或 `--spec-type technical-debt`；不得因主输入缺失自动切换类型。dry-run 输出 `spec_type` 和 `source_path` 供核对。

从权威输入提取目标、范围、验收和风险；技术债还合并评审风险。缺失内容明确标注，不编造或修改上游文件。正文和标题统一称为来源规格内容，不将技术债伪装成 PRD。

## 输出物

- 一个 GitHub Issue，代表整个 Spec。
- Issue 正文中的目标、范围、验收标准和 Task checklist。
- `team-spec/active/{slug}/DELIVERY.md` 中的 GitHub Issue 编号和 URL。

本技能不创建分支、commit、push 或 PR。

## 固定脚本

优先使用：

```text
./scripts/create_github_issue.py
```

默认 dry-run：

```sh
python3 {skill_dir}/scripts/create_github_issue.py --slug {slug}
```

正式执行：

```sh
GITHUB_TOKEN=... python3 {skill_dir}/scripts/create_github_issue.py --slug {slug} --execute
```

常用参数：

- `--repo owner/repo`
- `--remote upstream`
- `--github-url https://github.example.com`
- `--title "[Component] Requirement title"`
- `--body-file path/to/localized-issue.md`
- `--label label`
- `--assignee login`
- `--milestone number`
- `--force`
- `--language zh-CN`
- `--spec-type auto|product|technical-debt`
- `--json`

脚本使用隐藏标记 `team-spec-slug` 做幂等识别。发现已有 Issue 时同步标题和正文，不重复创建。

## Issue 合同

- 一个 slug 最多对应一个 GitHub Issue。
- 标题来自显式参数或来源规格一级标题。
- 正文从完整来源规格生成，不从单个 Task 生成。
- 来源规格/Task 语言与 Issue 语言不同时，生成对应语言的标题和完整正文，并通过 `--title`、`--body-file` 传入；不修改源文档。Task ID、代码标识符、命令、路径和专有名词保持原样。
- 所有 `T{nnn}` Task 作为 checklist。
- checklist 仅反映本地 Task 状态：`committed` 为已完成，其他状态为未完成。
- 正文保留 slug 标记，供重复执行定位。
- 远端 Issue 是可选跟踪对象；没有它也允许后续创建 PR。

## 工作流

1. 读取配置、slug、来源规格、Tasks 和已有 `DELIVERY.md`。
2. 确认仓库、平台地址、语言和认证 token 来源。
3. 生成标题、正文、Task checklist 和幂等标记。
4. 运行 dry-run，展示创建或同步计划。
5. 用户已要求正式发布时追加 `--execute`。
6. 创建或更新一个 GitHub Issue。
7. 回写 `DELIVERY.md`，不得暂存或提交该文件。

## 安全要求

- token 只从环境变量读取，不记录、不回显、不写文件。
- 默认 dry-run。
- 不创建多个 Task Issues。
- 不执行 git add、commit、push 或 PR 操作。
- 回写 `team-spec/` 后保持未暂存。

## 完成标准

- 只存在一个与 slug 对应的 GitHub Issue。
- 正文表示完整 Spec，并包含全部 Task checklist。
- `DELIVERY.md` 记录编号和 URL。
- 未执行任何 git 提交或推送。

## 最终回复

必须包含：

- dry-run 或 execute 状态。
- slug、仓库、Issue 编号和 URL。
- Task checklist 数量。
- `DELIVERY.md` 回写结果。
- 失败阶段、安全重试入口和下一步。
