# 粒子系统与 GPU 模拟

粒子系统用大量生命周期短、行为相似的元素近似烟、火、碎片、轨迹和环境动态。系统真正困难的部分是生命周期管理、数据布局、并行更新、排序与跨系统交互。

## Particle、Emitter 与 System

Particle 保存单个元素的状态，例如：

- Position、Velocity、Age、Lifetime；
- Color、Size、Rotation；
- Random Seed、Custom Data；
- Mesh/Material/Frame Index。

Emitter 定义 Spawn Rate、Burst、初始分布和 Update 规则。System 组合多个 Emitter，并管理共享参数、事件、LOD 和整体 Bounds。

一个爆炸可能由火球、烟、火星、冲击波、碎片、光源和声音组成。它们应共享时间与 Gameplay 语义，但不一定使用同一种模拟或材质。

## 生命周期

最基本的流程是 Spawn → Initialize → Update → Render → Kill。每帧应确保 Age 超过 Lifetime 的粒子被回收。只生成不回收会让存活数量持续增长。

Spawn Rate 按每秒计数时，应累积不足一个粒子的余数：

$$
n=\lfloor r\Delta t+a\rfloor,\qquad a'=r\Delta t+a-n
$$

$r$ 是每秒发射率，$a$ 是上一帧余数。这样帧率变化时平均数量仍稳定。Burst 则在事件时一次生成指定数量。

Random 不应直接依赖线程执行顺序。使用粒子 Stable ID、Emitter Seed 和 Spawn Index 派生随机数，才能重放和调试。

## 基础积分

简单粒子常用 Semi-implicit Euler：

$$
\mathbf{v}_{t+\Delta t}=\mathbf{v}_t+\mathbf{a}_t\Delta t
$$

$$
\mathbf{x}_{t+\Delta t}=\mathbf{x}_t+\mathbf{v}_{t+\Delta t}\Delta t
$$

它足以表现重力、风、Drag 和简单吸引力。视觉特效优先稳定、可控，不要求严格守恒。

大 `Delta Time` 会导致高速粒子穿过碰撞体。可以限制最大步长、增加 Substep，或对高速轨迹使用 Sweep。

## CPU 粒子

CPU 适合：

- 需要精确 Gameplay 事件和物理查询；
- 数量较少但行为分支复杂；
- 需要网络同步或 CPU 读取结果；
- 平台不支持所需 Compute 能力。

数据应使用 Structure of Arrays 或紧凑 Chunk，避免每粒子独立对象和分配。更新任务可按 Emitter/Chunk 并行，但 Spawn、Kill 与 Event Queue 需要清楚的所有权。

CPU 模拟后仍要把实例数据上传 GPU。数量很大时，模拟和上传都会成为瓶颈。

## GPU Particle Pool

GPU 粒子通常预分配固定容量的 Structured Buffer，不在每帧动态创建对象。常见资源：

- Particle State Pool；
- Alive List；
- Dead List；
- Spawn Request；
- Sort Key/Index；
- Indirect Draw Arguments；
- Event Buffer。

Dead List 保存可复用 Slot。Spawn 从 Dead List 取索引并初始化；Update 遍历 Alive List，仍存活的写入下一帧 Alive List，死亡的归还 Dead List。

这相当于 GPU 上的对象池和 Stream Compaction。Append/Consume Buffer 或 Atomic Counter 可以管理数量，但原子竞争和无序写仍需控制。

## 一帧 GPU 模拟

典型调度：

1. 清零本帧 Counter；
2. Spawn Pass 消费请求和 Dead Slot；
3. Update Pass 推进位置、生命周期与属性；
4. Collision/Event Pass 产生事件；
5. Compact Alive List；
6. 可选 Cull、LOD 与 Sort；
7. 写 Indirect Argument；
8. Indirect Draw。

Pass 间 Buffer 从 UAV Write 变为 SRV/Indirect Read 时需要正确 Barrier。漏同步可能表现为随机丢粒子或读取上一帧数据。

## Bounds 与可见性

CPU 不知道 GPU 粒子的最终位置时，很难得到紧致 Bounds。固定巨大 Bounds 会让离屏系统无法剔除；过小则粒子突然消失。

方案包括：

- 作者设置保守 Fixed Bounds；
- GPU Reduction 计算 Bounds，异步回读给下一帧 CPU；
- 按空间 Tile 管理粒子；
- System 不可见时降低频率或停止 Spawn，但谨慎处理重新出现时的时间状态。

GPU 回读会引入延迟，不能为了实时 Bounds 强制同步。

## Billboard、Mesh 与 Ribbon

Billboard 用面片朝向摄像机。它顶点少，但透明区域可能很大。

