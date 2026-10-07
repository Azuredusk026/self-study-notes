# IK

一段动画的脚落在平地上，地面变成斜坡以后就会悬空。IK从已采样姿态出发，根据末端目标修正关节链。骨长、弯曲平面、接触相位和迭代预算决定修正是否稳定。

## FK 与 IK

Forward Kinematics（FK）从父到子给定关节旋转，结果稳定且符合动画制作习惯，但末端位置只能间接控制。

Inverse Kinematics（IK）给定 End Effector 目标，反求链上 Joint。它适合脚贴地、手握武器、看向目标和攀爬接触。

IK 通常是在已采样动画上做最后修正，不是替代全部动画。

## 让末端适应交互目标

### Two Bone IK

手臂和腿可近似为两段固定长度。给定根节点、目标和 Pole Vector，可解析求出中间 Joint 的弯曲平面和两个角度。

目标距离必须限制在：

$$
|l_1-l_2| \le d \le l_1+l_2
$$

超出范围时需要 Clamp 或允许 Stretch。Pole Vector 决定膝盖/肘部朝向；接近完全伸直时平面不稳定，应使用上一帧方向或动画 Hint 防止翻转。

### CCD 与 FABRIK

CCD 从末端向根部迭代旋转每个 Joint，使末端逐步靠近目标。实现简单，但长链可能收敛慢，姿势也容易卷曲。

FABRIK 在位置空间做 Forward/Backward Pass：先从末端向根部拉直，再固定根节点从根向末端恢复骨长。它收敛通常较快，也容易加入长度约束，但仍需把最终位置还原为 Joint Rotation。

迭代 IK 必须设置最大迭代次数和误差阈值，避免不可达目标消耗无限时间。

### Foot IK

一个可用的 Foot IK 不只是 Raycast 后移动脚：

1. 从动画得到原始脚和骨盆 Pose；
2. 向地面查询命中点与 Normal；
3. 计算脚底 Offset 和朝向；
4. 调整 Pelvis，避免腿被过度拉长；
5. 对位置、旋转和权重做时间平滑；
6. 仅在脚处于支撑相位时锁定，抬脚时释放。

移动平台需要把锁定点保存在平台局部空间。楼梯边缘和突然失去地面时要有回退策略。

## 两段链的角度

算法伪代码输入正骨长l1、l2，d为根到目标的距离。Clamp后用余弦定理，角度余弦再限制到[-1,1]。

```text
d = clamp(length(target-root), abs(l1-l2)+epsilon, l1+l2-epsilon)
cosRoot = clamp((l1*l1+d*d-l2*l2)/(2*l1*d), -1, 1)
rootAngle = acos(cosRoot)
plane = BuildStablePlane(target-root, poleHint, previousPlane)
```

## 验证方法

目标在可达域内、域外与完全伸直附近分别测试。记录末端误差、骨长误差、迭代数与平面翻转，移动平台锁点保存到平台局部空间。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[09_动画系统/骨骼动画与蒙皮]]
- [[18_游戏物理与模拟/Character Controller]]
- [[09_动画系统/动画姿态混合]]
- [[09_动画系统/动画重定向]]

## 参考资料

- Buss, *Introduction to Inverse Kinematics with Jacobian Transpose, Pseudoinverse and Damped Least Squares Methods*.
- Aristidou and Lasenby, *FABRIK: A fast, iterative solver for the Inverse Kinematics problem*.
- Unity and Unreal Engine animation state machine, IK and Root Motion documentation.
