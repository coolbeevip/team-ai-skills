---
name: team-config-init
description: 初始化、校验并增量补全 team-spec/config.yml，集中管理语言、版本控制、访问策略和写作风格入口。Initialize, validate, and safely complete shared team-spec project configuration.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 初始化团队配置
  - 创建 team-spec 配置
  - 补全项目运行时配置
  - initialize team config
  - create team-spec config
  - complete project configuration
---

# 团队配置初始化

集中创建、校验和增量补全目标项目根目录的 `team-spec/config.yml`。只收集当前操作必需的字段，不用一次性问完所有配置，也不覆盖用户已有配置。

## 触发边界

- 适合触发：用户显式要求初始化配置；其他技能准备写入、提交或执行远端操作，但配置文件不存在或缺少必需字段。
- 不适合触发：纯对话、只读分析或仅展示预览且不依赖稳定配置时继续原技能；建立公共写作指南使用 `team-writing-style`。

## 配置所有权

- 本技能是 `team-spec/config.yml` 结构、初始化、校验和增量补全的唯一入口。
- 其他技能只声明当前操作需要哪些字段；不得自行创建、补全或回写配置。
- `team-writing-style` 仍负责写作指南内容，但通过本技能安全登记或更新 `writing_style.guide`。
- 完整字段、默认值、优先级和兼容规则见 [CONFIG-SCHEMA.md](./references/CONFIG-SCHEMA.md)。准备配置前必须读取该文件。

## 渐进式初始化

按当前任务选择最小配置范围：

| 范围 | 何时需要 | 最少字段 |
| --- | --- | --- |
| 基础 | 首次需要稳定语言或写入 `team-spec/` | `language` |
| 访问策略 | 当前操作受目录权限约束 | `access_policy.mode` 及策略文件入口 |
| 版本控制 | Commit、Issue、PR 或 MR | `version_control.language`；当前操作无法从 Git 证据唯一推断的其他字段 |
| 写作风格入口 | 已有或新建公共风格指南 | `writing_style.guide` |

不要因为未来可能用到某字段而提前询问。可以从 Git 或现有项目事实安全推断的字段先展示证据；只有无法唯一确定且会阻塞当前操作时才询问用户。

校验范围必须显式区分：

- 用户单独调用本技能初始化或全面检查项目配置时，使用 `all` 范围；项目基线至少包含 `language` 和 `version_control.language`。
- 由其他技能触发时，只使用当前操作需要的范围，例如只写需求文档使用 `basic`，准备 commit 使用 `basic` 和 `version-control`。
- 无论选择哪个范围，只要配置中已经出现 `access_policy` 或 `writing_style`，都要校验该节必需字段及具体文件引用，不能把悬空引用视为有效配置。
- 最终回复必须说明已检查哪些范围；不得把“当前范围无文本差异”表述为“整个配置已完成”。

## 固定脚本

使用：

```text
./scripts/init_team_config.py
```

脚本默认 dry-run，不写文件：

```sh
python3 {skill_dir}/scripts/init_team_config.py --language zh-CN --json
```

用户单独要求初始化或全面检查时：

```sh
python3 {skill_dir}/scripts/init_team_config.py --scope all --json
```

补全版本控制配置：

```sh
python3 {skill_dir}/scripts/init_team_config.py \
  --version-control-language en-US \
  --system git \
  --trunk-branch main \
  --source-remote origin \
  --target-remote upstream \
  --json
```

用户确认 dry-run 差异后才正式写入：

```sh
python3 {skill_dir}/scripts/init_team_config.py --language zh-CN --execute
```

主要参数：

- `--path team-spec/config.yml`
- `--language zh-CN`
- `--version-control-language en-US`
- `--system git`
- `--trunk-branch main`
- `--contribution-model fork-pull`
- `--source-remote origin`
- `--target-remote upstream`
- `--access-mode default-readonly`
- `--directory-file team-spec/access_policy/default.md`
- `--user-file-template 'team-spec/access_policy/{user_name}.md'`
- `--writing-style-guide team-spec/STYLE.md`
- `--scope basic|version-control|access-policy|writing-style|all`：可重复；单独调用本技能时使用 `all`，由下游技能触发时只传当前必需范围。
- `--overwrite`：只在用户确认替换既有值后使用。
- `--execute`：执行已展示的写入计划。
- `--json`

脚本只处理配置中约定的一层映射，保留未知字段和未修改内容。发现重复键、非法根结构、字段冲突或无法安全合并的结构时停止，不尝试重写整个文件。校验不完整时退出码为 `2`，JSON 中返回 `validation.status: incomplete`、缺失字段和缺失文件；此时即使 `action` 为 `unchanged` 也不得宣称配置有效，`--execute` 也不会写入，并返回 `write_status: blocked-incomplete`。

## 工作流

1. 确认校验范围：用户单独调用时使用 `all`；由其他技能触发时使用当前操作的最小范围。
2. 读取 `CONFIG-SCHEMA.md`、现有 `team-spec/config.yml` 和可用于推断的项目证据。
3. 配置不存在时，只询问当前范围无法推断的最少字段；存在时只找缺失或冲突字段。
4. 运行脚本 dry-run，展示将创建、补全、保持或冲突的字段和文本差异。
5. 存在冲突时说明旧值、新值及影响；未获用户确认不得使用 `--overwrite`。
6. 等用户确认当前差异后，以相同参数追加 `--execute`。
7. 重新读取配置并验证所需字段、已配置的具体文件引用、未知字段和未修改内容均符合预期。
8. 返回原技能继续执行；本技能不代替原业务技能。

## 安全合同

- 默认 dry-run；用户确认前不得写入。
- 创建父目录只限目标配置路径的父目录。
- 不删除未知字段、注释或用户已有配置。
- 不把临时语言偏好自动写成长期配置。
- 不从远端地址、用户名或目录名猜测组织政策。
- 不自动创建空的访问策略或写作指南；具体文件缺失时将配置判定为不完整，等待用户提供内容或确认移除对应配置。
- 不写 token、密钥、账号密码或个人数据。
- 不创建 slug、PRD、Task、分支、commit、Issue、PR 或 MR。

## 输入物

- 用户本轮明确配置偏好。
- 目标项目现有 `team-spec/config.yml`（如果存在）。
- 当前操作声明的必需字段。
- 可只读获取的 Git 主干、remote 和贡献模式证据。
- 已存在的访问策略文件或公共写作指南路径。

## 输出物

- dry-run 配置计划和统一差异。
- 用户确认后创建或增量更新的 `team-spec/config.yml`。
- 配置冲突、缺失字段和未执行项说明。
- 供所有读取 `team-spec/config.yml` 的技能使用的项目级配置。

## 完成标准

- 只配置当前操作需要的字段。
- 写入前已经展示 dry-run 差异并获得用户确认。
- 既有值仅在用户明确确认后覆盖。
- 未知字段和未修改内容保持不变。
- 配置可被当前下游技能读取，且没有写入敏感信息。
- 校验结果为 `valid`，不存在已配置但缺失的具体文件引用。

## 最终回复

- 说明配置是新建、补全、保持不变还是因冲突停止。
- 明确列出已校验范围，并区分 YAML 的 `action` 与整体 `validation.status`。
- 列出本次涉及的字段和配置路径。
- 说明 dry-run 与正式写入结果。
- 若由其他技能触发，提示返回原技能继续；不要自行启动业务流程。
