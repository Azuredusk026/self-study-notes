# Houdini 程序化树木、PDG 批量生成、LOD 与地形物件材质

## 一、核心知识点与原理剖析

### 1. Labs Tree 程序化树木系统

#### 1.1 核心节点与树干生成

- 在 SOP 中使用 SideFX Labs 的 `Labs Tree` 系列节点。
- 主要节点：
  - **Labs Tree Controller**：统一控制整棵树的重力、向上弯曲、整体噪声、网格精度和随机裁切；不是必需节点。
  - **Labs Tree Trunk Generator**：生成主干，是最核心的起始节点。
  - **Labs Tree Branch Generator**：在父级曲线上生成分枝。
  - **Labs Tree Leaf Generator**：把叶片几何附着到末级枝条。
  - **Labs Tree Simple Leaf**：快速生成单片叶形。
- Tree Trunk 的内部逻辑可理解为：先生成中心曲线，再沿曲线逐圈 Sweep/扫描出网格。

#### 1.2 Tree Trunk 主要参数

- 主干半径、长度、弯曲位置与弯曲幅度可调。
- Root 参数控制树根形态、旋转与扭曲范围。
- **Line Noise** 作用于中心曲线，改变树干整体走向。
- **Mesh Noise** 作用于网格表面，形成树皮凹凸。
  - 默认 X、Z 方向频率约为 Y 方向的 10 倍，使噪声沿树干方向拉长，更接近纵向树皮。
- Meshing：
  - `End Caps` 控制末端封口及顶部网格。
  - `Resolution` 控制沿树干长度方向的环数。
  - `Divisions` 控制每个截面圆环的边数。
  - 还可使用外部 Displacement Map，但本课未采用。

#### 1.3 分枝的植物学分布逻辑

- Tree Branch Generator 的左右输入都要连接父级相应输出，以同时传递网格与生长曲线数据。
- 分枝可按固定数量生成，也可按沿父枝的间距生成。
- 分枝不是完全随机，而是每生长一根后绕父枝旋转固定角度。
- 默认约 **137.5°**，接近植物叶序中常见的黄金角，能形成自然且不易重叠的分布。
- 常用 Branching 模式：
  - `Alternate`：枝条交替生长，真实树木常用。
  - `Opposite`：每个节点在相对方向成对生长。
  - `Radial`：同一层绕一圈同时长出 3、4、5 根等。
  - 90°：容易形成四向、菱形或松树式层级外观。
  - 180°：通常只适合特殊植物，普通树木较少采用。
- 同种植物各层分枝角度通常应保持规律，因为分枝模式来自同一套生长规则；可叠加适量 `Angle Variation` 打破机械感。
- 可用 Ramp 控制枝条沿树高的长度、半径和上下夹角。例如底层略短、中层较长、顶部收拢。

#### 1.4 Prune 与 LOD 准备

- `Prune` 可按以下条件删除分枝：
  - 向上或向下角度。
  - 根部生长角度。
  - 末端角度。
  - 随机百分比。
- 随机裁枝最适合远距离 LOD；应优先裁末级小枝，不能轻易裁主干和一级枝条，否则轮廓会突然破坏。

### 2. 叶簇卡片：把几何复杂度烘焙到贴图

#### 2.1 为什么不能每片叶子都建模

- 直接把 Simple Leaf 挂到三级枝条后，课堂模型一度达到约 **120 万面**；降低末级分辨率后仍约 **50 万面**，实时项目不可接受。
- 参考预算：
  - 极近、占据屏幕很大的树约不超过 5 万面。
  - 一般近景约 1–2 万面。
  - 中景约几千面。
  - 远景约几百到一千面。
- 解决方案是把最后两级小枝和真实叶片烘焙成一张带透明度的叶簇贴图，再把贴图放到少量 Grid 卡片上。

#### 2.2 叶簇几何与贴图制作

- 用一个低细分 Grid 代表一簇末级枝叶；若需要立体感，可把两个 Grid 垂直交叉成十字卡片。
- 卡片通常只需 1–3 个纵向分段；若不做风动弯曲，甚至可降为单个四边面。
- 单独新建树枝网络：Trunk + 两级 Branch + Simple Leaf + Leaf Generator。
- 调整原则：
  - 末级枝条数量约 4–5 根作为课堂起点。
  - 叶序使用 137.5°，比 180° 左右交替更杂乱自然。
  - 增大叶片尺寸和间距，尽量让画面覆盖均匀。
  - 用 Controller 或角度 Ramp 让枝叶向上弯，避免落到 0 高度以下后被裁掉。
