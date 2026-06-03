# 扫描摘要 JSON 规范

默认机器摘要输出到当前 `codebase-onboarding/` 目录下的 `scan-summary.json`。只有用户明确要求仓库文档导出时，才输出或同步到 `docs/SCAN_SUMMARY.json`。

基础字段不得删除，可按项目需要扩展。

```json
{
  "generated_at": "",
  "repo_path": "",
  "initial_assumptions": {
    "project_languages": "unspecified",
    "project_type": "unspecified",
    "repo_size": "unspecified"
  },
  "detected_languages": [],
  "detected_project_type": {
    "value": "unspecified",
    "confidence": "low",
    "evidence": []
  },
  "declared_intent_sources": [],
  "intent_reality_gaps": [],
  "repo_size": {
    "files": 0,
    "directories": 0,
    "source_files": 0,
    "is_large_repo": false
  },
  "code_metrics": {
    "total_text_lines": 0,
    "source_lines_by_language": {},
    "largest_text_files": []
  },
  "entry_points": [],
  "routes": [],
  "controllers": [],
  "services": [],
  "data_access_layers": [],
  "config_files": [],
  "env_files": [],
  "build_scripts": [],
  "ci_files": [],
  "docker_files": [],
  "orchestration_files": [],
  "test_files": [],
  "lint_and_quality_files": [],
  "security_configs": [],
  "performance_markers": [],
  "modules": [],
  "public_apis": [],
  "data_models": [],
  "db_schema_sources": [],
  "config_keys": [],
  "environment_variables": [],
  "third_party_services": [],
  "important_files": [],
  "todo_markers": [],
  "git_recent_commits": [],
  "high_churn_files": [],
  "created_files": [],
  "updated_files": [],
  "excluded_paths": [],
  "unknowns": [],
  "verification_checklist": [],
  "human_review_next_steps": []
}
```

## 字段说明

- `generated_at`：ISO 8601 时间。
- `repo_path`：目标仓库绝对路径或用户提供路径。
- `initial_assumptions`：固定记录初始非假设状态。
- `detected_languages`：从扩展名、manifest、构建文件和源码证据识别的语言。
- `detected_project_type`：项目类型，例如 web、service、library、CLI、desktop、monorepo、mixed。证据不足时保持 unspecified。
- `declared_intent_sources`：README、docs、PRD/TRD/SPEC/DESIGN、ROADMAP、ADR 或发布说明等声明意图来源候选。
- `intent_reality_gaps`：人工阅读后补充的声明意图和源码现实偏差；纯脚本可保持空数组。
- `repo_size`：文件数量、目录数量、源码文件数量和大型仓库判断。
- `code_metrics`：文本行数、按语言估算的源码行数和最大文本文件，用于判断规模和阅读风险。
- `entry_points`：入口候选，包含路径、符号、证据和置信度。
- `routes`：路由候选。
- `controllers`：控制器/handler/endpoint 候选。
- `services`：服务层/业务逻辑候选。
- `data_access_layers`：repository/DAO/query/ORM 候选。
- `config_files`：配置文件。
- `env_files`：环境变量文件和模板。
- `build_scripts`：构建、任务、包管理脚本。
- `ci_files`：CI/CD 配置。
- `docker_files`：容器和 compose 文件。
- `orchestration_files`：Kubernetes、Helm、Kustomize、Procfile、serverless 等部署/编排线索。
- `test_files`：测试文件、fixture、mock 和测试配置候选。
- `lint_and_quality_files`：lint、format、typecheck、pre-commit、editorconfig 等质量工具配置候选。
- `security_configs`：安全扫描、依赖审计、CodeQL、Dependabot、Semgrep、Snyk、SBOM 等配置候选。
- `performance_markers`：benchmark、压测、profiling、性能配置和容量测试候选。
- `modules`：模块或子项目清单。
- `public_apis`：公开 API、CLI、消息事件或协议接口。
- `data_models`：实体、DTO、schema、migration、协议数据结构。
- `db_schema_sources`：数据库 schema、migration、ORM 来源。
- `config_keys`：配置键。
- `environment_variables`：环境变量。
- `third_party_services`：外部服务和平台。
- `important_files`：关键文件索引。
- `todo_markers`：TODO/FIXME/HACK 等源码标记候选，包含路径、行号和上下文。
- `git_recent_commits`：最近提交摘要候选；没有 `.git` 或无法读取时保持空数组并写入未知项。
- `high_churn_files`：近期高变更文件候选；用于风险提示，不自动等同于缺陷。
- `created_files`：本次创建的文档。
- `updated_files`：本次更新的文档。
- `excluded_paths`：被跳过或降级处理的路径和原因。
- `unknowns`：未知项和待人工确认事项。
- `verification_checklist`：执行后的检查项。
- `human_review_next_steps`：建议人工复核步骤。

## 生成要求

- JSON 必须是 UTF-8、合法 JSON，不带注释。
- 路径尽量使用仓库相对路径。
- 每个高价值结论尽量包含 `evidence` 字段。
- 置信度统一使用 `high`、`medium`、`low` 或中文文档中的 `高`、`中`、`低`，同一 JSON 内保持一致。
- 如果某字段没有发现内容，保留空数组，不要删除字段。