Mesh Particle 适合碎片、石块和简单 Crowd。可通过 Instancing 绘制，并从粒子 Buffer 读取 Transform、颜色和动画帧。

Ribbon/Trail 按历史点生成带状网格。Catmull-Rom 等曲线可平滑轨迹，但过密采样会增加顶点，过稀会在急转弯处折断。还要处理宽度方向、UV 距离和相机朝向。

## 排序

标准 Alpha Blend 依赖 Back-to-front 顺序。Per-emitter 排序便宜，但两个 Emitter 互相穿插时错误；Global Sorting 更正确，却要统一收集粒子并减少状态切换。

GPU 可生成 View Depth Sort Key，再用 Radix Sort、Bitonic Sort 或并行 Merge。排序成本随粒子数量增长，且会额外读写 Buffer。

并非所有粒子都要严格排序：

- Additive/Modulate 对顺序不敏感；
- 烟雾可接受近似分桶；
- 小而快速的火星可以关闭排序；
- 关键透明层再使用精确排序。

## 碰撞

CPU Physics 对数十万粒子过贵。GPU 粒子常用：

- Scene Depth：便宜，但只能碰当前视图可见表面，屏幕后信息缺失；
- SDF/Distance Field：支持体积查询，但需要内存和更新；
- Heightfield：适合地面；
- 简化 Primitive/Analytic Collider；
- Hardware Ray Query：质量高但成本与平台支持需评估。

Depth Collision 要把粒子投影到 Screen UV，比较粒子 View Depth 与 Scene Depth，并用重建 Normal 反射或衰减速度。相机外和被前景遮挡的碰撞都不可靠。

## Niagara 与 VFX Graph 的架构理解

现代系统把逻辑拆为 System、Emitter、Particle 阶段和可复用 Module。Parameter/Data Interface 负责从 Gameplay、Scene Texture、Skeleton、SDF 或外部 Buffer 输入数据。

节点图最终仍要编译成 CPU Vector VM、GPU Shader 或对应执行代码。图可视化不会消除分支、Buffer、同步和 Shader Variant 成本。

可复用模块应定义清楚输入、输出、单位、空间和默认值。隐式读取全局参数的模块很难移植和调试。

## 事件与读回

GPU Event 可以在设备内驱动二级 Emitter，例如死亡火花生成小烟。若要通知 Gameplay，通常需要异步 Readback，结果会延迟若干帧。

关键命中、伤害和可交互碎片应由 Gameplay/CPU 决定，粒子只表现结果。不要让必须即时可靠的逻辑依赖 GPU 回读。

## 验证方法

- 显示 Spawn、Alive、Dead、Culled、Sorted 数量和容量峰值。
- 检查固定 Seed 下结果是否可复现。
- 用 RenderDoc 检查 Compute Dispatch、Counter、Barrier 和 Indirect Args。
- 分开记录 Simulation、Sort、Collision、Draw 和 Pixel 成本。
- 测试暂停、时间缩放、大帧间隔、Emitter 销毁和场景切换。
- 检查容量耗尽时是拒绝 Spawn、替换旧粒子还是降级，不能静默写越界。

### GPU 粒子更新

输入 Buffer 保存上一帧粒子，输出 Buffer 与存活计数器属于当前帧。每个线程处理一个槽位，存活粒子通过原子计数压紧写入：

```hlsl
[numthreads(64, 1, 1)]
void Simulate(uint id : SV_DispatchThreadID)
{
    if (id >= inputCount) return;
    Particle p = InputParticles[id];
    p.velocity += gravityWS * deltaTime;
    p.position += p.velocity * deltaTime;
    p.age += deltaTime;
    if (p.age < p.lifetime) {
        uint dst;
        InterlockedAdd(AliveCount[0], 1, dst);
        OutputParticles[dst] = p;
    }
}
```

Dispatch 前要把 `AliveCount` 清零，并确保上一轮写入已完成；模拟后再用计数生成 Indirect Draw 参数。原子追加在粒子很多时可能争用，分组前缀和能进一步优化。验证时读取少量计数器或在 GPU 调试器中检查：`AliveCount` 不得超过输出容量，死亡粒子不能残留到 Draw。

## 相关主题

- [[03_Shader编程/Compute Shader与GPU执行模型]]
- [[10_VFX与模拟/常用VFX材质、模拟与性能]]
- [[13_引擎架构与资源系统/Draw Call、Batching与GPU Instancing]]
- [[14_性能分析与优化/帧时间、瓶颈与GPU成本]]

## 参考资料

- Reeves, *Particle Systems: A Technique for Modeling a Class of Fuzzy Objects*.
- Unreal Engine Documentation, *Niagara Overview*.
- Unity Documentation, *Visual Effect Graph*.
- GPU Gems 3, *Chapter 23. High-Speed, Off-Screen Particles*.
