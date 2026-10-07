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
- 几何着色器中不存在屏幕空间导数。需要采样纹理时只能用显式 mip 级别（如 `SampleLevel`），不能使用依赖隐式 LOD 的采样。

### 图元拓扑

几何着色器的输入前缀必须与输入装配阶段声明的图元拓扑一致，否则顶点对不上。基础拓扑分两类五种：点列表（point list）、线列表（line list）、线条带（line strip）、三角形列表（triangle list）、三角形带（triangle strip）。

列表与带的区别在顶点复用方式。三角形列表每三个顶点组成一个独立三角形；三角形带中每个后续顶点都与前两个顶点组成新三角形，$N$ 个顶点表达 $N-2$ 个三角形，内存与处理都更省。

两个容易忽略的细节：

**绕序**。三角形带中相邻三角形共享边，顶点顺序天然交替，导致奇数位置与偶数位置的三角形绕序相反。GPU 内部会对偶数序三角形的后两个顶点做调换，使所有三角形保持一致的绕序，背面剔除才能正确工作。

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
    look = normalize(look);
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
    // 三个顶点分别携带 (d0,0,0) (0,d1,0) (0,0,d2)，光栅化时自动插值
}
```

在屏幕像素空间计算距离，线宽才能以像素为单位稳定控制。片元着色器取三个分量的最小值，经指数衰减得到抗锯齿的线宽，阈值外的片元丢弃。距离属性在片元阶段使用屏幕线性插值（如noperspective）才能保持屏幕距离含义。退化三角形与接近零w要拒绝。注意这里必须手动做透视除法：几何着色器拿到的 `positionCS` 尚未除以 $w$。

### 法线可视化与调试几何

对每个三角形或每个顶点生成一条短线段表示法线，是检查法线数据的直接手段。线起点取三角形重心或顶点位置，终点沿法线偏移固定长度，用 `LineStream` 输出。这类调试几何放在独立的渲染通道中，配合图层或渲染队列与正常绘制区分。

### 视距驱动的曲线细分

绘制光滑曲线需要把曲线离散成折线。固定段数的两难是：近景段数不足出现折角，远景段数过多浪费几何。几何着色器可以只提交控制点，按视距决定输出段数：

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

这个例子真正的意义是那条更一般的思想：让几何细节跟随视距与投影尺度生成，而不是在资产侧预烘焙所有 LOD。几何着色器不是实现这一思想的高效终局——曲面细分才是为规模化、规则化细分设计的阶段。

### 草地：两个阶段的组合

大规模草地演示常把两个阶段串起来用：曲面细分负责增密（把地面网格细分出大量顶点，每个顶点位置长一根草），几何着色器负责成形（把每个细分出的图元扩展成一根弯曲的草叶）。

一根草叶的生成按执行顺序是若干几何操作的组合：

1. 以基点位移哈希为种子，用轴角公式构造三个旋转矩阵——朝向随机旋转、弯曲随机旋转、风力旋转（风力纹理在域着色器阶段用显式 mip 采样后传递，因为细分与几何阶段都没有屏幕导数）；
2. 由法线、切线、副切线建立切空间到世界的变换，与三个旋转矩阵依次相乘，得到这根草的完整姿态矩阵；
3. 沿高度分若干段，每段输出左右两个顶点形成条带：宽度随高度线性收窄，前向弯曲量按 $t^{curve}$ 增长，幂指数控制弯曲形状；
4. 每个顶点的世界高度钳制不低于地面，防止弯曲穿透地表。

这类组合管线的代价也直接可见：曲面细分的放大作用在顶点阶段，几何着色器的放大作用在图元阶段，两级相乘后三角形数量爆炸，规模一大 GPU 就会跑满。它是教学演示的合理选择，不是生产草地方案——生产环境通常用实例化加预生成叶片，或计算着色器驱动的 GPU-Driven 方案。

## 几何着色器为什么慢

几何着色器在工程上的评价是“灵活但慢”，根源在于可变输出与 GPU 执行组织之间的结构性冲突。

**执行不均衡**。可变输出与分支可能降低执行批次利用率，具体调用映射与输出发射由硬件实现决定。Geometry Shader没有Compute线程组协作模型，不能把它描述为同组barrier等待。

**预留缓冲压力**。`maxvertexcount` 让编译器和硬件按最坏情况为每个线程预留输出存储。预留量乘以并发线程数，总量可能把片上缓冲挤到显存，带来显著带宽压力与延迟，进一步压低并行度。预留和发射成本需目标平台的编译统计与计数器确认。

**后变换缓存失效**。顶点着色器的结果可以按索引复用，避免同一顶点重复变换。几何着色器生成的顶点是全新顶点，没有索引身份，无法进入这套缓存，同样的数据也要重新计算。

**输出上限**。Direct3D 10 规定几何着色器单次调用最多输出 1024 个 32 位标量，足以让它只做小规模几何操作。早期GPU指南中的吞吐数字只适用于其具体硬件和测试，不能作为当前设备的成本预测。

**顺序保证**。图形管线要求输出结果等同于按输入顺序串行执行。并行产出可变数量的图元后，还要花代价把它们重新排成确定顺序。

由此得到使用边界：几何着色器适合整个图元级的任务——轮廓判断、中心计算、少量辅助几何；不适合大规模几何生成。移动端部分平台直接不支持几何着色器。需要大规模生成时，方向是实例化、计算着色器或网格着色器。

## 验证方法

分别输入点、线和三角形，核对调用数、邻接顶点与输出上限。关闭生成逻辑后比较GPU时间，逐步增加放大率。广告牌方向关系由Billboard说明，细分控制点与参数域由Tessellation与位移说明。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[08_几何与网格/Billboard]]
- [[08_几何与网格/Tessellation与位移]]
- [[02_GPU与光栅化管线/Stream Output]]

## 参考资料

- Frank Luna, *Introduction to 3D Game Programming with DirectX 12*, Tessellation and Geometry Shader chapters.
- Khronos OpenGL Wiki, *Tessellation*, *Tessellation Control Shader*, *Tessellation Evaluation Shader*, *Transform Feedback*.
- Microsoft Learn, *Geometry-Shader Stage*, *Primitive Topologies*, *Getting Started with the Stream-Output Stage*.
- Microsoft, *Direct3D 11.3 Functional Specification*, Tessellation Pattern and Fixed Order of Pipeline Results.
- NVIDIA, *GeForce 8 and 9 Series GPU Programming Guide*, Geometry Shader performance sections.
- Joshua Barczak, *Why Geometry Shaders Are Slow (Unless you're Intel)*.
- Jasper Bekkers, *Mesh Shaders and the Future of Geometry Processing*.
- Catlike Coding, *Flat and Wireframe Shading*.
