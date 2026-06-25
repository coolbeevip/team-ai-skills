# Skill 描述审视与通用改进思路

## 背景

本轮审视范围是 `skills/` 下全部 22 个 `SKILL.md`。目标不是修改技能功能或流程逻辑，而是从描述、触发、章节结构和可维护性角度找出共性问题，为后续低风险优化提供 sprint 输入。

已校验：

- `rtk find skills -maxdepth 3 -name SKILL.md -type f`：覆盖 22 个技能。
- `rtk wc -l skills/*/*/SKILL.md`：当前技能说明合计 4304 行。
- `rtk python3 scripts/check_skills.py`：现有结构校验通过。

## 覆盖清单

| 技能 | 主要观察 |
| --- | --- |
| `team-codebase-brief` | 描述包含输入来源、受众、输出类型和适用场景，信息完整但过长，触发定位容易被稀释。 |
| `team-codebase-onboarding` | 描述同时覆盖功能清单、架构、模块、API、数据、配置、详细设计和 AI 接手上下文，职责边界清楚但发现入口偏重。 |
| `team-codebase-walk` | 描述包含 onboarding 依赖、主动提问、走读、问答、深挖和学习路径，和 `team-codebase-onboarding`、`team-codebase-brief` 的边界需要更显式。 |
| `team-issue-batch-implement` | 描述叠加批量编排、依赖顺序、单 issue 实现、最小实现模式、验证、失败即停和续跑，适合执行但不适合快速匹配。 |
| `team-issue-create-mr-gitlab` | GitLab MR 创建语义清楚，但与 GitHub PR 技能高度镜像，公共描述和平台差异可以标准化。 |
| `team-issue-create-pr-github` | GitHub PR 创建语义清楚，但与 GitLab MR 技能高度镜像，标题、正文、关联 issue 规则可抽成统一描述模板。 |
| `team-issue-implement` | 描述把 issue 输入、行为测试、TDD、最小实现、复用现有代码和验证结果写在一起，容易让触发器同时命中实现和审查类任务。 |
| `team-issue-publish-github` | 描述包含路径、批量/单个、依赖排序、回写、dry-run、幂等和重试，过多执行细节进入 frontmatter。 |
| `team-issue-publish-gitlab` | 与 GitHub 发布技能高度镜像，平台差异清楚，但描述和触发可以统一到同一语义框架。 |
| `team-issue-verify` | 描述同时覆盖验收、PRD、风险、最小实现、diff 简化、过度设计和 ready for PR，职责强但触发范围很宽。 |
| `team-prd-to-alignment` | 描述简洁，但输入状态、输出形式和不适用场景可以更显式，避免和 PRD 固化、issue 拆解混淆。 |
| `team-prd-to-issues` | 描述清楚强调 vertical slice，但文档内出现重复 `## 下一步可选`，章节结构需要清理。 |
| `team-codex-harness` | 描述边界明确，但包含“只沉淀”“不维护团队技能库自身”等负向边界，建议保留在边界章节而不是全部压进 description。 |
| `team-skill-evolve` | 描述加入过度设计、写太多代码、未复用等近期经验，方向正确，但 description 承载了太多具体失败模式。 |
| `team-spec-archive` | 描述相对聚焦，适合作为短描述参考。 |
| `team-spec-refine` | 描述覆盖反复确认、术语、边界、业务规则、验收和上下文/决策更新，信息多但仍在同一需求细化职责内。 |
| `team-spec-review` | 描述清楚，但输出项和完成口径在不同技能中有多种命名，需要统一下游消费预期。 |
| `team-spec-to-prd` | 描述边界清楚，适合保留；可补更明确的不触发场景，避免用户还在访谈阶段时误触发。 |
| `team-tech-debt-analyze` | 描述同时覆盖只读分析、复杂度审计、延迟债务、维护性、稳定性、测试、架构、交付、过度设计、依赖和平台能力，明显过载。 |
| `team-tech-debt-refine` | 描述简洁，和 `team-spec-refine` 模式一致，可作为技术债链路短描述参考。 |
| `team-tech-debt-review` | 描述简洁，职责边界清楚，但完成输出章节命名和其他技能不一致。 |
| `team-tech-debt-to-issues` | 描述清楚，但文档内出现重复 `## 下一步可选`，章节结构需要清理。 |

## 共性问题

### 1. description 过度承担工作流说明

多个技能的 `description` 不只是说明“何时触发”，还塞入路径、输出物、执行策略、安全策略和失败处理。例如 issue 发布类技能在 description 中同时说明 `team-spec/active/{slug}/issues/`、批量/单个、依赖排序、回写、dry-run、幂等和重试。

问题不是内容错误，而是这些细节会降低技能发现质量：模型在做触发匹配时更需要短而稳定的用户意图，而不是完整执行说明。

改进方向：

- `description` 保持一句定位：用户意图 + 核心输入 + 核心输出。
- 路径、dry-run、幂等、续跑、安全要求放回正文对应章节。
- 中英文描述表达同一层级的信息，避免中文很细、英文很泛，或反过来。

### 2. 相邻技能边界依赖正文，frontmatter 不够显式

产品链路、技术债链路、交付链路都有相邻技能：

- `team-spec-refine` / `team-spec-review` / `team-spec-to-prd`
- `team-tech-debt-refine` / `team-tech-debt-review` / `team-tech-debt-to-issues`
- `team-issue-implement` / `team-issue-verify` / `team-issue-create-pr-github` / `team-issue-create-mr-gitlab`
- `team-codebase-onboarding` / `team-codebase-walk` / `team-codebase-brief`

