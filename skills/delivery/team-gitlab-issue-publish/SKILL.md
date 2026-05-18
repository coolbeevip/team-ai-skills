---
name: team-gitlab-issue-publish
description: 将 team-spec/active/issues/{slug}/ 下的本地 issue 草稿发布到 GitLab Issues，默认按依赖顺序处理整个目录，也可指定单个 issue，并回写发布结果，支持 dry-run、幂等检查与部分失败重试。Publish local issue drafts under team-spec/active/issues/{slug}/ to GitLab Issues, either as a full dependency-ordered batch or as a single selected issue, with write-back status, dry-run, idempotency checks, and retry support.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 发布到 GitLab
  - 发布 issue 到 GitLab
  - 批量创建 GitLab Issues
  - 把 issue 草稿发布到 GitLab
  - 发布单个 issue 到 GitLab
  - publish to GitLab
  - publish issue to GitLab
  - create GitLab issues from drafts
  - create GitLab issue from draft
  - batch publish issues to GitLab
---

# 发布 GitLab Issue

这个技能用于把 `team-prd-to-issues` 生成的本地 issue 草稿发布到 GitLab Issues。默认会按依赖顺序发布整个 slug 下的所有 issue；如果用户指定单个 issue，则只发布那一个。它关注“可重复执行、可追踪、可恢复”，避免重复创建和依赖顺序错误。

v1 仅支持 GitLab。不要在同一个技能中混合 GitHub 与 GitLab 发布逻辑；GitHub 请使用独立技能。

## 固定脚本

发布 GitLab issue 时，优先使用本技能目录下的固定脚本，不要临时重写 GitLab API 调用代码：

```text
./scripts/publish_gitlab_issues.py
```

脚本依赖同目录下的公共辅助模块 `./scripts/_team_common.py`（vendored copy，与仓库根目录 `scripts/_team_common.py` 保持同步）。复制本技能目录时需一并复制该文件。

脚本能力：

- 读取 `team-spec/active/issues/{slug}/` 或显式 `--issues-dir`。
- 默认发布该目录下全部 issue；也可以通过 `--issue` 只发布指定的单个 issue。
- 按 `Blocked by` 生成依赖顺序。
- 使用 `./scripts/templates/issue_body.md.tpl` 渲染平台正文，正文只保留对 GitLab 协作有用的摘要字段，不再直接发布完整草稿原文。
- 发布前会校验 issue 标题是否足够清晰：必须来自明确的 `#` 标题或 `Title` 段，不能回退到文件名；标题过短、过泛或缺少对象时会拒绝发布。
- 从显式 `--project` 或 git remote 推断 GitLab 项目，多个 remote 时优先 `upstream`。
- 默认 dry-run，只输出发布计划。
- `--execute` 时创建 GitLab Issues，并把发布结果回写到本地 issue 草稿。
- 使用 `Local-Issue-Key` 做幂等检查，避免重复创建。
- 正式请求 GitLab API 前会把 method、URL 和 payload 打印到 stderr，便于失败排查；token 不会输出。

推荐 dry-run：

```sh
python3 {skill_dir}/scripts/publish_gitlab_issues.py --slug {slug}
```

用户确认后正式发布：

```sh
GITLAB_URL=https://gitlab.example.com GITLAB_TOKEN=... python3 {skill_dir}/scripts/publish_gitlab_issues.py --slug {slug} --execute
```

其中 `{skill_dir}` 是当前技能目录。技能内部定位脚本时应使用相对 `SKILL.md` 的路径 `./scripts/publish_gitlab_issues.py`，执行命令时再解析成实际文件路径。

常用参数：

- `--issue 001-add-export-filter.md`：只发布指定的单个 issue，可传入文件名、文件路径或草稿标识。
- `GITLAB_URL=https://gitlab.example.com`：自建 GitLab 平台地址。默认从环境变量读取；未设置时才使用 `https://gitlab.com`。
- `--gitlab-url https://gitlab.example.com`：仅用于临时覆盖 `GITLAB_URL`，不要在常规执行命令中主动传入。
- `--project namespace/project`：显式指定项目，优先级高于 remote 推断。
- `--remote upstream`：显式指定用于推断项目的 remote。
- `--label label-name`：可重复传入多个 label。
- `--milestone-id 123`：指定 milestone。
- `--assignee-id 123`：可重复传入多个 assignee。
- `--force`：忽略本地 `Publish Status`，重新检查 GitLab；仍会使用远端 `Local-Issue-Key` 做幂等检查，不应直接重复创建。
- `--json`：输出机器可读 JSON。

