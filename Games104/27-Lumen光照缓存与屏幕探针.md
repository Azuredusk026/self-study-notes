# Lumen 动态全局光照的实现原理与工程细节（下）：光照缓存、屏幕空间探针与自适应采样

---

## 一、核心知识点与原理剖析

> 本节为 Games104 第二十一节（下），承接上一节"如何用硬件/SDF 做高速 ray tracing"，聚焦 Lumen 真正的核心：**光是怎么"打进去"的**。老师特意采用与主流讲法相反的顺序——先讲 Lumen 如何把"无数被照亮的表面"转成可复用的光照表达（Mesh Card → Surface Cache → Voxelized World Expression），再讲屏幕空间探针（Screen Space Probe）的分布、采样、自适应细化与最终 shading。全课约 3 小时，其中 Lumen 占约 2 小时。

### 1. 总体思路：把"每个被照亮的表面"变成光源

*   **核心概念**：做全局光照（GI）时，**从光的视角看，整个场景中无论你看得见还是看不见的像素，都会被光照亮**。每一个被照亮的物体表面（老师称为 `facet`，小表面）实际上都是 GI 的**一个光源贡献者**。
*   **困难**：复杂场景中，很可能是"一个你现在看不见的石头表面被光打到，反射光照到我"。传统反射阴影贴图（RSM，Reflective Shadow Map）只能作为一个近似（isbing/近似），有较大局限性；而且表面上的复杂几何细节（法向、材质等）我们并不知道。
*   **Lumen 的破解思路**：**对场景里的所有物体"拍快照"**——以相机位置为精度中心的 Ray LOD，离相机近的物体拍得细、分辨率高，离相机远的物体拍得粗、分辨率低；并且**从六个角度拍**（因为不知道一次 bounce、两次 bounce 的光到底来自天顶还是侧面）。这就是 Mesh Card（网格卡片）。

### 2. Mesh Card：六面快照与 Ray LOD

*   **核心概念**：`Mesh Card`（网格卡片）是 Lumen 为每个实例（`instance`，注意不是 mesh 本身——同一个几何体放两遍就是两个 instance）生成的"六个面"的投影快照。
*   **实现细节**：
    *   卡片的面是**沿 XYZ 轴对称的 AABB Box（Axis-Aligned Bounding Box，轴对称包围盒）**上的面，尽量简单。
    *   每张卡存储该视角下的 **`albedo`（反照率/固有色）、`normal`（法向）、`depth`（深度）**；`depth` 从包围盒开始计算，所以精度不用很高。
    *   如果物体带反射、自发光（`emissive`），还要把 emissive 一起拍出来。
*   **分辨率策略（Ray LOD）**：靠近相机的物体卡片分辨率高，远离相机的物体分辨率低。老师举例：侧面 2 米高的石头可能占据平面 1/3 的面积，会强烈影响近处物体，要拍得细；而 5 米高但距离 100 米远的雕像，卡片精度可以低一点。这样能**充分利用有限的存储空间**。
*   **定位**：真实 GI 很丰富也很复杂，原因就在于此——场景里每个物体都要"排好"。

### 3. Surface Cache：光照信息的统一表达

*   **核心概念**：`Surface Cache`（表面缓存）是存放所有 Mesh Card 的**图集（Atlas）空间**，大小固定为 **4096×4096**，每个 instance 的卡片在这里 `packing`（打包）好。
*   **关键辨析（易混淆点）**：Surface Cache **不是一个单张 texture，而是一系列 texture 组成的集合**（albedo 层、normal 层、depth 层……），形成一处东西。
*   **内存估算**：4096×4096 单层就是 16MB（$4096 \times 4096 \times 4$ bytes），多层叠加后轻松占用**上百 MB**。因此每一层的 albedo/depth/normal 都会使用**硬件支持的压缩方法（compression method）**——所有渲染都知道的原则：内存尽可能小。
*   **交换策略**：随着相机移动，有些物体（instance）会被 `swap out`，有些被放进缓存；因为缓存只用于 GI，多放几个少放几个"死不了人"，**direct collection（直接渲染收集）不需要用这个东西**。
*   **本质理解**：Surface Cache 是对整个世界**光照信息的一种 uniform（统一/规则化）表达**。如果直接去问原始几何面片"你的 radiance（辐射亮度）是多少"，每点材质不同、过程极其复杂；而用 Surface Cache 把最粗的光照信息统一表达后，无论做什么蒙特卡罗 ray tracing，都能**采样到那个点的表达**。
*   **类比（重要）**：老师反复引用心爱的 **Photon Mapping（光子映射）**——把光子"固定"在 mesh 表面，固定住之后才能做 GI（cache）。Surface Cache 相当于"把场景里所有光子的表达固化在上面"，是所有后续工作的基础。它非常像为 lighting 准备的 **Impostor（公告板/替身）**——如同做 LOD 时远处物体用几个面表达成 impostor 一样。

### 4. Surface Cache Final Lighting 的三步法（核心中的核心）

*   **核心概念**：有了 Surface Cache 后，要生成一张 **`Surface Cache Final Lighting`** 图——它上面**储存着成百上千万的"小灯泡"（radiance 采样点）**，是 Lumen 整个工作的基础。
*   **总体循环（老师形容为"左脚踩右脚、替云纵"）**：
    1. 光进入场景后，直接照亮一些表面（正面、背面、反面，不用 care）。
    2. 经过多次 bounce（BS 一堆），最终这些 radiance 要**固化（cache）到 Surface Cache 上**。
    3. Surface Cache 的 Final Lighting 又会被**采样回世界空间体素化表达（Voxelized World Expression）**，供下一帧使用。
