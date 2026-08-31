# GPU 驱动的几何管线与 Nanite 技术：从传统渲染瓶颈到 Cluster Based Rendering 与 Visibility Buffer

---

## 一、 核心知识点与原理剖析

### 1. 传统渲染管线（Traditional Rendering Pipeline）的瓶颈

*   **核心概念**：传统渲染管线的一切需求都**在 CPU 端发起**，其基本单元是 `draw primitive`（绘制图元）指令——告诉 GPU 用哪份 vertex（顶点）、哪份 index（索引）画一个小 mesh（网格）。这就是前几节课讲过的经典 `rendering pipeline`。
*   CPU 在发出 draw call 前必须准备一大堆 **render state**（渲染状态）：用哪张 texture（纹理）、Alpha Blend（阿尔法混合）怎么设等；随后指令经 `swap` 提交到 GPU，GPU 再依次跑 `VS`（顶点着色器）、`PS`（像素着色器）、`Rasterizer`（光栅化器）。
*   **核心痛点一：CPU 成为瓶颈**。CPU 经常跟不上 GPU 的速度；而且 CPU 有大量算力浪费在"准备绘制素材"本身——**一次 draw call 本身就是非常 expensive（昂贵）的操作**。
*   **核心痛点二：组合爆炸（Combination Explosion）**。现代 3A 场景中 mesh（网格）× LOD（细节层次）× 材质（每套材质又是一大堆参数 + 各种 texture）× 骨骼动画（skinned animation）会形成天文数字的组合；每切换一次组合都要重新提交 draw call，而且 **render state 的切换本身也非常昂贵**。
*   结论：用传统管线绘制现代 3A 级复杂场景**基本跑不动**，其瓶颈主要不在 GPU 的三角形吞吐，而在 CPU 的提交与状态切换。

### 2. GPU Driven Rendering：从 Draw Primitive 到一次 Draw Call

*   **核心概念**：GPU Driven Rendering（GPU 驱动渲染）的目标是——**整个世界的几何裁剪、LOD 选择、可见性判断全部在 GPU 内部完成**，CPU 只发一条指令"把场景给我绘制一遍"，最多设置一下相机参数，剩下的全部由 GPU 搞定。
*   **两大技术曙光**：
    1. **Compute Shader（计算着色器）成熟**：约 2010 年前后逐渐成熟，可以在 GPU 上完成以前只能在 CPU 上做的通用计算（如视锥裁剪中的大量数学运算），**大大简化 CPU 与 GPU 之间的通讯**，不再需要数据在 CPU 与 GPU 之间来回搬运。
    2. **Indirect Draw（间接绘制）**：以前一个 `draw primitive` 只能画一个 mesh；现在可以传入一个 `array of parameters`（参数数组）或 `parameter buffer`（参数缓冲区），**一个 draw call 可以画很多个 mesh**。
*   **理想状态**：场景数据全部放进显存（现代显卡显存动辄几个 GB，整个场景基本可以放进去），CPU 被释放出来去处理 AI、游戏逻辑、玩法、物理检测、网络通讯等其他系统。
*   这也是后续要讲的 **visibility buffer 与 Nanite 最原始的思想源头**。
*   **最早的先驱者：刺客信条大革命（Assassin's Creed Unity）**，老师印象中是在 **2015 年 SIGGRAPH** 上育碧的分享。其面临的核心挑战：巴黎城市场景中有大量精细建筑与浮雕几何（面片数可达**上亿级**、上万物体），传统方法只能把整个几何加载进来逐个 `instance`（实例）渲染，但大量 instance 甚至单个建筑内部的大部分三角形实际上不可见。
*   可见性判断的颗粒度对比：传统做法只能检测"instance 是否可见"；一旦 instance 只有一个角可见，它全部几万甚至十几万三角形都要被重新渲染，非常浪费。

### 3. Cluster Based Rendering：刺客信条大革命的革命性方案

