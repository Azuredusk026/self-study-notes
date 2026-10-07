# 知识库批量迁移全文验收报告

验收日期：2026-10-07。范围：`E:\docs\projects\self-study-notes`，基线提交 `b5d057f`。

## 验收结论

本轮已完成用户授权的四层实施：方案B领域迁移、冻结标题采用、113页正文复读与必要修订，以及全局路径、引用、登记和机制回归。正文工作分为六个15–25页子批次，各自保留独立提交。

结构与命名落地通过静态验收，75页标题为PASS，27页为SPLIT，11页为OVERVIEW。38项标题按既定边界保留延后采用状态，其中27项保留待拆边界。它们属于用户明确要求保留的结果，正文内部已整理，拆文与依赖边界的最终命名继续按独立任务验收。

全文处理覆盖完成不代表每篇已经获得用户文风认可，也不代表全部引擎代码运行通过。《描边》沿用用户认可的标杆；其余页面提供逐页修订、自检和证据，供阅读评审。完整Unity/Unreal工程、帧捕获及目标GPU性能未执行。

## 实施范围与数量

| 项目 | 结果 |
|---|---:|
| 主题文章 | 108 |
| 说明页 | 5 |
| 最终路径表 | 113，唯一且无大小写冲突 |
| 正文处理覆盖 | 113/113 |
| 一级领域 | 27，包含00说明领域 |
| 本轮路径变化 | 70 |
| 本轮主目录变化 | 31 |
| 本轮文件名变化 | 58 |
| 历史命名映射 | 79 |
| 标题PASS | 75 |
| 延后标题 | 38：27 SPLIT、11 OVERVIEW |
| 待拆文章边界 | 27 |
| 已采用图片资产 | 2 |

路径变化、目录变化和文件名变化存在交集，不能相加。统计基线是本轮开始时的113页；历史映射还包含此前试点采用记录。

## 结构与标题验收

最终目录与标题在移动前冻结，执行一次组合迁移。文件移动同步H1、Wiki双链、Markdown内链、地图、当前登记与历史映射目标。目录与命名批次的正文保护核对确认技术正文未因移动顺手改写；技术修订集中在后续正文批次。

方案B形成以下职责分工：

| 领域 | 页面数 | 主要职责 |
|---|---:|---|
| 13_渲染架构 | 14 | 帧组织、资源寻址、同步、寿命与光照路径 |
| 22_渲染引擎实现 | 6 | 指定Unity/Unreal版本的渲染入口 |
| 23_引擎运行系统 | 3 | 世界对象、任务与异步资源 |
| 24_游戏音频 | 1 | 音频回调、Voice与混音 |
| 25_UI与文本 | 1 | 布局、字形与绘制 |
| 12_光线追踪 | 2 | 光线查询、采样与降噪 |
| 26_GPU驱动与虚拟几何 | 2 | GPU可见列表、层级几何与流送 |

Billboard归属08_几何与网格，植被风动归属09_动画系统。单页领域按独立模型保留，数量只用于复查。

标题审查覆盖113页，采用标题均为PASS，全部SPLIT/OVERVIEW保持延后状态。Render Graph作为主概念命名示范，必要工程限定保留；联合标题中的待拆问题以明确状态登记，短标题不会代替边界处理。

## 正文修订与技术结果

### P0：渲染架构、GPU与Shader

Render Graph补足版本键、生产者表、内容依赖与执行依赖、反向保活、拓扑排序和闭区间寿命。参考编译器先按内容保留通道，再建立存活通道的RAW/WAR/WAW约束，避免用覆盖顺序错误保留无用写入。旧版本读取与后续覆盖冲突能够报错。它使用每个资源名一份物理资源的串行模型，15项CPU检查通过。

GBuffer补清字段契约、法线编码、UNORM量化和整数分类。264项CPU往返检查覆盖低位浮点量与高位分类；HLSL探针编译通过。半精度、真实附件读写和GPU过滤未执行。

资源同步、附件、命令提交、PSO、Shader Variant与核心采样页重新组织问题家族和机制层级，修正通用深度比较、精度、Tile复用和性能数字的条件。NPR材质与角色联合页按材质层、数据和光照整理；待拆角色边界保持登记。

### P1：几何、动画、光照、光追与性能

空间变换分清存储与向量约定，旋转公式统一四元数分量顺序。动画页补逆绑定同空间与额外根运动前提、混合映射法线规则、零权重处理、组合表情和目标拓扑约束。压缩与面部引用分别归到对应资料。

SH统一为3个band、截止阶数l=2的9系数表示，余弦卷积按band因子解释。纹理完整mip链预算修正为约4/3基级载荷，1024×1024 BC1块载荷为699064字节，设备对齐另计。ASTC LDR/HDR支持分别查询。

水面补完整Gerstner位移与单位，修正周期合成、反射成本排序和浅水衰减的适用范围。Froxel保留透射加权合成，补历史坐标约定。皮肤扩散剖面补分母d，按环面积检验归一化；散射合成区分已包含与未包含原漫反射。

GPU驱动页补容量溢出与间接计数约束，光追页补平行射线和历史深度可比空间。性能页把逻辑流量、外存流量、局部着色收益与整帧关键路径分开，VRS、半精度和移动持续性能按设备条件描述。

### P2/P3：资产、运行、玩法、AI、网络与生成管线

资产页按身份、增量构建、事务与发布整理。Houdini Point/Vertex属性解释、备用参数创建以及UI mip策略补清。运行系统区分依赖发现链与执行链、单请求延迟与稳定吞吐，清除加载代码中混入的历史目录。

玩法事件片段交换当前与下一轮队列，保护递归Flush，并记录处理器异常后继续派发。正文C#片段由最小宿主提取编译，3项行为检查通过。圆与盒碰撞补盒内圆心的出射面和完整修正深度；XPBD片段补零分母与时间步前提。

AI决策与导航整理世界表示、搜索、局部控制和计划家族，约束中止、特权信息与模型度量范围。网络页补固定线上头长、总长度溢出与超长包退出，插值时间使用服务器时间之前的显示点；回滚副作用和权威状态单列。

生成管线按任务状态、模型条件、失败恢复与输出审核组织。ComfyUI历史重采样使用当前像素上的反向光流，前向流不能直接取反替代。模型、节点和种子只在明确环境约定下讨论可复现性。

### 保留与轻重

《描边》全文复读后保留正文与既有两张解释图。导读页保持问题路线，说明页同步现行目录、作者规则和实施记录。有效段落、代码和资料按主题保留，修订力度可在逐页changed_sections与实际Git diff中检查。

## 自动验收与证据

