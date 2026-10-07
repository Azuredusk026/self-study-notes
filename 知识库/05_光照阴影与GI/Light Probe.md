# Light Probe

角色走出阴影，不能直接读取墙面的Lightmap。Light Probe在空间点保存低频光照，角色根据位置插值这份表示。系数重建与墙体可见性不同，漏光往往来自探针无效或跨墙插值。

## Light Probe

Light Probe 在离散空间点保存低频环境光，常用 SH 表示。动态物体根据位置插值附近 Probe，再按表面法线求光照。

Probe 的主要问题不是“数量不够”这么简单：

- Probe 放在墙内会记录错误环境；
- 墙两侧插值会漏光；
- 光照突变处需要更合理分布；
- 角色活动范围以外的 Probe 没有价值；
- 低阶 SH 不能表达锐利方向光和高频阴影。

### 存储与运行时读取

探针捕获线性HDR方向光照后，按 [[01_数学与采样/球谐光照]] 投影并卷积。运行时插值的是同一基底下的系数，空间有效性由探针系统保存。

27 个浮点数按这 9 个 SH 基函数的系数顺序排列，引擎通常打包成若干个 float4 传入 Shader。大场景中 Probe 数量巨大，稀疏八叉树等空间结构比均匀网格更省——空旷区域不需要密集采样。

烘焙时先确认 Cubemap 保存的是线性 HDR 数据。普通 8 位归一化 RGBA 格式不能直接保存大于 1 的辐射值，需使用浮点格式或明确的 HDR 编码。

迁移球谐系数时再核对基函数顺序、符号和归一化常数，以及是否已经卷积余弦核。约定不一致会导致亮度缩放或光照方向错误。用单位白色环境和单方向光分别验证。

验证方法是在 Probe 影响区域放一个纯白漫反射球，与同位置的完整烘焙结果对比。低频部分应基本一致；差异集中在高频方向说明这正是 SH 阶数的固有限制，而非数据错误。

## 三线性 Probe 插值

规则网格内的着色点先转为 Probe 网格坐标，再对包围它的八个 Probe 做三线性插值。每个 Probe 保存相同基底下的 SH 系数：

```hlsl
float3 grid = (positionWS - gridOriginWS) / cellSize;
int3 baseCell = clamp((int3)floor(grid), 0, gridSize - 2);
float3 t = saturate(grid - baseCell);
SH9 sh = 0;
for (uint corner = 0; corner < 8; ++corner) {
    int3 bit = int3(corner & 1, (corner >> 1) & 1, (corner >> 2) & 1);
    sh += LoadProbe(baseCell + bit) * TrilinearWeight(bit, t);
}
float3 irradiance = max(EvaluateSH9(sh, normalWS), 0.0);
```

位置、网格原点和 Cell Size 必须在同一世界空间。简单三线性插值会穿过墙体漏光，实际 Probe 系统还需要可见性、分类或位置偏移。把物体沿单元边界缓慢移动，亮度应连续；出现格子跳变时先检查索引 Clamp 和八角权重和是否为 1。

## 验证方法

用同一位置白色球对照参考积分，跨单元边界时亮度应连续。输出八角权重和、有效标记与深度可见性，在薄墙两侧检查漏光。SH基底定义与投影公式以球谐光照为主归属。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

本机CPU验证：三线性权重和由 [completion_reference.py](../examples/mechanisms/completion_reference.py) 检查，运行 `python 知识库/examples/mechanisms/completion_reference.py`。这些检查验证模型，不包含GPU执行或实际网络故障注入。

## 相关主题

- [[01_数学与采样/球谐光照]]
- [[04_光照模型与PBR/IBL]]
- [[05_光照阴影与GI/Lightmap]]
- [[05_光照阴影与GI/Reflection Probe]]
- [[05_光照阴影与GI/动态GI]]

## 参考资料

- Epic Games, *Lumen Global Illumination and Reflections*.
- NVIDIA, *RTXGI / Dynamic Diffuse Global Illumination*.
- Unity Manual, *Lightmapping and Light Probes*.
