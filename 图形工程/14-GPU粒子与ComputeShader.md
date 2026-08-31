# GPU粒子系统与计算着色器实时模拟

## 一、 核心知识点与原理剖析

### 1. GPU粒子系统概述与性能优势
*   **计算重构**：传统的粒子系统（如 Unity 早期默认的 CPU 粒子系统）其位置、速度、生命周期等物理模拟均运行在 CPU 上，然后再将顶点数据逐帧上传到 GPU 进行渲染。GPU 粒子系统则将粒子所有的物理状态更新算法转移到 **Compute Shader（计算着色器）** 中执行，利用 GPU 的海量并发核心进行状态迭代。
*   **消除传输瓶颈**：在实时渲染中，极高比例的性能开销源自 CPU 内存（RAM）与 GPU 显存（DRAM/VRAM）之间的数据传输。GPU 粒子系统由于模拟和绘制均在 GPU 显存内部完成，数据无需每帧回传 CPU，也无需从 CPU 重复上传顶点，从而彻底免除了这一带宽瓶颈，使得实时渲染数十万甚至数百万个粒子成为可能。

### 2. Compute Shader 粒子模拟机制
*   **粒子的双重定义**：
    为了在保证物理模拟精确度的同时优化渲染效率，将粒子结构体划分为两个版本：
    *   **模拟粒子结构体（Simulation Struct）**：保存物理计算所涉及的全部参数。
        ```hlsl
        struct Particle {
            float3 position;  // 粒子在世界空间或局部空间的位置
            float3 velocity;  // 粒子的当前速度向量（米/秒）
            float4 color;     // 粒子的基础颜色
            float size;       // 粒子的基础大小尺寸
            float lifetime;   // 粒子的剩余存活寿命
        };
        ```
    *   **绘制粒子结构体（Draw Struct）**：仅保留顶点着色器渲染所需的最小数据集，以极大节省 GPU 的片上带宽。
        ```hlsl
        struct ParticleDraw {
            float3 position;  // 渲染位置
            float size;       // 渲染大小
            float4 color;     // 渲染颜色
        };
        ```
*   **结构化缓冲区（Structured Buffer）**：
    在显存中开辟连续的存储空间（类似于 GPU 数组），用于存放上述两种结构体。在 Compute Shader 中，以可读写的结构化缓冲区形式声明：
    ```hlsl
    RWStructuredBuffer<Particle> particles : register(u0);
    RWStructuredBuffer<ParticleDraw> particlesDraw : register(u1);
    ```
    *注：这些缓冲区的大小必须由 CPU 在运行初期预先分配（例如 `ComputeBuffer`），一旦创建其内存大小不可动态改变。*
*   **一维线程组分配与越界保护**：
    粒子模拟是扁平的线性任务，因此在 Compute Shader 中通常配置一维线程组，如 `[numthreads(64, 1, 1)]`。执行 Dispatch 时，线程分配数量必须能够覆盖粒子总数（如粒子总数为 64000，则分配 1000 个线程组）。
    在着色器入口中，必须通过全局线程 ID（`SV_DispatchThreadID.x`）与传入的粒子总数进行安全比对，实施越界防护：
    ```hlsl
    if (id >= particleCount) return;
    ```
*   **状态的帧间迭代与持久化**：
    *   **时间增量传递**：CPU 端逐帧将 `Time.deltaTime` 传入 Compute Shader 的全局变量 `DeltaTime`。
    *   **物理公式迭代**：
        *   生命周期扣减：`lifetime -= DeltaTime`
        *   速度更新：`velocity += acceleration * DeltaTime`（可通过乘以阻尼系数如 `0.9` 模拟空气阻力）
        *   位置更新：`position += velocity * DeltaTime`
    *   **重生检测（Emit）**：若判定 `lifetime <= 0`，则在当前线程的缓冲区位置上赋入随机初始值（如利用哈希噪声生成新的位置与颜色），模拟粒子消亡后原位生成新粒子，保证活跃粒子数相对恒定。
    *   **写回显存**：物理迭代修改后的状态必须显式写回对应的缓冲区位置（如 `particles[id] = p`），以确保下一帧能正确读取累加后的状态。

