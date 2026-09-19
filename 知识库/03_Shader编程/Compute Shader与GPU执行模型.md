# Compute Shader 与 GPU 执行模型

Compute Shader 让程序直接提交并行计算，不需要顶点、三角形和光栅化。它适合大量结构相似、能够并行拆分的任务。

## Dispatch 和线程索引

HLSL 用 `[numthreads(x,y,z)]` 声明每个 Thread Group 的线程数。CPU 调用 `Dispatch(gx,gy,gz)` 提交 Group 数量。

总线程数是：

$$
(gx\cdot x,\ gy\cdot y,\ gz\cdot z)
$$

常见系统值：

- Group ID：当前 Group 在 Dispatch 网格中的位置；
- Group Thread ID：线程在 Group 内的位置；
- Dispatch Thread ID：整个 Dispatch 中的全局位置；
- Group Index：把 Group 内三维索引压成一维。

计算纹理时通常要做边界判断，因为 Dispatch 尺寸经常向上取整到 Group 大小。

CPU 侧的 Group 数通常按上取整计算：

$$
groupCount=\left\lceil\frac{elementCount}{threadCountPerGroup}\right\rceil
$$

`numthreads` 决定编译后 Kernel 的组内线程布局，运行时不能直接修改。不同 Kernel 可以使用不同 Group Size。选择 64、128、256 或二维 `8x8` 只是候选起点，需要结合目标 GPU 的 Wave 宽度、寄存器、共享内存和访问模式实测。

### 最小 Dispatch

下面的 Kernel 一一对应输入和输出像素。CPU 对尺寸向上取整，因此 Shader 必须处理边缘线程：

```hlsl
Texture2D<float4> InputTexture : register(t0);
RWTexture2D<float4> OutputTexture : register(u0);

cbuffer DispatchParams : register(b0)
{
    uint2 OutputSize;
    uint2 _Padding;
};

[numthreads(8, 8, 1)]
void CopyKernel(uint3 id : SV_DispatchThreadID)
{
    if (any(id.xy >= OutputSize))
        return;

    OutputTexture[id.xy] = InputTexture.Load(int3(id.xy, 0));
}
```

```cpp
uint groupsX = (width + 7) / 8;
uint groupsY = (height + 7) / 8;
commandList.Dispatch(groupsX, groupsY, 1);
```

输入和输出使用不同资源，避免同一次 Dispatch 中相邻线程读到正在被改写的数据。若算法需要原地更新，必须证明每个线程只依赖自己的旧值，或拆分阶段并建立 Barrier。

## Thread Group

同一 Group 的线程可以：

- 使用 `groupshared` 内存；
- 执行 Group Barrier；
- 合作加载 Tile、做 Reduction 或 Prefix Sum。

不同 Group 的执行顺序没有保证。普通 Dispatch 内不能用 Group Barrier 同步整个 Dispatch。需要全局阶段同步时，应拆成多个 Dispatch，并在 API/Render Graph 中建立资源依赖。

## Wave 和 Warp

GPU 会把线程分成硬件执行批次。NVIDIA 常称 Warp，DirectX 常称 Wave，AMD 文档也使用 Wavefront。

Wave 宽度可能是 32、64 或其他值，不能在跨平台 Shader 中写死，除非目标和 Feature 明确保证。

同一 Wave 通常按 SIMT 方式执行相同指令。遇到不同分支时，硬件可能分别执行各路径，再用 Mask 关闭不参与的 Lane。这就是 Branch Divergence。

## 分支什么时候危险

按像素随机变化的条件容易让同一 Wave 发散。按整个 Dispatch、材质或大块 Tile 一致的条件可能不会严重发散。

分支代价还取决于：

- 两侧工作量；
- 编译器是否展开或改写；
- 是否能提前退出大量昂贵循环；
- 发散持续多少条指令；
- 分支后的内存访问是否仍连续。

## `groupshared` 内存

Group Shared Memory 位于 Compute Unit/SM 附近，延迟低、带宽高，适合复用一个 Tile 数据。

典型模式：

1. 每个线程从全局资源加载一个元素；
2. 写入 `groupshared`；
3. 执行 Group Barrier；
4. 多个线程重复读取共享数据完成卷积或归约。

共享内存容量有限。每个 Group 用得越多，可同时驻留的 Group 可能越少。

## Barrier

Barrier 要区分两件事：

- 等待同组线程到达；
- 保证某类内存写入对其他线程可见。

