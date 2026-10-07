# 游戏AI决策模型

决策系统把感知到的信息变成可执行意图。最基础的循环是 Sense-Think-Act：感知层更新可用事实，决策层选择目标或动作，执行层向移动、动画和技能系统发请求。三层分开后，行为逻辑不必直接读场景里的所有对象，也不必亲自修改角色位移。

最直接的 Script-based AI 把行为顺序写在脚本或关卡事件中，适合高度确定的演出。Rule-based AI 用“条件 → 动作”规则响应世界事实，适合边界清楚、组合数量可控的系统。两者都需要把条件、执行副作用和优先级显式化，否则规则会形成难以追踪的覆盖关系。

BDI 用 Belief、Desire、Intention 描述 Agent：Belief 是它当前相信的世界状态，Desire 是候选目标，Intention 是已经承诺执行的计划。它的价值在于区分“知道什么、想做什么、正在坚持什么”，适合需要有限理性和持续意图的角色；实现时仍要定义信息过期、目标冲突和重规划条件。

## 反应式行为怎样组合

### FSM 与 HFSM

Finite State Machine 用状态和转移表达行为，适合待机、巡逻、追击、攻击这类边界明确的小系统。问题通常不是 FSM 本身，而是把感知、动画、技能和高层目标全塞进一张图，最后产生任意状态到任意状态的转移。

Hierarchical FSM 把共享逻辑放到父状态，例如“战斗”下再分追击和攻击，可以减少重复转移。状态进入、更新、退出的副作用必须清楚；跨帧异步行为要能取消，否则退出状态后旧回调仍可能生效。

### Behavior Tree

行为树从根节点向下运行。Sequence 要求子节点依次成功，Selector 选择第一个可成功的分支，Decorator 修改条件、次数或返回值，Leaf 执行条件判断和动作。常见返回值是 Success、Failure、Running。

Blackboard 保存目标、最后可见位置、危险程度等共享事实。它是受控的数据接口，不该成为任意系统都能写的全局字典。Key 最好有类型、来源和更新时间；短期感知与长期记忆要区分。

逐帧 Tick 整棵树实现简单，但大量 NPC 会浪费预算。事件驱动或条件观察可以只在相关 Blackboard 值变化时重新评估。Running 节点仍需收到更新和取消通知。调试器应记录当前路径、节点返回值、条件变化和中止原因。

行为树擅长表达设计师可读的层次与优先级，但树太大时会出现重复条件和隐式依赖。可把移动、战斗等稳定能力封装成可测试 Task，而不是不断复制子树。

节点实现常对应软件设计模式。父类用 Template Method 固定 Enter、Tick、Exit 与取消流程，子类只实现具体判断或动作；Decorator 包裹子节点，增加条件、循环、冷却或返回值变换。模式名称不是目标，关键是让节点生命周期和组合语义一致。

#### 中止语义

行为树真正难的不是节点类型而是中止。Decorator 上的条件通常分两档：Lower Priority 只在自己的子树未被激活时评估，用来让高优先分支抢走控制权；Self 只在自己子树激活时评估，用来让持续条件失效时退出。追击子树正在跑而“看见敌人”变假，攻击请求要被取消、按定义好的取消顺序退出 Running 子节点与父节点，并复位每个节点的内部索引。

实现上把条件注册成对 Blackboard 键的观察（Observer Abort），键变化时主动触发重评估，而不是每帧轮询整棵树——后者在大树上既浪费预算又让中止时机不可控。漏掉 Exit 的症状很典型：角色被打断后仍朝旧目标走两步，因为移动请求没有随子树一起取消。

### Utility AI

效用系统给候选行为计算分数，再选择最高或按概率采样。一个需求值可以通过 Curve 映射到 $[0,1]$，多个 Consideration 再组合。乘法会让任意低分强烈压低总分，加法更容易让不同数量的条件产生偏差，因此需要统一归一化规则。

最高分硬切换容易在相近行为间抖动，可加入迟滞、冷却、最短持续时间或当前行为加成。随机性应使用可复现种子，并显示每个候选的输入、曲线和最终分数。Utility AI 适合“此刻更值得做什么”，但不会自动生成一长串满足前置条件的计划。

#### 效用的组合与迟滞

```cpp
float ScoreAction(const Action& action, const Blackboard& bb)
{
    float score = 1.0f;
    for (const Consideration& c : action.considerations) {
        float input = c.eval(bb);               // 原始量先归一化到 [0,1]
        float s = c.curve.Evaluate(input);      // 曲线映射到效用
        s = pow(s, c.weight);                   // 权重以指数进入，保持 [0,1]
        score *= s;
        if (score < 1e-4f) return 0.0f;         // 乘性组合下低分不可逆，提前出局
    }
    return score;
}
```

这里展示乘法组合，输入与曲线输出在 $[0,1]$ 内，指数权重为正。零分会否决动作，适合表达必要条件。条件数量不同会影响分数，跨动作比较前需选择并验证归一化策略，例如加权几何平均；补偿公式属于项目策略，需要用测试局势校准。防抖可以给当前动作增加迟滞阈值，只在新动作明显更优时切换。

## 目标怎样分解成计划

### GOAP

Goal-Oriented Action Planning 把世界表示成有限事实。Action 声明 Preconditions、Effects 和 Cost，Goal 描述希望满足的事实。规划器从当前状态搜索一条动作序列，例如“拿到武器 → 接近掩体 → 攻击”。