*   **核心概念**：Cluster Based Rendering（基于簇的渲染）思想非常朴素——把每个 instance 拆分成无数个**固定小尺寸的 cluster（簇）**，每个 cluster 只含少量三角形（大革命时代作者选的是 **64 个三角形**），并且**每个 cluster 都有自己的 bounding box（包围盒）**。
*   **粒度细化带来的收益**：从此可见性判断从"instance 级"细化到"cluster 级"：
    *   可以判断每个 cluster 是否被视锥裁剪、是否被背面裁剪、是否被深度遮挡。
    *   对几何利用率的表达颗粒度变得非常细——**理论上可以做到对遮挡体（occluder）的最大化利用**，尽可能不绘制所有不可能看见的三角形。
*   **Chunk（块）层级**：cluster 太碎，因此 cluster 之上还有 `chunk` 这一层——把一群 cluster 归组（一般 16 或 32 个，多为 **32 个**）。其中有个小 trick：GPU 上每个 compute shader 一次发出一批工作，叫 **wave / wavefront**（NVIDIA 称为 **warp**），NVIDIA 一般 **32 个线程**同时发，AMD 以前是 **64 个**。**若能一次把 warp 的所有线程全部用完，效率最高**，所以 chunk 的设计就是让一整批工作一次性扔出去。cluster、chunk、instance 构成了**三层加速架构**。
*   **GPU 端完整流程**（作者的原流程图）：
    1. **CPU 端（蓝色部分）**：只对 instance 做最简单的粗粒度 `view frustum culling`（视锥裁剪）；并做一个**材质哈希表**，把相同材质、相同 render state 的绘制尽可能归并到一起提交。
    2. 把每个 instance 的 transform（变换）、LOD 等数据打包成一个 buffer 一股脑交给 GPU。
    3. **GPU 端第一步：instance 级精细视锥裁剪**，卡掉大量看不见的 instance（包含 depth 遮挡信息）。
    4. 对保留下来的 instance 遍历其 chunk、cluster，对每个 cluster 做自己的 culling（有独立 bounding box，可做自己的 depth testing）。
    5. **进一步剔除 cluster 背面的三角形**（cluster 是曲面，部分三角形朝前、部分朝后）。
    6. 最终把所有"**可见 instance 的可见 chunk 的可见 cluster 的可见三角形**"打包成一个**超大的 index buffer**——这个过程叫 **index buffer compaction（索引缓冲压缩）**。
    7. 最后一个 draw call（`indirect draw` 或 `multi-draw indirect`）把整个场景一次性画出来。
*   **实现细节**：
    *   GPU 一上来会先分配大约 **8 MB** 的 index buffer 空间。
    *   由于所有 instance、cluster 的遍历都是并行的，写入 index buffer 时**谁先写谁后写可能是乱序的**，依赖 GPU 上原子操作（atomic）的高效实现；只要 workload 均匀，写入效率可以非常高。
    *   **乱序导致的问题**：当几何密度特别高时，帧与帧之间渲染顺序可能变化（如第一帧 instance1、5、8，第二帧 5、8、1）。由于 Z buffer 精度有限，这种顺序漂移会产生 **z-fighting（深度冲突）**。硬件厂商提供的 **`multi-draw-indirect`** 可以锁死 instance、cluster、draw 的绘制顺序，从而避免 z-fighting。
*   **Backface Culling 的巧妙 trick**：cluster 共 64 个三角形，作者提出可以**在一个 cube 上做 cone culling（锥剔除）**——用 cube 的六个面表示三角形朝向（每个面对应一个方向），6 × 64 个 bit（即 6 × 64 个 vector）即可表达整个 cluster 三角形的可见性；相机视角过来后，如果三个面对我可见，那么这三个面中只要有一个面对应的 bit 是"亮"的，该三角形就可见。这个方法的 **backface culling 速度非常快**。该技术在 Nanite 中似乎没有用到，但老师认为它是一个非常好的 trick。
*   **历史意义**：大革命这一作引发了 **cluster based rendering 的革命**，其本质就是**做了一次超级彻底的 visibility culling**——把所有不可见三角形尽可能干掉，把所有可见几何分组打包，用一次 draw call 搞定，从而在获得最优性能的同时**尽可能降低 overdraw（过度绘制）**（同一像素被多个三角形重复绘制造成的浪费）。这正是 Nanite 思想的技术源头。

