# VFX性能

粒子只有两个三角形，也可能覆盖整个屏幕很多次。VFX性能把模拟、碰撞、排序和像素混合分别测量，降级根据真正瓶颈调整。少粒子不保证低Overdraw，局部快也不保证整帧快。

## 透明效果的成本从哪里来

### Overdraw 的成本

粒子面数很低，不代表便宜。半透明粒子通常关闭 Depth Write，同一像素会执行多层 Fragment Shader、纹理采样、混合和 Render Target 读写。

粗略成本更接近：

$$
\text{Pixel Cost}\propto \text{Covered Pixels}\times\text{Layers}\times\text{Shader Cost}
$$

因此一个贴近镜头的全屏烟片，可能比数千个远处小火星更贵。

### 常见降级手段

- 减小 Billboard 中无效透明边界，或使用更贴合轮廓的低面数 Mesh。
- 按屏幕占比限制 Spawn、Size 和 Lifetime。
- 远距离减少 Emitter、Flipbook 帧率和材质采样。
- 烟雾在 Half/Quarter Resolution Buffer 渲染，再做 Depth-aware Upsample。
- 分离必须排序和可 Additive 的粒子。
- 限制动态光源、阴影粒子和 Scene Color/Depth 采样。
- 为移动端准备独立 Material/Emitter LOD，而不只是减少总粒子数。

低分辨率透明需要处理物体边缘、深度不连续和 TAA 历史，否则会出现 Halo、泄漏和拖影。

### 预算与验证

不要只记录 Particle Count。至少统计：

- 同屏 System/Emitter/Alive Particle；
- Draw Call、Material/Variant；
- 屏幕覆盖率与 Overdraw Heatmap；
- Simulation/Sort/Render GPU 时间；
- Flipbook/Noise 纹理内存和带宽；
- 光源、阴影、碰撞和事件数量。

测试应包含近距离、多个效果叠加、低帧率、大战斗和移动端热稳定状态。单独预览器中的一个效果无法代表 Gameplay 峰值。

## 预算记录

这是诊断数据结构示意，字段来自实际Profiler或设备计数器；没有测量时不填假数字。

```text
SystemBudget { alive, simulationTime, sortTime, drawTime,
               coveredPixels, layers, textureBytes, peakEvents }
```

## 验证方法

近镜头、大战斗、多个效果重叠与持续热状态分别测试。降低分辨率、采样或排序时一次改一个因素，记录画质与整帧关键路径。通用blend公式见Alpha表示，这里只解释工作负载。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[14_性能分析与优化/性能对照实验]]
- [[10_VFX与模拟/GPU粒子系统]]
- [[10_VFX与模拟/VFX纹理动画]]
- [[10_VFX与模拟/溶解材质]]
- [[10_VFX与模拟/屏幕扰动]]
- [[10_VFX与模拟/软粒子]]

## 参考资料

- Unity Documentation, *Visual Effect Graph* and *Particle System*.
- Unreal Engine Documentation, *Niagara Renderers* and *Scalability*.
- GPU Gems, particle and flow simulation chapters.
