# ACT游戏框架开发：输入层 (Input Layer) 的体系化构建与实战拆解

## 一、 核心知识点与原理剖析

### 1. 程序分层设计的初衷
在构建如ACT（动作游戏）等复杂框架时，分层设计（Layered Design）的核心目的是**提高可维护性、增强可扩展性**。
*   **解耦：** 输入层（Input Layer）不应散落在项目的各个角落，而应提供一个全局访问器。
*   **定向传输：** 输入层只为请求层（Request Layer）提供数据传输，与其他层级不产生依赖，使代码结构规整、优雅。

### 2. 纯 C# 类与 Unity 生命周期管理（时序问题）
本次框架开发中的核心类（如 `InputBase`）**不继承 `MonoBehaviour`**。
*   **原生 C# 类的优势：** 不受 Unity 默认生命周期（Start/Update）的自动管理。
*   **解决时序冲突（Execution Order）：** 当项目中存在大量 `MonoBehaviour` 时，它们的 `Update` 执行顺序是随机的。在 ACT 游戏中，如果逻辑执行顺序不固定（例如结算先于输入执行），会导致严重的异常。
*   **手动驱动：** 通过一个终端 `MonoBehaviour` 类作为入口，统一调度所有原生 C# 类的生命周期，确保逻辑执行顺序严格按照设计进行。

### 3. 输入层生命周期的自定义架构
为了比 Unity 提供更细腻的控制，框架在 `InputBase` 中架构了自定义生命周期钩子：
*   `Update` / `FixedUpdate`：主循环逻辑。
*   `GetInputAxis`：受保护的虚方法，专门用于获取输入轴。
*   `SendCommand` / `FixedSendCommand`：将输入数据转化为命令并发送。
*   **扩展钩子：** 如 `EndOfUpdate`、`StartOfUpdate` 等，用于处理更精细的逻辑时序。

---

## 二、 重点术语与概念解析

### 1. 核心类定义
*   **InputData (数据类)：** 纯数据结构，用于存储当前帧的信号（如上下左右、按键状态）。
*   **InputBase (输入基类)：** 框架骨架，利用泛型约束（`where T : InputData, new()`）保证兼容性。它不包含具体业务逻辑，只负责生命周期管理和数据流转。
*   **InvokerBase (命令发送执行器)：** 命令发送的核心单元。它维护一个命令列表（Command List）和一个接收者引用（ReceiverBase），负责将解析后的指令推送到下一层。
*   **InputDevice (硬件适配层)：** 对接底层 API（如 Unity 新版 `Input System`）。它负责读取物理设备的原始数据（键盘、鼠标、手柄），并将其初步转化为框架通用的信号。

### 2. 动作系统术语（基于《街霸6》案例拆解）
*   **输入缓冲队列 (Input Buffer)：** 记录过去若干帧内的输入序列，是实现“搓招”的前提。
*   **判定帧 (Active Frames)：**
    *   **前摇 (Startup)：** 动作开始到产生判定前的帧数。
    *   **判定 (Active)：** 产生攻击效果的红框帧数。
    *   **后摇 (Recovery)：** 动作结束后的硬直收尾帧数。
*   **招式取消 (Cancel)：** 在特定帧内（通常是判定帧中），通过输入新指令中断当前动作的后摇，直接跳入下一个状态。
*   **蓄力 (Charge)：**
    *   **指令前蓄力：** 如春丽的“后蓄前拳”，需要维持方向键一定帧数。
    *   **指令后蓄力：** 如卢克的“指节拳”，按下指令后持续按住按键增强威力。

---

## 三、 框架核心代码实现逻辑

### 1. InputBase 泛型设计
```csharp
public abstract class InputBase<T> where T : InputData, new() {
    protected T m_InputData;
    protected InvokerBase m_Invoker;

    // 获取数据，若为空则实例化
    public T GetInputData() {
        if (m_InputData == null) m_InputData = new T();
        return m_InputData;
    }

    // 抽象生命周期
    public virtual void Update() {
        GetInputAxis();
        SendCommand();
    }
}
```

### 2. InputDevice 硬件读取
通过新版 `InputSystem` 获取当前设备实例，并将其转化为坐标向量：
```csharp
public static Vector2 GetMovement() {
    var keyboard = Keyboard.current;
    if (keyboard == null) return Vector2.zero;
    
    float h = (keyboard.dKey.isPressed ? 1 : 0) - (keyboard.aKey.isPressed ? 1 : 0);
    float v = (keyboard.wKey.isPressed ? 1 : 0) - (keyboard.sKey.isPressed ? 1 : 0);
    return new Vector2(h, v);
}
```

---

## 四、 工程经验与避坑指南

### 1. 开发避坑与技巧
*   **代码整洁度：** 即便只有一行逻辑，也必须加 `if` 大括号。禁止使用语法糖（如 `=>` 箭头函数）来代替复杂方法，确保框架结构统一，降低阅读负担。
*   **缓存清理：** 当 Unity 包管理器（Package Manager）报错或缓存异常时，可手动删除项目根目录下的 `Library`、`Logs`、`Temp` 文件夹，重新打开项目让其自动构筑。
*   **Input System 依赖：** 使用新版输入系统需在 `Player Settings` 中开启对应的后端支持，并注意处理设备为空（Null）的异常情况。

### 2. 搓招判定逻辑优化建议
*   **优先级排序：** 在解析输入队列时，应先判定“超必杀”，再判定“普通必杀”，最后判定“普通攻击”。因为复杂的招式通常包含简单招式的指令序列。
*   **指令消化：** 一旦一个指令序列被识别并触发了特定招式，应“消化”掉这些信号，防止其在同一帧触发多个不相关的动作。
*   **斜向判定：** 在格斗游戏中，斜下方向信号通常应被视为同时包含了“下”和“前/后”两个分量，这在处理升龙拳等指令时至关重要。

### 3. 数据驱动的生产力解放
*   **ScriptableObject (SO) 的应用：** 将动作的数值参数（如跳跃高度、位移速度、前/后摇帧数）全部写在 SO 配置文件中，而非硬编码。
*   **意义：** 程序只负责架构逻辑（加新功能），而玩法调优、数值修改完全交给策划通过 SO 进行，实现“程序解放生产力，策划自主调玩法”。
*   **状态机解耦：** 状态机中的每个 State 也建议做成可配置的对象，通过数据驱动实现状态的动态添加与切换。

---

## 五、 Q&A 互动精华整理

**Q：双击、长按、蓄力应该在输入层还是请求层处理？**
**A：** 建议放在请求层（Request Layer）。输入层只负责最纯粹的 0 和 1 信号（按下/抬起/坐标），而复杂的逻辑解析（如计时、判断长短按、识别搓招队列）应由请求层结合业务逻辑去拆解。

**Q：如何处理不同载具（飞机、坦克）的输入差异？**
**A：** 输入层保持统一，在最后的行为层（Behavior Layer）实现。角色根据当前所处的状态（骑车状态、驾驶状态），对同一个输入请求做出不同的行为响应。

**Q：为什么需要两个请求队列（前端/后端）？**
**A：** 为了处理请求的“滞后性”和“优先级”。未通过的请求可以放入后端队列在下一帧重新尝试，确保在复杂的连招判定中不丢失玩家指令。
