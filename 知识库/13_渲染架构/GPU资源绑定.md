# GPU资源绑定

材质参数已经上传，Shader却采到别的纹理，问题可能出在绑定表与对象寿命。描述符告诉GPU从哪里、按什么格式读资源，它不负责上传数据，也不负责完成写后读同步。先把布局、索引和更新频率对应起来，再检查GPU尚未结束访问时哪些槽位不能复用。

## 寻址与布局

### API 暴露方式

| API | 主要对象 | 必须核对的条件 |
|---|---|---|
| Vulkan | descriptor set layout、descriptor set、pipeline layout | descriptor 类型、阶段范围、动态偏移和布局兼容 |
| D3D12 | root signature、descriptor heap、descriptor table | 根参数预算、堆寿命、视图与状态 |
| Metal | buffer/texture 绑定、argument buffer | 平台能力、资源使用声明和寿命 |

描述符是资源视图与寻址信息。绑定描述符本身不会上传像素数据，也不自动完成 GPU 写后读同步。

### 按访问和更新频率组织

全帧数据、视图数据、材质数据和逐对象数据通常分开。其目的是减少更新与重绑范围，但最终分组还取决于 API、材质排序、实例化方式和 CPU/GPU 数据生产者。

一组材质参数可放进共享缓冲，以索引或动态偏移选择记录。Vulkan 动态 uniform/storage 描述符使用对应类型和设备对齐限制。D3D12 常用 CBV、root descriptor 或结构化缓冲索引，不能把 Vulkan 动态偏移接口直接套到根签名。

## 动态数据与索引

### Vulkan 动态 uniform 示例

缓冲记录按 `minUniformBufferOffsetAlignment` 对齐，每个帧使用独立的未完成区间。示例只演示绑定已创建的 descriptor set，输入偏移为字节单位。

```cpp
VkDeviceSize alignment = limits.minUniformBufferOffsetAlignment;
VkDeviceSize recordSize = sizeof(MaterialConstants);
VkDeviceSize stride = ((recordSize + alignment - 1) / alignment) * alignment;
VkDeviceSize offset = frameBase + materialIndex * stride;
assert(offset <= UINT32_MAX);
uint32_t dynamicOffset = static_cast<uint32_t>(offset);
vkCmdBindDescriptorSets(commandBuffer,
    VK_PIPELINE_BIND_POINT_GRAPHICS,
    pipelineLayout, materialSetIndex,
    1, &materialSet,
    1, &dynamicOffset);
```

绑定时的动态偏移与描述符中保存的基础偏移相加。范围需在实际缓冲内，描述符类型需为动态缓冲，offset 数量和顺序由布局决定。设备限制应查询，256 字节仅是部分场景的常见值。

### 小参数与推送常量

Vulkan push constants 把少量值记录在命令里，适合对象索引与标志。Vulkan 1.0 核心保证至少 128 字节，实际容量查询 `maxPushConstantsSize`。范围、阶段和管线布局需要匹配。

D3D12 root constants 受根签名 DWORD 预算约束，Metal 采用其绑定模型。小参数通道可减少缓冲更新，但实际延迟和驱动开销仍需测量。

### Bindless 的索引访问

大描述符数组允许着色器用材质索引选择纹理。不同片元访问不同纹理时，编译器需要知道索引可能不一致；HLSL 可用 `NonUniformResourceIndex`，Vulkan 对应 descriptor indexing 能力及 SPIR-V 装饰。

```hlsl
Texture2D<float4> materialTextures[] : register(t0, space1);
SamplerState materialSampler : register(s0);

float4 ReadBaseColor(uint textureIndex, float2 uv)
{
    uint index = NonUniformResourceIndex(textureIndex);
    return materialTextures[index].Sample(materialSampler, uv);
}
```

这是 SM 5.1 及相应绑定环境中的函数片段，数组实际容量、根签名和材质表由应用建立。索引必须指向有效描述符。GPU 工作结束前释放纹理或复用槽位会产生无效访问或串材质；使用完成值延迟回收，并为未加载资源设置有效的回退描述符。

## 寿命与成本

### 成本与边界

改参数值、改纹理视图和改静态关键字分别影响上传、描述符更新和 Shader/PSO 组合。Bindless 减少逐材质绑定，仍有描述符访问、纹理缓存、索引传输与生命周期维护成本。

大量不相干的纹理访问会降低局部性。材质排序仍可能有价值。更新仍在使用的描述符需遵守 API 的 update-after-bind、堆和可见性限制。

## 验证方法

- 以高对比纹理给每个索引编号，批量切换材质，观察是否串读。
- 把 GPU 人为延迟，快速销毁并重建材质，检查描述符是否等完成后才复用。
- 记录每帧描述符更新数、绑定调用数和上传字节，比较分组前后 CPU 时间。
- 使用不同设备对齐要求构建参数表，并检查范围和偏移验证消息。

## 相关主题

- [[13_渲染架构/GPU资源生命周期]]
- [[26_GPU驱动与虚拟几何/GPU-Driven Rendering]]
- [[03_Shader编程/Shader接口与数据流]]

示例状态：本页代码用于解释对应的数据和调用约束，完整资源创建、类型与调用环境由项目提供。除文中另列的实际实验外，本页未执行目标引擎编译、GPU捕获或性能计时。

## 参考资料

- [Vulkan Resource Descriptors](https://docs.vulkan.org/spec/latest/chapters/descriptorsets.html)。
- [D3D12 Root Signatures](https://learn.microsoft.com/en-us/windows/win32/direct3d12/root-signatures)。
- [NonUniformResourceIndex](https://learn.microsoft.com/en-us/windows/win32/direct3d12/resource-binding-in-hlsl)，动态索引与资源绑定。
