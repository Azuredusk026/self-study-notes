# Houdini 高度场地形、侵蚀分层与 Unity 地形材质全流程

## 一、核心知识点与原理剖析

### 1. 高度场地形的本质与工具选择

- **地形（Terrain）本质上是一张高度图（Height Map）**。引擎把二维图像中每个像素的灰度解释为对应位置的高度，再用规则网格或四叉树组织的网格绘制出来。
- 传统高度场只能描述每个水平坐标上的一个高度，即只有竖直方向的位移，不能表示悬挑、倒扣、洞穴顶部或同一位置存在多个表面的复形结构。
  - Unity Terrain 与传统 Unreal Landscape 都属于这一类。
  - 洞穴、悬崖、桥洞等结构通常要靠独立三维模型覆盖或与地形洞配合完成。
- Houdini 的侵蚀算法和程序化组合能力较强，出结果快且能够覆盖完整流程；World Creator、World Machine 等专用地形软件在特定操作上可能更方便。

### 2. HeightField 的建立与基础塑形

#### 2.1 HeightField 初始设置

- 在 SOP 网络中创建 **HeightField**。
- 课堂使用的物理范围保持默认 **1000 × 1000**，不要随意修改；后续与 Unity、Houdini Engine 或项目世界尺寸对接时，这个尺寸具有实际意义。
- HeightField 在视口中虽然以立体表面显示，内部仍然主要是二维栅格层。

#### 2.2 HeightField Noise

- 使用 **HeightField Noise** 生成基础山形。
- 默认的 `Hybrid Terrain` 是专门面向地形的组合噪声。
- `Center Noise` 会让噪声同时向正负方向变化，因此地形可能低于海平面；关闭后通常只向上堆积。
  - 制作初始地形时常关闭 `Center Noise`。
  - 若后续导出会做归一化，出现负高度并非绝对错误，本质上可以整体抬升。
- 课堂尝试的噪声类型：
  - **Worley F2 - F1**：适合作为丘陵、连续山地区域的基础。
  - **Worley Cellular F1**：适合高原、高山山脉等较大块结构。
  - **Perlin**：适合补充较自然、连续的小尺度起伏。
- 噪声通常分层叠加：先建立大形，再用更小的 `Element Size`、较低的 `Amplitude` 和更高的 `Roughness` 增加细节。不要让单个噪声同时承担所有尺度。

#### 2.3 HeightField Project：可控形状投影

- 仅靠噪声很难精确控制“哪里高、哪里低”，因此应使用 **HeightField Project** 把三维几何体投影到高度场。
- 左侧输入地形，右侧输入待投影几何体，例如 Sphere 或 Box。
- 节点从高度场下方向上发射射线取得几何体表面高度，可使用 `Maximum`、`Minimum`、`Add`、`Multiply`、`Replace` 等方式与原高度合并。
- 典型用途：
  - 用压扁的 Sphere 形成丘陵或湖盆基础。
  - 用旋转后的 Box 制作斜坡、三角形山体或人工控制的山脊。
  - 先抬高一块平台，再投影较小形状向下扣出山顶湖。
- **投影形状不能依赖朝下的表面表达悬挑**。HeightField 只能保留一层高度，Box 的负面或倒扣部分不会得到正确的实体结构。

#### 2.4 Blur、Distort 与 Mask

- **HeightField Blur**：给投影后过硬的边缘增加过渡，使地形不再像直接切出的几何体。
- **HeightField Distort / Distort by Noise**：用噪声改变二维采样位置，从周围采样高度，适合把规则的山体轮廓扭曲成自然边界。
  - 可先对基础大形做一次低强度 Distort，再增加表面噪声。
  - 山体细节阶段可再叠一次默认强度附近的 Distort。
- **HeightField Mask by Height**：按高度范围建立遮罩。
  - `Compute Range` 会读取当前地形最低点与最高点，自动填写范围。
  - 渐变条决定各高度受影响的强弱。
- 当某个 HeightField 节点需要读取遮罩时，必须把含有 `mask` 层的高度场正确接入相应输入；遮罩可先单独生成，再与 Terrain 一同接回目标节点。

### 3. HeightField Erode 自然侵蚀

#### 3.1 侵蚀模拟内容