| 检查层 | 结果 | 能证明的范围 |
|---|---|---|
| 冻结路径、H1、唯一性 | 113页通过 | 路径字段与当前文件一致 |
| Wiki与Markdown内链 | 全局通过 | 目标存在；实际锚点按出现数量验证 |
| 反链与知识地图 | 无孤立页、全部收录 | 页面可从地图或关系入口访问 |
| Related Topics与参考资料 | 108主题页通过 | 必要章节与本地引用存在 |
| 标题与目录登记 | 无未审查项 | 113页当前状态与主归属一致 |
| 历史章节映射 | 63条通过 | 目标与现行章节可定位，原文标题保留历史含义 |
| 代码围栏、层级与路径污染 | 通过 | 围栏语言、闭合、标题跨级与已知污染模式 |
| 图片资产 | 2项通过 | 路径、哈希、来源、许可说明与使用登记 |
| Git diff | diff --check通过 | 空白与暂存范围检查；变更对应批次或全局修复 |
| 写作、深度与事实 | 全文自检记录 | 逐篇阅读评审与完整外部核验另列 |

当前正文没有带锚点的实际内链，因此锚点扫描数量为0；历史章节映射的63条是另一组具体章节校验。检查器另用故意损坏的H1、锚点、路径和状态夹具验证能报告失败，8项检测检查通过。结果见 [检查器回归](../batch-validator-tests.json)。

### 真实执行的机制回归

| 实验 | 检查数 | 环境与范围 |
|---|---:|---|
| 原有A*、深度、扫掠单位、模板与体积前缀 | 115 | Python CPU |
| 描边参考函数 | 43 | Python CPU，未执行Shader画面 |
| Render Graph参考编译器 | 15 | 串行CPU图模型 |
| GBuffer量化往返 | 264 | R8_UNORM CPU模型 |
| mip、碰撞、Slab、Gerstner、扩散能量、TAA权重、TCP分帧 | 83 | Python CPU模型 |
| 事件队列正文片段 | 3 | .NET SDK 10.0.401 Release，模拟处理器宿主 |
| 合计 | 523 | 检查项数，不能解释为523个引擎场景 |
| HLSL探针 | 3 | DXC 1.9：OutlineVS、OutlinePS、ProbePS |

运行命令与原始输出见 [测试结果](../batch-test-results.json)，路径与引用结果见 [静态验收](../batch-validation-results.json)。检查器不评分文风，模型实验不证明GPU性能，探针编译不证明完整ShaderLab或引擎工程可运行。

### 资料核对范围

重点核对RDG参数与资源、URP图流程、Vulkan执行/内存依赖与附件字段、D3D12 PSO与allocator Reset，以及当前Epic PSO预缓存内存策略。补读ACL目标与ASTC profile说明。具体断言、条件、来源与定位见 [断言登记](../batch-claim-review.json)。

取回网页只说明资料可获取。全库参考书目、源码版本和内部实现没有逐条完成外部核验；无法确认的普遍结论采用明确条件或保留待验证。没有给未执行的引擎、捕获或设备测量写“通过”。

## 九维验收结果

| 维度 | 本轮结论 |
|---|---|
| 范围 | 逐页复读完成；27项待拆边界按授权保留，最终单问题验收延后 |
| 结构 | 问题家族与子机制按实际主题整理，静态标题检查通过 |
| 深度 | 核心架构参考实现补足；全库按机制与排错复读，自检不代替用户逐篇评价 |
| 实现 | CPU、.NET与HLSL证据通过；完整引擎工程待验证 |
| 证据 | 重点断言可追溯；全部引用未逐条独立核验 |
| 写作 | 113页有记录；描边保留用户认可，其余为本轮自检与待阅读评审 |
| 标题 | 75 PASS；38边界/导读项延后，未审查项0 |
| 信息架构 | 方案B落地，27领域使命与113页主归属一致 |
| 视觉 | 2项采用资产检查通过；来源许可未知图片保持候选 |

## 提交与回滚边界

目录与命名使用组合移动提交，正文使用15–25页子批次提交。全局验收提交同步检查器、实验、报告和最终状态。回滚时按实际依赖选择提交范围：撤销结构迁移需一并处理后续引用与正文路径，不能单独删除某个目录。

| 提交 | 阶段 | 内容 |
|---|---|---|
| a1ce467 | Batch0 | 冻结113页最终路径与标题 |
| b8cafde | Batch1–2 | 领域归位与标题一次迁移 |
| 6de6394 | Batch3-P0-A | 21页渲染架构与核心修订 |
| ba93fc8 | Batch3-P0-B | 20页采样颜色与GPU修订 |
| 4e626da | Batch4-P1-A | 20页几何动画光照VFX |
| 8045bc0 | Batch4-P1-B | 20页光追性能与引擎接入 |
| 162fef2 | Batch4-P2-A | 17页资产编程物理玩法AI网络 |
| 9160f31 | Batch4-P2-P3-B | 15页生成管线、导读与说明复读 |
| 本报告所属全局验收提交 | Final | 检查器、523项回归、报告与最终登记 |

原始基线、临时工作脚本和来源缓存位于仓库外 `E:\docs\projects\self-study-notes-审计-2026-10-07\批量迁移`。正式映射、质量矩阵、实验源和报告随仓库发布；docs与构建日志遵循本机维护层的忽略规则。

## 保留事项与实际限制

1. 27项待拆边界与11项导读标题按用户指令保持延后，本轮没有创建拆分正文。
2. Unity/Unreal完整导入编译、运行、GPU帧捕获、跨队列和性能未执行；需要目标工程与设备完成这层验收。
3. 独立语言和深度评价仍需阅读正文；本轮全文自检提供证据与diff，没有用扫描词频代替判断。
4. 全库书目与源码尚未逐条核验，重点断言登记明确了实际范围。版本敏感片段不能当作无条件生产补丁。
5. 外部图片许可未确认的资产保留候选，自制SVG明确属于模型图或CPU结果。

## 目录完整清单

