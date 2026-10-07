# LOD选择

距离一样的树和大楼占屏幕大小不同，按固定距离减面会让两者产生不同误差。LOD先估计屏幕贡献，再选择几何、材质和动画预算；切换稳定性由过渡与滞回处理。

## 以屏幕占比决定 LOD

只按世界距离切换会忽略物体大小、FOV 和分辨率。引擎通常根据包围体投影到屏幕的比例选择 LOD。大物体在相同距离下会比小物体更晚降级。

透视投影下，物体的近似屏幕高度与下面的比例相关：

$$
s \propto \frac{h}{d\tan(\theta/2)}
$$

$h$ 是物体世界高度，$d$ 是相机距离，$\theta$ 是垂直 FOV。实际引擎还会使用包围球、投影矩阵和平台缩放，因此阈值应在目标设备实测。

## LOD 减什么

LOD 不只调整三角形：

- 减少轮廓影响较小的边和内部结构；
- 降低圆柱段数、枝干分段和小装饰数量；
- 合并材质或取消局部 Detail Pass；
- 降低骨骼数、动画更新频率和 Blendshape；
- 切换较便宜的 Shader、阴影或透明策略；
- 在远处换成 Impostor/Billboard，最后完全剔除。

植被远景应优先保留主干和树冠轮廓。随机裁掉末级小枝比整体 Decimate 更稳定。裁叶后可略微放大保留叶簇，补偿视觉密度。

## 切换、Cross Fade 与 Hysteresis

硬切换只绘制一个 LOD，成本稳定，但轮廓或材质突然变化会产生 Pop。

Cross Fade 在过渡区同时绘制两级，通过 Dither 或 Alpha 混合切换。它改善连续性，却会暂时增加顶点、像素和 Draw 成本。透明植被还可能放大 Overdraw。

Hysteresis 为进入和退出阈值留出差值，避免摄像机在边界附近时来回切换。相机快速移动时还要考虑资源是否已经流送完成。

## Geometry LOD 与 Mipmap 要同步

几何变少时，材质细节也应随之预过滤。否则远距离会出现：

- 高频 Normal Map 闪烁；
- Alpha Clip 叶片因 Mipmap 平均后变细或消失；
- 细线、铁丝和小孔时隐时现；
- 纹理仍保持高分辨率，几何省下的成本被带宽抵消。

植被可使用 Alpha-to-Coverage、保 Alpha Coverage 的 Mip 生成或远景专用贴图。阈值补偿需要检查不同背景和 MSAA 设置，不能只在一张截图上调好。

## LOD 预算来自画面与平台

阈值不应写成所有资产共用的固定距离。可以先按类别设预算，再由捕获验证：

- Hero Asset 关注轮廓、材质与阴影连续性；
- 重复道具关注 Draw、顶点和实例数据；
- 植被关注 Alpha Overdraw、阴影和风动更新；
- 地形关注纹理采样、Tile 流送和远景几何；
- 移动端还要检查带宽、热降频和内存峰值。

同一 LOD 方案在 1080p 手机、4K PC 和 VR 双眼中产生的屏幕误差不同。最终阈值应成为平台质量档配置，而不是只存在于 DCC 导出预设。

## 带滞回的 LOD 选择

输入 `screenFraction` 是对象投影尺寸占屏幕高度的比例，阈值按从高细节到低细节排列。滞回让进入和退出使用不同边界：

```cpp
int SelectLod(float screenFraction, int currentLod,
              Span<float> enterLower, float hysteresis)
{
    int lod = currentLod;
    while (lod < enterLower.size()
        && screenFraction < enterLower[lod] - hysteresis) ++lod;
    while (lod > 0
        && screenFraction > enterLower[lod - 1] + hysteresis) --lod;
    return lod;
}
```

阈值单位必须与 `screenFraction` 一致。滞回区间过大，会让对象长时间停留在不合适的 LOD；没有滞回时，相机在阈值附近抖动会造成频繁切换。验证应记录每秒 LOD 切换次数，并用缓慢往返相机检查进入与退出边界。

## 验证方法

固定FOV与分辨率往返经过阈值，记录切换次数、轮廓差和双绘制成本。远景法线、Alpha覆盖与材质mip同时检查；流送未完成时回退已驻留层。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[08_几何与网格/网格数据与GPU访问]]
- [[26_GPU驱动与虚拟几何/Nanite几何选择与流送]]
- [[08_几何与网格/Heightfield地形]]
- [[15_资产与工具管线/程序化资产生成]]
- [[08_几何与网格/植被包裹法线]]
- [[15_资产与工具管线/WFC]]

## 参考资料

- Paul Merrell, *Model Synthesis* and SideFX WFC dungeon generator tutorial.
- Gabriel Taubin, *A Signal Processing Approach to Fair Surface Design*, SIGGRAPH.

- Unity Manual, *LOD Group* and *Terrain Data*.
- Houdini Documentation, *HeightField*, *PDG* and *Houdini Engine for Unity*.
- Lindstrom and Turk, *Fast and Memory Efficient Polygonal Simplification*.
- meshoptimizer documentation, *Vertex cache optimization*.
- LearnOpenGL, `src/8.guest/2021/3.tessellation`.