### 3. 程序化渲染与 `DrawProcedural`
*   **无网格绘制（Procedural Drawing）**：
    传统的物体绘制依赖于三维美术模型及复杂的网格结构（Mesh）。程序化渲染（Procedural Rendering）完全打破这一限制，通过调用 `Graphics.DrawProcedural` 可以在没有任何 Mesh 数据的情况下直接调用 Vertex/Fragment Shader 进行光栅化绘制。
*   **渲染流水线接口与 ID 语义**：
    在顶点着色器（Vertex Shader）中，利用以下两个关键的系统内置语义来定位当前执行的像素或面片：
    *   `SV_InstanceID`：当前渲染的实例索引（在粒子系统中对应特定粒子的索引，用于从 `particlesDraw` 缓冲区中获取对应的粒子属性）。
    *   `SV_VertexID`：当前执行的顶点索引（例如绘制点拓扑时始终为 0，绘制面片时为 0 到 5）。
*   **视锥体剔除（Frustum Culling）与 Bounds 手动设置**：
    在常规渲染中，Unity 根据模型的静态网格自动计算轴向包围盒（AABB Bounds），若该包围盒不在相机的视锥体内则不进行绘制。而在程序化渲染中，由于没有网格，Unity 无法得知粒子的运动范围。
    开发者必须手动计算并传入一个合理的估计包围盒 `Bounds`。如果相机没有看到这个 Bounds，CPU 就会在剔除阶段直接丢弃该绘制指令。
*   **C# 调用语法糖**：
    通过命名参数可以跳过有默认值的参数，直接传递最后的阴影设置：
    ```csharp
    Graphics.DrawProcedural(
        material,
        new Bounds(center, size),
        MeshTopology.Triangles,
        vertexCount,
        instanceCount,
        castShadows: UnityEngine.Rendering.ShadowCastingMode.Off
    );
    ```

### 4. GPU 并行计算与原子锁存操作（Atomic Operations）
*   **竞态条件（Race Conditions）与多线程写入冲突**：
    在 GPU 并行架构下，成百上千个线程同时运行。若多个线程同时读取并试图对同一个全局地址执行累加（如 `count++`），由于各个线程将数据载入片上寄存器的先后顺序不同，且存在缓存刷新延迟，多个线程算出的新值会互相覆盖，导致最终的计数值产生严重丢失。
*   **原子操作与锁存机制**：
    为了在多线程并发时保证计数的正确性，必须采用原子锁存指令（Interlocked）。原子操作在执行“读取-修改-写入”的完整周期中，会暂时阻塞其他线程对该地址的访问。
    在 HLSL 中，使用以下形式：
    ```hlsl
    InterlockedAdd(destination, value, original_value);
    ```
    *   `destination`：必须是可读写的全局内存空间（如 `RWStructuredBuffer` 的某个元素）。
    *   `value`：要加上的数值（如 `1`）。
    *   `original_value`：输出变量，用来存放加法执行**之前**的旧值。这个设计使得线程能安全地取得自身专享的数组写入索引。
*   **全局计数器的硬件开销与 CPU 归零**：
    由于 Compute Shader 的全局常量缓冲区（Constant Buffer）只读，写入计数必须创建额外的单元素结构化缓冲区 `RWStructuredBuffer<int>`。由于 GPU 不具有帧间自动归零机制，CPU 必须在每一帧 Dispatch 开始前，显式调用 `SetData` 方法向该缓冲区重新覆盖写入零值，从而完成计数器的帧间初始化。

### 5. Billboard（公告牌）渲染技术与施密特正交化相机对齐
*   **顶点几何体的手动组装**：
    要将无维度的点粒子渲染为贴图面片，必须利用 `MeshTopology.Triangles`，一个面片由 2 个三角形（共 6 个顶点）组成。顶点着色器通过 `SV_VertexID`（取值范围 0~5）判断自身在面片中的局部位置，并根据预设的偏移数组确定位置：
    *   三角形 1 顶点偏移：`(-0.5, 0.5)`、`(0.5, 0.5)`、`(-0.5, -0.5)`
    *   三角形 2 顶点偏移：`(0.5, 0.5)`、`(-0.5, -0.5)`、`(0.5, -0.5)`
