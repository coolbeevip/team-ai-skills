# Team Spec Workspace

`team-spec/` 是技能协作的统一工作空间。技能运行时应优先在这里读取上游产物并写入自己的输出物。

## Layout

```text
team-spec/
├── requirements/
│   ├── CONTEXT.md
│   ├── decisions/
│   ├── prd/
│   └── risks/
└── engineering/
    └── issues/
```

- `team-spec/requirements/`：需求角色工作空间，保存澄清结论、术语上下文、产品决策、PRD 和风险报告。
- `team-spec/engineering/`：工程角色工作空间，保存工程拆解、issue 草稿和实现相关计划。

目录按需创建。不要创建空产物文件。