**HeightField Erode** 模拟降雨、流水、冷热风化和重力搬运，产生多个可继续处理的栅格层：

- `height`：侵蚀后的高度。
- `water`：水流或积水区域。
- `debris`：崩落的碎石、砂砾和风化土块。
- `sediment`：水流搬运并沉积的泥沙。

可以在节点的 `Visualization` 中分别查看这些层。

#### 3.2 帧迭代与冻结

- Erode 按 Houdini 时间轴逐帧迭代。刚连接节点时效果可能不明显，向后播放帧数会持续侵蚀。
- 静态地形不需要真正播放动画，应启用 **Freeze at Frame**，通常使用约 **20–40 帧**的结果。
- 修改侵蚀参数后点击 **Reset Simulation**，否则可能继续沿用旧缓存。
- 网格精度会改变模拟结果；改变 `Grid Spacing` 后必须重新模拟。
  - `Grid Spacing = 1` 可提高栅格精度。
  - 精度越高，河沟也会越细，计算更慢，而且过细的侵蚀细节未必适合实时地形。

#### 3.3 关键参数

- `Hydro`：水力侵蚀部分。
- `Thermal`：热力风化、岩石崩解部分，并不是“岩浆节点”。
- `Erosion Rate`：侵蚀总体倍率；提高后沟槽更深。
- `Bank Angle`：河岸或河床允许的角度，数值较小会使河道更宽。
  - 实时地形常用约 **20°–40°**。
  - 约 70° 往往显得过硬、过假。
- 对河道、湖泊位置有明确设计要求时，应先通过投影或遮罩塑形，再交给侵蚀模拟自然细化，不能只依赖随机噪声。

### 4. 从侵蚀结果制作地形材质分层遮罩

#### 4.1 Mask 中转工作流

- 旧工作流中很多 HeightField 操作只方便处理 `mask` 层，因此常用 **HeightField Layer Combine / Combine Layers**：
  1. 把 `water`、`sediment`、`debris` 等目标层 Copy 到 `mask`。
  2. 对 `mask` 执行 Blur、Expand、Shrink、Sharpen、Noise、Remap 等操作。
  3. 再把处理后的 `mask` Copy 回原层或新层。
- 新版部分节点可直接指定其他 Layer，但 Mask 中转方法仍然便于统一流程。
- `Visualizer` 应放在流程末端，用纯黑底分别检查每一层。

#### 4.2 数值范围与边缘处理

- Erode 产生的层数值可能远大于 1，但 Visualizer 中看起来都只是白色；Blur 或 Expand 会让这些大值继续扩散，导致遮罩范围失控。
- 因此在关键操作前后要用 **Remap** 充当 Clamp，把层重新限制到 `0–1`。
- `Expand` 不只扩大边缘，也可能叠高中心值；必要时每次 Expand 后再次 Remap。
- 高分辨率 PBR 地形不适合大面积柔软灰边。灰边叠加纹理后会产生不自然的“糊成一片”，通常应：
  1. 给边缘加入 Mask Noise。
  2. 用 Remap 截取并重新锐化过渡。
  3. 通过 `Octaves` 提高边缘细节，而不是只留平滑渐变。

#### 4.3 各层生成规则

- **Water（水层）**：从 `water` 层开始，可 Blur 填补断裂，适当拓宽河床，并把结果重新限制到 `0–1`。
- **Debris（碎石层）**：来自 `debris`，课堂中曾用 `Shrink = 2` 收缩约两个像素，控制碎石覆盖量；边缘可叠噪声后 Remap。
- **Sediment / Grass（土壤或草地层）**：
  - 从 `sediment` 层展开覆盖范围。
  - 使用 **HeightField Mask by Feature** 按坡度筛选，移除陡坡上的草。
  - 再按高度限制，课堂示例把约 60 高度以上区域排除。
  - 将坡度、高度遮罩与沉积层相乘，再叠加边缘噪声。
- **Ice / Snow（雪层）**：
  - 只按固定高度会得到整齐的水平切线，效果僵硬。
  - 更合理的方法是结合高度与 Occlusion/峰顶特征提取高处，再 Expand、Blur、Noise、Remap，生成不规则雪线。
  - 太陡的坡面可用坡度进一步排除，但课堂最终认为单纯强坡度限制未必必要。
