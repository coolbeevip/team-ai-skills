---
name: team-spec-create-issue-gitlab
description: 将完整 Spec 创建或同步为一个 GitLab Issue，并用 checklist 汇总其所有 Tasks。Create or sync one GitLab Issue for a complete spec, with all local tasks represented as a checklist.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 为 Spec 创建 GitLab Issue
  - 发布完整需求到 GitLab
  - 同步 GitLab 需求跟踪 Issue
  - create GitLab issue for spec
  - publish spec to GitLab
  - sync GitLab spec tracking issue
---

# 为 Spec 创建 GitLab Issue

把一个完整 Spec 工作区创建或同步为一个 GitLab Issue。远端 Issue 表示整个 Spec；本地 Tasks 只作为 checklist，不逐个创建远端 Issue。

## 触发边界

- 适合触发：唯一 Spec/slug 已有 PRD 和 Tasks，需要一个可选的远端跟踪 Issue。
- 不适合触发：拆解 Task 使用 `team-prd-to-tasks`；实现 Task 使用 `team-task-implement`；创建代码 MR 使用 `team-spec-create-mr-gitlab`。

## 运行时配置

先读取 `team-spec/config.yml`，应用语言、访问策略和 `version_control`。文件不存在或正式发布所需字段无法从参数与 Git 证据唯一确定时，先使用 `team-config-init` 创建或增量补全；本技能不得自行回写配置。Issue 语言按“本次 `--language` 或用户明确指定 > `version_control.language` > 顶层 `language` > `en-US`”确定。目标项目优先级：用户参数 > `target_remote` > `upstream` > 唯一 GitLab remote。

GitLab 地址必须从 `GITLAB_URL` 读取。

## 公共写作风格

生成远端 Issue 正文和用户可见说明前，读取配置中的 `writing_style.guide`（如果存在）。正文结构、slug 标记和安全合同不受风格覆盖。

Issue 正文遵守以下原则：
- 直接陈述事实，不夸大意义（禁止"标志着""为……奠定基础""彰显了"等）
- 用具体数字代替形容词（写"误差不超过 0.005m"不写"高精度"）
- 不堆砌三段式（不要硬凑"快速、稳定、安全"）
- 不用破折号制造"强调"效果

## Issue 正文模板

从 PRD 提取信息后，按以下结构用自然语言组织：

```markdown
## 背景

{一段话说明为什么要做这件事，当前有什么问题。}

## 要做什么

{一段话或几个要点说明具体要改什么，不涉及实现细节。}

## 做完的标准

- {用自然语言描述验收条件，不用 Given/When/Then 格式}
- {每条一句话，直接说"什么情况下应该怎样"}
- {不列编号，不分内外范围}

<!-- team-spec-slug: {slug} -->
```

模板只是参考结构，不是强制格式。如果 PRD 内容更适合其他组织方式，按实际调整。核心原则：一个人花两分钟读完就能理解要做什么、怎么算做完。

## 输入物

必须先确定唯一 `{slug}`，默认读取：

- `team-spec/active/{slug}/prd/prd.md`
- `team-spec/active/{slug}/spec/refine.md`
- `team-spec/active/{slug}/DELIVERY.md`（如果存在）
- `team-spec/config.yml`

缺少 PRD 或 slug 不唯一时停止。不得扫描 archive 猜测。

## 输出物

- 一个 GitLab Issue，代表整个 Spec。
- Issue 正文用自然语言描述背景、要做什么和做完的标准。
- `team-spec/active/{slug}/DELIVERY.md` 中的 GitLab Issue IID 和 URL。

本技能不创建分支、commit、push 或 MR。

## 固定脚本

优先使用：

```text
./scripts/create_gitlab_issue.py
```

默认 dry-run：

```sh
GITLAB_URL=https://gitlab.example.com python3 {skill_dir}/scripts/create_gitlab_issue.py --slug {slug}
```

正式执行：

```sh
GITLAB_URL=https://gitlab.example.com GITLAB_TOKEN=... python3 {skill_dir}/scripts/create_gitlab_issue.py --slug {slug} --execute
```

常用参数：

- `--project namespace/project`
- `--remote upstream`
- `--title "[Component] Requirement title"`
- `--body-file path/to/localized-issue.md`
- `--label label`
- `--assignee-id id`
- `--milestone-id id`
- `--force`
- `--language zh-CN`
- `--json`

脚本使用隐藏标记 `team-spec-slug` 做幂等识别。发现已有 Issue 时同步标题和正文，不重复创建。

## Issue 合同

- 一个 slug 最多对应一个 GitLab Issue。
- 标题来自显式参数或 PRD 一级标题。
- **Issue 是给人看的，不是给 AI 看的**。正文用自然语言写成一段可读的概述，不要复刻 PRD 的章节结构，不要用 Given/When/Then 格式。
- 正文从 PRD 中提取三个核心信息：背景（为什么做）、要做什么、做完的标准（用自然语言描述，不用僵硬格式）。
- 规格文档本身不会上传到 Git，Issue 正文中不得出现指向本地规格文件的链接或路径。
- 不暴露工程 Task 编号（T{nnn}），Issue 只需要描述工作内容，不需要透漏内部 Task 拆解。
- 正文末尾保留一行隐藏式的 slug 标记用于幂等识别，格式为 `<!-- team-spec-slug: {slug} -->`，人类读者不可见。
- 远端 Issue 是可选跟踪对象；没有它也允许后续创建 MR。

## 工作流

1. 读取配置、slug、PRD 和已有 `DELIVERY.md`。
2. 确认项目、`GITLAB_URL`、语言和 token 来源。
3. 从 PRD 中提取背景、目标和验收标准，用自然语言改写为 Issue 正文。
4. 运行 dry-run。
5. 用户已要求正式发布时追加 `--execute`。
6. 创建或更新一个 GitLab Issue。
7. 回写 `DELIVERY.md`，不得暂存或提交该文件。

## 安全要求

- token 只从环境变量读取。
- 默认 dry-run。
- 正式 API 请求可输出 method、URL 和无敏感信息 payload，不输出 token。
- 不创建多个 Task Issues。
- 不执行 git add、commit、push 或 MR。

## 完成标准

- 只存在一个与 slug 对应的 GitLab Issue。
- 正文是自然语言概述，包含背景、要做什么和做完的标准，不包含 Given/When/Then、T{nnn} 编号或本地文件链接。
- 正文末尾有隐藏式 slug 标记。
- `DELIVERY.md` 记录 IID 和 URL。
- 未执行任何 git 提交或推送。

## 最终回复

必须包含：

- dry-run 或 execute 状态。
- slug、项目、Issue IID 和 URL。
- `DELIVERY.md` 回写结果。
- 失败阶段、安全重试入口和下一步。