### 4. Occlusion Culling（遮挡剔除）

*   **核心概念**：对于彼此遮挡但都在视锥内的几何，尽管所有三角形都正对相机，也应尽量把被遮挡的 cluster 整个剔除掉。**Occlusion culling（遮挡剔除）是所有 cluster based rendering 最核心、最复杂的计算模块**——如果做不好，几何做得再高效也很难渲染。没有 occlusion culling，几乎所有现代游戏的性能都会差得一塌糊涂，这是游戏开发中最常见的性能 bug 之一。
*   **基本思想**：尽可能快速、低成本地基于当前相机位置构建一个 depth buffer，基于它构建 **HZB（Hierarchical Z-Buffer，层次 Z 缓冲）**——可以理解为"一层层密铺的幕布"，每层取**最近（最小）的 Z**（保守测试：测试通过说明肯定没被遮挡，没通过则可能被遮挡）。拿到任何 instance / cluster 的 bounding box 后，就能用 bounding box 与 HZB 快速在 GPU 上测试可见性，迅速踢掉大量看不见的东西。
*   **大革命作者方案（单次剔除）**：
    1. 用一个**启发式算法（heuristic）**：优先挑选"体积大且离相机近"的约 **300 个**最有可能遮挡别人的 occluder，先把它们渲染出来形成指导性的 Z buffer。
    2. 把该深度图采样到 **512 × 256** 分辨率。
    3. 把**上一帧的 Z buffer 重新投影（reproject）**到当前相机位置，把采样后深度图上的"洞"填上。
    4. 基于此 Z buffer 构建 HZB，在 GPU 上快速做 cluster / chunk / instance 的逐级剔除。
    *   **该方法的已知问题**：上一帧 Z 里的物体若在本帧高速移动，理论上会产生 artifact（瑕疵）。作者自己承认理论上会有 artifact，但称"结果基本可以接受"。
*   **Two-Pass Occlusion Culling（二次遮挡剔除，另一作者改进）**：
    *   第一步：用**上一帧的 Z** 把所有物体快速测试一遍（保守过滤）。真实游戏场景通过率极低——站在巴黎街道里满眼只有几十栋建筑，而整个城市可能有上万栋。例如 1 万个物体测试后可能只剩约 100 个通过。
    *   第二步：把这少量"可能可见"的物体按**当前相机**全部画一遍，形成**当前帧的新 Z**。
    *   第三步：用这个新 Z，把所有刚被过滤掉的物体**再快速测试一遍**——此时用的是当前帧的 Z，与"用上一帧强行投影"完全不同，因此会发现一些新可见的物体。
    *   **优点**：准确且保守——近处高速通过的马车不会造成错误剔除，最多只是少剔除几个物体，后续测试一定能把它画出来。
    *   **验证案例**：作者（被育碧收购的一个独立团队的老哥）用一个**非游戏案例**做了强力验证——行星边界漂浮的云小行星带，包含约 **25 万个随时运动的小行星/陨石**，该算法仍能取得非常好的效果。老师建议有兴趣的同学**把这两种算法都实现一遍并比较**。
*   **总结**：所有这类算法的共同哲学是——**用尽可能低的成本形成需要的深度"挡板"（occluder）**。

### 5. Shadow Map 的高效生成与 Shadow Caster 剔除

*   **核心概念**：写真实游戏引擎的人都知道，**cascaded shadow generation（级联阴影生成）在整个渲染管线中占据非常显著的时间**，可能占前绘制时间的 **1/10 到 1/5 甚至更多**。
*   **为什么阴影代价如此之高**：
    1. 阴影成本**只和几何复杂度有关**，材质上做任何简化都不受影响。
    2. **shadow caster（阴影投射体）的几何精度必须与 camera space（相机空间）看过去的精度一致**——若用低精度几何去 cast shadow，投到高精度几何上，两者的 depth 信息无法匹配，会产生很多脏的瑕疵（即 shadow acne、漏光等）。
