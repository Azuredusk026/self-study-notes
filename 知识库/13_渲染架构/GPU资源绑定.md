# GPU资源绑定

材质参数已经上传，着色器却采到别的纹理，问题可能出在绑定表与对象寿命。描述符告诉GPU从哪里、按什么格式读资源，它不负责上传数据，也不负责完成写后读同步。先把布局、索引和更新频率对应起来，再检查GPU尚未结束访问时哪些槽位不能复用。

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

### 从着色器接口建立布局

以一条Vulkan图形管线为例：顶点阶段从set0/binding0读取相机uniform buffer；片元阶段从set1/binding0读取材质动态uniform buffer，从set1/binding1读取一张combined image sampler。宿主创建两个descriptor set layout：set0的binding0类型为UNIFORM_BUFFER、数量1、阶段VERTEX；set1的binding0为UNIFORM_BUFFER_DYNAMIC、数量1、阶段FRAGMENT，binding1为COMBINED_IMAGE_SAMPLER、数量1、阶段FRAGMENT。管线布局按set0、set1的次序引用这两个布局，着色器反射得到的set、binding、数组数量和资源类型逐项与之对应。

随后从能容纳这些类型与数量的描述符池分配集合，更新相机缓冲视图、材质缓冲视图和纹理采样视图。更新材质binding0时描述符基础偏移取0、range取80字节；bind调用绑定set1并传一项动态偏移，决定本次读取哪条80字节记录。这里着色器仍声明普通uniform块，动态寻址由描述符类型与绑定参数决定。把它误建为STORAGE_BUFFER，或将纹理写到binding0，不能靠传入正确地址修复，因为着色器使用的解释方式已经不同。

80字节记录也需要两端有相同字段布局。可用std140块包含一个列主序mat4和一个vec4，矩阵在偏移0占64字节，向量在偏移64占16字节。CPU按这份反射布局填充，不以某个宿主结构体恰好sizeof为80替代字段偏移检查。矩阵上传转置与否沿两端列向量约定确定；偏移正确却矩阵主序相反，仍会得到合法读取下的错误变换。具体布局规则见[[03_Shader编程/Shader接口与数据流]]。

### 管线切换与兼容性

设管线P使用上述set1，管线Q却把set1/binding1改成采样图像数组，并另加独立sampler。即使两个布局都有binding1，它们的类型、数量与其他绑定不同，P的材质集合不能直接交给Q。为Q分配按Q布局创建的集合，更新其数组与sampler，再显式绑定；资源底层图像可以共享，描述符集合的接口并不因此兼容。

Vulkan集合兼容还涉及管线布局中此前集合的布局与push constant范围。本文采用容易审查的绑定策略：每次切换管线，按该管线的布局显式绑定所有将被使用的集合，并写入它实际消费的push constants。这样不依赖先前管线留下的绑定状态；进一步省略重绑时，才按规范逐集合证明兼容前缀和常量范围，不能仅比较当前set编号或资源地址。布局兼容只证明着色器能解释绑定，内容版本、资源状态与寿命仍由后续步骤保证。

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

例如记录大小 80 字节、设备要求 256 字节对齐，步长取 256；第 3 条记录偏移为 768 字节。描述符基础偏移若已包含 `frameBase`，动态偏移就只加记录内偏移，否则帧基址会加两次。绑定范围还需满足“基础偏移 + 动态偏移 + range”不超过缓冲大小，正确对齐本身不能证明地址有效。

绑定之前还要完成数据生产。CPU先取得已满足完成条件的帧区间，在`frameBase+materialIndex*stride`复制材质记录；非一致映射内存按设备的非一致原子大小对齐刷新范围，一致内存则遵守宿主写入与队列提交的同步约定。描述符的基础偏移可以取0、range取一条记录大小，动态偏移包含帧与记录地址；也可以把帧基址放进描述符，二者只选择一种计址方式。提交后该区间保持只读，完成值达到后再复用。上传与寿命的完整规则见[[13_渲染架构/GPU资源生命周期]]和[[13_渲染架构/GPU同步与屏障]]。

例如双帧缓冲每帧占4096字节，第二帧第3条记录的动态偏移为`4096+3*256=4864`。描述符基础偏移0、range80时读取`[4864,4944)`；若描述符基础偏移又设为4096，实际读到8960附近，上传正确也会串帧。CPU写完但未刷新非一致内存则是另一类失效：地址正确，GPU仍可能看不到新内容。分别检查GPU读取地址与内存可见性，才能把绑定错位和上传失效分开。

### 缓冲偏移与映射偏移

描述符寻址相对缓冲开头，内存刷新相对`VkDeviceMemory`开头，CPU指针则相对映射起点。这三个原点必须先对齐。设缓冲绑定在内存对象的字节偏移B，映射从内存偏移M开始，记录在缓冲内的偏移为O，则CPU写入地址是`mappedPointer+(B+O-M)`；刷新使用内存偏移`B+O`，描述符仍使用缓冲偏移O。把B再次加到描述符里，会把GPU读址推向另一份记录。

