# UV、图集、流送与虚拟纹理

纹理组织解决两个问题：表面坐标如何对应纹理，以及大量纹理如何在有限内存中按需加载。

## UV Layout

展开 UV 时需要平衡：

- 拉伸；
- 接缝；
- Texel Density；
- 岛屿方向；
- Padding；
- 烘焙和 Lightmap 约束。

没有一种展开能同时最小化所有指标。角色脸部可能优先连续和高密度，硬表面可能优先直线、对齐和 Trim Sheet 复用。

## Texel Density

Texel Density 描述单位世界尺寸对应多少纹理像素。统一密度让同类资产的细节尺度一致，也方便估算内存。

它不是所有资产必须同值。主角、背景、可交互物体和远景可以使用不同预算，但差异应来自可见性和项目规范，而不是随意缩放 UV。

## Padding 和 Bleeding

过滤和 Mipmap 会读取 UV 岛边缘以外的 Texel。如果岛屿间距不够，远处 Mip 会混入别的岛或背景颜色。

需要：

- UV 岛之间保留与目标分辨率和 Mip 数匹配的间距；
- 烘焙时做 Dilation/Edge Padding；
- Atlas 子图保持边缘扩展；
- Clamp 不能代替岛屿内部 Padding。

## Texture Atlas

Atlas 把多张小纹理放进一张大纹理，通过 UV Rect 选择区域。

可能收益：

- 减少纹理和材质切换；
- 为 UI、Sprite、粒子或同类材质创造合批条件；
- 减少大量小资源的管理成本。

代价：

- 任一小图更新可能导致整个 Atlas 重建；
- 不同内容被迫共享分辨率、压缩和 Mip 策略；
- 动态加载粒度变粗；
- Padding 浪费空间；
- 重复纹理和不可见内容可能一起驻留。

Atlas 本身不会自动减少 Draw Call。材质状态、Shader、Render State、网格提交和引擎 Batching 条件仍要一致。

## Trim Sheet

Trim Sheet 把可重复的边、面板和装饰带放在一张纹理中，多资产通过 UV 复用。它适合模块化硬表面和建筑。

相比唯一展开，它减少纹理数量和制作成本，但会限制局部独特细节，需要 Decal、Vertex Color 或额外 Mask 补充变化。

## Texture Array

Texture Array 保存一组尺寸、格式和 Mip 一致的纹理层。Shader 用 Layer Index 选择，不需要改变 Sampler 绑定。

它避免 Atlas UV 重映射和边缘串色，适合地形、材质集合和粒子。但所有层仍共享尺寸/格式，并且整个 Array 的流送策略受引擎实现影响。

## Texture Streaming

纹理流送根据相机、Bounds、UV 密度和预算，只保留当前需要的高 Mip。远处使用低 Mip，接近时逐步加载高 Mip。

核心状态：

- Desired Mip：根据屏幕覆盖希望使用的层级；
- Resident Mip：当前内存里已有的层级；
- Streaming Budget：允许纹理占用的总内存；
- Priority：关键资源在压力下的保留权重。

如果加载速度追不上相机移动，会看到低清停留或 Mip Pop。盲目把所有纹理设为 Never Stream 会把问题转成显存溢出。

## Streaming 估算为什么会错

- Shader 对 UV 做了缩放或程序化变换；
- 同一纹理在不同对象上使用不同密度；
- 粒子、Decal 和 UI 没有可靠 Bounds；
- 相机 FOV 或动态分辨率变化；
- 运行时生成材质没有正确登记依赖。

引擎通常提供 Streaming Debug View，需要检查实际 Desired/Resident Mip。

## Virtual Texture

Virtual Texture 把超大纹理拆成 Page。Shader 使用虚拟地址，系统通过 Page Table 映射到物理缓存。

典型流程：

1. Shader 请求某个虚拟 Page；
2. Feedback 记录缺页；
3. CPU/IO 调度加载；
4. Page 上传到物理 Tile Cache；
5. 更新 Page Table；
6. 后续采样命中新页。

它让纹理逻辑尺寸大于实际驻留内存，适合大地形、Megatexture 和大量唯一表面。

代价：

- Page Table 采样；
- Feedback 和调度延迟；
- Tile Border；
- 缺页时低清或占位结果；
- 随机访问导致缓存抖动；
- 资产构建和 IO 管线更复杂。

## Runtime Virtual Texture

引擎可以在运行时把地形、Decal、道路或物体材质写入虚拟纹理，再由其他表面读取。它常用于地形融合和缓存昂贵材质结果。

它不是无限免费的 Render Target。更新区域、Page 数、分辨率、写入频率和采样次数都会影响成本。

## 验证方法

- 检查 UV Stretch、重叠、翻转和 Texel Density。
- 在最低 Mip 查看 Atlas 是否串色。
- 记录相机快速移动时的 Desired/Resident Mip 差距。
- 用显存预算压力测试 Streaming 淘汰行为。
- 显示 Virtual Texture Page、Cache 命中和 Feedback。
- 对比 Atlas、Array 和独立纹理的 Draw、内存和加载粒度。

### 图集 UV 变换

输入 `uvLocal` 是子图内部 $[0,1]^2$ 坐标，`rectPixels` 是图集中的像素矩形，`atlasSize` 是图集尺寸。半纹素内缩避免双线性过滤直接采到相邻子图：

```hlsl
float2 AtlasUv(float2 uvLocal, float4 rectPixels, float2 atlasSize)
{
    float2 minUv = (rectPixels.xy + 0.5) / atlasSize;
    float2 maxUv = (rectPixels.xy + rectPixels.zw - 0.5) / atlasSize;
    return lerp(minUv, maxUv, uvLocal);
}
```

半纹素内缩不能代替 Padding。较低 Mip 会把更大范围的 Texel 混合进一个样本，因此子图边缘仍要复制扩展，并按最大使用 Mip 预留间距。用高对比相邻子图和倾斜平面测试；若只在远处出现串色，问题通常来自 Mip Padding 或 Atlas Mip 生成。

## 相关主题

- [[06_纹理技术/纹理采样、过滤、Mipmap与压缩]]
- [[08_几何与网格/LOD、地形与程序化资产]]
- [[13_引擎架构与资源系统/资源打包、依赖与异步加载]]
- [[13_引擎架构与资源系统/UI、字体与文本渲染]]
- [[15_资产与工具管线/资产导入、验证与发布]]

## 参考资料

- id Software, *MegaTexture* references.
- Microsoft Learn, *Sampler Feedback and Tiled Resources*.
- Unity and Unreal documentation on Texture Streaming and Virtual Texturing.