*   **大革命作者的做法**：
    1. 把**上一帧的 shadow map 中的 depth buffer 重新投影**成当前帧的深度，但**采样精度极低（只有 64 × 64 个 pixel）**。
    2. 用这个低精度深度做一次快速 culling，用上一帧的 depth 把大量物体裁掉。
    3. 这非常重要——否则要沿着光的方向把整个巴黎城（cascaded shadow 最后一层可能是方圆几平方公里的物体）再完整绘制一遍。
*   **城市街道场景的聪明假设**：作者提出一个很有意思的思路——当相机**平视**街道时，在 camera space 生成 depth buffer，对每 **16 × 16 个 texel** 采样得到最近的 depth，从而生成一个"四棱柱"（不是 cube，是一个 frustum 状的体积）。数学上可以判断：**shadow caster 形成的阴影体积（shadow volume）与 camera 形成的视锥体积之间如果没有交集，则该 shadow caster 在当前相机位不可能投影出可见的阴影**。
    *   其背后的大假设：游戏建筑是平放在地面上的，人走在街道上——前面几栋房子形成的 depth 在空间上无限投影成一个个四棱锥区域；站在拐角处时，前方房屋会把大部分后面的 shadow caster 全部过滤掉（能高到与视锥相交的物体在全场景里没有几个）。
    *   **这正是 Nanite 中 virtual shadow map（虚拟阴影贴图）要解决的核心问题**：在 camera space 与 light space 下如何高效渲染超复杂几何，只画必要的东西、用必要的精度。
*   老师强调：occlusion culling 是**下一代渲染管线最核心的算法模块之一**。

### 6. Visibility Buffer 渲染管线

*   **前置对比：Deferred Shading（延迟着色）的缺陷**：
    *   第一步把可见几何的 normal（法线）、texture、diffuse、specular、roughness 等数据全部写入一个 **screen space buffer**，即 **GBuffer**；第二步根据光源对像素进行着色。
    *   好处：避免大量不必要的 pixel shading，且可支持海量动态光源（tiled-based 下可实现"thousand lights"、上千个动态光源）。
    *   **最大问题：Fat GBuffer（臃肿的 GBuffer）**。每个像素要存**几十个甚至接近 100 个 bit** 的数据；4K 分辨率下这个 buffer 光写入、fetch 一下就已经很费，**内存带宽成为瓶颈**。手游圈经常讨论"手机上 memory 带宽很紧张，不能直接上 deferred shading，只能用 tiled base + hack"就是源于此。
    *   **在 foliage（植被）场景中的灾难**：植物叶子层层叠叠，绘制顺序不受控制，屏幕上某个像素可能被绘制**十几次**（overdraw 严重）。每一次绘制都要做完整 texture 采样（一次 trilinear 采样是若干次 bilinear 差值——先在 mipmap 上下两层之间差值，每层内部又是 bilinear 差值）、算 albedo/roughness/normal、转 local space，然后写入 GBuffer。虽然 ALU（算术逻辑单元）计算对现代 GPU 还 OK，但**大量 texture sampling + GBuffer 读写会非常慢**。传统 deferred shading 在 foliage 场景会产生巨大的性能问题。
*   **核心概念：Visibility Buffer（可见性缓冲）**：最早的一篇 paper 是 **2013 年**，作者自称这是一种 **cache-friendly（缓存友好）** 的、优化 deferred shading 的方法。
    *   **第一步（几何 pass）**：渲染几何时不做任何材质采样，对每个 pixel **只存几样东西**——`primitive id`（图元 ID）、`instance id`（实例 ID）、`material id`（材质 ID，有 alpha mask 与无 alpha mask 的材质分开处理、走单独通道），全部 **packing 成一个 32 位 `UINT`** 直接写入 screen space buffer。最终画面是一张"色彩斑斓、毫无可读性"的 ID 图。
    *   **第二步（shading pass / 材质 pass）**：拿到 instance id、triangle id 后做 **geometry reconstruction（几何重建）**：
        1. 取出三角形（primitive）的 4 个顶点（3 个顶点 + 深度信息）。
        2. 由相机参数把 3 个顶点投影回屏幕空间；已知该像素的屏幕空间 XY 与深度，可**反算它在三角形内的重心坐标（barycentric coordinates）**。
        3. 用重心坐标对三个顶点的 UV、albedo、roughness、specular 等进行插值，得到该像素完整的 shading information，再进行 lighting（光照）。
    *   **为什么"听起来非常费"却很快**：
        *   取每个顶点数据时 **cache hit（缓存命中）率很高**，常常就在那一小块缓存里取。
        *   屏幕上同一小块区域往往对应同一个三角形，反复取那三个顶点的数据，**cache miss 率很低**（而性能影响最大的恰恰是 cache miss）。
        *   无论屏幕上有多少层 overdraw，几何 pass 付出的真实代价只是打那"花里胡哨的 ID"——计算量极低极低；shading pass 时绘制次数只取决于**屏幕上有多少个像素**，**overdraw 成本几乎为零**。
