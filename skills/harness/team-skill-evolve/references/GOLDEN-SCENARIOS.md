# Lean Implementation Golden Scenarios

这些黄金场景用于验证最小实现模式是否真的减少过度设计，同时不破坏正确性、安全和验收标准。它们不是业务产物，不要求在本技能库中实现代码；用于人工回归、技能演进复盘和 benchmark 记录。

使用方式：

- 修改 `team-issue-implement`、`team-issue-verify`、`team-tech-debt-analyze`、`team-skill-evolve` 或 `PLATFORM-STDLIB.md` 后，至少人工跑 3 个场景。
- 不只比较代码行数。必须同时记录新增依赖数、新增文件数、验收是否通过、安全边界是否保留。
- 如果目标项目缺少对应技术栈，用同等复杂度的本地场景替代，并保留替代原因。

## 指标口径

| Metric | Meaning |
| --- | --- |
| LOC delta | 相对常见过度设计方案的代码行数变化，只作为参考。 |
| New files | 新增文件数；新增通用层、配置层和抽象层应单独说明。 |
| New dependencies | 新增 runtime/dev dependency 数量；新增依赖必须有验收或代码证据。 |
| Acceptance passed | 是否满足任务验收标准。 |
| Safety preserved | 输入校验、权限、数据一致性、错误处理、可访问性等边界是否保留。 |
| Reuse evidence | 复用了哪些 helper、组件、标准库、平台能力、数据库能力或已有依赖。 |

## Scenario 1: Form Date Input

- Task: Add a date input to a form and submit the selected date.
- Existing context: The project already uses native form controls and server-side validation.
- Common over-engineered result: Add a date-picker dependency, theme wrapper, adapter layer, and new date utility file.
- Expected lean result: Use `<input type="date">`, existing form component styling, and existing validation path.
- Correctness acceptance:
  - User can select and submit a date.
  - Server receives the expected date format.
  - Existing validation errors still render correctly.
- Safety acceptance:
  - Server-side validation remains authoritative.
  - Accessibility label and error association are preserved.
- Metrics to record: LOC delta, new files, new dependencies, acceptance passed, safety preserved.

## Scenario 2: URL Query Parsing

- Task: Read `page`, `sort`, and `filter` from URL query parameters.
- Existing context: The app already runs in a modern browser or Node runtime with URL APIs.
- Common over-engineered result: Add `qs`, a generic query parser service, and custom serialization rules.
- Expected lean result: Use `URLSearchParams` or the project's existing router query helper.
- Correctness acceptance:
  - Missing parameters get existing defaults.
  - Invalid values are rejected or normalized.
  - Existing navigation behavior is unchanged.
- Safety acceptance:
  - Query values are not trusted as permissions or raw HTML.
  - Input validation remains in place.
- Metrics to record: LOC delta, new files, new dependencies, acceptance passed, safety preserved.

## Scenario 3: Python Config Parsing

- Task: Add a small CLI option and read a JSON config file.
- Existing context: The script already uses Python standard library modules.
- Common over-engineered result: Add a CLI framework and config package for one option.
- Expected lean result: Use `argparse`, `json`, `pathlib`, and existing script conventions.
- Correctness acceptance:
  - CLI help shows the new option.
  - Missing file and invalid JSON produce clear errors.
  - Existing options keep working.
- Safety acceptance:
  - Paths are resolved safely.
  - Secrets are not printed in errors.
- Metrics to record: LOC delta, new files, new dependencies, acceptance passed, safety preserved.

## Scenario 4: Simple Cache

- Task: Cache a deterministic expensive lookup inside one service.
- Existing context: The project has an existing cache helper or language-level memoization utility.
- Common over-engineered result: Add a cache abstraction, backend adapter, config section, and metrics surface before scale requires it.
- Expected lean result: Use the existing cache helper, standard library memoization, or a local bounded cache with clear invalidation.
- Correctness acceptance:
  - Cache hit and miss behavior are covered by tests.
  - Invalidation or TTL follows existing project conventions.
  - Behavior remains correct when cache is empty.
- Safety acceptance:
  - User-specific or permission-sensitive data is not shared across users.
  - Cache cannot grow without bound unless scope proves it is safe.
- Metrics to record: LOC delta, new files, new dependencies, acceptance passed, safety preserved.

## Scenario 5: API Bug Fix

- Task: Fix an API bug where two callers receive inconsistent normalized status values.
- Existing context: Both callers use a shared normalization helper or should use one.
- Common over-engineered result: Patch each caller separately, add caller-specific conditionals, and introduce a new response wrapper.
- Expected lean result: Fix the shared root normalization path and add one behavior regression test.
- Correctness acceptance:
  - Both affected callers now return consistent values.
  - Existing response format remains compatible.
  - Regression test fails before the fix and passes after.
- Safety acceptance:
  - Authorization and error handling paths are unchanged.
  - No unrelated response fields are modified.
- Metrics to record: LOC delta, new files, new dependencies, acceptance passed, safety preserved.

## Scenario 6: Data Uniqueness

- Task: Ensure a user cannot create duplicate names inside the same workspace.
- Existing context: The data is persisted in a relational database with migrations.
- Common over-engineered result: Add app-only duplicate checks in several service methods and still allow races.
- Expected lean result: Add or reuse a database unique constraint/index, keep app-level validation for user-friendly errors if needed.
- Correctness acceptance:
  - Duplicate names are rejected reliably, including concurrent requests.
  - Existing records are migrated or handled safely.
  - User receives the existing style of validation error.
- Safety acceptance:
  - Migration is reversible or has an explicit rollback/mitigation plan.
  - Existing data conflicts are detected before enforcing the constraint.
- Metrics to record: LOC delta, new files, new dependencies, acceptance passed, safety preserved.

## Scenario 7: CSV Export

- Task: Export a small admin table to CSV.
- Existing context: The backend language has CSV support or the project already has an export helper.
- Common over-engineered result: Add a spreadsheet generation dependency, background job framework, and generic export service for a small synchronous table.
- Expected lean result: Use standard CSV support or an existing export helper, with proper escaping and content type.
- Correctness acceptance:
  - Headers and rows are exported in the requested order.
  - Commas, quotes, and newlines are escaped correctly.
  - Empty result sets still produce a valid file.
- Safety acceptance:
  - Permissions are checked before export.
  - Sensitive fields are not included unless explicitly required.
- Metrics to record: LOC delta, new files, new dependencies, acceptance passed, safety preserved.

## Scenario 8: Grouped List Display

- Task: Group a list of items by status for display.
- Existing context: The list is already loaded in memory and small enough for local grouping.
- Common over-engineered result: Add a generic collection utility package or global data transformation layer.
- Expected lean result: Use `Object.groupBy`, a small `Map` reducer, Python `itertools`/`collections`, or an existing project helper depending on stack.
- Correctness acceptance:
  - Items appear in the correct groups.
  - Empty and unknown statuses behave as specified.
  - Existing sort order is preserved if required.
- Safety acceptance:
  - Untrusted labels are escaped by existing rendering path.
  - No hidden permission filtering is bypassed.
- Metrics to record: LOC delta, new files, new dependencies, acceptance passed, safety preserved.
