# Billboard

面片已经面向相机，角色却像绕中心悬在地面上，说明朝向算对了，锚点还没有对齐。Billboard用相机方向构造面片位置，接地点、阴影和深度仍属于场景。先固定脚底，再转动上面的面片，就能把显示朝向与世界位置联系起来。

## 朝向与坐标架

### 球面与轴约束

球面Billboard使用相机Right和Up构造面片，中心为`c`，局部顶点为`(x,y)`：

$$\mathbf p=\mathbf c+x\mathbf r+y\mathbf u$$

轴约束Billboard保持世界Up，只绕这个轴转向相机，适合树木和站立角色。相机方向投影到水平面后归一化，再用叉积得到Right。相机几乎在正上方时投影趋近零，需要稳定的备用方向，避免坐标架突然翻转。

下面是HLSL机制片段，`anchorWS`为脚底，`localX`为左右距离，`localY`为向上距离；输入相机位置和单位Up都在世界空间。`fallbackRightWS`来自稳定对象朝向。

```hlsl
float3 towardCamera = cameraPositionWS - anchorWS;
float3 forward = towardCamera - upWS * dot(towardCamera, upWS);
float3 right = fallbackRightWS;
if (dot(forward, forward) > 1e-8)
    right = normalize(cross(upWS, normalize(forward)));
float3 positionWS = anchorWS + localX * right + localY * upWS;
```

此片段未接入引擎运行。Right的符号、顶点顺序和纹理方向要共同验证：面片背面被剔除或左右镜像时，检查叉积顺序和三角形绕序。

### 在哪个阶段生成

少量面片可由CPU构造，大量实例可在顶点Shader中用共享四边形与实例数据生成。几何Shader也能把点扩张为面片，但平台支持与输出成本需按设备判断。实例化的关键是共享几何和材质，同时传入每个锚点、尺度和相位。

## 锚点与场景深度

### 脚底保持固定

角色用脚底作为锚点，面片只在锚点上方展开。排序、接地、阴影、雾和交互使用同一世界位置，面片中心由脚底加高度偏移得到。中心Pivot转动时容易产生悬浮感，脚底锚点能稳定地面联系。

假视差可按高度和视向偏移UV，脚底区域的高度权重接近零。偏移过大会采到轮廓外区域，需要Padding或分层面片。采样偏移改变画面内容，真实深度若仍是平面，就会留下遮挡不一致。

### 多视角Impostor

植被远景可烘焙多个方向的颜色、法线和深度。运行时根据相机方位选择邻近视角，必要时重建视差与像素深度。颜色混合与深度重建要使用同一视角权重，避免颜色属于一个角度而深度属于另一个角度。

Mesh切换到Impostor时，检查Bounds、树高、锚点、曝光、法线、Alpha覆盖、阴影和风相位。蒙皮和复杂几何不能只靠一张正面图恢复，烘焙覆盖与运行表现需要匹配。

## 验证与代价

绕对象水平和垂直旋转相机，检查正上方退化、绕序、脚底、背面和镜像。用前后遮挡物检查深度；切换LOD时分别看轮廓、曝光与阴影。粒子和植被同时使用时，确认相机依赖的数据逐视图生成。

Billboard减少几何，代价可能转移到透明覆盖、排序与纹理采样。统计屏幕覆盖与采样次数，并对照Mesh路径的实际顶点、Draw和GPU耗时。

## 相关主题

- [[11_NPR与风格化渲染/NPR与场景风格导读]]
- [[09_动画系统/植被风动]]
- [[02_GPU与光栅化管线/Geometry Shader]]、[[02_GPU与光栅化管线/Stream Output]]
- [[10_VFX与模拟/GPU粒子系统]]
- [[02_GPU与光栅化管线/透明合成]]

示例状态：本页代码用于解释对应的数据和调用约束，完整资源创建、类型与调用环境由项目提供。除文中另列的实际实验外，本页未执行目标引擎编译、GPU捕获或性能计时。

## 参考资料

- Microsoft Learn，[Geometry Shader Stage](https://learn.microsoft.com/en-us/windows/win32/direct3d11/geometry-shader-stage)：点和图元输入、可变输出模型。
- Epic Games，[Impostor Baker](https://dev.epicgames.com/documentation/en-us/unreal-engine/impostor-baker-plugin-in-unreal-engine)：多方向表示与烘焙；具体插件功能按目标版本核对。
- 本仓库几何Shader专题的Billboard示例，作为坐标架与阶段应用说明。