| 目录 | 页数 | 使命 |
|---|---:|---|
| 00_知识库说明 | 5 | 知识库导航与作者规则 |
| 01_数学与采样 | 4 | 解释空间运算、信号与概率采样的数学模型 |
| 02_GPU与光栅化管线 | 12 | 解释GPU执行、覆盖与可见性怎样生成图形样本 |
| 03_Shader编程 | 3 | 解释Shader接口、编译与并行程序的执行契约 |
| 04_光照模型与PBR | 4 | 解释表面材质对光的响应及其可计算表示 |
| 05_光照阴影与GI | 3 | 解释光源、可见性和场景间接照明的生成 |
| 06_纹理技术 | 4 | 解释表面数据的采样、组织、格式与驻留 |
| 07_颜色与后处理 | 2 | 解释场景颜色到显示图像的编码、合成与处理 |
| 08_几何与网格 | 4 | 解释几何资产的表示、访问与运行时密度选择 |
| 09_动画系统 | 7 | 从姿态与模拟代理生成可控的角色和资产运动 |
| 10_VFX与模拟 | 5 | 用动态元素、表面与介质构建实时特效 |
| 11_NPR与风格化渲染 | 5 | 用受控材质、轮廓与角色明暗形成风格画面 |
| 12_光线追踪 | 2 | 用光线查询、采样与重建计算实时照明 |
| 13_渲染架构 | 14 | 组织一帧的通道、命令、光照路径、资源寻址、同步与寿命 |
| 14_性能分析与优化 | 5 | 用可复查实验定位并验证游戏运行成本 |
| 15_资产与工具管线 | 4 | 将制作数据转换为可验证、协作和发布的资产 |
| 16_编程与数据结构 | 4 | 解释工程语言、内存并发和算法的数据契约 |
| 17_AIGC与Agent管线 | 3 | 把生成模型与Agent执行组织成可复现资产流程 |
| 18_游戏物理与模拟 | 2 | 从状态、碰撞和约束计算游戏运动 |
| 19_Gameplay与游戏框架 | 2 | 将输入、规则和状态推进为可观察玩法行为 |
| 20_游戏AI | 3 | 从感知与目标产生可执行的决策和路径 |
| 21_游戏网络 | 3 | 通过传输、共同时间和权威边界维护联机状态 |
| 22_渲染引擎实现 | 6 | 在指定Unity/Unreal版本接入相机、场景、Pass和图形后端 |
| 23_引擎运行系统 | 3 | 组织世界对象、任务与运行资源的所有权和更新 |
| 24_游戏音频 | 1 | 在实时音频预算内组织声音、解码、混音和空间化 |
| 25_UI与文本 | 1 | 把界面布局与文本语义转成可交互的绘制结果 |
| 26_GPU驱动与虚拟几何 | 2 | 用GPU可见性、间接绘制与虚拟化组织大规模几何 |

## 113页全文处理清单

下表记录最终页面、批次、正文动作、标题和边界。具体修改章节、前后哈希、最终哈希及提交位于 [逐批记录](../batch-review.json)；每行的内容变化可通过对应提交审查。KEEP表示复读保留有效正文。