- 用 **Maps Baker** 从合适视角烘焙：
  - Base Color。
  - Alpha/Opacity。
  - Height。
  - World Space Normal（课堂中直接试用后可改善叶簇立体感）。
- 烘焙时软件多次崩溃，但输出图片仍成功写出；应先检查结果文件，再判断是否需要重算。

#### 2.3 UV、材质预览与卡片装配

- Grid 没有合适 UV 时使用 **UV Project**，课堂明确初始化到 `ZX Plane`。
- 通过 **Quick Material** 在 Houdini 中预览颜色与透明度；Quick Material 不能直接成为 Unity 最终材质，但 UV 可以导出。
- 叶簇根部应向枝干内部插入，避免卡片底部空白或枝条根部露在外面；移动几何后也要检查 UV 投影位置。
- 双卡片方案：复制 Grid，绕 Z 轴旋转 90°，再 Merge。
- 完整树在课堂优化后约 **2.5 万面**，使用 **ROP FBX Output** 导出。

### 3. Unity 叶片 Shader 与植被着色

#### 3.1 Alpha Clipping 而非透明混合

- 叶片卡片应使用 **Opaque + Alpha Clipping**，不应直接使用 Transparent：
  - Transparent 容易产生前后排序错误和穿插问题。
  - Alpha Clip 通过阈值直接丢弃透明像素，深度写入和排序更稳定。
- 课堂阈值由 0.5 调高到约 **0.75** 以减少黑边，实际值应随贴图调整。
- 叶片需要双面可见，但课堂所用 URP 与 ASE 双面模式的背面法线表现异常。
  - 最终在 Houdini 中复制叶片面，使用 **Reverse** 翻转面朝向，再 Merge。
  - 代价是叶片面数翻倍，但只增加约 3000 面，仍可接受。

#### 3.2 Amplify Shader Editor 叶片材质

- 建立 Universal Lit Shader，并启用 Alpha Clipping、Transmission、Translucency。
- 基本连接：
  - Base Color 贴图 → Albedo。
  - 独立 Alpha 贴图 → Opacity/Alpha Clip。
  - Normal 贴图采样时启用 `Unpack Normal Map`。
  - Metallic 固定为 0。
  - Smoothness 暴露为参数。
  - AO 初始可设为 1。
- 树叶不是完全不透明物体，逆光观感来自透射和次表面式散射：
  - `Transmission` 可近似理解为光穿过薄叶片后的方向性透射。
  - `Translucency` 控制背面透亮与散射表现。
  - Transmission/Translucency 颜色应与 Base Color 相乘；枝条本身不应获得叶片透射，精细流程应有独立遮罩。
- ASE 切换到 **Specular Workflow** 后，高光颜色可直接控制：
  - Metallic 流程下叶片高光容易偏灰。
  - Specular 流程可得到更自然的偏白高光，并允许适量 Smoothness。

#### 3.3 假 AO 与阴影

- 树冠内部应比外部暗，可用对象空间片元位置到树冠中心的距离制作假 AO。
- 暴露参数：`AO Distance` 与 `AO Min`；将距离重映射为由中心向外的环境光权重。
- 必须使用片元的 **Position**，不是 Object Position；后者只是整个物体枢轴位置。
- 枢轴若位于树根，径向 AO 会从地面开始变化，因此叶簇最好拆成独立对象并把 Pivot 放到树冠重心。
- URP 默认 Shadow Distance 约 50，阴影图精度过高时叶簇内部会显得又黑又硬。适当增大 Shadow Distance 会降低单位范围内精度，反而让树叶阴影更柔和。
- 更完整方案是在自定义光照模型中偏移阴影采样位置，但本课为了效率只调整全局阴影距离。

#### 3.4 顶点色随机化

- 所有叶簇共用同一张贴图，颜色完全一致会暴露卡片重复。
- 在 Houdini 中暂时断开树干网格传递，使叶片可以单独处理，再使用 **Attribute Randomize** 随机化 `Cd`。
- 可分别随机：
  - 轻微 RGB 差异，形成少量色相变化。
  - 约 `0.7–1.0` 的亮度，再通过 Attribute Combine 与颜色相乘。
- Merge 回树干后，在 Shader 中把 Vertex Color RGB 乘到 Albedo，即可得到每簇略有差异的颜色。

### 4. PDG/TOPs 批量生成树木变体

