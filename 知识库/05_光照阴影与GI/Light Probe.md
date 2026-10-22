# Light Probe

角色走出阴影，不能直接读取墙面的Lightmap。Light Probe在空间点保存低频光照，角色根据位置插值这份表示。系数重建与墙体可见性不同，漏光往往来自探针无效或跨墙插值。

## 低频光照表示

Light Probe 在离散空间点保存低频环境光，常用 SH 表示。动态物体根据位置插值附近 Probe，再按表面法线求光照。

Probe 的主要问题不是“数量不够”这么简单：

- Probe 放在墙内会记录错误环境；
- 墙两侧插值会漏光；
- 光照突变处需要更合理分布；
- 角色活动范围以外的 Probe 没有价值；
- 低阶 SH 不能表达锐利方向光和高频阴影。

### 存储与运行时读取

探针捕获线性HDR方向光照后，按 [[01_数学与采样/球谐光照]] 投影并卷积。运行时插值的是同一基底下的系数，空间有效性由探针系统保存。

保留 $l=0,1,2$ 三个频带时，共有 $1+3+5=9$ 个 SH 基函数。RGB 各保存 9 个系数，27 个浮点数按约定的基函数顺序排列，引擎通常打包成若干个 float4 传入 Shader。存储27个32位浮点数时，每个探针的原始系数占108字节，尚未计索引、对齐和可见性数据。均匀网格查询简单；稀疏布局可按光照变化密度分配探针，但会增加寻址与插值成本。空旷区域也可能有细窄光束，密度应按误差与活动范围确定。

烘焙时先确认 Cubemap 保存的是线性 HDR 数据。普通 8 位归一化 RGBA 格式不能直接保存大于 1 的辐射值，需使用浮点格式或明确的 HDR 编码。

迁移球谐系数时再核对基函数顺序、符号和归一化常数，以及是否已经卷积余弦核。约定不一致会导致亮度缩放或光照方向错误。用单位白色环境和单方向光分别验证。

验证方法是在 Probe 影响区域放一个纯白漫反射球，与同位置的完整烘焙结果对比。低频部分应基本一致；高频方向的差异可能来自阶数截断，也可能来自采样或编码错误；可提高阶数、固定输入逐项比较来区分。

## 三线性 Probe 插值

规则网格内的着色点先转为 Probe 网格坐标，再对包围它的八个 Probe 做三线性插值。每个 Probe 保存相同基底下的 SH 系数：

```hlsl
struct SH9 { float3 c[9]; };
StructuredBuffer<float3> ProbeCoefficients : register(t0);

SH9 InterpolateProbes(float3 positionWS, float3 gridOriginWS,
    float3 cellSize, uint3 gridSize)
{
    float3 grid = (positionWS - gridOriginWS) / cellSize;
    int3 baseCell = clamp((int3)floor(grid), int3(0,0,0), int3(gridSize)-2);
    float3 t = saturate(grid - float3(baseCell));
    SH9 sh;
    for (uint k=0; k<9; ++k) sh.c[k]=0.0;
    for (uint corner=0; corner<8; ++corner) {
        int3 bit = int3(corner&1, (corner>>1)&1, (corner>>2)&1);
        float3 w = lerp(1.0-t, t, float3(bit));
        float weight = w.x*w.y*w.z;
        uint3 index = uint3(baseCell+bit);
        uint probe = index.x + gridSize.x*(index.y+gridSize.y*index.z);
        for (uint k=0; k<9; ++k)
            sh.c[k] += ProbeCoefficients[probe*9+k] * weight;
    }
    return sh;
}
```

这是 HLSL 机制函数，`gridSize` 每维至少2，`cellSize` 为正且与世界位置同单位。缓冲按X最快、每探针9个`float3`排列，结构化缓冲元素步长为12字节。示例把体积外位置钳到边界；也可由宿主选择环境回退，需明确策略。得到9个系数后按 [[01_数学与采样/球谐光照]] 的同名实基求值；本页约定系数已做余弦卷积，输出为辐照度，Lambert材质再乘反照率并除π。

八角权重相加为 `(1-t.x+t.x)*(1-t.y+t.y)*(1-t.z+t.z)=1`，因此常量场保持不变，线性场在单元内可精确重建。简单三线性插值会穿过墙体漏光，可见性或有效性权重加入后，应对剩余权重重新归一化；总权重为零时使用明确回退，不能除以零。距离可见性估计见 [[05_光照阴影与GI/动态GI]]。把物体沿单元边界缓慢移动，亮度应连续；出现格子跳变时先检查索引 Clamp 和八角权重和是否为 1。

## 验证方法

用同一位置白色球对照参考积分，跨单元边界时亮度应连续。输出八角权重和、有效标记与深度可见性，在薄墙两侧检查漏光。SH基底定义与投影公式以球谐光照为主归属。

[test_gi.py](../examples/revision/test_gi.py) 检查权重和、角点选择及仿射光照场重建；正文插值函数完成DXC编译。捕获光照、探针布局和实际GPU数据尚未验证。

本机CPU验证：三线性权重和由 [completion_reference.py](../examples/mechanisms/completion_reference.py) 检查，运行 `python 知识库/examples/mechanisms/completion_reference.py`。这些检查验证插值模型，不包含GPU执行。

## 相关主题

- [[01_数学与采样/球谐光照]]
- [[04_光照模型与PBR/IBL]]
- [[05_光照阴影与GI/Lightmap]]
- [[05_光照阴影与GI/Reflection Probe]]
- [[05_光照阴影与GI/动态GI]]

## 参考资料

- [[01_数学与采样/球谐光照]]：9项基底、投影与余弦卷积的公式和原始资料。
- [Majercik 等：DDGI 算法说明](https://morgan3d.github.io/articles/2019-04-01-ddgi/algorithm.html)：空间探针的辐照度查询及可见性需求。
