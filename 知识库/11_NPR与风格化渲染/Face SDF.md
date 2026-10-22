# Face SDF

鼻翼和眼窝的真实阴影很细碎，原画却常用一块连续暗面。Face SDF 把设计好的明暗边界存成可比较的灰度场，头部局部光方向决定阈值。灰度值的含义、左右通道与头部坐标对齐，明暗才会随转头连续。

## 灰度场与角度契约

这里的 SDF 是风格化材质中的习惯叫法。严格的有符号距离场保存到边界的距离，单位可以是纹素或长度；本页模型保存每个纹素的熄灭角度，数值在 0 到 1 之间，不宣称是空间距离。它适合用单个阈值扫出一族连续边界。

设头部局部 X 轴向右，Y 轴向上，Z 轴向前。光方向从表面指向光源，头部变换仅保留旋转。将光投影到局部 XZ 平面，以正面为 0、背面为 1：

$$t=\frac{|\operatorname{atan2}(L_x,L_z)|}{\pi}$$

贴图 R 通道表示从左侧转到背面的一族边界，G 通道表示从右侧转到背面的一族边界。通道值 $d$ 表示该纹素保持亮面的最大归一化角度：$d>t$ 为亮，$d<t$ 为暗。例如 $d=0.7$ 的面颊在侧光 $t=0.5$ 时仍亮，到偏背光 $t=0.8$ 时变暗。这给美术绘制和运行时比较提供了同一判据。

这种编码要求某一侧旋转过程中每个纹素只跨越边界一次。若鼻侧需要先亮、再暗、又变亮，单通道单阈值不能表达，需要分角度贴图或额外遮罩。编码能力由数据模型决定，增加纹理分辨率不能解决这个限制。

## 方向求值与边界过滤

下面是像素阶段 HLSL 机制片段。`worldToHeadRotation` 为无缩放的逆旋转矩阵；纹理按线性数据采样，关闭 sRGB。R/G 两个通道遵守上述左右契约，`verticalThreshold` 是光线接近头顶时使用的艺术参数。

```hlsl
float3 lightHead = mul(worldToHeadRotation, lightDirWS);
float2 horizontal = lightHead.xz;
float angleThreshold = verticalThreshold;
if (dot(horizontal, horizontal) > 1e-8)
    angleThreshold = abs(atan2(horizontal.x, horizontal.y)) / 3.14159265;
float sdf = lightHead.x < 0.0 ? faceSdf.r : faceSdf.g;
float width = max(max(fwidth(sdf - angleThreshold), userSoftness), 1e-5);
float faceLit = smoothstep(angleThreshold - width,
                          angleThreshold + width, sdf);
```

水平分量为零时不存在左右角度，因此不能靠归一化得到答案。固定阈值可让静态模型有确定输出，动画中则可在接近竖直的区域平滑过渡到这个阈值。直接保存上一帧方向还会引入历史状态，多个相机需要各自管理，不能把偶然残留的数据当作方向。

两通道在正前与正后方向交接。如果端点的明暗不同，通道选择一变，鼻梁就会跳色；制作时应约束两端结果一致。镜像角色也必须同步处理局部轴与左右贴图。只有纹理明确编码了对称关系时，才可用 `1-u` 代替双通道。

`fwidth` 把阈值差在像素内的变化转成软边宽度，减少细边闪烁。贴图压缩会改变阈值场，mip 平均也会移动边界，所以近景、远景和动态分辨率都需检查。增加 UV 岛的边缘扩展宽度可以防止 UV 岛外的无关值渗入，无法修复错误的颜色空间或阈值方向。

## 艺术分区与实际遮挡

Face SDF 决定脸部设计明暗，法线仍可参与面颊的柔和层次，AO 保存眼窝等局部遮蔽。头发和外部物体的投影由真实可见性提供。将这些量都命名为“阴影”再反复相乘，会把暗面压黑，失去原画的色彩。

可以先由 `faceLit` 在设计的亮色和暗色间插值，再由角色阴影可见性调整直接光层。固定 AO 放在哪一层属于材质规则，需用各层单独显示来确认。编辑面部法线时保留鼻翼和眼窝的必要结构，并检查它与法线贴图组合后的方向。

## 验证与证据

固定头部，使主光绕局部 Y 轴旋转，依次显示局部光方向、阈值、通道和亮区。正面、侧面、背面的阈值应为 0、0.5、1；头部与光一起旋转时结果应保持一致，因为局部方向没变。再测试镜像、非均匀对象缩放和竖直来光，确认它们各自遵守输入契约。

2026-10-22 执行 [CPU参考测试](../examples/revision_09_15/test_reference.py)通过，两项检查覆盖角度阈值和竖直回退。该实验验证本页定义的艺术模型，不代表某个商业游戏的内部实现。[编译检查](../examples/revision_09_15/verify.py)已用 DXC 将方向求值片段编译为 `ps_6_0`。贴图资产效果、引擎运行和 GPU 性能尚未执行。

## 相关主题

- [[11_NPR与风格化渲染/NPR材质与分层光照]]
- [[11_NPR与风格化渲染/角色阴影]]
- [[01_数学与采样/空间变换]]

## 参考资料

- 本仓库 [reference.py](../examples/revision_09_15/reference.py) 的 `face_threshold` 与 `test_reference.py`：角度场模型、端点与退化输入的可复现实验。贴图契约是本文明确设计的示例。
- Microsoft，[fwidth](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-fwidth)：屏幕导数定义；API 说明支持过滤操作，不支持特定角色的美术设计。
