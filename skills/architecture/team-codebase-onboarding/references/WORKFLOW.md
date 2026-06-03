# 扫描与知识提取工作流

## 目录

- 1. 初始前提
- 2. 允许修改范围
- 3. 一级来源优先级
- 4. 阶段一：仓库盘点与声明意图
- 5. 阶段二：结构识别
- 6. 阶段三：知识提取
- 7. 阶段四：成文与索引
- 8. 输出验证与修复循环
- 9. 常见误判防护
- 10. 证据不足处理
- 11. 最终回复

## 1. 初始前提

开始执行时必须采用以下前提：

- 项目语言：未指定。
- 项目类型：未指定。
- 仓库规模：未指定。
- 是否为大型仓库：未知，但流程必须支持大型仓库。

只有扫描到明确证据后，才可把“未指定”更新为“已检测到”。证据不足时保持“未指定”“未确认”或“待人工确认”。

## 2. 允许修改范围

执行期间默认只读目标仓库。默认只允许写入：

- 目标项目根目录 `team-spec/active/{slug}/design/codebase-onboarding/`。

只有用户明确要求仓库文档导出时，才允许写入目标项目 `docs/**` 和根目录 `AGENTS.md`。禁止修改源代码、测试代码、构建配置、部署配置、迁移脚本和业务文件。若发现已有 `docs/` 或 `AGENTS.md`，只能增量更新相关文档，不能删除无关内容。

## 3. 一级来源优先级

按以下优先级建立证据链。

第一优先级：

- `README*`。
- 声明意图文档：`docs/` 下的 PRD、TRD、SPEC、DESIGN、ARCHITECTURE、ROADMAP、RFC、ADR、产品说明、需求说明和技术方案。现有文档必须标注可能过时，并在源码对照后确认或修正。
- 包管理和依赖清单：`package.json`、`pnpm-lock.yaml`、`yarn.lock`、`package-lock.json`、`requirements.txt`、`pyproject.toml`、`poetry.lock`、`Pipfile`、`go.mod`、`go.sum`、`Cargo.toml`、`pom.xml`、`build.gradle*`、`settings.gradle*`、`Gemfile`、`composer.json`、`mix.exs`、`*.csproj`。
- 构建和任务文件：`Makefile`、`Taskfile*`、`justfile`、`turbo.json`、`nx.json`。
- 容器和部署：`Dockerfile*`、`docker-compose*`、`compose.yaml`。
- CI/CD：`.github/workflows/*`、`.gitlab-ci.yml`、`Jenkinsfile`、`azure-pipelines.yml`。
- 环境和配置模板：`.env*`、`*.example`、`config/*`、`application*.yml`、`application*.properties`、`settings.*`。
- 数据库线索：`migrations/`、`schema.sql`、`db/`、`prisma/`、`models/`、ORM 实体定义。
- API 契约：`openapi.*`、`swagger.*`、`proto/`、GraphQL schema、路由配置。

第二优先级：

- 入口文件、路由文件、控制器、服务层、仓储层、领域模型。
- 导入/依赖图、模块边界、monorepo 工作区配置。
- 调试配置：`.vscode/launch.json`、IDE 配置、脚本参数。

第三优先级：

- 代码注释。
- 示例脚本、样例配置。
- 现有 `docs/` 内容。必须标注可能过时。

## 4. 阶段一：仓库盘点与声明意图

1. 递归扫描仓库目录，建立文件索引。
2. 对大型或疑似大型仓库采用先粗后细策略：
   - 先识别顶层目录、工作区、子项目和核心清单文件。
   - 再按模块或子项目深入。
   - 优先阅读入口与配置，再读业务骨架，再读实现细节。
3. 可使用只读探索型子任务并行扫描模块；无法并行时顺序执行。
4. 默认忽略或降级处理大体积/生成型目录，但记录其存在：
   - `.git/`、`node_modules/`、`vendor/`、`dist/`、`build/`、`target/`、`.next/`、`.nuxt/`、`coverage/`、`out/`、`bin/`、`obj/`、`Pods/`、`DerivedData/`、`__pycache__/`、`.venv/`、`venv/`。
5. 对用户提供的排除模式也要写入排除说明。

建议优先运行 `./scripts/scan_codebase.py` 生成基础扫描 JSON，再人工补充深度结论。

扫描后必须先形成“声明意图”摘要，再进入深度源码阅读：

- 从 README、现有 docs、PRD/TRD/SPEC/DESIGN/ROADMAP/RFC/ADR、发布说明和示例中提取项目声称要解决的问题、目标用户、主要能力、非目标和运行方式。
- 在 `project-overview.md`、`analysis-plan.md` 或 `docs/README-overview.md` 中记录“声明意图”和来源。
- 后续源码阅读必须对照声明意图，记录已被源码支持、源码不支持、源码现实不同、证据不足和需要用户确认的事项。
- 若用户指定关注范围，仍先做全局轻量扫描；关注范围可以获得更深文档，非关注范围也必须保留基础索引、未知项和风险提示。

## 5. 阶段二：结构识别

识别并记录以下结构。不存在时写“未检测到”：

