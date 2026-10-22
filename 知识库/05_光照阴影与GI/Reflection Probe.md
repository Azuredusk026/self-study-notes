# Reflection Probe

镜面用一张全局环境图，在室内会把墙面当作无限远。Reflection Probe保存某个捕获位置的六面环境，并按区域混合或近似修正视差。捕获结果还要按粗糙度预过滤，运行时求值交给IBL。

## 局部反射数据

Reflection Probe 保存局部环境反射，通常是预过滤 Cubemap。它主要服务间接镜面，而 Light Probe 主要服务低频漫反射。

两者名字相似，数据和用途不同。

## 局部反射查询

捕获中心 $C$ 与着色点 $P$ 不同。直接以反射方向 $R$ 查询 Cubemap，隐含两条平行射线看见同一环境；室内墙面距离有限，这个假设会产生位置偏差。盒投影先求 $P+tR$ 与代表房间的盒边界交点 $Q$，再以 $Q-C$ 查询捕获图，使两次查询指向同一个近似墙面位置。

以下 HLSL 机制函数用于轴对齐包围盒，位置均为世界坐标且单位一致。`P` 位于盒内，`R` 为单位方向；盒外查询返回失败，由调用端使用其他探针或全局环境。

```hlsl
bool BoxProjectedDirection(float3 P, float3 R, float3 boxMin,
    float3 boxMax, float3 capturePosition, out float3 direction)
{
    direction = R;
    if (any(P < boxMin) || any(P > boxMax) || dot(R,R) == 0.0)
        return false;
    float exitDistance = 3.402823466e+38F;
    for (uint axis=0; axis<3; ++axis) {
        if (R[axis] > 0.0)
            exitDistance = min(exitDistance, (boxMax[axis]-P[axis])/R[axis]);
        else if (R[axis] < 0.0)
            exitDistance = min(exitDistance, (boxMin[axis]-P[axis])/R[axis]);
    }
    float3 toHit = P + exitDistance*R - capturePosition;
    if (dot(toHit,toHit) == 0.0) return false;
    direction = normalize(toHit);
    return true;
}
```

射线从盒内出发，三个轴中最早到达的出向平面就是出口。某分量为零时，射线与对应平面平行，跳过该轴可避免 `0/0`。旋转盒需把位置和方向变到盒局部空间求交，再将交点变回环境采样空间。

以边界为 $[-1,1]^3$、捕获中心为原点为例：着色点 $(0.5,0,0)$ 沿正Z反射，与墙相交于 $(0.5,0,1)$，故Cubemap方向中的 $x/z=0.5$；直接查询正Z会错失这段横向位置变化。

## 探针混合与更新

每个探针先用自己的盒和捕获中心完成查询，再混合得到的线性HDR颜色。把两个捕获方向平均后只采一次图，并不能表示两份环境。可用着色点到盒最近面的内部距离 $d$ 和正的混合宽度 $b$ 构造 $w=\mathrm{saturate}(d/b)$，多个探针以 $w_i/\sum w_i$ 混合时，权重只控制探针之间的相对占比。只有一个探针时，任意非零权重都会被归一化成 1，直到盒边界才突然切到全局环境。

需要连续过渡到全局环境时，可为全局颜色 $C_g$ 保留剩余权重。令 $W=\sum_i w_i$，采用

$$
C=\frac{\sum_i w_i C_i+\max(1-W,0)C_g}{\max(1,W)}.
$$

单探针权重从 1 降到 0 时，这就是局部与全局颜色的线性混合；多个探针总权重超过 1 时，仅归一化局部结果。所有输入颜色相同会保持原值。重叠区域仍需留足宽度，权重构造与捕获曝光共同决定过渡效果。这是本文的简化权重策略，具体引擎还可能按优先级、体积或独立混合区域选探针。

捕获图应固定曝光或恢复为统一的场景线性值。移动物体和灯光可能使缓存过期，六面捕获与粗糙度预过滤的更新需要一并调度。详见 [[04_光照模型与PBR/Cubemap环境采样]] 和 [[04_光照模型与PBR/IBL]]。

盒投影把环境近似为盒表面，不能表示盒内任意物体的深度和遮挡。粗糙反射还涉及一簇方向，单一投影方向只是近似；因此墙面视差改善不等于得到了真实反射追踪。

## 验证方法

把镜面球从捕获中心移向墙面，比较未修正与盒投影。六面方向标签、混合边界和动态更新延迟分别检查，过滤与BRDF LUT约定见IBL。

[test_gi.py](../examples/revision/test_gi.py) 检查捕获中心恒等情况、平行轴、偏移点与盒外/零方向回退，以及常量环境保持、单探针到全局环境的连续过渡和多探针归一化；正文函数通过DXC编译。Cubemap内容与GPU画面尚未验证。

## 相关主题

- [[04_光照模型与PBR/IBL]]
- [[04_光照模型与PBR/Cubemap环境采样]]
- [[05_光照阴影与GI/Lightmap]]
- [[05_光照阴影与GI/Light Probe]]
- [[05_光照阴影与GI/动态GI]]

## 参考资料

- [Unity 6000.0：Troubleshooting reflections，Box projection](https://docs.unity3d.com/6000.0/Documentation/Manual/AdvancedRefProbe.html)，有限距离环境与探针盒范围。