#### 4.1 Wedge 工作项

- 程序化模型的价值不只是生成一棵树，而是批量生成一组合理变体。
- 切换到 **Tasks/TOPs（PDG）网络**，增加 Task Graph Table 查看工作项。
- 使用 **Wedge** 节点生成多个任务，每个 Work Item 对应一组参数。
- 可在 Wedge 中增加整数或浮点属性，例如：
  - `seed`：随机种子。
  - `first_level_branch_count`：一级枝条数量，课堂示例范围约 6–10。
- Houdini 参数中用 `@wedgeindex` 或 `@属性名` 读取当前工作项数据。
- `wedgeindex` 本身就是 0、1、2……的索引，可直接作为随机种子。

#### 4.2 ROP Fetch 与并行导出

- 使用 **ROP Fetch** 指向模型网络中的输出 ROP，让每个 Wedge 工作项触发一次导出。
- 文件名必须拼接工作项索引，否则每次会覆盖同一文件：

```text
tree_`@wedgeindex`.fbx
```

- 课堂先生成 10 个，随后演示 40 个树模型。
- `Local Scheduler` 决定并行数：
  - 可设为 CPU 核心数的 1/4，减少内存压力。
  - 也可设为核心数减 1；12 核机器约同时运行 11 个任务，但资源压力显著增大。
- 生成任务可在 TOP 图中取消；修改参数后使用 Dirty and Cook 重新计算。

### 5. Houdini Engine for Unity、材质属性与 LOD

#### 5.1 插件版本必须匹配

- Houdini Engine for Unity 必须使用当前 Houdini 安装目录自带的 Unity Package。
- 不建议从 Asset Store 或网络随意下载其他版本，否则很可能无法连接本机 Houdini Session。
- 常见路径位于 Houdini 安装目录的 `engine/unity` 下，可用 Everything 快速搜索 Unity Package。
- 老 Houdini 与新 Unity 组合可能出现 API/序列化报错，课堂临时移除了不兼容的 `SerializeFile` 相关声明；正式项目应优先安装匹配版本。

#### 5.2 BGEO 与自动材质

- 为走 Houdini Engine 流程，批量输出从 FBX 改为 **ROP Geometry Output** 的 `.bgeo`。
- Houdini Engine 支持特殊属性 `unity_material`，其值是 Unity 项目中的材质路径。
- 叶片与树干应在 Primitive 级分别创建字符串属性：
  - 叶片指向 Leaf Material。
  - 树干指向 Trunk Material。
- Unity 资产路径可在 Inspector 中 `Copy Path`，避免手输错误。
- 该属性在 Houdini 视口只表现为字符串，导入 Unity 后才自动绑定材质。
- 课堂所用旧版插件无法方便地一次导入全部 BGEO；单个 Load File 后还需 Bake 为 Prefab。真正批量导入通常需要 HDA 或 Unity Editor 脚本。

#### 5.3 LOD 组输出

- 用 Primitive Group 命名 `LOD0`、`LOD1`、`LOD2`，Houdini Engine 可据此生成 Unity LODGroup。
- 课堂层级：
  - `LOD0`：完整模型，约 2.4 万面。
  - `LOD1`：降低各级树干 Resolution/Divisions，约 1 万面。
  - `LOD2`：进一步降树干精度，随机裁掉约 1/3–1/2 末级枝叶，并适当放大叶簇补偿轮廓，约 5800 面。
  - `LOD3` 理论上可把整树烘焙成单张 Billboard/Grid，但涉及自动烘图、生成材质和脚本，本课未展开。
- LOD0 → LOD1 外观变化小，可以较早切换；LOD2 改变了叶片分布，应在更远处切换。
- Unity 可使用 `Cross Fade` 减少突变，Fade 宽度课堂约 **0.3**。
  - 前两级几何较重，同时渲染会增加成本，可不启用 Cross Fade。
  - 后级模型较轻，适合渐变。
- `lod_screensizes` 等 Detail 属性可在 Houdini 指定屏幕比例阈值；Cross Fade 等导入后配置通常仍需要人工或后处理脚本。

### 6. HDA 地形物件：悬崖、洞穴与岩块

#### 6.1 为什么需要地形物件

- Terrain 无法良好表达陡直悬崖、洞穴和悬挑结构，因此场景中大量结构来自独立 Mesh。
- 关卡策划可先在 Unity 用多个 Cube/Sphere 搭白盒，HDA 再把这些输入快速加工为自然岩体。

