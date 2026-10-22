# 屏幕空间AO

接触处需要更暗，但深度缓冲只有当前视图最前层。SSAO从这份局部信息采样周围遮挡，再过滤估计值。它能补接触层次，也会在屏幕外和深度断层失去信息，不能当作完整GI。

## Screen-space Ambient Occlusion

SSAO 从深度和法线估计当前点周围是否被几何遮挡。它只看屏幕可见表面，因此存在：

- 屏幕边缘缺失；
- 深度不连续 Halo；
- 远处物体在屏幕邻域造成错误遮挡；
- 噪声和时域拖影。

AO 应主要影响间接光。直接把它乘到所有光照会让有主光的区域也被错误压黑。

HBAO/GTAO 等方法改进方向包括 Horizon Search、法线余弦权重、距离衰减和更接近参考积分的近似。

### SSAO 的采样数据流

最小 SSAO 通常在观察空间工作。每个像素读取位置和法线，用一张小 Noise Texture 随机旋转半球 Kernel，再把样本点投影回屏幕，与深度缓冲中的表面比较。

```hlsl
float ComputeSSAO(float2 uv, float3 positionVS, float3 normalVS)
{
    float3 N=normalize(normalVS);
    float3 randomDir=NoiseTexture.SampleLevel(NoiseSampler,uv*NoiseScale,0).xyz*2.0-1.0;
    float3 T=randomDir-N*dot(randomDir,N);
    if (dot(T,T)<1e-6) {
        float3 axis=abs(N.z)<0.9 ? float3(0,0,1) : float3(0,1,0);
        T=cross(axis,N);
    }
    T=normalize(T);
    float3 B=cross(N,T);
    float3x3 tbn=float3x3(T,B,N);
    float occlusion=0.0;
    for (uint i=0; i<KernelSize; ++i) {
        float3 sampleVS=positionVS+mul(Kernel[i],tbn)*Radius;
        float4 clip=mul(Projection,float4(sampleVS,1.0));
        if (clip.w<=0.0 || clip.z<0.0 || clip.z>clip.w) continue;
        float2 sampleUV=clip.xy/clip.w*float2(0.5,-0.5)+0.5;
        if (any(sampleUV<0.0) || any(sampleUV>1.0)) continue;
        float4 scene=PositionTexture.SampleLevel(PointSampler,sampleUV,0);
        if (scene.w<0.5) continue;
        float range=smoothstep(0.0,1.0,Radius/max(abs(positionVS.z-scene.z),Radius*1e-4));
        occlusion+=(scene.z>=sampleVS.z+Bias ? 1.0 : 0.0)*range;
    }
    return 1.0-occlusion/KernelSize;
}
```

这是HLSL机制函数：观察空间相机前方为负Z，投影裁剪深度为0到w，纹理UV原点在左上。`PositionTexture` 为线性浮点RGBA，XYZ保存观察位置、W为几何有效标记；背景清W为0。`NoiseTexture` 保存映射到0—1的随机方向，用重复点采样；位置纹理用点采样。宿主保证 `1<=KernelSize<=64`、`Radius>0`、`Bias>=0`、有限非零法线和局部单位半球内样本，即Kernel的Z非负、长度不超过1。实际管线也可从深度重建位置，比较关系须随空间约定同步。

Kernel 样本靠近原点时更密，能保留接触阴影；Noise Texture 只负责旋转采样方向，后续需要空间或时域滤波消除噪声。Radius与Bias使用观察空间长度。距离分母的数值下限取Radius的固定比例，因此换长度单位时位置、Radius与Bias共同缩放，权重保持不变。相机前方Z为负时，`scene.z`越大表示越靠近相机；所以 `scene.z>=sampleVS.z+Bias` 表示真实表面在样本前方，样本可能被遮挡。距离权重抑制与中心深度相差过远的表面，但仍不能恢复屏幕未保存的几何。

本例越屏、背景和裁剪外样本的贡献为零，分母仍是总KernelSize，相当于把缺失方向当作未遮挡，会使屏幕边缘偏亮。改为只除有效样本数会改变这种偏差，也可能放大边界噪声；两种策略都不能凭单层深度得到真实缺失遮挡。

例如中心位置z=-5，某半球样本投影后的z=-4.8，Bias=0.05。深度读取表面z=-4.7时，`-4.7>=-4.8+0.05`成立，该样本贡献遮挡；读取z=-5时不成立。若4个等权方向中仅这一个被挡，且距离权重为1，最终可见值为0.75。改成z=-1的前景虽然仍满足比较，但与中心相差4米，半径0.5米时距离权重显著衰减，避免把很远的前景当局部凹陷。

平面正上方的样本正常位于平面之前，读取平面z=-5不应遮挡它；若测试平面仍整片发黑，先检查空间符号、基底法线和Bias单位，而不是提高模糊强度。

## 边界过滤与合成

随机旋转把条带变成噪声，普通模糊又会把前景AO带到背景。双边过滤可将空间核乘以 $\exp(-|z_s-z_c|/\sigma_z)$ 与 $\max(N_s\cdot N_c,0)^p$，再按有效权重和归一化。深度与 $\sigma_z$ 单位一致，法线必须处于同一空间；权重和为零时保留中心。时域累积还需运动重投影、深度和法线拒绝，详见 [[02_GPU与光栅化管线/抗锯齿与时域重建]]。

输出的1代表环境可见、0代表遮蔽。合成时先定位间接漫反射项，避免重复乘烘焙AO或把直接光和自发光同时压黑；间接镜面遮挡需要考虑反射方向和粗糙度，不能默认等同此标量。

## 验证方法

显示原AO、滤波结果与半径，测试平面应基本无自遮挡。屏幕边缘、薄墙与远近深度断层分别检查；采样点出屏或在相机后时拒绝，随机向量平行法线时用稳定基底。AO合成明确作用于间接项。

[test_post.py](../examples/revision/test_post.py) 检查右手观察空间比较方向、距离衰减和全部长度同比缩放的权重不变性，正文函数通过DXC编译。深度采集、GPU噪声与过滤画面尚未运行。

## 相关主题

- [[02_GPU与光栅化管线/深度缓冲与位置重建]]
- [[05_光照阴影与GI/动态GI]]
- [[07_颜色与后处理/Tone Mapping]]
- [[07_颜色与后处理/Bloom]]
- [[07_颜色与后处理/景深与运动模糊]]

## 参考资料

- [LearnOpenGL 作者示例：9.ssao.fs](https://raw.githubusercontent.com/JoeyDeVries/LearnOpenGL/master/src/5.advanced_lighting/9.ssao/9.ssao.fs)，半球样本、观察空间比较和距离权重；本文另显式处理裁剪、纹理原点和退化基底。
- [[02_GPU与光栅化管线/深度缓冲与位置重建]]：深度资源与空间恢复的主归属。
