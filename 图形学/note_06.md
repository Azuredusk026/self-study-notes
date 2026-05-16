# 现代渲染引擎架构：从 Pass 到 Material 的进阶与 Unity ShaderLab 对应解析

## 一、 核心知识点与原理剖析

### 1. 光照优化回顾：单 Pass 多光源渲染
- **前置问题**：旧方案采用多 Pass 渲染（Forward Base + Forward Add），每个光源都需要额外进行一次全场景的 DrawCall 渲染，开销极大。
- **优化方案**：在一个 Pass 内一次性上传所有的光源数据，Shader 内部利用循环遍历每一个光进行光照累加。
- **C# 与 GPU 数据交互（Marshal 数据封送）**：
  - **内存结构差异**：在 C# 中，数组是引用类型的独立对象。若直接把带有数组的结构体传给 GPU，会导致内存不连续。而传递给 GPU 的常量缓冲区（Constant Buffer）必须是连续、密集排列的数据块。
  - **解决方案**：使用 `[MarshalAs(UnmanagedType.ByValArray, SizeConst = MaxLightCount)]` 特性将数组作为内联的“值数组”打包进结构体中；配合 `[StructLayout(LayoutKind.Sequential)]` 强制规定数据必须按代码声明的顺序进行排列，防止编译器为了性能优化而重排内存。
  - **大小计算**：放弃手动计算结构体大小，改用 `Marshal.SizeOf()` 来获取精准的封送后字节大小，以此去申请 GPU 的常量缓冲区。
- **HLSL 循环控制标签 (`[unroll]` 与 `[loop]`)**：
  - `[unroll]`：强制循环展开。编译器会将循环体代码平铺，省去循环判断的开销。适用于**循环次数固定且较短**的代码，性能更优。
  - `[loop]`：真实的流控制循环。代码会在每次迭代时做条件判断。适用于循环次数不确定、代码很长或包含高开销操作（如纹理采样）的情况。不加标签时，编译器会按内部逻辑自行判定。

### 2. 模型导入与索引缓冲区 (AssimpNet 应用)
- **AssimpNet 简介**：一套基于 Assimp 的 C# 包装库，用于读取 FBX、OBJ、GLTF 等主流的开源三维模型格式。
- **加载流程**：
  - 创建全局导入器上下文。
  - 指定路径读取文件并将其转化为 Scene（场景对象），然后提取其中的 Mesh。
  - 获取 `Vertices`（位置）、`Normals`（法线）和 `VertexColor`（顶点颜色）。若模型缺少法线，工程上通常需要基于顶点位置和面朝向重新计算生成。
- **索引缓冲区 (Index Buffer) 的补全与规范**：
  - 只有顶点缓冲区不够，复杂模型（或平滑表面的软边模型）必须引入索引缓冲区，否则无法正常组装出面。
  - **格式约束**：DirectX 11 中索引缓冲区只支持无符号整数（`DXGI_FORMAT_R32_UINT` 或 `DXGI_FORMAT_R16_UINT`），对应 C# 中需严格使用 `uint` 或 `ushort` 格式读取和传输。
  - **绘制指令更改**：在绑定索引缓冲 (`SetIndexBuffer`) 后，渲染调用的 API 必须从 `Draw` 替换为 `DrawIndexed`，渲染的数量以索引缓冲区的长度为准。

### 3. 渲染架构重构：Pass、Effect 与 Material
随着要实现的效果越来越多（光照、纯色、描边等），使用 if-else 和硬编码管理 Shader 会导致灾难，需对渲染对象进行层级抽象：
- **Pass (渲染通道)**：
  - **定义**：执行一次绘制的完整配置。它持有一套具体的 Shader 程序（Vertex/Pixel Shader）以及管线的核心状态（如深度测试方式 DepthStencilState、混合模式 BlendState、面剔除光栅化 RasterizerState 等）。
  - **职责**：设置自身状态后，发起对当前批次所有关联物体的绘制，不负责管理游戏物体的变换。
- **Effect (渲染效果/技术)**：
  - **定义**：一组 Pass 的组合，决定了一个物体最终在屏幕上的总体表现是由哪几步画出来的。
  - **例如**：`LitOnlyEffect` 内部只装配一个 Forward 光照 Pass；`LitOutlineEffect` 内部装配了一个描边 Pass 和一个 Forward 光照 Pass，渲染时需要画两遍。
- **Material (材质)**：
  - **定义**：Effect 中所需的各种外观参数的实例。
  - **作用**：让不同物体在使用相同 Effect 时拥有不同表现（如物体 A 粗白边，物体 B 细粉边）。通过在每种 Material 中维护一个逐材质常量缓冲区（Per-Material Constant Buffer）并绑定给 GPU 来实现。

### 4. 优化合批与降低 SetPass Call
- **直观渲染的缺陷**：遍历物体 -> 绑定材质 -> 遍历它的 Effect -> 遍历 Pass -> 切换管线状态并绘制。这种逐物体的渲染会导致频繁的 `SetPass Call`。
- **SetPass Call 的代价**：它是改变 GPU 渲染管线状态（更换着色器程序、混合模式等）的指令，代价比修改常量缓冲区高得多，严重打断 GPU 并行。
- **重构反向注册与聚合渲染**：
  - 为了合批，要求 **Object 注册进 Material**，**Material 注册进 Effect**。
  - 最终的渲染循环演变为：
    ```text
    遍历 Effect -> 
      遍历 Pass (执行且仅执行一次最昂贵的 SetPass Call) -> 
        遍历 Material (更新材质参数 Constant Buffer) -> 
          遍历 GameObject (更新变换矩阵，执行 DrawCall)
    ```
  - **优势**：保证管线相同的对象一次性画完，让最昂贵的 SetPass Call 次数降到最低（即场景中总 Effect 数 × 内置 Pass 数）。这正是 Unity 等商业引擎底层管线运行的本质逻辑。

