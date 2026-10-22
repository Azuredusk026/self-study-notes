# MCTS

候选动作很多，写固定评分可能难以覆盖长远后果。MCTS反复选择、扩展、模拟并回传，让预算集中到有希望或尚不确定的分支。回报视角和状态复制成本决定搜索能否可靠运行。

## 树搜索与探索

蒙特卡洛树搜索（MCTS） 反复执行选择、扩展、模拟、回传。选择常用 UCT 平衡已知收益与探索：

$$UCT_i=\bar X_i+C\sqrt{\frac{\ln N}{n_i}}$$

$\bar X_i$ 是子节点平均收益，$N$ 是父节点访问次数，$n_i$ 是子节点访问次数。$C$ 越大越偏探索。扩展添加未尝试动作，模拟用简化策略推演，最后把结果沿路径回传。

UCT 是 UCB 思想在树搜索中的应用。PUCT 再引入策略网络给出的先验概率，让高先验动作更早得到探索，同时仍随访问次数调整探索奖励。先验只能引导搜索，最终质量仍取决于模拟、价值估计和访问预算。

MCTS 适合规则可模拟、分支较大且无法预先写出完整评估的决策。其质量依赖状态复制成本、模拟速度和奖励设计。实时游戏按迭代数或时间限制预算；确定性回放还需固定实际迭代数与执行顺序。隐藏信息游戏还需避免在模拟中偷看真实状态。

先测量单次模拟耗时，再确定实时预算允许的迭代数。搜索质量随预算变化的曲线依赖游戏、模拟策略和局面，需要用固定测试集测量，不能预设统一的对数增长规律。

隐藏信息的一种近似是确定化采样：从当前信息允许的完整状态中采样，再分别搜索并汇总结果。它容易产生策略融合，例如把不同隐藏状态下各自可行的动作组合成实际无法执行的策略。应与信息集搜索对比，并检查是否使用了决策者无法观察的信息；偏差方向由具体游戏决定。

## MCTS 的 UCT 选择

选择阶段从已展开子节点中平衡平均回报和探索。父节点访问次数必须大于零，未访问子节点优先展开：

```cpp
Node* SelectChildUct(Node& parent, float exploration, float playerSign)
{
    Node* best = nullptr;
    float bestScore = -Infinity;
    for (Node& child : parent.children) {
        if (child.visits == 0) return &child;
        float exploit = playerSign * child.totalValue / child.visits;
        float explore = exploration
            * Sqrt(Log((float)parent.visits) / child.visits);
        if (exploit + explore > bestScore) {
            bestScore = exploit + explore;
            best = &child;
        }
    }
    return best;
}
```

本片段把所有totalValue存为根玩家收益，适用于双人零和决策节点。parent的行动者是根玩家时playerSign=+1，是对手时为-1；探索项始终非负。机会节点按概率采样，不套用对手最小化。回报视角必须统一。探索系数依赖回报量纲，不能跨项目直接照搬。用固定随机种子记录每次选择分数、访问次数和最终动作，能复现树搜索偏差。

## 四阶段与回报视角

固定一次迭代：从根复制状态，按UCT走到仍有未尝试动作的节点；选一个合法动作建立子节点；用模拟策略推进到终局或深度上限；把终局收益或叶估值回传到沿途节点。终局节点无需继续扩展，深度上限的估值与真实胜负要使用同一量纲。

回报约定可以选择根玩家视角。此时所有节点累计同一根玩家收益，但对手回合的利用项需取负号后再最大化探索分数，等价于倾向减少根收益。另一种做法为每条边存父节点行动者视角，每层选择都最大化，回传时按玩家身份换符号。两种都可成立，混用会让对手主动帮助根玩家。

```text
path = select_and_expand(root, copiedState)
valueForRoot = rollout_or_evaluate(copiedState)
for node in path:
    node.visits += 1
    node.totalValue += valueForRoot
choose final root action by the configured visit-count rule
```

伪代码中的选择沿正文UCT展开，模拟器由游戏合法转移提供。固定种子也不足以保证时间预算下重放一致：机器快慢会改变迭代次数。需要确定复现时固定迭代数、动作排序与随机消费顺序，在线时间预算则记录实际次数。

## 验证方法

固定局面与随机种子记录选择分数和访问数，与小规模穷举比较。预算递增观察收益曲线，不预设统一拐点；隐藏信息模拟只使用决策者允许知道的状态。


## 实现与证据

UCT为C++选择片段，四阶段是搜索协议。[Python参考模型](../examples/revision_16_21/review_reference.py)通过3项选择检查，覆盖根玩家最大化、对手最小化根收益与未访问优先；运行 `python 知识库/examples/revision_16_21/test_review_reference.py` 可复现。完整游戏模拟器与预算质量曲线尚未运行。

## 相关主题

- [[20_游戏AI/游戏AI决策模型]]
- [[16_编程与数据结构/图搜索]]
- [[20_游戏AI/群体战术信息]]
- [[20_游戏AI/游戏强化学习]]

## 参考资料

- [Kocsis与Szepesvári：Bandit Based Monte-Carlo Planning](https://www.cs.utexas.edu/~shivaram/readings/b2hd-KocsisSzepesvari2006.html)：UCT原论文书目信息与论文入口。
- [Browne等MCTS综述](https://repository.essex.ac.uk/4117/)：选择、扩展、模拟、回传与变体综述。
