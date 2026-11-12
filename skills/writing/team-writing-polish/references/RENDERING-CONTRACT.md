# 输入、制作计划与本地渲染

这些 JSON 是本次制作协议，不是共享 `team-spec/config.yml` 的扩展。先读取项目配置、写作风格和访问边界，再将已明确的用户意图写入协议。脚本不会替代内容编辑或自动检查来源是否真的支持一句话。

## 两份 schema

- [request.schema.json](../assets/request.schema.json)：用户口语经上下文解析后的输入。`audience` 必须先明确；未知枚举与未知字段报错，不猜近似值。
- [plan.schema.json](../assets/plan.schema.json)：可渲染的单受众计划，必须包含事实底稿、内容版本、风格版本和选择依据。`both` 只在请求层出现，解析成两个独立计划。

校验器实现这两份 schema 实际使用的 JSON Schema 子集：类型、枚举、对象字段、数组、数值范围、正则和 `anyOf`；不是通用 JSON Schema 引擎。协议文件使用 JSON，避免让技能暗中安装 YAML 解析器。

请求示例：

```json
{
  "sources": ["report.md"],
  "audience": "both",
  "purpose": "understand",
  "visual_style": "auto",
  "preview": "auto",
  "formats": ["html", "png", "markdown"],
  "locale": "zh-CN",
  "density": "comfortable",
  "canvas": {"css_width": 400, "export_scale": 2.7, "split_policy": "semantic"},
  "brand": null,
  "source_scope": "supplied-only"
}
```

允许 `visual_style` 为单个风格 ID，或在 `both` 时使用 `{"ceo":"modern-minimal","cto":"swiss-rational"}`。`auto` 解析为默认 `tech-magazine`，推荐理由与其他候选由编辑者按材料生成，脚本不假装完成语义推荐。

| 请求字段 | 计划字段 | 说明 |
| --- | --- | --- |
| `visual_style` | `styleId`、`styleVersion` | 选定风格及安装的配置版本 |
| `formats` | `outputs` | 同一内容版本的交付格式 |
| `canvas.css_width` | `canvas.cssWidth` | CSS 逻辑宽度，默认 400 |
| `canvas.export_scale` | `canvas.scale` | 像素倍率，默认 2.7；不是字号 |
| `canvas.max_export_pixels` | `canvas.maxExportPixels` | 单个 PNG 的总像素预算，默认 2400 万 |
| `target_channel_limits.max_width_px` | `targetChannelLimits.maxWidthPx` | 导出像素宽度上限 |
| `target_channel_limits.max_height_px` | `targetChannelLimits.maxHeightPx` | 导出像素高度上限 |
| `target_channel_limits.max_total_pixels` | `targetChannelLimits.maxTotalPixels` | 单图总像素上限，与本地预算取较小值 |
| `preview` 与上下文 | `selection` | 记录原因、预览策略和具体确认；不得代替用户确认 |

计划 `specVersion` 与 `styleVersion` 首版均为 `1.0`。`contentVersion` 是编辑者维护的内容版本；导出时额外计算内容 SHA-256，生成文件哈希保存在 QA 记录。换风格不重新编造事实，改正文、来源事实或实际图片必须生成新版本并重新验收。

## 内容结构与来源

- `mainClaim`：`text`、可选 `deck`、`claimIds`。文本字段为纯文本，不嵌入 HTML 或 Markdown 图片。
- `facts`：唯一 `id`、原始主张 `text`、`kind`、可追溯 `source`、`conditions`；`kind` 为 `fact`、`judgment`、`recommendation` 或 `hypothesis`。`required: true` 的主张必须在主线被引用。
- `quantity`：仅在来源给出可靠量值时写入 `value` 与 `unit`。缺数据不设零。冲突保留在底稿与正文，不能选择更吸引眼球的数字作图。
- `blocks`：唯一 `id`、语义 `role`、`title`、`paragraphs`、`claimIds`；可设 `appendix: true`。每块至多一个主视觉：`diagramId`、`chartId`、`scene` 或 `image`。
- `diagrams`：标题、文字说明、节点和边。节点包含来源、行列位置、`observed/pending` 状态；边必须有可解析的端点和来源。位置不是事实顺序，箭头才表示关系。
- `charts`：标题、比较条件和点；每个点只给标签与 `claimId`，数值与单位从事实底稿读取，不能在图表里另填一个数。
- `scene`：同一 `object`、`state`、`caption`、`claimIds`、状态。当前几何组件只表达“对象与证据状态”的概念对应；不适用时用真实素材或另行制作插画，不套成机器人能力图。
- `image`：本地路径、具体 `alt`、图注、来源和 `evidence/explanation/concept` 身份。只读取计划目录内部的 PNG/JPEG/WebP，保留原件，交付副本按内容哈希命名并内联 HTML。

