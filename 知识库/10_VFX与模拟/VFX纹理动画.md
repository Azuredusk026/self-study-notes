# VFX纹理动画

同一张纹理可以逐帧换图，也可以沿流向连续移动。VFX纹理动画先选择时间参数怎样映射到采样坐标，再处理周期接缝、帧间插值和mip。两种表示都要保持动画尺度与资产布局一致。

## Flipbook

Flipbook 把多帧烟、火或爆炸打包进一张 Atlas。给定列数 $C$、行数 $R$ 和帧索引 $f$：

$$
x=f\bmod C,\qquad y=\lfloor f/C\rfloor
$$

局部 UV 缩放到单格后加上 $(x/C,y/R)$ Offset。需要确认贴图原点方向，否则帧序会上下颠倒。

帧间直接切换会抖动。Frame Blending 同时采样相邻两帧并插值，运动更平滑，但纹理采样翻倍，也可能产生重影。

Atlas 每格需要 Padding。Mipmap 和 Bilinear Filter 会跨格采到相邻帧，产生边缘串色。可以扩边、使用专用 Mip，或在 Shader 中收紧单格 UV。

## Polar UV、Flow 与噪声

圆形冲击波可把中心化 UV 转为极坐标：半径控制环形推进，角度控制沿圆周的纹理采样。

Flow Map 用 RG 表示二维流向，按时间偏移 UV。单次滚动在周期重置时会跳变；常用两组相差半周期的采样，再用三角权重交叉淡入淡出。

噪声不要无目的叠加。区分用途：

- 大尺度噪声改变整体轮廓；
- 中尺度噪声控制密度和卷动；
- 小尺度噪声补表面细节；
- 时间 Offset 控制运动速度。

多层噪声会增加采样和 Alias，应为远距离准备简化版本。

## 双相流动

伪代码输入UV、二维流向和时间，两个相位用周期权重交叉淡化，避免单次回绕跳变。

```text
phase0 = frac(time)
phase1 = frac(time+0.5)
c0 = Sample(uv-flow*phase0)
c1 = Sample(uv-flow*phase1)
color = BlendWithComplementaryTriangleWeights(c0,c1,phase0)
```

## 验证方法

固定时间检查Atlas帧索引与原点，跨周期观察连续性。移动镜头检查mip串色与UV缝，Flow速度单位、纹理重复和Mask是否跟随预期空间分别核对。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[06_纹理技术/纹理图集]]
- [[01_数学与采样/程序噪声]]
- [[10_VFX与模拟/溶解材质]]
- [[10_VFX与模拟/屏幕扰动]]
- [[10_VFX与模拟/软粒子]]
- [[14_性能分析与优化/VFX性能]]

## 参考资料

- Unity Documentation, *Visual Effect Graph* and *Particle System*.
- Unreal Engine Documentation, *Niagara Renderers* and *Scalability*.
- GPU Gems, particle and flow simulation chapters.
