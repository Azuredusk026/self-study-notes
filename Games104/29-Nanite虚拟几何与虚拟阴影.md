# Nanite 虚拟化几何：无限精度几何的表达、渲染管线与虚拟阴影映射

## 一、核心知识点与原理剖析

### 1. Nanite 的起源与设计动机：从 Virtual Texture 到虚拟化几何

*   **核心概念**：Nanite 是虚幻引擎 5 中官方命名为 **virtual geometry**（虚拟化几何）的技术。它的核心梦想是**在游戏引擎的渲染管线（pipeline）中实现"无限"的几何细节**，达到 **cinematic（电影级）** 精度。
*   老师的开场白强调：每个做实时渲染的人（无论做硬件还是做算法）心中都有还原真实世界的梦想。观察真实的自然（如海浪拍击海岸时无穷无尽的细节）就知道渲染离 realistic（写实）还有多远。
*   **Virtual Texture 思想的源头**：老师首先想到理解 Nanite 的关键词是 **virtual texture（虚拟纹理）**。该思想由 **John Carmack**（id Software 创始人、Quake 系列的作者，老师在课上称其为"心中的神"）提出，时间大致在 **Quake 3 之后**。
    *   **VT 要解决的问题**：真实游戏场景中物体众多、每个物体有自己的纹理（texture），贴图总量非常巨大，无法全部装入内存/显存（"显存都会炸"）。
    *   **VT 的解决方案**：
        1. 给一个内存 **budget（预算）**；
        2. 根据当前相机位置，近处贴图精度高、远处贴图精度低，形成一个 **clip map（裁剪贴图）**；
        3. 在一个限定 budget 内，把当前 view（视野）下所需的所有材质贴图 **cache（缓存）** 起来。
    *   **VT 的两个巨大好处**：
        1. 提供了一个 **unified（统一的）表达**去表达所有材质；
        2. 传统渲染管线中每换一次材质都要切一次 **render state**（绑定 albedo 贴图、specular 贴图、roughness 贴图等），而把所有材质拍进一个巨大的 virtual texture 后，**材质切换一次就搞定了**。
    *   **TeraRendering（万亿像素渲染，虚拟地形系统）** 用的也是 virtual texture 思想。
    *   老师评价：virtual texture 对游戏引擎而言是一个非常 **elegant（优雅的）** 的 solution，"非常的美"，是系统架构之美、算法之美。
*   **Nanite 的梦想**：能否把**几何**也 virtualize，变成 **virtualize geometry**？
    *   理由：**屏幕上的像素数是固定的**，几何数量不可能超过像素数量；每时刻只需渲染几百万个三角形即可，而且每个三角形要尽可能简单。
    *   当达到**每个像素一个三角形**时，就达到了 **cinematic（电影级）** 画质。
*   **核心挑战：几何是 irregular data（不规则数据）**（与 Lumen 课程中反复强调的观点一致）：
    *   几何不是 uniform data（均匀数据），对它做分页（paging）、加载（loading）等处理很麻烦。
    *   例如 index buffer（索引缓冲）在绘制一个 mesh 时可能在 vertex buffer（顶点缓冲）中**跳到非常远的位置**，只能把整个 VB 都加载进来，不能分段加载。
    *   LOD0 和 LOD1 的 mesh 之间可能**彼此没有关联性**，是两个完全不同的 mesh；即使部分顶点可以复用（合并到同一个 VB、用两套 index），其滤波（filter）也是不连续的。
    *   因此几何难以进行 filtering（滤波/过滤）——贴图是"有规律"数据，可以做到近处细、远处糊的连续过渡，而几何做不到。
*   **可以好 filter 的数据候选**：SDF 可以过滤（可对信号做各种滤波），但 SDF 太粗，无法直接绘制。
*   老师在讲解前还特别说明了自己的整理历程：Nanite 原始文档非常晦涩，很多关键性细节需要花很长时间去"猜"；并预告本节的三个部分：① Nanite 最初为什么选择这个 solution；② 重点——几何到底如何表达（cluster 构建 LOD 体系 + BVH）；③ 有了表达之后如何渲染（软光栅化、visibility buffer、材质、阴影 virtual shadow map）。Streaming 和压缩等更多属于 implementation detail（实现细节），会点到为止。

### 2. 几何表达方案的评估与三角形之选

*   **核心概念**：Nanite 作者在做决定之前，**几乎遍历了所有可能的几何表达方案**，最后选择了三角形。老师欣赏作者遍历全部可能性的工作方式。
*   **评估过的方案与结论**：
    *   **Voxel（体素）**：
        *   优点：是非常 uniform（均匀）的表达，滤波特性好，密铺（tessellation）方便。
        *   缺点一：数据量本身很难压下去，尤其要表达**高频细节（如边界）**时要求体素精度很高，数量惊人。
        *   缺点二：对这种数据进行 filtering 和处理非常费。
        *   缺点三（老师认为是最重要的观察）：**现在艺术家的整个 pipeline（3ds Max、Maya、ZBrush 生成的资产）都不是基于体素表达的**。如果为了实时渲染逼迫所有资产变成体素表达，成本惊人。存储是一回事，对传统艺术家管线的工作流是**致命的**。因此作者最终 **bypass（放弃）** 了体素方案。
        *   老师补充：上一节 Lumen 全局光照中基于 sparse voxel（稀疏体素）的方法讲得简单跳跃，正是因为课程组没有找到 source code，担心该算法实现起来坑很多——因为它对世界的表达太复杂了。
    *   **Mesh Shader 流派 / GPU 动态加密几何**（十年前就提出 tessellation shader 概念）：
        *   Tessellation shader、domain shader 等命名让老师"痛恨"（明明能懂的东西被名字绕晕）。
        *   核心思想：有一个粗的几何，在 GPU 上用类似 **subdivision（细分曲面）** 的方法把几何继续细分，可用各种样条、控制点把几何面变得无比光滑。
        *   电影工业用 subdivision surface 特别多；艺术家做精细模型时一上来全部用四边形面（quad）帮助造型；四边形面作为 control points（控制点）可形成 cage（笼状控制网），再细分成很细的光滑几何。
        *   **致命缺陷**：subdivision 只能不断 refine（细化）增加面数，**不能往下减**。例如美术做一匹 5000 面的小马，可以一路细分到 100 万面没问题；但如果小马离得特别远，希望几百个面就表达时，subdivision 做不到。而 Nanite 中每个对象可以一路**减到 100 多个面，甚至减到一个 imposter（公告板）**。这是作者 pass 掉该方案的核心原因。
    *   **Displacement map（位移贴图）流派**：
        *   在粗糙（coarse）的三角形面上通过位移贴图增加几何细节。
        *   优点：做 **organic（有机形态）** 的效果非常好，而且确实可以做 LOD。
        *   缺点一：做**硬表面（hard surface）**时 displacement map 很难设置。
        *   缺点二：拿到一个很精细的几何后，**如何生成一个好的 displacement map 本身需要运算**。
        *   老师指出这一趴是业界目前 debate（争论）最多的：NVIDIA 40 系显卡专门提出的 **micro mesh（微网格）** 就在猛推"基于 GPU 自动加密几何 + 在上面做光线追踪"，不要再用 Nanite 那套复杂技术。**未来十年到底是 Nanite 成为王者，还是基于硬件的几何加密流派获胜**，两派都在快速前进，战斗尚未决出胜负。
    *   **Point cloud（点云）基础的方法**：
        *   3D scanner（三维扫描仪）扫出来的原始数据就是点云，漂亮的几何是基于点云重建的。
        *   优点：filtering 非常方便。
        *   缺点：要达到屏幕绘制精度，point 在屏幕上会变成 splat（小圆点），每个像素可能有很多 **overdraw（重复绘制）**；要达到高精度，效果并不好。
*   **最终选择：三角形**。原因：
    *   三角形是大家最熟悉、最成熟的几何表达形式；
    *   整个 content pipeline（3ds Max、Maya、ZBrush）全面支持；
    *   硬件支持最成熟。
    *   因此 Nanite 的整个无限几何解决方案全部基于三角形构建，这是 Nanite 的 **foundation（基石）**。

### 3. Cluster 化几何与 View Dependent LOD Transition