*   **三步法明细**：
    *   **第一步：Direct Lighting（直接光照）——简单**。对 Surface Cache 上的每个像素，已知其空间位置、albedo、法向，与每个光源算出 shading 值；可见性（shadow）可以用 shadow map 采样，或者直接发一条从像素到光源的射线、用 **Mesh SDF 查交**判断可见与否——上节讲的 ray tracing 在这里就用上了。假设是**漫反射（diffuse）面**，多个光源就逐个计算后**累加**。
    *   **第二步：生成世界空间体素化光照表达——复杂**。见下一小节。
    *   **第三步：间接光照（Indirect Lighting）采样**。Surface Cache 上每个 **8×8 texel 的 tile**，取 **4 个采样点**（带 jittering），发出 **16 根射线**与空间体素表达求交，得到该点的 indirect lighting；结果存储为**球谐（Spherical Harmonics, SH）**，便于相邻点插值。**注意：Surface Cache 永远不会用自己去做 indirect lighting，它永远在体素光照（Voxel Lighting）上去取结果。**
*   **数学本质：时间上的多级反弹（Multi-Bounce）积累**。这个方法并非 Lumen 首创，老 ROG（以及 SSGI）就有：每次 render 只算一次 bounce，但**再采样上一帧的那一次 bounce 数据**叠加到当前点，数学上就等于二次 bounce。随时间积累：
    *   $F_0$（第一帧）：只有一次 bounce，只有 direct lighting，Surface Cache Final Lighting = 直接光照结果；
    *   $F_0 \to F_1$：有两次 bounce 的值；
    *   $F_2$：有三次 bounce 的值……
    *   蒙特卡罗数值就这样一次一次积累上去，**十几帧内就能得到十几次 bounce 的光照结果**，光看起来自然。
*   **可观察现象（老师自己做的实验）**：用 Lumen 后动了光，能明显感觉到光在**零点几秒内慢慢变亮**——这就是 Voxel Lighting 在传递多 bounce 结果。

### 5. 世界空间体素化光照（Voxelized World Expression / Voxel Lighting）

*   **动机：两类精度问题的分工**。对光源采样时，只有**近距离**的 ray tracing 能精确知道 hit 到哪个 instance、哪个表面；射得远会 hit 掉很多物体，精确 recasting 做不远。Global SDF 只能找到采样点和法向，**拿不到 hit 到哪个 instance、更拿不到那个面的信息**。于是：
    *   **近处物体**：用 per-instance 的精确采样（Mesh SDF），可以精确拿到 radiance；
    *   **远处物体**：以相机为中心做一个**体素化（Voxelization）**表达，Global SDF hit 到哪个体素，就提供那个点的亮度当"灯泡"。
*   **Clip Map 结构**：用传统艺能 Clip Map（裁剪图，围绕相机的多层体素场），**4 层，每层 64×64×64 个体素**。每个体素大小约 **0.78 米**（老师团队读源码反算：$0.78 \times 64 \approx 50$ 米，正好 50×50 米一层，推测原作者是"公制单位爱好者"——很多美国人用英尺让欧洲工程师头疼）。每层缩到 3D texture 里，**每个体素的六个面各存储一个亮度**。
*   **体素化方法（不用硬件 ray tracing）**：Lumen 不采用 SDFGI / VXGI 那种保守栅格化（保守光栅化），而是：
    1. 把体素空间分成**更小的 4×4 tile**（比体素大一点），每个 tile 内先统计有多少个 instance——在几米见方的范围内不可能框太多 mesh；
    2. 从 tile 的边上**随机射一根射线**，若打中任意 mesh，说明该 tile 非空，并能采样出法向、颜色；
    3. 用 **Mesh SDF 直接求交**即可，完全不需要硬件 ray tracer。因此**整个 Lumen 的很多计算基础用的全是 SDF**。
    4. 多次采样碰到多个面/多个点时，Lumen 内部有大量细节处理（今天不展开），处理完就得到世界的一个体素化表达。
*   **增量更新**：和 VXGI 一样，**不需要每帧全部更新**——只有相机移动或场景物体移动时，把"弄脏"的几个区域更新即可。
*   **鸡生蛋问题的解法（巧妙之处）**：第一帧所有空间体素全是黑的，没有 indirect lighting，Surface Cache Final Lighting 就是直接光照结果；然后用 **Surface Cache 的 Final Lighting 去照亮体素（Voxel Lighting）**，存入下一帧；下一帧更新 Surface Cache Final Lighting 时，用体素化世界表达来做 indirect lighting——**取到的天然具有 multi-bounce 结果**。数据是"一套一套对应好的"。
*   **易混淆辨析（老师特意强调）**：
    *   **Voxel Lighting**：每个体素的六个面各存**一个亮度**——记录"**我被照得有多亮**"；
    *   **World Space Probe（世界空间探针）**：是空间上的**光场分布**，作用是"**负责照亮别人**"。
    *   两个概念极易混淆，但算法上环环相扣。

### 6. 自发光（Emissive）物体的光照——被 surface cache 顺带解决

