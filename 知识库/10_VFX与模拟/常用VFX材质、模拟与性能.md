# 常用 VFX 材质、模拟与性能

VFX 材质通常用简单几何、时变 UV、遮罩和透明混合制造复杂现象。效果是否可用，取决于时间和空间是否稳定、深度关系是否可信，以及屏幕覆盖成本是否受控。

## Flipbook

Flipbook 把多帧烟、火或爆炸打包进一张 Atlas。给定列数 $C$、行数 $R$ 和帧索引 $f$：

$$
x=f\bmod C,\qquad y=\lfloor f/C\rfloor
$$

局部 UV 缩放到单格后加上 $(x/C,y/R)$ Offset。需要确认贴图原点方向，否则帧序会上下颠倒。

帧间直接切换会抖动。Frame Blending 同时采样相邻两帧并插值，运动更平滑，但纹理采样翻倍，也可能产生重影。

Atlas 每格需要 Padding。Mipmap 和 Bilinear Filter 会跨格采到相邻帧，产生边缘串色。可以扩边、使用专用 Mip，或在 Shader 中收紧单格 UV。

## Dissolve

Dissolve 用标量场 $m(\mathbf{x})$ 与阈值 $t$ 比较：

$$
\text{visible}=m(\mathbf{x})\ge t
$$

标量场可以来自 Noise Texture、Vertex Color、World Position、Object Space Gradient 或 SDF。

边缘带可写成：

$$
e=\operatorname{smoothstep}(t,t+w,m)-\operatorname{smoothstep}(t+w,t+2w,m)
$$

$w$ 控制边宽。将 $e$ 用于 Emissive/Color，可产生燃烧边缘。

Object Space 遮罩随物体稳定；World Space 可让多个物体共享扫描平面；UV Noise 会跟随贴图，但可能在 UV 缝断裂。选择应符合效果语义。

使用 `clip/discard` 能保留不透明排序和深度写入，但边缘会锯齿，也可能削弱 Early-Z。Alpha Blend 更柔和，却带来排序和 Overdraw。Shadow、Depth、Motion Vector Pass 应使用一致阈值，否则影子和轮廓不同步。

## Distortion 与 Refraction

屏幕扰动通常采样 Scene Color：

$$
\mathbf{uv}'=\mathbf{uv}+\mathbf{d}\,k
$$

$\mathbf{d}$ 可由 Normal/Noise 的 RG 映射到 $[-1,1]$，$k$ 是强度。

需要限制 Offset，避免采到物体轮廓外的错误前景。Scene Color 只包含已经渲染的内容，因此执行时机、透明队列和相机堆叠都会改变结果。

真正物理折射还涉及 IOR、厚度和入射方向。简单屏幕偏移只是视觉近似，在屏幕边缘和遮挡关系上天然缺信息。

## Depth Fade 与 Soft Particle

半透明面片与场景几何相交时会出现硬切线。Soft Particle 比较粒子深度 $z_p$ 和 Scene Depth $z_s$：

$$
f=\operatorname{saturate}\left(\frac{z_s-z_p}{d}\right)
$$

$d$ 是 Fade Distance。用 $f$ 乘 Alpha 可软化交界。

两种深度必须先还原到同一线性 View Space。直接比较非线性 Depth Buffer 会让淡出随距离变化。

Depth Fade 会让贴地烟雾在接触处变淡，不一定符合所有效果。也可以把深度差用于边缘颜色、泡沫或交界亮线。

## Fresnel、Rim 与 Camera Fade

Fresnel 近似常用：

$$
F=(1-\operatorname{saturate}(\mathbf{N}\cdot\mathbf{V}))^p
$$

它能增强能量罩、幽灵和冲击波的边缘。$p$ 越大，亮边越窄。

粒子靠近相机时，Billboard 会突然覆盖整个屏幕。Camera Fade 可根据 View Depth 或相机距离降低 Alpha/Size，并限制近裁剪面附近的粒子数量。

## Polar UV、Flow 与噪声

圆形冲击波可把中心化 UV 转为极坐标：半径控制环形推进，角度控制沿圆周的纹理采样。

Flow Map 用 RG 表示二维流向，按时间偏移 UV。单次滚动在周期重置时会跳变；常用两组相差半周期的采样，再用三角权重交叉淡入淡出。

噪声不要无目的叠加。区分用途：

- 大尺度噪声改变整体轮廓；
- 中尺度噪声控制密度和卷动；
- 小尺度噪声补表面细节；
- 时间 Offset 控制运动速度。

多层噪声会增加采样和 Alias，应为远距离准备简化版本。

## Trail 与 Ribbon 材质

Trail UV 常用 U 表示沿轨迹累计距离，V 表示横向。按累计距离而不是点序号铺 UV，可以避免采样密度变化时纹理伸缩。