*   **核心概念**：将细密的几何像 cluster based rendering 一样分成一个个 **cluster（簇）**。课程组用与 Nanite 相同的算法把一条龙模型分成了无数个 cluster。
*   **基本单位**：一个 cluster 大约由 **128 个三角形**组成。
*   **View Dependent LOD Transition（视点相关的 LOD 过渡）**——老师认为 Nanite 最引以为傲、也是整个算法中最复杂的部分：
    *   一条 dragon 由约 2400 万个面构成；当相机去看它时，可以实现**近处显示密度极高、稍远一点每个 cluster 的精度逐渐降低**，从而极大节约面数。
    *   **与刺客信条那代技术的本质区别**：刺客信条技术中**每个 instance 的 LOD level 是锁死的**，不可能在一个 instance 里让不同 cluster 用不同的 LOD；而 Nanite 真正实现了 **view dependent LOD transition**——**对一个物体（一个 instance）而言，它的每个 cluster 会切到不同的 LOD**，从而实现对屏幕空间"三角形预算"（老师口误为"船口/团购"，均指三角形预算/开销）的最大化利用。
    *   效果示例：这条龙几乎只用 **1/30 的三角形预算**就实现了每个屏幕像素几乎有一个三角形的精度。

### 4. 朴素 Cluster 简化方案及其缺陷（锁边问题）

*   **核心概念**：老师先讲一个最简单、最容易理解的 cluster LOD 算法，再讲其严重问题，从而引出 Nanite 的真正解法。
*   **朴素算法步骤**：
    1. 假设 mesh 已经分成很多 cluster；
    2. 每 **2×2** 地把 cluster 合并，合并后三角形数量减少一半，形成上一层的 cluster——这样就能构建一个非常简单的 **cluster LOD hierarchy（层次结构）**；
    3. 每次简化时知道本次简化的 **error（误差）**——几何每次简化 error 就会增加；
    4. 在**当前 view 下**，可以算出每个 cluster 离相机的距离，从而算出**"误差不高于一个像素"的 error tolerance（误差容限）**：
       $$E_{screen} \propto \frac{E_{world}}{d} \le 1\ \text{pixel}$$
       若该 cluster 简化后与原始几何的误差小于一个 **subpixel（子像素）**，就认为可以绘制；若误差大于容限，则继续往下走到更细的 LOD。
    5. 由此可以实时 decide（决定）一个 **cluster based 的 LOD 选择**。
*   **附带好处**：有了这个 LOD 结构，**streaming（流式加载）** 也可以用它实现——精细几何（数量很大）一上来可以不加载，先加载粗的扩展版本；相机推进到小雕像时发现 LOD2 不好使了，就加载 LOD1；再近就加载 LOD0。**一个方法几乎解决了全部核心需求**，这就是 Nanite 最基础的 cluster based 方法。
*   **朴素算法的问题**：
    *   当对 cluster 进行合并、简化时，**简化后的几何边界与未简化几何的边界无法保证对齐**（例如深蓝色 cluster 用 LOD0 绘制、浅蓝色 cluster 用 LOD1 绘制），两者本来是 **watertight（水密）** 地连在一起的，简化后就会在交界处形成 **T-junction（裂缝/裂痕）**（老师称之为 crack）。
    *   **常规解法——锁边（把 cluster 的边锁住）**：每次简化时把 cluster 的边界边全部锁住，简化后的 cluster 无论切到 LOD1 还是 LOD2，与相邻 cluster 仍能 watertight 地拼在一起。但注意**锁的始终是 LOD0 的边**，因此随着 LOD 从 0 到 1、2、3… 上升，边界处的三角形密度永远是高的。
    *   锁边引发**两个严重后果**：
        1. **面片简化利用率不高**：在高层 LOD（如 LOD10）时，一个 cluster 虽然只有 128 个面，却要表达原来几何中很大很大的区域；但锁边导致边界附近需要大量三角形，128 个面远远装不下。
        2. **非均匀的几何密度产生视觉 artifact（伪影）**：若放弃 128 三角形约束，拉开来观察，会发现某些区域几何密度和整体密度 non-uniform（不均匀）。在信号采样上会出现明显 artifact——就像**两块布缝在一起，缝合处能看到"密密麻麻的缝合线"**，因为那个地方加了很多几何细节，而其他面上的细节全部消失。人眼对高频信号、尤其对 **frequency change（频率突变）** 的检测能力非常强，即使数值上的误差已很小，人眼仍能注意到这种 artifact。
*   结论：没有任何一种方法可以简单 work；如果简单方案 work，课程就到此结束了。Nanite 提出了一个非常神奇的方案。

### 5. Cluster Group：解决锁边困境的核心结构

*   **核心概念**：把 10 几个 cluster（8 个、16 个或 32 个，作者自己选了一个数，数字不重要）组成一个 **cluster group（簇组）**。
*   **核心做法**：
    *   **锁住整个 cluster group 的外边界**；
    *   **打碎 group 内部 cluster 之间的边界（boundary）**，所有内部 cluster 作为一个整体一起简化；
    *   这样就能最大化地利用简化带来的好处。
*   **定量感受**：一个 cluster 约 128 个三角形；把 16 个 cluster 聚在一起，约有 2000+ 个三角形。锁住的边界可能只需 1000 多个三角形，而 2000+ 个三角形整体简化到一半（约 1000 个三角形），**锁边的"痛苦"被平摊掉了**，简化变得非常有效。
*   **再聚类（re-cluster）**：对简化过的约 1 万个三角形**再做一次 clustering（聚类）**，把 cluster 的数量一下子减掉一半。
*   **原作者的案例**：四种不同颜色（黄、红、绿、蓝）代表四个不同的 cluster，合成一个 cluster group，整体做简化，但保持整个 group 的外边界（保证 LOD transition 时 watertight），得到三角形数量减半的几何；再 run clustering，得到数量约少一半的 cluster。
*   **关键点 1——父子关系是一对多而非一对一**：简化后的 2 个 cluster（LOD1 层）与下面 4 个 LOD0 的 cluster 之间不是传统树状结构的一对一父子关系，而是**一对多**：每个简化过的 cluster 与下面多个 LOD0 cluster 都有关联关系；LOD1 的两个 cluster 之间是兄弟关系。
*   **算法核心流程**：
    1. 把当前 LOD（比如 LOD0）的所有 cluster 先变成若干个 group；
    2. 在 group 内部做简化；
    3. 简化完后**再 re-cluster（重新聚类）**成新的 cluster，形成上一层 LOD。
*   **关键点 2——相邻层 group 边界不保证一致**：例如 LOD0 有 2000 个 cluster，10 个 cluster 一组共 200 个 group；LOD1 有 1000 个 cluster，同样按 1:10 变成 100 个 group，但**这 100 个 group 的边界与 LOD0 那 200 个 group 的边界不保证一致**。这正是整个算法的核心思想——**保证 LOD 切换时看不到一个持续存在的 boundary**，否则会一直出问题。
*   **为什么这样做（老师的"土法炼钢"类比）**：group boundary 正是做 LOD 时需要锁住精度的边。作者希望被锁住的边在每一层 LOD 时都发生变化——这很像做 **Screen Space AO（屏幕空间环境光遮蔽）** 时对每个像素的采样半径做 **jitter（抖动）**，否则噪声会呈现可被注意到的 pattern（图案）。Nanite 在几何采样时对每一层 LOD 都**强迫把 boundary 做一次"jitter"**，于是当几何随着相机移动不停 popping（跳变）切换 LOD 时，人眼无法"盯死"一个高频区域（因为高频区域每层都在变），也就注意不到清晰的锁边 boundary。老师认为这个方法**非常巧妙**。
*   **极易混淆之处（重要）**：作者原图中的边界不是 **cluster boundary**，而是 **cluster group boundary**：
    *   红色表示 LOD0 所有 cluster group 的 boundary；
    *   在 group 内做简化、再 clustering、再跑一次 grouping 后，得到绿色一层的边界——绿色边界与红色边界没有对应关系；
    *   越往上走，cluster group 越大，各层形成**套接关系**。
