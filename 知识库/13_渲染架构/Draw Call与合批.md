# Draw Call与合批

Frame Debugger里的Draw数量减少了，GPU时间却没变，说明原瓶颈可能不在提交。合批改变命令与状态组织，实例化仍会为每个实例处理顶点和像素。把CPU准备、Draw、实例数据与覆盖分开计量，再比较静态、动态、SRP和实例路径。

## 绘制状态

CPU 需要确定：

- 管线状态；
- 顶点/索引缓冲；
- Descriptor/Resource；
- Constant 和实例数据；
- Draw 参数。

GPU 执行后，还要处理顶点、光栅化、像素着色器、深度和混合。减少 Draw 只解决其中一部分成本。

## 状态切换成本

连续 Draw 如果共享着色器、材质状态和资源布局，CPU 和 GPU 更容易复用状态。频繁切换管线、渲染目标、Descriptor 和纹理会增加验证、缓存失效或管线空泡。

渲染排序经常同时考虑：

- 不透明物体从前向后，提高 Early-Z；
- 按管线/材质分组，减少状态切换；
- 透明物体从后向前，保证混合近似正确。

这些目标可能冲突，需要按场景权衡。

## 静态合批

把静态网格变换到统一空间并合并缓冲，减少提交。

优点：

- 运行时不需要逐对象变换；
- 可以减少小网格 Draw。

代价：

- 合并后的顶点会复制，增加内存；
- 大合并网格可能降低剔除粒度；
- 不能单独移动；
- Lightmap、材质和平台限制影响能否合并。

## 动态合批

CPU 每帧把少量动态网格转换并合并。它只适合很小的网格和有限属性。

现代平台上，CPU 变换和拷贝成本可能比节省的 Draw 更贵。不同 Unity 版本和 SRP 支持也不同，不能把它当默认优化。

## SRP Batcher

Unity SRP Batcher 的重点是减少相同着色器 Variant 间材质常量设置和 CPU 状态准备。它把引擎内置数据和材质数据按稳定布局组织，让 Draw 间只更新必要内容。

它通常**不会把多个对象变成一个 Draw Call**。Profiler 中 Draw 数可能不变，但 CPU 渲染线程时间下降。

材质着色器的 Constant 缓冲布局、兼容 Pass 和 Keyword 会影响是否进入 SRP Batcher。

它的前提是**相同着色器 Variant**，而不是相同材质。同一着色器的不同材质可以进入同一批，因为材质数据被组织成稳定布局的常量缓冲，切换材质只需换绑定偏移，不必重新设置全部状态。

### 与 GPU Instancing 的取舍

两者优化的是不同环节，因此存在选择问题：

| | 减少的对象 | 前提 | 典型场景 |
|---|---|---|---|
| SRP Batcher | 材质常量与状态准备开销 | 相同着色器 Variant | 材质多样、网格各异的普通场景 |
| GPU Instancing | Draw Call | 相同网格与材质 | 同屏大量相同网格 |

同屏有大量相同网格时，GPU Instancing 实打实地减少 Draw Call 数量，可能比只减少状态准备更有价值，结果由网格、实例、材质与设备计时决定。

关键在于两者**不能同时作用于同一对象**，且在特定Unity/SRP版本与Renderer路径中存在优先关系，示意为：

```text
SRP Batcher > GPU Instancing > Dynamic Batching
```

这意味着在启用 SRP Batcher 的项目中，兼容 SRP Batcher 的着色器不会走 Instancing 路径——即使场景中确实有几千个相同的网格。想让这批对象走 Instancing，需要主动让其着色器不满足 SRP Batcher 的兼容条件。

这是一个容易踩的坑：开发者为大量重复物体写好 Instancing 支持，却发现 Frame Debugger 显示它们走的是 SRP Batcher，Draw Call 数毫无变化。

可先检查目标 URP 版本中所用着色器的 SRP Batcher 兼容状态，再比较 CPU 提交时间。大量同网格、同材质对象适合评估实例化，但最终选择取决于可见实例数、材质变体、剔除粒度和数据上传成本。

本节自动 Renderer 路径的优先关系以 Unity 6000.0 的 GPU Instancing 文档为范围。显式 `Graphics.RenderMeshInstanced`、间接绘制及其他批渲染入口各有自己的调度方式，不能由自动 Renderer 的优先关系推断全部 API。验证时保留实际调用入口、渲染管线与着色器兼容原因，再解释 Draw 数量。

## GPU Instancing

多个对象共享网格和材质/着色器 Variant，只为每个实例提供不同数据：

