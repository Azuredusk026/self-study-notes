# Cubemap环境采样

六张图片已经摆好，反射方向一转却出现接缝，可能是面朝向、手性或跨面mip不一致。Cubemap把三维方向映射到六面坐标，天空绘制与反射查询共享这份方向契约，粗糙响应则交给IBL。

## 六面方向与采样地址

Cubemap 用三维方向查找六个二维面。采样坐标不是普通 UV，而是从立方体中心指向目标方向的向量。硬件根据绝对值最大的分量选择面，再计算面内坐标。例如方向 `(2,0,-1)` 命中正 X 面；按 OpenGL 面朝向，其面内横坐标来自 `-z/abs(x)=0.5`，映射到 $[0,1]$ 后为 0.75，纵坐标为 0.5。方向整体乘任意正数不改变查询位置，零向量则没有有效方向。

六个面的朝向、坐标手性和纹理原点必须一致。接缝常来自：

- 面顺序或旋转错误；
- 边缘 Texel 没有连续过滤；
- 各面曝光和颜色处理不同；
- Mip 生成时没有跨面处理；
- 方向在错误空间中计算。

## 天空绘制

Skybox 常使用一个以相机为中心的立方体。View Matrix 保留旋转、去掉平移，让背景看起来位于无限远。下面的 GLSL 写法让输出深度位于远平面；这里约定 OpenGL 常规深度、清除值 1、深度比较 `LEQUAL`，关闭深度写入并在不透明物体之后绘制。立方体从内部观察，剔除状态需要保留内侧面。以下 GLSL 机制片段由宿主提供 `mat4 view`、`mat4 projection` 与线性 HDR `samplerCube environmentMap`：

```glsl
vec4 SkyboxPosition(vec3 cubePosition)
{
    mat4 viewRotation = mat4(mat3(view));
    vec4 clip = projection * viewRotation
              * vec4(cubePosition, 1.0);
    return clip.xyww;
}

vec3 SampleSkybox(vec3 directionWS)
{
    return texture(environmentMap, normalize(directionWS)).rgb;
}
```

`clip.xyww` 让透视除法后的 Z 等于 1。反向 Z 管线的深度值和比较函数不同，需要使用引擎提供的 Skybox 深度约定。

## 反射与折射

环境反射使用反射方向查询 Cubemap：

$$
\mathbf R=reflect(-\mathbf V,\mathbf N)
$$

$\mathbf V$ 和 $\mathbf N$ 必须处于 Cubemap 期望的同一空间。直接采样清晰环境只适合理想镜面；粗糙材质需要按 BRDF 预过滤后的环境 Mip。

透明介质的理想折射方向可以用 `refract` 计算。输入的 $\eta$ 是入射介质折射率与透射介质折射率之比：

```glsl
vec3 incidentWS = normalize(positionWS - cameraPositionWS);
float eta = etaIncident / etaTransmitted;
vec3 interfaceNormal = normalize(normalWS); // 指向入射介质一侧
vec3 refractedWS = refract(incidentWS, interfaceNormal, eta);
vec3 sampleDirection = dot(refractedWS, refractedWS) > 0.0
    ? refractedWS : reflect(incidentWS, interfaceNormal);
vec3 environment = texture(environmentMap, sampleDirection).rgb;
```

输入法线应朝入射介质一侧。光从空气进入玻璃与从玻璃离开时，需要交换两个折射率并相应翻转法线。依据 Snell 定律，根号内的 $k=1-\eta^2[1-(N\cdot I)^2]$ 小于零时无实数透射方向；当发生全反射时，`refract` 返回零向量，Shader 应改用反射方向。这个环境采样只近似无限远背景，不包含物体厚度、吸收、局部遮挡和折射后的场景深度。

## 动态捕获与发布

动态环境捕获会从 Probe 位置覆盖 Cubemap 的六个面。实现可以提交六个视图，也可以使用分层渲染一次写入多个面；完整更新还要生成 Mip 或重新预过滤。分帧捕获会使六个面代表不同时间；可用前后台 Cubemap，在六面及其预过滤全部完成后整体发布，换取额外内存与更新延迟。常见调度方式是分面、分帧或按重要性更新，捕获宿主的可见表面若会把自身近处外壳录进环境，需要按用途排除对应渲染体；Probe 组件本身没有可绘制表面。验证时在 Probe 六面放置方向标记，检查接缝、手性、更新延迟和递归捕获。

## 验证方法

六面放置正负轴标签，用已知方向查询。检查天空去掉观察平移、深度比较及反向Z，逐级显示mip接缝。折射零向量表示全反射时回退到反射。

天空与折射片段在 [编译检查](../examples/revision/compile_lighting.py) 中补齐 GLSL 入口和资源声明，完成离线链接。六面实际上传、过滤接缝和动态捕获仍需在目标引擎运行检查。

## 相关主题

- [[04_光照模型与PBR/IBL]]
- [[01_数学与采样/空间变换]]
- [[04_光照模型与PBR/法线贴图]]

## 参考资料

- [Khronos GLSL：refract](https://raw.githubusercontent.com/KhronosGroup/OpenGL-Refpages/main/gl4/refract.xml)，输入归一化、折射率比与全反射零向量。
- [Filament：Cubemaps coordinates system](https://google.github.io/filament/main/filament.html#imagingpipeline/coordinatessystems/cubemapscoordinatessystem)，说明环境方向与工具预处理必须共同定义；Filament 的镜像存储属于该工具链约定。
- [LearnOpenGL 作者示例：Cubemaps skybox](https://github.com/JoeyDeVries/LearnOpenGL/tree/master/src/4.advanced_opengl/6.1.cubemaps_skybox)，用于检查天空顶点深度和绘制状态。
