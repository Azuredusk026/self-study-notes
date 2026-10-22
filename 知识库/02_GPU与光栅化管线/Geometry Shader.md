# Geometry Shader

顶点阶段只看到单个输入顶点，画三角形边或生成调试几何却需要图元上下文。Geometry Shader每次接收一个图元，再输出数量有上限的新顶点。它提供这种局部生成能力，输出放大与有序流也决定了成本。

## 几何着色器的编程模型

几何着色器由 Direct3D 10 引入，随后进入 OpenGL 3.2 核心规范。它位于顶点着色器（或曲面细分）之后、光栅化之前，是可选阶段。

与顶点着色器的本质差异有两条：

- **输入单位是图元**。每次调用拿到一个完整图元的顶点数组：三角形 3 个、线段 2 个、点 1 个；带邻接信息时更多；
- **输出数量可变**。一次调用可以输出 0 到 N 个顶点，组成新的图元流。

HLSL 的概念形态：

```hlsl
[maxvertexcount(N)]
void GSMain(triangle VS_OUT input[3], inout TriangleStream<GS_OUT> outStream)
{
    // 可读取 input[0..2]，拥有整个三角形的上下文
    // 按需发射 0..N 个顶点
    outStream.Append(v);
    outStream.RestartStrip();
}
```

GLSL 形态：

```glsl
layout(triangles) in;
layout(triangle_strip, max_vertices = N) out;

void main() {
    gl_Position = f(gl_in[0].gl_Position);
    EmitVertex();
    EndPrimitive();
}
```

几个接口要点：

- `[maxvertexcount(N)]` 声明单次调用输出顶点的最大值，供编译器与硬件按最坏情况预留资源；
- 输出通过流类型表达：`PointStream`、`LineStream`、`TriangleStream`。线条与三角形的输出拓扑只有带（strip）形式；需要列表语义时用 `RestartStrip` 逐段切分。条带末端顶点数不足以构成图元的部分会被丢弃；
- 输出顶点的位置必须已经变换到齐次裁剪空间。顶点属性插值发生在光栅化阶段，几何着色器输出的每个顶点属性就是插值端点；
- 几何着色器中不存在屏幕空间导数。纹理访问可使用显式mip级别（如`SampleLevel`）、显式梯度或Load；不能依赖本阶段不存在的屏幕导数。

### 图元拓扑

几何着色器的输入前缀必须与输入装配阶段声明的图元拓扑一致，否则顶点对不上。基础拓扑分两类五种：点列表（point list）、线列表（line list）、线条带（line strip）、三角形列表（triangle list）、三角形带（triangle strip）。

列表与带的区别在顶点复用方式。三角形列表每三个顶点组成一个独立三角形；三角形带中每个后续顶点都与前两个顶点组成新三角形，$N$ 个顶点最多构成 $N-2$ 个三角形，退化图元和条带重启另计。索引三角形列表也能复用顶点；条带是否节省带宽或处理取决于索引排列、缓存和输出接口。

两个容易忽略的细节：

**绕序**。三角形带中相邻三角形共享边，顶点顺序天然交替，导致奇数位置与偶数位置的三角形绕序相反。图元装配规则按三角形序号交替调整有效绕序，使一个连续条带的正面方向一致；这是接口语义，不要求硬件物理交换顶点。

**邻接图元**。`lineadj`（4 顶点：线段本体加两端邻点）与 `triangleadj`（6 顶点：三角形本体加三条边的对顶点）只为几何着色器提供邻接信息，邻接顶点不会被绘制——即使管线没有启用几何着色器，邻接顶点也不会出现在画面上。轮廓检测等算法依赖这一输入形态。

## 几何着色器的应用

几何着色器的用法可以统称为**有限放大**：每个输入图元的输出上限可控、放大量不大。

### 广告牌：点扩展为四边形

广告牌要求一个面片始终朝向相机。把每个广告牌存成一个点，几何着色器在 GPU 端把它扩展为两个三角形组成的四边形，CPU 每帧只需提交点列表，不必回写顶点缓冲。

核心是用观察方向构造面片的局部坐标架。下面的圆柱广告牌保持世界上方向，只绕竖直轴转向相机：

```hlsl
[maxvertexcount(4)]
void GS(point VS_IN input[1], inout TriangleStream<GS_OUT> triStream)
{
    float3 up = float3(0, 1, 0);
    float3 look = GetWorldSpaceViewDir(input[0].positionWS);
    look.y = 0.0;
    float lookLengthSq = dot(look, look);
    look = lookLengthSq > 1e-8 ? look * rsqrt(lookLengthSq) : float3(0, 0, 1);
    float3 right = cross(up, look);

    float2 corners[4] = { float2(-1,-1), float2(1,-1), float2(-1,1), float2(1,1) };
    for (int i = 0; i < 4; ++i) {
        float3 posWS = input[0].positionWS
                     + right * corners[i].x * halfWidth
                     + up * corners[i].y * halfHeight;
        GS_OUT o;
        o.positionCS = TransformWorldToHClip(posWS);
        o.uv = corners[i] * 0.5 + 0.5;
        triStream.Append(o);
    }
}
```

