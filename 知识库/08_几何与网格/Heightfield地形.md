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

## 采样位置与世界法线

一个包含N_x×N_z个端点样本的网格、水平尺寸L_x×L_z米，样本间距为 `dx=L_x/(N_x-1)`、`dz=L_z/(N_z-1)`，两个样本数至少为2。第(i,j)个顶点为 `(origin.x+i*dx, baseHeight+h[i,j]*heightRange, origin.z+j*dz)`。heightRange以米计，输入h在[0,1]，按线性数据读取。对于b位UNORM高度，量化步长约为 `heightRange/(2^b-1)`；高度范围100米时8位约0.392米，16位约1.53毫米。

在样本之间可用[[06_纹理技术/纹理采样与过滤]]的双线性模型求值。几何端点与纹素中心的映射需要一致：网格UV=i/(N-1)，对应高度纹素中心的UV为 `(i+0.5)/N`；导入接口若已完成转换，应使用其约定。

将采样高度解码成米后，内部点用中心差分：

$$h_x=\frac{h_{i+1,j}-h_{i-1,j}}{2dx},\quad h_z=\frac{h_{i,j+1}-h_{i,j-1}}{2dz},\quad n=normalize(-h_x,1,-h_z).$$

这个式子来自两个切向量(1,h_x,0)、(0,h_z,1)的叉积，并选择朝上的方向。h=2x+3z时，无论采样间距是否相同，都应得到normalize(-2,1,-3)。省掉dx/dz会让地形缩放改变坡度。

相邻Tile共享边高度必须一致，边界法线还需要邻Tile的一圈高度；只对各块自身Clamp会得到不同的边缘导数。缺邻居时采用明确的单边差分或粗层回退，待邻块到达后更新接缝法线。

### 相邻层级的边界

粗块一条边只有端点A与B，细块还有中点M。即使两块共享A/B，若细块的M来自原始高度而不在粗边线段上，便形成T形裂缝。Stitching可以让细侧连接关系在边界匹配粗侧，或把M约束到粗边插值高度；后者暂时牺牲边缘细节。相邻层级差限制为一级，会使需要处理的边界模式保持有限。

Skirt则沿块边缘向下延伸一圈几何，遮住裂口。它没有让两份表面真正重合，侧视、洞口或阴影中仍可能露出裙边，因此裙长应覆盖已知高度差并纳入Bounds。相邻块高度源不一致属于数据错误，不能只靠无限加深裙边掩盖。

## GPU 细分地形

GPU Tessellation 可以让每个地形 Patch 根据屏幕贡献生成不同密度的三角形。细分控制阶段确定边和内部因子。固定细分器生成参数坐标，求值阶段据此采样高度图并计算顶点位置。Direct3D 对应 Hull/Domain，OpenGL 对应 Tessellation Control/Evaluation。

细分因子适合由边的屏幕像素长度或位移误差决定。只按 Patch 中心到相机的距离会让同一共享边的两侧得到不同因子，产生裂缝。稳定方案包括：

- 共享边只使用两个端点或同一边界球计算因子；
- 相邻Patch约束到兼容层级，并保证共享边位移、纹理LOD和求值一致；
- 使用 Fractional Even/Odd Partitioning 缓和因子变化；
- 最终边界增加 Skirt 处理地形 Tile 接缝。

细分增加的是当前帧生成和处理的图元，不会自动降低高度纹理带宽，实际采样量还取决于生成点数、mip和缓存复用。因子过高会把瓶颈推到 Tessellator、Vertex/Domain Shader 或光栅化。近处需要真实轮廓时细分有效；远处地形仍应依赖 Chunk LOD、Mipmap 和流送。

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

## 材质权重求值

机制伪代码输入[0,1]高度与非负层权重，输出约定世界长度的地表位置和材质混合。

```text
y = baseHeight + sampleHeight(uv) * heightRange
weights = max(layerWeights, 0)
if sum(weights) == 0: weights = fallbackLayer
weights /= sum(weights)
baseColor = sum(weights[i] * linearBaseColor[i])
normal = normalize(sum(weights[i] * normalInSameSpace[i]))
```

此混合假定颜色已在线性空间，法线位于同一空间且加权和非零。零法线和需要稳定备用方向；粗糙度等BRDF参数的线性混合是一种材质选择，不能等同于精确混合两个BRDF。fallbackLayer应为有效的一热权重。

## 验证方法

相邻Tile边界逐点比较高度、材质权重与法线。测试最低高度精度、斜坡三向采样与缺块回退，显示层权重和检查零权重区域。硬件细分因子机制引用Tessellation与位移。

CPU参考`height_normal`使用不同世界间距复算解析斜坡，见 [reference.py](../examples/revision_06_08/reference.py)，运行 `python -B 知识库/examples/revision_06_08/test_reference.py`。未执行Houdini生成、Tile导出、引擎地形或GPU细分；这些状态为尚未验证。

## 相关主题

- [[08_几何与网格/Tessellation与位移]]
- [[06_纹理技术/Virtual Texture]]
- [[08_几何与网格/LOD选择]]
- [[15_资产与工具管线/程序化资产生成]]
- [[08_几何与网格/植被包裹法线]]
- [[15_资产与工具管线/WFC]]

## 参考资料

- [SideFX，Heightfields and terrains](https://www.sidefx.com/docs/houdini/heightfields/index.html)：2026-10-22核读Houdini22.0的Overview与Limitations，高度层及二维表示限制。
- [Microsoft，Tessellation Stages](https://learn.microsoft.com/en-us/windows/win32/direct3d11/direct3d-11-advanced-stages-tessellation)：固定参数域生成与Domain求值。
- 世界采样间距、量化步长与高度梯度法线由本文公式推导，CPU解析斜坡提供独立检查。
