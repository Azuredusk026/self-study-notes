# LOD、地形与程序化资产

LOD 的目标不是单纯减少面数，而是让资产成本随屏幕贡献变化。地形和程序化资产进一步要求：同一套规则既能生成内容，也能稳定输出引擎理解的数据。

## 以屏幕占比决定 LOD

只按世界距离切换会忽略物体大小、FOV 和分辨率。引擎通常根据包围体投影到屏幕的比例选择 LOD。大物体在相同距离下会比小物体更晚降级。

透视投影下，物体的近似屏幕高度与下面的比例相关：

$$
s \propto \frac{h}{d\tan(\theta/2)}
$$

$h$ 是物体世界高度，$d$ 是相机距离，$\theta$ 是垂直 FOV。实际引擎还会使用包围球、投影矩阵和平台缩放，因此阈值应在目标设备实测。

## LOD 减什么

LOD 不只调整三角形：

- 减少轮廓影响较小的边和内部结构；
- 降低圆柱段数、枝干分段和小装饰数量；
- 合并材质或取消局部 Detail Pass；
- 降低骨骼数、动画更新频率和 Blendshape；
- 切换较便宜的 Shader、阴影或透明策略；
- 在远处换成 Impostor/Billboard，最后完全剔除。

植被远景应优先保留主干和树冠轮廓。随机裁掉末级小枝比整体 Decimate 更稳定。裁叶后可略微放大保留叶簇，补偿视觉密度。

## 切换、Cross Fade 与 Hysteresis

硬切换只绘制一个 LOD，成本稳定，但轮廓或材质突然变化会产生 Pop。

Cross Fade 在过渡区同时绘制两级，通过 Dither 或 Alpha 混合切换。它改善连续性，却会暂时增加顶点、像素和 Draw 成本。透明植被还可能放大 Overdraw。

Hysteresis 为进入和退出阈值留出差值，避免摄像机在边界附近时来回切换。相机快速移动时还要考虑资源是否已经流送完成。

## Geometry LOD 与 Mipmap 要同步

几何变少时，材质细节也应随之预过滤。否则远距离会出现：

- 高频 Normal Map 闪烁；
- Alpha Clip 叶片因 Mipmap 平均后变细或消失；
- 细线、铁丝和小孔时隐时现；
- 纹理仍保持高分辨率，几何省下的成本被带宽抵消。

植被可使用 Alpha-to-Coverage、保 Alpha Coverage 的 Mip 生成或远景专用贴图。阈值补偿需要检查不同背景和 MSAA 设置，不能只在一张截图上调好。

## 地形的基本表示

Heightfield 用二维标量网格表示高度，天然适合连续地表、分块、LOD 和碰撞。它无法直接表示洞穴、悬挑和垂直峭壁，这些通常由独立 Mesh 补充。

高度图的关键参数包括：

- 世界尺寸和高度范围；
- Sample Resolution；
- 位深，8 位高度容易形成台阶；
- 边界是否能与相邻 Tile 无缝拼接；
- DCC 与引擎对高度、轴向和单位的解释。

规则网格可按 Chunk 或 Quadtree 管理。远处使用更低采样密度，边界通过 Stitching、Skirt 或约束相邻层级差来避免裂缝。

## GPU 细分地形

GPU Tessellation 可以让每个地形 Patch 根据屏幕贡献生成不同密度的三角形。Hull/Tessellation Control 阶段计算边和内部细分因子，固定 Tessellator 生成参数坐标，Domain/Tessellation Evaluation 阶段再采样高度图并计算最终位置。

细分因子适合由边的屏幕像素长度或位移误差决定。只按 Patch 中心到相机的距离会让同一共享边的两侧得到不同因子，产生裂缝。稳定方案包括：

- 共享边只使用两个端点或同一边界球计算因子；
- 相邻 Patch 约束到兼容层级；
- 使用 Fractional Even/Odd Partitioning 缓和因子变化；
- 最终边界增加 Skirt 处理地形 Tile 接缝。

细分增加的是当前帧生成和处理的图元，不会降低高度纹理带宽。因子过高会把瓶颈推到 Tessellator、Vertex/Domain Shader 或光栅化。近处需要真实轮廓时细分有效；远处地形仍应依赖 Chunk LOD、Mipmap 和流送。

## 地形材质分层

Splat Map 的 RGBA 通道保存各 Terrain Layer 权重。若层数超过四个，需要多张控制图或改用索引/虚拟纹理方案。

权重通常应满足：

$$
w_i' = \frac{w_i}{\sum_j w_j}
$$

若制作端没有先做互斥与归一化，引擎归一化会改变预期覆盖关系。雪、草、碎石等有优先级时，可先让下层减去上层遮罩，再统一归一化。

每层同时采样 Base Color、Normal、Mask 会很快增加纹理读取。Triplanar 能缓解陡坡 UV 拉伸，但每层会从单方向采样变为三个方向。大地形通常需要按距离减少层数、烘焙远景颜色或使用 Virtual Texture。

## Houdini HeightField 流程

一条可维护的地形流程可以是：