`look.y = 0` 是圆柱与球面广告牌的分界：压平视方向的竖直分量后，`right` 只随水平朝向变化，面片不俯仰。观察方向与世界上方向接近平行时 `look` 退化，需要另行处理。用 `SV_PrimitiveID` 作为索引采样纹理数组，可以让同一批点呈现不同外观。

### 线框渲染：逐片元到边距离

线框效果要求片元知道自己离所在三角形最近边有多远。共享索引顶点未必保存每个三角形角的重心身份，Geometry Shader是一条补充图元上下文的路径。独立角顶点或支持的片元重心扩展也能提供线框信号。几何着色器可以算出每个顶点到对边的距离，作为属性交给光栅化插值：

```hlsl
[maxvertexcount(3)]
void GS(triangle VS_IN p[3], inout TriangleStream<GS_OUT> triStream)
{
    // 顶点已是裁剪空间坐标：先做透视除法到 NDC，再映射到屏幕像素
    float2 p0 = screenSize * (p[0].positionCS.xy / p[0].positionCS.w * 0.5 + 0.5);
    float2 p1 = screenSize * (p[1].positionCS.xy / p[1].positionCS.w * 0.5 + 0.5);
    float2 p2 = screenSize * (p[2].positionCS.xy / p[2].positionCS.w * 0.5 + 0.5);

    float2 e0 = p2 - p1, e1 = p2 - p0, e2 = p1 - p0;
    float area = abs(e1.x * e2.y - e1.y * e2.x);
    float3 d = float3(area / length(e0), area / length(e1), area / length(e2));
    // GS_OUT.edgeDistance必须声明为 noperspective float3
    for (int i = 0; i < 3; ++i) {
        GS_OUT o;
        o.positionCS = p[i].positionCS;
        o.edgeDistance = float3(0, 0, 0);
        o.edgeDistance[i] = d[i];
        triStream.Append(o);
    }
}
```

在屏幕像素空间计算距离，线宽才能以像素为单位稳定控制。片元着色器取三个分量的最小值，经指数衰减得到抗锯齿的线宽，阈值外的片元丢弃。距离属性在片元阶段使用屏幕线性插值（如noperspective）才能保持屏幕距离含义。该片段要求输入已经位于可投影的同一裁剪区域，且三条边长度非零；跨近平面三角形应先正确裁剪并重算距离，不能只检查w非零。注意这里必须手动做透视除法：几何着色器拿到的 `positionCS` 尚未除以 $w$。

### 法线可视化与调试几何

对每个三角形或每个顶点生成一条短线段表示法线，是检查法线数据的直接手段。线起点取三角形重心或顶点位置，终点沿法线偏移固定长度，用 `LineStream` 输出。这类调试几何放在独立的渲染通道中，配合图层或渲染队列与正常绘制区分。

### 视距驱动的曲线细分

绘制光滑曲线需要把曲线离散成折线。近景段数不足会出现折角，远景段数过多则增加几何工作。几何着色器可以接收四个控制点，按视距决定输出段数。以下 GLSL 3.30 机制片段要求顶点阶段以独立属性传入视空间控制点 P0—P3，均使用同一长度单位；相机位于视空间原点，`proj` 负责投影。`maxDist > minDist >= 0`，`1 <= minSeg <= maxSeg <= 63`。

三次贝塞尔求值 `bezier3(t,P0,P1,P2,P3)` 的完整定义是 $(1-t)^3P_0+3(1-t)^2tP_1+3(1-t)t^2P_2+t^3P_3$，输入t在[0,1]，输出仍是视空间位置。t为0和1时分别得到首尾控制点。下列片段省略属性接口及uniform声明：

```glsl
layout(lines_adjacency) in;
layout(line_strip, max_vertices = 64) out;

void main() {
    vec3 mid = bezier3(0.5, P0, P1, P2, P3);
    float w = clamp((length(mid) - minDist) / (maxDist - minDist), 0.0, 1.0);
    int segments = clamp(int(round(mix(float(maxSeg), float(minSeg), w))), 1, 63);

    for (int i = 0; i <= segments; ++i) {
        gl_Position = proj * vec4(bezier3(float(i) / segments, P0, P1, P2, P3), 1.0);
        EmitVertex();
    }
    EndPrimitive();
}
```