*   **与 Deferred Shading 混合的架构（非常重要的思想）**：
    *   一部分几何（如 foliage、灌木丛、树林——overdraw 严重）走 visibility buffer 方法；另一部分几何（如主角、近处物体，overdraw 不多）走传统 deferred shading。
    *   visibility buffer pass 输出 visibility buffer，再进入一个 material pass 把 albedo/specular/roughness 等写入 GBuffer；传统管线也写 GBuffer。二者因共享 Z buffer 而**不会产生数据冲突**。
    *   最后的 lighting pass 完全不 care 数据来源，统一上光渲染出整个场景。
*   **必须处理的细节问题——手动计算 mipmap 层级**：传统管线中 vertex shader 算完后光栅化器自动生成 `ddx/ddy`，texture sampling 的硬件 API 会自动选择正确的 mipmap 层级。但 visibility buffer 中只打印了 triangle id，**必须手动额外处理**：根据三角形三个顶点的 UV 投影到 screen space，反算该像素 UV 在屏幕空间上的梯度，从而确定该采哪一层 mipmap。若不做对，结果会产生 artifact（如图中凳子拐角处的白边——两侧密度不匹配导致）。
*   **性能验证**：原作者给过一个 **800 万个三角形**的场景示例，屏幕精度越大时，visibility buffer 相对 deferred shading 的领先幅度越大。老师推测在现代显卡上**差距不但没变小，反而可能变大**——因为显卡**算力（compute）的增长远快于内存带宽的增长**，二者不匹配；visibility buffer 方法算力越强优势越大。
*   **与 Nanite 的关系**：这是理解 Nanite 渲染非常重要的基础——**Nanite 的绘制直接采用了 visibility buffer 的方法去 shading**。

### 7. Nanite 的两个前导知识点总结

*   本节课（第二十二节上）为 Nanite 铺垫了两大基础：
    1. **Cluster Based Rendering**（源自刺客信条大革命的 `visibility culling + index buffer compaction + 单次 draw call` 思路）。
    2. **Visibility Buffer Rendering**（2013 年 paper，cache-friendly 的延迟着色优化，overdraw 成本趋近于零）。
*   下一部分将正式进入 Nanite 本体，包括其自取的名称 **Virtual Geometry（虚拟几何）** 以及这个名字的由来。

---

## 二、 重点术语与概念解析

### 1. Draw Call / Draw Primitive
*   **定义**：CPU 向 GPU 发起的一次绘制指令，指定 vertex、index、render state 等。传统管线以它为最小绘制单元。
*   **应用/注意点**：draw call 本身非常昂贵，render state 切换同样昂贵，是现代 GPU 渲染中 CPU 侧的主要瓶颈。

### 2. Indirect Draw / Multi-Draw Indirect
*   **定义**：Indirect Draw（间接绘制）通过传入 `parameter buffer`（参数数组）让**一次 draw call 绘制多个 mesh**；`multi-draw-indirect` 是硬件厂商提供的、能**锁死 instance / cluster / draw 绘制顺序**的接口。
*   **应用/注意点**：是 GPU Driven Rendering 的关键 API；锁序特性可避免高密度几何下因并行乱序写入导致的 z-fighting。

### 3. Compute Shader（计算着色器）
*   **定义**：在 GPU 上执行通用计算的着色器阶段（约 2010 年起逐渐成熟），不局限于传统渲染管线。
*   **应用/注意点**：它让视锥裁剪、LOD 选择、遮挡剔除、index buffer compaction 等原本属于 CPU 的工作全部可以搬进 GPU，是 GPU Driven Rendering 的前提之一。

