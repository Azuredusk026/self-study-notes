# XPBD

增加普通PBD迭代次数，布料会变硬，参数难以跨时间步保持一致。XPBD把柔顺度与累计乘子加入约束更新，让柔软度有明确量纲。迭代顺序和有限预算仍影响收敛。

## 布料与 XPBD

布料可以用质点和边约束表示。Verlet 或半隐式欧拉负责预测位置，约束求解负责恢复边长、弯曲和体积。PBD 直接修正位置，稳定且易控制；XPBD 为约束增加柔顺度，使软硬程度对时间步和迭代次数更稳定。

XPBD 的约束增量常写成：

$$
\Delta\lambda=\frac{-C(x)-\tilde{\alpha}\lambda}{\sum_i w_i\lVert\nabla C_i\rVert^2+\tilde{\alpha}},\qquad
\tilde{\alpha}=\alpha/\Delta t^2
$$

C 是约束误差，w 是逆质量，alpha 是柔顺度。固定点权重、碰撞厚度、自碰撞和阻尼决定约束所处的边界条件。渲染网格可以绑定到更低分辨率的物理代理网格，避免直接模拟所有顶点。

## XPBD 距离约束

两个粒子的位置为 `x0`、`x1`，逆质量为 `w0`、`w1`。`compliance` 控制柔软度，`lambda` 在同一时间步的迭代间保留：

```cpp
Vec3 d = x1 - x0;
float length = Length(d);
if (length <= 1e-6f) return; // 方向未定义：本片段跳过并由宿主记录退化约束
Vec3 n = d / length;
float C = length - restLength;
float alpha = compliance / (deltaTime * deltaTime);
if (w0 + w1 + alpha <= 0.0f) return;
float deltaLambda = (-C - alpha * lambda) / (w0 + w1 + alpha);
lambda += deltaLambda;
x0 -= w0 * deltaLambda * n;
x1 += w1 * deltaLambda * n;
```

这是约束求值片段，要求正时间步、非负 compliance，并对重合粒子选择稳定方向或跳过。两个粒子都固定且 compliance 为零时直接返回，避免零分母。固定粒子的逆质量为 0。XPBD 用 `compliance / dt²` 减少刚度随时间步变化的问题，但迭代数和约束顺序仍影响结果。按相同物理时间比较不同步长时，同时记录形变、速度与约束误差。柔顺度的时间步缩放提供相同材料参数，有限步长的惯性和迭代收敛仍可能改变动态绳长；不能要求任意运动在步长减半后误差相等。先用下方孤立静态约束检查乘子清零与单位，再测试动态多约束系统。

## 乘子的量纲与完整时间步

对长度约束 $C=|x_1-x_0|-L$，位置使用米，逆质量使用千克的倒数，柔顺度 $\alpha$ 使用米/牛顿。于是 $\alpha/\Delta t^2$ 与逆质量具有相同量纲，累计乘子 $\lambda$ 的量纲为千克·米，$\lambda/\Delta t^2$ 才对应约束力尺度。把“刚度滑杆”直接填进柔顺度字段会颠倒软硬关系。

一个时间步先用外力预测位置，保存旧位置，把每条约束的乘子清零；迭代时按上式累计乘子并更新位置，结束后用 `(newPosition-oldPosition)/dt` 重建速度。乘子若每轮清零，软约束的弹性项无法累积；跨步直接保留又属于另一套热启动策略，需要相应缩放与分析。

取一端固定、另一端质量1千克，长度由2米拉回静止长度1米，步长0.1秒。零柔顺度给出乘子增量-1，活动端回到1米。柔顺度0.01米/牛顿时分母为2，活动端只回到1.5米；同一步再迭代，误差项与累计乘子项平衡，位置保持1.5米。这个例子说明柔软来自约束方程，有限迭代的多约束收敛仍是另一项误差。

## 验证方法

同一物理时长用不同正时间步比较伸长误差，检查每步lambda清零与迭代内保留。固定双端、重合点与零柔顺度要处理零分母，不能用epsilon隐藏非法配置。角色代理映射见角色布料。


## 实现与证据

2026-10-22，以本机 Python 3.11 运行 `python 知识库/examples/revision_16_21/test_reference.py`，17项检查通过。[参考实现](../examples/revision_16_21/reference.py)与[测试输入](../examples/revision_16_21/test_reference.py)可复现本页注明的机制。 本页检查固定端、柔顺度与同一步乘子累计，重合输入在Python实验中明确拒绝；C++片段采用跳过策略。完整布料碰撞与引擎求解尚未运行。

## 相关主题

- [[09_动画系统/角色布料]]
- [[18_游戏物理与模拟/刚体物理求解]]
- [[18_游戏物理与模拟/Character Controller]]
- [[18_游戏物理与模拟/Ragdoll]]
- [[18_游戏物理与模拟/破坏系统]]
- [[18_游戏物理与模拟/载具物理]]

## 参考资料

- [XPBD原论文](https://mmacklin.com/xpbd.pdf)：第4节公式17、18与Algorithm 1说明位置更新、累计乘子及时间步流程；2026-10-24复核。