*   这张图是**理解 Nanite 几何的基础中最核心的一张图**。
*   **课程组实验（Stanford Bunny）**：
    *   用 Nanite 算法把 bunny 生成很多 cluster（每个 cluster 约 100~128 个三角形）；
    *   把约 16 个 cluster 聚类成一个 cluster group（课件中红色区域）；
    *   对整个 cluster group 做一次简化；
    *   简化完后再 run 一次 clustering，得到新的 cluster——新 cluster 与老 cluster 不再一一对应，LOD1 的 cluster group 里所有 cluster 与 LOD0 的 cluster 都有关系，因为三角形被 reuse（复用）了。
    *   这个"cluster group 到底是什么"正是 Nanite 中大家特别容易弄混的东西。

### 6. 层次结构的本质：DAG 而非树

*   **核心概念**：Nanite 中 cluster 之间的层次结构是一个 **DAG（Directed Acyclic Graph，有向无环图）**，而不是树（tree）。
*   **原作的图是"有问题的"**：作者原图看起来像一棵树，但真实结构从 LOD1 到 LOD2 的连接**并不干净，而是非常复杂**。
*   **课程组读源代码后重绘的 DAG 图**（老师强调这是 Nanite 最重要的图，不理解它后面几乎所有算法都难理解；课程组为这张图"吵了三天三夜"，最终通过读源代码才看明白，堪称"神坑"）：
    *   LOD0 层中同一颜色的 cluster 表示**同一个 cluster group 里的所有 cluster**（红色 group、蓝色 group、绿色 group…）；
    *   对每个 cluster group 做简化，得到 LOD1 层的 cluster；
    *   再 run 一次 grouping 算法，LOD1 的 cluster 与 LOD0 的 cluster group 的关系被**打乱**：LOD1 左边那个 cluster group 里，有些 cluster 指向 LOD0 红色 group 的 cluster，有些指向蓝色 group 的 cluster；另一个 cluster group 也类似地交叉指向。
*   **DAG 的结构特征（乱中有序）**：
    *   **多对多链接**：每个底层的 cluster 可能有 **multiple parents（多个父节点）**；
    *   但**不会**与上一级所有同级 cluster 都建立父关系——**只与由自己做简化带上去的那几个 cluster 建立关系**，因此影响是 **localized（局部化的）**。
*   **验证**：用课程组实现的算法跑 bunny——LOD0 时 cluster 密；LOD2 时 cluster 变大；LOD4 时 cluster 更大；到最后一级时 bunny 只剩约 128 个三角形。说明**每一级的 cluster group boundary 确实一直在变**，因此在 cluster 间来回切换时，人眼不会注意到一个 consistent（一致的）边界。
*   **代价**：这个漂亮的架构需要维护一个非常复杂的 DAG，做 LOD 很复杂。

### 7. 并行化 LOD Selection：从树遍历到扁平列表

*   **核心概念**：有了 DAG，给定相机位后如何选择每个 cluster 的 LOD level。**Nanite 的做法是把 LOD selection 彻底并行化**。
*   **朴素做法及其问题**：从 DAG 的根节点开始（源码显示合并最终只会生成**一个 cluster**，合并即停止）往下遍历：已知每个节点的 error，根据 view 问"error 够不够？不够就往下走"。同一个 cluster group 内的 cluster 要么全部画 LOD0、要么都不画。问题：真实几何（如 dragon 例子）有 1 万多个 cluster 以及层层 LOD 结构，整体遍历一遍非常慢。
*   **核心需求**：让 LOD selection **全部并行化**——每个单位（每个 cluster group / 节点）自己决定在当前的 LOD 下是否绘制。这样得到的 **cut line（裁剪线，即树上"被黄线勾中要绘制"的节点集合）** 必须是 **deterministic（确定性的）**。
*   **为什么必须 deterministic**：如果不做单调性约束，从左向右、从上向下或从右向左遍历，数学上 cut 可能**不稳定**。cut 不稳定时，即使相机没动，仅仅因为 GPU 并行化计算提交的先后顺序有亿万分之一的差异，就可能导致两帧结果不同，出现 **fighting / popping** 的闪烁。
*   **实现确定性的两个条件**：
    1. **DAG 上每个节点的 error 必须单调递增（monotonic，单向累加）**：只要 error 随层级单调上涨，给定任何一个 **error threshold（误差阈值）**，这条 cut line 一定是**唯一**的（数学上可证明）。
    2. **节点可见性判定**（对任何节点，被渲染需同时满足两个条件）：
       $$\text{error}_{parent} > T \quad \text{且} \quad \text{error}_{self} \le T$$
       其中 $T$ 是给定误差阈值。即：**父节点 error 大于阈值、自己 error 小于等于阈值**时，该 cluster 可见。
*   **拍平技巧（flatten）**：其实并不需要按树的顺序从根往下遍历。**把树全部拍平成一个列表（flat list）**，每个节点存下**父亲节点的 error**，然后用上述方程对每个节点独立验证一遍即可。这样就把"树的遍历"变成了 **flat list 遍历**，每个节点的 LOD decision 都能并行化执行（一次可向 GPU 扔 32 个节点）。如果不拍平，按树结构访问时，随着树的深度增加访问效率会下降。
*   **LOD selection 的单位**（极易混淆）：
    *   **代码中以 cluster group 为单位**做检测，但又**精准到每一个 cluster**；
    *   每个检测都是 **isolated（孤立的）** 的；
    *   每个节点存两组数据：**parent error**（本次简化过程中产生的最大 error，如 1.2）和**自己的 error**；
    *   细节 trick：LOD0 的 cluster 自己 error **强制设为 -1**，作为"绝对正确的几何"的标记（-1 比任何阈值小，语义上没问题）。
    *   **重要性质**：源自同一个低层 cluster group 的两个简化后的 cluster，即使分属不同的 LOD1 cluster group，**它们的 error 一模一样**——因为都取本次简化过程中产生的**最大 error**。
*   **完整判定示例**（threshold $T=1$）：
    *   三个候选 cluster group：一个属于 LOD0，两个属于 LOD1（红色、绿色）。
    *   条件 1（parent error > T）：LOD0 的 parent error 1.1 > 1 满足；LOD1 红色 parent error 1.2 > 1 满足；LOD1 绿色 parent error 1.4 > 1 满足。
    *   条件 2（cluster error ≤ T）：LOD1 红色 group 的 cluster error 1.1 > 1 **不满足** → 不绘制；LOD1 绿色 group 同理不满足 → 不绘制；而 LOD0 的四个小 cluster，其 parent error 1.1 > 1、自己 error 为 -1 ≤ 1 → **全部被绘制**。
*   **最容易混淆的误区**：不要理解为"上一级 LOD 检测没通过，就去看下一级"。实际上**整棵树被拍平了**，哪个 cluster 画不画由它自己独立判断；只要保证 error 严格单调向上传递、且下一级的 parent error 与上一级对应 cluster 自己的 error 严格一致，测试结果就严格一致，**几何不会渲染两次**。
*   **为什么这样设计**：传统 LOD 天然用树状结构一次一次向下处理；Nanite 意识到现代 GPU 的并行化处理能力极强，于是把 LOD selection 变成彻底的并行化处理。作者在原始 PPT 中几乎一笔带过，源码里写的是"cluster error < threshold"（其实 group 里存 parent error，group 里每个 cluster 自己比较自己的 error），导致这一部分非常难理解。

### 8. BVH 加速结构：让 LOD Selection 真正可实战

*   **核心概念**：作者报告里只用三句话描述——"构建了一个 BVH（Bounding Volume Hierarchy，包围体层次结构），把所有的 children 的 LOD error 全部 maximum（取最大）在一起，然后所有的 LOD selection 都（通过它完成）"。老师吐槽"这么复杂的算法用三句话讲完"，课程组被迫钻进源代码研究。
*   **动机：cluster group 的数量仍然太大**。
    *   以龙为例：700 万个三角形会生成 11 万个 cluster，group 数量有几万个；
    *   按 1:10 换算，LOD0 约 11000 个 cluster group，LOD1 约 5000 多个，LOD2 约 2000 多个，所有 LOD 加起来约 2 万多个 cluster group；
    *   即使把这些数据并行化处理，效率依然很低——"traverse 一个 array 的数据是很不香的"。
