# 动态GI

门打开以后，预计算结果不会自动让另一间房变亮。动态GI选择可更新的场景表示，再用有限采样与缓存摊平传播成本。屏幕、体素、距离场和探针保存的信息不同，缺失、漏光和历史滞后也要分别解释。

## 场景变化后怎样更新

### Screen-space GI

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

### Voxel GI

把场景几何或光照注入体素结构，再在体素中传播或追踪。它能访问屏幕外信息，但精度受体素分辨率限制。

常见问题：

- 体素内存和更新成本；
- Thin Geometry 漏光；
- 大世界需要 Clipmap；
- 高光和锐利遮挡难以表达。

Reflective Shadow Map（RSM）在光源视角保存位置、法线和反射通量，把可见表面当作一组虚拟点光源。它能从直接光照结果近似传播一次间接光，但只覆盖光源可见表面，采样数量和漏光控制是主要问题。

Light Propagation Volume（LPV）把 RSM 注入低阶球谐体素，再在网格中传播；VXGI 使用体素锥追踪近似积分更宽的方向范围。SVOGI 用稀疏体素八叉树保存多尺度场景信息，减少均匀体素的空区浪费。它们共同面对体素分辨率、场景更新、显存和漏光之间的取舍。

### Distance Field GI

Mesh SDF 可以快速估计光线到表面的距离，适合软件 Ray March。它比屏幕空间完整，但 SDF 分辨率、薄片、蒙皮和动态更新仍有限制。

### Probe-based Dynamic GI

DDGI 等方法在空间布置 Probe，每个 Probe 向场景发射少量射线，更新辐照度和距离信息。运行时插值 Probe 结果。

需要解决：

- Probe 被放进几何内部；
- 可见性和漏光；
- 更新预算；
- 滚动体积和大世界；
- 时域稳定。

SDFDDGI 可以用距离场加速 Probe Ray 的场景查询。大世界通常把 Probe 组织成随相机移动的 Clipmap，各级覆盖不同空间尺度。更新时只重算新进入或失效的区域，并保留历史滞后以摊平成本。

Screen Probe 把探针布置在屏幕或重建表面附近，能把计算集中到当前可见区域，并利用屏幕深度、法线和运动信息。它仍需要世界空间追踪或缓存补足屏幕外、遮挡后和反射方向缺失的信息。

### Lumen 的理解框架

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

移动遮挡物、改变灯光、相机瞬移与跨体积边界分别测试。输出场景表示、有效探针、历史权重和更新时间，比较同场景离线参考。Lumen内部接口按目标Unreal版本核对，当前记录为UNVERIFIED运行状态。

## 相关主题

- [[12_光线追踪/光追降噪]]
- [[05_光照阴影与GI/Light Probe]]
- [[05_光照阴影与GI/Lightmap]]
- [[05_光照阴影与GI/Reflection Probe]]

## 参考资料

- Epic Games, *Lumen Global Illumination and Reflections*.
- NVIDIA, *RTXGI / Dynamic Diffuse Global Illumination*.
- Unity Manual, *Lightmapping and Light Probes*.