不是所有 Barrier 都同时完成两者。应使用语言/API 中与目标内存范围匹配的语义。

如果只有部分线程进入 Barrier，其他线程走了不同分支，可能死锁或产生未定义结果。Barrier 应位于 Group 内一致控制流中。

## UAV 和原子操作

UAV/Storage Resource 支持无序读写。多个线程写同一地址会产生 Race Condition。

解决方法包括：

- 让每个线程写唯一位置；
- 使用原子操作；
- 先在 Group 内归约，再少量写回；
- 使用前缀和分配唯一索引；
- 拆分为多个阶段。

原子操作保证更新不丢失，但大量线程竞争同一地址会串行化。

## 资源类型与计数器

常见 Compute 资源包括：

- `Texture2D`、`StructuredBuffer<T>`：只读资源；
- `RWTexture2D<T>`、`RWStructuredBuffer<T>`：随机读写资源；
- `ByteAddressBuffer`、`RWByteAddressBuffer`：按字节寻址，适合自定义布局；
- `AppendStructuredBuffer<T>`、`ConsumeStructuredBuffer<T>`：带隐藏计数器的追加与消费队列。

RW Texture 通常使用整数坐标直接读写。普通采样器提供过滤、寻址和 LOD，RW 访问表达的是精确元素地址，两者的访问语义不同。

Append/Consume Buffer 的计数器属于资源状态，不会因新一帧自动归零。CPU 或前置 Pass 必须显式设置计数器初值。后续 Indirect Draw 可以通过 `CopyCount` 或 API 对应操作把计数复制到 Argument Buffer，避免把数量同步回 CPU。

结构化 Buffer 的 CPU 结构和 Shader 结构必须具有相同步长、对齐和字段顺序。`bool`、混合精度和编译器 Padding 容易造成跨边界布局错误，交换结构优先使用固定宽度标量并显式核对 Stride。

## 内存访问和合并

相邻 Lane 访问连续地址时，硬件更容易合并内存事务并利用 Cache。随机跳跃访问会浪费带宽。

数据布局需要结合访问方式：

- AoS 适合一次读取一个对象的全部属性；
- SoA 适合大量线程只读取同一属性；
- 对齐和步长会影响事务数量；
- 纹理缓存适合具有空间局部性的采样。

## CPU、GPU 与资源生命周期

完整调用链通常是：

1. CPU 创建 Buffer/Texture，并确定容量、格式和访问标志；
2. 绑定 Kernel、常量和 SRV/UAV；
3. 记录 Dispatch；
4. 建立后续 Pass 所需的资源状态与 Barrier；
5. GPU 执行；
6. 结果留在 GPU 继续消费，或按需要异步回读；
7. Fence 确认 GPU 不再使用后才能复用或释放资源。

同一资源先被 UAV 写入、再作为 SRV、Indirect Argument 或 Copy Source 使用时，需要匹配 API 的状态转换和内存可见性。Shader 内的 Group Barrier 只能协调一个 Group，不能替代 Dispatch 之间的 API Barrier。

同步 Readback 会让 CPU 等待 GPU 完成前面的工作，容易形成流水线停顿。`AsyncGPUReadback` 或 Staging Buffer 把结果延迟到后续帧取得，避免当前帧硬等待，但调用方必须接受延迟、处理请求失败，并保证源资源在复制完成前有效。

## Occupancy

GPU 通过同时驻留多个 Wave 隐藏访存延迟。Occupancy 受以下资源限制：

- 每线程寄存器；
- 每 Group 共享内存；
- Group 线程数；
- 硬件最大 Wave/Group 数。

Occupancy 高不等于一定快。算法可能受带宽、指令吞吐或同步限制。它只是分析维度之一。

寄存器压力过高时，编译器可能把线程私有临时数据 Spill 到 Local Memory。这里的 Local 通常仍位于显存层级，不是低延迟的 `groupshared`。Spill 会增加访存并降低可驻留 Wave 数，应通过编译统计、ISA 和性能计数器确认。

Wave Intrinsic 可以直接做 Lane 间求和、投票、广播和前缀操作，省去部分共享内存与 Barrier。它的作用范围是当前 Wave，不能假设整个 Group 只有一个 Wave；跨平台代码还要检查 Shader Model、Subgroup 支持和 Wave Size 约束。

## 常见算法

### Reduction

把一组值求和、最小值或最大值。通常先在 Group Shared 中做树形归约，再写一个 Group 结果，继续下一阶段。