1. 用噪声和形状节点生成基础 Height；
2. 用 Erode 生成 Flow、Water、Debris、Sediment 等层；
3. 按坡度、高度和侵蚀层生成材质 Mask；
4. 处理图层优先级与归一化；
5. 按 Tile 导出 Height、Splat 和辅助 Mask；
6. 在引擎中创建 Terrain Layer、碰撞、植被和远景代理；
7. 校验边界、尺寸、色彩空间与重建结果。

Erode 可能依赖时间迭代。只保存最终 Height 图片无法恢复中间侵蚀层，因此 `.hip`、参数、随机种子和导出 manifest 都属于可复现资产。

## SOP、HDA 与 PDG

SOP 负责单份几何的数据处理；HDA 把节点网络封装成带输入、参数和输出契约的数字资产；PDG/TOPs 负责任务依赖、参数 Wedge、批处理和并行调度。

例如程序化树管线可以：

1. HDA 根据曲线、种子和生长参数生成树干与枝叶；
2. 不同 Wedge 产生树种、年龄和随机变体；
3. 为每个变体生成 LOD0/1/2 和碰撞；
4. 用 Primitive Group 命名 `LOD0`、`LOD1`、`LOD2`；
5. 用 `unity_material` 等约定传递目标材质；
6. PDG 调度导出，并记录输入参数、工具版本和结果路径。

并行数不是越高越好。Houdini Session、贴图烘焙和几何生成都可能占用大量内存。Scheduler 应限制并发，并让单个失败项可以重试，而不是整批重跑。

## 程序化不等于完全自动

适合自动化的是规则明确、重复量大、结果可验证的部分，例如：

- 道路贴地、护栏和管线沿曲线生成；
- 岩石、树木和建筑变体；
- LOD、碰撞、命名和目录输出；
- 地形切块、Mask 打包和批量导出。

艺术方向、关键轮廓和 Hero Asset 往往需要人工控制。工具应暴露有意义的美术参数，并允许局部 Override。过多底层节点参数会把工具变成难用的节点面板。

程序化内容生成（Procedural Content Generation，PCG）把规则、种子和输入数据转换为关卡、散布或资产结果。相同版本、参数和种子应生成相同输出，便于复现、版本比较和网络同步。随机数流要按区域或规则分组，避免新增一个节点后让整个世界随机结果全部变化。

## 分块散布与稳定重建

开放场景常把树木、岩石和小物件按 Terrain Chunk 生成。每次改一个参数都重新随机整张地图，会让人工调整全部失效，也会产生难以审查的巨大版本差异。

生成器应让结果具有确定性：

- 用世界分块坐标和资产类型派生随机种子；
- 为生成实例保存稳定 ID，不依赖当前数组下标；
- 将手工删除、移动和替换记录为 Override，而不是直接改生成缓存；
- 参数变化后只标记受影响的 Chunk 为 Dirty；
- 输出 manifest 记录规则版本、输入 Hash 和实例数量。

分块边界还需要邻域信息。道路避让、Poisson Disk 散布和坡度过滤如果只看本块，会在边缘形成断层或重复。可以在计算时读取一圈扩展边界，最后只提交本 Chunk 范围内的结果。

实例进入引擎后，还要接入空间分区、LOD、GPU Instancing 和流送。程序化工具产出十万棵树并不等于它们能直接运行；输出预算和运行时表示应当在 HDA 设计阶段就确定。

PCG 的验收还包括密度、可达性、穿插、性能预算和重复模式。设计师的 Override 应作为独立层保存，在局部重建后重新应用；无法应用的覆盖要报告冲突，不能静默丢失。

## LOD 预算来自画面与平台

阈值不应写成所有资产共用的固定距离。可以先按类别设预算，再由捕获验证：

- Hero Asset 关注轮廓、材质与阴影连续性；
- 重复道具关注 Draw、顶点和实例数据；
- 植被关注 Alpha Overdraw、阴影和风动更新；
- 地形关注纹理采样、Tile 流送和远景几何；
- 移动端还要检查带宽、热降频和内存峰值。

同一 LOD 方案在 1080p 手机、4K PC 和 VR 双眼中产生的屏幕误差不同。最终阈值应成为平台质量档配置，而不是只存在于 DCC 导出预设。

## 验证清单

- 以 Screen Percentage 和目标 FOV 检查 LOD 阈值。
- 对切换前后做轮廓、法线、材质和阴影对照。
- 检查 Cross Fade 过渡区的双份 Draw 与 Overdraw。
- 在不同距离检查植被 Alpha Coverage 和 Mipmap。
- 对地形 Tile 检查高度边界、Splat 权重和坐标方向。
- 记录 HDA/Houdini Engine 版本、随机种子、参数和导出日志。
- 在引擎 Profiler 中验证 GPU 时间、内存和流送收益。

## 相关主题

- [[06_纹理技术/UV、图集、流送与虚拟纹理]]
- [[08_几何与网格/网格数据、缓存与几何处理]]
- [[12_光追与现代渲染/GPU-Driven管线与Nanite]]
- [[15_资产与工具管线/资产导入、验证与发布]]

## 参考资料

- Unity Manual, *LOD Group* and *Terrain Data*.
- Houdini Documentation, *HeightField*, *PDG* and *Houdini Engine for Unity*.
- Lindstrom and Turk, *Fast and Memory Efficient Polygonal Simplification*.
- meshoptimizer documentation, *Vertex cache optimization*.
- LearnOpenGL, `src/8.guest/2021/3.tessellation`.
