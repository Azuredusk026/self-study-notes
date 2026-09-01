# 动作游戏框架设计（第三课）：请求层、行为层与系统集成

本课核心任务是完成动作游戏框架的底层架构搭建，涵盖请求层（Request Layer）、行为层（Behavior Layer）以及将各层级联动的代理层（Agent/Player Layer）。重点在于通过反射机制实现低耦合的实例初始化，并建立严格的生命周期更新顺序，以解决 Unity 自带 `MonoBehaviour` 时序混乱的问题。

## 一、 核心知识点与原理剖析

### 1. 请求层（Request Layer）深度解析
请求层是输入层与行为层之间的中转站，负责指令的接收、筛选、存储与分发。

*   **RequestReceiver（请求接收器）**
    *   **核心功能**：维护一个字典 `requestDictionary<int, RequestBase>`，将请求 ID 与具体的请求对象映射。
    *   **注册机制**：提供 `Register` 与 `Unregister` 方法，允许动态添加或移除功能模块，确保系统闭环。
    *   **多态处理**：支持带参数（`object[]`）与不带参数的请求接收，增强了数据的扩展性。
*   **RequestHandler（请求处理器）**
    *   **逻辑原理**：使用前端队列与后端队列对请求进行筛选和排序。
    *   **生命周期管理**：通过 `Update` 和 `FixedUpdate` 驱动队列中的请求，判断请求是否过期或满足执行条件。
*   **RequestBase（请求基类）**
    *   **属性**：包含行为引用（`BehaviorBase`）、请求 ID、生命周期帧数（`LifeStep`）以及执行条件委托（`Func<bool>`）。
    *   **状态管理**：定义请求状态枚举（后端、前端、执行结束），支持在生命周期内自增帧数并在过期时自动销毁。

### 2. 行为层（Behavior Layer）与状态管理
行为层是逻辑的最终执行者，核心是状态机与具体行为的映射。

*   **BehaviorBase（行为基类）**
    *   作为冷酷的执行者，它只负责接收请求并调用对应的执行逻辑（`ExecuteRequest`）。
*   **StateHandlerBase（状态处理器基类）**
    *   **设计理念**：参考 Unity `Animator` 源码逻辑，但将逻辑控制权收回到脚本中。
    *   **核心字段**：当前状态哈希（`CurrentStateHash`）、标签（`Tag`）、转换标志（`IsInTransition`）。
    *   **数据驱动**：提供 `StartConfiguration` 方法，支持从配置表、SO（ScriptableObject）或 JSON 中读取状态与跳转条件。
    *   **哈希同步**：实时通过 `Animator.GetCurrentAnimatorStateInfo` 更新脚本内的哈希值，确保逻辑层与表现层状态一致。

### 3. 系统集成：Agent 与 PlayerBase
这是框架的顶层，负责所有底层组件的实例化与驱动。

*   **Agent（代理层）**
    *   继承自 `MonoBehaviour`，作为所有实体（玩家、敌人 AI）的基类，提供 Transform 获取和组件封装（`GetEntityComponent`）。
*   **PlayerBase（玩家基类）**
    *   实现 `IPlayerBase` 接口，持有所有层级的引用（Input, Invoker, Request, Behavior, State）。
    *   **三段式初始化**：`AgentData`（数据加载） -> `FrameworkInit`（框架初始化） -> `EndOfInit`（结束回调）。

### 4. 关键技术：基于反射的实例初始化
为了实现基类代码的复用，避免在子类中重复编写 `new` 操作，引入了反射工具类 `ActivatorUtil`。

*   **原理**：通过类名字符串（`string`）和构造函数参数列表（`object[]`），利用 `System.Activator.CreateInstance` 在运行时创建具体子类的对象。
*   **优势**：在父类 `PlayerBase` 中定义初始化流程，子类只需提供具体的类名字符串，即可完成高度解耦的实例化。

---

## 二、 重点术语与概念解析

*   **封闭原则（Open-Closed Principle）**：在框架设计中，核心流程代码（如 `Update` 顺序）一旦确定即封死不动。开发者通过继承和重写子类逻辑来扩展功能，而非修改框架源代码。
*   **时序问题（Timing Issue）**：Unity 中多个 `MonoBehaviour` 的 `Update` 执行顺序是不确定的。本框架通过一个统一的管理器（`PlayerBase`）手动按顺序调用各个层的 `OnUpdate`，确保逻辑链条（输入->请求->行为）永远正确。
*   **模板方法模式（Template Method Pattern）**：在基类中定义算法的骨架（如 `OnUpdate` 内部的调用顺序），将某些步骤延迟到子类实现（如 `OnRequestExecute`）。
*   **单向依赖（One-way Dependency）**：系统内部遵循严格的依赖关系。初始化顺序为**由下至上**（Behavior -> Request -> Input），而执行顺序为**由上至下**（Input -> Invoker -> Request -> Behavior -> State）。

---

## 三、 工程经验与避坑指南

### 1. 开发经验与架构建议
*   **解耦 MonoBehaviour**：不要让所有类都继承 `MonoBehaviour`。初学者习惯全员继承，但项目变大后会导致时序不可控。应通过一个主 `MonoBehaviour`（如 `PlayerBase`）来驱动一堆纯 C# 类。
*   **Animator 的使用策略**：
    *   **蜘蛛网问题**：当动作过多时，Animator 连线会变得极其复杂（蜘蛛网）。
    *   **解决建议**：将逻辑判断留在脚本状态机中，Animator 仅作为一个纯粹的播放器，脚本通过哈希直接切换动画，无需在 Unity 编辑器中连线。
*   **生命周期管理**：建议使用“帧（Frame）”而非“秒”作为请求的生命周期单位，因为逻辑循环（Loop）通常是基于帧执行的，这样更符合底层运行逻辑。

### 2. 避坑指南
*   **初始化顺序**：必须严格遵守依赖关系。如果先初始化 `Invoker` 而此时 `RequestReceiver` 还没创建，会导致空引用异常。
*   **反射性能**：虽然反射有一定开销，但仅在 `Awake` 阶段初始化时使用一次，对运行效率影响微乎其微。
*   **访问修饰符**：属性建议使用 `get; protected set;`。过度开放 `set` 权限会导致项目耦合度过高，难以维护。

### 3. 职业发展建议（Q&A）
*   **作品集构建**：
    *   不要只盯着一个框架看，要尝试基于框架实现具体的业务逻辑。
    *   建议在框架基础上实现一个完整的 Boss 战或 3D 操控 Demo，包含开宝箱交互、处决动画演示等，这比单纯说“我懂框架”更有说服力。
*   **系统扩展方向**：
    *   **Buff 系统**：动作游戏的实时 Buff 计算（如法环的战前加 Buff）与卡牌游戏的回合制结算 Buff 有很大区别，值得深入研究。
    *   **战斗系统**：深入研究伤害判定、硬直状态切换、动作取消（Cancel）逻辑，这些是动作游戏程序的核心竞争力。