#### 6.2 几何处理链

- 对旋转、拼接且拓扑不规则的输入，不要用只沿原面切分的 Subdivide；应使用 **Remesh** 统一重拓扑。
- 课堂流程：
  1. 多个 Box 输入。
  2. Boolean `Union` 合并。
  3. Remesh，示例 `Target Size ≈ 1`。
  4. Smooth 消除硬角。
  5. Mountain/Attribute Noise 塑造大形。
  6. 再次 Remesh、Boolean Union，消除噪声造成的自相交。
  7. Triangulate 标准化网格。
  8. 最后 Smooth。
- 噪声尝试：
  - 大尺度 Perlin/Worley 向外推基础轮廓。
  - Sparse Convolution 增加第二层细节。
  - Worley F1/F2-F1 作为块状补充。
  - `Zero Center` 会同时向内外位移，容易造成收缩、自穿插；原型阶段更适合主要向外推，再调整整体位置。
- 两层 Mountain 之间可插入 Remesh + Boolean，降低自相交风险。
- **Mesh Sharpen** 可迭代约 50 次恢复被 Smooth 过度软化的特征，但噪声尺度与强度仍需反复美术调参。
- 将流程打包为 Subnet，再用 `Create Digital Asset` 生成 HDA。Unity 中通过 `Add Slot` 把多个白盒物件作为输入。

### 7. 地形物件的顶点色遮罩与三向采样

#### 7.1 生成 Grass/Rock 权重

- 正式流程常在 Substance Painter 绘制 Mask；课堂因 Painter 许可故障，改用顶点色。
- 按表面法线方向建立 Group，把朝上的面选为草地候选区域。
- 创建 Float Attribute `grass`：组内为 1，组外默认 0。
- 用 **Attribute Blur** 模糊边界。
- 建立互补权重：`rock = 1 - grass`。
- 在 Point Wrangle 中写入顶点色：

```c
v@Cd = set(f@grass, f@rock, 0.0);
```

- R 通道表示 Grass，G 通道表示 Rock，Shader 中按顶点色混合材质。

#### 7.2 Triplanar 原理

- 普通平面投影在陡直表面会被严重拉伸。三向采样分别用世界空间位置的三个二维分量采样：
  - YZ 平面纹理由法线 X 权重控制。
  - XZ 平面纹理由法线 Y 权重控制。
  - XY 平面纹理由法线 Z 权重控制。
- 权重取世界空间法线分量绝对值，并用 Power 调整交界锐度：

```text
w = pow(abs(NormalWS), Falloff)
color = (sampleYZ * w.x + sampleXZ * w.y + sampleXY * w.z)
        / (w.x + w.y + w.z)
```

- `Falloff` 小，三个投影交界较柔；数值大，分区更硬，可能出现接缝。
- `Tiling` 乘到 World Position 上，控制纹理密度。
- ASE 已有 Triplanar 节点，课堂在手动推导原理后改用内置节点，避免重复搭建大量连线。
- Grass 与 Rock 的 Albedo、Normal 分别三向采样，再乘 R/G 顶点权重后相加。
- 如果权重未预先互斥，应除以 R+G 做归一化；本课在 Houdini 中已令 `rock = 1 - grass`。
- 每层 Normal 强度应独立控制，混合后再 Normalize。

## 二、重点术语与概念解析

- **SOP**：Surface Operator，Houdini 中处理几何体与属性的节点网络。
- **Tree Controller**：统一覆盖多个 Tree 节点参数的全局控制器。
- **Golden Angle（黄金角）**：约 137.5°，植物叶序中常见的旋转角，可减少枝叶遮挡。
- **Leaf Card / Leaf Cluster（叶片卡/叶簇卡）**：把多片叶与小枝烘焙到透明卡片，以少量面数替代大量真实几何。
- **Alpha Clipping**：低于阈值的像素直接丢弃，适合树叶、草和铁丝网。
- **Transmission / Translucency**：薄物体透光和散射的近似着色能力。
- **PDG/TOPs**：Houdini 的依赖图与任务调度系统，用于批处理、参数变体和并行导出。
- **Wedge**：为多个 Work Item 生成不同参数组合的节点。
- **ROP Fetch**：在 TOPs 中调用指定 ROP 输出节点的任务节点。
- **BGEO**：Houdini 原生几何格式，可保留组、属性和 Houdini Engine 元数据。
- **HDA**：Houdini Digital Asset，把节点网络封装成可复用、可暴露参数、可在 Unity 中执行的数字资产。
- **LOD**：Level of Detail，根据屏幕占比切换不同复杂度模型。
- **Vertex Color / Cd**：储存在顶点上的 RGBA 数据，常被用作材质混合遮罩。
- **Triplanar Mapping**：从三个轴向投射并混合纹理，避免没有 UV 或陡坡表面的拉伸。

