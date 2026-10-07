# Unreal RDG Pass实现

RDG 用参数结构声明通道读写的纹理、缓冲和附件。图根据这些声明建立依赖，再在执行时提供 RHI 资源。资源句柄和回调跨阶段使用，需要遵守图的生命周期。

## 适用范围

采用 UE5 RDG 官方文档的参数和 AddPass 模型，核对日期为 2026-10-04。示例为 Renderer 内部通道片段，Shader 类型注册、模块依赖和实际组数由项目提供。完整编译需对应版本源码环境。

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

## 参数、引用与执行回调

参数内存用 graph allocator 分配，寿命覆盖本次执行。栈对象按引用捕获到延迟回调时可能失效，应使用图分配数据或按值捕获稳定对象。RHI 资源解析按 RDG 规定在执行范围内进行。

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

## 相关主题

- [[22_渲染引擎实现/Unreal渲染帧组织]]
- [[13_渲染架构/Render Graph]]
- [[13_渲染架构/GPU同步与屏障]]

## 参考资料

- [Epic Render Dependency Graph](https://dev.epicgames.com/documentation/en-us/unreal-engine/render-dependency-graph-in-unreal-engine)，参数、通道、外部资源与调试。
- UE5 源码：`RenderGraphBuilder.h`、`RenderGraphResources.h`、`RenderGraphUtils.h`；使用项目相同版本核对。