标题规则：

- 优先使用 issue 草稿里的 `# 标题`，其次使用 `Title` 段的首行。
- 不允许退回到文件名作为标题来源。
- 标题建议至少包含动作、对象和范围，不要只写 `Fix`、`Update`、`Refactor` 这类泛化词。
- 标题过短、过长或缺少足够语义时，脚本会停止发布并提示修正。

## 输入物

主输入：

- `team-spec/active/issues/{slug}/` 下的 issue 草稿文件。
- `--issue` 可选参数：只发布指定的单个 issue 草稿。

必须参数：

- 平台地址（默认从环境变量 `GITLAB_URL` 读取；未设置时使用 `https://gitlab.com`。自建 GitLab 必须通过 `GITLAB_URL` 提供自定义地址，除非用户明确要求用 `--gitlab-url` 临时覆盖）。
- 仓库定位：`namespace/project` 或可唯一定位项目的项目 ID；如果用户未显式提供，可按下面“仓库定位规则”从 git remote 推断。
- 认证 token（必须通过环境变量提供，不写入任何文件）。
- 目标 slug 或明确的 issue 目录路径（如 `team-spec/active/issues/{slug}/`）。

建议参数：

- 默认 labels。
- milestone。
- assignee 映射规则。
- `dry-run` 开关（默认建议先开）。

前置条件：

- 如团队需要人类对齐，建议先使用 `team-prd-to-alignment` 生成 `team-spec/active/prd/{slug}-alignment.md` 并完成评审讨论。
- `team-prd-to-issues` 已产出可发布草稿；如果只发单个 issue，则该 issue 草稿已存在。
- 需要有效 token 且具备 GitLab Issues 写权限。

如果无法唯一确定 slug、项目或 token 来源，必须停止并向用户确认，不得猜测。

## 仓库定位规则

当用户没有显式提供 GitLab 项目 ID 或 `namespace/project` 时，先读取当前仓库的 git remote：

1. 如果存在名为 `upstream` 的 GitLab remote，默认使用 `upstream` 对应的上游仓库创建 issue。
2. 如果不存在 `upstream`，但当前分支配置了唯一的 upstream tracking remote，使用该 tracking remote。
3. 如果只有一个 GitLab remote，使用这个 remote。
4. 如果存在多个 GitLab remote 且无法按以上规则唯一判断，停止并要求用户指定项目，不要默认使用 `origin`。

从 remote URL 提取项目时，兼容 HTTPS 与 SSH 格式，例如：

- `https://gitlab.com/group/project.git` -> `group/project`
- `git@gitlab.com:group/project.git` -> `group/project`

自建 GitLab 场景下，remote host 必须与平台地址一致；如果不一致，应要求用户确认平台地址和目标项目。

## 多 Remote 模式

当仓库中存在多个 remote 时，先结合 remote 名称判断工作模式：

- fork-pull 模式：通常会同时存在 `origin` 和 `upstream`，并且 `origin` 指向开发者 fork、`upstream` 指向上游仓库。此时 issue 应默认创建到 `upstream` 对应的上游仓库。
- 单仓模式：如果只有一个远端或无法判断 fork-pull，则按仓库定位规则继续推断。

无论是哪种模式，真正执行 `--execute` 之前，都必须先输出 dry-run 结果，并由人类确认目标项目、issue 列表和发布计划没有问题。

## 输出物

- GitLab Issue 或 GitLab Issues（默认按依赖顺序批量创建；指定单个 issue 时只创建一个）。
- 本地回写结果（每个 issue 草稿都应记录）：
  - 远端 issue IID/ID。
  - 远端 issue URL。
  - 发布状态（created / skipped / failed）。
  - 错误原因（如失败）。
  - 发布时间戳。
