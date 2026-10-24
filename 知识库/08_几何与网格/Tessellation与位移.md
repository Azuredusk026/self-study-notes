# Tessellation与位移

近看模型露出折角，直接换高模能改善，却会让远景也承担同样的几何成本。Tessellation在运行时细分Patch，再由求值Shader决定新点位置。先分清生成密度和几何位移，才能判断裂缝来自共享边因子，还是高度采样与变换。

## 管线位置

固定管线插入三个阶段，位于 Vertex Shader 与 Geometry Shader 之间：

1. **Hull Shader**（OpenGL 称 Tessellation Control Shader）：输出细分因子和控制点；
2. **Tessellator**：固定功能硬件，按细分因子在参数域内生成拓扑；
3. **Domain Shader**（OpenGL 称 Tessellation Evaluation Shader）：对每个新顶点求最终位置与属性。

Tessellator 本身不可编程。它只知道参数域坐标，不知道模型形状。所有几何含义都由 Hull 和 Domain 两个可编程阶段赋予。

## 控制点与 Patch

启用细分后，Vertex Shader 的职责变成处理控制点。典型位移实现将位置保留在模型或世界空间，由求值阶段计算最终裁剪位置。API 不强制顶点阶段采用这一空间，所有阶段的数据约定需保持一致。

Patch 的控制点数量由 API 声明。线性三角面常用三个控制点，双线性四边形常用四个；三角或四边参数域本身不限定控制点数。Bezier 等高阶曲面可以使用更多控制点，由求值函数解释其几何含义。

Hull Shader 的输出控制点数量不必等于输入数量，但两者都由管线与着色器声明固定；这允许把一种控制网转换成另一种，不能逐 Patch 任意改变输出数量。

## 细分因子

Hull Shader 分为两部分。Patch Constant Function 每个 Patch 执行一次，输出边细分因子与内部细分因子；Control Point Function 每个输出控制点执行一次。

因子语义随 Domain 类型变化：

| Domain | `SV_TessFactor` | `SV_InsideTessFactor` |
|---|---|---|
| `quad` | 长度 4，四条边各分几段 | 长度 2，内部横向与纵向各分几段 |
| `tri` | 长度 3，三条边各分几段 | 长度 1，控制内部采样密度 |
| `isoline` | 长度 2，线段数量与每段细分数 | 忽略 |

tri的内部因子控制内部采样密度，边因子独立控制边界采样。应用消费规范提供的重心坐标，不应把特定内部生成示意当作跨API的通用算法；参数域拓扑见后文。

Direct3D11的integer与fractional_even有效上限为64，fractional_odd为63；OpenGL 支持细分的核心实现保证最大等级至少为 64，实际查询 `GL_MAX_TESS_GEN_LEVEL`。`maxtessfactor` 属性把 Shader 实际使用的上限告知驱动，硬件可能据此优化。

## 分割模式

`partitioning` 决定细分因子的小数部分如何处理：

- `integer`：因子向上取整。因子跨越整数边界时，新顶点整排突然出现，产生可见跳变（Popping）；
- `fractional_odd`：保持奇数段数，小数部分体现为新边从零宽度平滑生长；
- `fractional_even`：同理但保持偶数段数。

fractional 模式能缓和细分因子变化时的顶点插入。整数模式会改变离散段数，若要平滑过渡还需形变或交叉淡化。是否可见取决于位移和投影大小。

相邻Patch共享边要使用兼容的分割模式与相同边因子。边界位置的计算顺序、UV、法线和位移mip也要一致，否则因子相同仍可能出现裂缝。因子应当由共享边的两个端点唯一决定，例如用共享端点投影后的像素边长除以目标段长，而不能使用 Patch 中心或面法线——后者在两侧 Patch 上取值不同。

## 参数域坐标

Tessellator 把新顶点以参数坐标交给 Domain Shader，形式随 Domain 类型变化：

- `quad` 与 `isoline`：二维 UV 坐标；
- `tri`：三维重心坐标 $(u,v,w)$，满足 $u+v+w=1$。

Domain Shader 对每个新顶点执行一次，用这些参数坐标在控制点之间插值。它的调用次数随生成点数增加，所需顶点属性也在此求值，并完成到裁剪空间的变换。实际瓶颈还可能来自细分单元、纹理访问或后续光栅化，应分别计时。

### Domain Shader 的插值与位移