## 三、工程经验与避坑指南

### 1. 面数、卡片与 LOD

- 枝条层级每增加一级都会指数级增长，三级真实叶片很容易达到百万面；应尽早确定哪一级改为烘焙卡片。
- LOD 不只是整体 Decimate：远景先降低圆环边数和纵向分段，再裁末级枝叶，保留主轮廓。
- Alpha Clip 阈值在远处会因 Mipmap 让叶簇逐渐变细甚至消失；远距离 LOD 可能需要降低阈值、使用 Alpha Coverage 或专门的植被 Mipmap。
- Cross Fade 会同时绘制两个 LOD，视觉更稳但会增加过渡区开销。

### 2. 法线、双面与导入比例

- 不要假设 URP/第三方 Shader 的 Double-Sided 一定正确翻转背面法线；应在目标版本中实际检查受光方向。
- 若无法可靠修正 Shader，可复制面并 Reverse，换取稳定法线，代价是面数和顶点处理翻倍。
- Houdini FBX 导入 Unity 后比例过小时，课堂临时关闭了 `Convert Units`。正式管线应统一 Houdini 与 Unity 的单位和 FBX 导出设置，避免每个资源手调。
- Quick Material 只供 Houdini 预览；最终材质必须在 Unity 重建或通过 `unity_material` 自动引用。

### 3. 植被着色的常见错误

- 树叶不要使用普通 Transparent 混合，否则深度排序会在叶片互相穿插时暴露问题。
- 枝干不应共享叶片 Transmission；高质量叶簇贴图应提供专门遮罩区分枝与叶。
- 基于对象空间距离的 AO 强依赖 Pivot；枢轴不在树冠中心时会产生错误渐变。
- 用世界空间法线烘焙图直接作为切线空间法线理论上存在空间不匹配风险。课堂中视觉上可用，但正式项目应明确做空间转换或从 Height 重建切线空间 Normal。

### 4. PDG 与 Houdini Engine 管线

- 批量导出时文件名必须含 `wedgeindex` 或其他唯一属性，否则任务会互相覆盖。
- 并行数越高不一定越快：树生成、贴图和 Houdini Session 都可能吃大量内存；应按机器资源选择 Local Scheduler 并行度。
- Houdini Engine 插件和 Houdini 主程序版本必须匹配；旧插件强行适配新 Unity 会产生编译和序列化问题。
- BGEO 保留的数据丰富，但课堂版本无法无脚本批量导入、Bake Prefab 和配置 Cross Fade。工业化需要 Unity Editor 后处理脚本或专门 HDA 导入工具。

### 5. Triplanar 与移动端性能

- 单层三向采样至少需要三个纹理样本。四层 Albedo 就是 12 次；再叠 Normal、Mask，带宽和采样次数会快速增长。
- 因此三向多层混合适合 PC/主机地形物件，手机端通常不能直接照搬。
- 顶点色只有 RGBA 四个通道，最多方便地控制四层，而且顶点色还可能需要存 AO、曲率、风动等数据。
- 更灵活的方法是绘制 256×256 或 512×512 的 Mask Texture：一张 RGBA 提供 4 层，四张可提供 16 个通道，但精度、显存和采样成本要平衡。

### 6. TA 项目职责与课程总结

- 集训或短周期 3D 项目中，TA 最重要的贡献往往是让场景达到“正常可用”的完整状态：
  - 配好 UV、纹理和材质。
  - 烘焙或布置 Reflection Probe、Light Probe、全局光照。
  - 完成常见游戏提示效果、特效和场景整合。
- 2D 项目同样有 TA 工作：URP 2D 法线、分层场景、体积粒子、2D 素材拼 3D 空间、UI/Sprite Shader 等。横版场景更容易用 2D 素材营造深度；俯视角受透视影响，常更依赖真实 3D 模型。
- AI 生成 Albedo、Normal 与概念素材已经成为 TA 工作的一部分，但仍需人工检查无缝性、通道物理正确性、脏点和法线方向。
- 对短周期 Low Poly 项目，HDA 可把白盒关卡快速转换为统一风格资产，通常比不熟练的手工建模更高效。
