# 贡献者指南

感谢参与维护团队技能库。提交变更前，请先阅读根目录 `AGENTS.md`，并遵守其中的技能结构、命名、运行时工作空间、辅助脚本和验证规则。

## 开发环境

本仓库是 Markdown 技能库，没有构建系统或项目级依赖安装流程。基础检查需要：

- Python 3
- Git
- [pre-commit](https://pre-commit.com/)

首次克隆后安装 pre-commit，并安装仓库 Git hook：

```bash
python3 -m pip install pre-commit
pre-commit install
```

安装 hook 后，每次 `git commit` 都会读取仓库中的 `.pre-commit-config.yaml`。

GitHub Actions 会在 main push 和 pull request 上运行同一套检查。远端检查必须通过后才能合并。

## 提交前检查

pre-commit hook 会执行：

```bash
python3 scripts/check_skills.py
git diff --cached --check
```

同时使用官方基础 hooks 检查行尾空格、文件结尾、YAML 和合并冲突标记。

技能检查会验证所有技能的 frontmatter、双语描述、许可、作者、版本、触发词和标准章节。暂存区检查用于发现空白错误。

可以在提交前手动运行全部文件：

```bash
pre-commit run --all-files
```

## 修改技能

- 技能目录名必须与 `SKILL.md` 中的 `name` 一致，并以 `team-` 开头。
- 每个技能必须包含 `触发边界`、`输入物`、`输出物`、`完成标准` 和 `最终回复`。
- `description` 必须包含中文和英文，并保持简洁。
- `triggers` 至少包含 3 条中文和 3 条英文自然语言短语。
- 辅助文件必须由 `SKILL.md` 使用相对路径明确引用。
- 不要把业务项目的真实需求、PRD、风险报告或工程 Task 提交到本仓库。
- 不要在技能文档和脚本中加入本地执行包装器或个人机器路径。

## 修改辅助脚本

修改 Python 脚本后，至少执行语法检查或 `--help`。涉及发布、PR/MR、批处理、幂等或路径解析时，应优先复用技能目录中的确定性脚本，不要临时生成重复实现。

修改根目录 `scripts/_team_common.py` 时，只修改根目录源文件，然后同步并检查 vendored 副本：

```bash
python3 scripts/check_vendored_common.py
python3 scripts/check_vendored_common.py --check
```

敏感信息必须从环境变量或运行时参数读取，不得写入仓库或输出日志。

## 提交要求

- 提交信息使用简洁的祈使句。
- 提交前检查暂存范围，避免混入无关文件。
- 不提交 `team-spec/` 下的真实业务产物。
- Pull Request 应说明修改了哪些技能、修改原因、触发或工作流变化，以及执行过的验证。
