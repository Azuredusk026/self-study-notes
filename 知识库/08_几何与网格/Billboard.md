# Billboard

面片已经面向相机，角色却像绕中心悬在地面上，说明朝向算对了，锚点还没有对齐。Billboard用相机方向构造面片位置，接地点、阴影和深度仍属于场景。先固定脚底，再转动上面的面片，就能把显示朝向与世界位置联系起来。

## 朝向与坐标架

### 球面与轴约束

屏幕对齐Billboard使用相机Right和Up构造面片，中心为`c`，局部顶点为`(x,y)`：

$$\mathbf p=\mathbf c+x\mathbf r+y\mathbf u$$

若要求每张面片的法线指向相机位置，需要分别用相机到锚点的方向重建坐标架；透视画面边缘处，它与共用相机Right/Up的屏幕对齐方案不同。轴约束Billboard保持世界Up，只绕这个轴转向相机，适合树木和站立角色。相机方向投影到水平面后归一化，再用叉积得到Right。相机几乎在正上方时投影趋近零，需要稳定的备用方向，避免坐标架突然翻转。

下面是HLSL机制片段，`anchorWS`为脚底，`localX`为左右距离，`localY`为向上距离；输入相机位置和单位Up都在世界空间。`fallbackRightWS`来自稳定对象朝向，要求其在Up垂直平面的投影非零。代码将它投影并归一化，以免备用方向带有竖直分量而拉斜面片。所有位置和localX/localY使用同一世界长度单位。

```hlsl
float3 towardCamera = cameraPositionWS - anchorWS;
float3 forward = towardCamera - upWS * dot(towardCamera, upWS);
float3 right = normalize(fallbackRightWS - upWS * dot(fallbackRightWS, upWS));
if (dot(forward, forward) > 1e-8)
    right = normalize(cross(upWS, normalize(forward)));
float3 positionWS = anchorWS + localX * right + localY * upWS;
```

固定备用方向只避免零向量归一化，不能保证跨越正上方时朝向连续。投影方位在顶点上方本来就不唯一；若需要连续，可在一段退化角度区间保持上一有效朝向，并用进入、退出两条阈值避免反复切换。这个状态需要逐对象、逐视图保存。

此片段未接入引擎运行。Right的符号、顶点顺序和纹理方向要共同验证：面片背面被剔除或左右镜像时，检查叉积顺序和三角形绕序。

### 生成阶段

少量面片可由CPU构造，大量实例可在顶点Shader中用共享四边形与实例数据生成。几何Shader也能把点扩张为面片，但平台支持与输出成本需按设备判断。实例化的关键是共享几何和材质，同时传入每个锚点、尺度和相位。

## 锚点与场景深度

### 脚底保持固定

角色用脚底作为锚点，面片只在锚点上方展开。排序、接地、阴影、雾和交互使用同一世界位置，面片中心由脚底加高度偏移得到。中心Pivot转动时容易产生悬浮感，脚底锚点能稳定地面联系。

假视差可按高度和视向偏移UV，脚底区域的高度权重接近零。偏移过大会采到轮廓外区域，需要Padding或分层面片。采样偏移改变画面内容，真实深度若仍是平面，就会留下遮挡不一致。

### 多视角Impostor

植被远景可烘焙多个方向的颜色、法线和深度。运行时根据相机方位选择邻近视角，必要时重建视差与像素深度。颜色混合与深度重建要使用同一视角权重，避免颜色属于一个角度而深度属于另一个角度。

Mesh切换到Impostor时，检查Bounds、树高、锚点、曝光、法线、Alpha覆盖、阴影和风相位。蒙皮和复杂几何不能只靠一张正面图恢复，烘焙覆盖与运行表现需要匹配。

### 离散视角的选择

若只覆盖水平环，烘焙8个等间距方位，间隔45°。当前相对物体方位60°对应连续索引60/45=1.333，取视图1和2，权重为2/3与1/3；接近360°时后一索引按8取模回到0。相机方位必须先减去对象旋转，才能选择物体局部视角。

颜色直接混合会在轮廓不同处出现双影，因为两张图的同一UV未必代表同一表面。深度视差方案需要按各烘焙相机的逆投影恢复表面位置，转换到当前视角，再确定有效覆盖与深度。只平均两张深度数值不能补出这种对应关系；没有深度重建时应把它视为颜色交叉淡化，并接受轮廓误差。

## 验证与代价

绕对象水平和垂直旋转相机，检查正上方退化、绕序、脚底、背面和镜像。用前后遮挡物检查深度；切换LOD时分别看轮廓、曝光与阴影。粒子和植被同时使用时，确认相机依赖的数据逐视图生成。

Billboard减少几何，代价可能转移到透明覆盖、排序与纹理采样。统计屏幕覆盖与采样次数，并对照Mesh路径的实际顶点、Draw和GPU耗时。

## 相关主题

- [[11_NPR与风格化渲染/NPR与场景风格导读]]
- [[09_动画系统/植被风动]]
- [[02_GPU与光栅化管线/Geometry Shader]]、[[02_GPU与光栅化管线/Stream Output]]
- [[10_VFX与模拟/GPU粒子系统]]
- [[02_GPU与光栅化管线/透明合成]]

CPU参考`billboard_right`检查正常相机方向和正上方退化输入，备用方向投影后与Up正交，见 [reference.py](../examples/revision_06_08/reference.py)。运行 `python -B 知识库/examples/revision_06_08/test_reference.py`。HLSL为宿主机制片段；Impostor烘焙、多视图、阴影与GPU画面为UNVERIFIED。

## 参考资料

- [Microsoft，Geometry Shader Stage](https://learn.microsoft.com/en-us/windows/win32/direct3d11/geometry-shader-stage)：点与图元输入、可变输出模型。
- [Epic，Impostor Baker，UE5.6](https://dev.epicgames.com/documentation/en-us/unreal-engine/impostor-baker-plugin-in-unreal-engine?application_version=5.6)：多方向表示与烘焙；坐标架公式由本文正交投影及叉积推导，未执行插件。