*   **BVH 的构建**：
    *   把 **LOD0 的所有 cluster group** 用 BVH 方法形成一棵树；**LOD1 的所有 cluster group** 也形成一棵 BVH 树；LOD0~LODn 各自形成 BVH；
    *   把这些**所有树的节点连到一个共同的根节点**，构建一个**超级 BVH tree**。
*   **为什么有效**：每个 cluster group 可以想象成一小片几何，有 bounding（包围盒），是空间上的物体块，且大小都差不多——最优的组织方式就是 BVH。BVH 节点的 error 可取它的 bounding，或取子节点 error 的**最大值**。
    *   当相机看到一个物体、且距离较远（如 10 米外）时，LOD0 最大的 error 是 -1，整棵 LOD0 的树（1 万多个 cluster group）**完全不用 traverse**，直接整棵 cut 掉；
    *   同理 LOD1 若在 10 米之外也可整棵 cut 掉；
    *   只有到较高 LOD（如 LOD7）发现 error 需要细分时，才进入树内部去 traverse。
*   **为什么要 LOD0~n 各建一棵树再连根**：物体与相机距离常在 5 米、10 米、20 米之间变化；cluster group 数量最多的那个 case 往往可以整棵 cut 掉（直接踢掉一整棵树），所以先粗粒度剔除最划算。这其实是 **visibility（可见性）领域非常常用的方法**，被作者借用于 LOD。
*   **关键性**：对这么高精度的几何，即使把所有 cluster group 遍历一遍，负载也惊人，何况场景中物体非常多。构建 BVH 对 Nanite 的性能影响非常大——**如果不做 BVH，上一章的并行 LOD selection 算法在实战中效率很低**。
*   **细节**：
    *   BVH 树的**叶节点挂的是一个个 cluster group，不是 cluster**（这一点老师提醒大家核对，课程组花了很多力气读源代码确认）；
    *   尽量构建**张度（分支因子）为 4** 的平衡树（类似数据结构里的"树的平衡"），让遍历效率尽可能高。
*   **实战数据**（600 万个三角形的 case）：
    *   生成约 11 万 cluster；
    *   构建 BVH 后，**只需要 check 107 个 BVH node**（从 11 万降到 107）；
    *   只需 check 4000 多个 cluster（比 11 万少约 **20~30 倍**）；
    *   最终可见的约 2000 多个 cluster。
    *   这让算法变得**真正可以实战**。
*   **BVH 的遍历：类似 job system 的实现**：
    *   传统方法一层层 traverse：第一层扫根节点、产生很多新子节点，扔到新的任务 thread 里再跑，形成第二层、第三层……**非常慢**。
    *   作者实现了一个小的 **job system**：固定一批 **worker thread（工作线程）**，用 **MPMC（multi-producer multi-consumer，多生产者多消费者）** 结构——一端往 task queue（任务队列）里 push（生产者），另一端有空的 thread 就从队列 pop 任务（消费者）；产生任何子节点直接扔进 task queue，有空的线程捡起来处理。
    *   实现依赖 GPU compute shader 的能力：**多个 worker thread 可以共享一个队列，通过原子操作（atomic）实现锁定**。可理解为在 compute shader 上一次发出 32 个 worker thread 并全部固定，配一个公共的 **to-be-handle task buffer**（待处理任务缓冲），两个指针（push 指针、pop 指针）即可。
    *   老师评价：这只是一个小 trick，作者称可带来 **10%~30% 左右的加速**；BVH 本身才是核心思想。
*   讲完这一部分，**Nanite 最复杂的几何表达部分就讲完了**。

### 9. 渲染：Software Rasterization 与 Visibility Buffer

*   **核心概念**：Nanite 几何密度下很多三角形已与屏幕像素差不多大，此时传统硬件光栅化不再高效，Nanite 用 **compute shader 实现软件光栅化（software rasterization）**，据称**比硬件光栅化快 3 倍**。
*   **硬件光栅化的两个隐性假设/缺陷**：
    1. 硬件为计算 texture sampling（纹理采样）所需的 **ddx/ddy**，每次光栅化至少光栅化 **2×2 pixel**；
    2. 硬件光栅化算法是高度优化的古典算法（适用于古典时代的大三角形）：用 **skyline 算法**逐行扫描三角形；屏幕按 **4×4 分成 tile**，先检测 skyline 是否在 tile 内，不在则整个 tile 无需检测。该优化依赖"三角形数量远低于屏幕像素数量"的假设，但当**三角形小到与像素差不多大**时：为了渲染一个像素大小的三角形，要 generate **16 倍（4×4 tile）** 的像素去做光栅化，大量计算被浪费。
*   **Nanite 的软件光栅化原理**：
    1. 若三角形投影小于一个像素，直接**打一个像素**上去即可（快过 skyline 算法在 16 个像素里先算一遍再找到那一个像素）；
    2. 已知每个三角形的边长和面积，就知道其投影约等于一个像素，直接丢上去；
    3. 根据顶点上存的 **UV 可算出 ddx/ddy**，无需做 2×2 pixel。
*   **软/硬光栅化的选择原则**（经验数据，老师认为是作者的工程经验值）：
    *   对**每个 cluster**：若其中所有三角形在投影情况下边长都小于约 **16 个像素**，就把整个 cluster 切换到 **software rasterization pipeline**；
    *   反之若 cluster 离得近、有三角形边长**超过阈值（约 16~18 个像素）**，则交给传统的 **hardware pipeline**。
*   **Early-Z 的软件实现 trick**：software rasterizer 写起来不难（skyline 算法对每行像素算两头即可），但复杂几何遮挡很多，传统管线靠 **early z** 提前剔除，软件版怎么做到？
    *   利用扩展的 GPU SDK，直接写一个 **64 位的原子操作**，算子用 **InterlockedMax**；
    *   **把深度写到 64 位数的高位**，低位随便存 buffer 信息（是哪个 cluster、哪个 triangle）；
    *   只要新深度的数值比已有值大，其他 depth 就会被自动"干掉"（InterlockedMax 保证写最大者获胜）；
    *   这样就**手动模拟了 z testing**，把被遮挡的几何全部过滤掉。
*   **输出与 shading 阶段**：
    *   软件光栅化生成三张数据：**depth（深度）、cluster id、triangle id**（课件用伪彩色表达 id）；
    *   cluster 即使分层也非常密，三角形几乎达到像素级别；
    *   这隐含了关键事实：**Nanite 的 shading 在几何这一趴是用 visibility buffer（可见性缓冲）的方法渲染的**——它**不是上来直接生成 G-buffer**，而是先把每个 cluster id 和三角形 id 打出来，**shading 放在后面**。
    *   Lighting pass 与 visibility buffer renderer 完全一致：拿到 triangle id → 找到三个 vertex index → 取 vertex 的 position 等数据 → 根据每个 vertex 的 UV 插值 → 算出 albedo（反照率）、specular（高光）等。
    *   老师强调：前面课程讲 **visibility buffer based rendering** 正是理解 Nanite 核心的关键 block。
*   **Visibility Buffer 与 Deferred 的结合（现代引擎实践）**：
    *   对真正的现代游戏引擎，建议把 **visibility buffer 和 deferred renderer（延迟渲染器）结合在一起**；
    *   原因：很多物体仍走传统 deferred rendering，此时增加一个 **material pass** 同样去写 G-buffer，后面的 lighting pass 整个 pipeline 全部统一，否则要处理两遍；
    *   示例：Aya / Matrix（曼哈顿）demo 中**不是所有几何都走 Nanite**，只有部分几何走 Nanite，绝大部分几何仍走传统 deferred pipeline，两种渲染毫无压力地混合在一起；
    *   原因是 **Nanite 目前只能解决静态几何**——动态的 character（角色）、奔跑的汽车等，Nanite 目前的技术解决不了。
*   **光栅化的单位**：Nanite 做光栅化时**以每个 cluster 为单位（不是 cluster group）**，根据上述边长原则把整个 cluster 分发给 software 或 hardware pipeline。原作者的示意图中红色区域走 hardware，**绝大部分区域走的全是 software rasterization**。
*   **对硬件发展趋势的展望**：老师认为用 compute shader 做软件光栅化很聪明、效率高于传统硬件实现；并猜测 NVIDIA、AMD 看到这个算法后**一定会在硬件上实现一套效率更高、无需自己写 compute shader 的方案**（比如三角形声明为 tiny triangle 时走高效的硬件 single-pixel 管线）。NVIDIA 最新的 **micro mesh** 功能可能正是把 Nanite 的 software rasterizer 硬件化。未来这些代码很可能由硬件直接支撑，不需要引擎自己写这么复杂的 compute shader。

