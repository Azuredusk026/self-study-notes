# Face SDF

鼻翼和眼窝的真实阴影很细碎，原画却常用一块连续暗面。Face SDF把设计好的边界存成可比较灰度场，头部局部光方向决定阈值。坐标、左右通道与烘焙约定对齐，明暗才会随转头连续。

## 面部明暗

### 面部为什么难

人脸几何有鼻翼、眼窝、嘴角等高频曲率。真实光照会产生细碎阴影，而二维原画常只保留一块连续的脸部暗面。

常用组合：

- 编辑过的 Face Normal；
- Face SDF 控制大阴影边界；
- AO/Mask 固定眼窝、鼻底等细节；
- Ramp 控制亮暗颜色；
- 实时 Shadow Map 处理头发投影和外部遮挡。

这些数据解决不同问题，不应互相替代。

### Face SDF的含义

Face SDF 通常把一组预设计脸部阴影边界编码到 UV Texture。它不一定是真正以世界单位保存的严格 Signed Distance；很多项目保存的是可阈值比较的灰度场。

运行时把主光方向变到 Head Local Space。只考虑脸部水平平面上的方向，得到光从左或右照入的角度，再用该角度选择阈值：

$$
\mathbf{l}_h=\operatorname{normalize}(M_{world\rightarrow head}\mathbf{L})
$$

$$
a=\frac{\operatorname{atan2}(l_{h,x},l_{h,z})}{\pi}
$$

具体 Forward Axis、符号、UV 左右和阈值映射取决于项目约定。不能复制公式后假设方向自动正确。

### 左右脸与翻转

很多 Face SDF 只烘焙半边或在一张纹理中编码左右两组边界。运行时根据 $l_{h,x}$ 选择原 UV 或镜像 UV。

必须验证：

- 模型 Head Forward 是 +Z 还是其他轴；
- Directional Light 变量表示“光传播方向”还是“指向光源”；
- UV 原点与左右镜像方式；
- 贴图灰度是“距离亮区”还是“距离暗区”；
- 光从正前/正后时如何退化。

最简单的校验是固定头部，绕 Y 轴旋转一圈主光，并输出光方向、采样值和最终阈值。

### SDF阈值与软边

如果采样值为 $d$、角度映射阈值为 $t$，可使用：

$$
w=\operatorname{smoothstep}(t-\epsilon,t+\epsilon,d)
$$

$w$ 在亮暗层间插值。$\epsilon$ 可结合 `fwidth(d-t)` 做屏幕空间抗锯齿。

SDF 贴图需要足够 Padding 和合适压缩。强有损压缩会让平滑距离场出现块状边界。Mipmap 则可能改变阈值，需要在不同距离检查。

## Face SDF 阈值

输入 SDF 使用脸部 UV，左右方向分别存于两个通道。光照方向先变换到头部局部空间，再用水平分量决定通道和阈值：

```hlsl
float3 lightHead = normalize(mul(worldToHead, float4(lightDirWS, 0)).xyz);
float side = step(0.0, lightHead.x);
float sdf = lerp(faceSdf.r, faceSdf.g, side);
float threshold = lightHead.z * 0.5 + 0.5;
float softness = max(fwidth(sdf - threshold), userSoftness);
float faceLit = smoothstep(threshold - softness,
                           threshold + softness, sdf);
```

通道、头部前向轴和光方向正负必须与烘焙约定一致。SDF 负责艺术化明暗分界，角色仍可叠加 Shadow Map 处理场景遮挡。让方向光绕头部旋转一周，阴影应连续跨过鼻梁；左右跳变通常来自通道选择或局部轴错误。

## 面部法线的配合

Face Normal 常经过传递或手工编辑，让面颊形成更完整的明暗面。修改后必须保留眼窝、鼻翼等必要结构，并检查与 Normal Map 的叠加。

## 验证方法

固定头部让主光绕水平轴一圈，显示局部方向、通道选择与阈值。检查镜像角色、轴向和mip，Face SDF控制艺术分区，外部遮挡由角色阴影处理。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[11_NPR与风格化渲染/NPR材质与分层光照]]
- [[11_NPR与风格化渲染/角色阴影]]
- [[11_NPR与风格化渲染/风格化头发高光]]
- [[11_NPR与风格化渲染/风格化眼睛]]

## 参考资料

- Kajiya and Kay, *Rendering Fur with Three Dimensional Textures*.
- Marschner et al., *Light Scattering from Human Hair Fibers*.
- Arc System Works and miHoYo technical presentations on anime character rendering.
