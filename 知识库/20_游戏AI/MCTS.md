# MCTS

候选动作很多，写固定评分可能难以覆盖长远后果。MCTS反复选择、扩展、模拟并回传，让预算集中到有希望或尚不确定的分支。回报视角和状态复制成本决定搜索能否可靠运行。

## MCTS

Monte Carlo Tree Search 反复执行 Selection、Expansion、Simulation、Backpropagation。Selection 常用 UCT 平衡已知收益与探索：

$$UCT_i=\bar X_i+C\sqrt{\frac{\ln N}{n_i}}$$

$\bar X_i$ 是子节点平均收益，$N$ 是父节点访问次数，$n_i$ 是子节点访问次数。$C$ 越大越偏探索。Expansion 添加未尝试动作，Simulation 用简化策略推演，最后把结果沿路径回传。

UCT 是 UCB 思想在树搜索中的应用。PUCT 再引入策略网络给出的先验概率，让高先验动作更早得到探索，同时仍随访问次数调整探索奖励。先验只能引导搜索，最终质量仍取决于模拟、价值估计和访问预算。

MCTS 适合规则可模拟、分支较大且无法预先写出完整评估的决策。其质量依赖状态复制成本、模拟速度和奖励设计。实时游戏要限制迭代数或时间，使用固定随机种子时才能稳定重放。隐藏信息游戏还需避免在模拟中偷看真实状态。

先测量单次模拟耗时，再确定实时预算允许的迭代数。搜索质量随预算变化的曲线依赖游戏、模拟策略和局面，需要用固定测试集测量，不能预设统一的对数增长规律。

隐藏信息的一种近似是确定化采样：从当前信息允许的完整状态中采样，再分别搜索并汇总结果。它容易产生策略融合，例如把不同隐藏状态下各自可行的动作组合成实际无法执行的策略。应与信息集搜索对比，并检查是否使用了决策者无法观察的信息；偏差方向由具体游戏决定。

## MCTS 的 UCT 选择

选择阶段从已展开子节点中平衡平均回报和探索。父节点访问次数必须大于零，未访问子节点优先展开：

```cpp
Node* SelectChildUct(Node& parent, float exploration)
{
    Node* best = nullptr;
    float bestScore = -Infinity;
    for (Node& child : parent.children) {
        if (child.visits == 0) return &child;
        float exploit = child.totalValue / child.visits;
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

回报视角必须统一：双人零和游戏在回传层级切换时常需要翻转符号。探索系数依赖回报量纲，不能跨项目直接照搬。用固定随机种子记录每次选择分数、访问次数和最终动作，能复现树搜索偏差。

## 验证方法

固定局面与随机种子记录选择分数和访问数，与小规模穷举比较。预算递增观察收益曲线，不预设统一拐点；隐藏信息模拟只使用决策者允许知道的状态。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[20_游戏AI/游戏AI决策模型]]
- [[16_编程与数据结构/图搜索]]
- [[20_游戏AI/群体战术信息]]
- [[20_游戏AI/游戏强化学习]]

## 参考资料

- Sutton and Barto, *Reinforcement Learning: An Introduction*.
- Browne et al., *A Survey of Monte Carlo Tree Search Methods*.
- Millington and Funge, *Artificial Intelligence for Games*.
- Silver et al., *Mastering the Game of Go with Deep Neural Networks and Tree Search*（策略网络与 MCTS 结合的开山之作，Nature 2016）.
- Vinyals et al., *Grandmaster Level in StarCraft II Using Multi-agent Reinforcement Learning*（AlphaStar，部分可观察与长时序问题的工程样本，Nature 2019）.
- Berner et al., *Dota 2 with Large Scale Deep Reinforcement Learning*（OpenAI Five，连续控制与联盟式训练）.
