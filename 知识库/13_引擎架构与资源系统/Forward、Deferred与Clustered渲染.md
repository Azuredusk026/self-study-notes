# Forward、Deferred 与 Clustered 渲染

渲染路径的主要差别是：什么时候计算材质和光照，怎样找出影响当前表面或像素的光源，以及中间数据如何保存。

## 专题阅读

- [[13_引擎架构与资源系统/前向渲染、Forward加与材质光照流程]]：前向渲染在材质着色时计算光照。
- [[13_引擎架构与资源系统/延迟渲染、光体积与GBuffer消费]]：延迟渲染先保存可见表面的材质属性，再执行光照。
- [[13_引擎架构与资源系统/分块与簇光照剔除]]：分块与簇剔除将光源分配给屏幕区域或三维簇，再由着色器读取局部列表。

## 验证方法

- 在 Frame Capture 中找 Geometry Pass 和每个 Lighting Event。
- 单独查看 GBuffer 通道和材质分类。
- 统计每 Tile/Cluster 灯数、最大值和溢出。
- 用 100 个重叠灯和 100 个不重叠灯分别测试。
- 检查 Directional Fullscreen Pass、Point Light Volume 或 Compute Lighting 的实际执行。

## 相关主题

- [[02_GPU与光栅化管线/一帧如何到达屏幕]]
- [[05_光照阴影与GI/光源与直接光照]]
- [[13_引擎架构与资源系统/GBuffer布局设计与通道压缩]]
- [[13_引擎架构与资源系统/Render Pass、Command Buffer与Render Graph]]
- [[14_性能分析与优化/帧时间、瓶颈与GPU成本]]

## 参考资料

- Ola Olsson et al., *Clustered Deferred and Forward Shading*.
- Johan Andersson, *Tiled Deferred Shading*.
- Unity and Unreal documentation on Forward+, Deferred and mobile renderers.
- LearnOpenGL, `src/5.advanced_lighting/8.1.deferred_shading`.
