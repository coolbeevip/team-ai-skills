# 配图策划与制作

## 先决定图的职责

先盘点原文图片及其图注、来源、正文引用和邻近说明，默认尽量保留原图。原文插画、截图或照片也属于材料，不只保留数据图。先安排原图，再判断是否需要补图，避免重造已经存在的表达。

为每张候选图回答：它帮助读者看清哪条关系、哪个场景或哪项证据，放在何处最有用？在现有制作记录中简记对应主张、类型、来源、位置和图注即可，不强制另建表格。读者只需看到图及必要解释。

先区分证据图与解释图，再选制作方法。证据图保留真实性；解释图可依据原文统一重绘，但保留原件与来源映射。概念插画只提供情境或隐喻。不能把三者混成同一种证据身份，也不能为了统一外观给真实照片滤色。

按内容决定是否配图。复杂机制优先考虑关系图，陌生业务场景可以考虑情境插画；简单状态说明可以不配图。没有固定图数、每节配图或封面图要求。用户明确指定图片类型、数量或已有素材时按该请求制作；若不能完成，说明具体缺口，不静默删图或用另一种图冒充。

## 三条制作路径

| 路径 | 适用内容 | 制作与事实边界 |
| --- | --- | --- |
| 原图复用 | 原文实验图、产品截图、现场照片、用户提供素材 | 保留证据身份和来源；裁切不能丢掉坐标、条件、图例或关键上下文 |
| 确定性绘图 | 架构、流程、时序、状态、对照、可靠数据 | 使用可编辑 SVG、HTML/CSS 或环境已有绘图库；精确控制文字、数字、连线及比例 |
| 生成插画 | 封面概念、业务情境、难以直接拍摄的抽象关系 | 使用可用图像生成工具，清楚标为概念或场景示意；不能当作真实客户、产品、现场或实验记录 |

已有素材足够时先复用，不重复生成。外部图片搜索仅在用户允许来源扩展时使用；搜到的图不等于获准转载，须核对来源、许可与必要署名。无法确认可用性时换成自绘表达或报告缺口，不热链随机图片。

## 原图保留与调整

- 优先获取原始图片文件；对文档内嵌图按已有工具能力提取。只能取得页面截图时，保留图注与必要上下文并说明来源形式，不假装拿到了原始高清图。
- 保留原始副本，按正文关系安放，必要时移动到相关章节；不得脱离原来的条件、时间或比较对象。可以调整显示尺寸与周边版式，不为配色统一而改动证据内容。
- 原图信息较密时，先保留完整图，再补局部放大或简化解读；新增解读明确身份，不能替代原图。放大只改善阅读呈现，不宣称恢复了原本缺失的细节。
- 原图仅在重复、与本次范围无关、来源失效、清晰度不足或披露/许可不允许等具体情况下调整或省略，并在制作记录说明原因。关键证据图不能只因不好看、占高度或不合模板而删除。
- 缺图或链接失效时报告哪张图未取得；可完成其他内容，不能凭图注重生成一张并当作原图。需要从外部获取时遵守已给定来源与访问授权。
- 双模式都先保留与各自正文有关的原图。技术细节可安排到后续章节或附图，不因“速览”自动删光；如确实省略，检查不会改变结论和理解，并保留原因记录。
- 图片清单记录主线、局部放大或 HTML 附录的具体去向。移入附录不等于删除，必须有可用原件、图注及主线入口；影响结论的证据仍在主线呈现。

## 确定性绘图

- 全文使用一致的节点含义、线宽、箭头、字体、配色和状态图例。主机制图优先承担全篇解释，局部展开沿用其名称与方向；不为统一排版强行改变关系。
- 架构图先确定组件、边界和数据方向；将现有实现、计划与建议区分，不能凭图补出不存在的组件。
- 流程与时序只画来源支持的顺序；并行依赖画成分支或汇合，不能为了排版画成串行。
- 数据图从可核对的数值绘制，保留单位、分母、基线、时间和测量条件；缺失值不补成零。柱形通常从零开始，其他坐标选择须清楚标注且不夸大差异。
- 对照图各侧使用同一口径和尺度；没有可靠数值就比较结构、步骤或约束，不画暗示量化收益的曲线。
- 标签、图例和箭头用确定性排版；颜色之外再用文字或线型表达状态。图注说明这张图支持什么判断及必要限制。
- SVG 包含可识别的 `title`、`desc` 或等价可访问说明；在手机宽度下检查实际标签字号与连线。宽图优先拆分或改成纵向，不缩小到难读。

## 生成插画

默认使用环境已提供的图像生成工具；可用的 `imagegen` 技能可辅助调用，但本技能不依赖其他技能目录里的模板或脚本。工具不存在或失败时如实报告，不能自动切换收费 API、安装依赖或上传材料到未授权服务。

配图请求已有明确授权且披露范围清楚时直接制作，不逐张重复确认。内部材料只提取获准传出的必要语义；没有外传授权时使用本地绘图或保留缺口，不能因删掉客户名就自行认定整份材料可上传。提示词无需包含全文、内部路径、密钥或真实数据。

提示词只描述需要的视觉结果，可按以下要素组织，不必机械填写每项：