*   **问题**：游戏中自发光很难做。若只考虑自身亮度，往最终颜色上加一层光即可；但真实期望是——武士身上的蓝色灯带，靠近的墙**会被照亮一点**，甚至带一点软阴影。
*   **难点**：处理一个光源的原始做法是"渲染一次"，之前讲了很多方法能解决多光源问题，但**一条光带怎么渲染**？无法把它当点光源。
*   **Lumen 的解法**：用 Surface Cache 方法，一条光带也能整体 cache 到 lighting 里。第一帧光带不起作用；但通过"左脚踩右脚"把它注入 Voxel Lighting 空间，**下一帧就卷回来了，再卷一次、两次，墙就会被照亮**。老师认为这是 Surface Cache 方法中非常巧妙的部分。

### 7. Surface Cache / Voxel 更新的预算与调度

*   **性能约束**：
    *   Direct lighting：每帧**最多更新不超过 1024×24 个 texel**（4096×4096 总量中的一小块）；
    *   Indirect lighting：每帧**最多更新 512×512 texture**（间接光照要在体素世界上采样，虽比 direct 慢但基于 SDF 的采样效率高、Global SDF 更快，总体仍然"挺废的"）。
*   **排队机制**：每个 mesh card 都想更新，必须设置 `priority`（优先级），配合 **bucket sort（桶排序）** 算法来管理挑选更新对象。细节不展开。

### 8. Screen Space Probe：屏幕空间探针的分布

*   **传统做法及其问题**：最自然的想法是在**空间上均匀撒无数采样点**（探针/probe），对球面空间光照采样——构建探针本身是可行的（已有 Surface Cache 与体素光照缓存）。但真实场景起伏极多：靠近相机放密、远离放疏也只能大致表达，**遇到一米间隔一个的几何结构时，探针密度无法表达光场变化**，结果"看上去很平"（行话）。这是所有预生成探针位移方案的共同问题。
*   **Lumen 的激进方案**：**直接在屏幕空间（screen space）打探针**。最粗暴是每个像素都做全球面光场采样（一定对，但太疯狂），折中方案是**每 16×16 个 pixel 采样一个 Screen Space Probe**。
*   **为什么 16×16 合理**：相机近处 16×16 个 pixel 在空间上距离不会太远；而**间接光照是低频信号**，这么近的距离内其变化（variance）确实不大。高频信息（法线、材质细节）由表面自己表达。所以低频的间接光照可以大胆上采样。
*   **每个探针采两个数据**：`radiance`（辐射亮度）和 **`hit distance`（命中距离）**。

### 9. Octahedral Mapping：探针存储与球面采样

*   **核心概念**：`Octahedral Mapping`（八面体映射）是参数化里一个非常经典的 mapping，做任何 GI 算法和采样算法都值得研究。
*   **背景**：图形学常遇到"在球面上撒采样点"。最简单的**经纬度采样（equirectangular）**映射到 2D texture 会出问题：**天顶采样密度特别高、赤道附近采样率很低**。
*   **八面体映射的优点**：
    1. **任意方向映射到 2D UV 的计算非常简单**（就是下页那个 shader）；
    2. 支持**双线性插值（Bilinear Interpolation）**——相邻 texel 之间在纹理空间的插值基本上逼近球面上的插值。
*   **应用**：屏幕空间探针的球面采样精度为 **8×8**（约 64 个方向，大致均匀分布，并非严格均匀）。

### 10. 自适应细化（Adaptive Refinement）——Lumen 的招牌想法

*   **动机**：16×16 pixel 的探针，若 tile 内点在**真实物理空间距离**相差很大（屏幕上相邻、深度值不同），强行插值会把光照细节模糊掉。老师用天文学概念 **"视宁/视差"** 类比：两颗恒星看上去很近（如北斗七星），实际上深度值不同、相聚几百上千光年。
*   **判定方法（有效插值）**：对 16×16 tile，任意一个 pixel 渲染时要**从相邻四个探针之间插值**，取 16 或 32 个点做有效性检测：每个点除了空间位置还有法向，构成一个**法平面**；把四个探针的中心点**投影到该平面上**，看投影距离的权重。作者开发了一个很"high"的函数（老师展示）：
    *   结合平均相机到点距离、乘以一个 $\exp$ 幂次、再配一些常数；
    *   若累计 error 大于某个 `threshold`（阈值），认为该采样点不可用；当无效采样点足够多时，判定**这四个探针对我无效**，于是申请把这个 tile **细分**。
*   **细化流程**：16×16 不够 → refine 到 **8×8** → 还不够 → 再 refine 到 **4×4**。
*   **空间巧用（存储几乎零额外开销）**：把 screen space 所有探针打成一个 atlas（图集）——屏幕是长条形，而纹理是方形，**下方正好有一截空间没用**。Lumen 把需要 refine 的探针 **packing 在下面**，每个探针只存一个 index（"有没有被 refine、位移在哪"）；从 L0（最粗层）开始逐层往下索引。**没有用多少额外存储空间**，却实现了对视线空间光照信息的**自适应采样**。
*   **评价**：老师认为这是 Lumen 非常巧妙的想法，在之前的工作里似乎是**第一个用 screen space 方法做 radiance 采样并加上 adaptive** 的；VXGI、R3（R5?）本质都是 uniform 采样，R5 里那点 adaptive 思想（红色像素不够就再采样）只能算雏形。

### 11. 探针采样与重要性采样（Importance Sampling）："找窗户"