- **Bedrock（基岩）**：作为最底层，通常等于没有被上层遮罩覆盖的剩余区域。

### 5. 高度图与 Splat Map 导出

#### 5.1 HeightField Output

- 使用两个 **HeightField Output**：一个导出侵蚀后的高度，一个导出材质层遮罩。
- 高度必须来自最终 Erode 结果，不能继续使用侵蚀前的旧高度图。
- 高度输出启用 `Auto Remap`，将有效高度归一化。
- 课堂使用：
  - 高度图输出约 **2048 × 2048**。
  - 图层遮罩为与 Unity Terrain 数据匹配而使用 **2049 × 2049**。
- 高度图可直接使用 **EXR** 等高精度格式，避免旧式 PSD → RAW 工作流；关闭不需要的 Mipmap。
- 四个材质遮罩可打包到 RGBA：
  - R：Grass/Sediment。
  - G：另一材质层，课堂按当前组织映射为 Sediment 等。
  - B：Water。
  - A：Debris。
- **EXR 在本次流程中没有得到所需 Alpha 通道，因此含 RGBA 的 Splat Map 最终改用 PNG**。
- 输出各层时关闭自动 Remapping，避免遮罩之间的相对关系被再次改变；同时锁定与 Erode 相同的冻结帧。

#### 5.2 Unity Terrain 导入

- 通过 Terrain Toolbox 从高度图创建 Terrain；导入分辨率按 Unity 的合法高度图尺寸使用 **2049**。
- 创建 Terrain Layer：`Bedrock`、`Debris`、`Sediment/Grass`、`Water`、`Snow/Ice`。
- 每个 Terrain Layer 可包含：
  - Diffuse / Base Color。
  - Normal。
  - Mask Map。
- Unity Terrain 的 Mask Map 通道：
  - R：Metallic。
  - G：Ambient Occlusion。
  - B：Height。
  - A：Smoothness。
- 导入设置：
  - Normal 纹理设为 `Texture Type = Normal Map`，并关闭 sRGB。
  - Mask Map 关闭 sRGB，因为其通道存的是线性数据而非颜色。
  - Splat Map 关闭 sRGB、关闭压缩，并启用 Read/Write（工具预览或读取需要时）。

#### 5.3 Unity 各层不会自动“上层覆盖下层”

- Unity Terrain 的权重是归一化混合，不会像图层软件一样自动用雪盖住草、用草盖住基岩。
- 如果直接导入彼此重叠的遮罩，水、草、碎石、雪会一起相加，基岩层也可能消失。
- 应在 Houdini 中预先按优先级处理：**下层减去所有上层**。
  - 最上层无需减。
  - 每个更低层依次减去上方遮罩。
  - Bedrock 由 `1 - 所有上层权重` 得到。
- 完成互斥处理后再把通道打包成 Splat Map，才能得到稳定的 Terrain Layer 权重。

### 6. Substance Designer 制作 Terrain Layer 材质

- 分别制作 Bedrock、Sediment、Debris、Water、Snow 的 Base Color、Normal 和 Mask。
- 使用 **RGBA Merge** 打包 Mask Map：Metallic、AO、Height、Smoothness。
- Designer 输出通常是 Roughness，Unity 需要 Smoothness，因此使用 `1 - Roughness` 或 Levels 反相后写入 Alpha。
- 基岩和土石通常 `Metallic = 0`，Roughness 较高；课堂初始粗糙度约 0.8。
- Designer 推荐切换英文界面：高级节点和资料通常使用英文名，中文界面只翻译部分菜单。
- 课堂展示的进阶程序化材质方法包括：
  - `Splatter Circular Grayscale`：环形或放射状分布石块。
  - `Multi Directional Warp Grayscale`：沿多个方向扭曲轮廓。
  - `Slope Blur Grayscale`：用噪声侵蚀或切碎边缘。
  - `Scratches Generator`：增加划痕、裂纹。
  - `Crystal`、`Polygon 2`、Gradient、Blend、Transform 2D：构造石块基形及方向性变化。
