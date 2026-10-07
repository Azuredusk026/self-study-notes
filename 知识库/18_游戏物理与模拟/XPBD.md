# XPBD

增加普通PBD迭代次数，布料会变硬，参数难以跨时间步保持一致。XPBD把Compliance与累计乘子加入约束更新，让柔软度有明确量纲。迭代顺序和有限预算仍影响收敛。

## 布料与 XPBD

布料可以用质点和边约束表示。Verlet 或半隐式欧拉负责预测位置，约束求解负责恢复边长、弯曲和体积。PBD 直接修正位置，稳定且易控制；XPBD 为约束增加 Compliance，使软硬程度对时间步和迭代次数更稳定。

XPBD 的约束增量常写成：

$$
\Delta\lambda=\frac{-C(x)-\tilde{\alpha}\lambda}{\sum_i w_i\lVert\nabla C_i\rVert^2+\tilde{\alpha}},\qquad
\tilde{\alpha}=\alpha/\Delta t^2
$$

C 是约束误差，w 是逆质量，alpha 是 Compliance。Pinned Weight、碰撞厚度、自碰撞和阻尼需要一起调。渲染网格可以绑定到更低分辨率的 Physical Mesh，避免直接模拟所有顶点。

## XPBD 距离约束

两个粒子的位置为 `x0`、`x1`，逆质量为 `w0`、`w1`。`compliance` 控制柔软度，`lambda` 在同一时间步的迭代间保留：

```cpp
Vec3 d = x1 - x0;
float length = Max(Length(d), 1e-6f);
Vec3 n = d / length;
float C = length - restLength;
float alpha = compliance / (deltaTime * deltaTime);
if (w0 + w1 + alpha <= 0.0f) return;
float deltaLambda = (-C - alpha * lambda) / (w0 + w1 + alpha);
lambda += deltaLambda;
x0 -= w0 * deltaLambda * n;
x1 += w1 * deltaLambda * n;
```

这是约束求值片段，要求正时间步、非负 compliance，并对重合粒子选择稳定方向或跳过。两个粒子都固定且 compliance 为零时直接返回，避免零分母。固定粒子的逆质量为 0。XPBD 用 `compliance / dt²` 减少刚度随时间步变化的问题，但迭代数和约束顺序仍影响结果。把时间步减半并保持相同物理时间，绳长误差应接近；差异很大时检查 `lambda` 的清零时机和单位。

## 验证方法

同一物理时长用不同正时间步比较伸长误差，检查每步lambda清零与迭代内保留。固定双端、重合点与零Compliance要处理零分母，不能用epsilon隐藏非法配置。角色代理映射见角色布料。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[09_动画系统/角色布料]]
- [[18_游戏物理与模拟/刚体物理求解]]
- [[18_游戏物理与模拟/Character Controller]]
- [[18_游戏物理与模拟/Ragdoll]]
- [[18_游戏物理与模拟/破坏系统]]
- [[18_游戏物理与模拟/载具物理]]

## 参考资料

- Matthias Müller et al., *Position Based Dynamics*（PBD 原始论文）.
- Miles Macklin et al., *XPBD: Position-Based Simulation of Compliant Constrained Dynamics*（Compliance 形式化的来源）.
- Erin Catto, *Soft Constraints* 与 *Solver* 系列 GDC 讲义（约束求解的工程推导）.
- Hans Pacejka, *Tire and Vehicle Dynamics*（滑移率、侧偏角与魔术公式）.
- NVIDIA PhysX Character Controller 与 Vehicle 文档；Unreal Chaos 布料与破坏文档.
