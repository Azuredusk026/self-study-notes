# GPU归约与前缀和

可见标记是一组零和一，间接绘制却要一个紧凑列表。归约计算总数，前缀和给每个保留元素分配不冲突的输出位置。两者共享分阶段协作模型，但输出语义不同，不能拿原子计数的无序结果当稳定顺序。

## 输出语义

### Reduction

把一组值求和、最小值或最大值。通常先在 Group Shared 中做树形归约，再写一个 Group 结果，继续下一阶段。

### Prefix Sum

计算每个元素之前的累计值。GPU Culling 中可以用它把“可见/不可见”标记转换成紧凑输出索引。

## 归约的标准范式

归约（多个输入求出一个值）与逐像素处理（一对一）是两类完全不同的问题。一种常用GPU方案是“组内树形折半 + 多次 Dispatch 收尾”：

```hlsl
groupshared float s_Min[64];
groupshared float s_Max[64];

// 阶段一：每线程读一个元素写入共享内存
s_Min[idx] = value;  s_Max[idx] = value;
GroupMemoryBarrierWithGroupSync();

// 阶段二：树形折半，log2(64) = 6 轮
for (int offset = 32; offset > 0; offset /= 2)
{
    if (idx < offset)
    {
        s_Min[idx] = min(s_Min[idx], s_Min[idx + offset]);
        s_Max[idx] = max(s_Max[idx], s_Max[idx + offset]);
    }
    GroupMemoryBarrierWithGroupSync();   // 每轮之后都必须同步
}

if (idx == 0) _TileResults[groupIndex] = float2(s_Min[0], s_Max[0]);
```

三个容易出错的地方：

- **每轮都要同步**。少一个 Barrier 就是竞态，表现为结果随机波动且难以复现；
- **Barrier 只在组内有效**。跨组无法同步，因此单次 Dispatch 只能把数据归约到“每组一个值”；
- **收尾靠多次 Dispatch**。第一次把每个 Tile 归约成一个值，之后反复对上一轮结果归约，直到剩下一个。CPU 侧循环 Dispatch 直到计数为 1。

层级深度生成也可以复用组内归约，具体多级写入见 [[02_GPU与光栅化管线/基于深度的可见性优化]]。

## 排他前缀和

输入0或1的flag，输出第i项之前的总和。一般非负计数也能扫描，但每个输入需写出对应数量的元素，不能套用只写一项的压紧循环。这里给CPU参考伪代码，GPU分块实现先做组内scan，再扫描组和并回加块偏移。

```text
running = 0
for i in 0..count-1:
    offset[i] = running
    running += flag[i]
for i in 0..count-1:
    if flag[i] != 0: compacted[offset[i]] = input[i]
```

边缘线程以求和零、最小值正无穷或最大值负无穷参与，仍要到达组内barrier。全局结果在前一阶段完成后消费。

### 组内上扫与下扫

排他扫描需要每个叶子之前的总量。先向上累加得到各子树的和，再从根传递“本子树之前已有多少”。左子树继承父节点偏移，右子树再加左子树的和。以四项 $[1,0,1,1]$ 为例，上扫根为3；根偏移置0后，下扫得到 $[0,1,1,2]$。

下面HLSL提供64项一组的完整计算入口。输入和局部输出按uint存储，Count与缓冲容量由宿主设置；和必须能装入32位无符号整数。组尾越界线程装入0并参与全部屏障。

```hlsl
StructuredBuffer<uint> ScanInput : register(t0);
RWStructuredBuffer<uint> LocalOffsets : register(u0);
RWStructuredBuffer<uint> GroupTotals : register(u1);
cbuffer ScanParams : register(b0) { uint Count; uint3 ScanPadding; };
groupshared uint scratch[64];

[numthreads(64, 1, 1)]
void ScanGroups(uint3 group : SV_GroupID, uint lane : SV_GroupIndex)
{
    uint index = group.x * 64 + lane;
    scratch[lane] = index < Count ? ScanInput[index] : 0;
    GroupMemoryBarrierWithGroupSync();
    for (uint step = 1; step < 64; step *= 2) {
        uint right = (lane + 1) * 2 * step - 1;
        if (right < 64) scratch[right] += scratch[right - step];
        GroupMemoryBarrierWithGroupSync();
    }
    if (lane == 0) {
        GroupTotals[group.x] = scratch[63];
        scratch[63] = 0;
    }
    GroupMemoryBarrierWithGroupSync();
    for (uint step = 32; step > 0; step /= 2) {
        uint right = (lane + 1) * 2 * step - 1;
        if (right < 64) {
            uint leftSum = scratch[right - step];
            scratch[right - step] = scratch[right];
            scratch[right] += leftSum;
        }
        GroupMemoryBarrierWithGroupSync();
    }
    if (index < Count) LocalOffsets[index] = scratch[lane];
}
```

宿主按 `ceil(Count/64)` 调度，Count为0时直接返回空结果。组和数组再做排他扫描，获得每组基址；回加通道计算 `GlobalOffset[i]=LocalOffsets[i]+GroupBase[i/64]`。组和超过64项时继续递归分块，再从上层向下回加。每次生产到消费之间建立API资源依赖，组内屏障无法替代它。

算法每层的目标索引互不重叠，上扫与下扫共进行线性数量的加法。此实现用于说明正确的索引与同步，未加入wave优化或共享内存bank布局优化。并行浮点求和还会因运算顺序改变误差；整数检查通过不代表浮点结果逐位一致。

## 验证方法

空数组、全零、全一与不能整除组大小的输入分别比较总数和偏移。保留元素的输出偏移应唯一且稳定，组和回加后不能遗漏块边界。整数累计还要检查溢出与输出容量。

实现状态：[shader_models.py](../examples/revision/shader_models.py)用分块上扫/下扫与独立顺序和对照，[test_shader.py](../examples/revision/test_shader.py)覆盖空数组、部分组、多个组及稳定压紧。ScanGroups通过本文提取的DXC探针检查，完整多Dispatch调度及GPU竞态尚未运行。

本机CPU验证：排他前缀和与压紧由 [completion_reference.py](../examples/mechanisms/completion_reference.py) 检查，运行 `python 知识库/examples/mechanisms/completion_reference.py`。这些检查验证CPU模型，不包含GPU执行。

## 相关主题

- [[03_Shader编程/Compute Shader]]
- [[26_GPU驱动与虚拟几何/GPU-Driven Rendering]]
- [[03_Shader编程/GPU异步回读]]

## 参考资料

- [Harris、Sengupta与Owens，GPU Gems 3第39章](https://developer.nvidia.com/gpugems/gpugems3/part-vi-gpu-computing/chapter-39-parallel-prefix-sum-scan-cuda)：2026-10-22核读§39.2.2上扫/下扫及§39.2.4分块回加；本文用独立HLSL实现，不沿用旧硬件性能结论。
- [Microsoft GroupMemoryBarrierWithGroupSync](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/groupmemorybarrierwithgroupsync)：组内一致到达约束。
- [compile_shader.py](../examples/revision/compile_shader.py)：正文计算入口编译与常量布局检查。