贝塞尔曲线完全由控制点决定，对控制点做仿射变换曲线形状同步保持，因此控制点只需在顶点着色器变换一次，几何着色器直接在变换后的控制点上求值。

用曲线中点距离选择段数只是启发式：同一视距下，投影尺度和曲率仍会改变屏幕误差。质量要求更高时可按投影后的曲线与弦之间的偏差细分，并限制最大输出量。规模化的规则细分还可采用专用曲面细分阶段。

### 草地：两个阶段的组合

大规模草地演示常把两个阶段串起来用：曲面细分负责增密（把地面网格细分出大量顶点，按细分后的图元选择草叶基点），几何着色器负责成形（把每个细分出的图元扩展成一根弯曲的草叶）。

一根草叶的生成按执行顺序是若干几何操作的组合：

1. 以基点位移哈希为种子，用轴角公式构造三个旋转矩阵——朝向随机旋转、弯曲随机旋转、风力旋转（风力纹理在域着色器阶段用显式 mip 采样后传递，因为细分与几何阶段都没有屏幕导数）；
2. 由法线、切线、副切线建立切空间到世界的变换，与三个旋转矩阵依次相乘，得到这根草的完整姿态矩阵；
3. 沿高度分若干段，每段输出左右两个顶点形成条带：宽度随高度线性收窄，前向弯曲量按 $t^{curve}$ 增长，幂指数控制弯曲形状；
4. 对高度场地面，在每个顶点的水平位置采样地面高度，限制该顶点不低于地面。固定高度只适用于水平平面；悬崖与悬挑表面需要另外的碰撞表示，顶点约束也不能保证整片三角形均不穿透。

曲面细分器产生参数域采样点，域着色器求出位置，几何着色器再按图元生成叶片。两级放大量相乘后，应预算输出顶点、覆盖面积和阴影重复绘制。可与实例化叶片、计算着色器生成方案在相同草密度和画质下比较，性能结论由目标设备测量决定。

## 几何着色器的执行成本

几何着色器的成本来自每图元调用、可变输出和后续光栅化。判断瓶颈需同时改变输入图元数、输出上限与实际输出量。

**执行不均衡**。可变输出与分支可能降低执行批次利用率，具体调用映射与输出发射由硬件实现决定。Geometry Shader没有Compute线程组协作模型，不能把它描述为同组barrier等待。

**预留缓冲压力**。`maxvertexcount`给出输出上界，编译器与硬件可据此分配输出资源。较大的上界可能限制并发，即使实际输出较少也可能有成本；具体分配方式、是否溢出以及存储位置属于硬件实现。预留和发射成本需目标平台的编译统计与计数器确认。

**后变换缓存失效**。顶点着色器的结果可以按索引复用，避免同一顶点重复变换。几何着色器生成的顶点是全新顶点，没有索引身份，无法进入这套缓存，同样的数据也要重新计算。

**输出上限**。Direct3D 10 规定几何着色器单次调用最多输出 1024 个 32 位标量，足以让它只做小规模几何操作。早期GPU指南中的吞吐数字只适用于其具体硬件和测试，不能作为当前设备的成本预测。

**顺序保证**。图形管线要求输出结果等同于按输入顺序串行执行。并行产出可变数量的图元后，还要花代价把它们重新排成确定顺序。

由此得到使用边界：几何着色器适合整个图元级的任务——轮廓判断、中心计算、少量辅助几何；不适合大规模几何生成。移动端部分平台直接不支持几何着色器。需要大规模生成时，方向是实例化、计算着色器或网格着色器。

## 验证方法

分别输入点、线和三角形，核对调用数、邻接顶点与输出上限。关闭生成逻辑后比较GPU时间，逐步增加放大率。广告牌方向关系由Billboard说明，细分控制点与参数域由Tessellation与位移说明。

实现状态：HLSL/GLSL均为机制片段，宿主补齐输入输出类型、矩阵、屏幕尺寸和缓冲；线框片段明确发射距离属性，广告牌提供垂直视角退化方向。未编译完整Geometry Shader管线，未测放大吞吐；拓扑与Append语义已核对官方文档。

## 相关主题

- [[08_几何与网格/Billboard]]
- [[08_几何与网格/Tessellation与位移]]
- [[02_GPU与光栅化管线/Stream Output]]

## 参考资料

- [Microsoft HLSL Append](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-so-append)：2026-10-22核读StreamDataType与CubeMapGS示例，支持Append及RestartStrip的输出关系。
- [Microsoft Geometry-Shader Stage](https://learn.microsoft.com/en-us/windows/win32/direct3d11/geometry-shader-stage)：2026-10-22核读输入图元、输出拓扑、RestartStrip与允许的显式采样操作；完整平台能力以设备查询为准。
- 广告牌坐标构造与曲面细分机制分别由相关专篇维护。
