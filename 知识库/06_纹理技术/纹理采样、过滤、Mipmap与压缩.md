# 纹理采样、过滤、Mipmap 与压缩

纹理是可以按坐标读取的离散数据。一次采样不只是“拿一个像素”：GPU 需要决定坐标落在哪里、用哪个 Mip、读取哪些 Texel、如何过滤，以及是否做格式解码。

## Texture、Texel 和 UV

Texel 是纹理中的离散元素。像素是屏幕输出元素。一个像素可能读取多个 Texel，一个 Texel 也可能影响多个像素。

二维 UV 通常使用归一化坐标。$(0,0)$ 和 $(1,1)$ 对应纹理边界，但 API、图片格式和引擎可能有不同的 V 轴方向。

## Point Sampling

选择离采样位置最近的一个 Texel。它保留硬边，适合像素风、索引贴图和不允许混合的离散数据。

缩放时会明显跳变和闪烁。

## Bilinear Filtering

读取附近 2x2 Texel，先沿 X 插值，再沿 Y 插值。结果在单个 Mip 内连续。

它不能解决纹理缩小时一个像素覆盖很多 Texel 的问题，只是在当前 Mip 内取四个邻居。

## Mipmap

Mipmap 保存逐级缩小的纹理：

```text
L0: W × H
L1: W/2 × H/2
L2: W/4 × H/4
...
```

完整 Mip 链的额外像素数量约为原图的三分之一，因此未压缩内存约增加 33%。它换来更稳定的缩小采样和更好的缓存/带宽使用。

### LOD 如何估计

GPU 根据 UV 在屏幕相邻像素间的变化估计纹理 Footprint。简化理解：

$$
\rho=\max\left(
\left\lVert\frac{\partial \mathbf u}{\partial x}\right\rVert,
\left\lVert\frac{\partial \mathbf u}{\partial y}\right\rVert
\right),
\qquad LOD\approx\log_2\rho
$$

实际还要乘纹理尺寸并考虑实现细节。

`SampleLevel` 显式指定 LOD，`SampleGrad` 显式提供导数。Vertex/Compute Shader 没有天然的 2x2 Pixel Quad 导数，因此常需要显式 LOD。

## Trilinear Filtering

分别在两个相邻 Mip 做 Bilinear，再在 Mip 之间插值。它减少 Mip 切换带状边界，但采样和带宽比单级 Bilinear 更高。

## Anisotropic Filtering

倾斜表面的 Footprint 不是正方形，而是细长椭圆。普通 Mipmap 只按最大范围选一个方形尺度，会让某个方向过度模糊。

各向异性过滤沿长轴增加多个采样，保留道路、地面和斜面纹理细节。等级越高，最坏采样成本越高，但硬件会根据 Footprint 自适应。

## Magnification 和 Minification

- Magnification：一个 Texel 覆盖多个屏幕像素，主要靠 Point/Bilinear 决定放大外观。
- Minification：一个屏幕像素覆盖多个 Texel，需要预过滤、Mipmap 和各向异性过滤减少混叠。

## Address Mode

### Repeat/Wrap

取坐标小数部分平铺纹理。适合 Tileable 材质。

### Clamp

超出范围时使用边缘值。适合 Mask、Lookup Table 和屏幕纹理。

### Mirror

每个重复区间翻转，可以减少平铺边界方向突变。

### Border

范围外返回指定颜色。并非所有平台和 Sampler 类型都同样支持。

Atlas 子区域即使使用 Clamp，也可能在过滤和 Mip 中读到邻近图块，需要 Padding 和边缘扩展。

## Mipmap 不是对所有数据简单平均

### Normal Map

平均法线向量后长度会变短。生成 Mip 时需要按方向语义处理，并在采样后归一化。高频法线还会改变表面统计 Roughness，可使用 Toksvig、LEAN 等思路减少远处高光闪烁。

### Alpha Test

平均 Alpha 会改变覆盖率，导致树叶远处变稀或变厚。可以在各 Mip 调整阈值或重映射 Alpha，尽量保持 Coverage。

### SDF

