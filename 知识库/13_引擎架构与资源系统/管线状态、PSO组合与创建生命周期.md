# 管线状态、PSO 组合与创建生命周期

管线状态对象（PSO）保存 GPU 绘制或计算所需的一组状态。Shader 字节码相同的两次绘制，也可能因为颜色格式、混合、深度或样本数不同而需要不同 PSO。理解组合范围，才能解释预热为何有遗漏。

## 状态组成

图形 PSO 通常涉及着色器阶段、资源布局、顶点输入、光栅化、深度模板、混合、附件格式与样本数。哪些状态固定在对象里、哪些可动态设置由 API 和启用特性决定。

Vulkan pipeline layout 约束 descriptor 和 push constant 接口；D3D12 root signature 表达根参数。不能只用 Shader 名称作为缓存键。动态状态不一定进入相同的键，但设置责任仍在绘制路径。

## 缓存键

下面是平台中立的数据结构轮廓。具体键包含目标 API 真正参与编译与兼容性判断的字段。

```cpp
struct GraphicsPipelineKey
{
    Hash shaderStages;
    Hash bindingLayout;
    Hash vertexLayout;
    Hash rasterState;
    Hash depthStencilState;
    Hash blendState;
    Format colorFormats[MaxTargets];
    Format depthFormat;
    uint32_t sampleCount;
    uint64_t dynamicStateMask;
};
```

缓存命中后仍需确认对象属于当前设备。磁盘缓存要带驱动、设备和 API 兼容信息；源码或编译选项变化后应失效。缓存键编码需要稳定，避免结构 padding 或未初始化字段进入哈希。

## 创建与使用

```text
材质/Shader 组合 → 状态归一化 → 查缓存
                                  ├─ 命中：复用对象
                                  └─ 未命中：编译/创建 → 入缓存
GPU 最后使用完成 → 可回收对象及相关布局
```

创建可能涉及驱动编译，CPU 耗时和首次使用时的隐藏工作都需要观察。预热只覆盖列出的完整组合。材质变体、不同 render target 和 MSAA 档位可能生成采集时没有遇到的键。

## 与 Shader 变体的关系

静态关键字改变编译结果，PSO 将结果与渲染状态组合。动态分支减少部分 Shader 组合，可能增加运行时着色成本。渲染状态通常不能简单转成材质 uniform；它们仍决定固定功能行为。

具体缓存收集、构建预编译与卡顿治理见性能专题。机制页负责对象与组合定义，性能页记录采集和测量。

## 验证方法

- 保持 Shader 不变，只改变附件格式或样本数，确认缓存键与对象正确区分。
- 记录创建线程、键、命中来源和耗时，定位首次进入场景的尖峰。
- 清空缓存与预热缓存分别运行相同路线，对比首次使用和第二次使用。
- 改编译版本，确认旧磁盘数据被识别为不兼容。

## 相关主题

- [[14_性能分析与优化/PSO首次使用为什么卡顿]]
- [[03_Shader编程/Shader编译、关键字与变体]]
- [[13_引擎架构与资源系统/资源绑定、描述符与材质数据组织]]

## 参考资料

- [D3D12 Pipeline State](https://learn.microsoft.com/en-us/windows/win32/direct3d12/managing-graphics-pipeline-state-in-direct3d-12)。
- [Vulkan Pipelines](https://docs.vulkan.org/spec/latest/chapters/pipelines.html)。
- Epic Games，PSO Precaching 和 Shader Development 官方文档。