### 10. 远距离渲染：Imposter

*   **核心概念**：很多 instance 离相机非常远（如 20 米外的小雕像只占几个像素），即使简化到最小的 **128 个三角形**，精度也过度了（bunny 减到 128 三角形时已经不像兔子了）。
*   **方案**：使用传统 LOD 的经典算法 **imposter（公告板/替身）**：
    *   对每个 instance 进行 **12×12 = 144 个 view** 的采样；
    *   每个 view 下采一张 **12×12 像素**的图；
    *   图里存储 **albedo、normal（法线）、甚至深度（depth）**；
    *   当 instance 离得足够远时，**整个 Nanite 管线都不启动**，直接把 imposter 贴上去——depth 正确、G-buffer 数据正确，后面的 shading 该怎么做就怎么做。
*   **启示**：传统 LOD 方法在现代高级管线里依然有用、依然是实战技术。

### 11. Overdraw 分析与硬件趋势

*   **核心概念**：Nanite 场景中 overdraw（重复绘制）依然昂贵，但**不同三角形尺寸下 overdraw 的瓶颈各不相同**：
    *   **small triangle（小三角形）**：无论三角形多小，都要采集三个顶点数据做插值、采样，每个像素都得折腾一遍；且一个像素里可能叠了多个三角形，**vertex transform（顶点变换）和 triangle setup（三角形设置）**变得非常慢（即 visibility buffer 后的那一块很费）；
    *   **medium（中等大小三角形）**：pixel 在 **coverage（覆盖）** 时比较费；
    *   **很大（大三角形）**：最费的是**自己 hack 的 64 位 depth 原子性计算**——原子操作（InterlockedMax）在读写时必须互斥，会形成 **atomic bound（原子操作瓶颈）**。
*   **趋势**：相信随着硬件优化，未来可能不需要自己 hack software rasterizer，甚至不需要自己实现 z buffer testing——NVIDIA / AMD 如果相信这是未来，一定会在硬件上解决。老师期望"业界的发展能够追上引擎发展的步伐"。

### 12. 材质渲染：从全屏深度测试到 Tiled-based 方法

*   **核心概念**：有了几何和 buffer 之后，难点变成**如何给几何贴材质**。游戏场景由非常多的材质合成，每种材质的 texture 数据都不一样（课件中不同材质用伪彩色表达）。
*   **早期 Nanite 方法：材质 ID 深度测试法**：
    *   把每个**材质 id 变成一个 depth 值**，每个 id 在 depth buffer 里的值不同；
    *   对每种材质绘制时，把材质 id 做 **z testing，测试操作符用"等于"**——即 depth 等于当前材质 id 的像素才被绘制；
    *   每个材质全屏扫过去，只有 depth 中材质值等于当前材质 id 的像素被绘制；
    *   **既费又不费**：费在屏幕上有 50 种材质就要 full screen 扫 50 次；不费在每次对每个像素只做一次复杂的 pixel shading（对一个像素只算一遍，而不是 50 遍）。
    *   **缺点**：若镜头里有上百种材质，就要渲染**上百个 full screen pass**；几百万像素做 50~100 次 z testing 的 overhead 并不小。老师类比：做粒子时最容易犯的错误是画很多透明 quad，在镜头前叠几十上百个、每个都全屏那么大，基本没什么贡献却让性能下降非常厉害。
*   **最新 Nanite 方法：Tiled-based 材质渲染**：
    *   思路：为什么要把 full screen 分开处理？用 **tile-based 方法**——把屏幕分成 **64×64 的 tile（瓦片/块）**；
    *   每个 tile 内真正有的材质数量不会那么多；
    *   用 compute shader 把所有 tile 扫一遍，得到一张表：
        *   虽然理论上场景可能有 1000 种、1 万种材质，但当前 screen 可能只用了 100 种；
        *   每个材质称为一个 **material slot（材质槽）**；
        *   对每个 tile 检测：只要有一个像素含该材质，就把该 tile 标记为 yes；
        *   用 **32 位一个数字表达 32 个 tile** 内该材质是否可见；
        *   屏幕分辨率无非 1080p / 2K / 4K，tile 数量有限，因此对每种可见材质生成一个 array，知道哪些 tile 里需要处理该材质；
    *   得到表之后：对每个材质用**一次 indirect draw（间接绘制）**；虽然看起来画了无数个 tile，但可以在 compute shader 里**把没有该材质的 tile 全部跳掉**；
    *   效率：一次处理 32 个 tile，一个屏幕快速扫过去；最费的是逐像素运算，这种方式一次 64×64=3000+ 像素直接过去，且很多 tile 直接跳掉，**非常快**。
    *   这就完成了对 material 处理的最大简化。具体算法不难，研究一下即可清楚。
*   **通用性**：tiled-based 思路在渲染中很常见——比如场景有上百个光源，但每个 tile 里可能只看到两三个光源，处理量就降下来了。**用 compute shader 把复杂的 full-screen 运算切成 tile 分而治之**，能极大降低材质复杂场景下的绘制复杂度。
*   **未来方向**：如果所有 texture 和材质都采用 **virtual texture** 思路（整个材质拍到一张 virtual texture 里），**材质数量可以进一步下降**。作者在 future work 中提到了与 virtual texture 结合，老师认为"very worth considering（很值得思考）"。
*   **重要性**：材质问题不解决，几何再漂亮也无法达到商业级引擎的画面——商业级引擎的材质非常丰富，**artist（美术）绝对不允许只用一个材质**。

### 13. 阴影：Virtual Shadow Map

*   **核心概念**：几何越细，做 shadow（阴影）越头疼。**Virtual Shadow Map（虚拟阴影贴图，VSM）** 是虚幻引擎 5 针对这一挑战提出的技术，老师评价"非常了不起"。
*   **为什么 GI 不构成问题**：Lumen 做的是**低频的间接光照**，不要求几何做到很细——这就是**Nanite 能跟 Lumen 做朋友**的原因。
*   **为什么 shadow 是高频难题**：shadow 很多时候是高频信号，**做 shadow casting 的几何精度要和渲染精度一致**，否则会出现各种很脏的 artifacts。Shadow 的本质是**采样问题**：近处需要高采样密度，远处可以低密度。
*   **为什么不能用光线追踪**：Nanite 的几何表达非常定制化，现代光追硬件**无法在其 BVH 架构里表达 Nanite 的几何**，因此无法用光追算 Nanite 的 shadow。这正是这一代显卡"打架"的地方（NVIDIA micro mesh 强调自建 BVH 后也能光追，而 Nanite 做不了）。
*   **古典 shadow 算法的演进（理解 VSM 的基础）**：
    *   **Cascade Shadow Map（CSM，级联阴影贴图）**：用多层次的 LOD、根据 view dependent 生成不同精度的 shadow map。数学本质是 **view dependent sampling（视点相关采样）**——基于相机位置采取不同的采样精度去生成 shadow。
    *   **CSM 的问题**：围绕相机无脑地一层层变大，但人眼真正看见的区域只有那么一点——比如方圆 2km 的 shadow map 里真正用到的区域就是**一条 refresh（刷新）地带**，大量 texel（纹素）被浪费。
    *   **Sample distribution shadow map（采样分布阴影贴图）**：意识到传统 CSM 的浪费后，根据 view frustum（视锥体）在 shadow map 空间里那条切线**有效地生成 shadow map**，把更多精度放在相机相对近的地方、远处不浪费。分布明显比硬性 CSM 更合理。
    *   **Shadow map 的本质（老师反复强调）**：**shadow map 是根据相机视空间的精度去采样光空间**。为什么 shadow map 会有 artifacts？因为**相机空间对几何的采样频率与几何在光空间对光的可见性采样频率不一样**——两个采样频率不同产生了各种 artifact；加 **bias（偏移）** 正是为了给不准确的测试加一点容错。
    *   **Perspective shadow map（透视阴影贴图）**：试图在相机空间与光空间两个角度之间找平衡，但已经很久没用了，是古老算法。