### Prefix Sum

计算每个元素之前的累计值。GPU Culling 中可以用它把“可见/不可见”标记转换成紧凑输出索引。

### Tiled Processing

把图像分成 Tile，在 Shared Memory 缓存包含边界的区域，再执行模糊、边缘检测或光源筛选。

### Indirect Argument Generation

Compute Shader 统计可见对象并写 Indirect Draw 参数，让后续绘制不回读 CPU。

## 归约的标准范式

归约（多个输入求出一个值）与逐像素处理（一对一）是两类完全不同的问题。GPU 上的标准解法是"组内树形折半 + 多次 Dispatch 收尾"：

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
- **Barrier 只在组内有效**。跨组无法同步，因此单次 Dispatch 只能把数据归约到"每组一个值"；
- **收尾靠多次 Dispatch**。第一次把每个 Tile 归约成一个值，之后反复对上一轮结果归约，直到剩下一个。CPU 侧循环 Dispatch 直到计数为 1。
 
这个范式是许多算法的基础，下面的层级深度金字塔就是它的变体。

## 一次 Dispatch 生成多级结果

构建深度金字塔（每级取若干子像素的最远深度）的朴素做法是每级一次 Dispatch，十级就是十次。

利用共享内存可以在一次 Dispatch 内完成多级。思路是每轮让活跃线程数降到四分之一，用位掩码筛选哪些线程继续工作：

```hlsl
gs_Depth[localIndex] = mipDepth;
GroupMemoryBarrierWithGroupSync();

// 0x9 = 二进制 001001，筛出 x、y 均为偶数的线程
if ((localIndex & 0x9) == 0)
{
    // 合并右、下、右下三个邻居
    mipDepth = MaxDepth(float4(mipDepth,
                               gs_Depth[localIndex + 0x01],
                               gs_Depth[localIndex + 0x08],
                               gs_Depth[localIndex + 0x09]));
    _OutMip1[dispatchId.xy >> 1] = mipDepth;
    gs_Depth[localIndex] = mipDepth;
}
// 下一轮用 0x1B，再下一轮判断 localIndex == 0
```

8×8 的组每轮活跃线程 64 → 16 → 4 → 1，一次 Dispatch 产出四级。十级金字塔因此只需三次 Dispatch。

两个实现细节：

**反向 Z 的方向**。金字塔要保存"最远"深度，但反向 Z 下最远对应数值最小，比较函数必须跟着翻转。这类符号错误不会报错，表现为遮挡剔除把该显示的物体剔掉。

**未使用的 UAV 槽位**。着色器声明了固定数量的输出资源，某些平台上不绑定会直接报错。不用的槽位需要绑定占位资源，靠标志位屏蔽实际写入。

## 位掩码表达集合

当集合元素数量不超过 32 时，一个 `uint` 就能表达任意子集，交集是一条与指令，遍历用 `firstbitlow` 逐位取出。

这在光照剔除中很典型：把屏幕切成 Tile、视锥深度切成 Bin，分别预计算各自影响的灯光集合，着色时两个掩码求交即可：

```hlsl
uint tileLightMask = 0u;
for (uint j = 0; j < lightCount; ++j)
{
    if (RaySphereOrConeIntersection(tileFrustum, lights[j]))
        tileLightMask |= (1u << j);
}
_XYLightMaskMap[globalId.xy] = uint4(tileLightMask, 0, 0, 0);
```

一个 Tile 的灯光列表被压成四字节。超过 32 盏灯时用多个 `uint` 扩展，求交仍是几条指令。

这类 Kernel 常有共享计算的机会：$4\times4$ 个 Tile 需要 $5\times5$ 个角点，多出的角点可以由空闲线程顺带算出并存入共享内存，避免相邻 Tile 重复计算同一角点。

## 移动端的两条硬约束

这两条认知在移动 GPU 上的影响远大于桌面端。

### 寄存器是静态分配的

编译器按整个 Kernel 的最大寄存器需求分配，**写了但运行时没走到的分支照样占用寄存器**。占用过多会 Spill 到显存，性能出现断崖。

因此可选功能必须用 `#ifdef` 在编译期彻底切掉，不能依赖运行时分支。即使条件在整个 Dispatch 内一致、即使分支从不进入，只要代码存在，寄存器就被占着。

对应的做法是把功能开关做成 Shader Keyword，由 CPU 侧按质量档位设置。收益是双份的：既省下寄存器，也省下该功能的 UAV 声明、常量读取与写入带宽。

