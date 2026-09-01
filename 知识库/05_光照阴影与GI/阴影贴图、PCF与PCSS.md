# 阴影贴图、PCF 与 PCSS

Shadow Map 解决的是从光源到表面的可见性。它不是保存“阴影颜色”的图片，而是保存光源视角下最近表面的深度。

## Shadow Map 流程

### 生成

从光源视角渲染场景，把最近深度写入 Shadow Map。方向光使用正交投影，Spot Light 常使用透视投影，Point Light 可以使用 Cubemap 或其他多面投影。

### 查询

把当前表面点变换到 Light Clip/Shadow Texture Space，得到：

- Shadow UV；
- 当前接收点深度 $z_r$。

读取 Shadow Map 的遮挡深度 $z_s$。如果 $z_r$ 明显大于 $z_s$，说明光源和接收点之间有更近表面，当前点在阴影中。

## 为什么不能直接双线性插值深度

假设一个采样落在遮挡物边缘，两侧深度分别属于近处遮挡物和远处背景。直接插值得到的是一个现实中不存在的中间深度。拿它与接收深度比较，会产生错误可见性。

PCF 的做法是：

1. 对邻域每个深度分别做比较；
2. 得到 0/1 或比较结果；
3. 过滤这些可见性结果。

$$
V=\frac{1}{N}\sum_{i=1}^{N}[z_r-bias\le z_i]
$$

硬件 Comparison Sampler 可以对相邻 Texel 的比较结果做过滤，而不是先过滤原始深度。

## PCF 的含义

Percentage-Closer Filtering 产生的是过滤后的可见比例。固定采样半径会得到近似固定宽度的柔边，但它主要是在抑制 Shadow Map 的离散锯齿，不是真正根据面积光源几何得到半影。

采样核越大：

- 边缘越软；
- 采样成本越高；
- 阴影细节更容易丢失；
- Bias 和漏光问题更明显。

Poisson Disk、旋转采样核和时域抖动可以减少规则图案，但会引入噪声或时间稳定性问题。

硬件比较采样器可以把深度比较和过滤组合起来。下面的 HLSL 代码执行一个 3x3 PCF 核，`shadowCoord.xy` 已在 $[0,1]$，`shadowCoord.z` 与 Shadow Map 使用同一深度约定：

```hlsl
float SampleShadowPCF(float3 shadowCoord, float bias)
{
    uint width, height;
    ShadowMap.GetDimensions(width, height);
    float2 texel = 1.0 / float2(width, height);
    float visibility = 0.0;

    for (int y = -1; y <= 1; ++y)
        for (int x = -1; x <= 1; ++x)
            visibility += ShadowMap.SampleCmpLevelZero(
                ShadowSampler,
                shadowCoord.xy + float2(x, y) * texel,
                shadowCoord.z - bias);

    return visibility / 9.0;
}
```

这里返回的是受光比例。Comparison Function、反向 Z、Border Color 和深度格式都会影响结果，移植时需要一起核对。

## PCSS

Percentage-Closer Soft Shadows 用三个步骤近似面积光半影。

### 1. Blocker Search

在接收点投影附近搜索深度小于 $z_r$ 的样本。它们是可能挡住光源的 Blocker。

计算平均 Blocker 深度 $z_b$。没有找到 Blocker 时，接收点通常视为完全受光。

### 2. 估计 Penumbra

平行平面近似下，半影大小与接收点和遮挡物的距离关系有关：

$$
w_p\propto w_l\frac{z_r-z_b}{z_b}
$$

$w_l$ 是光源尺寸。接收面离 Blocker 越远，半影越宽。

具体公式需要根据光源投影和深度空间转换。不能直接把非线性 Shadow Depth 塞进比例式。

### 3. Variable-radius PCF

把估算半影转换为 Shadow Map UV 中的过滤半径，再执行 PCF。

PCSS 是 Contact-hardening Shadow 的近似。它仍会受到 Blocker Search 样本数、深度不连续、接收面角度和复杂遮挡关系影响。

## Shadow Acne

由于深度精度、采样和表面斜率，接收面可能错误地与自己的 Shadow Depth 比较失败，出现条纹。

常见 Bias：

- Constant Depth Bias；
- Slope-scaled Bias；
- Normal Bias；
- Receiver Plane Depth Bias。

Bias 太小会 Acne，太大会 Peter Panning，让阴影与物体脚底分离。Normal Bias 还可能让薄物体漏光或改变阴影形状。

## CSM

级联阴影贴图（Cascaded Shadow Maps，CSM）为方向光准备多张不同覆盖范围的 Shadow Map。近处 Cascade 覆盖小、世界空间 Texel 密度高；远处 Cascade 覆盖大，用较低精度维持可见距离。

