---
name: team-spec-archive
description: 将 team-spec/active 中已完成、废弃或暂停的单个需求产物归档到 team-spec/archive/{slug}/，清空活跃工作区以避免新需求误改旧规格。Archive a completed, abandoned, or paused requirement from team-spec/active into team-spec/archive/{slug}/ so new active specs do not accidentally modify old work.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 归档需求
  - 清空 active
  - 结束这个需求
  - 开始新需求前归档
  - archive spec
  - archive requirement
  - clear active spec
  - close this requirement
---

# 需求归档

这个技能用于把 `team-spec/active/` 中某个需求 slug 的过程产物移动到 `team-spec/archive/{slug}/`。归档是需求生命周期动作，不负责继续细化、评审、生成 PRD、拆 issue 或实现代码。

## 输入物

必须先确定唯一 slug，来源可以是：

- 用户显式提供的 `{slug}`。
- 明确的 active 文件路径，例如 `team-spec/active/spec/refine/{slug}.md`。
- `team-spec/active/` 中唯一可识别的 slug。

可归档的 active 产物：

- `team-spec/active/spec/refine/{slug}.md`
- `team-spec/active/spec/reviews/{slug}.md`
- `team-spec/active/prd/{slug}.md`
- `team-spec/active/prd/{slug}-alignment.md`
- `team-spec/active/issues/{slug}/`
- `team-spec/active/design/{slug}.md`

不自动归档长期共享上下文：

- `team-spec/active/spec/CONTEXT.md`
- `team-spec/active/spec/decisions/`

如果无法唯一确定 slug，必须停止并要求用户提供 slug 或明确文件路径，不得猜测。如果 `team-spec/archive/{slug}/` 已存在，默认停止，不得覆盖旧归档。

## 输出物

- `team-spec/archive/{slug}/spec/refine/{slug}.md`
- `team-spec/archive/{slug}/spec/reviews/{slug}.md`
- `team-spec/archive/{slug}/prd/{slug}.md`
- `team-spec/archive/{slug}/prd/{slug}-alignment.md`
- `team-spec/archive/{slug}/issues/`
- `team-spec/archive/{slug}/design/{slug}.md`
- `team-spec/archive/{slug}/ARCHIVE.md`

归档完成后，`team-spec/active/` 中不应再保留该 slug 的 refine、review、PRD、alignment、issue 草稿或设计文档，避免后续 `team-spec-refine` 开始新需求时误读旧上下文。

## 固定脚本

归档时优先使用本技能目录下的固定脚本：

```text
./scripts/archive_team_spec.py
```

脚本能力：

- 默认 dry-run，只输出将移动的文件和目录。
- `--execute` 时移动对应 slug 的 active 产物并生成 `ARCHIVE.md`。
- 如果未传 `--slug`，仅在 active 中能唯一识别 slug 时自动推断。
- 如果目标归档目录已存在，停止执行。
- 不移动 `CONTEXT.md`、`decisions/`、缓存文件或其他无关文件。

推荐 dry-run：

```sh
python3 {skill_dir}/scripts/archive_team_spec.py --slug {slug}
```

用户确认后正式归档：

```sh
python3 {skill_dir}/scripts/archive_team_spec.py --slug {slug} --reason completed --execute
```

其中 `{skill_dir}` 是当前技能目录。技能内部定位脚本时应使用相对 `SKILL.md` 的路径 `./scripts/archive_team_spec.py`，执行命令时再解析成实际文件路径。

常用参数：

- `--slug {slug}`：指定要归档的需求 slug。
- `--team-spec-dir team-spec`：指定目标项目中的 `team-spec/` 目录，默认是当前工作目录下的 `team-spec`。
- `--reason completed|abandoned|superseded|paused|manual`：归档原因，默认 `manual`。
- `--execute`：正式移动文件；不传时只 dry-run。
- `--json`：输出机器可读 JSON。

## 工作流

1. 确认目标项目根目录和 `team-spec/` 位置。
2. 确认唯一 slug；如果 active 中存在多个 slug 或无法判断，要求用户提供。
3. 运行固定脚本 dry-run，展示将归档的文件、目录和目标路径。
4. 如果 dry-run 结果为空，说明 active 中没有该 slug 的可归档产物，停止并说明原因。
5. 用户确认后追加 `--execute` 正式归档。
6. 归档完成后，输出 `ARCHIVE.md` 路径，并提示新需求可从干净的 `team-spec/active/` 开始。

## 安全要求

- 不覆盖已有 `team-spec/archive/{slug}/`。
- 不归档或删除 `team-spec/active/spec/CONTEXT.md` 与 `team-spec/active/spec/decisions/`。
- 不修改 PRD、规格正文、issue 内容或验收状态，只移动归档并生成归档记录。
- 不执行 `git add`、`git commit`、`git push`。

## 完成标准

- 目标 slug 的 active 产物已移动到 `team-spec/archive/{slug}/`。
- `ARCHIVE.md` 已记录归档时间、原因、来源路径和目标路径。
- `team-spec/active/` 中不再存在该 slug 的过程文件。
- 最终回复说明 dry-run 或 execute 结果，以及是否还有长期共享上下文留在 active。
