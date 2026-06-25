# Lean Implementation Benchmark Template

本模板用于记录最小实现模式的轻量 benchmark。它衡量“是否减少不必要复杂度”，但不把少代码当成唯一目标。

## Benchmark Limits

- 结果只能说明当前场景和当前项目约束下的表现，不能证明所有任务都应极简。
- LOC delta、文件数和依赖数只是复杂度信号；正确性、安全和验收标准优先级更高。
- 如果验收标准要求完整方案，更多代码或依赖可能是正确结果。
- 人工判断必须写证据：现有 helper、平台能力、数据库约束、测试结果或项目约定。

## Run Metadata

| Field | Value |
| --- | --- |
| Date | YYYY-MM-DD |
| Repository | `{repo}` |
| Skill Version / Commit | `{commit}` |
| Runner | `{human or agent}` |
| Scenarios Run | `{scenario ids}` |
| Notes | `{constraints, skipped checks, replacement scenarios}` |

## Result Table

| Scenario | Baseline Over-Engineering | Lean Expected Result | LOC Delta | New Files | New Dependencies | Acceptance Passed | Safety Preserved | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form Date Input | {summary} | {summary} | {n/a or number} | {count} | {count} | yes/no | yes/no | `{path}` / `{test}` / note |
| URL Query Parsing | {summary} | {summary} | {n/a or number} | {count} | {count} | yes/no | yes/no | `{path}` / `{test}` / note |
| Python Config Parsing | {summary} | {summary} | {n/a or number} | {count} | {count} | yes/no | yes/no | `{path}` / `{test}` / note |

## Scenario Record

```md
### {Scenario Name}

- Task:
- Existing context:
- Baseline over-engineering:
- Lean result:
- Reuse evidence:
- Correctness acceptance:
  - [ ] ...
- Safety acceptance:
  - [ ] ...
- Metrics:
  - LOC delta:
  - New files:
  - New dependencies:
  - Acceptance passed:
  - Safety preserved:
- Commands or checks:
  - `{command}`: passed / failed / not run
- Outcome:
  - pass / needs skill change / invalid scenario
- Notes:
```

## Pass Criteria

A benchmark run is useful only when:

- At least 3 scenarios were run manually.
- Each scenario records correctness acceptance and safety acceptance.
- Any reduced LOC/new files/new dependencies are tied to concrete reuse or platform capability evidence.
- Any failure leads to a specific skill change proposal or a note explaining why the scenario is invalid for the project.