- **信息任务**：读者需要看见的场景、对比或关系。
- **主体与动作**：具体对象做什么；抽象概念怎样对应现实。
- **构图与位置**：封面、章节图或局部说明；按实际版面选择横幅、方形或纵向，留出必要裁切安全区。
- **视觉语言**：与文章一致的纸色、深灰与强调色；插画风格前后一致，不堆通用机器人、发光大脑或无关科技符号。
- **保留与排除**：必须保留的物体关系、禁止暗示的事实；默认不生成文字、数字、坐标、标志、水印或受众标签。标题和精确标注由 HTML/SVG 添加。
- **图片身份**：概念插画或场景示意，不能要求仿造某个机构的官方出版物或虚构现场证据。

例如，材料说明“代码生成变快，但审查仍可能限制交付”，可以将配图任务写成：用一幅编辑插画呈现输入材料持续进入、审查环节逐份检查、已审核材料再交付的情境；各环节不画速度数值，保持审查与输出关系明确；米白背景、深灰线条和单一绿色强调，不出现文字或品牌。图注说明这是瓶颈关系的概念示意，不代表实测吞吐。

调用后必须查看图片：对象和动作是否准确，是否多出不存在的功能，隐喻是否容易误导，有无乱码、伪标签或视觉瑕疵。需要修改时针对实际问题调整，单图初次生成后最多再修正两次；仍不合格则停止并报告，保留已通过部分。用户另行指定次数或预算时服从其范围。

用户提供编辑目标时先查看原图，修改只覆盖获准范围；证据图需要保留原件，生成式编辑不得冒充原始记录。仅用于风格参考的图不自动成为可转载素材。

## 落盘、嵌入与一致性

1. 将选定图片与可编辑图源保存到本次产物的 `assets/`，使用清楚且稳定的名称；不覆盖原图，不让项目引用仅存在于工具缓存或临时返回链接中的图片。
2. Markdown 用本地相对路径引用图片并写图注；HTML 内联 SVG 或将实际位图编码为 data URI。内联前确认拿到的是图片文件，不能把下载错误页或占位图当素材。
3. 为图片提供具体 `alt`，说明对象、动作和与正文的关系，不能只写“配图”。证据图标来源，生成图就近标“概念插画”或“场景示意”，无需把提示词和工具日志塞入成品。
4. 在制作记录中保存来源/许可或生成方式、最终提示词及实际文件位置；包含内部信息的制作记录遵守原披露范围。图片增加的关系和限制同步到正文或图注。
5. 浏览器中检查加载、宽高比、手机尺度及裁切。不要用固定高度和 `object-fit: cover` 裁掉证据图；插画也需确保关键对象完整。
6. 对双模式可复用同一素材，但图注与强调点可按阅读任务调整。图片更新后同步两版中所有引用并重新导出受影响 PNG，避免一版用旧图、一版用新图。

## 不可用时的处理

生成工具不可用时，可以完成有依据的结构图与文字；若用户明确要插画，说明插画未生成，提示词仅作为制作准备。对可有可无的插画可以省略；对必需的证据图或明确指定的图片，不能将省略报告为整项完成。最终报告分别说明已制作、未制作及尚未验收的图片。

## 随技能提供的封面示例

[editorial-cover.png](../assets/editorial-cover.png) 是本技能制作时由内置 imagegen 工具生成并查看的概念插画，尺寸为 1536×1024。纸张、支撑与缺口只比喻“已有测试与新任务之间尚未补齐的证据”，不是原文照片或实验图。它为相邻模板提供可用样张，运行技能时先保留用户原图；不得因示例现成而替换用户原图，或复用于无关主题。

首次生成提示词如下，未发送内部业务材料：

```text
Create a premium editorial conceptual still-life photograph for a serious technology magazine article about the gap between success on familiar evaluation tasks and performance on unseen tasks. No text, letters, numerals, logos, symbols or charts anywhere. Single wide landscape composition, approximately 3:2. On a pale cool-grey matte background, an orderly stack of thin off-white rectangular paper sheets extends horizontally from the lower left, crossing a solid cobalt blue rectangular support. The top paper sheet is delicately folded into a narrow bridge and reaches toward a separate solid pale-grey block at upper right, but stops before it, leaving a clearly visible gap. The physical gap is the focal point. Precisely art-directed studio still life, tactile paper edges, subtle hard directional daylight shadows, quiet sculptural geometry, real material texture, architectural photography, sophisticated restrained magazine cover aesthetic. Cobalt is the only saturated color. The solid support and distant block must read as distinct objects with the missing connection clearly visible. No surreal melting, no floating objects, no gradients, no cyberpunk, no robot imagery. This is a conceptual illustration, not scientific evidence or a diagram. Compose the objects as a coherent still life with balanced negative space; avoid adding any decorative objects.
```

最终样张按用户要求用图像工具调整为暖纸色与深绿色，并查看了实际结果。编辑提示词如下；此调整只针对生成的概念素材，不适用于原始证据图：

```text
Edit this conceptual editorial still life only in its palette. Preserve exactly the paper stack, folded paper bridge, visible gap, separate right block, camera angle, shadows, texture and composition. Change the cobalt blue support block to a restrained dark forest green, approximately #28584A. Change the cool-grey ground and background to warm matte off-white, approximately #F6F4EE, while retaining realistic shadows and subtle material shading. Keep the separate right block a light neutral warm grey and the sheets warm off-white. No other colored accents. No text, logos, labels, numbers or additional objects. This remains a conceptual illustration, not documentary evidence.
```