### 分支本身有代价

老的移动 GPU 上，跳转指令即使在条件一致时也会造成流水线停顿。对于两侧都很轻量的分支，两边都算再选择反而更快——多出的几条按位或与选择指令，代价低于一次跳转。

这正是 `UNITY_FLATTEN` 一类提示的用途。判断依据是两侧工作量：轻量分支倾向压平，重量分支仍应保留跳转以跳过昂贵计算。

## 异步回读与延迟数据

结果需要回到 CPU 时（例如 CPU 侧执行剔除），同步回读会让 CPU 硬等 GPU，形成流水线停顿。异步回读避免了等待，但结果要几帧之后才能取到。

工程做法是维护一个环形队列：本帧使用最新已完成的回读结果，同时提交本帧的新请求。队列长度取决于可容忍的延迟。

用旧数据必然不准，因此需要有效性判断。以遮挡剔除为例：

```csharp
var isTooFarAway   = Vector3.Distance(currentCameraPos, recordCameraPos) >= 20.0f;
var isDifferentDir = Vector3.Dot(currentCameraForward, recordCameraForward) <= 0.0f;
var isStale        = Mathf.Abs(Time.frameCount - recordFrameIndex) > k_MaxInflight;

if (isTooFarAway || isDifferentDir || isStale)
    SkipCullingThisFrame();   // 宁可多画，不能画漏
```

失效策略的方向必须是保守的：剔除失效时宁可多提交绘制，也不能漏画——多画只是掉帧，漏画是可见的画面错误。

## 一份源码编译多个 Kernel

同一套逻辑常需要多个变体：首级与后续级采样来源不同、输出到 Buffer 还是 Texture、是否启用某项功能。用宏定义在编译期生成多个 Kernel，比运行时分支更合适（原因见前述寄存器约束）。

输出目标保留两条路径有实际意义：不同移动 GPU 上 Buffer 与 Texture 的回读性能差异很大，保留开关便于按机型选择。

## 运行时与编辑器工具的差异

同样是 Compute Shader，两种场景的工程要求差别很大：

| | 运行时管线 | 编辑器工具 |
|---|---|---|
| 调度 | Render Graph Pass 内记录命令 | 直接调用 Dispatch |
| 资源 | 由 Render Graph 托管生命周期 | 手动创建并显式释放 |
| 取结果 | 异步回读，多帧队列 | 同步阻塞，卡一下无妨 |
| 优化重点 | 寄存器、带宽、Keyword 裁剪 | 只要比 CPU 版快即可 |

编辑器工具中手动创建的 Buffer 必须显式释放，遗漏会造成显存泄漏，且在编辑器长时间运行下不断累积。

编辑器工具还有一个验证优势：可以同时保留一份逻辑相同的 CPU 实现，直接比对两者结果。这是验证 Compute 逻辑正确性最可靠的方式，值得在开发期保留。
## 调试与验证

- 检查 Dispatch 尺寸和边界条件。
- 用小输入在 CPU 上写参考实现，比对 GPU 结果。
- 使用 GPU Debugger 检查资源状态、UAV 和 Barrier。
- 测试不同 Group Size，不凭 8x8 或 16x16 的惯例决定。
- 查看寄存器、共享内存、Occupancy 和带宽指标。
- 对原子竞争和非确定顺序做压力测试。
- 检查 Append Counter 是否在正确时机初始化，Indirect Args 是否来自当前帧结果。
- 检查 CPU 结构体大小、Buffer Stride 与 Shader 字段偏移。
- 分别测同步回读、异步回读和全 GPU 消费路径的等待时间。

## 相关主题

- [[02_GPU与光栅化管线/一帧如何到达屏幕]]
- [[10_VFX与模拟/粒子系统与GPU模拟]]
- [[12_光追与现代渲染/GPU-Driven管线与Nanite]]
- [[14_性能分析与优化/帧时间、瓶颈与GPU成本]]
- [[10_VFX与模拟/大气散射、天空与体积云]]

## 参考资料

- Microsoft Learn, *Compute Shader Overview* and *HLSL Shader Model 6 Wave Intrinsics*.
- Khronos, *Vulkan Specification*, Compute Pipelines and Memory Model.
- NVIDIA and AMD GPU architecture/performance guides.
- LearnOpenGL, `src/8.guest/2022/5.computeshader_helloworld`.
