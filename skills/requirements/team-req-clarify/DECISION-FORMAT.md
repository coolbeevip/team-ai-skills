# 产品决策记录格式

产品决策记录存放在 `team-spec/requirements/decisions/`，按顺序编号：

```text
0001-short-slug.md
0002-short-slug.md
```

只有在第一个决策确实需要记录时才创建目录。

## 模板

```md
# 简短决策标题

我们决定{决策内容}，因为{原因}。这个决策重要，是因为{产品影响}。
```

可选章节只在有价值时添加：

- `Status`：proposed、accepted、deprecated、superseded by 000N。
- `Considered Options`：值得未来记住的备选方案。
- `Consequences`：对用户、运营、发布或未来范围的非显性影响。

## 记录标准

只记录难以反悔、没有上下文会显得奇怪、并且来自真实取舍的决策。显而易见、临时性或更适合写进 PRD 正文的内容不要记录。