- 批量发布汇总：
  - 总数、成功数、跳过数、失败数。
  - 失败清单与重试建议。

优先回写原 issue 草稿；若原文件结构不便回写，再在同目录新增发布结果文件。

## 发布规则

- 默认按依赖顺序发布：先 blocker，再依赖它的 issue。
- 如果用户通过 `--issue` 指定单个 issue，则只发布该 issue，不会发布同 slug 下其它草稿。
- 先做参数与权限检查，再执行真正发布。
- 默认先执行 `dry-run` 预览发布计划，用户确认后再正式发布。
- 幂等优先：重复执行时，不应重复创建同一 issue。
- 出现部分失败时继续处理可执行项，并保留失败清单用于补偿重试。

## 幂等策略

每个本地 issue 在发布前必须做唯一性检查。推荐组合键：

- 本地 issue 文件名（`team-prd-to-issues` 已生成的 `{local-seq}-{short-issue-slug}.md` 格式，其中 `local-seq` 直接取自现有文件名前缀，用作本地唯一标识，不是远端 GitLab issue IID/ID）。
- issue 标题（`Title`）。

若远端已存在匹配项，则标记为 `skipped` 并回写现有 issue URL，不重复创建。

发布时必须把本地唯一键持久化到远端 issue 描述，例如追加标准元数据行：`Local-Issue-Key: {local-seq}-{short-issue-slug}.md`。

推荐匹配逻辑：

- 第一步：读取本地草稿 `## Publish Status`。如果 `Status` 为 `created` 或 `skipped`，且已有 `GitLab URL` 或 `GitLab IID`，默认标记为 `skipped`，不再创建远端 issue。
- 第二步：如果用户显式传入 `--force`，或本地没有有效发布记录，则按远端 issue 描述中的 `Local-Issue-Key` 精确匹配（完全一致）。
- 第三步：在同一 `Local-Issue-Key` 候选内按标题精确匹配（去除首尾空白后比较）。
- 第四步：若仍有多个候选，停止自动发布该条并标记为 `failed`，要求人工确认，避免误关联。

## 建议流程

1. 确认 slug、项目、平台地址、token 来源与权限范围；平台地址优先读取环境变量 `GITLAB_URL`，不要默认追加 `--gitlab-url`；若项目来自 git remote，按“仓库定位规则”优先选择上游仓库。
2. 读取 `team-spec/active/issues/{slug}/` 下所有待发布 issue 草稿。
3. 解析 `Blocked by` 关系并生成依赖有向图。
4. 检查循环依赖；若存在循环依赖，停止并输出冲突清单。
5. 使用固定脚本生成拓扑顺序发布计划。
6. 先执行固定脚本的默认 `dry-run`，输出将创建/跳过的完整清单。
7. 用户确认后用固定脚本追加 `--execute` 执行正式发布。
8. 每创建一个 issue 即刻回写本地结果，避免中断后丢失进度。
9. 对失败项按可配置策略重试；重试后仍失败则保留失败状态并汇总。
10. 输出批量发布报告和下一步建议（如补充权限、修复依赖或手动处理失败项）。

## 错误与恢复策略

- 认证失败：立即停止，不执行发布。
- 权限不足：立即停止，并提示所需权限范围。
- 单条数据错误（标题缺失、格式不合法等）：标记该条失败，继续其余可执行项。
- 网络或临时 API 错误：按重试策略处理，超过上限后标记失败。
- 已发布部分不回滚；使用回写状态与汇总清单做后续补偿。

## 安全要求

- token 只能从环境变量读取。
- 自建 GitLab 平台地址默认从 `GITLAB_URL` 读取；除非用户明确要求覆盖，否则不要把平台地址作为命令行参数传入。
- 不记录、不回显 token。
- 不将 token 写入 `team-spec/` 或任何仓库文件。

## 完成标准

- 目标 slug 下 issue 已按依赖顺序处理完成，或指定的单个 issue 已处理完成（创建/跳过/失败均有记录）。
- 每个本地 issue 草稿都有可追踪的回写状态。
- 输出了可执行的失败重试清单。
- 结果可重复执行，且不会产生重复 issue。
