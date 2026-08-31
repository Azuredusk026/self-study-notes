# 描边、Billboard 与场景风格化

描边负责轮廓和结构可读性，Billboard 用低成本平面表达体积元素，场景风格化则让材质、植被、阴影和后处理遵守同一视觉尺度。

## Inverted Hull

Inverted Hull 会额外绘制一层模型：顶点沿法线外扩，Cull Front，只显示扩张壳的背面并输出描边色。

Object Space 外扩：

$$
\mathbf{p}'=\mathbf{p}+w\mathbf{n}
$$

实现简单，但 $w$ 是世界/模型单位，近处线宽、远处线细。模型非均匀缩放也会改变宽度。

要近似固定屏幕像素宽度，可把 View/Clip Space Offset 与 Clip $w$、Projection Scale 和屏幕尺寸关联。精确实现依赖投影矩阵与目标 API，必须在不同 FOV、Aspect 和动态分辨率下验证。

## 硬边为什么裂开

立方体硬边处，同一位置会拆成多个顶点，每个面有不同法线。沿各自法线外扩后，顶点彼此分离，产生裂缝。

常见处理：

- 额外烘焙一套平滑 Outline Normal 到 Vertex Color/Tangent/UV；
- 用相邻面加权平均法线，但保留原 Shading Normal；
- 对需要硬轮廓的区域手工编辑外扩方向；
- 改用屏幕空间描边。

直接把模型法线全部平滑会破坏正常光照。Outline Normal 应作为独立属性。

## Outline Pass 成本

Inverted Hull 不是“只多一点顶点”。它通常意味着额外 Pass 和 Draw，并可能重复 Skinning、Vertex Animation、Alpha Clip 和材质状态。

批次成本取决于：

- 描边是否能共享 Shader Variant 与材质布局；
- Skinned Mesh 是否重复蒙皮；
- 是否为全部 Submesh 画壳；
- 前后顺序与深度状态；
- 透明发片和局部关闭描边的 Mask；
- 阴影/Depth Pass 是否无意包含 Outline。

可把多个对象的 Outline 参数放入实例数据，减少材质实例。对远景角色可关闭内部线或切换屏幕空间方案。

## 屏幕空间描边

后处理描边从 Depth、Normal、Color、Material ID 或 Custom Depth 检测不连续。

简单深度梯度：

$$
g_d=|z(x+1,y)-z(x-1,y)|+|z(x,y+1)-z(x,y-1)|
$$

深度差随距离和斜面变化，应在线性 View Depth 中计算，并让阈值随深度或导数适配。否则远处地面会整片被识别为边缘。

Normal 边缘可用相邻法线点积：

$$
g_n=1-\mathbf{n}_0\cdot\mathbf{n}_1
$$

它能发现内部折角，却会把高频 Normal Map 也当边缘。可使用几何法线 Buffer、降采样法线或 Material Mask 控制。

## Object ID 与可控内部线

只用深度和法线无法知道两个接触面是否属于同一对象。Object/Material ID 可以：

- 给角色外轮廓更粗线；
- 忽略同材质内部接缝；
- 只描选中或被遮挡对象；
- 为脸、头发和服装设置不同线色。

ID Buffer 需要稳定格式和抗锯齿策略。TAA 前后执行位置会影响抖动、History 和线宽。不能笼统认为 TAA 一定不能用于描边；关键是 Jitter、Depth/Normal History 与 Reject 是否一致。

## Inverted Hull 与屏幕描边的组合

Inverted Hull 能稳定表现外轮廓和物体间遮挡，但难表现内部结构。屏幕描边能检测内部法线/深度边缘，却容易受分辨率和噪声影响。

常见组合是：

- Hull 负责角色外轮廓；
- Face/Material Mask 控制内部手绘线；
- Screen-space 负责场景接触和部分内部折角；
- 远景使用简化的一像素屏幕线。

## Billboard 的朝向

Spherical Billboard 完全朝向相机。给定中心 $\mathbf{c}$、Camera Right $\mathbf{r}$ 和 Up $\mathbf{u}$，面片顶点为：

