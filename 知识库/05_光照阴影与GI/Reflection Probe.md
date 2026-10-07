# Reflection Probe

镜面用一张全局环境图，在室内会把墙面当作无限远。Reflection Probe保存某个捕获位置的六面环境，并按区域混合或近似修正视差。捕获结果还要按粗糙度预过滤，运行时求值交给IBL。

## Reflection Probe

Reflection Probe 保存局部环境反射，通常是预过滤 Cubemap。它主要服务间接镜面，而 Light Probe 主要服务低频漫反射。

两者名字相似，数据和用途不同。

## 局部反射查询

这是模型伪代码，probeBox与方向位于同一世界空间；无有效探针时使用已定义的环境回退。

```text
reflection = reflect(-viewDirection, normal)
hit = IntersectProbeBox(position, reflection)
sampleDirection = normalize(hit - capturePosition)
color = SamplePrefilteredCube(sampleDirection, roughness)
```

盒投影假设环境接近包围盒表面，无法表达任意内部遮挡；不能把它当作真实反射光线追踪。

## 验证方法

把镜面球从捕获中心移向墙面，比较未修正与盒投影。六面方向标签、混合边界和动态更新延迟分别检查，过滤与BRDF LUT约定见IBL。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[04_光照模型与PBR/IBL]]
- [[04_光照模型与PBR/Cubemap环境采样]]
- [[05_光照阴影与GI/Lightmap]]
- [[05_光照阴影与GI/Light Probe]]
- [[05_光照阴影与GI/动态GI]]

## 参考资料

- Epic Games, *Lumen Global Illumination and Reflections*.
- NVIDIA, *RTXGI / Dynamic Diffuse Global Illumination*.
- Unity Manual, *Lightmapping and Light Probes*.
