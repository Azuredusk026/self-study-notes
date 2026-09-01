# Shader 语言与数据流

Shader 是运行在 GPU 特定阶段的小程序。写法像普通函数，但输入、输出、资源访问和执行方式都受管线阶段约束。

## HLSL、GLSL 和 ShaderLab

- HLSL 是 Direct3D 体系常用的着色语言，也被 Unity、Unreal 和现代跨平台编译链广泛使用。
- GLSL 是 OpenGL 体系的着色语言。
- Vulkan 常使用 SPIR-V 中间表示，源语言可以是 GLSL、HLSL 或其他前端。
- Unity ShaderLab 负责声明 SubShader、Pass、状态和属性；其中的 HLSL 才是 GPU 程序。

语言语法不是主要差异。资源绑定、坐标约定、编译目标和引擎生成代码更容易造成跨平台问题。

## 顶点输入

Vertex Shader 通常读取：

- Position；
- Normal、Tangent；
- UV、Vertex Color；
- Skin Weight 和 Bone Index；
- Instance ID 或自定义实例数据。

数据来自 Vertex Buffer。Input Layout/Vertex Declaration 说明每个属性的格式、步长和位置。Shader 声明与 Buffer 实际布局不一致时，结果可能完全错误，但 API 不一定能替你发现语义问题。

## Constant、Uniform 和 Buffer

同一个 Draw 中保持不变的小数据通常放在 Constant/Uniform Buffer：

- 变换矩阵；
- 相机和时间；
- 光源参数；
- 材质参数。

GPU 读取常量时偏好对齐后的连续布局。HLSL Constant Buffer 常以 16 字节寄存器组织，`float3` 后面不一定能按 CPU 结构体直觉紧密排列。CPU 结构、Shader 结构和 API 绑定必须使用同一布局。

大量结构化数据可以使用 Structured Buffer、Byte Address Buffer 或 Storage Buffer。它们比普通常量灵活，但访问成本、缓存行为和平台支持不同。

HLSL 用 `cbuffer` 声明常量缓冲区，并可用 `register(b0)` 指定绑定槽位。CPU 侧需要创建同样大小和布局的 Buffer，把数据写入后绑定到对应 Shader Stage。动态更新常见路径是 `Map/Unmap`：`WRITE_DISCARD` 取得一段可重新分配的写入区域，适合整块替换；`NO_OVERWRITE` 保证不会覆盖 GPU 尚未读取的区间，适合环形缓冲中的追加写入。两者都要求 CPU 明确管理正在飞行的帧和资源寿命。

常量应按更新频率分组，而不是把所有参数塞进一个大 Buffer：

- Per-frame：时间、全局环境；
- Per-view：相机、投影和曝光；
- Per-material：材质参数；
- Per-draw：对象矩阵和对象 ID。

频率分组能避免只改一个对象时重新上传全局数据。Unity SRP Batcher 要求材质属性位于 `UnityPerMaterial`，引擎按对象提供的数据位于 `UnityPerDraw`，并保持各 Pass 的布局一致。违反布局约定会失去批处理兼容性或读到错误偏移。

## 资源视图与访问权限

同一底层资源可以通过不同视图进入管线。Direct3D 常见名称包括：

- SRV（Shader Resource View）：Shader 只读访问纹理或 Buffer；
- UAV（Unordered Access View）：Shader 随机读写，常用于 Compute 和图像写入；
- RTV（Render Target View）：作为颜色输出；
- DSV（Depth Stencil View）：作为深度模板输出。

视图决定格式解释、Mip、数组层和允许的访问方式，不等于复制一份资源。资源从 Render Target 写入转为 Shader 读取时，现代显式 API 还需要正确的 Resource State、Barrier 和同步范围。把仍在写的资源同时当作 SRV/UAV 读取，会形成读写冲突；调试时应同时检查视图、槽位和状态转换。

## Texture 和 Sampler

Texture 保存数据。Sampler 描述如何读取：过滤、寻址、LOD 等。

它们在某些 API 中可以独立绑定，也可以组合成一个对象。引擎可能复用 Sampler，避免每张纹理重复创建相同状态。

一次纹理采样包含：

1. 计算坐标；
2. 选择 Mip；
3. 应用寻址；
4. 读取一个或多个 Texel；
5. 执行过滤；
6. 必要时做格式解码，例如 sRGB 到 Linear。

因此“只采了一张纹理”并不等于只读一次显存。

## Varying 和插值

Vertex Shader 输出会在三角形内部插值，再进入 Pixel Shader。常见数据有 UV、世界位置、法线和颜色。

注意：

- 方向插值后通常需要重新归一化；
- 使用太多 Varying 会增加寄存器和带宽压力；
- `flat/nointerpolation` 不做插值，适合 ID 等离散数据；
- `noperspective` 使用屏幕线性插值，不做透视修正。

## Semantic 和 Location

HLSL 常用 `POSITION`、`TEXCOORD0`、`SV_Position` 等 Semantic 连接阶段。GLSL/Vulkan 常用显式 Location。

System Value 表示管线提供的特殊数据，例如 Vertex ID、Instance ID、Position、Depth。它们不是普通顶点属性。

## 精度

`float`、`half`、`min16float` 的实际位宽和运算方式受目标平台、编译器和 GPU 影响。桌面 GPU 可能把 `half` 仍按 32 位执行，移动 GPU 则可能真正受益。

低精度容易出问题的位置：

- 大世界坐标；
- 深度和重建；
- 长时间累积；
- HDR 亮度；
- 很小的法线或概率值。

精度优化必须看编译结果和目标硬件，不应只改类型名。

## 分支

### 编译期分支

预处理宏会产生不同程序。未选中的代码不会进入当前变体，但组合过多会增加编译、包体和加载成本。

### 运行时分支

条件在运行时判断。若同一 Wave 中线程走不同路径，GPU 可能依次执行两边并屏蔽不参与的 Lane。

运行时分支不一定慢：

- 条件在整个 Draw 中一致时，通常不会产生像素间发散；
- 分支能跳过很重的工作时可能值得；
- 很短的分支可能被编译器改成无分支选择。

## Shader Graph

Shader Graph 是生成 Shader 代码的前端，不是另一种 GPU 管线。节点最终仍会变成采样、算术、分支、Varying 和 Pass。

检查 Shader Graph 性能时，要看生成代码、变体、纹理采样数和最终编译指令，不能只数节点。

## 调试方法

- 检查编译后的 HLSL、SPIR-V 或 ISA，而不只看源代码。
- 在 RenderDoc 中检查资源绑定、Constant Buffer 和 Shader Input/Output。
- 用纯色或方向 RGB 逐段验证中间结果。
- 对比引擎坐标转换函数和手写矩阵结果。
- 在不同平台检查精度、UV 原点、深度范围和纹理格式。

## 相关主题

- [[02_GPU与光栅化管线/一帧如何到达屏幕]]
- [[03_Shader编程/Shader编译、关键字与变体]]
- [[03_Shader编程/Compute Shader与GPU执行模型]]
- [[06_纹理技术/纹理采样、过滤、Mipmap与压缩]]

## 参考资料

- Microsoft Learn, *HLSL Reference*.
- Khronos, *OpenGL Shading Language Specification*.
- Unity Manual, *Writing shaders*.