*   **施密特正交化相机对齐算法（Schmidt Orthogonalization）**：
    为实现面片无论相机如何旋转都始终面向相机的 Billboard 效果，需要将上述 2D 面片顶点的平面投影到与视线向量完全垂直的 3D 平面上。
    1.  **确定视线向量（View Direction）**：
        计算相机位置与当前粒子中心位置的差值，并对其进行单位化（Normalize）处理，得到方向向量：
        $$viewDir = \text{normalize}(CameraPosition - ParticlePosition)$$
    2.  **构造世界右向量（Right Vector）**：
        将视线向量与世界空间的上方向向量（如 `float3(0, 1, 0)`）进行叉积（Cross Product）。所得向量垂直于二者构成的平面，即为公告牌的本地右向量：
        $$right = \text{normalize}(\text{cross}(viewDir, float3(0, 1, 0)))$$
    3.  **构造本地上向量（Up Vector）**：
        将已归一化的右向量与视线向量再次进行叉积，得到正交平面上的上方向向量：
        $$up = \text{cross}(right, viewDir)$$
    4.  **顶点投影映射**：
        利用顶点对应的 2D 偏移值 `offset2D`，乘以粒子尺寸 `size`，并沿着刚才计算的右向量和上向量方向进行偏移，求得最终的世界空间顶点坐标：
        $$worldPos = ParticlePosition + (offset2D.x \cdot right + offset2D.y \cdot up) \cdot size$$

### 6. 模拟与绘制分离的动态列表机制
*   **传统方案的性能浪费**：
    在包含 64000 个粒子的系统中，随时间推移大部分粒子可能已死亡。若依然在渲染通道中调用 64000 个实例，即使在顶点着色器中将已死亡粒子强制坐标移至极远处（如 `10万` 里外），GPU 依然会为这 64000 个实例启动顶点着色器线程，造成极大的硬件资源浪费。
*   **动态列表的写回流程**：
    为了仅渲染当前帧存活的粒子，需要将模拟逻辑与渲染实例数完全分离：
    1.  声明一个专门的动态渲染数据缓冲区 `RWStructuredBuffer<ParticleDraw> particlesDraw`。
    2.  在 Compute Shader 执行物理模拟的过程中，一旦判定当前粒子存活，则利用原子操作对存活粒子计数器 `particleDrawCounter` 执行 `InterlockedAdd(..., 1, writeIndex)`。
    3.  使用返回的 `writeIndex` 作为索引，将该粒子的位置、颜色和大小写回 `particlesDraw[writeIndex]`。
    4.  若当前线程的粒子已死亡，则直接跳过，不写入 `particlesDraw`。
    通过此方案，`particlesDraw` 缓冲区中将紧凑排列所有存活粒子，排除了所有无效空洞。
*   **回读瓶颈（Get Data）与间接绘制（DrawProceduralIndirect）**：
    *   **CPU 同步回读**：CPU 端通过 `buffer.GetData(drawCounterArray)` 获取 `particleDrawCounter` 的累加终值，作为 `Graphics.DrawProcedural` 的 `instanceCount` 输入。由于该操作属于显存（VRAM）数据写回内存（RAM），会强制阻断 CPU 线程，造成管线等待与数据回读延迟。
    *   **异步回读优化**：使用 `AsyncGPUReadback` 接口发出回读请求，在下一帧或数帧后以回调函数形式获取数据，避免当前帧的主线程发生硬阻塞。
    *   **间接绘制（DrawProceduralIndirect）**：利用 `Graphics.DrawProceduralIndirect` 接口，渲染所需的实例数量不通过 CPU 回读传递，而是直接由 GPU 端的缓冲区提供。这实现了数据的全显存闭环，完全免除了 CPU-GPU 的回读开销，是移动端与高性能渲染的首选方案。

