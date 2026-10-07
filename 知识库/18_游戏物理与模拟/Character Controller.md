# Character Controller

把玩家当普通刚体推，接触响应未必符合操作意图。Character Controller以胶囊扫掠寻找最早碰撞，再沿接触面滑动；台阶、坡面和移动平台分别定义规则。位移和碰撞的单位必须一致。

## Character Controller

常见角色控制器使用胶囊做 Sweep，而不是把玩家当普通 Dynamic 刚体。一次位移会先检测最早碰撞，再把剩余位移投影到接触平面形成 Sliding。Stepping 需要额外尝试“向上、向前、向下”三个阶段，并检查台阶高度和落点。

Slope Limit 通过地面法线与 Up 的夹角判断可站立区域。贴地检测需要容忍很小的间隙，但 Skin Width 过大又会让角色悬浮。移动平台要明确继承平台位移还是速度，并处理平台旋转。

### Sweep-Slide 循环

```cpp
Vec3 MoveWithCollision(Vec3 position, Vec3 displacement)
{
    for (int i = 0; i < maxSlideIterations && !IsNearlyZero(displacement); ++i) {
        SweepHit hit;
        if (!SweepCapsule(position, displacement, hit))
            return position + displacement;           // 全程无阻挡
        float distance = Length(displacement);
        float safeFraction = Max(0.0f, hit.fraction - skinWidth / Max(distance, 1e-6f));
        position += displacement * safeFraction;
        Vec3 remaining = displacement * (1.0f - hit.fraction);
        displacement = remaining - hit.normal * Dot(remaining, hit.normal);
    }
    return position;                                  // 迭代耗尽：停在夹角处
}
```

这是单平面滑动的算法伪代码。扫掠返回比例 `hit.fraction`，`skinWidth` 是世界空间长度，必须除以位移长度后才能相减。接触法线需归一化，初始穿透要先单独处理。

每次碰撞后将剩余位移投影到接触平面，再做下一次扫掠。完整控制器还需保留多个接触平面，在两面夹角沿交线移动，在封闭角落停止。用不同位移长度推进同一墙面，确认安全间距始终相同，再测试楔形墙角和 90 度内角。

跳跃初速度可由目标高度 h 推出：

$$
v_0=\sqrt{2gh}
$$

这里 g 使用重力加速度的正值。为了手感，起跳和下落可以使用不同重力倍率，但要把它当玩法规则，而不是物理常量。

## 验证方法

楔形内角、台阶、斜坡与平台旋转分别测试。记录Sweep比例和skin宽度，不可达目标限迭代，初始穿透单独解出。与固定步长参考比较跳跃高度。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[18_游戏物理与模拟/刚体物理求解]]
- [[19_Gameplay与游戏框架/输入与动作状态]]
- [[18_游戏物理与模拟/Ragdoll]]
- [[18_游戏物理与模拟/XPBD]]
- [[18_游戏物理与模拟/破坏系统]]
- [[18_游戏物理与模拟/载具物理]]

## 参考资料

- Matthias Müller et al., *Position Based Dynamics*（PBD 原始论文）.
- Miles Macklin et al., *XPBD: Position-Based Simulation of Compliant Constrained Dynamics*（Compliance 形式化的来源）.
- Erin Catto, *Soft Constraints* 与 *Solver* 系列 GDC 讲义（约束求解的工程推导）.
- Hans Pacejka, *Tire and Vehicle Dynamics*（滑移率、侧偏角与魔术公式）.
- NVIDIA PhysX Character Controller 与 Vehicle 文档；Unreal Chaos 布料与破坏文档.