例如B=8192、M=4096、O=4864，CPU指针偏移为8960，内存写入区间为`[13056,13136)`，描述符读取的缓冲区间仍为`[4864,4944)`。非一致原子大小若为256字节，刷新区间扩为`[13056,13312)`。分配器保证扩张区间处于映射内；到内存分配末尾的范围按API允许的末尾规则处理，不能越界刷新。

帧区间按这份刷新粒度隔离。两帧的有效记录即使没有重叠，共享一个非一致原子也可能让宿主刷新与GPU访问发生冲突。把帧起点和预留容量按动态缓冲对齐与非一致原子对齐的公倍数取整，并将扩张后的范围纳入在途占用检查；同帧记录可以共享原子，前提是统一写完、刷新后再提交。这样绑定对齐、内存可见性和帧寿命才使用同一份区间记录。

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

### 资源索引的生产与发布

索引首先来自CPU资源注册表。表项保存资源ID、资源代数、描述符槽位、加载状态和强引用；材质计划保存资源ID，在生成渲染快照时解析成有效槽位。未就绪纹理指向永久有效的回退槽位0，着色器不会拿尚未分配的槽位猜测资源是否可用。索引范围由实际数组容量检查，空洞也写合法回退描述符，或按设备能力启用部分绑定并保证着色器永远不访问未绑定项。

纹理B加载完成时，先创建兼容的图像与视图，上传内容并建立消费队列等待，再分配新槽位8、写入B的描述符。这里采用不可变描述符页：已发布给录制快照的页保持不变；需要新描述符就建立新的集合或堆页，并只写尚未被录制引用的页。页封闭后构造新的材质记录，记录textureIndex=8，同时保存它所属的描述符页身份。B的上传完成依赖也挂在这份快照上；描述符写完不等于像素已经上传完毕。

CPU在快照发布锁内把新材质记录、描述符页、资源引用和上传依赖一起发布。录制者先取得这一整份不可变快照，再写绘制命令。它绑定快照所属的页，上传同版本的材质表，并把对象索引与材质索引交给着色器。若页A的槽位8为红、页B的槽位8为蓝，来自页A的记录不能配页B绑定；只保存整数8会丢掉这个依赖。需要按设备能力在已绑定页内更新时，另按update-after-bind等规则设计，本条基线通过页不可变避免在途修改。

推送常量可携带对象索引和材质索引。偏移0保存对象索引12，偏移4保存材质索引3，着色器先取对象12的变换，再取材质记录3中的textureIndex=8，最后从本快照描述符页槽位8采样B。三个索引分别进入不同表；不能把材质编号3直接当纹理槽位3。每级表大小、元素布局和资源版本在快照中保持一致。

### 录制引用、提交与回收

资源从快照发布开始就可能被命令使用，回收条件必须覆盖尚未提交的录制。这复用[[13_渲染架构/GPU资源生命周期]]的保留、提交、完成三态，绑定层再把描述符页、材质版本与纹理绑定成同一个保留单位。资源管理器为每份快照保存发布引用，录制任务在同一锁内取得保留令牌，令牌持有材质表、描述符页、纹理及上传区间。发布新快照只释放旧快照的发布引用；旧录制令牌仍保持旧页和旧纹理存活。

假设旧页槽位7指向A，录制线程R已取得旧快照，但尚未提交。CPU发布B后，图形队列当前完成值已经追上所有已提交工作，也不能回收A，因为R仍可能提交引用7的命令。回收器同时检查发布引用、录制保留以及所有队列的在途引用，三者均为空才释放页或资源。槽位随所属页一起回收；页内局部复用需要同样证明没有任何旧记录可达该槽位。

提交协调器把R的令牌移交给提交记录，整个交接期间至少有一方持有。成功提交并登记完成值之后，提交记录接替录制任务保留引用；多队列访问保存各队列最后值，或使用覆盖全部访问的汇合完成值。GPU完成后释放提交引用，才可能满足回收条件。提交后Signal失败时保持提交引用并进入设备故障处理，不能因为没拿到完成值就按“未提交”释放，详见[[13_渲染架构/Command Buffer与帧提交]]。

取消录制则先让所有记录任务停止并确认该列表永远不会再提交，再丢弃命令并释放录制令牌。取消与提交竞争时，由同一个状态锁把Recorded原子转为Submitting或Cancelled；取消看到Submitting就交给提交路径完成回收。工作线程尚在读取快照时只设置取消请求，不能立即释放令牌。这样首次录制、延迟提交、取消与设备故障都有对应的持有者。

## 绑定成本

改参数值、改纹理视图和改静态关键字分别影响上传、描述符更新和着色器/PSO 组合。Bindless 减少逐材质绑定，仍有描述符访问、纹理缓存、索引传输与生命周期维护成本。

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

- [Vulkan VkMappedMemoryRange](https://docs.vulkan.org/refpages/latest/refpages/source/VkMappedMemoryRange.html)：刷新偏移相对内存对象，范围受映射与非一致原子对齐约束。
- [Vulkan Resource Descriptors](https://docs.vulkan.org/spec/latest/chapters/descriptorsets.html)。
- [D3D12 Root Signatures](https://learn.microsoft.com/en-us/windows/win32/direct3d12/root-signatures)。
- [NonUniformResourceIndex](https://learn.microsoft.com/en-us/windows/win32/direct3d12/resource-binding-in-hlsl)，动态索引与资源绑定。