### 4. Cluster / Chunk / Cluster Group
*   **定义**：Cluster（簇）是固定小尺寸的三角形组（大革命选 64 个三角形），是可见性剔除的最小几何单元，每个 cluster 拥有独立 bounding box；Chunk（块）是 cluster 的归组（16 或 32 个），用于填满 GPU 的一次工作批次。
*   **应用/注意点**：Nanite 中有一个特别难理解的 **cluster group** 概念（把 cluster 变成 group），与大革命的 chunk 有异曲同工之妙，是理解 Nanite 的一大难点。

### 5. Wave / Wavefront / Warp
*   **定义**：GPU 一次批量发出的工作线程组。NVIDIA 一般 **32 个线程**（warp），AMD 以前是 **64 个**（wavefront）。
*   **应用/注意点**：设计并行算法时应尽量让一次 wave 的工作线程全部用满，效率最高。

### 6. Index Buffer Compaction（索引缓冲压缩）
*   **定义**：把所有可见三角形重新打包成一个超大 index buffer 的过程。大革命方案中 GPU 先分配约 8 MB 缓冲区，并行线程用原子操作追加写入。
*   **应用/注意点**：写入是乱序的，帧间顺序变化可能诱发 z-fighting，需要确定性排序或用 multi-draw-indirect 锁序。

### 7. HZB（Hierarchical Z-Buffer，层次 Z 缓冲）
*   **定义**：把深度缓冲逐层缩小成一层层 mipmap 状的"幕布"，每层保存最近（最小）Z。
*   **应用/注意点**：用于保守的遮挡测试——测试通过则肯定可见，不通过则可能被遮挡；是 GPU 端快速 occlusion culling 的核心数据结构。

### 8. Two-Pass Occlusion Culling（二次遮挡剔除）
*   **定义**：先用上一帧 Z 保守过滤物体，把可能可见的少量物体按当前相机画出新 Z，再用新 Z 复核被过滤物体的遮挡剔除算法。
*   **应用/注意点**：准确且保守，对高速移动物体不会产生错误剔除；已被 25 万小行星的动态场景验证。

### 9. GBuffer / Fat GBuffer
*   **定义**：Deferred Shading 中存储每个可见像素几何与材质属性（normal、albedo、roughness 等）的屏幕空间缓冲；Fat GBuffer 指数据量大（每像素几十到近 100 bit）的 GBuffer。
*   **应用/注意点**：带宽压力大，4K 下尤甚；手游因内存带宽紧张通常用 tiled base + hack 模拟延迟着色。

### 10. Visibility Buffer（可见性缓冲）
*   **定义**：2013 年提出的 cache-friendly 渲染方法——几何 pass 每像素只写一个 32 位 `UINT`（primitive id + instance id + material id），shading pass 再做几何重建。
*   **应用/注意点**：overdraw 成本趋近于零，适合 foliage 等高密度层叠几何；算力越强优势越大。

### 11. Geometry Reconstruction（几何重建）
*   **定义**：在 shading pass 中根据 primitive id 取回三角形顶点，投影回屏幕空间、反算重心坐标，再对 UV / 材质属性插值的过程。
*   **应用/注意点**：需手动计算屏幕空间 UV 梯度以选择正确的 mipmap 层级，否则会产生白边等 artifact。

### 12. Z-Fighting（深度冲突）
*   **定义**：两个几何表面贴得极近、Z buffer 精度不足时，帧间绘制顺序变化导致表面闪烁/破碎的现象。
*   **应用/注意点**：高密度几何（如墙上的贴花）下尤其明显；应保证帧与帧之间的渲染顺序是 deterministic（确定性）的。

### 13. Virtual Geometry（虚拟几何）
*   **定义**：Nanite 为自己的技术取的大气名称。其核心仍是解决在 camera space 与 light space 下如何高效渲染与裁剪超复杂几何的问题。
*   **应用/注意点**：与之配套的 **Virtual Shadow Map（虚拟阴影贴图）** 是阴影侧的关键挑战。