下面是tri Domain的HLSL宿主片段。控制点位置和单位法线在对象空间，位移强度采用对象长度单位；法线插值和要求非零。输入gWorld与gViewProj采用行向量乘法，输出裁剪坐标。高度图按线性数据读取，Domain阶段使用SampleLevel显式指定mip：

```hlsl
[domain("tri")]
DomainOut DS(PatchTess patchTess,
             float3 bary : SV_DomainLocation,
             const OutputPatch<HullOut, 3> tri)
{
    float3 posL = tri[0].PosL * bary.x
                + tri[1].PosL * bary.y
                + tri[2].PosL * bary.z;
    float3 nrmL = normalize(tri[0].NrmL * bary.x
                          + tri[1].NrmL * bary.y
                          + tri[2].NrmL * bary.z);
    float2 uv   = tri[0].UV * bary.x
                + tri[1].UV * bary.y
                + tri[2].UV * bary.z;

    float h = gHeight.SampleLevel(gSampler, uv, gHeightMip).r;
    posL += nrmL * ((h - gDisplaceBias) * gDisplaceScale);

    DomainOut dout;
    dout.PosH = mul(mul(float4(posL, 1.0), gWorld), gViewProj);
    return dout;
}
```

在控制点形成平面三角形、属性线性插值且没有其他变形时，去掉位移会回到原三角形表面；浮点与光栅化差异仍可能改变少量像素。形状变化来自 Domain Shader 对位置的修改，或来自 Bezier 等高阶曲面求值。

位移方向用插值法线时，法线必须在插值后重新归一化。`gDisplaceBias` 是高度图单位下的零位面，先减偏置再乘强度。这样强度归零时位移也归零。验证方法是把 `gDisplaceScale` 设为 0，几何位置应回到未位移的线性表面。选择gHeightMip时还要保证共享边读取同一高度信号；始终采mip0可能放大远景高频几何。阴影和深度预通道应使用一致位移，并扩展剔除Bounds。

## Unity URP 中的写法

Unity6.0允许通过hull/domain入口声明细分阶段，并要求对应GPU特性。下列只是阶段入口示意，URP的Pass标签、光照、阴影和顶点结构仍需与目标包匹配：

```hlsl
#pragma require tessellation tesshw
#pragma vertex TessVert
#pragma hull Hull
#pragma domain Domain
#pragma fragment Frag
```

顶点阶段输出的是控制点，Domain阶段才写最终SV_POSITION。某些Unity示例使用INTERNALTESSPOS标记控制点位置；它属于相应生成代码的接口约定，不能据此要求所有手写URP管线都替换POSITION。平台能力应结合目标图形API、编译目标和运行设备检查。本页未创建Unity工程，独立DXC编译结果不能视为URP接入通过。

## 几何生成与采样成本

细分把成本从内存与带宽转移到 GPU 几何阶段：

- 均匀提高二维tri/quad内外因子时，Domain求值和输出图元数量近似平方增长；原Vertex Shader仍按输入控制点运行；
- Domain Shader按生成的域点采样，通常需要显式LOD；采样次数随生成点数增加；
- 细分产生的大量小三角形会降低光栅化效率。亚像素三角形可能造成较多辅助调用和较低 Quad 利用率，具体比例取决于覆盖和硬件；
- 硬件细分单元在部分 GPU 上是独立的有限吞吐单元，可能成为新瓶颈。

因此细分因子应当由屏幕空间尺寸驱动，目标是让每个输出三角形落在若干像素的范围内，而不是无条件取满 64。

## 与其他 LOD 方案的关系

离散 LOD 切换整套网格，切换瞬间有跳变但运行时成本可预测。细分结合分数分割和一致的曲面求值可以缓和过渡，代价是每帧几何阶段开销。Nanite 等虚拟化几何方案则在 Cluster 层级做选择，绕开了固定细分单元。

位移贴图与视差映射解决相似的视觉问题。视差只改变采样 UV，不产生真实几何，几何轮廓保持原网格，自阴影需要另加高度场光线查询；位移改变真实顶点位置，轮廓逼近程度取决于几何采样密度和高度信号，成本则取决于生成点数、着色和覆盖。

## Phong细分曲面

线性重心插值得到点q，只增加采样密度。Phong细分将q分别投影到三个顶点的切平面，然后混合三个投影结果。对位置p_i与单位法线n_i：