- 变换；
- 颜色；
- 动画帧；
- LOD/可见性；
- 自定义属性。

CPU 可以用一次 Instanced Draw 提交多个实例。主要收益是减少 Draw Call 和 CPU-GPU 命令交互，不是因为“只画一次模型”或自动减少像素工作。

GPU 仍会为每个实例处理对应顶点和片元。

顶点着色器可以使用系统提供的实例ID 索引实例缓冲。下面的例子让一个网格共享顶点数据，只为每个实例读取一份变换和颜色：

```hlsl
StructuredBuffer<float4x4> ObjectToWorld : register(t0);
StructuredBuffer<float4> InstanceColor : register(t1);

VSOutput VSMain(VSInput input, uint instanceID : SV_InstanceID)
{
    VSOutput output;
    float4 positionWS = mul(ObjectToWorld[instanceID],
                            float4(input.positionOS, 1.0));
    output.positionCS = mul(ViewProjection, positionWS);
    output.color = InstanceColor[instanceID];
    return output;
}
```

Draw 的 `startInstance`、缓冲中的基址和 `SV_InstanceID` 语义需要按 API 对齐。实例矩阵的行列主序也必须与 CPU 上传格式一致。

## 实例数据成本

每实例完整 4x4 矩阵需要 64 字节。大量实例时可以保存位置、四元数、缩放，或使用压缩格式减少带宽，但会增加着色器解码。

实例属性应连续存储，避免每实例随机访问多个缓冲。

## GPU 动画纹理

把每帧骨骼矩阵或变换烘焙到纹理/缓冲。每个实例保存动画 ID、时间和混合权重，顶点着色器采样骨骼数据完成蒙皮。

动画混合可以：

1. 分别采样动画 A/B 的骨骼变换；
2. 平移做 Lerp，旋转做 Nlerp/Slerp；
3. 重新组合变换后蒙皮。

直接线性混合矩阵可能破坏正交性并产生缩放。双采样也会增加纹理带宽和顶点成本。

## MaterialPropertyBlock

Unity MPB 可以为 Renderer 提供每对象参数而不克隆材质。它是否与 SRP Batcher、GPU Instancing 兼容取决于属性声明、管线和 Unity 版本。

不能只看“没有生成材质实例”。需要在 Frame Debugger/Profiler 检查实际 Batcher 原因。

## 间接绘制

GPU Culling 后把可见实例数量和参数写入 Indirect Argument 缓冲，再由 GPU 发起 Draw。CPU 不需要回读可见列表。

这能进一步减少大量实例的 CPU 工作，但需要：

- GPU 可见性和 LOD；
- Prefix Sum/Compaction；
- Indirect Argument；
- 资源屏障；
- 避免读回同步。

## 合批条件

- 材质/着色器 Variant 不同；
- 渲染状态或 Pass 不同；
- 网格不同且方案要求相同网格；
- Lightmap、Probe、阴影状态不同；
- Per-object 数据没有放入兼容实例通道；
- 排序或透明顺序不能合并；
- 负缩放、特殊渲染层或 Renderer Feature 分开绘制。

还要留意“合批成功但不是期望的那一种”：Frame Debugger 会标明每个批次采用的路径，看到 SRP Batcher 而非 Instancing 时，通常是优先级而非兼容性问题。

## 验证方法

- CPU Profiler 查看渲染线程、Batch 构建和提交时间。
- Frame Debugger 查看为什么一个对象没有进入目标 Batcher。
- RenderDoc 检查一次 Draw 的实例 Count。
- 分别统计 Draw、SetPass/PSO Switch、顶点和像素成本。
- 比较合批前后内存、剔除粒度和 GPU 时间，不只比较 Draw 数。

## 相关主题

- [[03_Shader编程/Shader Variant管理]]
- [[09_动画系统/骨骼动画与蒙皮]]
- [[26_GPU驱动与虚拟几何/GPU-Driven Rendering]]
- [[25_UI与文本/UI绘制]]、[[25_UI与文本/文字渲染]]
- [[14_性能分析与优化/帧瓶颈诊断]]

示例与验证范围：代码按文中前提解释机制，完整类型、资源和项目状态需由接入工程补齐。完整目标引擎运行与GPU性能为UNVERIFIED；正文给出的机制与实际实验范围分别记录。

## 参考资料

- [Unity 6000.0：GPU Instancing](https://docs.unity3d.com/6000.0/Documentation/Manual/GPUInstancing.html)：SRP Batcher 相容性与显式 Graphics.RenderMeshInstanced 路径。
