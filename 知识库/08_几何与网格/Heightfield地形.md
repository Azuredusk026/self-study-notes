# Heightfield地形

高度图能描述地表，却不能直接表达悬挑和洞穴。Heightfield把水平位置映射到一个高度，再用分块网格、边界连接和材质权重构成场景。单位、采样密度和相邻块契约决定它是否能无缝落地。

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

GPU Tessellation 可以让每个地形 Patch 根据屏幕贡献生成不同密度的三角形。细分控制阶段确定边和内部因子。固定细分器生成参数坐标，求值阶段据此采样高度图并计算顶点位置。Direct3D 对应 Hull/Domain，OpenGL 对应 Tessellation Control/Evaluation。

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

## 高度与材质求值

机制伪代码输入[0,1]高度与非负层权重，输出约定世界长度的地表位置和材质混合。

```text
y = baseHeight + sampleHeight(uv) * heightRange
weights = max(layerWeights, 0)
if sum(weights) == 0: weights = fallbackLayer
weights /= sum(weights)
material = BlendLayers(weights, layerMaterials)
```

## 验证方法

相邻Tile边界逐点比较高度、材质权重与法线。测试最低高度精度、斜坡三向采样与缺块回退，显示层权重和检查零权重区域。硬件细分因子机制引用Tessellation与位移。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[08_几何与网格/Tessellation与位移]]
- [[06_纹理技术/Virtual Texture]]
- [[08_几何与网格/LOD选择]]
- [[15_资产与工具管线/程序化资产生成]]
- [[08_几何与网格/植被包裹法线]]
- [[15_资产与工具管线/WFC]]

## 参考资料

- Paul Merrell, *Model Synthesis* and SideFX WFC dungeon generator tutorial.
- Gabriel Taubin, *A Signal Processing Approach to Fair Surface Design*, SIGGRAPH.

- Unity Manual, *LOD Group* and *Terrain Data*.
- Houdini Documentation, *HeightField*, *PDG* and *Houdini Engine for Unity*.
- Lindstrom and Turk, *Fast and Memory Efficient Polygonal Simplification*.
- meshoptimizer documentation, *Vertex cache optimization*.
- LearnOpenGL, `src/8.guest/2021/3.tessellation`.
