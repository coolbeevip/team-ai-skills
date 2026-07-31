# Platform and Standard Library First

本文件用于最小实现模式。实现、验证或技术债分析时，先检查项目已有能力、标准库、平台能力、数据库和已安装依赖，再考虑新增依赖、自定义抽象或通用框架。

使用边界：

- 平台能力优先不等于拒绝依赖。旧运行环境、兼容性要求、复杂业务规模、成熟安全库或验收标准明确要求时，可以使用依赖。
- 不为了少代码牺牲输入校验、权限、安全、数据一致性、错误处理、可访问性或用户明确要求。
- 先确认目标项目的运行时版本、浏览器支持矩阵、数据库类型和框架约束；不确定时查项目配置或文档。

## JavaScript / TypeScript

| You may think you need | Prefer first | Notes |
| --- | --- | --- |
| `qs` for simple query parsing | `URLSearchParams` | 适合普通 query 读写；复杂嵌套对象再评估库。 |
| `moment` / `dayjs` for display formatting | `Intl.DateTimeFormat` | 适合本地化展示；复杂日期计算再评估现有依赖。 |
| `lodash.groupby` | `Object.groupBy` or small `Map` reducer | 先确认运行时支持；不支持时用局部 reducer。 |
| `lodash.clonedeep` for plain data | `structuredClone` | 适合可结构化克隆的数据；函数、类实例需谨慎。 |
| Custom timeout wrapper | `AbortSignal.timeout` | 适合支持该 API 的 fetch/async cancellation 场景。 |
| `uuid` for browser random ids | `crypto.randomUUID` | 适合现代浏览器和 Node 运行时。 |
| `lodash.debounce` for one local UI use | Existing project helper or tiny local function | 多处复用时优先项目已有 helper。 |

## Browser / HTML / CSS

| You may think you need | Prefer first | Notes |
| --- | --- | --- |
| Date picker library | `<input type="date">` | 先确认设计、i18n 和浏览器支持需求。 |
| Modal library for simple dialog | `<dialog>` | 复杂焦点管理或兼容要求再用既有组件。 |
| Accordion component | `<details>` / `<summary>` | 适合简单展开收起。 |
| Autocomplete package | `<datalist>` | 适合轻量建议列表；复杂远程搜索用现有组件。 |
| Layout utility dependency | CSS grid / flexbox | 先使用现有 CSS 和平台布局能力。 |
| Resize JS listener | Container queries | 适合样式响应容器尺寸的场景。 |
| Tooltip framework for native labels | `title`, accessible text, existing design-system tooltip | 不牺牲可访问性。 |

## Python

| You may think you need | Prefer first | Notes |
| --- | --- | --- |
| Path helper package | `pathlib` | 路径拼接、遍历、扩展名处理优先用标准库。 |
| Small record class library | `dataclasses` | 适合轻量结构化数据；复杂校验再评估现有依赖。 |
| Timezone package for basic zones | `zoneinfo` | Python 3.9+ 可用；旧版本看项目约束。 |
| CLI parser dependency | `argparse` | 简单命令行不新增依赖。 |
| JSON utility dependency | `json` | 标准 JSON 读写优先标准库。 |
| Grouping/chunking helpers | `itertools` / `collections` | 先用标准迭代工具。 |
| Temporary file helper dependency | `tempfile` | 安全临时文件优先标准库。 |

## Database

| You may think you need | Prefer first | Notes |
| --- | --- | --- |
| App-only uniqueness check | Unique constraint / unique index | 应用层校验可保留作体验，数据一致性靠数据库。 |
| Manual referential checks | Foreign key | 先确认迁移和历史数据兼容。 |
| App-only enum/range validation | Check constraint | 不替代用户友好错误，但保护数据边界。 |
| Custom dedupe query loops | Indexes and `ON CONFLICT` / upsert | 按数据库方言确认语法。 |
| Manual ranking in app code | Window functions | 适合分页排名、分组取首项等。 |
| Recursive traversal in app loops | Recursive CTE | 适合数据库支持且数据规模合适的层级查询。 |
| Pagination helper dependency | Existing query builder / SQL `limit` and cursor pattern | 优先沿用项目已有分页约定。 |

## Shell / OS

| You may think you need | Prefer first | Notes |
| --- | --- | --- |
| Custom file search script | `find`, `rg`, existing project scripts | 自动化前先找已有脚本。 |
| Custom text replacement tool | `sed`, `awk`, language stdlib | 注意跨平台差异。 |
| Manual temp path | `mktemp` / language `tempfile` | 避免不安全固定临时路径。 |
| Hand-built shell quoting | Language subprocess array APIs | 不拼接未信任输入。 |
| Custom archive script | `tar`, `zip`, platform tools | 先确认 CI/部署环境可用。 |
| Custom process lookup | `pgrep`, service manager, existing ops script | 不为一次性检查写长期脚本。 |

## Project-Local Capabilities

| You may think you need | Prefer first | Notes |
| --- | --- | --- |
| New permission abstraction | Existing auth/permission helper | 权限逻辑必须复用一致入口。 |
| New API response wrapper | Existing handler/response pattern | 保持错误结构和状态码一致。 |
| New form validation layer | Existing schema/form helper | 不创建第二套校验语义。 |
| New UI primitive | Existing design-system component | 小 UI 需求贴合现有组件。 |
| New fixture factory | Existing test fixture/builder | 测试数据模式保持一致。 |
| New migration helper | Existing migration scripts and conventions | 数据变更先找项目惯例。 |

## Platform Capability Example Tasks

1. URL query task: For simple query parsing or mutation, use `URLSearchParams` or the project's existing router/query helper before considering `qs`.
2. Date display task: For locale-aware date display, use `Intl.DateTimeFormat` or the project's existing date formatter before considering `moment` or `dayjs`.
3. Uniqueness task: For persistent uniqueness, add or reuse a database unique constraint/index before relying on app-only duplicate checks.