这些技能正文通常有边界说明，但 frontmatter 描述和 triggers 不总是表达“不触发场景”。这会让用户只说“看一下这个需求”“处理这个 issue”“讲一下代码库”时，技能选择更依赖模型临场判断。

改进方向：

- 每个技能增加稳定的边界小节：`适合触发`、`不适合触发`。
- 在 description 中只保留正向触发场景，不写复杂反例。
- 把相邻技能之间的转交条件标准化，例如 `refine -> review -> prd`、`implement -> verify -> create-pr/create-mr`。

### 3. 运行时配置章节命名不一致

当前存在三种相近章节：

- `## 运行时配置`
- `## 运行时语言配置`
- `## 语言约定`

这些章节本质上都在处理语言、访问策略、版本控制或平台偏好，但命名和覆盖范围不同。长期会造成维护成本：新增 `team-spec/config.yml` 字段时，不知道需要同步哪些技能。

改进方向：

- 统一章节名为 `## 运行时配置`。
- 固定子项顺序：语言、访问策略、版本控制、平台偏好。
- 平台类技能保留平台差异，但继承同一套配置语义。

### 4. 输出和完成口径不统一

当前同时存在：

- `## 完成标准`
- `## 完成输出`
- 只有 `## 输出物` 而没有完成口径

有些技能面向执行完成，有些面向报告输出，这种差异合理；但命名不一致会影响自动审计和下游技能引用。例如验证类、评审类、发布类技能对“完成”的含义不同，但可以使用统一结构表达。

改进方向：

- `## 输出物`：列出会生成或更新的文件/远端对象。
- `## 完成标准`：列出何时可以结束本技能。
- `## 最终回复`：列出需要回给用户的摘要格式。

### 5. 重复章节暴露出文档编辑风险

已发现重复标题：

- `skills/delivery/team-prd-to-issues/SKILL.md` 有两个 `## 下一步可选`。
- `skills/tech-debt/team-tech-debt-to-issues/SKILL.md` 有两个 `## 下一步可选`。

这类问题不一定改变功能逻辑，但会削弱技能说明的可信度，也容易让后续维护者在错误位置继续追加内容。

改进方向：

- 在 `scripts/check_skills.py` 增加重复二级标题检查。
- 对 `下一步可选` 这类尾部章节只允许出现一次。
- 将可选下一步分成固定模式：`建议下游技能`、`人工确认事项`、`不自动执行事项`。

### 6. 触发词粒度不均

部分技能触发词偏用户语言，例如“细化需求”“需求不清楚”；部分技能触发词偏内部流程或文件结构，例如 issue 发布、PR/MR 创建类。两类都需要，但比例不均会影响自然语言触发。

改进方向：

- 每个技能至少保留三类 trigger：用户口语、产物驱动、动作驱动。
- 平台镜像技能使用同构触发词，只替换 GitHub/GitLab、PR/MR。
- 增加常见中文表达，例如“帮我发 issue”“把这些草稿发布出去”“这个实现验一下”“准备提 PR”。

### 7. 脚本和安全细节在技能正文中占比偏高

发布、PR/MR、harness、技术债分析等技能包含大量脚本参数、环境变量、安全要求和异常处理。这些内容对执行正确性有价值，但放在主 `SKILL.md` 中会让描述越来越长。

改进方向：

- 保留主 `SKILL.md` 的路由、边界和执行骨架。
- 将脚本参数、远端 API 细节、故障排查放入同目录 `references/` 或脚本 `--help`。
- 主文档只引用相对路径，避免技能安装到业务项目后依赖仓库根路径。

## 建议的改进合同

后续优化每个技能描述时，建议使用同一份“描述合同”，不改变实际功能：

```markdown
## 定位

一句话说明这个技能解决什么用户问题。

## 适合触发

- 用户口语场景。
- 产物或文件场景。
- 动作请求场景。

## 不适合触发

- 应转交给哪个相邻技能。
- 哪些情况需要先澄清。

## 输入物

稳定列出读取的上游产物。

## 输出物

稳定列出生成、更新或发布的产物。

## 运行时配置

语言、访问策略、版本控制、平台偏好。

## 工作流

只保留执行骨架，细节引用辅助文档或脚本。

## 完成标准

列出可结束条件和最终回复要求。
```

## 建议拆成的后续 sprint

1. 描述瘦身：只调整 frontmatter `description` 和 `triggers`，不改正文流程。
2. 章节统一：统一 `运行时配置`、`输出物`、`完成标准`、`最终回复`，清理重复 `下一步可选`。
3. 边界补强：为相邻技能补 `适合触发` 和 `不适合触发`，降低误触发。
4. 脚本说明下沉：把高密度脚本/API/安全细节迁移到相对引用的辅助文档，主 `SKILL.md` 只保留路由。
5. 规则自动化：扩展 `scripts/check_skills.py`，增加重复标题、description 长度、章节命名和 trigger 覆盖检查。

## 验收建议

后续真正改技能时，每一批修改都应满足：

- 不改变技能职责、输入输出和执行逻辑。
- `rtk python3 scripts/check_skills.py` 通过。
- 每个被改技能的 frontmatter 仍包含中文和英文描述。
- 每个相邻技能能从 description 和 triggers 上看出边界。
- 新增辅助文件必须由对应 `SKILL.md` 相对路径引用。
