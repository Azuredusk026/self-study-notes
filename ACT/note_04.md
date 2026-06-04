# 游戏框架实现：从动作状态机到移动逻辑的解耦与落地

## 一、 核心知识点与原理剖析

### 1. 架构调整：移动逻辑与动作状态机的分离
在行为层（Behavior Layer）中，将**移动（Movement）**与**动作状态机（Action State Machine，如攻击、跳跃等指令）**区分开来。
*   **原因**：移动指令与普通动作指令混在一起会导致逻辑混乱。
*   **方案**：独立拆分出 `MovementBase` 作为移动基类，专门处理位移相关逻辑，而 `StateHandler` 继续负责状态转换。

### 2. 移动基类（MovementBase）的核心组成
`MovementBase` 模仿 Unity 的 `CharacterController` 设计，包含以下核心要素：
*   **坐标空间（3C 核心概念）**：主角的移动坐标轴应基于**相机空间（Player Input Space）**投射，而非主角当前的朝向。
*   **配置属性**：
    *   `Max Speed`：最大速度。
    *   `Accelerate`：加速度。
    *   `Slope Limit`：爬坡限制（0-89度）。
*   **运行时引用**：
    *   `Rigidbody`、`Animator`、`MonoBehavior`。
    *   `InputBase`：存储当前输入轴信息。
*   **生命周期管理**：提供 `OnInit`、`OnUpdate`（包含 Start/End）、`OnFixedUpdate` 三套生命周期勾子，由上一级系统统一调度。

### 3. 请求-行为（Request-Behavior）流转逻辑
框架通过多层解耦实现输入到行为的转化：
1.  **输入层（Input Layer）**：获取原始硬件输入（WSAD、Space）。
2.  **调用层（Invoker Layer）**：将输入转化为 `CommandID`（如移动命令、跳跃命令）。
3.  **请求层（Request Layer）**：
    *   `RequestReceiver`：接收 Command 并根据映射表转为 `RequestNode`。
    *   `RequestHandler`：通过**双队列（前端/后端队列）**筛选并管理请求的生命周期。
4.  **行为层（Behavior Layer）**：执行具体的业务代码，调用 `Movement` 模块完成物理位移。

### 4. 物理逻辑：跳跃速度公式
在 `MovementSample` 中实现跳跃时，使用了经典的物理公式计算初速度：
$$v = \sqrt{2gh}$$
*   其中 $g$ 是重力加速度（代码中设为10），$h$ 是跳跃高度。这能确保跳跃表现符合物理预期。

---

## 二、 重点术语与概念解析

*   **3C (Character, Camera, Controls)**：游戏开发中最核心的玩家体验三角。本课重点解决了玩家控制（Controls）与角色（Character）在不同空间下的移动映射问题。
*   **位运算状态管理（Bitwise State Management）**：在 `PlayerStateSample` 中，使用 `1 << 0`, `1 << 1` 等位移操作定义状态 ID。
    *   **优点**：可以通过与运算（`&`）快速判断当前是否处于多个状态中的某一个（如：同时判断是否在 Idle 或 Move 状态下）。
*   **装箱与拆箱（Boxing/Unboxing）**：
    *   **装箱**：值类型（int, struct）转换为引用类型（object）。
    *   **拆箱**：引用类型转换为值类型。
*   **反射（Reflection）**：在 `PlayerSample` 中，使用 `Activator.CreateInstance` 根据类名字符串动态创建对象。这实现了高度的灵活性，但也需要注意初始化开销。

---

## 三、 工程经验与避坑指南

### 1. 任务取消机制（Cancel Request）
在执行新任务（如新的一段位移或动画）之前，**必须先取消（Cancel）旧的任务**。
*   **避坑指南**：如果不做取消处理，多个任务（如两个协程或两个物理力）可能同时作用于物体，导致角色行为“裂开”或逻辑冲突。

### 2. 代码的可读性与“炫技”
*   **建议**：代码应保证任何一个程序员在 5 分钟内能看懂逻辑。
*   **避坑指南**：过度使用复杂的 Lambda 表达式嵌套或一行写完所有功能的“优雅”代码，在团队协作中是灾难性的，后期维护成本极高。

### 3. 性能优化：GC 与装箱
*   **性能准则**：避免在循环（Update）中频繁进行装箱拆箱操作。
*   **对象池思维**：减少在运行时的内存申请与回收（GC）。本框架在初始化阶段使用 `object[]` 传递参数虽然涉及装箱，但因为只在创建时发生一次，对性能影响微乎其微，优先保证了框架的通用性。

### 4. 调试技巧：埋点与日志
*   **工程实践**：在各层转换处（如 `SendCommand`、`ReceiveRequest`）埋入 `Debug.Log`。当框架不跑时，通过日志排查是类名拼错（反射失败）、对象未引用还是逻辑条件（Condition）不满足。

---

## 四、 关键实现细节（代码逻辑速查）

### 状态跳转条件判断
使用 Lambda 表达式定义请求执行条件，结合位运算：
```csharp
// 判断是否允许移动：必须在地面，且处于 Idle 或 Move 状态
conditions.Add(RequestID.Move, () => {
    return (stateSample.state & (PlayerStateID.Idle | PlayerStateID.Move)) != 0 
           && stateSample.onGround;
});
```

### 移动向量投影（相机空间）
主角的上下左右应基于摄像机朝向：
```csharp
// 伪代码逻辑
Vector3 inputDir = new Vector3(inputX, 0, inputY);
Vector3 movement = Camera.main.transform.TransformDirection(inputDir);
movement.y = 0; // 锁定垂直方向，防止斜着飞
```

### 框架初始化顺序
1.  初始化数据（Data）。
2.  初始化各个层级对象（Invoker, Receiver, Handler 等）。
3.  **最后一步**：将 Input 实例注入到 Movement 模块中（`SetInput`），确保移动逻辑能获取到最新的输入轴信息。