*   **Virtual Shadow Map 原理**：
    *   把相机看到的世界按 resolution（分辨率）划分——近处采样密度高、远处低，这就是一个 **clip map（裁剪贴图）**；
    *   每个 clip map 区域在 light space（光空间）里分一小块 shadow map；
    *   **shadow map 的大小不是以世界空间大小决定的，而是以该区域在视空间里的大小决定的**——因此远处一大片区域只需一小片几何去表达，对应很小的一块 tile；
    *   这完成了对 shadow map 空间采样的**最大化利用**。
    *   **额外好处**：clip map 按 world space 角度划分，**光不动、相机不动时 shadow map 完全不用更新**；相机向前移动时只有部分需要更新，大量数据可复用（类似 Lumen 中体积材质 clip map 一格一格生成的方式）。
    *   **核心思想总结**：把 shadow map 充分切成一小块一小块，确保每一小块的**采样率与视空间高度对应**；且光不动时可以 **cache（缓存）** 下来。游戏世界中主光源（太阳）基本不动，cache 命中率非常高。
*   **Nanite 中的 VSM 实现细节**：
    *   Nanite 的 shadow 用的就是 virtual shadow map 方法：**对每一个光源给一个 16K（16384）分辨率的大 shadow buffer**；
    *   不同颜色表示相机看过去对应不同版本（层级）tile 所需的几何；
    *   计算每一小块 shadow 时，到那个 virtual shadow map 里找到对应的 tile 判断光源可见性；
    *   **点光源**：对世界的投影是六个 quad（立方体六个面）；查 Unreal 源码发现，放一个点光源会生成**六个 16K×16K 的 virtual shadow map**（老师感叹"太废了"，但确实能解决问题）；
    *   不同 light type（光照类型）对视空间几何的 tile 划分不同：**spotlight（聚光灯）、点光源、方向光**的划分方式都不一样。
    *   **配置与分配（allocation）**：相机和光源都不变时不用重新分配；相机移动时只需更新其中**部分 tile** 的 shadow map。相比 CSM 要画一大片几何，现在只画**一小片与光相关的几何**，其锥体很小，大量物体被 cut 掉，更新效率非常高。
*   **VSM 的 invalidation（失效）场景**：
    1. **相机移动**：如果相机移动是 smooth（平滑）的，只有部分配置需要更新；
    2. **光移动**：一旦光动了，**所有 shadow map 都要变**——所以使用 VSM 时**尽量选择主光不动的场景**（UE5 demo 中山谷的光是固定直直射下来的）；
    3. **几何（物体）本身移动**：shadow 也会变，但可以把这种变化控制得更 local（局部）一些；
    4. 还有很多其他因素会产生变化。
*   **课程组实验**：搭了场景，推动相机、主光不变，观察发现**绿色的切片（山那边的 tile）基本不用更新，只有少量红色 tile 需要更新**——需要更新的地方非常少，这就是 VSM 的巧妙之处。
*   **VSM 的优点**：
    *   生成的 shadow 质量非常高，**高于传统 CSM**；
    *   CSM 在相机移动时不同层级之间有 transition，能明显感受到 **shadow 的 popping（跳变）**（从 LOD0 的 shadow map 切到 LOD1、LOD2 时边界处几何 popping）；而 VSM 的 shadow 基本**很稳定**；
    *   这套 pipeline 能**非常柔和、自然地与 Nanite 结合**；
    *   从数学原理上讲非常 elegant（优雅），老师认为**大概率会成为取代 CSM 的下一代 shadow 技术**。
    *   老师强调：VSM 是理解 Nanite 整个 rendering pipeline 必须理解的基础算法。

### 14. 数据 Streaming 与压缩

*   **核心概念**：Nanite 处理开放世界时可以进行 **streaming（流式加载）** 了。老师认为其中大部分实现比较自然，但指出几个关键点。
*   **Streaming 的实现**：既然已经构建了 BVH 树结构，就可以很自然地根据 **view dependent** 只加载一部分 LOD 数据，再往下去构建 LOD 数据；把数据构建成**一个个 page（页）**，一块一块地往内存里加载——这是很多系统里常用的技术。几何终于可以像 virtual texture 一样**用到即下载、不用则不下载**。老师认为"如果我想做一个基于 Nanite 的技术，这可能是我必须要用的技术"。
*   **压缩的两个层次**：
    *   **内存中的数据：quantization（量化）**——把浮点型数据变成定点型：
        *   vertex 位置：如果知道一个 cluster 的 **bbox（包围盒）**，内部很多位置就可以定点化；
        *   normal（法线）：不需要很高精度，可以定点化；
        *   UV：也可以定点化；
        *   好处：节约存储空间，且**访问、反向解码的效率都非常高**。
    *   **磁盘上的数据：hardware LZ decompression（硬件 LZ 解压缩）**：
        *   **LZ compression** 是效率最高、且很多硬件支持的压缩/解压缩算法；
        *   **DirectStorage**（Microsoft、AMD、NVIDIA 的 SDK 中的技术）：从磁盘读数据**不过 CPU、不过主内存，直接读到显存**，读取过程中自动对数据解压缩（解压缩算法就是 LZ）；
        *   配合 **SSD（固态硬盘）**，数据可直接到显存且自动解压，实现海量数据从磁盘高速涌入。
    *   **提高 LZ 压缩效率的小 trick**：在数据中**加一些 padding data（填充数据）**，让 LZ 的**字典命中率更高**，从而获得更高的压缩率。
*   **总结评价**：Nanite 首先是一个非常了不起的**工程思想**；其次作者团队把这一代硬件的性能**基本压榨到了极致**——想学高性能编程，可以从 Nanite 的实践中学到很多有意思的东西。课程组制作的小视频展示了 Nanite demo 中山谷下**一层一层、达到像素级精度的三角形层叠**构成丰富几何世界的过程。老师认为：**下一代的游戏必须有一套全新的几何管线来 handle 这些复杂事件**，一步步逼近电影级/影视级画面，这是每一代游戏人、游戏引擎人的梦想。

---

## 二、重点术语与概念解析

### 1. Virtual Texture（虚拟纹理）
*   **定义**：John Carmack 在 Quake 3 之后提出的思想：游戏场景贴图总量巨大，无法全部装入内存/显存，因此按相机位置给一个 budget，用 clip map 形式把当前 view 所需的材质贴图 cache 起来，提供统一的材质表达。
*   **应用/注意点**：避免频繁切换材质 render state，一次绑定即可。TeraRendering 也用了该思想。Nanite 的几何虚拟化正是这一思想在几何上的延伸。

### 2. Clip Map（裁剪贴图）
*   **定义**：根据观察者位置划分的、近处精度高、远处精度低的纹理/数据组织方式。
*   **应用/注意点**：VSM 用 clip map 划分视空间采样密度；VT 用它组织缓存。

### 3. Cluster（簇）
*   **定义**：Nanite 几何的基本组织单元，约 128 个三角形构成一个 cluster。
*   **应用/注意点**：LOD 选择、光栅化（software/hardware 分发）均以 cluster 为单位；BVH 叶子挂的是 cluster group 而非 cluster。

### 4. Cluster Group（簇组）
*   **定义**：由若干（约 8/16/32 个）cluster 组成的中间结构；LOD 锁定整个 group 的外边界，打碎内部 cluster 边界后整体简化。
*   **应用/注意点**：LOD selection 以 cluster group 为单位做检测、又精准到每个 cluster；各层 LOD 的 group 边界刻意不重合（"jitter"），避免人眼注意到固定的锁边 boundary。这是 Nanite 中最易混淆的概念。

### 5. View Dependent LOD Transition（视点相关的 LOD 过渡）
*   **定义**：同一 instance 内不同 cluster 根据相机距离/视角独立切换 LOD。
*   **应用/注意点**：与刺客信条那代"每个 instance LOD 锁死"的技术本质不同，是 Nanite 最引以为傲的能力，也是算法最复杂的部分。

### 6. DAG（Directed Acyclic Graph，有向无环图）
*   **定义**：由顶点和有向边组成、不含环的图。Nanite 的 cluster 层次结构是 DAG 而非树。
*   **应用/注意点**：底层 cluster 可有多个 parent，但只与自身简化来源的几个 cluster 建立父关系，影响是局部化的；图中各层 cluster group boundary 交叉套接，是理解 Nanite 几何的核心。

