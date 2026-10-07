# GPU归约与前缀和

可见标记是一组零和一，间接绘制却要一个紧凑列表。归约计算总数，前缀和给每个保留元素分配不冲突的输出位置。两者共享分阶段协作模型，但输出语义不同，不能拿原子计数的无序结果当稳定顺序。

## 输出语义

### Reduction

把一组值求和、最小值或最大值。通常先在 Group Shared 中做树形归约，再写一个 Group 结果，继续下一阶段。

### Prefix Sum

计算每个元素之前的累计值。GPU Culling 中可以用它把“可见/不可见”标记转换成紧凑输出索引。

## 归约的标准范式

归约（多个输入求出一个值）与逐像素处理（一对一）是两类完全不同的问题。GPU 上的标准解法是“组内树形折半 + 多次 Dispatch 收尾”：

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

输入非负整数flag，输出第i项之前的总和。这里给CPU参考伪代码，GPU分块实现先做组内scan，再扫描组和并回加块偏移。

```text
running = 0
for i in 0..count-1:
    offset[i] = running
    running += flag[i]
for i in 0..count-1:
    if flag[i] != 0: compacted[offset[i]] = input[i]
```

边缘线程以求和零、最小值正无穷或最大值负无穷参与，仍要到达组内barrier。全局结果在前一阶段完成后消费。

## 验证方法

空数组、全零、全一与不能整除组大小的输入分别比较总数和偏移。输出偏移应唯一且稳定，组和回加后不能遗漏块边界。整数累计还要检查溢出与输出容量。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

本机CPU验证：排他前缀和与压紧由 [completion_reference.py](../examples/mechanisms/completion_reference.py) 检查，运行 `python 知识库/examples/mechanisms/completion_reference.py`。这些检查验证模型，不包含GPU执行或实际网络故障注入。

## 相关主题

- [[03_Shader编程/Compute Shader]]
- [[26_GPU驱动与虚拟几何/GPU-Driven Rendering]]
- [[03_Shader编程/GPU异步回读]]

## 参考资料

- Microsoft Learn, *Compute Shader Overview* and *HLSL Shader Model 6 Wave Intrinsics*.
- Khronos, *Vulkan Specification*, Compute Pipelines and Memory Model.
- NVIDIA and AMD GPU architecture/performance guides.
- LearnOpenGL, `src/8.guest/2022/5.computeshader_helloworld`.
