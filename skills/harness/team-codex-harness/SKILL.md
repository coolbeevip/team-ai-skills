---
name: team-codex-harness
description: 维护具体代码项目中的 Codex harness，包括 AGENTS.md 入口、项目任务地图、命令、验证路径和失败模式；不维护团队技能库自身。Maintain a Codex harness inside a concrete code project, including AGENTS.md entry points, project task maps, commands, verification paths, and failure patterns; it does not maintain the team skill library itself.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 维护 Codex harness
  - 改进 AGENTS.md
  - Codex 看不懂项目
  - Codex 不知道怎么验证
  - 沉淀 Codex 失败经验
  - Codex 项目接入
  - maintain Codex harness
  - improve AGENTS.md
  - Codex project onboarding
  - document Codex workflow
  - fix Codex project context
  - update Codex verification
---

# Codex Harness 维护

这个技能用于让一个具体代码项目更适合 Codex 接手工作。它维护项目级 Codex harness，把会影响 Codex 理解项目、修改代码、运行命令、完成验证和处理失败的知识，沉淀到 `AGENTS.md` 和项目内的深层 harness 文档中。

本技能只处理“Codex 在某个代码项目里如何工作”的问题，不处理团队技能库自身如何演进，也不把普通项目文档整理成知识库。它的核心动作是：观察真实项目事实，识别 Codex 工作阻塞点，更新入口、任务地图、命令、验证路径或失败记录，再用真实任务或失败案例反向检查这些材料是否有用。

## 职责边界

本技能负责：

- 建立或维护项目根目录的 `AGENTS.md`，让 Codex 进入项目后知道先读什么、怎么改、怎么验证。
- 维护项目级 harness 目录，例如 `docs/codex-harness/`、`docs/agent-harness/` 或项目已有等价目录。
- 梳理 Codex 需要的最小项目任务地图，包括模块边界、关键入口、常见修改路径和禁止误改区域。
- 固化真实可用的开发、测试、检查、构建和调试命令。
- 定义不同变更类型的最低验证路径。
- 记录 Codex 或人工在项目中遇到的可复用失败模式和恢复方式。

本技能不负责：

- 维护本团队技能库自身；技能定义、触发词、脚本和流程演进应使用 `team-skill-evolve`。
- 写 PRD、拆 issue、实现 issue、验证 issue 或发布 issue。
- 生成完整架构设计说明书；需要面向评审的功能设计时应使用架构类技能。
- 整理通用项目文档、会议纪要、一次性任务日志或人类知识库。
- 在没有真实代码、命令、任务或失败证据时凭空编写注意事项。
- 维护 `CLAUDE.md` 作为核心输出；如果项目已经存在 `CLAUDE.md`，只能作为兼容入口链接到同一套 Codex harness。

## 运行时配置

Codex harness 独立于需求、PRD、issue 拆解或技术债流程，不读取、不创建、不修改 `team-spec/` 运行时工作区，除非用户明确把某个真实任务或失败案例作为证据输入。

Harness 目录识别规则：

- 优先从现有 `AGENTS.md` 中识别已链接的 Codex harness 目录。
- 如果项目没有现成目录，应使用项目内独立目录保存 harness 文档，优先选择 `docs/codex-harness/`。
- 如果项目已经有 `docs/agent-harness/` 等等价目录，可以继续沿用，不为改名而制造迁移。
- 目录必须是相对项目根目录的路径，不应是绝对路径，不应位于需求、PRD、issue 或归档工作区下。
- 如果无法从现有文件唯一判断目录，只问用户一个问题确认 harness 目录，不展开多轮访谈。

执行要求：

- 对话回复与 harness 文档默认沿用项目现有语言；若无法判断，优先使用用户本轮语言。
- 用户临时切换语言时，本次立即生效；只有用户明确要求持久化语言偏好时，才写入 harness 文档。
- 除非用户明确说“只分析、不改文件”，否则本技能默认应该产生或更新目标项目中的持久化 harness 输出物。