### 7. BVH（Bounding Volume Hierarchy，包围体层次结构）
*   **定义**：用包围盒把空间物体组织成树状层次，用于加速空间查询/遍历。
*   **应用/注意点**：Nanite 对每个 LOD 的 cluster group 各建一棵 BVH，再连到公共根节点构成超级 BVH；LOD selection 时远距离整棵树直接 cut 掉，把检查量从 11 万 cluster 降到 107 个 BVH 节点 + 4000 多个 cluster。

### 8. Error / Parent Error（误差 / 父节点误差）
*   **定义**：几何简化过程中偏离原始几何的度量；parent error 是本次简化过程中产生的最大误差，向上传递时严格单调递增。
*   **应用/注意点**：LOD 选择依赖"父 error > 阈值 且 自己 error ≤ 阈值"的双条件；error 必须精确计算，否则相机移动时出现可察觉的 popping。

### 9. Cut Line（裁剪线）
*   **定义**：在类树状 LOD 结构中选择"绘制哪些节点"的边界。
*   **应用/注意点**：在 error 单调递增的约束下，给定 threshold，cut line 唯一（deterministic），从而保证并行化 LOD selection 结果确定、不闪烁。

### 10. QEM（Quadric Error Metrics，二次误差度量）
*   **定义**：一种经典的网格简化误差度量方法（基于二次曲面/二次型误差）。
*   **应用/注意点**：课程组的实验 pipeline 用它作为 simplification（简化）的 error metric。

### 11. Software Rasterization（软件光栅化）
*   **定义**：用 compute shader 在 GPU 上自行实现三角形光栅化，代替硬件光栅化。
*   **应用/注意点**：对边长小于约 16 像素的 cluster 使用；比硬件快约 3 倍；与硬件管线通过"所有边 < 16 像素则走软件、否则走硬件"的原则按 cluster 分发。

### 12. InterlockedMax（原子最大操作）
*   **定义**：GPU 原子操作算子，对目标内存执行读-比较-写最大值，不可中断。
*   **应用/注意点**：Nanite 用它做 64 位深度原子打包：深度放高位、cluster id / triangle id 放低位，实现软件 early-z 剔除。

### 13. ddx / ddy（屏幕空间偏导数）
*   **定义**：像素在屏幕上沿 x/y 方向对某属性的偏导数，用于纹理采样时的 mipmap 选择。
*   **应用/注意点**：硬件光栅化需 2×2 pixel 计算导数；软件光栅化可直接由顶点的 UV 插值算出，无需 2×2 像素。

### 14. Visibility Buffer（可见性缓冲）
*   **定义**：只存储每个像素可见的三角形/实例 id 的缓冲，不存完整 G-buffer。
*   **应用/注意点**：Nanite 先输出 cluster id 和 triangle id，lighting pass 再取顶点数据插值算 albedo/specular 等；现代引擎建议与 deferred renderer 结合，用额外 material pass 统一写 G-buffer。

### 15. Early Z（提前深度测试）
*   **定义**：像素着色前先做深度测试，被遮挡的片元直接丢弃，节省计算。
*   **应用/注意点**：硬件管线原生支持；软件光栅化通过 64 位 InterlockedMax 原子操作模拟。

### 16. Skyline 算法（天际线算法）
*   **定义**：古典硬件光栅化算法，对三角形逐行（scanline）扫描填充像素。
*   **应用/注意点**：配合 4×4 tile 预检测可快速跳过不覆盖的 tile；但小三角形时代效率低，被 Nanite 软件光栅化替代。

### 17. Imposter（公告板/替身）
*   **定义**：用预先渲染的多视角小图代替远处物体几何的 LOD 技术。
*   **应用/注意点**：Nanite 对足够远的 instance 用 12×12=144 个 view、每 view 12×12 像素采样，存储 albedo/normal/depth，直接替换整个 Nanite 管线。

### 18. Overdraw（重复绘制/过度绘制）
*   **定义**：同一像素被绘制多次的现象。
*   **应用/注意点**：小三角形主要费在 vertex transform 与 triangle setup，中三角形费在 coverage，大三角形费在 64 位深度原子操作（atomic bound）。

### 19. Material Slot（材质槽）
*   **定义**：Tiled-based 材质渲染中每种可见材质对应的处理槽位。
*   **应用/注意点**：用 32 位掩码一次标记 32 个 tile 中该材质是否可见，再用 indirect draw 只绘制含该材质的 tile。

### 20. Tiled-based Rendering（基于瓦片/分块的渲染）
*   **定义**：把屏幕划分成固定大小 tile（如 64×64），按 tile 组织渲染计算。
*   **应用/注意点**：Nanite 最新材质渲染方法；也用于 tiled lighting（每个 tile 只处理该 tile 可见的少数光源）。

### 21. Indirect Draw（间接绘制）
*   **定义**：由 GPU 生成绘制参数（顶点数、实例数等）的绘制调用。
*   **应用/注意点**：材质渲染中每个材质一次 indirect draw，在 compute shader 里跳掉不含该材质的 tile。

### 22. CSM（Cascade Shadow Map，级联阴影贴图）
*   **定义**：按距离把视锥切成多级，逐级生成不同精度的 shadow map。
*   **应用/注意点**：数学本质是 view dependent sampling；问题是大量 texel 浪费、层级过渡时有 shadow popping。

### 23. Virtual Shadow Map（VSM，虚拟阴影贴图）
*   **定义**：把 shadow map 空间切成小块（page/tile），按视空间采样需求动态分配，采样率与视空间高度对应。
*   **应用/注意点**：Nanite 对每个光源用 16K 分辨率 buffer；点光源生成 6 个 16K×16K；光不动时大量 tile 可 cache，更新量极小；shadow 质量高且稳定，老师认为大概率取代 CSM。

### 24. View Dependent Sampling（视点相关采样）
*   **定义**：根据相机位置决定采样精度。
*   **应用/注意点**：是 CSM 的数学本质，也是 VSM 设计的基础。

### 25. Bias（阴影偏移/容错）
*   **定义**：给深度比较加偏移量以容忍采样误差。
*   **应用/注意点**：因为相机空间与光空间的采样频率不一致会产生 artifacts，bias 就是给不准确测试加的容错。

### 26. Micro Mesh（微网格）
*   **定义**：NVIDIA 40 系显卡推出的基于硬件的几何加密技术，在低模上加细节并构建自有的 BVH 以支持光追。
*   **应用/注意点**：代表"硬件加密几何 + 光追"流派，与 Nanite 竞争；老师猜测它可能把 Nanite 的软件光栅化硬件化了。

### 27. Quantization（量化）
*   **定义**：把浮点数据转成定点数据以压缩存储。
*   **应用/注意点**：Nanite 内存中数据压缩手段：利用 cluster bbox 定点化顶点位置，normal/UV 也可定点化。

### 28. LZ Compression（LZ 压缩）
*   **定义**：基于字典的经典无损压缩算法，效率高且硬件支持广泛。
*   **应用/注意点**：Nanite 磁盘数据压缩手段，配合 DirectStorage 在数据直读显存过程中自动解压；加 padding data 提高字典命中率。

### 29. DirectStorage（直连存储）
*   **定义**：Microsoft / AMD / NVIDIA SDK 中的技术，数据从磁盘（SSD）不过 CPU 和主内存直接进显存。
*   **应用/注意点**：配合硬件 LZ 解压实现海量几何数据快速流式加载。

### 30. Job System / MPMC（任务系统 / 多生产者多消费者）
*   **定义**：任务并行的调度模式：worker thread 从共享任务队列取任务执行，生产者往队列推任务。
*   **应用/注意点**：作者用它并行遍历 BVH；在 compute shader 上用原子操作实现共享队列。

### 31. SDF（Signed Distance Field，有向距离场）
*   **定义**：每个点存储到最近表面的带符号距离的场数据。
*   **应用/注意点**：可过滤、信号特性好，但太粗无法直接绘制，故 Nanite 不采用。