*   **问题**：如果不做重要性采样，8×8 均匀方向采样在真实渲染中必然有问题——**窗户在哪里我不知道**。室内场景必须使劲朝窗户方向多射几根射线，否则任何 GI 结果都像"秃头一样黑一块白一块"。
*   **数学背景**：lighting 函数本质是**蒙特卡罗积分（Monte Carlo integration）**。要让概率函数（PDF）尽量符合被积函数分布；被积函数是两个函数的积：**光**与**表面 BRDF**。因此需要知道：(1) 光在哪强；(2) 法向在哪——因为即使光在这，法向背对它也没意义。
*   **方法一：从上一帧探针估计光的分布**。当前帧不知道光在哪，但假设**光的变化没那么快**——从最近的上一帧 screen space probe 里采样并把值积在一起，就知道哪个区域亮。上一帧数据在 GI 里非常有用，"千万别丢"。
*   **方法二：法向分布函数（Normal Distribution）**。
    *   **陷阱**：framebuffer 里拿到的 normal 是**单个像素的 normal，非常高（高）频**；而一个探针覆盖的 32×32 区域可能含 1024 个像素，其"大致法向朝向"**不能由这一个采样点代表**——它应该是一个**分布（distribution）**，这是特别容易弄混的地方。
    *   **做法（大量 hack）**：在探针影响的 **32×32 范围**（因为对 screen space 做双线性插值时，一个探针最多影响 32 个像素的距离）内**采样 64 个点**；同时做 **depth weight（深度加权）**，确保各点在投影平面上与探针点的深度彼此相差不大，太远的直接扔掉；每个采样点的 normal 用一个 **cos lobe（$\cos \theta$ 瓣）** 表示重要性，而每个 cos lobe 就是一个 **SH**，把所有 SH 积分在一起，得到该区域**法向的分布函数（distribution function）**，从而知道哪些方向需要重点采样。
*   **固定预算 + 重分配（非常实战）**：每个探针固定只射 **64 根射线**（屏幕空间探针有上万个甚至十几万个，每根多射几条现代硬件都扛不住）。做法：
    1. 把 BRDF（来自法向分布提供的 PDF）与 lighting（来自上一帧）**卷积**得到 importance function；
    2. 对 64×64 个方向点**排序**，从最不重要的方向开始丢弃，设置阈值；
    3. 把省下的采样次数**集中到最重要的方向做 super sampling**（例如原 1 次加到 4 次 → 实现一次 refined sampling）。
    *   这样**总采样次数不变、硬件时间成本可算**，但采样密度有了侧重。

### 12. 探针间过滤（Filtering）：相邻探针光的插值非常讲究

*   **动机**：16×16 screen space tile 采出的信息很不稳定、噪声多，需要对每个探针做**3×3 kernel** 的邻域过滤。
*   **陷阱一：方向有效性**。两个相邻探针射出的射线方向不同，不能直接同方向相加。老师举例：前方有个球面反射物，头顶光源照下，我的 light probe 需要采它；但邻居探针那根射线方向朝下，直接拿来用就"彻底用错"。代码中 hardcode 了一个规则：**夹角超过 10 度就丢弃那根射线**（"我只相信我自己"）。不处理就会出现墙上大量噪声。
*   **陷阱二：命中距离有效性**。邻居射得很远（100 米外打中东西）、而自己同一方向 5 米就被拦住，即使夹角小于 10 度，那个 radiance 大概率对我是**无效的**——强行插值会**漏光（light leaking）**。案例：毛巾内侧靠墙处如果生硬不考虑这个差值，会发白很多（光被插值插进来了）。
*   **评价**：Lumen 的每个细节都考虑得"周到"，非常实战。

### 13. World Space Radiance Cache：世界空间探针与 Connected Ray

*   **动机**：screen space 探针数量非常大，且 shading 跑得太远效率低。硬件 ray tracing 的性能不只受射线数量影响，还受**场景复杂度**和**射线跑多远**影响——射 100 米远的效率非常低。
*   **方案**：在**世界空间预先放好一些探针（World Space Probe / World Space Radiance Cache）**，把远处的 lighting 缓存进去；screen space probe 需要一个方向的光时，就**找一个沿途较近的 world probe 把那个方向的光取出来**。
*   **Clip Map 部署**：与前面一致用 clip map，**4 层**，每层约 **50 米**；网格为 **48×48×3**（老师也不确定为什么是 48×3，但原作者就选了这数字）。
*   **采样密度更高**：world probe 是 screen space probe 的"老大哥/参考"，会被 screen space 兄弟采样（screen probe 球面上只有 8×8 很稀疏），所以 world probe 采样 **32×32 ≈ 1000 多根射线**，距离远、密度高，扛得住任意方向来的查询。
*   **Connected Ray（接光/接骨）**：像老中医接骨头，把光分成一节一节。screen space probe 射出的射线**只走一小段**——找到最近的 world probe 包围盒，**取它的对角线长度的两倍**作为射线长度，然后停下"问"world probe："那个方向有没有东西？有多亮？"
    *   **射线长度不是常量**：近处 world probe 密（体素约 1m×1m，对角线×2 ≈ 2~3 米），远处 world probe 大（体素约 50 米），射线长度相应变长。**注意千万不要写死**，这里有很深的道理。