数据条图首版只接受同单位、非负的事实量值；更复杂的时序、多变量、负数或统计图应另行确定性绘制并保留可编辑图源。SVG 原件不得直接作为可执行页面注入；可保留原件并使用受信工具栅格化用于展示，或根据来源建立节点/边数据。不会因不支持一种图形而伪造替代数据。

引用解析只能证明 ID 存在，不能证明语义保真。`required` 检查也不能证明文字解释足够；来源、证据强度与承重信息仍要人工复核。

## 预览状态

- 新风格选择：固定受众、正文、事实与素材版本，为 2～3 个候选分别生成预览。不能只给某候选更好的文案。
- `preview=auto/required` 且 `selection.confirmed=false`：脚本仅允许 `--preview`，不会生成最终长图。
- 已确认具体预览：记录依据后设置 `confirmed=true`；同一项目适用的确认可沿用。
- 用户直接要求完成或沿用已选风格、不需额外预览：记录原意，设置 `preview=skip`；不重复提问。
- 源内容或主布局改变：重新检查构图，必要时重新预览；不承诺旧版式容纳任意内容。

风格的默认首屏视觉由配置 `heroRole` 选择，正文先后顺序以受众计划为基础。若材料没有匹配图形，允许文字首屏；数据新闻不会自动捏造图表。各块仍使用可编辑 HTML/SVG，不能把全部内容交给图像模型。

## 脚本与依赖

入口为 [render.py](../scripts/render.py)，内部使用 [contracts.py](../scripts/contracts.py) 与 [browser.py](../scripts/browser.py)。三个文件必须一起安装。模板为 [editorial.html](../assets/templates/editorial.html) 与 [editorial.css](../assets/templates/editorial.css)。

先解析当前技能目录为 `{skill_dir}`，命令中的输入与输出路径属于目标业务项目：

```bash
python3 {skill_dir}/scripts/render.py --request request.json
python3 {skill_dir}/scripts/render.py --plan plan.json --output preview-v1 --preview
python3 {skill_dir}/scripts/render.py --plan plan.json --output preview-v1 --preview --apply
python3 {skill_dir}/scripts/render.py --plan plan.json --output final-v1 --apply
```

默认 dry-run，只校验、读素材并报告解析结果；`--apply` 才写文件或启动浏览器。目标目录必须为空，不覆盖旧导出或源文件。后续修订使用新版本目录，避免旧图混入新内容。

JSON、Markdown、HTML 和图源制作只用 Python 标准库。PNG 需要本地 Chrome/Chromium 和运行该命令的 Python 已安装 `websocket-client`；可用 `--browser /path/to/chrome` 指定浏览器。缺少依赖时保留可用文本/HTML、退出码为 2，并报告 PNG 未完成。用户允许安装依赖时，可为选定 Python 执行 `python3 -m pip install websocket-client`；不要默认联网安装或改用远程截图服务。

脚本只用隔离的临时浏览器配置，阻断页面 HTTP(S) 请求，不读取用户浏览器会话。未打开来源链接，不调用生成服务，不修改配置、原文、状态或远端。访问策略仍需编辑者先执行，不能以脚本的目录检查代替授权。

## 渲染与报告

1. 校验结构、引用、必要主张、图表数值来源和最终配色对比度。
2. 从同一计划生成 Markdown、HTML、图源、`sources.md` 和 `design-plan.json`；PNG 需要的 HTML 即使未单独请求也作为渲染源保留。
3. 在 360/400/430 CSS px 和指定宽度等待字体、图片完成；检查溢出、SVG 文字裁切、标签实际缩放字号、图片加载与实际字体家族。记录浏览器版本；CDP 未暴露的系统字体版本明确标为不可获取，不捏造。
4. 只导出主线，附录留在 HTML。受像素预算或渠道限制时按完整语义块分段；单块超限则报错，返回编辑拆块，不缩字或截断图注。
5. 超过约四个手机屏时报告编辑提醒，供检查是否应拆分；它不是强制裁切阈值。没有真实渠道限制时不伪造平台上限。
6. 读回 PNG 的签名、尺寸与分块校验；记录文件哈希、截取范围及自动检查。实际图片仍须打开查看，不能把文件校验称为视觉验收。

`qa-report.json` 保留机器记录与文件哈希，`qa-report.md` 给出检查状态和未验项。字体缺字、事实语义、首中尾和全篇视觉评审、分段上下文及真人理解测试必须区分。首版不自动启用真实设备读屏、播放声音或改音频设置。

退出码：`0` 为请求格式已生成或 dry-run 通过，仍可能待人工复核；`1` 为计划/文件等硬错误；`2` 为浏览器导出未完成但已保留可用产物。任何硬门禁失败都不能宣称最终作品完成。