### 32. Subdivision Surface（细分曲面）
*   **定义**：用四边形控制网格（cage）递归细分生成光滑曲面的建模方法。
*   **应用/注意点**：电影工业常用；只能向上细化、不能向下简化，故不适合 Nanite 的远距离低面数需求。

### 33. Displacement Map（位移贴图）
*   **定义**：通过贴图驱动顶点沿法线位移以增加几何细节的技术。
*   **应用/注意点**：organic 效果好、可做 LOD；硬表面难设置，且从精细几何生成位移贴图本身需要运算。

### 34. Skinned Geometry（蒙皮几何）
*   **定义**：带骨骼蒙皮动画的几何（如角色）。
*   **应用/注意点**：Nanite 目前无法表达，动态几何是 Nanite 的短板。

### 35. T-junction / Crack（裂缝/裂痕）
*   **定义**：相邻曲面共享边时因简化程度不同产生的缝隙/破面。
*   **应用/注意点**：cluster 简化不锁边就会产生；锁边可保证 watertight 但带来密度非均匀问题。

### 36. Watertight（水密性）
*   **定义**：几何表面无缝衔接、没有裂缝的状态。
*   **应用/注意点**：LOD transition 时不同 cluster 需保持 watertight。

---

## 三、工程经验与避坑指南

### 1. 理解 Nanite 架构的踩坑经历（课程组经验）
*   Nanite 原始文档（paper/PPT）非常晦涩：关键细节需要花很长时间去"猜"。老师的策略是**直接读源代码**（"我们大部分的东西都是啃代码啃出来的"）。
*   **cluster group 概念**是全书最容易混淆的点：原作图里画的边界其实是 cluster group boundary 而非 cluster boundary；LOD 之间父子关系是一对多，不是树的一对一。
*   **DAG 图是"神坑"**：原作图画得像树，实际连接非常复杂。课程组为这张图"吵了三天三夜"，最后通过读源代码才弄明白。教训：**遇到官方文档说不清的关键结构，直接看实现**。
*   **BVH 只讲三句话**：作者对如此关键的加速结构一笔带过，课程组被迫钻进代码研究。老师调侃"这么高深的算法怎么可能让我们凡人学会"，但也指出理解 job system 后就能理解其 compute shader 上的 MPMC 遍历。
*   老师提醒：如果发现课程组讲错，欢迎更正确认——因为很多结论（如 BVH 叶子挂 cluster group 而非 cluster）都是靠大量读代码推断出来的。

### 2. 误差与 LOD 切换的工程质量
*   **error 的计算必须准确**：如果 LOD 计算（error）不准确，相机推来推去时会出现 noticeable（可察觉）的 popping。每次误差都要保证 **subpixel（子像素）** 级别。
*   **error 必须单向单调累加**：error 向上传递必须严格单调递增，这是 cut line 唯一性（deterministic）的数学前提；同时下一级 parent error 必须与上一级对应 cluster 自己的 error 严格一致，否则并行化判断结果不一致、几何会被渲染两次。
*   **锁边是一把双刃剑**：锁边能保持 watertight，但会让边界三角形密度永远偏高（利用率下降），并产生"缝合线"式的非均匀密度 artifact。**人眼对高频信号和频率突变极其敏感**，数值上很小的误差也可能被注意到——这是做 LOD 和几何压缩时要牢记的。
*   **LOD 切换边界要"抖动"**：仿照 SSAO 采样半径做 jitter 的思路，让每层 LOD 被锁的边界都变化，避免人眼盯住一个固定的高频 boundary。

### 3. 性能分析与硬件发展趋势
*   **小三角形时代硬件光栅化的浪费**：硬件为计算 ddx/ddy 至少光栅化 2×2 pixel，配合 4×4 tile 预检测的 skyline 优化在小三角形时代效率极低。Nanite 用 compute shader 软件光栅化快 3 倍。
*   **Overdraw 瓶颈随三角形尺寸迁移**：调优 Nanite 性能时先判断当前场景三角形尺寸处于哪个区间——小三角形看 vertex transform / triangle setup，中等看 coverage，大三角形看 64 位深度原子操作（atomic bound）。
*   **BVH 带来的量级收益**：600 万三角形 → 11 万 cluster → 只 check 107 个 BVH 节点 + 4000 多个 cluster → 最终可见约 2000 多个 cluster（约 20~30 倍削减）。**没有 BVH，并行 LOD selection 在实战中效率很低**。
*   **对未来的判断**：软件光栅化和 64 位深度打包这类"hack"很可能是过渡方案；NVIDIA/AMD 极可能在硬件上原生支持（micro mesh 可能是硬件化的软件光栅化）。引擎团队应关注硬件演进，避免在注定被硬件取代的方向上投入过多。
*   **点光源是性能大坑**：在虚幻引擎中放一个点光源会生成 6 个 16K×16K 的 virtual shadow map，开销惊人——**少用点光源**。

### 4. Virtual Shadow Map 的工程使用建议
*   **尽量让主光不动**：光一旦移动，所有 shadow map 都要重新生成；VSM 的巨大优势（缓存复用）依赖光源静止。这也是 UE5 官方 demo 总是"一道光直直射下来"的原因。
*   **相机移动时 shadow 更新开销很小**：平滑移动只更新部分 tile，很多 tile 可复用——课程组实验显示移动相机时只有少量红色 tile 需要更新。
*   **VSM 质量与稳定性优于 CSM**：shadow 分辨率与视空间高度匹配、无 CSM 层级过渡的 popping；与 Nanite 结合自然，很可能成为下一代主流 shadow 方案。

### 5. 课程团队工程实践方法论
*   **尊重艺术家管线**：选择表达方式时，除了算法优劣，更要考虑对现有工作流的兼容性（体素方案因此被淘汰）。
*   **并行化优先**：现代 GPU 并行能力极强，把树遍历拍平成列表、让每个节点独立决策，是 Nanite 性能的关键。
*   **传统方法不丢**：imposter、CSM 等经典技术在 Nanite 时代依然有实战价值；新引擎不应盲目抛弃旧技术。
*   **压榨硬件性能**：Nanite 团队把当代硬件性能压榨到极致，是学习高性能编程的绝佳案例。
*   **工程妥协与边界**：Nanite 目前只解决静态几何，动态角色/载具仍需传统管线；商业级引擎必须考虑与 deferred pipeline 的混合渲染。

### 6. Q&A：课堂问答实录
*   **Q1：Nanite 这种"无限精度、无极渐变"的几何表达方式，会成为未来几何表达的主流吗？**
    *   **A**：确实非常 promising，很有可能；但目前有几种不同流派在 compete。
    *   Nanite 本身做了大量工程妥协，算法非常复杂，对 **skinned geometry（蒙皮/骨骼动画几何）** 和**动态几何**难以表达。
    *   但它的确让游戏第一次出现了**实时的 cinematic 级别几何细节**。
    *   未来随着硬件发展，可能出现更简洁、更 elegant 的方法成为主流。观察引擎行业过去几十年的发展：**一个新思想出现后，要经过好几代开发者共同迭代、形成共识，才沉淀为一代成熟的 pipeline**（例如 deferred shading 就是经过多代迭代才成熟）。
    *   硬件厂商也在疯狂努力（micro mesh 等硬件加密流派），**"两条腿"谁跑得更快，未来几年会看到精彩的你追我赶**；现在断言"大局已定"为时尚早。
*   **Q2：Nanite 的应用空间是否不止游戏领域？**
    *   **A**：答案一定是 yes。
    *   用游戏引擎做的渲染已能逼近影视级需求：**虚拟拍摄**使用 Nanite 技术制作巨大的 LED 屏（上亿像素），绘制出极其真实的山和水，演员直接在 LED 屏前表演、一起拍摄，效果如同实景。
    *   在影视、游戏之外的领域，如**电影、智慧城市、建筑的光照仿真、自然场景表达**等，很多场景都需要 Nanite 这样的技术。

### 7. 课程结语
*   Games104 整个课程到此结束（本节是最后一课）。老师总结课程初衷："每一个想做引擎的同学，他的心里都是有光的"，希望把这份光和热爱传递给更多不肯放弃的人，鼓励大家敢于构建自己的世界、探索技术最前沿。
*   参考资料方面，Nanite 的公开资料并不多，课程组大部分内容靠**阅读源代码**得出。

---