- 入口点：`main`、`index`、`app`、`server`、`bootstrap`、CLI 入口、job/scheduler 入口。
- 路由与 API 定义。
- 控制器、handler、endpoint 层。
- 服务层或业务逻辑层。
- 数据访问层、repository、DAO、query、ORM。
- 配置体系与配置优先级。
- 环境变量与密钥占位。
- 构建脚本、启动脚本、测试脚本、lint/typecheck 脚本。
- 任务调度、队列消费者、异步 worker、cron。
- 数据模型、实体、DTO、schema、migration。
- 第三方服务：数据库、缓存、消息队列、对象存储、搜索、鉴权、监控、支付、短信、邮件、地图等。
- 部署线索：Docker、K8s、Procfile、systemd、serverless、cloud 配置。

## 6. 阶段三：知识提取

从代码与配置中提取：

- 模块名称、相对路径、职责。
- 模块之间的依赖方向与调用关系。
- 公开 API：HTTP、RPC、GraphQL、CLI、消息主题、事件订阅。
- 关键函数/类签名：入口函数、导出接口、控制器、服务、仓储、核心领域对象。
- 数据模型、关键字段、数据库表、关系、索引、迁移来源。
- 配置键、默认值、覆盖顺序、环境变量映射。
- 第三方依赖及用途。
- 运行、构建、测试、调试方式。
- 高风险修改点和容易漏掉的文件/流程。
- 近期提交、高变更文件、TODO/FIXME/HACK 标记、安全配置、性能/压测/benchmark 线索和测试缺口。

大型仓库不必穷举低价值私有工具函数，优先覆盖入口、导出接口、核心流程和高风险模块。

## 7. 阶段四：成文与索引

写文档前读取 `OUTPUT-SPEC.md` 并确认输出范围：

- 默认生成 `team-spec/active/{slug}/design/codebase-onboarding/` 下的分层接手文档和每个功能的详细设计。
- 只有用户明确要求仓库文档导出时，才额外生成或改写 `docs/` 文档集、`docs/SCAN_SUMMARY.json`、操作日志、最终报告，并创建或更新根目录 `AGENTS.md` 文档索引区。

成文时优先使用 `assets/templates/` 下的模板：

- 模板提供章节、表格和证据栏位；不能把模板占位当成已确认事实。
- 默认产物使用 `assets/templates/onboarding/`；可选仓库文档导出使用 `assets/templates/docs/`。
- `Core` 字段必须尽力填充；`Extended` 字段在大型仓库、monorepo、通信系统、用户关注范围或证据明显时填充。
- 证据不足时保留 `[TODO]`，需要用户业务判断时保留 `[ASK USER]`。
- 填写后删除无关占位文本，避免交付空模板。

所有 Markdown 文档都必须包含：

- 执行摘要。
- 文档元信息。
- 正文。
- 来源文件。
- TODO / 未知项。

能画图时优先使用 Mermaid。命令示例必须来自仓库证据；若只是推测，必须标注“推测”。

## 8. 输出验证与修复循环

最终回复前必须执行一轮验证修复：

1. 按 `OUTPUT-SPEC.md` 检查必需文件是否齐全，路径是否符合允许输出范围。
2. 按模板检查每个 Markdown 是否包含执行摘要、文档元信息、正文、来源文件、TODO/未知项。
3. 检查所有非平凡结论是否有来源文件；没有来源时必须降级为“推断”或 `[TODO]`。
4. 检查“声明意图 vs 源码现实”是否已记录，偏差是否进入未知项或风险项。
5. 检查 `SCAN_SUMMARY.json` 或 `scan-summary.json` 是否包含新增/更新文件、排除路径、未知项、风险信号和人工复核建议。
6. 若任何检查失败，继续补扫、补写或显式降级，不要直接交付。

## 9. 常见误判防护

- README 和旧 `docs/` 是意图来源，不是最终事实来源；必须用源码、配置或测试对照。
- 不要从 `dist/`、`build/`、`target/`、`coverage/`、生成代码和二进制产物总结源码约定。
- `.env.example`、配置模板和 CI 往往比 README 更能反映实际运行要求，但密钥值不得写入文档。
- `devDependencies`、测试依赖和工具链依赖不能直接当作生产运行栈。
- 测试名、fixture、Fake/Mock 可作为功能候选证据，但正式功能必须回到生产源码或明确标注为测试反推。
- TODO/FIXME/HACK、近期提交和高变更文件是风险信号，不自动等同于缺陷；必须写清证据和影响范围。
- 缺少测试不等于功能不存在；只能写“未检测到测试证据”或“验证路径未确认”。

## 10. 证据不足处理

按以下顺序处理未知项：

1. 继续在仓库内寻找一级来源。
2. 若仍不足，基于代码做推断，并明确标注“推断”。
3. 若推断不稳妥，写 `[TODO]`、`未确认` 或 `待人工确认`。
4. 不要因为缺少信息而中止整个任务。
5. 除非完全无法访问仓库或没有写入允许目录的权限，否则不要向用户追问。

## 11. 最终回复

最终回复使用中文，并包含：

- 本次结果概览。
- 创建/更新文件清单。
- 验证清单。
- 声明意图与源码现实的关键差异。
- 待人工复核的高风险项。
- 下一步建议。
- JSON 摘要位置。