- Debris 可从单块鹅卵石高度开始，改变种子和尺寸随机性后分布；若只用一层，密度与重复感需要仔细平衡。
- Bedrock 可用多边形/金字塔基形乘 Gradient，再经 Warp、Slope Blur、噪声和环形分布形成片状岩壁。

## 二、重点术语与概念解析

- **HeightField（高度场）**：二维规则网格，每个像素只保存一个高度值，是传统实时地形的数据基础。
- **Height Map（高度图）**：灰度表示高度的图像；Unity 会据此生成 Terrain 网格。
- **Grid Spacing（栅格间距）**：高度场相邻样本的物理间距，越小表示分辨率越高、模拟成本越大。
- **HeightField Project**：把三维物体沿竖直方向投影成高度层的节点。
- **Erosion（侵蚀）**：模拟水流、风化和沉积对地形的长期改造。
- **Debris**：崩落并堆积的碎石、砂砾或土块。
- **Sediment**：被水流搬运并重新沉积的细颗粒泥沙。
- **Mask by Feature**：按高度、坡度、遮蔽度、曲率等地形特征生成遮罩。
- **Remap / Clamp**：重映射数值范围；本课常把任意范围重新限制到 `0–1`。
- **Splat Map**：用 RGBA 通道保存多种地形材质权重的控制图，也常写作 Splatmap。
- **Terrain Layer**：Unity Terrain 上的一层材质定义，包含颜色、法线和通道遮罩等纹理。
- **ACES / ACEScg**：电影和实时渲染常用的色彩管理体系。Houdini 预览与 Unity 后处理都采用 ACES 时，颜色更容易对齐。
- **Triplanar Projection（三向投影）**：分别从三个轴向投射纹理并按表面法线混合，用于避免陡坡纹理被垂直投影拉长。

## 三、工程经验与避坑指南

### 1. 导出、精度与颜色空间

- Houdini 与 Unity 想得到相近颜色，应把 Houdini OCIO 设置为 `ACEScg` 与 `ACES SDR Video`，并重新打开视口使设置生效。
- 高度图应使用足够精度的 EXR/RAW 等线性格式；带 Alpha 的多通道遮罩应先确认格式实际保留 Alpha，本课最终使用 PNG。
- 分辨率、Grid Spacing 或 Erode 帧数任何一项改变后，都要重新计算与重新导出，不能混用旧缓存。
- Normal Map 光照方向异常时检查 **Flip Green Channel**。本课后续确认前一课的地形法线绿色通道未翻转，导致受光方向相反。

### 2. 软件崩溃与恢复

- Houdini 本课发生崩溃且文件未保存，导出的 Height Map 只能恢复 `height`，不能恢复 Erode 生成的 `water`、`debris`、`sediment` 历史层。
- 恢复方法：用 **HeightField File** 导回高度图，设置正确的通道和 Height Scale，再重新运行 Erode 补建各层。
- 每完成一次模拟、遮罩分层或导出设置都应立即保存；HeightField 模拟缓存不能替代项目文件。
- 同时开启 Houdini、Unity、Substance Designer、会议软件可能耗尽显存或内存。课堂机器频繁崩溃时采用一次只开一个重型软件的办法。

### 3. 地形材质的真实限制

- Unity 默认 Terrain 主要从上向下采样纹理，陡坡会严重拉伸；没有随机旋转采样时，大面积纹理还会出现规则重复。
- Unreal 的某些地形方案支持格子随机旋转或更完整的防重复采样，Unity 默认流程没有同等处理。
- 三向采样能解决陡坡拉伸，但每层从 1 次采样变成 3 次；8 层就可能需要 24 次采样，URP 中修改整套 Terrain Shader 也较麻烦。
- 开放世界最终画面不能只依赖 Terrain：
  - Terrain 只提供大地形底子。
  - 悬崖、洞穴、岩壁用独立模型摆放。
  - 河流使用独立水面网格，河岸再用石头、植被遮住接缝。
  - 独立地形模型同样应使用 Triplanar 与材质遮罩，而不是强行展开超大 UV。
- 课程目标首先是**完整跑通 Houdini 分层 → Splat Map → Unity Terrain Layer → Designer 材质**。此流程环节多、容易导错，能够稳定复现比一次追求最终美术质量更重要。