### 7. Built-in 管线下的光照与多 Pass 阴影采样
*   **多 Pass 光照管线**：
    在 Unity 的 Built-in（内置）渲染管线下，要让粒子实现完整的多光源光照与阴影接收，必须实现以下三个 Pass：
    *   **Forward Base Pass**：处理场景中的主方向光（Main Light）、环境光以及主光源的阴影接收。
    *   **Forward Add Pass**：处理场景中的点光源、聚光灯等附加光源。需要设置混合模式 `Blend One One`（加法混合）以将多光源的贡献累加到主光上，同时设置深度写入关闭 `ZWrite Off`。
    *   **Shadow Caster Pass**：虽然粒子可能关闭了投射阴影，但为了让粒子自身能正常渲染和接收来自其他物体的阴影，或者在屏幕空间阴影（Screen Space Shadow）机制下工作，必须在 Shader 中提供 Shadow Caster Pass。
*   **内置管线阴影宏解析（AutoLight.cginc）**：
    *   `UNITY_SHADOW_COORDINATES(idx)`：用于声明保存阴影坐标的纹理寄存器。
    *   `TRANSFER_SHADOW(o)`：在顶点着色器中，将计算好的世界坐标变换为对应的阴影贴图采样坐标并赋值。
    *   `UNITY_LIGHT_ATTENUATION(atten, i, i.worldPos)`：在片元着色器中，传入顶点着色器生成的插值结构体以及计算所得的世界位置，执行阴影图的物理采样，返回的 `atten` 变量即代表当前像素的阴影强度值（`1.0` 表示完全受光，`0.0` 表示处于阴影中）。

---

## 二、 重点术语与概念解析

*   **Compute Shader（计算着色器）**：
    运行在 GPU 上的通用计算程序，跳出了传统顶点-片元渲染流水线的限制，可用于进行物理模拟、路径规划、图像处理等非渲染计算。
*   **DrawProcedural（程序化绘制）**：
    Unity 提供的无网格渲染接口。由渲染管线直接触发顶点与片元着色器，不使用网格过滤器（MeshFilter）或网格渲染器（MeshRenderer），顶点数据完全在 GPU 端动态计算。
*   **RWStructuredBuffer（可读写结构化缓冲区）**：
    HLSL 中的一种无序访问视图（UAV），支持 GPU 线程在任意位置进行并发的读取与写入操作。
*   **InterlockedAdd（原子加法）**：
    HLSL 的内置原子操作函数，保证在多线程同时修改同一内存地址时，加法操作以串行方式正确执行，避免因竞态条件导致的数据覆盖错误。
*   **Winding Order（顶点绕行顺序）**：
    三角形顶点的顺时针（CW）或逆时针（CCW）定义。光栅化器以此来判断三维模型面片的朝向，并据此执行背面剔除（Backface Culling）。
*   **Frustum Culling（视锥体剔除）**：
    GPU/CPU 渲染管线的一种基本优化机制。通过比对物体包围盒（Bounds）与相机的视锥体，直接丢弃视锥体外的物体，避免浪费渲染性能。
*   **DRAM 与 RAM**：
    *   **DRAM（动态随机存取内存）**：在本文中特指显卡板载的显存（VRAM），带宽大但与 CPU 交换数据存在物理总线延迟。
    *   **RAM（随机存取内存）**：系统主内存，CPU 读写速度快。
*   **Register（寄存器）**：
    GPU 芯片内部速度最快、最稀缺的存储媒介。所有的物理与数学指令计算必须在寄存器内发生。
*   **Async GPU Readback（异步显存回读）**：
    一种非阻塞式地将 GPU 显存数据传回 CPU 内存的技术，用以规避传统的 `GetData` 导致的 CPU 线程阻塞。

---

## 三、 工程经验与避坑指南

