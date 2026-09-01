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

方向光需要覆盖很大范围。单张 Shadow Map 会把分辨率浪费在远处。Cascaded Shadow Maps 按相机深度把视锥分段，每段使用独立 Shadow Projection。

需要处理：

- Cascade Split 分布；
- Cascade 间过渡；
- 相机移动导致的投影抖动；
- Texel Snapping/Stabilization；
- 不同 Cascade 的 Bias 和过滤尺度；
- 远距离阴影淡出。

Cascade 越多不一定越好，会增加渲染和采样成本。

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

- [[知识库/02_GPU与光栅化管线/光栅化、插值与深度模板]]
- [[知识库/05_光照阴影与GI/光源与直接光照]]
- [[知识库/06_纹理技术/纹理采样、过滤、Mipmap与压缩]]
- [[知识库/11_NPR与风格化渲染/角色面部、头发与阴影]]

## 参考资料

- Randima Fernando, *Percentage-Closer Soft Shadows*.
- NVIDIA, *Integrating Realistic Soft Shadows into Your Game Engine*.
- Microsoft Learn, *Cascaded Shadow Maps*.
