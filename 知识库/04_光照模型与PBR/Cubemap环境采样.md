# Cubemap环境采样

六张图片已经摆好，反射方向一转却出现接缝，可能是面朝向、手性或跨面mip不一致。Cubemap把三维方向映射到六面坐标，天空绘制与反射查询共享这份方向契约，粗糙响应则交给IBL。

## Cubemap、Skybox 与环境映射

Cubemap 用三维方向查找六个二维面。采样坐标不是普通 UV，而是从立方体中心指向目标方向的向量。硬件根据绝对值最大的分量选择面，再计算面内坐标。

六个面的朝向、坐标手性和纹理原点必须一致。接缝常来自：

- 面顺序或旋转错误；
- 边缘 Texel 没有连续过滤；
- 各面曝光和颜色处理不同；
- Mip 生成时没有跨面处理；
- 方向在错误空间中计算。

Skybox 常使用一个以相机为中心的立方体。View Matrix 保留旋转、去掉平移，让背景看起来位于无限远。下面的 GLSL 写法让输出深度位于远平面；深度测试使用 `LEQUAL`，并在不透明物体之后绘制：

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

环境反射使用反射方向查询 Cubemap：

$$
\mathbf R=reflect(-\mathbf V,\mathbf N)
$$

$\mathbf V$ 和 $\mathbf N$ 必须处于 Cubemap 期望的同一空间。直接采样清晰环境只适合理想镜面；粗糙材质需要按 BRDF 预过滤后的环境 Mip。

透明介质的理想折射方向可以用 `refract` 计算。输入的 $\eta$ 是入射介质折射率与透射介质折射率之比：

```glsl
vec3 incidentWS = normalize(positionWS - cameraPositionWS);
float eta = etaIncident / etaTransmitted;
vec3 refractedWS = refract(incidentWS, normalize(normalWS), eta);
vec3 environment = texture(environmentMap, refractedWS).rgb;
```

当发生全反射时，`refract` 返回零向量，Shader 应改用反射方向。这个环境采样只近似无限远背景，不包含物体厚度、吸收、局部遮挡和折射后的场景深度。

动态环境捕获会从 Probe 位置覆盖 Cubemap 的六个面。实现可以提交六个视图，也可以使用分层渲染一次写入多个面；完整更新还要生成 Mip 或重新预过滤。常见调度方式是分面、分帧或按重要性更新，并从捕获列表中排除 Probe 自己。验证时在 Probe 六面放置方向标记，检查接缝、手性、更新延迟和递归捕获。

## 验证方法

六面放置正负轴标签，用已知方向查询。检查天空去掉观察平移、深度比较及反向Z，逐级显示mip接缝。折射零向量表示全反射时回退到反射。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[04_光照模型与PBR/IBL]]
- [[01_数学与采样/空间变换]]
- [[04_光照模型与PBR/法线贴图]]

## 参考资料

- Mikkelsen, *MikkTSpace*.
- Brian Karis, *Real Shading in Unreal Engine 4*.
- Colin Barré-Brisebois and Stephen Hill, *Blending in Detail*.
- LearnOpenGL, `src/5.advanced_lighting/4.normal_mapping`.
- LearnOpenGL, `src/4.advanced_opengl/6.1.cubemaps_skybox` and `6.2.cubemaps_environment_mapping`.
