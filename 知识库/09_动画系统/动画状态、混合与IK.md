# 动画状态、混合与 IK

动画系统的职责不是“播放一个 Clip”，而是根据 Gameplay 状态生成连续 Pose，并在最后用 IK 和约束适应地面、武器与交互目标。

## Clip 采样

Animation Clip 保存多个 Joint 或属性随时间变化的 Track。运行时根据归一化时间找到相邻 Key，对 Translation/Scale 做 Lerp，对 Rotation 做 Nlerp 或 Slerp。

Clip 需要明确：

- Sample Rate 和是否循环；
- Root Motion 轨道；
- Event 与 Curve；
- 起止 Pose 是否连续；
- 参考姿态和骨架版本。

高 Sample Rate 不保证更好。源动画频率、压缩误差和最终动作速度共同决定所需采样密度。

## State Machine

State Machine 把 Idle、Walk、Run、Jump、Attack 等动作组织成状态和 Transition。Transition 一般依赖参数、事件、Exit Time 和优先级。

常见问题：

- Any State 过多，导致无法推断实际跳转路径；
- 动画 Event 与 Gameplay 状态互相驱动，形成隐式循环；
- 过渡可被连续打断，Pose 永远到不了稳定状态；
- 状态数量因武器、受伤和移动方向做笛卡尔积，迅速膨胀。

复杂系统可把 Gameplay 状态与 Pose 生成分开。Gameplay 决定意图和标签，Animation Graph 负责选择、混合和修正动作。

## Crossfade

两个 Pose 的局部 TRS 按权重混合：

$$
T=(1-w)T_A+wT_B
$$

Rotation 通常用 Nlerp/Slerp。每个 Joint 混合后再累积层级，能保持骨长关系。

线性权重不一定产生自然速度。Ease Curve 能让过渡的起停更柔和，但打击动作可能需要短而明确的过渡。

还要处理两段动作的相位。例如左右脚完全相反的 Walk/Run 直接混合，会让双脚互相抵消。可用 Sync Marker 或归一化步态相位对齐脚步事件。

## Blend Tree

1D Blend Tree 根据 Speed 在 Idle、Walk、Run 间插值。2D Blend Tree 根据前后和左右速度混合方向动作。

它适合连续参数，不适合用几十个离散动作强行铺满二维空间。样本分布不均时，简单三角插值会造成权重突变，需要检查参数空间和动作相位。

二维 Blend Space 常对样本点做 Delaunay Triangulation。运行参数落入某个三角形后，只采样三个顶点动画，并用重心坐标计算权重。这样能处理不规则样本分布，也避免每帧混合全部 Clip；三角形过瘦、样本覆盖不足和参数越界仍需专门处理。

## Motion Matching

Motion Matching 把动画数据库切成可检索帧，为每帧保存姿势特征和未来轨迹特征。运行时根据当前骨骼状态、期望速度与轨迹查找代价最低的候选，再跳转并混合到该片段。

特征需要归一化和加权，否则位置、速度、朝向等不同量纲会让距离失真。检索结果还要考虑 Pose Continuity、Foot Contact、Transition Cost 和最短驻留时间，避免频繁跳片与脚滑。数据库质量、标签约束和查询可视化通常比单纯更换最近邻算法更重要。

## Additive Animation

Additive Clip 保存相对 Reference Pose 的差值，而不是完整 Pose。

Translation 差值可以相加；Rotation 应用相对旋转：

$$
q_{out}=q_{base}\left(q_{ref}^{-1}q_{add}\right)^w
$$

常见用途：呼吸、瞄准、后坐力、受击、表情和局部姿势修正。Reference Pose 不一致会让角色突然偏移或扭曲。

## Layer 与 Bone Mask

Layer 可以让下半身保持移动，上半身播放持枪或攻击。Bone Mask 决定哪些 Joint 接收这一层。

边界不能生硬截断。只替换手臂而不处理胸椎和肩部，会在肩膀产生断裂。Mask 通常需要从骨盆/脊柱开始渐变，并处理 IK 目标和武器挂点的一致性。

## Root Motion

Root Motion 从动画 Root Track 提取位移和旋转，驱动角色实体。它能保持脚步与位移一致，适合攻击突进、翻滚和精确表演。

Gameplay-driven Movement 则由角色控制器决定速度，动画只跟随参数。它响应直接、网络预测更容易，但可能脚滑。

项目常混合使用：常规移动由代码驱动，特殊动作消费 Root Motion。需要明确 Root Motion 在本地、服务器和重放中的权威来源，并处理碰撞阻挡后的剩余位移。

## FK 与 IK