单张方向光 Shadow Map 必须同时容纳相机附近和远处视锥。透视相机中，近处物体占屏幕面积大，却只得到和远处相同的光空间 Texel 密度，因此近景最容易出现锯齿和游动。

### 1. 分割相机视锥

设相机近远平面为 $n,f$，Cascade 数量为 $m$，第 $i$ 个分割位置可以使用均匀分割：

$$
d_i^{uniform}=n+(f-n)\frac{i}{m}
$$

对数分割会把更多范围留给近处：

$$
d_i^{log}=n\left(\frac{f}{n}\right)^{i/m}
$$

实际常用 Practical Split 在两者之间插值：

$$
d_i=(1-\lambda)d_i^{uniform}+\lambda d_i^{log}
$$

$\lambda$ 越大，近处 Cascade 越密。分割距离通常按正的观察空间深度保存。右手观察空间常用 $d=-z_{view}$，不能直接拿非线性的 Depth Buffer 值比较。

### 2. 计算每层光空间矩阵

每个 $[d_i,d_{i+1}]$ 都形成一个截断视锥。计算步骤是：

1. 用该层的近远距离建立相机投影矩阵。
2. 反投影 NDC 的八个角点到世界空间。
3. 计算角点中心，建立方向光 View Matrix。
4. 把八个角点变换到光空间。
5. 对光空间角点求包围范围，建立正交投影。
6. 沿光照 Z 方向扩展范围，容纳可能投影进层内的 Caster。

NDC 深度范围取决于 API。OpenGL 默认使用 $[-1,1]$，Direct3D 和常见 Vulkan 配置使用 $[0,1]$。反投影时必须与实际投影矩阵约定一致。

下面的伪代码表达矩阵构造的数据流：

```cpp
Matrix BuildCascadeMatrix(float splitNear, float splitFar)
{
    Matrix sliceProj = Perspective(fov, aspect, splitNear, splitFar);
    Vector4 corners[8] = InverseProjectNdcCorners(sliceProj * view);

    Vector3 center = Average(corners);
    Matrix lightView = LookAt(center - lightDir * casterRange,
                              center, stableUp);
    Bounds bounds = FitLightSpaceBounds(corners, lightView);
    bounds.ExpandDepth(casterRange);

    Matrix lightProj = Orthographic(bounds.min, bounds.max);
    return lightProj * lightView;
}
```

`casterRange` 不能只按接收者视锥取值。视锥外的树或建筑仍可能把阴影投进视锥，过小会丢失阴影，过大则浪费深度精度。

### 3. 保存每层深度

各层可以使用独立纹理，也可以使用同尺寸、格式和 Mip 规则一致的 Texture Array。Array Layer 让 Shader 通过层索引采样，资源绑定更集中。

深度生成可以逐层提交 Draw，也可以使用 Layered Rendering。LearnOpenGL 的 CSM 示例用 Geometry Shader 的 `gl_Layer` 把图元写入不同 Array Layer。现代引擎也会通过多视图、实例化或逐层 Pass 完成，具体方式取决于 API、硬件和场景提交成本。

光空间矩阵数组适合放在 UBO 或 Constant Buffer。CPU 结构、Shader 布局和矩阵主次序必须一致。

### 4. 选择 Cascade

像素先计算正的观察空间深度，再找到包含它的分层区间。随后使用对应光空间矩阵和 Texture Array Layer：

```glsl
int SelectCascade(vec3 positionWS)
{
    float viewDepth = -(view * vec4(positionWS, 1.0)).z;
    int layer = cascadeCount - 1;

    for (int i = 0; i < cascadeCount - 1; ++i) {
        if (viewDepth < cascadeSplits[i]) {
            layer = i;
            break;
        }
    }
    return layer;
}
```

这段代码假定右手观察空间中相机前方 Z 为负。引擎使用其他约定时，`viewDepth` 的符号需要同步调整。

### 5. 处理边界过渡

相邻 Cascade 的投影、Bias 和过滤结果不同。硬切换会在分割平面出现明显跳线。常见做法是在边界附近定义一段重叠区，同时采样相邻两层：

$$
V=lerp(V_i,V_{i+1},t)
$$

$t$ 由观察空间深度在过渡区中的位置得到。过渡越宽，双层采样区域越大；过窄则难以隐藏差异。两层的世界空间过滤半径也应接近，否则混合仍会看到软硬变化。

### 6. Bias 和过滤尺度

同样的 Shadow UV 偏移在不同 Cascade 中代表不同世界距离。每层需要按正交投影范围和纹理分辨率计算世界空间 Texel 尺寸，再据此调整：

- Constant/Slope Bias；
- Normal Bias；
- PCF 或 PCSS 采样半径；
- Cascade 过渡区宽度。