距离场的零等值线和距离尺度需要保持。普通颜色平均可能让边界漂移。

### ORM/Mask

不同通道可能需要不同缩小策略。通道打包前要确认它们是否适合共享分辨率和 Mip。

## GPU 纹理压缩

PNG/JPEG 主要减少磁盘和下载大小，GPU 通常不能直接按任意 Texel 随机采样它们。运行时 GPU 压缩格式把纹理分成固定大小 Block，每个 Block 解码出若干 Texel，支持随机访问。

优点：

- 减少 VRAM；
- 减少纹理带宽；
- 保持硬件直接采样。

限制：

- Block 内像素共享端点或模式，容易产生块状和颜色误差；
- 质量与内容类型有关；
- 即使图片大面积透明，GPU 占用通常仍由尺寸、格式和 Mip 决定；
- 运行时重新压缩成本高。

## BC 格式

| 格式 | 常见用途 | 主要特点 |
|---|---|---|
| BC1 | RGB、可选 1-bit Alpha | 4 bpp；适合无平滑 Alpha 的颜色 |
| BC3 | RGBA | 8 bpp；颜色类似 BC1，Alpha 独立压缩 |
| BC4 | 单通道数据 | 4 bpp；Mask、高度、灰度数据 |
| BC5 | 双通道数据 | 8 bpp；常用于 Normal XY |
| BC6H | HDR RGB | 8 bpp；浮点 HDR 环境数据 |
| BC7 | 高质量 RGB/RGBA | 8 bpp；多种模式，质量高、编码更慢 |

BC5 法线只保存 X/Y，再重建 Z。相比把三通道法线塞进普通颜色压缩，它给两个关键方向分量更稳定的精度。

BC1 的“1-bit Alpha”并不适合平滑透明。BC3 是否比 BC7 更合适，要看目标平台、编码质量、内容和构建时间。

## 移动端格式

### ETC2/EAC

OpenGL ES 3 级移动设备常见。ETC2 处理 RGB/RGBA，EAC 适合单/双通道数据。

### ASTC

支持多种 Block 尺寸，例如 4x4、6x6、8x8。Block 越大，每像素位数越低、占用越小，但细节损失更明显。

ASTC 还能处理 LDR/HDR 和不同通道模式，适合作为现代移动端统一格式，但需要目标 GPU 支持。

### PVRTC

较老的 PowerVR/iOS 设备常见。它不是普通独立 4x4 Block 思路，低分辨率、小图和 Alpha 边缘可能出现明显扩散伪影。

## 压缩格式怎么选

先按数据语义：

- Base Color：BC1/BC7、ETC2、ASTC；
- 平滑 Alpha 颜色：BC3/BC7 或合适 ASTC；
- Normal：BC5、EAC RG、ASTC 双通道思路；
- 单通道 Mask：BC4、EAC R；
- HDR Environment：BC6H 或 HDR ASTC；
- UI：根据文字边缘、Alpha 和平台决定，不能直接套场景纹理规则。

再看目标平台、质量、内存、带宽、包体和编码时间。最终应检查目标设备上的解码结果，而不是只看源 PNG。

## 验证方法

- 显示 Mip Level 和 Texture Streaming 状态。
- 缓慢移动相机，观察远处闪烁和 Mip Band。
- 对比 Point、Bilinear、Trilinear 和 Anisotropic。
- 放大查看压缩 Block、渐变、Normal 高光和 Alpha 边缘。
- 用引擎 Memory Profiler 检查运行时格式和完整 Mip 占用。
- 检查平台 Override，避免编辑器格式与真机格式不一致。

## 相关主题

- [[01_数学与采样/信号、频率与噪声]]
- [[04_光照模型与PBR/法线贴图、切线空间与IBL]]
- [[06_纹理技术/高度、法线与视差映射]]
- [[06_纹理技术/UV、图集、流送与虚拟纹理]]
- [[14_性能分析与优化/渲染优化验证与移动端实践]]

## 参考资料

- Microsoft Learn, *Block Compression*.
- Khronos, *ASTC Specification* and *Data Format Specification*.
- NVIDIA, *Texture Filtering and Mipmapping* references.
