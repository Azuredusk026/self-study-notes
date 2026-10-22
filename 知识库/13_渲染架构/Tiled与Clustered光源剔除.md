# Tiled与Clustered光源剔除

让每个像素遍历场景所有灯，很多计算只是排除根本照不到它的光源。Tiled和Clustered先把灯分配给屏幕区域或三维簇，材质只读取本区域的列表。列表必须保守且有容量规则，否则一次溢出或深度范围遗漏就会让灯光消失。

## Clustered Rendering

二维 Tile 无法区分同一屏幕区域内近处和远处的灯。Clustered Rendering 再沿深度划分，把视锥变成三维 Cluster。

### 二维 Tile 与 Z Bin 分离

Clustered 的一种实现方式是把 XY 与 Z 两个维度**分开预计算**，而非直接构建三维 Cluster 列表。

屏幕切成若干 Tile，深度范围切成若干 Bin，分别计算各自影响的灯光集合并存为位掩码。着色时取当前像素所在 Tile 的掩码与所在 Bin 的掩码求交：

$$
\text{lights} = \text{mask}_{XY} \;\&\; \text{mask}_{Z}
$$

若每个单元都使用相同长度的固定位掩码，这种分离将掩码个数从 $N_x \times N_y \times N_z$ 降到 $N_x \times N_y + N_z$。每份掩码占 $4\lceil L/32\rceil$ 字节，其中 L 是灯光总数；可变长度列表的内存则取决于实际候选数，不能直接套用这个比例。代价是求交结果偏保守——某盏灯可能同时命中某个 Tile 和某个 Bin，实际却不在两者的交叉区域内。

分离能减少掩码的存储与构建工作，同时增加着色阶段的假阳性灯光。收益取决于灯数、覆盖范围、深度分布和每盏灯的着色成本，需要分别计时构建与最终着色。

两个剔除 Kernel 的工作方式不同：XY 方向用 Tile 视锥的角点构造侧平面并测试灯体积，Z 方向用前后两个平面测试深度区间；只测试角射线会漏掉完全落在分块内部的小灯。相邻分块可共享角点。

优势：

- 深度跨度大的场景中灯列表更短；
- 透明物体可以根据自身深度选择 Cluster；
- 适合大量局部灯、Decal 和 Probe。

问题：

- Cluster 尺寸和深度切分需要调节；
- 灯列表需要前缀和、原子或固定上限；
- 超大灯会进入很多 Cluster；
- 列表溢出必须有明确行为。

### 灯光集合的位掩码实现

当集合元素数量不超过 32 时，一个 `uint` 就能表达任意子集，交集是一条与指令，遍历用 `firstbitlow` 逐位取出。

这在光照剔除中很典型：把屏幕切成 Tile、视锥深度切成 Bin，分别预计算各自影响的灯光集合，着色时两个掩码求交即可：

```hlsl
RWTexture2D<uint> _XYLightMaskMap; // 资源格式为 R32_UINT

// 下列主体位于每个 Tile 对应的计算着色器调用中。
uint tileLightMask = 0u;
for (uint j = 0; j < lightCount; ++j)
{
    if (ConservativeSphereFrustumTest(tileFrustum, lights[j]))
        tileLightMask |= (1u << j);
}
_XYLightMaskMap[globalId.xy] = tileLightMask;
```

一个 Tile 的灯光列表被压成四字节。超过 32 盏灯时用多个 `uint` 扩展，求交仍是几条指令。

这类 Kernel 常有共享计算的机会：$4\times4$ 个 Tile 需要 $5\times5$ 个角点，若工作组有 16 个线程，可让线程 i 依次处理索引 `i, i+16` 中小于 25 的角点，再执行工作组内存同步屏障。25 个角点全部就绪后，每个线程读取自己 Tile 的四角，避免相邻 Tile 重复计算。

## 簇索引与列表构建

透视相机可以用对数深度切片，输入是正的线性视空间距离和相机 near/far。均匀屏幕分块决定 XY，深度切片决定 Z，三者组成列表索引。

```hlsl
uint DepthSlice(float viewDistance)
{
    float safeDistance = clamp(viewDistance, nearPlane, farPlane);
    float fraction = log(safeDistance / nearPlane)
                   / log(farPlane / nearPlane);
    return min((uint)(fraction * sliceCount), sliceCount - 1);
}
uint ClusterIndex(uint2 pixel, float viewDistance)
{
    uint2 tile = min(pixel / tileSize, tileCount - 1);
    uint slice = DepthSlice(viewDistance);
    return (slice * tileCount.y + tile.y) * tileCount.x + tile.x;
}
```

前提是 `nearPlane > 0`、`farPlane > nearPlane`、分块和切片数量非零。构建端与读取端使用相同的索引规则。灯光与簇相交测试要保守，列表溢出要有显式回退。只有不透明深度范围的分块列表可能漏掉透明表面的灯，需要单独处理其范围。

例如三个簇的候选数为[2,0,3]，独占前缀和得到起点[0,2,2]，总索引数为5。第三簇写区间[2,5)，第二簇为空，不占位置。若第三簇计数后场景又新增灯，填充端写4项就越过预分配范围；计数和填充必须使用同一冻结光源快照，或重新分配。

两阶段列表构建可以先计数，再做前缀和分配区间，最后写灯索引。固定上限方案更简单，但灯光集中时容易溢出。算法选择应记录最大列表长度、构建时间和内存峰值。

球形点光源的保守测试可以逐平面执行。平面法线指向簇内部且已归一化，球心 c 的有符号距离为 `dot(n,c)+d`；任一平面的距离小于 `-radius` 就可拒绝，全部通过则保留候选。通过只表示未被平面排除，允许边角假阳性。聚光灯可以先用保守包围球，再做可选锥体测试。

位掩码代码要求 `lightCount <= 32`。扩展到多个字时，使用 `word=j/32`、`bit=j%32`，分别更新对应字；直接执行 `1u << j` 不能表示第 32 盏以后的灯。

## 验证方法

- 可视化每簇灯光数，对边界灯逐个检查。
- 测试近远平面和对数切片边界，排除漏灯。
- 记录列表构建、原子竞争、溢出回退和最终着色时间。


## 相关主题

- [[02_GPU与光栅化管线/渲染帧流程]]
- [[05_光照阴影与GI/直接光照]]
- [[13_渲染架构/GBuffer布局]]
- [[13_渲染架构/渲染命令的组织方式]]
- [[14_性能分析与优化/帧瓶颈诊断]]

- [[13_渲染架构/渲染路径与光源组织]]

示例状态：本页代码用于解释对应的数据和调用约束，完整资源创建、类型与调用环境由项目提供。除文中另列的实际实验外，本页未执行目标引擎编译、GPU捕获或性能计时。

## 参考资料

- [Olsson 等：Clustered Deferred and Forward Shading](https://diglib7.eg.org/items/6342d4d6-5220-4376-a5c6-a153058f4a3c/full)：论文元数据与摘要：按三维位置或法线分簇；本文规则网格和位掩码是限定场景下的实现。
- [AMD：ForwardPlus11](https://github.com/GPUOpen-LibrariesAndSDKs/ForwardPlus11/)：README：按屏幕块构造光源列表的官方样例入口。