$$q=\sum_i b_i p_i,\quad \pi_i(q)=q-[(q-p_i)\cdot n_i]n_i,$$

$$p_{phong}=\sum_i b_i\pi_i(q),\quad p=(1-\alpha)q+\alpha p_{phong}.$$

b是重心坐标，α在[0,1]，所有位置和法线处于同一对象空间。每次投影减去沿法线的有符号距离，结果落在对应顶点切平面。α=0回到线性表面；α=1使用完整投影混合。位于某个顶点时，对应权重为1且投影距离为0，因此顶点保持不动；三个法线一致且垂直于原三角形时，整片三角形保持不动。沿插值法线加固定长度不具有这两个性质。

```hlsl
float3 q = bary.x*p0 + bary.y*p1 + bary.z*p2;
float3 a = q - dot(q-p0, n0)*n0;
float3 b = q - dot(q-p1, n1)*n1;
float3 c = q - dot(q-p2, n2)*n2;
float3 position = lerp(q, bary.x*a + bary.y*b + bary.z*c, strength);
```

曲面由顶点切平面近似，不保证恢复原高模，也不保证凹区无折叠。共享边上的两端法线一致时，两侧投影计算能对应；硬边使用不同法线则需要边界约束。完整Domain入口见 [domain.hlsl](../examples/revision_06_08/domain.hlsl)，包含显式高度mip与对象空间位移。

## 参数点生成的API约定

固定细分阶段输出参数域坐标和拓扑，Domain Shader再赋予几何位置。Direct3D功能规范定义其精度和生成规则，不能把这一后端规则自动推广成所有API硬件实现。

三角域可按内部因子形成环，再用各边外部因子连接边界。具体拓扑和退化处理以目标API规范为准；应用只依赖域坐标、因子和一致共享边。

OpenGL的equal、fractional_even与fractional_odd分别向对应整数段数约束。fractional模式有少量短段参与连续过渡，短段长度和位置由规范决定，不能把“分数段数”直接当作世界距离。

## 验证方法

- 线框模式下拉近拉远相机，观察细分因子是否连续变化，`integer` 模式应能看到整排新顶点突现。
- 检查相邻 Patch 边界是否出现裂缝，同时检查因子、分割模式、边端点、位移UV与mip是否一致。
- 在帧捕获中查看 Domain Shader 调用次数与输出图元数，确认与预期细分因子相符。
- 在线性三角面求值模式中把位移强度归零，检查生成点仍落在原三角面；采用Phong或其他曲面求值时，先把曲面混合强度也归零。
- 统计输出三角形的平均屏幕面积；大量亚像素三角形提示检查细分是否过密，再结合轮廓与位移误差决定能否减少。


## 相关主题

- [[08_几何与网格/LOD选择]]、[[08_几何与网格/Heightfield地形]]、[[15_资产与工具管线/程序化资产生成]]、[[08_几何与网格/植被包裹法线]]、[[15_资产与工具管线/WFC]]
- [[06_纹理技术/视差映射]]
- [[02_GPU与光栅化管线/光栅化可见性]]
- [[02_GPU与光栅化管线/Geometry Shader]]、[[02_GPU与光栅化管线/Stream Output]]
- [[26_GPU驱动与虚拟几何/GPU-Driven Rendering]]
- [[10_VFX与模拟/水面与海洋渲染]]

本机检查：CPU模型`phong_point`验证顶点保持、共面保持和非平坦法线导致的曲面变化。`domain.hlsl`的DSMain已通过DXC ds_6_0编译，尚缺Hull、资源与绘制宿主；完整细分流水线、Unity运行、GPU画面和性能为尚未验证。运行入口见 [verify.py](../examples/revision_06_08/verify.py)。

## 参考资料

- [Boubekeur与Alexa，Phong Tessellation](https://perso.telecom-paristech.fr/boubek/papers/PhongTessellation/PhongTessellation.pdf)：2008论文第3节、公式(3)—(4)，切平面正交投影与重心混合；2026-10-22核读。
- [Microsoft，Tessellation Stages](https://learn.microsoft.com/en-us/windows/win32/direct3d11/direct3d-11-advanced-stages-tessellation)：Hull/Tessellator/Domain职责和分割范围。
- [Unity6.0，GPU feature requirements](https://docs.unity3d.com/6000.0/Documentation/Manual/SL-Pragma-require.html)：2026-10-22核读tessellation与tesshw能力要求；本页未执行URP集成。