### 14. Overdraw（过度绘制）
*   **定义**：同一像素被多个三角形重复绘制产生的浪费（光栅化、采样、写缓冲重复执行）。
*   **应用/注意点**：foliage 等层叠密集几何的 overdraw 极其严重，是 deferred shading 的主要短板，也是 visibility buffer 的核心优化对象。

### 15. LOD（Level of Detail，细节层次）
*   **定义**：根据距离/投影面积选择不同精度几何模型的机制。传统做法中每个 instance 的 LOD 是整体选择的（整体切 LOD0/LOD1/…）。
*   **应用/注意点**：这与 Nanite 有本质不同——Nanite 的 LOD 是逐 cluster 细粒度选择的（具体将在下节课展开）。

### 16. Mipmap / Trilinear Filtering
*   **定义**：Mipmap 是一系列预降采样分辨率的纹理层级，用于避免采样时的走样与闪烁；一次 trilinear（三线性）采样 = mipmap 上下两层之间做一次差值 + 每层内部各做一次 bilinear（双线性）差值。
*   **应用/注意点**：硬件在传统管线中自动选择 mipmap 层级（由光栅化自动生成 ddx/ddy）；visibility buffer 中必须手动反算梯度。

---

## 三、 工程经验与避坑指南

### 1. 渲染顺序的确定性（Deterministic）与 Z-Fighting
*   GPU 并行 compute 写入 index buffer 是乱序的，帧与帧之间渲染顺序可能漂移；当几何密度极高、表面贴得极近时（例如在墙上加一层贴花几何），Z buffer 精度不足会触发 z-fighting。
*   务必保证帧与帧之间的渲染顺序是**确定性的**，或利用 `multi-draw-indirect` 锁死顺序；这是做真实游戏时必须注意的细节。

### 2. Occlusion Culling 缺失是常见性能 Bug
*   未做 occlusion culling 时，同样一个场景帧率下降一个量级是非常正常的事——几乎所有现代游戏的性能都依赖它。
*   所有遮挡剔除算法的共同哲学：**用尽可能低的成本形成你需要的深度挡板**。

### 3. Cache Miss 的测量与性能分析
*   程序内自测 cache miss 很难，一般要借助 **GPU 厂商提供的 profiling 工具**：把 application 挂到工具里，工具会报告 CPU 的 L1/L2/L3 cache miss。例如英特尔 CPU 上的 **VTune**。
*   GPU 上也有类似的 profiling 工具（硬件厂商开放），因为开发者无法知道硬件最底层的 spec 与接口函数；想写高性能代码必须学会使用这些工具。

### 4. 算力增长快于带宽：架构选择会放大差距
*   显卡算力（compute）增长速度远快于内存带宽增长速度，两者长期不匹配。
*   因此凡是以算力换带宽的方法（如 visibility buffer），其相对优势在现代硬件上**只会越来越大**——这是选择渲染架构时的重要判断依据。

### 5. Visibility Buffer 的工程细节
*   实现基于 visibility buffer 的渲染时，必须手动处理 mipmap 层级的推导（反算 screen space 的 UV 梯度），否则会在几何密度不匹配的边界（如凳子拐角）出现小白边等 artifact。
*   带 alpha mask 的材质与无 alpha mask 的材质要区分开、走单独的通道。

### 6. GPU Driven 对游戏引擎整体架构的意义
*   游戏引擎是对实时性要求极高的 SDK；渲染交给 GPU 后，CPU 被释放出来去处理 AI、逻辑、玩法、物理、网络等系统——这解决了传统 render thread 满载、CPU 资源被大量浪费的问题。

### 7. 学习建议
*   对 cluster based rendering 的两种 occlusion culling 算法（单次启发式剔除 vs two-pass 剔除），**建议都亲手实现一遍并比较效果**。
*   理解 Nanite 时应回到技术源头推演——很多复杂设计（如 virtual shadow map）本质都是在解决"camera space 与 light space 下如何高效渲染、按需精度绘制"这一老问题。

---

## 四、 Q&A 环节（上一节遗留问题解答）