| 页面 | 批次 | 正文动作 | 标题 | 边界与范围 |
|---|---|---|---|---|
| [学习与维护方法](../../../知识库/00_知识库说明/学习与维护方法.md) | Batch4-P2-P3-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [技术中文写作规范](../../../知识库/00_知识库说明/技术中文写作规范.md) | Batch4-P2-P3-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [术语表](../../../知识库/00_知识库说明/术语表.md) | Batch4-P2-P3-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [知识地图](../../../知识库/00_知识库说明/知识地图.md) | Batch4-P2-P3-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [知识库实施规范](../../../知识库/00_知识库说明/知识库实施规范.md) | Batch4-P2-P3-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [信号、频率与噪声](../../../知识库/01_数学与采样/信号、频率与噪声.md) | Batch4-P1-A | FACT-CHECK / REWRITE | SPLIT | pending_split |
| [空间变换](../../../知识库/01_数学与采样/空间变换.md) | Batch4-P1-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [旋转表示与插值](../../../知识库/01_数学与采样/旋转表示与插值.md) | Batch4-P1-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [概率采样、积分与球谐函数](../../../知识库/01_数学与采样/概率采样、积分与球谐函数.md) | Batch3-P0-B | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [GPU执行与访存](../../../知识库/02_GPU与光栅化管线/GPU执行与访存.md) | Batch3-P0-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [一帧如何到达屏幕](../../../知识库/02_GPU与光栅化管线/一帧如何到达屏幕.md) | Batch4-P1-B | FACT-CHECK / REWRITE | OVERVIEW | OVERVIEW |
| [光栅化、插值与深度模板](../../../知识库/02_GPU与光栅化管线/光栅化、插值与深度模板.md) | Batch4-P1-B | FACT-CHECK / REWRITE | OVERVIEW | OVERVIEW |
| [光栅化与属性插值](../../../知识库/02_GPU与光栅化管线/光栅化与属性插值.md) | Batch3-P0-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [几何着色器、曲面细分与流输出](../../../知识库/02_GPU与光栅化管线/几何着色器、曲面细分与流输出.md) | Batch3-P0-B | FACT-CHECK / REWRITE | SPLIT | pending_split |
| [剔除、透明与混合](../../../知识库/02_GPU与光栅化管线/剔除、透明与混合.md) | Batch4-P2-P3-B | FACT-CHECK / RESTRUCTURE / REWRITE | OVERVIEW | OVERVIEW |
| [抗锯齿与时域重建](../../../知识库/02_GPU与光栅化管线/抗锯齿与时域重建.md) | Batch4-P1-B | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [基于深度的可见性优化](../../../知识库/02_GPU与光栅化管线/基于深度的可见性优化.md) | Batch3-P0-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [Stencil与对象遮罩](../../../知识库/02_GPU与光栅化管线/Stencil与对象遮罩.md) | Batch3-P0-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [深度缓冲与位置重建](../../../知识库/02_GPU与光栅化管线/深度缓冲与位置重建.md) | Batch3-P0-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [可见性剔除](../../../知识库/02_GPU与光栅化管线/可见性剔除.md) | Batch3-P0-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [透明合成](../../../知识库/02_GPU与光栅化管线/透明合成.md) | Batch3-P0-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [Compute Shader与GPU执行模型](../../../知识库/03_Shader编程/Compute Shader与GPU执行模型.md) | Batch3-P0-A | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [Shader Variant管理](../../../知识库/03_Shader编程/Shader Variant管理.md) | Batch3-P0-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [Shader接口与数据流](../../../知识库/03_Shader编程/Shader接口与数据流.md) | Batch3-P0-B | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [PBR材质](../../../知识库/04_光照模型与PBR/PBR材质.md) | Batch3-P0-B | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [皮肤次表面散射](../../../知识库/04_光照模型与PBR/皮肤次表面散射.md) | Batch4-P1-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [法线贴图、切线空间与IBL](../../../知识库/04_光照模型与PBR/法线贴图、切线空间与IBL.md) | Batch3-P0-B | FACT-CHECK / REWRITE | SPLIT | pending_split |
| [BRDF与微表面模型](../../../知识库/04_光照模型与PBR/BRDF与微表面模型.md) | Batch3-P0-B | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [直接光照](../../../知识库/05_光照阴影与GI/直接光照.md) | Batch4-P1-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [烘焙光照、Probe与实时GI](../../../知识库/05_光照阴影与GI/烘焙光照、Probe与实时GI.md) | Batch4-P1-A | FACT-CHECK / RESTRUCTURE / REWRITE | OVERVIEW | OVERVIEW |
| [Shadow Map](../../../知识库/05_光照阴影与GI/Shadow Map.md) | Batch4-P1-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [UV、图集、流送与虚拟纹理](../../../知识库/06_纹理技术/UV、图集、流送与虚拟纹理.md) | Batch3-P0-B | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [纹理压缩格式](../../../知识库/06_纹理技术/纹理压缩格式.md) | Batch4-P1-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [纹理采样与过滤](../../../知识库/06_纹理技术/纹理采样与过滤.md) | Batch3-P0-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [视差映射](../../../知识库/06_纹理技术/视差映射.md) | Batch4-P1-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [Tone Mapping、Bloom与屏幕效果](../../../知识库/07_颜色与后处理/Tone Mapping、Bloom与屏幕效果.md) | Batch3-P0-B | FACT-CHECK / REWRITE | SPLIT | pending_split |
| [颜色空间、Alpha、HDR与曝光](../../../知识库/07_颜色与后处理/颜色空间、Alpha、HDR与曝光.md) | Batch3-P0-B | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [LOD、地形与程序化资产](../../../知识库/08_几何与网格/LOD、地形与程序化资产.md) | Batch4-P1-A | FACT-CHECK / REWRITE | SPLIT | pending_split |
| [Tessellation与位移](../../../知识库/08_几何与网格/Tessellation与位移.md) | Batch3-P0-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [网格数据与GPU访问](../../../知识库/08_几何与网格/网格数据与GPU访问.md) | Batch4-P1-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [动画压缩](../../../知识库/09_动画系统/动画压缩.md) | Batch4-P1-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [动画压缩、面部、布料与毛发](../../../知识库/09_动画系统/动画压缩、面部、布料与毛发.md) | Batch4-P2-P3-B | FACT-CHECK / RESTRUCTURE / REWRITE | OVERVIEW | OVERVIEW |
| [动画状态、混合与IK](../../../知识库/09_动画系统/动画状态、混合与IK.md) | Batch4-P1-A | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [布料与毛发的表示、碰撞和LOD](../../../知识库/09_动画系统/布料与毛发的表示、碰撞和LOD.md) | Batch4-P1-A | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [面部动画](../../../知识库/09_动画系统/面部动画.md) | Batch4-P1-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [骨骼动画与蒙皮](../../../知识库/09_动画系统/骨骼动画与蒙皮.md) | Batch4-P1-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [Froxel体积雾](../../../知识库/10_VFX与模拟/Froxel体积雾.md) | Batch4-P1-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [大气散射、天空与体积云](../../../知识库/10_VFX与模拟/大气散射、天空与体积云.md) | Batch4-P1-A | FACT-CHECK / REWRITE | SPLIT | pending_split |
| [常用VFX材质、模拟与性能](../../../知识库/10_VFX与模拟/常用VFX材质、模拟与性能.md) | Batch4-P1-A | FACT-CHECK / RESTRUCTURE / REWRITE | OVERVIEW | OVERVIEW |
| [水面与海洋渲染](../../../知识库/10_VFX与模拟/水面与海洋渲染.md) | Batch4-P1-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [GPU粒子系统](../../../知识库/10_VFX与模拟/GPU粒子系统.md) | Batch4-P1-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [Billboard](../../../知识库/08_几何与网格/Billboard.md) | Batch3-P0-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [NPR与场景风格导读](../../../知识库/11_NPR与风格化渲染/NPR与场景风格导读.md) | Batch4-P2-P3-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [NPR材质与分层光照](../../../知识库/11_NPR与风格化渲染/NPR材质与分层光照.md) | Batch3-P0-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [描边](../../../知识库/11_NPR与风格化渲染/描边.md) | Batch4-P2-P3-B | KEEP | PASS | KEEP |
| [描边、Billboard与场景风格化](../../../知识库/11_NPR与风格化渲染/描边、Billboard与场景风格化.md) | Batch4-P2-P3-B | FACT-CHECK / REWRITE | OVERVIEW | OVERVIEW |
| [植被风动](../../../知识库/09_动画系统/植被风动.md) | Batch3-P0-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [角色面部、头发与阴影](../../../知识库/11_NPR与风格化渲染/角色面部、头发与阴影.md) | Batch3-P0-A | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [GPU-Driven Rendering](../../../知识库/26_GPU驱动与虚拟几何/GPU-Driven Rendering.md) | Batch4-P1-B | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [Nanite几何选择与流送](../../../知识库/26_GPU驱动与虚拟几何/Nanite几何选择与流送.md) | Batch4-P1-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [光线求交与BVH](../../../知识库/12_光线追踪/光线求交与BVH.md) | Batch4-P1-B | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [实时光追、采样与降噪](../../../知识库/12_光线追踪/实时光追、采样与降噪.md) | Batch4-P1-B | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [Draw Call与合批](../../../知识库/13_渲染架构/Draw Call与合批.md) | Batch3-P0-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [渲染路径与光源组织](../../../知识库/13_渲染架构/渲染路径与光源组织.md) | Batch4-P1-B | FACT-CHECK / RESTRUCTURE / REWRITE | OVERVIEW | OVERVIEW |
| [GBuffer布局](../../../知识库/13_渲染架构/GBuffer布局.md) | Batch3-P0-A | DEEPEN / FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [Render Pass、Command Buffer与Render Graph](../../../知识库/13_渲染架构/Render Pass、Command Buffer与Render Graph.md) | Batch4-P1-B | FACT-CHECK / REWRITE | OVERVIEW | OVERVIEW |
| [UI、字体与文本渲染](../../../知识库/25_UI与文本/UI、字体与文本渲染.md) | Batch4-P1-B | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [URP Render Graph自定义Pass](../../../知识库/22_渲染引擎实现/URP Render Graph自定义Pass.md) | Batch3-P0-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [Unity渲染帧组织](../../../知识库/22_渲染引擎实现/Unity渲染帧组织.md) | Batch3-P0-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [Unity与Unreal渲染扩展入口](../../../知识库/22_渲染引擎实现/Unity与Unreal渲染扩展入口.md) | Batch4-P1-B | FACT-CHECK / RESTRUCTURE / REWRITE | OVERVIEW | OVERVIEW |
| [Unreal RDG Pass实现](../../../知识库/22_渲染引擎实现/Unreal RDG Pass实现.md) | Batch3-P0-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [Unreal渲染帧组织](../../../知识库/22_渲染引擎实现/Unreal渲染帧组织.md) | Batch3-P0-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [Unreal自定义Mesh Pass](../../../知识库/22_渲染引擎实现/Unreal自定义Mesh Pass.md) | Batch4-P1-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [GPU资源生命周期](../../../知识库/13_渲染架构/GPU资源生命周期.md) | Batch3-P0-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [Tiled与Clustered光源剔除](../../../知识库/13_渲染架构/Tiled与Clustered光源剔除.md) | Batch3-P0-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [Forward Rendering与Forward+](../../../知识库/13_渲染架构/Forward Rendering与Forward+.md) | Batch3-P0-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [Command Buffer与帧提交](../../../知识库/13_渲染架构/Command Buffer与帧提交.md) | Batch3-P0-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [Deferred Rendering](../../../知识库/13_渲染架构/Deferred Rendering.md) | Batch3-P0-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [引擎世界与对象模型](../../../知识库/23_引擎运行系统/引擎世界与对象模型.md) | Batch4-P1-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [数据导向设计与任务系统](../../../知识库/23_引擎运行系统/数据导向设计与任务系统.md) | Batch4-P1-B | FACT-CHECK / REWRITE | SPLIT | pending_split |
| [Render Graph](../../../知识库/13_渲染架构/Render Graph.md) | Batch3-P0-A | DEEPEN / FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [Render Pass与附件](../../../知识库/13_渲染架构/Render Pass与附件.md) | Batch3-P0-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [游戏音频系统](../../../知识库/24_游戏音频/游戏音频系统.md) | Batch4-P2-P3-B | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [Pipeline State Object](../../../知识库/13_渲染架构/Pipeline State Object.md) | Batch3-P0-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [资源依赖与异步加载](../../../知识库/23_引擎运行系统/资源依赖与异步加载.md) | Batch4-P1-B | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [GPU同步与屏障](../../../知识库/13_渲染架构/GPU同步与屏障.md) | Batch3-P0-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [GPU资源绑定](../../../知识库/13_渲染架构/GPU资源绑定.md) | Batch3-P0-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [帧捕获与性能分析工具](../../../知识库/14_性能分析与优化/帧捕获与性能分析工具.md) | Batch4-P1-B | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [PSO首次使用为什么卡顿](../../../知识库/14_性能分析与优化/PSO首次使用为什么卡顿.md) | Batch3-P0-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [帧瓶颈怎么判断](../../../知识库/14_性能分析与优化/帧瓶颈怎么判断.md) | Batch4-P1-B | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [性能对照实验](../../../知识库/14_性能分析与优化/性能对照实验.md) | Batch4-P1-B | FACT-CHECK / REWRITE | PASS | KEEP |
| [移动端渲染优化](../../../知识库/14_性能分析与优化/移动端渲染优化.md) | Batch4-P1-B | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [DCC资产交换](../../../知识库/15_资产与工具管线/DCC资产交换.md) | Batch4-P2-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [版本控制、CI与大型资产协作](../../../知识库/15_资产与工具管线/版本控制、CI与大型资产协作.md) | Batch4-P2-A | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [编辑器工具的事务与批处理](../../../知识库/15_资产与工具管线/编辑器工具的事务与批处理.md) | Batch4-P2-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [资产构建与发布](../../../知识库/15_资产与工具管线/资产构建与发布.md) | Batch4-P2-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [C++、CSharp与Python工程基础](../../../知识库/16_编程与数据结构/C++、CSharp与Python工程基础.md) | Batch4-P2-A | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [内存、对象生命周期与对象池](../../../知识库/16_编程与数据结构/内存、对象生命周期与对象池.md) | Batch4-P2-A | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [操作系统、进程与并发基础](../../../知识库/16_编程与数据结构/操作系统、进程与并发基础.md) | Batch4-P2-A | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [算法设计、树、图与空间划分](../../../知识库/16_编程与数据结构/算法设计、树、图与空间划分.md) | Batch4-P2-A | FACT-CHECK / RESTRUCTURE / REWRITE | OVERVIEW | OVERVIEW |
| [Agent资产管线](../../../知识库/17_AIGC与Agent管线/Agent资产管线.md) | Batch4-P2-P3-B | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [ComfyUI工作流与时序一致性](../../../知识库/17_AIGC与Agent管线/ComfyUI工作流与时序一致性.md) | Batch4-P2-P3-B | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [扩散模型、条件控制与微调](../../../知识库/17_AIGC与Agent管线/扩散模型、条件控制与微调.md) | Batch4-P2-P3-B | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [刚体物理求解](../../../知识库/18_游戏物理与模拟/刚体物理求解.md) | Batch4-P2-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [角色、布料、破坏与载具物理](../../../知识库/18_游戏物理与模拟/角色、布料、破坏与载具物理.md) | Batch4-P2-A | FACT-CHECK / REWRITE | SPLIT | pending_split |
| [玩法事件与脚本](../../../知识库/19_Gameplay与游戏框架/玩法事件与脚本.md) | Batch4-P2-A | FACT-CHECK / REWRITE | PASS | KEEP |
| [输入与动作状态](../../../知识库/19_Gameplay与游戏框架/输入与动作状态.md) | Batch4-P2-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [游戏AI导航](../../../知识库/20_游戏AI/游戏AI导航.md) | Batch4-P2-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [群体、学习与高级决策](../../../知识库/20_游戏AI/群体、学习与高级决策.md) | Batch4-P2-A | FACT-CHECK / REWRITE | SPLIT | pending_split |
| [游戏AI决策模型](../../../知识库/20_游戏AI/游戏AI决策模型.md) | Batch4-P2-A | FACT-CHECK / RESTRUCTURE / REWRITE | PASS | KEEP |
| [服务器架构、分区与反作弊](../../../知识库/21_游戏网络/服务器架构、分区与反作弊.md) | Batch4-P2-A | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [状态同步、预测与回滚](../../../知识库/21_游戏网络/状态同步、预测与回滚.md) | Batch4-P2-A | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |
| [网络协议、时钟与RPC](../../../知识库/21_游戏网络/网络协议、时钟与RPC.md) | Batch4-P2-P3-B | FACT-CHECK / RESTRUCTURE / REWRITE | SPLIT | pending_split |

