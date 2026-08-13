# 工作区状态格式

`team-spec/active/{slug}/STATUS.md` 只记录整个工作区的生命周期状态，不承载阶段评审、Task 交付、风险、成本、里程碑或沟通台账。

## 模板

```md
# Workspace Status

Status: refining
```

## 状态值

产品需求链路只使用：

- `concept-drafting`
- `concept-review`
- `concept-ready`
- `refining`
- `spec-ready`
- `prd-ready`
- `implementing`
- `paused`
- `blocked`

## 更新规则

- 只在工作区生命周期发生变化时更新。
- 阶段评审结果写入对应阶段报告，不写入 `STATUS.md`。
- Task 状态写入对应 Task 文件，不写入 `STATUS.md`。
- 项目进度、风险、证据、里程碑、成本和沟通记录写入 `design/project-dashboard.md`。
