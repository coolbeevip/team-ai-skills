# team-spec/config.yml 配置合同

## 目录

1. 配置结构
2. 字段职责
3. 渐进式配置
4. 优先级与兼容性
5. 修改规则

## 配置结构

完整结构示例仅用于说明支持字段，不表示首次初始化必须全部写入：

```yaml
language: zh-CN
version_control:
  language: en-US
  system: git
  trunk_branch: main
  contribution_model: fork-pull
  source_remote: origin
  target_remote: upstream
access_policy:
  mode: default-readonly
  directory_file: team-spec/access_policy/default.md
  user_file_template: team-spec/access_policy/{user_name}.md
writing_style:
  guide: team-spec/STYLE.md
```

## 字段职责

| 字段 | 含义 | 所有者或主要消费者 |
| --- | --- | --- |
| `language` | AI 对话与 refine/review/prd/tasks/design 等需求文档语言 | 产品、技术债、代码库和文档技能 |
| `version_control.language` | Commit、Issue、PR 和 MR 的统一交付语言 | Task 实现和远端交付技能 |
| `version_control.system` | 版本控制系统，例如 `git` | Task 实现和远端交付技能 |
| `version_control.trunk_branch` | 主干分支，例如 `main`、`master`、`develop` | Task 实现、验证和 PR/MR 技能 |
| `version_control.contribution_model` | `fork-pull` 或 `direct` | 推送与 PR/MR 技能 |
| `version_control.source_remote` | 贡献分支默认推送 remote | 推送与 PR/MR 技能 |
| `version_control.target_remote` | Issue、PR 或 MR 面向的 remote | 远端交付技能 |
| `access_policy.mode` | 访问策略模式索引 | 所有需要读写项目文件的技能 |
| `access_policy.directory_file` | 默认目录策略文件路径 | 所有需要读写项目文件的技能 |
| `access_policy.user_file_template` | 协作者策略文件路径模板 | 所有需要读写项目文件的技能 |
| `writing_style.guide` | 公共写作风格文件路径 | 所有生成用户可见内容的技能 |

配置只存机器可读入口，不承载长篇访问规则、产品知识、写作指南正文、token 或密钥。

## 渐进式配置

首次需要稳定语言或写入 `team-spec/` 时，最小配置为：

```yaml
language: zh-CN
```

只有当前操作需要访问边界时才补充 `access_policy`。只有首次执行 Commit、Issue、PR 或 MR 且必需字段无法从 Git 证据唯一推断时，才补充 `version_control`。只有已有公共写作指南时才登记 `writing_style.guide`。

纯对话、只读分析和不依赖稳定配置的预览不得仅因配置不存在而阻塞。

## 优先级与兼容性

对话和需求文档语言：

1. 用户本轮明确指定。
2. 顶层 `language`。
3. 当前操作允许继续时使用用户所用语言；准备长期写入时通过 `team-config-init` 确认并落盘。

版本控制交付语言：

1. 用户对本次 Commit、Issue、PR 或 MR 的明确指定，包括脚本 `--language`。
2. `version_control.language`。
3. 顶层 `language`，兼容旧项目。
4. `en-US`。

旧项目没有 `version_control` 时，交付技能先通过 Git 证据推断当前操作所需字段。无法唯一确定且会阻塞操作时，调用 `team-config-init` 增量补全，不由交付技能直接回写。

交付语言与文档语言不同时，转换标题、说明和摘要；Task ID、commit SHA、代码标识符、命令、路径和专有名词保持原样，不修改 PRD 或 Task 原文。

## 修改规则

- 默认只补充缺失字段，不覆盖既有值。
- 覆盖既有值前必须展示旧值、新值和影响，并获得用户明确确认。
- 临时偏好只对本次操作生效；只有用户同意长期保存时才写入。
- 保留未知字段和未修改内容，避免破坏其他工具扩展。
- 重复键、已知节为非映射结构或无法安全解析时停止并请求人工处理。
- `team-writing-style` 负责风格指南内容；登记或变更 `writing_style.guide` 时仍遵守本配置写入合同。