*   **避免重复采样**：world probe 自己的射线会 **skip（跳过）自身对角线长度**的距离——近处已被 screen space probe 采完了，我只提供你踩不到的地方的 radiance。这样 recasting 的起点可以往外推，缩短距离，同时避免重复采样。
*   **漏光 artifact 与"光线弯曲" hack**：screen space 射线很难精确穿过 world probe 中心，world probe 很可能**跳过靠近我的一个阻挡物**造成漏光。Lumen 的处理是：取到最近 world probe 采样的 SDF 编码里的焦点，用焦点与中心连线出去——**光线"拐弯"了**，避免不正确的 visibility 判断。这是游戏渲染常见的 hack：物理不完全正确没关系，能解决一部分漏光问题（但解决不了所有）。
*   **增量更新策略（巧妙）**：
    *   最终 shading 仍用 **screen space probe**（只有这些 pixel 有用），world probe 只是帮助采集贴近物体表面这些探针取不到的**远处光线**；
    *   只有**被 screen space probe 有插值需求**（被周围八个 screen probe 标记为 `marked`）的 world probe 才需要采样——因此虽然理论上有 48×48×48×4 那么多探针，实际每帧需要更新的很少；
    *   场景不动、光不动时**完全不需要更新**。
*   **效果对比**：只有 screen space probe（2 米内）时，光很不正确、漏了很多；加上 world probe 后，光看上去准确得多、更符合 GI 真正想要的效果。

### 14. 最终 Shading：SH 低通滤波

*   **流程收束**：折腾了 Mesh Card → Surface Cache → Voxel Lighting → Screen Space Probe（adaptive sampling）→ World Probe（接光）→ filtering → importance sampling，最终**还是在屏幕空间生成了密密麻麻的 screen space probe**。
*   **SH 的作用**：虽然做了 importance sampling，间接光照用单一方向采的光仍不稳定、有很多 jitter（抖动）。**把光投影到 SH 上**，本质上相当于对间接光做了一次**低通滤波**，把它变成低频信号——shading 时看上去就柔和非常多，最终结果漂亮。
*   **老师自我修正**：最终演示图上的探针采样是 uniform 的，而实际上 adaptive 后下面还挂着 8×8、4×4 的小探针——只是细节，不影响结论。

### 15. Lumen 的 Tracing 策略全景（官方经典图）

*   **核心思想**：**不同 ray tracing 方法在硬件上的成本不一样**，按成本排序：
    *   **最快**：基于 **Global SDF** 的射线求交；
    *   **其次**：屏幕空间（screen space）的 **linear step（线性步进）** 插值；
    *   **稍慢**：**Mesh SDF**（近距离），但前提是跨的步骤不要太大、不要一下子 involve 太多 mesh，否则会非常慢；其准确度比 linear step 更高；
    *   **更慢但更准**：**HiZ（层级 Z-Buffer）** screen space ray tracing，成本稍高但准确度比 linear step 高；
    *   **最准最贵**：**Hardware ray tracing**，准确度最高、cost 最大；也可对 Surface Cache 做 hardware tracing（本质是 impostor，成本很高）。
*   **单个探针 64 方向的分配权重**：官方图里红色 = screen space 垂线方法，绿色 = mesh 方法，蓝色 = Global SDF 方法——三个区域呈**渐变**而非纯色，说明每个探针的 64 个方向里**按权重混合**使用几种 trace 方式。
*   **具体决策链（老师团队从源码中抠出）**：
    1. **Screen Space Trace（HiZ）**：最多 **50 步**，能 trace 到就用结果；
    2. 拿不到 → **Mesh SDF Trace**：trace 距离非常近、只有 **1.8 米**，且只用于**相机 40 米之内**的命中位置；它能返回更详细的数据——`mesh id`、`hit world position`、`normal`，直接送去采样 Surface Cache 的 final lighting；
    3. 前两个条件不满足（距离太远/位置超 40 米）→ 一股脑射 **20 米**的 shadow ray，只用 **Global SDF**，能拿到的只有 **Voxel Lighting**——所以 Voxel Lighting 对整个 Lumen 的光场采集极其重要（探针是采集结果，而采集源头是 surface cache 和 voxel lighting）；
    4. **兜底**（原作者没细讲但团队补充）：Global SDF tracing 也失败时，**踩到天球（sky box / 天空盒）上**——天球在无穷远，采到的就是天光。这不是 hack：真实场景里天空的蓝天白云、移动的云对表面光照影响很大，天光很多时候非常亮。**如果写 Lumen 时把这一趴少掉，对效果影响会特别大。**
*   **SSGI 的地位**：只有 Lumen 时倒影看着很粗糙；而**高频的近处细节（如倒影）主要靠 screen space GI（SSGI）**。想黑 Lumen 的人说"下面用的就是 SSGI"既对也错——Lumen 本身很复杂，但确实离不开 SSGI 的基础思想。

### 16. 性能表现与参数选择

*   **PS5 实测**：GPU 很强但 CPU 一般，全特效下 **3.74ms** 完成整个 GI；若把 screen space probe 与 world probe 分辨率各降 4 倍，可降到 **2.15ms**（牺牲精度）。
*   **16×16 像素间距是试出来的**：作者肯定试过 8×8、32×32，最后 16×16 是大家最能接受的折中；老师猜测这与 UE5 里 Nanite 复杂场景的密度做了最佳配合。
*   **结果评价**：低分辨率下效果已非常 amazing；全分辨率下能看到更多光照细节。效果已逼近过去离线 ray tracing renderer（室内设计师、效果图公司梦寐以求的效果），对电影、动画行业冲击巨大，奠定了未来 10 年下一代游戏引擎渲染的标杆——**GI 是下一代顶级引擎的标配**。Lumen 仍是这一系列征程的开始，做了大量基于这一代硬件的妥协。

