---
name: team-spec-archive
description: 将已完成、废弃或暂停的单个需求工作区从 active 归档到 archive。Archive one completed, abandoned, or paused requirement workspace from active to archive.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 归档需求
  - 归档 active 需求
  - 结束这个需求
  - 暂停这个需求
  - 归档这个 slug
  - archive spec
  - archive requirement
  - archive active spec
  - close this requirement
  - archive this slug
---

# 需求归档

这个技能用于把 `team-spec/active/{slug}/` 中某个需求 slug 的过程产物移动到 `team-spec/archive/{slug}/`。归档是需求生命周期动作，不负责继续细化、评审、生成 PRD、拆 issue 或实现代码。`team-spec/active/` 允许存在多个未归档需求；归档一个 slug 不应影响其他 slug。

归档只处理指定 slug 的工作区，不移动跨需求共享上下文 `team-spec/CONTEXT.md` 和 `team-spec/decisions/`。

## 触发边界

- 适合触发：用户明确要归档某个已完成、废弃或暂停的 `team-spec/active/{slug}/` 工作区。
- 不适合触发：用户只是开始新需求或存在多个 active slug 时，不要求归档；应让对应产品或交付技能继续处理目标 slug。

## 输入物

必须先确定唯一 slug，来源可以是：

- 用户显式提供的 `{slug}`。
- 明确的 active 文件路径，例如 `team-spec/active/{slug}/spec/refine.md`。
- `team-spec/active/` 中唯一可识别的 slug。

可归档的 active 产物：

- `team-spec/active/{slug}/concept/whitepaper.md`
- `team-spec/active/{slug}/spec/refine.md`
- `team-spec/active/{slug}/spec/reviews.md`
- `team-spec/active/{slug}/spec/CONTEXT.md`
- `team-spec/active/{slug}/spec/decisions/`
- `team-spec/active/{slug}/prd/prd.md`
- `team-spec/active/{slug}/prd/alignment.md`
- `team-spec/active/{slug}/issues/`
- `team-spec/active/{slug}/design/`
- `team-spec/active/{slug}/STATUS.md`

兼容旧布局时，也可以归档 `team-spec/active/spec/refine/{slug}.md`、`team-spec/active/spec/reviews/{slug}.md`、`team-spec/active/prd/{slug}.md`、`team-spec/active/prd/{slug}-alignment.md`、`team-spec/active/issues/{slug}/` 和 `team-spec/active/design/{slug}.md`。

不可归档的全局产物：

- `team-spec/CONTEXT.md`
- `team-spec/decisions/`

如果无法唯一确定 slug，必须停止并要求用户提供 slug 或明确文件路径，不得猜测。如果 `team-spec/archive/{slug}/` 已存在，默认停止，不得覆盖旧归档。

## 输出物

- `team-spec/archive/{slug}/concept/whitepaper.md`
- `team-spec/archive/{slug}/spec/refine.md`
- `team-spec/archive/{slug}/spec/reviews.md`
- `team-spec/archive/{slug}/prd/prd.md`
- `team-spec/archive/{slug}/prd/alignment.md`
- `team-spec/archive/{slug}/issues/`
- `team-spec/archive/{slug}/design/`
- `team-spec/archive/{slug}/STATUS.md`
- `team-spec/archive/{slug}/ARCHIVE.md`

归档完成后，`team-spec/active/{slug}/` 不应再存在。其他 `team-spec/active/{other-slug}/` 工作区必须保留。

## 固定脚本

归档时优先使用本技能目录下的固定脚本：

```text
./scripts/archive_team_spec.py
```

脚本能力：

- 默认 dry-run，只输出将移动的文件和目录。
- `--execute` 时移动对应 slug 的 active 工作区并生成 `ARCHIVE.md`。
- 如果未传 `--slug`，仅在 active 中能唯一识别 slug 时自动推断。
- 如果目标归档目录已存在，停止执行。
- 新布局下移动 `team-spec/active/{slug}/`；旧布局兼容模式只移动同 slug 产物，不移动全局 `team-spec/CONTEXT.md`、`team-spec/decisions/`、旧布局共享 `CONTEXT.md`、`decisions/`、缓存文件或其他无关文件。

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
6. 归档完成后，输出 `ARCHIVE.md` 路径，并说明其他 active 需求未受影响。

## 安全要求

- 不覆盖已有 `team-spec/archive/{slug}/`。
- 新布局下只归档指定 `team-spec/active/{slug}/`；任何布局都不归档或删除 `team-spec/CONTEXT.md` 与 `team-spec/decisions/`；旧布局兼容模式也不归档或删除 `team-spec/active/spec/CONTEXT.md` 与 `team-spec/active/spec/decisions/`。
- 不修改 PRD、规格正文、issue 内容或验收状态，只移动归档并生成归档记录。
- 不执行 `git add`、`git commit`、`git push`。

## 完成标准

- 目标 slug 的 active 产物已移动到 `team-spec/archive/{slug}/`。
- `ARCHIVE.md` 已记录归档时间、原因、来源路径和目标路径。
- `team-spec/active/{slug}/` 中不再存在该 slug 的过程文件。
- 最终回复说明 dry-run 或 execute 结果，以及是否还有其他 active slug 保留。
