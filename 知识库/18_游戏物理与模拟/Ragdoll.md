# Ragdoll

角色受击倒下，直接开启刚体会让身体从绑定姿态跳走。Ragdoll先把物理骨架对齐当前动画，再继承线角速度；恢复时对齐根与骨盆，按权重交回动画控制。

## Ragdoll 与动画混合

Ragdoll 用刚体和关节近似骨骼。动画切入物理时要先把刚体对齐到当前 Pose，并从骨骼运动估计初速度。物理回到动画时不能瞬间夺回全部控制权，通常先选择骨盆或根节点对齐，再按权重混合到可恢复姿势。

关节角度、质量分布和碰撞层比增加求解迭代更重要。相邻骨骼互相碰撞、细长肢体惯性不合理和初始穿透，都会造成“抖成一团”。

切入布娃娃的标准顺序：按当前动画 Pose 摆放刚体、从最近两帧骨骼位移估计线速度与角速度、切换为动态模拟。切回动画时先让根节点对齐到动画根的运动方向，再按关节权重从物理姿势混合到目标姿势，权重曲线持续几百毫秒。混合期间保持关节约束参与求解，否则肢体会被权重拉成不可能姿势。

## 切换轮廓

伪代码输入当前与前帧姿态，速度除以实际正时间步。

```text
AlignBodiesToPose(currentPose)
velocity = (currentPosition-previousPosition)/dt
angularVelocity = RotationDelta(previousRotation,currentRotation)/dt
EnableDynamicsWithInheritedVelocity()
```

## 验证方法

切入瞬间比较位置和速度，切回检查骨盆、关节约束与挂点。质量差、初始穿透与相邻自碰撞逐项关闭定位，恢复权重时长按项目动作测试。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[09_动画系统/骨骼动画与蒙皮]]
- [[18_游戏物理与模拟/刚体物理求解]]
- [[18_游戏物理与模拟/Character Controller]]
- [[18_游戏物理与模拟/XPBD]]
- [[18_游戏物理与模拟/破坏系统]]
- [[18_游戏物理与模拟/载具物理]]

## 参考资料

- Matthias Müller et al., *Position Based Dynamics*（PBD 原始论文）.
- Miles Macklin et al., *XPBD: Position-Based Simulation of Compliant Constrained Dynamics*（Compliance 形式化的来源）.
- Erin Catto, *Soft Constraints* 与 *Solver* 系列 GDC 讲义（约束求解的工程推导）.
- Hans Pacejka, *Tire and Vehicle Dynamics*（滑移率、侧偏角与魔术公式）.
- NVIDIA PhysX Character Controller 与 Vehicle 文档；Unreal Chaos 布料与破坏文档.
