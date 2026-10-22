# Unreal RDG Pass实现

计算通道里确实写了纹理，结果却没显示出来，先看输出有没有被RDG的后续通道消费。RDG从参数结构读取资源关系，回调只负责执行具体工作。把输入、UAV、输出所有者和回调寿命说清以后，图才知道什么时候执行与回收。

## 适用范围

采用 UE5.4 RDG 官方文档的参数和 AddPass 模型，核对日期为 2026-10-22。示例为 Renderer 内部通道片段，Shader 类型注册、模块依赖和实际组数由项目提供。完整编译需对应版本源码环境。

## 计算通道示例

输入与输出是 RDG 纹理，计算 Shader 的参数结构已声明对应 SRV/UAV。输出需要被后续通道读取或按引擎接口导出。

```cpp
FExampleCS::FParameters* parameters =
    graphBuilder.AllocParameters<FExampleCS::FParameters>();
parameters->InputTexture = inputTexture;
parameters->OutputTexture =
    graphBuilder.CreateUAV(FRDGTextureUAVDesc(outputTexture));
TShaderMapRef<FExampleCS> shader(view.ShaderMap);
FComputeShaderUtils::AddPass(
    graphBuilder,
    RDG_EVENT_NAME("ExampleCompute"),
    shader,
    parameters,
    groupCount);
```

输出参数需使用 RDG UAV 宏声明，输入使用对应纹理或 SRV 宏。宏中的资源类型决定图看到的访问；把资源藏在不受图跟踪的全局状态里，可能使依赖和回收判断错误。

## 参数布局与线程覆盖

以下是UE5.4风格的参数结构片段，放在`FGlobalShader`派生类型中。输入为单采样二维纹理，输出为支持UAV的浮点RGBA纹理；`Extent`使用像素单位，二者尺寸一致。模块、生成Shader类型与虚拟Shader路径注册仍由宿主提供。

```cpp
BEGIN_SHADER_PARAMETER_STRUCT(FParameters, )
    SHADER_PARAMETER(FIntPoint, Extent)
    SHADER_PARAMETER_RDG_TEXTURE(Texture2D, InputTexture)
    SHADER_PARAMETER_RDG_TEXTURE_UAV(RWTexture2D<float4>, OutputTexture)
END_SHADER_PARAMETER_STRUCT()
// 每组8×8线程，向上取整覆盖完整纹理。
parameters->Extent = outputTexture->Desc.Extent;
FIntVector groupCount = FComputeShaderUtils::GetGroupCount(
    parameters->Extent, FIntPoint(8, 8));
```

与之对应的HLSL机制片段直接展开一次读写。它假设输入含有效颜色，输出每个像素只有一个写者，坐标不涉及滤波和UV缩放：

```hlsl
Texture2D<float4> InputTexture;
RWTexture2D<float4> OutputTexture;
int2 Extent;
[numthreads(8, 8, 1)]
void MainCS(uint3 tid : SV_DispatchThreadID)
{
    if (any(tid.xy >= uint2(Extent))) return;
    float4 value = InputTexture.Load(int3(tid.xy, 0));
    OutputTexture[tid.xy] = float4(value.rgb * 0.5, value.a);
}
```

17×9输出需要`ceil(17/8)×ceil(9/8)=3×2`组，共384个线程，其中153个在有效像素内，231个通过边界判断退出。宽度为17时，需要3组线程，最后一组只有一个有效横坐标。没有边界判断就会访问目标外区域；组数向下取整则会漏掉最后一列。先用17×9输入验证边缘，再用逐像素编号图检查映射，能把dispatch范围错误与颜色算法错误分开。

这里把RGB乘0.5只是便于辨认输出的数值操作，尚未定义曝光与色调映射阶段。真正的相机效果要把输出交给后续颜色通道，离线测试则用`QueueTextureExtraction`保存结果；提取指针的存储位置必须活到图执行完毕。

## 参数、引用与执行回调

设记录函数在CPU时刻0建立局部参数`strength=0.5`，时刻1返回，图在时刻2才执行回调。按引用捕获strength就指向已结束寿命的栈存储；按值把0.5放进图分配的参数，才使回调读取这次记录的值。长期共享对象也不自动安全：若另一个视图在时刻1.5把它改成0.8，本视图会执行错误参数。

记录通道的函数返回以后，回调可能还没执行。若它按引用捕获了局部栈对象，执行时引用就可能失效。参数使用graph allocator，让内存覆盖图执行；其他数据按值捕获或交给明确的长期所有者。RHI资源也在RDG允许的执行范围解析。

`ERDGPassFlags::Compute`、Raster、Copy 与 AsyncCompute 表示执行类型。异步标记需要实际资源依赖和平台支持，标记本身不保证收益。GPU 资源与 CPU 对象寿命仍要分别管理。

## 导入与导出

已有历史或外部纹理可以注册为 external resource，使图知道访问关系。导出结果需使用对应提取接口，在图执行后获得外部所有者可保存的引用。下一帧再导入，并检查描述变化与历史有效性。

外部资源、显式副作用和提取结果可以形成有效输出，所以“没有后续通道采样”不等同于一定剔除。调试时先检查图对输出的可观察性，再考虑禁用剔除定位。

## 光栅通道

Raster 通道参数声明颜色与深度附件及 load/store，回调设置 viewport 并执行绘制。参数结构中无实际使用的资源应按引擎工具清理，避免假依赖阻止剔除、合并或内存回收。

网格通道与全屏通道共享附件，但网格处理器的筛选、排序和 Shader 选择属于另一个层次。RDG 只根据声明管理资源，不能推导材质内部未表达的访问。

## 成本和故障

资源声明过宽会延长寿命，阻止复用并增加屏障。声明不足会导致数据竞争或未初始化读取。人为用所有阶段屏障掩盖错误，可能让输出正确但关键路径串行。

图内别名、异步和剔除应分别开关测试。模式变化时输出不同，优先查初始化、捕获对象寿命、读写范围和外部副作用。

## 验证方法

- 为每帧输入写入编号，输出可视化编号和 Shader 结果。
- 将输出接入明确消费者，再通过图调试工具检查依赖。
- 关闭剔除、别名和异步分别复现，记录哪个开关改变错误。
- 在图外提取历史，连续切换相机尺寸并检查重建。
- 查看 UAV 写后读、资源格式、group count 与边界裁剪。

## 编译证据

2026-10-22运行[verify.py](../examples/revision_22_26/verify.py)，从本页提取`MainCS`，DXC以`cs_6_0`编译通过；[结果记录](../examples/revision_22_26/results.json)包含工具版本。命令为`python 知识库/examples/revision_22_26/verify.py`。此检查只证明HLSL语法与入口可编译，UE参数绑定、模块编译、dispatch与输出消费尚未运行（UNVERIFIED）。

## 相关主题

- [[22_渲染引擎实现/Unreal渲染帧组织]]
- [[13_渲染架构/Render Graph]]
- [[13_渲染架构/GPU同步与屏障]]

## 参考资料

- [Epic Render Dependency Graph](https://dev.epicgames.com/documentation/en-us/unreal-engine/render-dependency-graph-in-unreal-engine?application_version=5.4)，Shader Parameter Structs、Resource Lifetimes和External Resources章节，参数、通道、外部资源与调试。
- UE5 源码：`RenderGraphBuilder.h`、`RenderGraphResources.h`、`RenderGraphUtils.h`；使用项目相同版本核对。
