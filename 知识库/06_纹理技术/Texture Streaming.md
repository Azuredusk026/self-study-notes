# Texture Streaming

相机走近物体，Shader想读取高清mip，内存里却还只有粗层。Texture Streaming把需要层级和实际驻留分开记录，再按优先级加载。它要解决的是带宽、反馈延迟和预算竞争，UV本身正确仍可能出现低清停留。

## 纹理驻留

### Texture Streaming

纹理流送根据相机、Bounds、UV 密度和预算，只保留当前需要的高 Mip。远处使用低 Mip，接近时逐步加载高 Mip。

核心状态：

- Desired Mip：根据屏幕覆盖希望使用的层级；
- Resident Mip：当前内存里已有的层级；
- Streaming Budget：允许纹理占用的总内存；
- Priority：关键资源在压力下的保留权重。

如果加载速度追不上相机移动，会看到低清停留或 Mip Pop。盲目把所有纹理设为 Never Stream 会把问题转成显存溢出。

### Streaming 估算为什么会错

- Shader 对 UV 做了缩放或程序化变换；
- 同一纹理在不同对象上使用不同密度；
- 粒子、Decal 和 UI 没有可靠 Bounds；
- 相机 FOV 或动态分辨率变化；
- 运行时生成材质没有正确登记依赖。

引擎通常提供 Streaming Debug View，需要检查实际 Desired/Resident Mip。

## 驻留调度

这是CPU调度伪代码，mip编号越小分辨率越高。大小从格式与完整块预算计算。

```text
for texture in visibleTextures:
    desired = EstimateMip(texture, camera, uvDensity)
    if desired < residentMip:
        enqueue missing levels with priority
while projectedResidentBytes > budget:
    evict least-important detail levels
publish new resident view only after upload completion
```

丢弃高mip不改变资源身份，视图与GPU完成值仍由资源系统维护。频繁升降会造成IO抖动，可用滞回和请求去重。

## 验证方法

记录Desired与Resident差距，相机快速移动和预算耗尽时观察缺失时长。测试UV缩放、动态材质与多个相机，确认估计与实际采样密度一致。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[23_引擎运行系统/资源依赖与异步加载]]
- [[06_纹理技术/纹理压缩格式]]
- [[06_纹理技术/纹理图集]]
- [[06_纹理技术/Virtual Texture]]

## 参考资料

- id Software, *MegaTexture* references.
- Microsoft Learn, *Sampler Feedback and Tiled Resources*.
- Unity and Unreal documentation on Texture Streaming and Virtual Texturing.
