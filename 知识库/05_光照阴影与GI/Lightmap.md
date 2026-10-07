# Lightmap

墙面和灯都不动时，运行时反复追踪间接光没有必要。Lightmap把表面光照烘进专用UV，采样时复用结果。它省下积分，却把质量要求转到UV覆盖、边距、方向编码和资产重烘焙上。

## 静态表面怎样保存间接光

### Lightmap

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

### Directional Lightmap

普通 Lightmap 只保存最终颜色，无法对动态 Normal Map 做合理方向响应。Directional Lightmap 会额外保存主导光方向或方向性信息，运行时根据表面法线调整结果。

它提高动态细节表现，也增加纹理和 Shader 成本。

## 运行时查询

HLSL机制片段使用不重叠的光照UV及图集scale/bias，DecodeLightmap与烘焙编码对应。

```hlsl
float2 uv = lightmapUV * scaleBias.xy + scaleBias.zw;
float3 irradiance = DecodeLightmap(Lightmap.Sample(LinearClamp, uv));
float3 diffuse = baseColor * irradiance / 3.14159265;
```

若数据已保存漫反射出射颜色，就不能重复乘反照率或除π。方向性Lightmap另保存方向约束，用于法线响应。

## 验证方法

显示UV2与图集索引，检查重叠、Padding、纹素密度和最低mip。移动灯光或几何时标记烘焙失效，与未变化的参考场景比较接缝与能量。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[06_纹理技术/纹理图集]]
- [[04_光照模型与PBR/法线贴图]]
- [[05_光照阴影与GI/Light Probe]]
- [[05_光照阴影与GI/Reflection Probe]]
- [[05_光照阴影与GI/动态GI]]

## 参考资料

- Epic Games, *Lumen Global Illumination and Reflections*.
- NVIDIA, *RTXGI / Dynamic Diffuse Global Illumination*.
- Unity Manual, *Lightmapping and Light Probes*.
