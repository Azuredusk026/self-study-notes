# LOD选择

距离一样的树和大楼占屏幕大小不同，按固定距离减面会让两者产生不同误差。LOD先估计屏幕贡献，再选择几何、材质和动画预算；切换稳定性由过渡与滞回处理。

## 以屏幕占比决定 LOD

只按世界距离切换会忽略物体大小和FOV。屏幕比例本身不随分辨率改变；换算成像素误差时才需要输出尺寸。引擎通常根据包围体投影到屏幕的比例选择 LOD。大物体在相同距离下会比小物体更晚降级。

透视投影下，物体的近似屏幕高度与下面的比例相关：

$$
s \approx \frac{h}{2z\tan(\theta/2)}
$$

h是近似平行于屏幕竖轴的世界高度，z是正的视空间轴向深度，二者同单位；θ为垂直FOV。物体深度跨度相对z很小时可用这个近似。高度2米、z=10米、FOV=90度时，屏幕比例为0.1；1080像素高的输出约占108像素。离轴物体不能直接用到相机的欧氏距离替换z。

若离线简化误差上界为e米，可估计屏幕误差 `e_px ≈ e*H/(2*z*tan(θ/2))`，H为输出像素高度。它把物体尺寸进一步转成该级损失是否可见。包围体跨越近平面、巨大深度跨度或相机进入物体时，应使用保守投影或强制细节层。

## LOD的简化对象

LOD 不只调整三角形：

- 减少轮廓影响较小的边和内部结构；
- 降低圆柱段数、枝干分段和小装饰数量；
- 合并材质或取消局部 Detail Pass；
- 降低骨骼数、动画更新频率和 Blendshape；
- 切换较便宜的 Shader、阴影或透明策略；
- 在远处换成 Impostor/Billboard，最后完全剔除。

植被远景应优先保留主干和树冠轮廓。可按枝干层级裁减末级小枝，再与整体简化比较轮廓和时域稳定性；随机删除并不保证更稳定。裁叶后可略微放大保留叶簇，补偿视觉密度。

## 切换、Cross Fade 与 Hysteresis

硬切换只绘制一个 LOD，成本稳定，但轮廓或材质突然变化会产生 Pop。

Cross Fade 在过渡区同时绘制两级，通过 Dither 或 Alpha 混合切换。它改善连续性，却会暂时增加顶点、像素和 Draw 成本。透明植被还可能放大 Overdraw。

Hysteresis 为进入和退出阈值留出差值，避免摄像机在边界附近时来回切换。相机快速移动时还要考虑资源是否已经流送完成。

## 几何与材质细节同步

几何变少时，材质细节也应随之预过滤。否则远距离会出现：

- 高频 Normal Map 闪烁；
- Alpha Clip 叶片因 Mipmap 平均后变细或消失；
- 细线、铁丝和小孔时隐时现；
- 纹理仍保持高分辨率，几何省下的成本被带宽抵消。

植被可使用 Alpha-to-Coverage、保 Alpha Coverage 的 Mip 生成或远景专用贴图。阈值补偿需要检查不同背景和 MSAA 设置，不能只在一张截图上调好。

## LOD预算

阈值不应写成所有资产共用的固定距离。可以先按类别设预算，再由捕获验证：

- Hero Asset 关注轮廓、材质与阴影连续性；
- 重复道具关注 Draw、顶点和实例数据；
- 植被关注 Alpha Overdraw、阴影和风动更新；
- 地形关注纹理采样、Tile 流送和远景几何；
- 移动端还要检查带宽、热降频和内存峰值。

同一 LOD 方案在 1080p 手机、4K PC 和 VR 双眼中产生的屏幕误差不同。最终阈值应成为平台质量档配置，而不是只存在于 DCC 导出预设。

## 带滞回的 LOD 选择

以下C++宿主片段输入有限非负screenFraction，阈值严格降序，长度M表示M+1个LOD；currentLod位于[0,M]，hysteresis非负且小于最小阈值。滞回让进入和退出使用不同边界：

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

例如阈值0.20、滞回0.02，从LOD0下降要低于0.18，从LOD1返回要高于0.22。0.19与0.21都保持当前层。相机瞬移可一次跨越多个阈值，因此使用循环而非单次判断。阈值单位必须与screenFraction一致。滞回区间过大，会让对象长时间停留在不合适的 LOD；没有滞回时，相机在阈值附近抖动会造成频繁切换。验证应记录每秒 LOD 切换次数，并用缓慢往返相机检查进入与退出边界。

## 验证方法

固定FOV与分辨率往返经过阈值，记录切换次数、轮廓差和双绘制成本。远景法线、Alpha覆盖与材质mip同时检查；流送未完成时回退已驻留层。

CPU参考`select_lod`覆盖滞回双向边界与跨多级跳变，见 [reference.py](../examples/revision_06_08/reference.py)，运行 `python -B 知识库/examples/revision_06_08/test_reference.py`。C++片段未独立编译，真实LOD画面、资源流送与交叉淡化成本为UNVERIFIED。

## 相关主题

- [[08_几何与网格/网格数据与GPU访问]]
- [[26_GPU驱动与虚拟几何/Nanite几何选择与流送]]
- [[08_几何与网格/Heightfield地形]]
- [[15_资产与工具管线/程序化资产生成]]
- [[08_几何与网格/植被包裹法线]]
- [[15_资产与工具管线/WFC]]

## 参考资料

- [Unity 6.0，LOD Group](https://docs.unity3d.com/6000.0/Documentation/Manual/class-LODGroup.html)：2026-10-22核读LOD Group selection bar与Transitioning between LOD levels，屏幕高度比例和双层绘制。
- 本文投影比例由透视投影推导，滞回模型由CPU边界例验证；简化误差来源见[[08_几何与网格/网格数据与GPU访问]]。
