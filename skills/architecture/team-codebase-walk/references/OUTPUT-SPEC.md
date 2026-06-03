# 输出规范

## 目录

- 1. 输出目录
- 2. 文档类型
- 3. 模板映射
- 4. 通用写作要求
- 5. 完成校验

## 1. 输出目录

默认写入：

```text
team-spec/active/{slug}/design/codebase-walk/
```

目录结构：

```text
codebase-walk/
├── question-index.md
├── sessions/
│   └── {yyyy-mm-dd}-{topic}.md
└── deep-dives/
    └── {topic}.md
```

不要写入 `codebase-onboarding/`，也不要修改业务源码。

## 2. 文档类型

### `question-index.md`

用于累计记录问题和走读状态。

至少包含：

| 编号 | 日期 | 主题 | Feature | 用户问题 | 类型 | 状态 | 产物 | 后续问题 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

### `sessions/{yyyy-mm-dd}-{topic}.md`

用于记录一次走读会话。

适合：

- 单模块理解。
- 单功能解释。
- 修改路径梳理。
- 学习路径建议。
- 用户问题的可追溯回答。

### `deep-dives/{topic}.md`

用于记录需要跨模块或跨文件追踪的专题深挖。

适合：

- 请求/任务/消息/数据流追踪。
- 复杂功能实现链路。
- 调试路径。
- 风险和联动分析。
- 修改前影响面分析。

## 3. 模板映射

| 输出文件 | 模板 |
| --- | --- |
| `question-index.md` | `assets/templates/question-index.md` |
| `sessions/{yyyy-mm-dd}-{topic}.md` | `assets/templates/session.md` |
| `deep-dives/{topic}.md` | `assets/templates/deep-dive.md` |

模板是骨架，不是事实来源。填充后删除无关占位。

## 4. 通用写作要求

每个文档必须包含：

- 走读主题。
- 用户关注点。
- 主动提问和用户反馈。
- 选中的 feature 编号、名称、功能域和置信度。
- 设计灵魂和场景：设计意图、服务对象、触发场景、问题边界、成功信号和异常场景。
- 当前走读层级：L0 设计灵魂与场景、L1 概览、L2 入口调用链、L3 数据/配置/接口、L4 测试验证或 L5 修改影响面。
- 本次结论。
- 建议阅读路径。
- 核心解释或实现链路。
- 来源文件。
- 风险和易误解点。
- `[TODO]` 未确认项。
- `[ASK USER]` 需要用户确认项。

来源文件表建议：

| 路径 | 符号/对象 | 用途 | 证据类型 |
| --- | --- | --- | --- |

证据类型使用：

- onboarding 文档结论。
- 源码显式证据。
- 测试/配置证据。
- 代码推断。
- 待确认。

下一轮问题建议必须是具体选项，不要只写“继续提问”。

## 5. 完成校验

完成前检查：

- 文档路径位于 `team-spec/active/{slug}/design/codebase-walk/`。
- 问题类型和用户关注点已记录。
- 主动提问、用户反馈、选中的 feature 和走读层级已记录。
- 设计灵魂和场景已在源码细节前说明。
- 已引用相关 onboarding 产物或说明缺失。
- 已回到源码、配置或测试补强关键结论。
- 结论、推断、TODO 和 ASK USER 已区分。
- `question-index.md` 已创建或建议更新。