转弯处宽度方向可能翻转。生成网格时应保持连续 Frame，或使用 View-facing Ribbon 并处理相机方向接近平行时的退化。

透明 Ribbon 的自交无法通过简单排序完全解决。可改用 Additive、缩短寿命、控制轨迹形状，或在关键效果使用 OIT/专门网格。

## Scene Depth、SDF 与流体近似

VFX 常用低成本场而不是完整物理：

- Scene Depth 做屏幕空间碰撞和交界；
- SDF 做体积碰撞、吸引和避障；
- Curl Noise 生成近似无散度的旋涡速度场；
- Vector Field 驱动群体流向；
- Heightfield 模拟水面或地面传播；
- Flipbook 播放 Houdini 离线流体结果。

实时网格流体、Grid/FLIP 和体积烟雾需要更完整的模拟和渲染管线。游戏效果常把低分辨率模拟、上采样、历史重建与艺术控制结合，而不是追求完全物理准确。

## Alpha Blend、Premultiplied 与 Additive

普通 Alpha Blend 适合烟和柔和透明层，但需要排序。Premultiplied Alpha 能让边缘颜色与透明更稳定，并能在同一表示中兼顾发光与透明。

Additive 不依赖目标 Alpha，排序影响较小，适合火花、能量和亮光。它无法表现遮暗的烟，叠加过多也容易过曝。

贴图导出、材质 Blend State 和 Shader 输出必须采用同一种 Alpha 约定。黑边/白边常来自 Straight 与 Premultiplied 混用。

## Overdraw 的成本

粒子面数很低，不代表便宜。半透明粒子通常关闭 Depth Write，同一像素会执行多层 Fragment Shader、纹理采样、混合和 Render Target 读写。

粗略成本更接近：

$$
\text{Pixel Cost}\propto \text{Covered Pixels}\times\text{Layers}\times\text{Shader Cost}
$$

因此一个贴近镜头的全屏烟片，可能比数千个远处小火星更贵。

## 常见降级手段

- 减小 Billboard 中无效透明边界，或使用更贴合轮廓的低面数 Mesh。
- 按屏幕占比限制 Spawn、Size 和 Lifetime。
- 远距离减少 Emitter、Flipbook 帧率和材质采样。
- 烟雾在 Half/Quarter Resolution Buffer 渲染，再做 Depth-aware Upsample。
- 分离必须排序和可 Additive 的粒子。
- 限制动态光源、阴影粒子和 Scene Color/Depth 采样。
- 为移动端准备独立 Material/Emitter LOD，而不只是减少总粒子数。

低分辨率透明需要处理物体边缘、深度不连续和 TAA 历史，否则会出现 Halo、泄漏和拖影。

## 预算与验证

不要只记录 Particle Count。至少统计：

- 同屏 System/Emitter/Alive Particle；
- Draw Call、Material/Variant；
- 屏幕覆盖率与 Overdraw Heatmap；
- Simulation/Sort/Render GPU 时间；
- Flipbook/Noise 纹理内存和带宽；
- 光源、阴影、碰撞和事件数量。

测试应包含近距离、多个效果叠加、低帧率、大战斗和移动端热稳定状态。单独预览器中的一个效果无法代表 Gameplay 峰值。

### 带抗锯齿边缘的 Dissolve

输入噪声和阈值都位于 $[0,1]$。`fwidth` 根据屏幕像素覆盖调整边缘宽度，输出包含裁剪结果与发光边缘：

```hlsl
float noise = DissolveNoise.Sample(LinearRepeat, uv).r;
float signedDistance = noise - threshold;
float pixelWidth = max(fwidth(signedDistance), 1e-4);
float coverage = smoothstep(-pixelWidth, pixelWidth, signedDistance);
float edge = saturate(1.0 - abs(signedDistance) / max(edgeWidth, pixelWidth));
clip(coverage - alphaCutoff);
float3 color = baseColor + edge * edgeColor * edgeIntensity;
```

这里的 `edgeWidth` 属于噪声值域，不是世界距离。噪声对比度或 UV Scale 改变时，视觉边宽也会改变。验证时缓慢推进 `threshold`，检查边缘是否连续，并在远近距离观察 `fwidth` 是否减少锯齿和闪烁。

## 相关主题

- [[02_GPU与光栅化管线/剔除、透明与混合]]
- [[07_颜色与后处理/颜色空间、Alpha、HDR与曝光]]
- [[10_VFX与模拟/粒子系统与GPU模拟]]
- [[14_性能分析与优化/渲染优化验证与移动端实践]]

## 参考资料

- Unity Documentation, *Visual Effect Graph* and *Particle System*.
- Unreal Engine Documentation, *Niagara Renderers* and *Scalability*.
- GPU Gems, particle and flow simulation chapters.
