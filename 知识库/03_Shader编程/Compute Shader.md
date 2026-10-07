# Compute Shader

逐像素复制可以让每个线程写自己的位置，但共享结果需要明确同步范围。Compute Shader用Dispatch与线程组组织工作，我们先界定每个索引读写哪份数据，再让组内共享和API依赖分别处理不同层次的协作。

## 线程怎样定位与协作

### Dispatch 和线程索引

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

#### 最小 Dispatch

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

### Thread Group

同一 Group 的线程可以：

- 使用 `groupshared` 内存；
- 执行 Group Barrier；
- 合作加载 Tile、做 Reduction 或 Prefix Sum。

不同 Group 的执行顺序没有保证。普通 Dispatch 内不能用 Group Barrier 同步整个 Dispatch。需要全局阶段同步时，应拆成多个 Dispatch，并在 API/Render Graph 中建立资源依赖。

### Wave 和 Warp

GPU 会把线程分成硬件执行批次。NVIDIA 常称 Warp，DirectX 常称 Wave，AMD 文档也使用 Wavefront。

Wave 宽度可能是 32、64 或其他值，不能在跨平台 Shader 中写死，除非目标和 Feature 明确保证。

同一 Wave 通常按 SIMT 方式执行相同指令。遇到不同分支时，硬件可能分别执行各路径，再用 Mask 关闭不参与的 Lane。这就是 Branch Divergence。

### 分支什么时候危险

按像素随机变化的条件容易让同一 Wave 发散。按整个 Dispatch、材质或大块 Tile 一致的条件可能不会严重发散。

分支代价还取决于：

- 两侧工作量；
- 编译器是否展开或改写；
- 是否能提前退出大量昂贵循环；
- 发散持续多少条指令；
- 分支后的内存访问是否仍连续。

## 资源怎样读写与同步

### `groupshared` 内存

Group Shared Memory 位于 Compute Unit/SM 附近，延迟低、带宽高，适合复用一个 Tile 数据。

典型模式：

1. 每个线程从全局资源加载一个元素；
2. 写入 `groupshared`；
3. 执行 Group Barrier；
4. 多个线程重复读取共享数据完成卷积或归约。

共享内存容量有限。每个 Group 用得越多，可同时驻留的 Group 可能越少。

### Barrier

Barrier 要区分两件事：

- 等待同组线程到达；
- 保证某类内存写入对其他线程可见。

不是所有 Barrier 都同时完成两者。应使用语言/API 中与目标内存范围匹配的语义。

如果只有部分线程进入 Barrier，其他线程走了不同分支，可能死锁或产生未定义结果。Barrier 应位于 Group 内一致控制流中。

### UAV 和原子操作

UAV/Storage Resource 支持无序读写。多个线程写同一地址会产生 Race Condition。

解决方法包括：

- 让每个线程写唯一位置；
- 使用原子操作；
- 先在 Group 内归约，再少量写回；
- 使用前缀和分配唯一索引；
- 拆分为多个阶段。

原子操作保证更新不丢失，但大量线程竞争同一地址会串行化。

### 资源类型与计数器

常见 Compute 资源包括：

- `Texture2D`、`StructuredBuffer<T>`：只读资源；
- `RWTexture2D<T>`、`RWStructuredBuffer<T>`：随机读写资源；
- `ByteAddressBuffer`、`RWByteAddressBuffer`：按字节寻址，适合自定义布局；
- `AppendStructuredBuffer<T>`、`ConsumeStructuredBuffer<T>`：带隐藏计数器的追加与消费队列。

RW Texture 通常使用整数坐标直接读写。普通采样器提供过滤、寻址和 LOD，RW 访问表达的是精确元素地址，两者的访问语义不同。

Append/Consume Buffer 的计数器属于资源状态，不会因新一帧自动归零。CPU 或前置 Pass 必须显式设置计数器初值。后续 Indirect Draw 可以通过 `CopyCount` 或 API 对应操作把计数复制到 Argument Buffer，避免把数量同步回 CPU。

结构化 Buffer 的 CPU 结构和 Shader 结构必须具有相同步长、对齐和字段顺序。`bool`、混合精度和编译器 Padding 容易造成跨边界布局错误，交换结构优先使用固定宽度标量并显式核对 Stride。

### 内存访问和合并

相邻 Lane 访问连续地址时，硬件更容易合并内存事务并利用 Cache。随机跳跃访问会浪费带宽。

数据布局需要结合访问方式：

- AoS 适合一次读取一个对象的全部属性；
- SoA 适合大量线程只读取同一属性；
- 对齐和步长会影响事务数量；
- 纹理缓存适合具有空间局部性的采样。