---

## 二、重点术语与概念解析

### 1. Mesh Card（网格卡片）
*   **定义**：Lumen 为每个 instance 沿 AABB 六面生成的投影快照（albedo/normal/depth，自发光物体还有 emissive）。
*   **应用/注意点**：以相机位置为中心做 Ray LOD，近细远粗；是 Surface Cache 的基本单元。

### 2. Surface Cache（表面缓存）
*   **定义**：存放所有 Mesh Card 的 4096×4096 图集，是一系列 texture 的集合（albedo/normal/depth/…每层用硬件压缩）。
*   **应用/注意点**：约 100MB 级内存，随相机移动 swap in/out；是对世界光照信息的 uniform 表达，相当于"为 lighting 准备的 impostor"。

### 3. Surface Cache Final Lighting
*   **定义**：Surface Cache 最终生成的一张 lighting 图，储存成百上千万"小灯泡"（radiance），是 Lumen 工作基础。
*   **应用/注意点**：由 direct lighting（逐像素×光源+SDF shadow 查询）+ indirect lighting（体素采样）合成；下一帧又回灌给体素。

### 4. Voxelized World Expression / Voxel Lighting（世界体素化表达 / 体素光照）
*   **定义**：以相机为中心 Clip Map（4 层×64×64×64，体素约 0.78 米，每层约 50×50 米）表达的 3D 光照场，每个体素六个面各存一个亮度。
*   **应用/注意点**：体素化靠 Mesh SDF 求交完成（不用硬件光追）；只更新"脏"区域；负责"我被照得有多亮"。

### 5. World Space Probe / World Space Radiance Cache（世界空间探针 / 世界空间辐射缓存）
*   **定义**：预先在世界空间（Clip Map，4 层、48×48×3、约 50 米一层）部署的探针，采样 32×32≈1000+ 方向，缓存远处光照。
*   **应用/注意点**：只更新被 screen probe 标记（marked）的探针；负责"照亮别人"；与 Voxel Lighting 极易混淆。

### 6. Screen Space Probe（屏幕空间探针）
*   **定义**：每 16×16 个屏幕 pixel 一个、在屏幕空间分布的探针，每个采 radiance 与 hit distance 两个数据。
*   **应用/注意点**：最终 shading 的基础；支持自适应细化（8×8→4×4）；用 Octahedral Mapping 存储球面方向（8×8）。

### 7. Octahedral Mapping（八面体映射）
*   **定义**：把球面方向映射到 2D 方形纹理的参数化方法；方向→UV 计算简单，且纹理空间插值逼近球面插值。
*   **应用/注意点**：相比经纬度映射（天顶过密、赤道过稀）分布更均匀；做 GI/采样算法都建议研究。

### 8. Adaptive Sampling / Adaptive Refinement（自适应采样/细化）
*   **定义**：当 16×16 tile 内探针插值有效性（基于法平面投影距离权重）超过阈值时，把探针密度翻倍（16×16→8×8→4×4）。
*   **应用/注意点**：refined 探针打包进方形纹理下方闲置空间，只存 index，几乎不增加存储。

### 9. Importance Sampling（重要性采样）
*   **定义**：让采样方向 PDF 匹配"光 × BRDF"分布，把有限射线集中到最亮/法向最相关的方向。
*   **应用/注意点**：Lumen 用上一帧探针估计光分布 + 法向分布函数（32×32 范围 64 点、depth weight、cos lobe 即 SH 累加）；固定 64 根射线/probe，排序后丢弃低重要性方向、对高重要性方向 super sampling。

### 10. SH / Spherical Harmonics（球谐函数）
*   **定义**：球面上的正交基函数，用于压缩表示低频方向光场。
*   **应用/注意点**：间接光照存储与插值（8×8 tile 只采 4 点、相邻点 SH 插值）；最终 shading 时对间接光做低通滤波，去噪并使结果柔和。每个 cos lobe 也是一个 SH。

### 11. Clip Map（裁剪图）
*   **定义**：以相机为中心、多分辨率层级、随相机移动在边缘增减数据的体素/探针部署方式。
*   **应用/注意点**：Lumen 的体素表达与世界探针都用它；移动时只需边缘加几个、后面删几个探针，更新量极小。

### 12. SDF（Signed Distance Field，有符号距离场）
*   **定义**：对空间每个点记录到最近表面的带符号距离；Global SDF 是场景整体的粗表达，Mesh SDF 是单个 mesh 的精细表达。
*   **应用/注意点**：Lumen 大量计算基于 SDF 求交（体素化、shadow、trace）。Global SDF 拿不到 instance 信息，只能回退到 Voxel Lighting。

### 13. Ray LOD
*   **定义**：以相机位置为基准的细节层次——近处物体拍得细、远处拍得粗。
*   **应用/注意点**：决定每个 Mesh Card 的分辨率。

### 14. Facet
*   **定义**：被照亮的物体小表面，作为 GI 的光源贡献者。
*   **应用/注意点**：GI 全光路分析的基本单元（direct lighting 只关心眼睛看的方向，GI 要关心全光路）。

