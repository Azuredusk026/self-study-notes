# Forward Rendering与Forward+

材质着色时逐盏灯计算很直接，灯一多，每个片元遍历的无关光源也变多。Forward+把筛灯提前，材质仍在前向阶段计算。先检查列表保守性和资源可见性，再看提交、像素和列表构建的总成本，才能判断这一步是否改善整帧。

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

## Forward+

Forward+ 保留 Forward 材质阶段，但先用 Tiled/Clustered Culling 建立灯列表。Pixel Shader 只遍历当前区域的灯。

它结合了：

- Forward 对透明、MSAA 和复杂材质的适应；
- 屏幕分区对大量灯的筛选能力。

代价是需要构建灯列表，且不透明和透明阶段可能使用不同列表或深度信息。

## 局部灯列表着色

以下为 HLSL 函数轮廓。输入片元位置、法线和对应区域索引，区域表记录灯索引缓冲的起点和数量。真实 BRDF、阴影和距离衰减由 `EvaluateLight` 提供。

```hlsl
float3 ShadeLocalLights(float3 positionWS, float3 normalWS, uint region)
{
    uint2 range = LightRanges[region];
    float3 lighting = 0.0;
    for (uint localIndex = 0; localIndex < range.y; ++localIndex)
    {
        uint lightIndex = LightIndices[range.x + localIndex];
        lighting += EvaluateLight(Lights[lightIndex], positionWS, normalWS);
    }
    return lighting;
}
```

读取前要保证构建列表的计算写入对图形着色可见。区域索引、数组容量与灯数据寿命必须匹配。用遍历全部光源的参考着色验证局部列表，结果差异提示漏灯、范围或阴影数据错误。

## 验证方法

- 记录材质绘制与灯光循环，确认列表只影响候选灯。
- 增加灯光和透明对象，对比普通前向与 Forward+ 的整帧耗时。
- 检查溢出列表、深度范围及透明路径使用的光源集合。

## 相关主题

- [[02_GPU与光栅化管线/一帧如何到达屏幕]]
- [[05_光照阴影与GI/直接光照]]
- [[13_渲染架构/GBuffer布局]]
- [[13_渲染架构/Render Pass、Command Buffer与Render Graph]]
- [[14_性能分析与优化/帧瓶颈怎么判断]]

- [[13_渲染架构/渲染路径与光源组织]]

示例与验证范围：代码按文中前提解释机制，完整类型、资源和项目状态需由接入工程补齐。本轮以正文、公式和调用范围复读为主，未执行此页的目标引擎运行与GPU性能实验。

## 参考资料

- Ola Olsson et al., *Clustered Deferred and Forward Shading*.
- Johan Andersson, *Tiled Deferred Shading*.
- Unity and Unreal documentation on Forward+, Deferred and mobile renderers.
- LearnOpenGL, `src/5.advanced_lighting/8.1.deferred_shading`.