Forward Kinematics（FK）从父到子给定关节旋转，结果稳定且符合动画制作习惯，但末端位置只能间接控制。

Inverse Kinematics（IK）给定 End Effector 目标，反求链上 Joint。它适合脚贴地、手握武器、看向目标和攀爬接触。

IK 通常是在已采样动画上做最后修正，不是替代全部动画。

## Two Bone IK

手臂和腿可近似为两段固定长度。给定根节点、目标和 Pole Vector，可解析求出中间 Joint 的弯曲平面和两个角度。

目标距离必须限制在：

$$
|l_1-l_2| \le d \le l_1+l_2
$$

超出范围时需要 Clamp 或允许 Stretch。Pole Vector 决定膝盖/肘部朝向；接近完全伸直时平面不稳定，应使用上一帧方向或动画 Hint 防止翻转。

## CCD 与 FABRIK

CCD 从末端向根部迭代旋转每个 Joint，使末端逐步靠近目标。实现简单，但长链可能收敛慢，姿势也容易卷曲。

FABRIK 在位置空间做 Forward/Backward Pass：先从末端向根部拉直，再固定根节点从根向末端恢复骨长。它收敛通常较快，也容易加入长度约束，但仍需把最终位置还原为 Joint Rotation。

迭代 IK 必须设置最大迭代次数和误差阈值，避免不可达目标消耗无限时间。

## Foot IK

一个可用的 Foot IK 不只是 Raycast 后移动脚：

1. 从动画得到原始脚和骨盆 Pose；
2. 向地面查询命中点与 Normal；
3. 计算脚底 Offset 和朝向；
4. 调整 Pelvis，避免腿被过度拉长；
5. 对位置、旋转和权重做时间平滑；
6. 仅在脚处于支撑相位时锁定，抬脚时释放。

移动平台需要把锁定点保存在平台局部空间。楼梯边缘和突然失去地面时要有回退策略。

## Retargeting

Retargeting 把源 Skeleton 动作映射到目标 Skeleton。即使骨骼名称对应，比例、Bind Pose、轴向和 Twist Joint 也可能不同。

常见步骤：建立骨骼映射、对齐 Reference Pose、处理 Root/Pelvis 位移比例、转移局部旋转、重新求解手脚 IK，再做肩膀和扭转修正。

只按骨长比例缩放全部 Translation 容易破坏动作。多数 Joint 应主要传递 Rotation，Root/Pelvis 和 IK Goal 才需要专门处理位移。

## 调试顺序

- 显示当前 State、Transition、Clip Time 和 Blend Weight。
- 分别关闭 Layer、Additive、IK，找到第一个出现错误的阶段。
- 可视化 Skeleton、IK Target、Pole Vector、Root Motion 轨迹和 Foot Lock。
- 记录更新顺序，确认 Gameplay、Animation、Physics 和 Camera 使用同一帧的数据。
- 对低帧率、时间缩放、网络延迟和状态被打断做回归。

### Crossfade 的局部姿态混合

输入是两个相同骨架的局部 Pose。Translation 与 Scale 线性插值，Rotation 使用最短弧 Slerp：

```cpp
for (int joint = 0; joint < skeleton.JointCount(); ++joint) {
    TRS a = SampleLocal(fromClip, joint, fromTime);
    TRS b = SampleLocal(toClip, joint, toTime);
    float alpha = SmoothStep01(blendElapsed / blendDuration);
    localPose[joint].translation = Lerp(a.translation, b.translation, alpha);
    localPose[joint].rotation = SlerpShortest(a.rotation, b.rotation, alpha);
    localPose[joint].scale = Lerp(a.scale, b.scale, alpha);
}
BuildModelPose(localPose, skeleton.parents, modelPose);
```

混合发生在局部空间，层级累积只执行一次。两个 Clip 的时间推进策略、Root Motion 和事件归属需要由状态转换明确决定。若先转成模型空间再逐关节混合，长骨链容易出现长度和轨迹异常；可用手臂快速摆动的转换检查末端轨迹是否连续。

## 相关主题

- [[01_数学与采样/旋转、四元数与插值]]
- [[09_动画系统/骨骼动画、蒙皮与GPU动画]]
- [[09_动画系统/动画压缩、面部、布料与毛发]]

## 参考资料

- Buss, *Introduction to Inverse Kinematics with Jacobian Transpose, Pseudoinverse and Damped Least Squares Methods*.
- Aristidou and Lasenby, *FABRIK: A fast, iterative solver for the Inverse Kinematics problem*.
- Unity and Unreal Engine animation state machine, IK and Root Motion documentation.