### 15. Jittering（抖动）
*   **定义**：对采样点加随机扰动，避免规律采样产生的重复感/过重感。
*   **应用/注意点**：screen space probe 采样与 surface cache tile 的 4 点采样都用到；多帧 jitter 在时序上又变成 multi-bounce 采样（SSGI 也有此技术）。

### 16. Hit Distance（命中距离）
*   **定义**：探针射出的射线命中物体的距离。
*   **应用/注意点**：探针间过滤时用于判定邻居数据是否有效（邻居命中距离与己方差距过大则丢弃，防止漏光）。

### 17. Connected Ray（接光/接骨）
*   **定义**：把光分成一节一节——screen probe 的射线只走到最近 world probe 包围盒对角线×2 处，然后"问"world probe 取远处光照。
*   **应用/注意点**：射线长度随远近 probe 密度变化，绝不能写死。

### 18. Density Test / Depth Weight（密度检测 / 深度加权）
*   **定义**：在采样法向分布时，要求各点在投影平面上与探针点深度彼此接近，太远的丢弃。
*   **应用/注意点**：避免把深度差异大的像素（如两颗"视宁"星）错误地当成同一平面。

### 19. Normal Distribution Function（法向分布函数）
*   **定义**：一个探针覆盖区域内所有像素法向朝向的概率分布，而非单个像素的高频 normal。
*   **应用/注意点**：决定 importance sampling 中 BRDF 部分的 PDF。

### 20. RSM / SSGI / VXGI / DDGI / SDFDDGI（对比算法）
*   **定义**：RSM（Reflective Shadow Map，反射阴影贴图，近似的间接光源表达）；SSGI（Screen Space GI，屏幕空间全局光照，近处高频细节重要）；VXGI（Voxel GI，体素全局光照，uniform 采样 + 保守光栅化）；DDGI（Dynamic Diffuse GI，动态漫反射 GI）；SDFDDGI（基于 SDF 的 DDGI）。
*   **应用/注意点**：Lumen 是这些思想的集大成者，也是第一个用 screen space 做自适应 radiance 采样；DDGI/SDFDDGI 今天被老师"秒掉"（时间不够），放到 200 系列课程。

### 21. HiZ（Hierarchical Z-Buffer，层级 Z 缓冲）
*   **定义**：Z 缓冲的多分辨率金字塔，用于快速 skip 屏幕空间远处区域。
*   **应用/注意点**：screen space ray tracing 用它加速，最多 50 步。

### 22. Light Leaking（漏光）
*   **定义**：光照穿过本应遮挡的物体、或插值把光"插"进不该亮的地方。
*   **应用/注意点**：Lumen 通过探针方向夹角阈值（10°）、命中距离一致性检查、以及"光线弯曲"hack 来缓解，但无法完全根除。

### 23. Multi-Bounce（多次反弹）
*   **定义**：光在场景表面间多次反射的照明效果。
*   **应用/注意点**：Lumen 用"每帧只算一次 bounce + 采样上一帧结果"的时间积累近似得到（$F_0$ 一次、$F_1$ 两次、$F_2$ 三次……），十几帧即收敛。

---

## 三、工程经验与避坑指南

### 1. 讲解顺序的教训：先讲"光怎么打进去"
*   市面上讲 Lumen 大多一上来就讲 screen space probe 的采样/布点，老师认为**应该反过来先把光怎么注入世界讲清楚**（Mesh Card → Surface Cache → Voxel Lighting），否则后面都是空中楼阁。

### 2. 读源码反算参数（团队实战）
*   老师团队（"土法炼钢"）直接读 Unreal 源码，反推出关键数值：体素 0.78 米（$\times 64 = 50$ 米，原作者是公制单位爱好者）；Screen Space Probe 夹角阈值 **10 度** hardcode；Mesh SDF trace **1.8 米 / 相机 40 米内**；Global SDF 兜底 shadow ray **20 米**；Screen Space trace 最多 **50 步**；Surface Cache **4096×4096**；每帧 direct 更新 ≤ **1024×24 texel**、indirect 更新 ≤ **512×512**；World probe Clip Map **4 层 48×48×3**。
*   **教训**：只有动手读代码、搭场景验证，才能把 Lumen 讲清楚；纯看官方图/PPT 很容易被绕晕。

### 3. 必须支持多光源
*   真实项目中 artist 可以随便打光（主光 + 环境补光），**任何 for real-time、for gaming 的 GI 解压算法都必须支持多光源**。Surface Cache 方案对每个 texel 逐光源计算累加，天然简单且高效地支持多光源。

### 4. 16×16 这类"魔数"是调出来的
*   16×16 pixel 的探针间距、0.78 米体素、48×48×3 等参数都是大量试验与硬件/场景密度配合的结果，不要轻易改。

### 5. 更新预算与调度是工程关键
*   间接光照更新很"废"（要在体素世界采样），必须设置**每帧预算上限**并用 priority + bucket sort 排队调度；不能每帧全量更新。

### 6. 静态截图陷阱
*   很多 Lumen 演示是**静帧 + 高配 + 已经跑了 0.5~1 秒**（多次 bounce 收敛后）的效果，非常漂亮；但**动画中光/相机快速移动时，现在的实时 GI 技术仍然很挑战**——光会"慢慢变亮"正是多 bounce 时间积累的特征。看效果图要留个心眼。