直接复用同一数值会让近层 Peter Panning，或让远层 Acne 和锯齿加重。

### 7. 稳定化和 Texel Snapping

紧致包围盒会随着相机旋转和移动持续改变，导致世界点映射到不同 Shadow Texel，画面出现阴影游动。稳定化通常包含：

- 使用包围球或固定尺度确定 Cascade 的 XY 范围；
- 把光空间投影中心吸附到 Shadow Texel 网格；
- 固定方向光基底，避免 Up Vector 在临界方向翻转；
- 对分割距离和投影范围保持确定性。

若正交投影宽度为 $w$、阴影分辨率为 $R$，一个 Texel 对应的光空间长度是：

$$
s_{texel}=\frac{w}{R}
$$

将投影中心除以 $s_{texel}$、取整后再乘回去，就能让平移以整 Texel 发生。包围球通常更稳定，紧致 AABB 的分辨率利用率更高。工程实现需要在稳定性和有效分辨率之间取舍。

### 8. 成本

CSM 的主要成本来自：

- 每个 Cascade 重复生成方向光深度；
- Caster 剔除、命令生成和状态提交；
- 多层深度纹理的显存和带宽；
- 边界混合的额外采样；
- PCF/PCSS 的采样核。

Cascade 数量、分辨率和更新频率应按平台与画面需求设置。远层可以降低更新频率或渐隐到烘焙阴影、距离场阴影等结果。

### 9. 调试

- 用不同纯色显示 Cascade Index，检查层选择和过渡。
- 单独显示 Texture Array 每一层的深度。
- 绘制每层世界空间视锥和方向光正交包围盒。
- 缓慢平移和旋转相机，观察边缘是否按整 Texel 移动。
- 在边界放置斜面、细杆和远处高 Caster，检查 Bias、漏投影和跳变。
- 记录每层 Draw、Caster 数量、分辨率和更新时间。

## 方差阴影与虚拟阴影

方差阴影贴图（Variance Shadow Map，VSM）保存深度的一阶、二阶矩，用切比雪夫不等式估计受光概率。矩数据可以线性过滤和预过滤，适合较软阴影，但数值误差与深度分布重叠会产生 Light Bleeding。EVSM 等变体通过指数变换增强分离度，同时更依赖精度和参数控制。

虚拟阴影贴图（Virtual Shadow Map，也简称 VSM）把高分辨率阴影空间切成 Page，只分配和更新当前视图需要的区域。它依赖虚拟地址映射、Page Cache、接收者驱动请求和失效规则，目标是让大世界和高密度几何保持细致阴影。

两个 VSM 指代完全不同：Variance 是基于深度矩的可过滤表示，Virtual 是稀疏分页与缓存方案。阅读资料或抓帧时要先确认上下文。

## Point Light Shadow

Cubemap Shadow 需要六个面，意味着最多六次场景渲染。Dual Paraboloid 等替代方案可以减少面数，但会引入投影畸变和接缝。

动态 Point Light Shadow 很贵，项目通常限制数量、分辨率、更新频率或使用缓存。

## 常见伪影定位

| 现象 | 优先检查 |
|---|---|
| 表面条纹 | Depth/Slope Bias、精度、法线 |
| 阴影悬空 | Bias 过大、Normal Bias |
| 边缘锯齿 | 分辨率、投影覆盖、PCF、Cascade |
| 相机移动抖动 | Cascade Stabilization、Texel Snapping |
| 薄墙漏光 | Shadow Caster 面、Bias、厚度 |
| PCSS 大块噪声 | Blocker Search、采样序列、深度转换 |

## 验证方法

- 直接显示 Shadow Map 和接收点 Shadow UV。
- 分别显示 $z_r$、$z_s$、比较结果和最终过滤值。
- PCSS 单独显示 Blocker Count、Average Blocker Depth 和 Filter Radius。
- 用平面、方块和可调面积光建立最小测试场景。
- 在斜面、薄片、远距离和 Cascade 边界做压力测试。

## 相关主题

- [[02_GPU与光栅化管线/光栅化、插值与深度模板]]
- [[01_数学与采样/向量、矩阵与空间变换]]
- [[05_光照阴影与GI/光源与直接光照]]
- [[06_纹理技术/纹理采样、过滤、Mipmap与压缩]]
- [[13_引擎架构与资源系统/Render Pass、Command Buffer与Render Graph]]
- [[11_NPR与风格化渲染/角色面部、头发与阴影]]

## 参考资料

- Randima Fernando, *Percentage-Closer Soft Shadows*.
- NVIDIA, *Integrating Realistic Soft Shadows into Your Game Engine*.
- Microsoft Learn, *Cascaded Shadow Maps*.
- LearnOpenGL, `src/8.guest/2021/2.csm`.
