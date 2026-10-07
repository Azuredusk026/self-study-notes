# Virtual Texture

一张巨大地形纹理只有少量区域可见，整张驻留会浪费内存。Virtual Texture把逻辑地址映射到页缓存，缺页由反馈驱动加载，已常驻粗层负责回退。页表、边框和替换顺序决定采样能否稳定。

## 虚拟分页

### Virtual Texture

Virtual Texture 把超大纹理拆成 Page。Shader 使用虚拟地址，系统通过 Page Table 映射到物理缓存。

典型流程：

1. Shader 请求某个虚拟 Page；
2. Feedback 记录缺页；
3. CPU/IO 调度加载；
4. Page 上传到物理 Tile Cache；
5. 更新 Page Table；
6. 后续采样命中新页。

它让纹理逻辑尺寸大于实际驻留内存，适合大地形、Megatexture 和大量唯一表面。

#### 页表与页边框

实现上通常有一张间接纹理（Indirection Texture），每个纹素存“这个虚拟页当前在物理缓存的哪个位置、处于哪个 Mip”。采样时先查间接纹理拿到物理地址，再访问物理缓存。物理缓存是一组固定大小（常见 128×128 加边框）的页槽，槽位数量远小于虚拟页总数。

页边框的作用与图集 Padding 相同：各向异性过滤和 Mip 过渡时，采样核会越过页边界读取邻页内容，而邻页在物理缓存中并不相邻。每页物理存储时向外扩一圈纹素，把逻辑上相邻的内容复制进来。边框宽度按最大过滤半径决定。

缺页时的回退是向上取更粗的 Mip：系统应显式保留可用粗层或定义占位回退；只有这个保证成立，缺页才能显示稳定低清而非错误内容。反馈回读到生效有数帧延迟，相机快速移动时的短暂模糊就是这条链路的长度。

代价：

- Page Table 采样；
- Feedback 和调度延迟；
- Tile Border；
- 缺页时低清或占位结果；
- 随机访问导致缓存抖动；
- 资产构建和 IO 管线更复杂。

### Runtime Virtual Texture

引擎可以在运行时把地形、Decal、道路或物体材质写入虚拟纹理，再由其他表面读取。它常用于地形融合和缓存昂贵材质结果。

它不是无限免费的 Render Target。更新区域、Page 数、分辨率、写入频率和采样次数都会影响成本。

## 虚拟地址查询

模型伪代码输入虚拟UV与目标mip，输出已驻留层的颜色。

```text
page = VirtualPage(uv, mip)
entry = PageTableLookup(page)
if not resident(entry):
    emit feedback(page)
    entry = FindResidentAncestor(page)
physicalUv = entry.slotOrigin + LocalPageUv(uv, entry.mip, border)
return SamplePhysicalCache(physicalUv)
```

粗层回退必须由系统显式保证，不是假设任何祖先自然在缓存中。槽位替换先等待旧GPU使用，再上传并发布新页表映射。

## 验证方法

显示页ID、实际mip、缓存命中和反馈延迟。跨页过滤、相机瞬移与缓存抖动分别检查；RVT写入页还要记录失效区域和消费者。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[06_纹理技术/Texture Streaming]]
- [[13_渲染架构/GPU资源生命周期]]
- [[06_纹理技术/纹理图集]]

## 参考资料

- id Software, *MegaTexture* references.
- Microsoft Learn, *Sampler Feedback and Tiled Resources*.
- Unity and Unreal documentation on Texture Streaming and Virtual Texturing.