### 7. 不要把 Connected Ray 长度写死
*   近处 world probe 密（射线短）、远处疏（射线长），射线长度必须随探针尺度动态变化；同时 world probe 要 skip 自身对角线距离避免重复采样。

### 8. 特殊几何要单独处理
*   **Terrain（地形）无法生成 Mesh Card**，不能放进 Surface Cache，需单独处理；
*   **Participating Media（参与介质，如一团半透明雾）**的光照计算坑特别多；自发光、快速移动场景（如 Sonic 式高速游戏）都是实战化 Lumen 的大挑战。这些细节 Lumen 内部都有处理，但"坑特别多"。

### 9. 概念区分是最大的难点
*   **Voxel Lighting（存"我被照得多亮"）** 与 **World Space Probe（负责"照亮别人"的光场）** 极易混淆；Surface Cache、Voxel Lighting、Surface Cache Final Lighting、World Radiance Cache 之间"数据是一套一套对应好的"，画图时务必理清。

### 10. 内存与 texture 管理经验
*   4096×4096 单层 16MB，多层上百 MB，必须压缩；atlas/packing、内存分配、virtual texture 类算法（老师自述"特别容易写出 bug"）很麻烦，但想清楚后非常值得做。

### 11. 数学与基础学科建议
*   Lumen 把不规则世界变成 uniform 表达后，积分、卷积、采样都基于数学表达；老师建议学完 Games104 后去学**信号处理、线性代数、几何、数学分析、高等代数**，它们与实际渲染问题密切相关。

### 12. 行业认知与敬畏之心
*   游戏引擎深度极深，是计算机科学最前沿的东西；**做引擎要啃硬骨头，要有敬畏之心**。Lumen 之前也有公司（如 Lighten）尝试把动态 GI 软件化，但公司已不在了——"大家会前赴后继"。
*   未来：硬件 ray tracing 与软件 SDF tracing 之争未有定论，但 PS5 3.74ms 的交付证明工程完成度才是关键。Lumen 的 broken case 很多，仍需产品化打磨；预计 GDC 会有大量实战产品文章讲"我用 Lumen 做了哪些调整"。

---

## 四、课堂问答（Q&A）

### Q1：硬件光追发展这么快，Lumen 还做一整套基于 SDF 的软件光追，未来引擎里软件光追和硬件光追是不是都必须？
*   **老师回答**：
    *   硬件光追（NVIDIA 猛推）确有潜力，30 系→40 系实时光追能力会继续加强；但团队实测 30 系约 **100 亿条/秒（10 billion rays/sec）**，作为 GI（尤其多次 bounce）**还是不够**。
    *   Lumen 作者团队正在尝试用硬件光追**取代部分基于距离场的光追**，这个方向值得尝试，但也很有挑战——Lumen 能 work 是因为每个参数都精细调校过，换成硬件光追会牵一发动全身。
    *   **结论：保持开放心态（open minded）**。主机换代慢、移动端更慢，在这些平台上基于距离场的软件 ray tracing（lumen 的路径）**目前仍是一个比较好的方案**。

### Q2：Lumen 系统这么复杂，是不是很难维护？要不要开发一个类似的系统？
*   **老师回答**：
    *   Lumen 是非常复杂的系统，**维护性确实是它接下来面临的大挑战**。游戏引擎面对的场景极度复杂：地形无法生成 mesh card、参与介质（雾）光照、高速运动场景（如 Sonic 式游戏）等，都是实战化问题。
    *   是否要开发类似系统：**针对你自己的 case**，可以只实现部分算法/部分效果——B 站很多人用部分算法做出漂亮的"我实现了 Lumen 效果"视频；但**把全套算法实现一遍，对编程、数学、系统功底要求非常高**。
    *   Lumen 目前仍是技术 demo，还不是商业级产品；期待今年/明年 GDC 上出现用 Lumen 的实战产品文章，展示产品化所需的调整与优化。

### Q3：实时动态 GI 会不会成为下一代 3A 游戏的标配？
*   **老师回答**：**会（yes）**。
    *   人眼一旦被"训练/习惯"了 GI 的效果，就很难接受没有它：**GI 开关直接定义"塑料化的古老渲染感"与"实景化的真实感"**；室内仿真效果已经非常逼近相机拍摄效果。
    *   甚至 GI + NPR（卡通渲染）也能产生以前做不到的效果。
    *   虽然它很难很复杂，但**未来 5~10 年游戏主流可能就是方向**——硬件算力持续增加会提供更大空间。Lumen 并没有彻底解决 GI 问题，但在游戏 GI 历史上迈出了**关键性的里程碑一步**。

---

## 五、课程收尾与预告

*   本课约 3 小时刷新纪录，Lumen 是"大硬菜"；老师坦言课程组为备课爆肝（多次开会到深夜、逐算法抠细节、读代码验证），PPT 因时间紧张略显粗糙，但"结果非常真诚"。
*   未展开内容：**DDGI、SDFDDGI、hardware ray tracing** 等将在 Games 200 系列课程继续；下节课（两周后）讲 **NNIGHT**；明天发布"50 万播放彩蛋"。
*   结束语回归祖师爷 **Kajiya 方程**：整个 rendering 体系在解决的就是如何**实时求解 Kajiya 的渲染方程**；Lumen 只解决了 GI 一部分，`transluency`（半透光）、`fur`（毛发）、透明物等渲染仍然复杂，是未来引擎的征程。