### CPU、GPU 与资源生命周期

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

## 编译与执行的代价

### Occupancy

GPU 通过同时驻留多个 Wave 隐藏访存延迟。Occupancy 受以下资源限制：

- 每线程寄存器；
- 每 Group 共享内存；
- Group 线程数；
- 硬件最大 Wave/Group 数。

Occupancy 高不等于一定快。算法可能受带宽、指令吞吐或同步限制。它只是分析维度之一。

寄存器压力过高时，编译器可能把线程私有临时数据 Spill 到 Local Memory。这里的 Local 通常仍位于显存层级，不是低延迟的 `groupshared`。Spill 会增加访存并降低可驻留 Wave 数，应通过编译统计、ISA 和性能计数器确认。

Wave Intrinsic 可以直接做 Lane 间求和、投票、广播和前缀操作，省去部分共享内存与 Barrier。它的作用范围是当前 Wave，不能假设整个 Group 只有一个 Wave；跨平台代码还要检查 Shader Model、Subgroup 支持和 Wave Size 约束。

### 平台编译与执行边界

寄存器活跃区间与分支执行都可能限制吞吐，影响程度按设备与工作负载比较。

#### 寄存器是静态分配的

编译器根据活跃区间、分支和目标寄存器规则分配空间。未执行分支仍可能影响分配，但不能把源码中最大局部变量数直接当成寄存器数；检查编译产物、Spill与GPU时间。

静态变体可以让编译器移除未使用路径，可能减少寄存器和指令需求。运行时分支仍可能影响寄存器分配，但具体结果取决于活跃区间和编译器优化。应比较编译产物、寄存器占用和 GPU 时间，再决定哪些功能需要静态切分。

#### 分支本身有代价

轻量分支可能被编译器转成选择指令，重量分支则可能通过跳过昂贵路径降低成本。结果由目标编译器、指令和执行条件决定，不能只按设备新旧给出统一结论。

这正是 `UNITY_FLATTEN` 一类提示的用途。判断依据是两侧工作量：轻量分支倾向压平，重量分支仍应保留跳转以跳过昂贵计算。

### 一份源码编译多个 Kernel

同一套逻辑常需要多个变体：首级与后续级采样来源不同、输出到 Buffer 还是 Texture、是否启用某项功能。编译期Kernel变体可以移除不需要的路径，运行时分支则减少变体管理。比较编译产物与执行成本后选择，不能仅凭代码形式判断。

输出目标保留两条路径有实际意义：不同移动 GPU 上 Buffer 与 Texture 的回读性能差异很大，保留开关便于按机型选择。

### 运行时与编辑器工具的差异

同样是 Compute Shader，两种场景的工程要求差别很大：

| | 运行时管线 | 编辑器工具 |
|---|---|---|
| 调度 | Render Graph Pass 内记录命令 | 直接调用 Dispatch |
| 资源 | 由 Render Graph 托管生命周期 | 手动创建并显式释放 |
| 取结果 | 按延迟预算异步回读 | 交互长任务异步，离线批处理可明确等待 |
| 优化重点 | 帧预算、正确性与设备成本 | 交互响应、吞吐、峰值与可恢复性 |

编辑器工具中手动创建的 Buffer 必须显式释放，遗漏会造成显存泄漏，且在编辑器长时间运行下不断累积。

编辑器工具还有一个验证优势：可以同时保留一份逻辑相同的 CPU 实现，直接比对两者结果。这是验证 Compute 逻辑正确性最可靠的方式，值得在开发期保留。

## 验证方法

使用不能整除线程组的尺寸核对边界，用小输入比较CPU参考。共享内存barrier必须由组内一致路径到达；跨组阶段由额外Dispatch和API依赖协调。记录实际资源stride与编译后寄存器，不由源码变量数推测。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

编译记录：[compile_completion.py](../examples/mechanisms/compile_completion.py)从正文片段补最小入口，以DXC编译CopyKernel通过。编译检查不包含完整引擎或GPU输出。

## 相关主题

- [[02_GPU与光栅化管线/GPU执行与访存]]
- [[13_渲染架构/GPU同步与屏障]]
- [[03_Shader编程/GPU归约与前缀和]]
- [[03_Shader编程/GPU异步回读]]

## 参考资料

- Microsoft Learn, *Compute Shader Overview* and *HLSL Shader Model 6 Wave Intrinsics*.
- Khronos, *Vulkan Specification*, Compute Pipelines and Memory Model.
- NVIDIA and AMD GPU architecture/performance guides.
- LearnOpenGL, `src/8.guest/2022/5.computeshader_helloworld`.
