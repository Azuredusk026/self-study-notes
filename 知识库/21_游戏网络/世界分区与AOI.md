# 世界分区与AOI

玩家只需要附近和玩法相关对象，完整世界复制会耗尽带宽。AOI用空间与关系筛选，跨服务器移动再交接状态和路由。复制范围与权威迁移是两个层次，边界切换都需要稳定身份。

## AOI 与世界分区

Area of Interest 只把相关实体复制给玩家。可按 Grid、Quadtree、动态区域或玩法关系筛选，再按距离和重要性分配带宽。进入和离开 AOI 要有稳定的 Spawn/Despawn 语义，边界抖动可加迟滞。

大型世界可按 Zone、Shard 或 Instance 划分。跨区对象需要 Ghost/Proxy 表示相邻区域状态。玩家跨服务器时，源服冻结可迁移状态，目标服确认接管，再切换路由。这个过程很难做到任意物理对象和战斗交互完全无缝，因此边界通常放在门、传送或低交互区域。

跨服迁移按三阶段执行：源服冻结玩家状态并生成带版本号与所有权 epoch 的迁移包；目标服加载、校验后回执；路由层切换完成，源服才释放资源。任何一步超时都要有回到源服的回滚路径。迁移期间到达的该玩家输入要排队，切换完成后按序补发，否则技能请求会在交接缝隙里丢失。

跨区事务应有唯一 ID、幂等处理和补偿流程。分布式系统里网络超时不能说明对方一定没执行，盲目重试会复制物品或重复扣费。

## 基于网格的 AOI 查询

实体按二维世界位置进入固定尺寸 Cell。查询只遍历观察者周围覆盖视距的 Cell，再做精确距离判断：

```cpp
CellKey ToCell(Vec2 p) { return Floor(p / cellSize); }

void QueryAoi(Vec2 center, float radius, Vector<EntityId>& out)
{
    CellKey minCell = ToCell(center - Vec2(radius));
    CellKey maxCell = ToCell(center + Vec2(radius));
    for (int y = minCell.y; y <= maxCell.y; ++y)
        for (int x = minCell.x; x <= maxCell.x; ++x)
            for (EntityId id : cells[{x, y}])
                if (DistanceSquared(position[id], center) <= radius * radius)
                    out.push_back(id);
}
```

实体跨 Cell 时要原子地更新旧桶和新桶，断线或迁移时也要清理成员。Cell 太小会增加桶遍历和迁移，太大又会增加精确过滤。验证时统计每次查询访问的 Cell、候选数、最终实体数和跨区迁移次数。

## 验证方法

全量遍历与网格查询比较集合，测试负坐标、边界与迁移清理。跨服每个故障点检查epoch和唯一权威，迁移输入按序缓冲，超时不能直接让两端同时继续。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[21_游戏网络/对局服务器架构]]
- [[16_编程与数据结构/空间索引]]
- [[21_游戏网络/服务端反作弊校验]]

## 参考资料

- Michael Nygard, *Release It!*（容量、稳定性与降级模式）.
- Martin Kleppmann, *Designing Data-Intensive Applications*（一致性、幂等与分区的系统参照）.
- Gaffer on Games, networking article series.
- Thor Alexander (ed.), *Massively Multiplayer Game Development*（MMO 分区、迁移与服务拆分的早期系统整理）.