### 1. ECS 架构中如何处理实体被删除
*   ECS 追求硬件性能，**删除 entity 时不会真正释放内存**（每次 allocate / deallocate 都牵扯 heap 操作，很慢），而是把 index 置空、用 free list 把所有空闲空间串起来，下一次 allocation 直接复用该 index。
*   新老 entity 的区分靠 **salt（盐值）**：salt 是累加的计数器——看到相同 index 但不同 salt，就知道旧 handle 已失效。
*   核心原则：在高频系统中尽可能降低 memory allocation 次数。

### 2. 如何测量 Cache Miss
*   程序内自测极难，通用做法是借助 GPU 厂商工具：跑起 application 并挂载到工具中，工具会报告 CPU 各级 cache（L1/L2/L3）的 miss 率（如英特尔 **VTune**）。
*   GPU 上同样存在硬件厂商开放的 profiling 工具，因为开发者拿不到硬件最底层的 spec 接口。

### 3. 如何给设计师一个面向数据编程的工具集
*   **背景**：游戏团队中 artist（艺术家）、designer（设计师）、programmer（程序员）是三种思维方式截然不同的物种——artist 凭直觉拼贴、不关心结构与逻辑；designer 希望表达自我、天然要打破你设计的范式（paradigm），于是才会产出有趣（novel）的创意。
*   **做法**：把每个 component 做成功能明确单一的"积木"，让 designer 自由组合；工具**不替设计师做选择，但必须把他每个选择产生的成本清晰告诉他**（性能预算、budget control）。
*   **预算控制与可视化**：这里"预算"指的是 CPU/GPU 性能预算，其控制与可视化在实战团队中非常重要；QA 流程应**全自动化**——设计师改动玩法、AI、NPC 作战模型后，大量测试自动跑一遍并出性能 report，判断有没有大的性能变化。
*   **trade-off 的引导**：如果 designer 需要高度定制（customize）的功能，就走不了 DOP（面向数据编程）管线（性能可能只有其 1/10），给他一个总性能 budget 让他自己权衡——"是花 10 倍成本做一辆很酷的车，还是用高效成本做 100 辆车"。

### 4. Lumen 中如何处理自发光材质
*   传统渲染中自发光材质的 lighting 很难处理，常给它加一个 **fake lighting（假光源）** 挂在自发光材质上，模拟"身上有个 LED 照亮了"的效果。
*   **Lumen 的方案**：自发光材质的 radiance（辐射率）会写进单独的 **surface cache** 里的 **emission channel** texture；空间采样 **water metric lighting**（体积度量光照）时这些 radiance 全部被采进去；生成 **screen space probe** 时又被采进屏幕空间。
*   **神奇的设定（"左脚踩右脚，梯云纵"）**：这一帧采到的光到下一帧又变成间接光照（indirect lighting）的输入，于是自发光在逐帧传递中自然形成了 **multi-bounce（多次反弹）的 GI 效果**。
*   老师评价：Lumen 对自发光 GI（多次反射）的处理"结构上做得还是蛮漂亮的"，但还需要实验验证：**自发光能否支持 HDR、效果是否足够明显和准确**。

---

## 五、 课程信息与补充说明

*   **结课通知**：课程组为完成作业（约 100 多人提交、40 多人达毕业标准、十几人全部答对）的同学准备了设计精美的毕业证书，可联系课程助理提供地址领取，作为求职求学路上的 certificate。
*   **课程资料**：课程内容正整理成文字版供阅读；课程公众号会持续更新 PICO（Piccolo）小引擎与源码解读，并逐步为其增加新 feature。
*   **知识图谱**：课程组已把 Piccolo 引擎全部知识点做成图谱（超过 1500 个知识点、2000 多人天的工作量），完成后会分享给同学们；结课时有课程组准备的彩蛋视频。
*   **关于 Nanite 的备课过程**：Nanite 是"神坑级"话题，原版 PPT 与作者讲解中存在很多空白和盲区，课程组只能**打开源代码一行行看**并做了大量小实验来确保理解尽可能正确；本课遵循"不讲原始 presentation 顺序、从技术源头讲到关键结构点"的传统。