## 输入物

- 目标项目根目录的 `AGENTS.md`，以及已有 `CLAUDE.md`、`README.md`、`docs/`、开发手册、测试说明和运维说明。
- 当前项目的真实代码、目录结构、构建配置、测试配置、脚本、CI 配置和本地开发工具。
- Codex 最近执行真实任务时遇到的卡点、失败测试、CI 日志、命令错误、人工修复记录或交付事故。
- 已有 Codex harness 目录，例如 `docs/codex-harness/` 或项目现有等价目录。
- 可选：来自 `team-prd-to-issues`、`team-issue-implement` 或 `team-issue-verify` 的真实工程任务反馈，但本技能只把其中与 Codex 工作环境相关的部分写入 harness。

如果用户没有提供明确范围，应先判断本轮属于初始化、修复还是刷新。无法唯一判断时，只问一个最关键的问题。

## 输出物

本技能按本轮证据更新最小必要文件，不要求一次补齐完整文档集合。

必须维护：

- `AGENTS.md`：Codex 的项目入口，保持短小，指向深层 harness 文档。
- `{harness_dir}/index.md`：Codex harness 总入口，说明最小阅读路径和每个文件的职责。

按需要维护：

- `{harness_dir}/project-map.md`：Codex 做任务需要理解的模块边界、关键入口、常见修改路径和禁止误改区域。
- `{harness_dir}/commands.md`：常用开发、测试、检查、构建和调试命令。
- `{harness_dir}/verification.md`：不同变更类型对应的最低验证策略。
- `{harness_dir}/coding-rules.md`：项目特有编码约束、提交约束和禁止事项。
- `{harness_dir}/review-rubric.md`：Codex 完成实现后的自查和评审关注点。
- `{harness_dir}/known-failures.md`：已知失败模式、复现方式、根因、规避方式和修复记录。
- `{harness_dir}/decisions.md`：只有当 harness 目录、命名、拆分或维护策略存在重要取舍时才创建或更新。

落盘规则：

- 初始化 Codex harness：至少创建或更新 `AGENTS.md`、`{harness_dir}/index.md`，并按证据更新 `commands.md` 或 `verification.md`。
- 修复 Codex 工作阻塞：至少更新导致阻塞的对应文件；如果阻塞来自失败案例，必须更新 `known-failures.md`。
- 刷新项目变化：项目结构、测试、CI、启动方式或关键脚本变化后，更新 `project-map.md`、`commands.md`、`verification.md` 或入口索引中受影响的部分。
- 只分析模式：用户明确要求不改文件时，只输出问题定位、建议改动和建议验证方式。

## 核心动作

本技能有 5 个动作：

1. 建入口：让 `AGENTS.md` 成为 Codex 的短入口，说明项目目标、先读路径、常用命令索引、验证入口和失败记录位置。
2. 画地图：把 Codex 容易迷路的模块边界、代码入口、配置入口、测试入口和禁止误改区域整理成任务地图。
3. 固化命令：把真实可执行的开发、测试、检查、构建和调试命令写清楚，包括运行目录、前置条件、适用场景、来源和最后验证日期。
4. 定义验证：说明不同变更类型的最低验证路径，减少 Codex 改完代码后不知道如何确认的问题。
5. 记录失败：把真实失败转化为可复用记录，包括症状、触发条件、根因判断、处理方式和下次优先检查项。

## 执行模式

### 初始化

当项目第一次接入 Codex，或没有清晰 `AGENTS.md` 时执行：

1. 读取项目结构、README、构建配置、测试配置、脚本和 CI。
2. 确认或创建 `{harness_dir}`，默认优先 `docs/codex-harness/`。
3. 创建或更新 `AGENTS.md`，只保留 Codex 必须知道的入口信息。
4. 创建或更新 `{harness_dir}/index.md`，列出最小阅读路径。
5. 根据已确认事实创建或更新 `commands.md`、`verification.md` 或 `project-map.md`。
6. 用一个最小真实任务路径检查 Codex 是否能从入口找到需要的信息。