## 113页最终路径映射

冻结映射保存本轮源路径和最终路径。文件目录与标题一次决定，content_actions作为正文计划与执行记录的连接点。完整字段见 [final-path-map.json](../final-path-map.json)。

| 起始路径 | 最终路径 | 最终H1 | 标题策略 |
|---|---|---|---|
| 知识库/00_知识库说明/学习与维护方法.md | 知识库/00_知识库说明/学习与维护方法.md | 学习与维护方法 | 采用 |
| 知识库/00_知识库说明/技术中文写作规范.md | 知识库/00_知识库说明/技术中文写作规范.md | 技术中文写作规范 | 采用 |
| 知识库/00_知识库说明/术语表.md | 知识库/00_知识库说明/术语表.md | 术语表 | 采用 |
| 知识库/00_知识库说明/知识地图.md | 知识库/00_知识库说明/知识地图.md | 知识地图 | 采用 |
| 知识库/00_知识库说明/知识库实施规范.md | 知识库/00_知识库说明/知识库实施规范.md | 知识库实施规范 | 采用 |
| 知识库/01_数学与采样/信号、频率与噪声.md | 知识库/01_数学与采样/信号、频率与噪声.md | 信号、频率与噪声 | 延后 |
| 知识库/01_数学与采样/向量、矩阵与空间变换.md | 知识库/01_数学与采样/空间变换.md | 空间变换 | 采用 |
| 知识库/01_数学与采样/旋转、四元数与插值.md | 知识库/01_数学与采样/旋转表示与插值.md | 旋转表示与插值 | 采用 |
| 知识库/01_数学与采样/概率采样、积分与球谐函数.md | 知识库/01_数学与采样/概率采样、积分与球谐函数.md | 概率采样、积分与球谐函数 | 延后 |
| 知识库/02_GPU与光栅化管线/GPU执行、缓存带宽与平台架构.md | 知识库/02_GPU与光栅化管线/GPU执行与访存.md | GPU执行与访存 | 采用 |
| 知识库/02_GPU与光栅化管线/一帧如何到达屏幕.md | 知识库/02_GPU与光栅化管线/一帧如何到达屏幕.md | 一帧如何到达屏幕 | 延后 |
| 知识库/02_GPU与光栅化管线/光栅化、插值与深度模板.md | 知识库/02_GPU与光栅化管线/光栅化、插值与深度模板.md | 光栅化、插值与深度模板 | 延后 |
| 知识库/02_GPU与光栅化管线/光栅覆盖、重心坐标与属性插值.md | 知识库/02_GPU与光栅化管线/光栅化与属性插值.md | 光栅化与属性插值 | 采用 |
| 知识库/02_GPU与光栅化管线/几何着色器、曲面细分与流输出.md | 知识库/02_GPU与光栅化管线/几何着色器、曲面细分与流输出.md | 几何着色器、曲面细分与流输出 | 延后 |
| 知识库/02_GPU与光栅化管线/剔除、透明与混合.md | 知识库/02_GPU与光栅化管线/剔除、透明与混合.md | 剔除、透明与混合 | 延后 |
| 知识库/02_GPU与光栅化管线/抗锯齿、TAA与时域超采样.md | 知识库/02_GPU与光栅化管线/抗锯齿与时域重建.md | 抗锯齿与时域重建 | 采用 |
| 知识库/02_GPU与光栅化管线/提前深度测试、深度预通道与分层深度.md | 知识库/02_GPU与光栅化管线/基于深度的可见性优化.md | 基于深度的可见性优化 | 采用 |
| 知识库/02_GPU与光栅化管线/模板缓冲、位分配与对象遮罩.md | 知识库/02_GPU与光栅化管线/Stencil与对象遮罩.md | Stencil与对象遮罩 | 采用 |
| 知识库/02_GPU与光栅化管线/深度缓冲、反向深度与位置重建.md | 知识库/02_GPU与光栅化管线/深度缓冲与位置重建.md | 深度缓冲与位置重建 | 采用 |
| 知识库/02_GPU与光栅化管线/背面、视锥与遮挡剔除.md | 知识库/02_GPU与光栅化管线/可见性剔除.md | 可见性剔除 | 采用 |
| 知识库/02_GPU与光栅化管线/透明排序、深度剥离与顺序无关透明.md | 知识库/02_GPU与光栅化管线/透明合成.md | 透明合成 | 采用 |
| 知识库/03_Shader编程/Compute Shader与GPU执行模型.md | 知识库/03_Shader编程/Compute Shader与GPU执行模型.md | Compute Shader与GPU执行模型 | 延后 |
| 知识库/03_Shader编程/Shader编译、关键字与变体.md | 知识库/03_Shader编程/Shader Variant管理.md | Shader Variant管理 | 采用 |
| 知识库/03_Shader编程/Shader语言与数据流.md | 知识库/03_Shader编程/Shader接口与数据流.md | Shader接口与数据流 | 采用 |
| 知识库/04_光照模型与PBR/PBR材质与能量守恒.md | 知识库/04_光照模型与PBR/PBR材质.md | PBR材质 | 采用 |
| 知识库/04_光照模型与PBR/次表面散射与皮肤渲染.md | 知识库/04_光照模型与PBR/皮肤次表面散射.md | 皮肤次表面散射 | 采用 |
| 知识库/04_光照模型与PBR/法线贴图、切线空间与IBL.md | 知识库/04_光照模型与PBR/法线贴图、切线空间与IBL.md | 法线贴图、切线空间与IBL | 延后 |
| 知识库/04_光照模型与PBR/经典光照、BRDF与微表面模型.md | 知识库/04_光照模型与PBR/BRDF与微表面模型.md | BRDF与微表面模型 | 采用 |
| 知识库/05_光照阴影与GI/光源与直接光照.md | 知识库/05_光照阴影与GI/直接光照.md | 直接光照 | 采用 |
| 知识库/05_光照阴影与GI/烘焙光照、Probe与实时GI.md | 知识库/05_光照阴影与GI/烘焙光照、Probe与实时GI.md | 烘焙光照、Probe与实时GI | 延后 |
| 知识库/05_光照阴影与GI/阴影贴图、PCF与PCSS.md | 知识库/05_光照阴影与GI/Shadow Map.md | Shadow Map | 采用 |
| 知识库/06_纹理技术/UV、图集、流送与虚拟纹理.md | 知识库/06_纹理技术/UV、图集、流送与虚拟纹理.md | UV、图集、流送与虚拟纹理 | 延后 |
| 知识库/06_纹理技术/纹理压缩、格式选择与平台预算.md | 知识库/06_纹理技术/纹理压缩格式.md | 纹理压缩格式 | 采用 |
| 知识库/06_纹理技术/纹理采样与过滤.md | 知识库/06_纹理技术/纹理采样与过滤.md | 纹理采样与过滤 | 采用 |
| 知识库/06_纹理技术/高度、法线与视差映射.md | 知识库/06_纹理技术/视差映射.md | 视差映射 | 采用 |
| 知识库/07_颜色与后处理/Tone Mapping、Bloom与屏幕效果.md | 知识库/07_颜色与后处理/Tone Mapping、Bloom与屏幕效果.md | Tone Mapping、Bloom与屏幕效果 | 延后 |
| 知识库/07_颜色与后处理/颜色空间、Alpha、HDR与曝光.md | 知识库/07_颜色与后处理/颜色空间、Alpha、HDR与曝光.md | 颜色空间、Alpha、HDR与曝光 | 延后 |
| 知识库/08_几何与网格/LOD、地形与程序化资产.md | 知识库/08_几何与网格/LOD、地形与程序化资产.md | LOD、地形与程序化资产 | 延后 |
| 知识库/08_几何与网格/曲面细分与位移.md | 知识库/08_几何与网格/Tessellation与位移.md | Tessellation与位移 | 采用 |
| 知识库/08_几何与网格/网格数据、缓存与几何处理.md | 知识库/08_几何与网格/网格数据与GPU访问.md | 网格数据与GPU访问 | 采用 |
| 知识库/09_动画系统/动画压缩.md | 知识库/09_动画系统/动画压缩.md | 动画压缩 | 采用 |
| 知识库/09_动画系统/动画压缩、面部、布料与毛发.md | 知识库/09_动画系统/动画压缩、面部、布料与毛发.md | 动画压缩、面部、布料与毛发 | 延后 |
| 知识库/09_动画系统/动画状态、混合与IK.md | 知识库/09_动画系统/动画状态、混合与IK.md | 动画状态、混合与IK | 延后 |
| 知识库/09_动画系统/布料与毛发的表示、碰撞和LOD.md | 知识库/09_动画系统/布料与毛发的表示、碰撞和LOD.md | 布料与毛发的表示、碰撞和LOD | 延后 |
| 知识库/09_动画系统/面部变形、口型与表情控制.md | 知识库/09_动画系统/面部动画.md | 面部动画 | 采用 |
| 知识库/09_动画系统/骨骼动画、蒙皮与GPU动画.md | 知识库/09_动画系统/骨骼动画与蒙皮.md | 骨骼动画与蒙皮 | 采用 |
| 知识库/10_VFX与模拟/体积雾、视锥网格与时域积分.md | 知识库/10_VFX与模拟/Froxel体积雾.md | Froxel体积雾 | 采用 |
| 知识库/10_VFX与模拟/大气散射、天空与体积云.md | 知识库/10_VFX与模拟/大气散射、天空与体积云.md | 大气散射、天空与体积云 | 延后 |
| 知识库/10_VFX与模拟/常用VFX材质、模拟与性能.md | 知识库/10_VFX与模拟/常用VFX材质、模拟与性能.md | 常用VFX材质、模拟与性能 | 延后 |
| 知识库/10_VFX与模拟/水体与海洋渲染.md | 知识库/10_VFX与模拟/水面与海洋渲染.md | 水面与海洋渲染 | 采用 |
| 知识库/10_VFX与模拟/粒子系统与GPU模拟.md | 知识库/10_VFX与模拟/GPU粒子系统.md | GPU粒子系统 | 采用 |
| 知识库/11_NPR与风格化渲染/Billboard.md | 知识库/08_几何与网格/Billboard.md | Billboard | 采用 |
| 知识库/11_NPR与风格化渲染/NPR与场景风格导读.md | 知识库/11_NPR与风格化渲染/NPR与场景风格导读.md | NPR与场景风格导读 | 采用 |
| 知识库/11_NPR与风格化渲染/NPR材质与分层光照.md | 知识库/11_NPR与风格化渲染/NPR材质与分层光照.md | NPR材质与分层光照 | 采用 |
| 知识库/11_NPR与风格化渲染/描边.md | 知识库/11_NPR与风格化渲染/描边.md | 描边 | 采用 |
| 知识库/11_NPR与风格化渲染/描边、Billboard与场景风格化.md | 知识库/11_NPR与风格化渲染/描边、Billboard与场景风格化.md | 描边、Billboard与场景风格化 | 延后 |
| 知识库/11_NPR与风格化渲染/植被风动.md | 知识库/09_动画系统/植被风动.md | 植被风动 | 采用 |
| 知识库/11_NPR与风格化渲染/角色面部、头发与阴影.md | 知识库/11_NPR与风格化渲染/角色面部、头发与阴影.md | 角色面部、头发与阴影 | 延后 |
| 知识库/12_光追与现代渲染/GPU-Driven管线与Nanite.md | 知识库/26_GPU驱动与虚拟几何/GPU-Driven Rendering.md | GPU-Driven Rendering | 采用 |
| 知识库/12_光追与现代渲染/Nanite虚拟化几何、层级选择与流送.md | 知识库/26_GPU驱动与虚拟几何/Nanite几何选择与流送.md | Nanite几何选择与流送 | 采用 |
| 知识库/12_光追与现代渲染/光线、求交与加速结构.md | 知识库/12_光线追踪/光线求交与BVH.md | 光线求交与BVH | 采用 |
| 知识库/12_光追与现代渲染/实时光追、采样与降噪.md | 知识库/12_光线追踪/实时光追、采样与降噪.md | 实时光追、采样与降噪 | 延后 |
| 知识库/13_引擎架构与资源系统/Draw Call、Batching与GPU Instancing.md | 知识库/13_渲染架构/Draw Call与合批.md | Draw Call与合批 | 采用 |
| 知识库/13_引擎架构与资源系统/渲染路径与光源组织.md | 知识库/13_渲染架构/渲染路径与光源组织.md | 渲染路径与光源组织 | 延后 |
| 知识库/13_引擎架构与资源系统/GBuffer布局.md | 知识库/13_渲染架构/GBuffer布局.md | GBuffer布局 | 采用 |
| 知识库/13_引擎架构与资源系统/Render Pass、Command Buffer与Render Graph.md | 知识库/13_渲染架构/Render Pass、Command Buffer与Render Graph.md | Render Pass、Command Buffer与Render Graph | 延后 |
| 知识库/13_引擎架构与资源系统/UI、字体与文本渲染.md | 知识库/25_UI与文本/UI、字体与文本渲染.md | UI、字体与文本渲染 | 延后 |
| 知识库/13_引擎架构与资源系统/URP Render Graph自定义Pass.md | 知识库/22_渲染引擎实现/URP Render Graph自定义Pass.md | URP Render Graph自定义Pass | 采用 |
| 知识库/13_引擎架构与资源系统/Unity SRP、URP与HDRP帧组织.md | 知识库/22_渲染引擎实现/Unity渲染帧组织.md | Unity渲染帧组织 | 采用 |
| 知识库/13_引擎架构与资源系统/Unity与Unreal渲染扩展入口.md | 知识库/22_渲染引擎实现/Unity与Unreal渲染扩展入口.md | Unity与Unreal渲染扩展入口 | 延后 |
| 知识库/13_引擎架构与资源系统/Unreal RDG资源声明与通道实现.md | 知识库/22_渲染引擎实现/Unreal RDG Pass实现.md | Unreal RDG Pass实现 | 采用 |
| 知识库/13_引擎架构与资源系统/Unreal Renderer、RDG与RHI帧组织.md | 知识库/22_渲染引擎实现/Unreal渲染帧组织.md | Unreal渲染帧组织 | 采用 |
| 知识库/13_引擎架构与资源系统/Unreal网格绘制与自定义Pass.md | 知识库/22_渲染引擎实现/Unreal自定义Mesh Pass.md | Unreal自定义Mesh Pass | 采用 |
| 知识库/13_引擎架构与资源系统/临时资源、上传回读与GPU内存生命周期.md | 知识库/13_渲染架构/GPU资源生命周期.md | GPU资源生命周期 | 采用 |
| 知识库/13_引擎架构与资源系统/分块与簇光照剔除.md | 知识库/13_渲染架构/Tiled与Clustered光源剔除.md | Tiled与Clustered光源剔除 | 采用 |
| 知识库/13_引擎架构与资源系统/前向渲染、Forward加与材质光照流程.md | 知识库/13_渲染架构/Forward Rendering与Forward+.md | Forward Rendering与Forward+ | 采用 |
| 知识库/13_引擎架构与资源系统/命令记录、队列提交与在途帧.md | 知识库/13_渲染架构/Command Buffer与帧提交.md | Command Buffer与帧提交 | 采用 |
| 知识库/13_引擎架构与资源系统/延迟渲染、光体积与GBuffer消费.md | 知识库/13_渲染架构/Deferred Rendering.md | Deferred Rendering | 采用 |
| 知识库/13_引擎架构与资源系统/引擎分层、世界与对象模型.md | 知识库/23_引擎运行系统/引擎世界与对象模型.md | 引擎世界与对象模型 | 采用 |
| 知识库/13_引擎架构与资源系统/数据导向设计与任务系统.md | 知识库/23_引擎运行系统/数据导向设计与任务系统.md | 数据导向设计与任务系统 | 延后 |
| 知识库/13_引擎架构与资源系统/Render Graph.md | 知识库/13_渲染架构/Render Graph.md | Render Graph | 采用 |
| 知识库/13_引擎架构与资源系统/渲染通道、附件与加载存储语义.md | 知识库/13_渲染架构/Render Pass与附件.md | Render Pass与附件 | 采用 |
| 知识库/13_引擎架构与资源系统/游戏音频系统.md | 知识库/24_游戏音频/游戏音频系统.md | 游戏音频系统 | 采用 |
| 知识库/13_引擎架构与资源系统/管线状态、PSO组合与创建生命周期.md | 知识库/13_渲染架构/Pipeline State Object.md | Pipeline State Object | 采用 |
| 知识库/13_引擎架构与资源系统/资源打包、依赖与异步加载.md | 知识库/23_引擎运行系统/资源依赖与异步加载.md | 资源依赖与异步加载 | 采用 |
| 知识库/13_引擎架构与资源系统/资源状态、屏障与跨队列同步.md | 知识库/13_渲染架构/GPU同步与屏障.md | GPU同步与屏障 | 采用 |
| 知识库/13_引擎架构与资源系统/资源绑定、描述符与材质数据组织.md | 知识库/13_渲染架构/GPU资源绑定.md | GPU资源绑定 | 采用 |
| 知识库/14_性能分析与优化/Profiler、RenderDoc与单帧分析.md | 知识库/14_性能分析与优化/帧捕获与性能分析工具.md | 帧捕获与性能分析工具 | 采用 |
| 知识库/14_性能分析与优化/PSO首次使用为什么卡顿.md | 知识库/14_性能分析与优化/PSO首次使用为什么卡顿.md | PSO首次使用为什么卡顿 | 采用 |
| 知识库/14_性能分析与优化/帧时间、瓶颈与GPU成本.md | 知识库/14_性能分析与优化/帧瓶颈怎么判断.md | 帧瓶颈怎么判断 | 采用 |
| 知识库/14_性能分析与优化/性能调查、对照实验与帧捕获证据.md | 知识库/14_性能分析与优化/性能对照实验.md | 性能对照实验 | 采用 |
| 知识库/14_性能分析与优化/渲染优化验证与移动端实践.md | 知识库/14_性能分析与优化/移动端渲染优化.md | 移动端渲染优化 | 采用 |
| 知识库/15_资产与工具管线/DCC、数据格式与资产交换.md | 知识库/15_资产与工具管线/DCC资产交换.md | DCC资产交换 | 采用 |
| 知识库/15_资产与工具管线/版本控制、CI与大型资产协作.md | 知识库/15_资产与工具管线/版本控制、CI与大型资产协作.md | 版本控制、CI与大型资产协作 | 延后 |
| 知识库/15_资产与工具管线/编辑器工具与批处理架构.md | 知识库/15_资产与工具管线/编辑器工具的事务与批处理.md | 编辑器工具的事务与批处理 | 采用 |
| 知识库/15_资产与工具管线/资产导入、验证与发布.md | 知识库/15_资产与工具管线/资产构建与发布.md | 资产构建与发布 | 采用 |
| 知识库/16_编程与数据结构/C++、CSharp与Python工程基础.md | 知识库/16_编程与数据结构/C++、CSharp与Python工程基础.md | C++、CSharp与Python工程基础 | 延后 |
| 知识库/16_编程与数据结构/内存、对象生命周期与对象池.md | 知识库/16_编程与数据结构/内存、对象生命周期与对象池.md | 内存、对象生命周期与对象池 | 延后 |
| 知识库/16_编程与数据结构/操作系统、进程与并发基础.md | 知识库/16_编程与数据结构/操作系统、进程与并发基础.md | 操作系统、进程与并发基础 | 延后 |
| 知识库/16_编程与数据结构/算法设计、树、图与空间划分.md | 知识库/16_编程与数据结构/算法设计、树、图与空间划分.md | 算法设计、树、图与空间划分 | 延后 |
| 知识库/17_AIGC与Agent管线/Agent驱动资产管线与质量门禁.md | 知识库/17_AIGC与Agent管线/Agent资产管线.md | Agent资产管线 | 采用 |
| 知识库/17_AIGC与Agent管线/ComfyUI工作流与时序一致性.md | 知识库/17_AIGC与Agent管线/ComfyUI工作流与时序一致性.md | ComfyUI工作流与时序一致性 | 延后 |
| 知识库/17_AIGC与Agent管线/扩散模型、条件控制与微调.md | 知识库/17_AIGC与Agent管线/扩散模型、条件控制与微调.md | 扩散模型、条件控制与微调 | 延后 |
| 知识库/18_游戏物理与模拟/刚体、碰撞与约束求解.md | 知识库/18_游戏物理与模拟/刚体物理求解.md | 刚体物理求解 | 采用 |
| 知识库/18_游戏物理与模拟/角色、布料、破坏与载具物理.md | 知识库/18_游戏物理与模拟/角色、布料、破坏与载具物理.md | 角色、布料、破坏与载具物理 | 延后 |
| 知识库/19_Gameplay与游戏框架/玩法系统、事件与脚本.md | 知识库/19_Gameplay与游戏框架/玩法事件与脚本.md | 玩法事件与脚本 | 采用 |
| 知识库/19_Gameplay与游戏框架/输入、动作状态与框架分层.md | 知识库/19_Gameplay与游戏框架/输入与动作状态.md | 输入与动作状态 | 采用 |
| 知识库/20_游戏AI/导航、寻路与移动控制.md | 知识库/20_游戏AI/游戏AI导航.md | 游戏AI导航 | 采用 |
| 知识库/20_游戏AI/群体、学习与高级决策.md | 知识库/20_游戏AI/群体、学习与高级决策.md | 群体、学习与高级决策 | 延后 |
| 知识库/20_游戏AI/行为树、效用与规划.md | 知识库/20_游戏AI/游戏AI决策模型.md | 游戏AI决策模型 | 采用 |
| 知识库/21_游戏网络/服务器架构、分区与反作弊.md | 知识库/21_游戏网络/服务器架构、分区与反作弊.md | 服务器架构、分区与反作弊 | 延后 |
| 知识库/21_游戏网络/状态同步、预测与回滚.md | 知识库/21_游戏网络/状态同步、预测与回滚.md | 状态同步、预测与回滚 | 延后 |
| 知识库/21_游戏网络/网络协议、时钟与RPC.md | 知识库/21_游戏网络/网络协议、时钟与RPC.md | 网络协议、时钟与RPC | 延后 |