$$
\mathbf{p}=\mathbf{c}+x\mathbf{r}+y\mathbf{u}
$$

Cylindrical Billboard 保持世界 Up，只绕垂直轴转向相机，适合树和站立角色。应处理 Camera Forward 与 Up 接近平行时的退化，并确认三角形 Winding 不会被 Backface Culling 剔除。

## Pivot、脚底与假深度

角色或场景 Billboard 若以面片中心作为 Pivot，绕地面转向时会像悬浮纸片。应以脚底/接地点作为 Anchor：

- Billboard Center 由脚底世界位置加高度 Offset 得到；
- 排序和地面接触使用 Foot Position；
- 阴影、雾和交互也以同一 Anchor 计算；
- 顶点仅在 Anchor 上方构造面片，不改变脚底位置。

风格化场景可进一步用 Foot Position 构造假深度。比如画面中的上半部分在 Shader 中获得轻微 Parallax、雾或 UV Offset，而脚底保持固定，使二维卡片看起来有局部体积。

若用 View Direction 偏移 UV：

$$
\Delta\mathbf{uv}=k\,h(\mathbf{uv})\,\mathbf{v}_{tangent,xy}
$$

$h$ 是伪高度，脚底区域应接近 0。偏移过大会暴露轮廓外信息，需要 Padding 或 Layered Card。

## 植被 Billboard

树木远景可以使用多视角 Impostor，而不只是一张正面图。离线从若干方位和俯仰角烘焙 Base Color、Normal、Depth 等 Atlas，运行时选择邻近视角并混合。

Depth Impostor 可重建更可信的视差和深度写入，但会增加采样与计算。切换 Mesh LOD 到 Impostor 时要匹配：

- Bounds、Pivot 与树高；
- Base Color、曝光和雾；
- Normal 与主光方向；
- Alpha Coverage；
- 阴影形状和风动相位。

## 场景风格化

场景不是给 PBR 材质套同一 Ramp 就结束。需要统一：

- 大中小形状频率和 Texel Density；
- 明暗层级与 Shadow Tint；
- 手绘 Normal/Curvature/AO 的使用强度；
- 植被风动、Alpha 和远景 LOD；
- Fog、Sky、Color Grading 与角色曝光；
- Decal、Outline、VFX 的线条和色板。

Hero Character 比场景更复杂是合理的，但两者的主光、暗部色相和后处理必须处在同一世界。

## 风动

树叶和灌木常用 Vertex Color/UV Mask 区分根部、枝条和叶尖。基础风动可由低频主摆动、高频叶片抖动和世界空间阵风组成。

Root Mask 要保证接地点稳定；不同实例用 World Position/Random Seed 偏移相位，避免整片树林同步。Shadow、Depth、Motion Vector Pass 必须使用同样的位移函数，否则产生影子脱离和 TAA 拖影。

## 验证方法

- 用球、立方体、硬边道具和蒙皮角色检查 Hull 裂缝与线宽。
- 统计 Outline Pass 的 Draw、Vertex、Skinning 和 Fragment 成本。
- 输出 Depth/Normal/ID Edge 分量，检查斜面、远景和动态分辨率。
- 在不同 FOV、TAA Jitter 和 Upscaler 下检查一像素线稳定性。
- 绕 Billboard/Impostor 旋转相机，检查 Foot Anchor、视角切换和假深度。
- 对植被风动检查 Shadow、Depth 和 Motion Vector 一致性。

## 相关主题

- [[02_GPU与光栅化管线/抗锯齿与时域采样]]
- [[09_动画系统/骨骼动画、蒙皮与GPU动画]]
- [[11_NPR与风格化渲染/NPR材质与分层光照]]
- [[14_性能分析与优化/Profiler、RenderDoc与单帧分析]]

## 参考资料

- Unreal Engine Documentation, *Impostor Baker* and *Custom Depth-Stencil*.
- Unity documentation and technical presentations on stylized outlines and vegetation animation.
- Lengyel, *Projection Matrix Tricks*，用于屏幕空间线宽与深度理解。