### 5. 简单描边效果 (Outline Pass) 实现
- **背面膨胀法 (Backface Outline)**：
  - **顶点着色器**：让顶点顺着自身法线（Normal）向外移动一段距离，生成一个稍大一圈的外壳。
  - **光栅化状态**：开启**正面剔除 (`Cull Front`)**，只渲染背面的多边形。
  - **片元着色器**：输出固定颜色。
  - 结合后一步画出来的正常光照物体，这层背面的“壳”就会在物体周围露出一圈形成描边。

### 6. 关联与对照：Unity ShaderLab
课程重构的代码架构直接映射了 Unity 内部概念：
- **Effect** 对应 Unity 中的一整个 `Shader`（包含 `SubShader`）。
- **Pass** 对应 Unity ShaderLab 中的 `Pass {}` 代码块。
- **Material** 对应 Unity 的 `.mat` 材质资源，用于调节参数。
- **渲染状态配置**：我们写的状态代码等同于 ShaderLab 中的声明指令。例如我们用 C# 配置的 `RasterizerState` 正面剔除，等于 Unity 里的 `Cull Front`；混合模式对应 `Blend One Zero`；深度测试对应 `ZWrite On` 与 `ZTest LEqual`。
- **入口函数绑定**：我们 C# 代码传给 Shader 编译器的 `vs_main` 和 `ps_main`，在 Unity 中对应 `#pragma vertex vert` 与 `#pragma fragment frag`。

## 二、 重点术语与概念解析
- **Pass**：一次绘制的具体实施者。代表一条特定配置的 GPU 渲染管线。
- **Effect**：Pass 的容器，定义了多通道组合渲染流程。
- **Material**：为 Effect 提供独立参数数据的实例化对象。
- **SetPass Call**：指示 GPU 切换全套着色器程序及光栅化/混合状态的调用，是比 DrawCall 贵得多的性能瓶颈。
- **数据封送 (Marshal)**：在受托管内存 (C#) 与非托管内存 (C++/GPU 显存环境) 之间转换、传递、格式化数据的过程。
- **StructLayout(LayoutKind.Sequential)**：内存布局约束标签。告诉编译器“绝不要优化打乱这个结构体的字段顺序，必须按代码书写从上到下排列”，这是向 GPU 传送结构体数据的硬性前提。

## 三、 工程经验与避坑指南
- **向 GPU 传定长数组踩坑**：
  在 C# 端声明含数组的结构体给 GPU 用时，必须使用 `[MarshalAs]` 将其打包为“值数组”，并且要使用 `Marshal.SizeOf()` 计算其实际占用大小来开辟 Buffer。不要直接取其 `Length` 或使用常规 C# 数组的方式映射，必会发生显存越界或读取错乱。
- **模型面朝向全部反转**：
  这是典型的右手坐标系（OpenGL / 部分建模软件）与左手坐标系（DirectX）不匹配导致的。导入模型时，如果是 DirectX 渲染环境，需在 AssimpNet 的导入配置里添加 `PostProcessSteps.FlipWindingOrder` 参数来翻转三角面的连接顺序（即修改索引缓冲区）。
- **引缓冲区的 16/32 位精度踩坑**：
  Direct3D 的索引缓冲区强制要求**无符号整型**。代码里千万不能用 `int` 数组传数据，必须明确解析为 `uint`，且 DXGI Format 务必对应写死为 `DXGI_FORMAT_R32_UINT`。若使用 Unity，其默认上限通常是 65000（采用 `ushort` 16位），超精细模型需特定配置突破限制。
- **硬表面描边断裂现象**：
  “法线向外膨胀”的描边法，如果应用在球体等平滑表面上效果很好，但在正方体这种有“硬折角”的模型上，会在顶点处直接撕裂脱节，且会导致距离相机越近边越粗、越远边越细。此类瑕疵属于算法天生缺陷，将在后续 NPR (非真实感渲染) 课程中探讨进阶修复方案。
- **常量缓冲区（Constant Buffer）三级划分规范**：
  当架构铺开后，常量缓冲区应遵守频率分离原则以最大化性能：
  1. `Per-Frame` (逐帧更新)：相机矩阵、全局时间、全局光源。
  2. `Per-Material` (逐材质更新)：描边粗细、物体颜色表现等。
  3. `Per-Object` (逐物体更新)：M矩阵（世界变换）。
  性能开销排序：SetPass Call > 上传更新数据 > 绑定数据 > DrawCall。

## 四、 课后作业与规划
1. **短作业 (场景渲染实战)**：
   不提供源码参考，基于上节课的基底，复现出本节内容：
   - 跑通 AssimpNet 模型加载逻辑（导入球体和正方体）。
   - 将渲染结构重构成 Effect -> Pass -> Material 的逻辑以实现合批。
   - 实现可配置粗细、颜色的自定义 Outline Pass，并在同一个画面中正确区分出无描边、细描边、粗白描边等不同材质的物体。
2. **长作业 (TA 大作业预演)**：
   确立一个长线想要完成的“综合性技术 Demo 或者场景氛围图”。不需要在现阶段就考虑实现难度，重点是找准想要的视觉与交互目标，形成解决一整套问题的长期推进方向。