事实数量太多会让状态空间爆炸。应只保留会影响计划选择的抽象信息，连续量通常离散成区间。Action Cost 可以包含时间、风险和资源，但各项尺度需要统一。环境变化使前提失效时再 Replan，不能每帧无条件重新搜索。

#### 规划的反向搜索

```cpp
Plan GoapPlan(WorldState start, Goal goal, Action[] actions)
{
    open.Push({ goal.facts, {}, 0 });           // 待满足事实、已选动作、累计成本
    while (!open.IsEmpty()) {
        Node node = open.PopLowestCost();
        if (start.Satisfies(node.required))     // 当前世界已满足全部剩余前提
            return Reverse(node.actions);
        foreach (Action& action in actions) {
            if (!action.effects.Intersects(node.required)) continue;
            Facts remaining = node.required - action.effects + action.preconds;

            open.Push({ remaining, node.actions + action,
                        node.cost + action.cost });
        }
    }
    return null;
}
```

这是回归规划的算法轮廓。每步用动作效果满足部分目标，再把动作前提加入剩余需求。完整实现还需检查负效果与目标冲突、重复状态、成本更新和搜索上限。当前状态尚未满足某项前提时，其他动作可能建立它，不能据此直接剪枝。布尔事实可用位掩码保存；多值状态需要显式的键值表示与冲突规则。

计划只是意图，不保证底层动作一定成功。执行器要报告完成、失败、取消和超时，规划器据此更新事实。调试时同时保存搜索过的状态、被拒绝的前提和最终成本。

### HTN

Hierarchical Task Network 从高层 Compound Task 出发，按 Method 的条件把它分解，直到得到 Primitive Task。比如“守卫区域”可根据警报状态分解成巡逻，或分解成搜寻、呼叫支援和交战。

HTN 的搜索空间通常比完全自由的 GOAP 小，因为设计师已经提供合理分解。代价是知识更多地写在 Method 中，内容覆盖不全时可能没有可用方案。它适合流程和战术结构清楚的玩法，也方便把关卡设计经验编码进去。

## 怎么选

小而确定的局部行为用 FSM；需要清晰优先级和可视化编排时用行为树；多个需求持续竞争时用 Utility；动作前提会组合成不同计划时用 GOAP；流程有稳定层级与领域知识时用 HTN。实际项目经常组合：Utility 选高层目标，行为树负责执行，局部技能内部再用状态机。

架构边界比算法名称更重要。感知只提供带时效的信息，决策输出请求，动作系统验证资源与规则，动画系统负责表现。服务端或确定性模拟中的权威结果不能由不可复现的黑盒决策直接决定。

## 验证方法

- 确定性回放：固定种子与世界快照离线重放整局决策，逐帧比对每个 NPC 的当前节点与动作序列；任何分叉都要能定位到具体 Blackboard 键的变化。
- 中止测试集：为每类 Observer Abort 构造“打断瞬间”用例，确认被打断动作的 Exit 执行了、外部请求被取消、黑板残留状态被清理。
- 黑板审计：记录每个键的写入者与时间戳，检查是否有系统绕过受控接口直接改写，短期感知键是否按过期时间清理。
- Utility 回归：录制典型局势（残血、弹尽、被围），确认期望动作得分第一；每个 Consideration 的输入、曲线输出与总分写日志，分数异常时可回放归因。
- GOAP 计划校验：对生成的计划逐步骤检查前提在模拟中成立；动作执行失败时确认执行器上报失败并触发 Replan，而不是原地干等。
- 预算检查：统计单帧决策耗时的 P99；大量 NPC 时确认事件驱动重评估生效，检查持续 Running 任务更新与条件重评估各占多少成本。事件驱动和逐帧 Tick 都可以成立，选择取决于实现语义与预算。

### Sequence 节点的 Tick

Sequence 按顺序执行子节点，遇到 `Running` 时保存当前索引，遇到 `Failure` 时立即失败：

```cpp
Status Sequence::Tick(Context& ctx)
{
    while (currentChild < children.size()) {
        Status status = children[currentChild]->Tick(ctx);
        if (status == Status::Running) return status;
        if (status == Status::Failure) {
            currentChild = 0;
            return status;
        }
        ++currentChild;
    }
    currentChild = 0;
    return Status::Success;
}
```

树被 Abort 时还要把正在运行的子节点复位，并释放移动、动画等外部请求。若每帧都从第一个子节点开始，长动作会重复初始化。调试视图应显示当前 Running 路径、进入时间、退出状态和 Blackboard 读取值。

## 相关主题

- [[19_Gameplay与游戏框架/玩法事件与脚本]]
- [[20_游戏AI/游戏AI导航]]
- [[20_游戏AI/群体战术信息]]、[[20_游戏AI/MCTS]]、[[20_游戏AI/游戏强化学习]]

## 参考资料

- Millington and Funge, *Artificial Intelligence for Games*.
- Orkin, *Three States and a Plan: The AI of F.E.A.R.*（GOAP 的原始实践报告）.
- Isla, *Handling Complexity in the Halo 2 AI*（行为树在工业项目中的成形）.
- Colledanchise and Ögren, *Behavior Trees in Robotics and AI*（节点语义与中止的形式化整理）.
- Dave Mark, *Behavioral Mathematics for Game AI*（Utility 曲线组合、补偿因子与迟滞的系统推导）.
