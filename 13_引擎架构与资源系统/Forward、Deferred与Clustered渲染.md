# Forward、Deferred 与 Clustered 渲染

渲染路径的主要差别是：什么时候计算材质和光照，怎样找出影响当前表面或像素的光源，以及中间数据如何保存。

## Forward Rendering

Forward 在绘制物体时直接计算光照并输出最终颜色。

简化流程：

```text
Object → Vertex Shader → Rasterization → Material + Lights → Color
```

优点：

- 流程直接；
- 透明和自定义材质容易接入；
- MSAA 相对自然；
- 中间 Buffer 少，适合带宽敏感平台。

问题是要先决定每个物体受哪些灯影响。传统 Multi-pass Forward 可能对额外灯重复绘制物体；Single-pass Forward 会把灯列表传给 Shader，但列表长度和分支受限。

不能简单说 Forward 的复杂度是 $N^2$。实际成本取决于可见对象、每个对象重叠灯数、屏幕覆盖、Pass 和剔除策略。

## Deferred Rendering

Deferred 先把可见表面的属性写入 GBuffer，再在屏幕空间计算光照。

### Geometry Pass

典型 GBuffer 保存：

- Base Color；
- Normal；
- Roughness、Metallic、AO；
- Emissive 或材质分类；
- Depth；
- Motion Vector 常在独立 Buffer。

具体布局取决于引擎、平台和材质模型。每多一个通道都会增加显存和带宽。

### Lighting Pass

读取 GBuffer，重建表面位置，再累加灯光。

有 100 盏灯时，不是“只读一次 GBuffer 就结束”。仍要计算影响像素的灯，只是材质和几何属性不必对每盏灯重复绘制。

## Deferred 中怎样画灯

### Fullscreen Pass

方向光影响全屏，可以画一个全屏三角形。每个像素读取 GBuffer 并计算方向光。

### Light Volume

点光源用球体、Spot Light 用锥体近似影响范围。只在 Volume 覆盖的像素计算该灯。

Depth/Stencil、Front/Back Face 和相机位于 Volume 内外时的状态需要正确设置，否则会漏算或重复计算。

### Tiled Deferred

先把屏幕分成 Tile，例如 16x16。Compute Shader 计算每个 Tile 与哪些灯相交，再让像素只遍历该 Tile 的灯列表。

它减少大量小 Light Volume Draw，也提高同 Tile 线程读取光源数据的局部性。

## Forward+

Forward+ 保留 Forward 材质阶段，但先用 Tiled/Clustered Culling 建立灯列表。Pixel Shader 只遍历当前区域的灯。

它结合了：

- Forward 对透明、MSAA 和复杂材质的适应；
- 屏幕分区对大量灯的筛选能力。

代价是需要构建灯列表，且不透明和透明阶段可能使用不同列表或深度信息。

## Clustered Rendering

二维 Tile 无法区分同一屏幕区域内近处和远处的灯。Clustered Rendering 再沿深度划分，把视锥变成三维 Cluster。

优势：

- 深度跨度大的场景中灯列表更短；
- 透明物体可以根据自身深度选择 Cluster；
- 适合大量局部灯、Decal 和 Probe。

问题：

- Cluster 尺寸和深度切分需要调节；
- 灯列表需要前缀和、原子或固定上限；
- 超大灯会进入很多 Cluster；
- 列表溢出必须有明确行为。

## Deferred 的限制

- GBuffer 带宽和内存大；
- 多材质模型需要编码分类或额外数据；
- 透明通常仍走 Forward；
- MSAA 成本和 Resolve 更复杂；
- 移动端 Tile-based GPU 可能不适合把大 GBuffer 写回外部内存；
- 每像素只保留最前表面，不适合多层材质。

## Deferred 并不一定更快

大量小灯、复杂不透明材质时可能占优。灯很少、分辨率高、带宽有限或透明很多时，Forward/Forward+ 可能更合适。

比较应记录：

- Geometry 和 Lighting Pass GPU 时间；
- GBuffer 字节/像素；
- 平均每 Tile/Cluster 灯数；
- Light List 构建成本；
- 透明和后处理占比；
- 目标 GPU 的带宽和 Tile 架构。

## 验证方法

- 在 Frame Capture 中找 Geometry Pass 和每个 Lighting Event。
- 单独查看 GBuffer 通道和材质分类。
- 统计每 Tile/Cluster 灯数、最大值和溢出。
- 用 100 个重叠灯和 100 个不重叠灯分别测试。
- 检查 Directional Fullscreen Pass、Point Light Volume 或 Compute Lighting 的实际执行。

## 相关主题

- [[02_GPU与光栅化管线/一帧如何到达屏幕]]
- [[05_光照阴影与GI/光源与直接光照]]
- [[13_引擎架构与资源系统/Render Pass、Command Buffer与Render Graph]]
- [[14_性能分析与优化/帧时间、瓶颈与GPU成本]]

## 参考资料

- Ola Olsson et al., *Clustered Deferred and Forward Shading*.
- Johan Andersson, *Tiled Deferred Shading*.
- Unity and Unreal documentation on Forward+, Deferred and mobile renderers.