### 1. 硬件底层逻辑与《图灵完备》的启示
*   **寄存器开销控制**：所有的计算都在寄存器中发生，GPU 寄存器数量极为有限（如主流显卡每线程仅分配约 256 个寄存器）。如果 Compute Shader 中临时变量过多或逻辑分支过深，编译器将无法将数据全部装入寄存器，从而被迫将多余的变量溢出（Spill）到延迟极高的高速缓存或显存中，导致计算速度发生断崖式下跌。推荐尝试《图灵完备》（Turing Complete）等硬件逻辑游戏，加深对寄存器、数据通路与并发硬件模型的理解。
*   **多级存储延迟与发热瓶颈**：
    *   **移动端（Mobile）**：处理器（GPU/CPU Core）与显存（DRAM）之间的数据存取是耗电与发热的最大元凶。频繁的读写显存数据会直接导致移动端设备降频、卡顿及电量骤减。
    *   **桌面端（PC）**：虽然散热良好且总线带宽极高，但由于主板物理距离和 PCIe 协议栈的开销，从显存到内存的数据回传会带来显著的 CPU 帧阻塞延迟（管线气泡）。
    *   **核心准则**：在架构设计中，**应极力避免在 Update 中使用同步的 `GetData` 操作**。

### 2. DrawProcedural 包围盒（Bounds）设置陷阱
*   如果使用程序化渲染，包围盒 Bounds 必须由开发者手动给定。若给定 Bounds 的尺寸过小（如误写为 `0.1`），或其中心点未跟随发射源的世界空间位置移动（如始终停留在世界原点），当相机转动且视锥体移出该 Bounds 时，即使粒子本身扩散到了相机视野中，CPU 也会判定物体不在视野内而触发剔除，导致整个粒子画面在一瞬间完全消失。
*   **避坑指南**：包围盒的中心点坐标必须动态与粒子发射器的世界坐标同步更新，且大小应根据粒子寿命和最大扩散速度进行保守估大（如粒子速度为 $10$ 米/秒，寿命为 $2$ 秒，则 Bounds 的尺寸至少应设为 $40$ 米以上）。

### 3. Billboard 顶点绕行顺序导致的剔除错误
*   手写 Billboard 三角形顶点时，必须严密规划 6 个顶点的 Winding Order。若顶点的时针方向写反，顶点着色器变换后面片的法线将背对相机，被 GPU 默认的背面剔除（Backface Culling）过滤掉，导致屏幕上什么也画不出来。
*   **避坑指南**：若粒子在视野中单面不可见或完全不显示，可优先尝试在材质 Shader 的 Pass 中加入 `Cull Off` 关闭剔除，若关闭后能正常渲染，说明手写顶点的顺序存在错误，应调整数组中顶点的顺逆时针排列顺序。

### 4. GPU 原子计数器清零的遗漏问题
*   像 `particleEmitCounter` 与 `particleDrawCounter` 这样的原子计数器，其功能是统计一帧内发射和绘制的粒子数量。由于 GPU 本身不维护帧间状态清除，**必须每帧在 C# 端的 Update 中向计数器显式 `SetData` 覆盖写入 `[0]` 值**。
*   若漏写此步骤，计数器的数值会在帧间持续累加，几帧之内就会超过最大粒子容量（如 64000），导致新粒子无法发射，或者因为数组写入索引超出缓冲区大小而引发显卡崩溃报错。

### 5. Unity 6 与更高版本的 Built-in 兼容性警告
*   本课的内置管线光照与阴影采样依赖于 `AutoLight.cginc` 中的底层宏。由于 Unity 官方正逐步放弃对 Built-in（内置管线）的维护，在 Unity 6 及其后续版本中，宏编译可能会由于接口微调导致解析失效（出现 `invalid macro` 报错或阴影采样异常）。
*   **开发避坑**：在中后期的大型项目开发中，强烈建议将渲染管线迁移至 **URP（通用渲染管线）**。在 URP 中，通过采样主光源阴影贴图仅需一个渲染 Pass 即可完成同样的粒子阴影采样，不仅彻底告别了 Built-in 复杂的宏拼写，其在不同硬件版本上的跨平台兼容性与稳定性也更为出色。