### 修复

当 Codex 在真实任务中卡住、跑错命令、误读模块、验证不完整或重复失败时执行：

1. 还原失败场景：症状、触发命令、相关路径、期望行为和实际结果。
2. 判断失败属于入口缺口、任务地图缺口、命令缺口、验证缺口、编码规则缺口、失败记录缺口，还是代码或测试债务。
3. 只更新造成阻塞的最小 harness 文件。
4. 如果失败可以复用，写入 `known-failures.md`。
5. 再用同一失败场景检查更新后的 harness 是否能指导下一次处理。

### 刷新

当项目结构、脚本、测试、CI、启动方式、关键模块或开发流程变化时执行：

1. 对照当前代码、配置、脚本和 CI 找出过期 harness 内容。
2. 删除、改写或标注过期命令、路径、模块说明和验证策略。
3. 同步更新 `AGENTS.md`、`index.md` 和被链接的深层文档。
4. 对关键命令或验证路径做轻量确认；无法确认时标注 `待验证`，不得写成确定事实。

## 最小阅读路径

`{harness_dir}/index.md` 必须按任务类型列出 Codex 的最小阅读路径：

- 新任务默认必读：`AGENTS.md`，再读 `{harness_dir}/index.md`。
- 修改代码前：读取 `project-map.md`、`coding-rules.md` 和 `verification.md` 中相关部分。
- 运行或修复测试前：读取 `commands.md`、`verification.md` 和 `known-failures.md`。
- 处理失败时：先读 `known-failures.md`，再按失败类型回到 `commands.md`、`verification.md` 或 `project-map.md`。
- 评审或收尾前：读取 `review-rubric.md` 和本次变更类型对应的验证要求。

## 证据规则

写入 Codex harness 的内容必须能追溯到证据来源：

- 强证据：当前代码、测试、CI 配置、构建配置、脚本、锁文件、类型配置、lint/format 配置。
- 中证据：README、架构文档、开发手册、运维说明、团队维护的正式文档。
- 弱证据：历史对话、一次性任务记录、人工经验、未复现的失败描述。
- 未验证内容：无法从强证据或中证据确认的命令、路径、规则或判断，必须标注为 `待验证`。

如果代码、配置、测试、脚本或 CI 与文档冲突，优先相信当前工程事实，并修正 harness。无法判断哪一方正确时，不要合并成模糊规则，应标注为 `待确认`，并说明需要用户或维护者确认的问题。

## 自检要求

每次修改 Codex harness 后，必须轻量自检：

- `AGENTS.md` 是否仍然短小，并能指向必要深层文档。
- 新增或改名文件是否已写入 `{harness_dir}/index.md`，并能从入口文件发现。
- 新增命令是否有来源、适用场景、前置条件和验证状态。
- 新增验证策略是否对应实际测试命令、构建命令、人工检查入口或 CI 检查。
- 新增规则是否能追溯到代码、配置、测试、CI、正式文档或明确团队约束。
- 是否引入敏感信息、绝对本机路径、个人凭证或一次性任务噪音。
- 是否需要删除、废弃或标注过期内容，而不是只追加新内容。

## 与其他技能的关系

- `team-skill-evolve`：维护团队技能库自身。Codex harness 技能定义、触发词、脚本或流程需要修改时，使用它。
- `team-prd-to-issues`：拆 PRD 时如果发现项目入口、验证命令或 Codex 工作环境不清楚，可以转入本技能补 harness。
- `team-issue-implement` / `team-issue-verify`：真实实现或验证暴露的命令、验证和失败模式缺口，可以反馈给本技能。
- `team-spec-to-functional-design`：需要面向人类评审的功能设计说明书时使用，不由本技能替代。
