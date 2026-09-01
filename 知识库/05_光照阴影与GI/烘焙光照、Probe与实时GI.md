# 烘焙光照、Probe 与实时 GI

全局光照（Global Illumination，GI）包含光在场景中的间接传播。实时项目不会只用一种方案，而是组合静态预计算、空间 Probe、屏幕空间、体素、距离场和光线追踪。

## Lightmap

Lightmap 把静态表面的烘焙光照保存到纹理。运行时通过第二套 UV 采样。

它适合：

- 静态环境的间接光和软阴影；
- 移动端和低端设备；
- 需要稳定画面且光照变化少的场景。

主要限制：

- 几何和灯光变化后需要重烘焙；
- 占用纹理内存和流送带宽；
- UV2 需要不重叠、足够 Padding 和稳定 Texel Density；
- 动态物体不能直接使用静态表面的 Lightmap。

## Directional Lightmap

普通 Lightmap 只保存最终颜色，无法对动态 Normal Map 做合理方向响应。Directional Lightmap 会额外保存主导光方向或方向性信息，运行时根据表面法线调整结果。

它提高动态细节表现，也增加纹理和 Shader 成本。

## Light Probe

Light Probe 在离散空间点保存低频环境光，常用 SH 表示。动态物体根据位置插值附近 Probe，再按表面法线求光照。

Probe 的主要问题不是“数量不够”这么简单：

- Probe 放在墙内会记录错误环境；
- 墙两侧插值会漏光；
- 光照突变处需要更合理分布；
- 角色活动范围以外的 Probe 没有价值；
- 低阶 SH 不能表达锐利方向光和高频阴影。

## Reflection Probe

Reflection Probe 保存局部环境反射，通常是预过滤 Cubemap。它主要服务间接镜面，而 Light Probe 主要服务低频漫反射。

两者名字相似，数据和用途不同。

## Screen-space GI

SSGI 使用当前屏幕的颜色、深度和法线估计间接光。

优点：

- 能反映动态画面；
- 与屏幕细节对齐；
- 不需要完整场景加速结构。

限制：

- 看不到屏幕外和被遮挡表面；
- 深度缓冲只有一层；
- 容易出现边缘漏光、拖影和缺失；
- 通常需要时域降噪。

## Voxel GI

把场景几何或光照注入体素结构，再在体素中传播或追踪。它能访问屏幕外信息，但精度受体素分辨率限制。

常见问题：

- 体素内存和更新成本；
- Thin Geometry 漏光；
- 大世界需要 Clipmap；
- 高光和锐利遮挡难以表达。

Reflective Shadow Map（RSM）在光源视角保存位置、法线和反射通量，把可见表面当作一组虚拟点光源。它能从直接光照结果近似传播一次间接光，但只覆盖光源可见表面，采样数量和漏光控制是主要问题。

Light Propagation Volume（LPV）把 RSM 注入低阶球谐体素，再在网格中传播；VXGI 使用体素锥追踪近似积分更宽的方向范围。SVOGI 用稀疏体素八叉树保存多尺度场景信息，减少均匀体素的空区浪费。它们共同面对体素分辨率、场景更新、显存和漏光之间的取舍。

## Distance Field GI

Mesh SDF 可以快速估计光线到表面的距离，适合软件 Ray March。它比屏幕空间完整，但 SDF 分辨率、薄片、蒙皮和动态更新仍有限制。

## Probe-based Dynamic GI

DDGI 等方法在空间布置 Probe，每个 Probe 向场景发射少量射线，更新辐照度和距离信息。运行时插值 Probe 结果。

需要解决：

- Probe 被放进几何内部；
- 可见性和漏光；
- 更新预算；
- 滚动体积和大世界；
- 时域稳定。

SDFDDGI 可以用距离场加速 Probe Ray 的场景查询。大世界通常把 Probe 组织成随相机移动的 Clipmap，各级覆盖不同空间尺度。更新时只重算新进入或失效的区域，并保留历史滞后以摊平成本。

Screen Probe 把探针布置在屏幕或重建表面附近，能把计算集中到当前可见区域，并利用屏幕深度、法线和运动信息。它仍需要世界空间追踪或缓存补足屏幕外、遮挡后和反射方向缺失的信息。

## Lumen 的理解框架

Lumen 不是单一“光追开关”。理解时可以拆成：

- 场景的可追踪表示，例如屏幕空间、Mesh SDF、Global Distance Field 或硬件 RT；
- Surface Cache 等可重用表面表示；
- 对直接/间接光的采样与缓存；
- Final Gather、Probe 和时域累积；
- 不同表示之间的回退和组合。

具体实现会随 Unreal 版本变化。笔记需要根据目标版本的官方文档、源码和帧捕获核验，不能把某篇旧文章当成永久架构。

## 静态和动态方案怎么选

| 需求 | 更常见方向 |
|---|---|
| 静态场景、低端平台 | Lightmap + Probe |
| 小范围动态间接光 | SSGI、局部 Probe 更新 |
| 大场景动态 GI | Clipmap、Distance Field、Probe、硬件 RT 的组合 |
| 高质量反射 | Reflection Probe + SSR + RT 回退组合 |

选择取决于动态范围、平台、内存、时间稳定、内容制作成本和画质目标。

## 验证方法

- 分开显示直接光、间接漫反射和间接镜面。
- 关闭主光，检查环境和反弹是否来自预期系统。
- 移动遮挡物，观察 GI 更新延迟和历史拖影。
- 检查 Probe 位置、插值权重和有效性。
- 在屏幕边缘、镜后、薄墙和大尺度场景测试漏光。
- 对比静态参考烘焙或离线路径追踪结果。

## 相关主题

- [[01_数学与采样/概率采样、积分与球谐函数]]
- [[04_光照模型与PBR/法线贴图、切线空间与IBL]]
- [[12_光追与现代渲染/实时光追、采样与降噪]]
- [[12_光追与现代渲染/GPU-Driven管线与Nanite]]

## 参考资料

- Epic Games, *Lumen Global Illumination and Reflections*.
- NVIDIA, *RTXGI / Dynamic Diffuse Global Illumination*.
- Unity Manual, *Lightmapping and Light Probes*.
