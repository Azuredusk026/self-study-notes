# Character Controller

把玩家当普通刚体推，接触响应未必符合操作意图。Character Controller以胶囊扫掠寻找最早碰撞，再沿接触面滑动；台阶、坡面和移动平台分别定义规则。位移和碰撞的单位必须一致。

## 扫掠与滑动

常见角色控制器使用胶囊做扫掠，而不是把玩家当普通动态刚体。一次位移会先检测最早碰撞，再把剩余位移投影到接触平面形成滑动。跨台阶需要额外尝试“向上、向前、向下”三个阶段，并检查台阶高度和落点。

坡度限制通过地面法线与 Up 的夹角判断可站立区域。贴地检测需要容忍很小的间隙，但安全间距过大又会让角色悬浮。移动平台要明确继承平台位移还是速度，并处理平台旋转。

### 扫掠与滑动循环

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
        displacement = remaining - hit.normal * Min(0.0f, Dot(remaining, hit.normal));
    }
    return position;                                  // 迭代耗尽：停在夹角处
}
```

这是单平面滑动的算法伪代码。扫掠返回比例 `hit.fraction`，`skinWidth` 是世界空间长度，必须除以位移长度后才能相减。接触法线需归一化，初始穿透要先单独处理。

每次碰撞后将剩余位移投影到接触平面，再做下一次扫掠。本片段用碰撞比例计算剩余位移，安全间距会使一次移动保守缩短；需要精确保留切向距离时，必须连同接触偏移一起定义剩余位移。完整控制器还需保留多个接触平面，在两面夹角沿交线移动，在封闭角落停止。用不同位移长度推进同一墙面，确认安全间距始终相同，再测试楔形墙角和 90 度内角。

跳跃初速度可由目标高度 h 推出：

$$
v_0=\sqrt{2gh}
$$

这里 g 使用重力加速度的正值。为了手感，起跳和下落可以使用不同重力倍率，但要把它当玩法规则，而不是物理常量。

## 坡面、台阶与平台

地面法线n和单位向上轴u的点积给出坡度余弦。设最大可站立角为θ，`dot(n,u)>=cos(theta)` 才把接触记成可站立地面。垂直墙不能仅因胶囊接触就恢复跳跃资格；陡坡的横向滑动与重力滑落由玩法规则分别处理。

台阶尝试先向上扫掠不超过最大台阶高，再水平前进，最后向下寻找可站立落点。三次查询都保留胶囊体积；只射一条向下射线会漏掉头顶和身体侧面的阻挡。任一步受阻或落点超坡度上限，就退回普通滑动结果。

角色站在旋转平台上时，把脚点先变到平台上一帧的局部空间，再用当前平台矩阵变回世界空间，两位置之差就是应继承的平台位移。只加平台质心平移会漏掉旋转造成的切向运动。离开平台时是否继承速度由跳跃规则确定，并避免与角色自己的积分重复。

单面滑动只移除朝向障碍内部的分量：`remaining -= n * min(0,dot(remaining,n))`，其中n从障碍指向角色。接触法线若表示反方向，符号也随之改变。多个接触面需要共同限制剩余位移，不能在两面之间反复投影而越过已有接触。

## 验证方法

楔形内角、台阶、斜坡与平台旋转分别测试。记录扫掠比例和skin宽度，不可达目标限迭代，初始穿透单独解出。与固定步长参考比较跳跃高度。


## 实现与证据

2026-10-22，以本机 Python 3.11 运行 `python 知识库/examples/revision_16_21/test_reference.py`，17项检查通过。[参考实现](../examples/revision_16_21/reference.py)与[测试输入](../examples/revision_16_21/test_reference.py)可复现本页注明的机制。 本页只检查单面滑动保留切向和离开分量。胶囊扫掠、台阶与旋转平台依赖宿主物理查询，尚未接入运行。

## 相关主题

- [[18_游戏物理与模拟/刚体物理求解]]
- [[19_Gameplay与游戏框架/输入与动作状态]]
- [[18_游戏物理与模拟/Ragdoll]]
- [[18_游戏物理与模拟/XPBD]]
- [[18_游戏物理与模拟/破坏系统]]
- [[18_游戏物理与模拟/载具物理]]

## 参考资料

- [PhysX5.4.1 Character Controllers](https://nvidia-omniverse.github.io/PhysX/physx/5.4.1/docs/CharacterControllers.html)：Kinematic Character Controller、Auto Stepping、Walkable Parts；2026-10-22核读。
