# 编程、物理与网络机制实验

使用Python3.11及以上版本，只依赖标准库。从仓库根目录运行：

```powershell
python 知识库/examples/revision_16_21/test_reference.py
```

`reference.py`提供四时间戳、16位序号比较、带墙面约束的输入重放、历史区间插值、射线与球求交、SQLite事务幂等、回滚状态恢复、XPBD距离约束、支撑连通图、轮胎合力限幅、单面滑动和临时文件发布。`test_reference.py`保存输入与预期，失败会返回非零退出码。

2026-10-22，本机Python3.11执行17项检查通过。SQLite与文件测试使用独立临时目录，结束后清理。文件发布实验验证替换结果及提交前异常，不模拟断电；SQLite实验验证事务回滚、重复请求与载荷冲突，不模拟多机投递。

数学模型只覆盖测试中的简化条件。射线方向为单位向量，球半径非负；网络序号活动跨度小于32768；输入命令按生成顺序保存。XPBD实验使用一维距离约束，重合粒子明确拒绝。滑动法线指向障碍外侧并已归一化，轮胎摩擦系数与载荷均非负。

真实Socket、引擎物理、跨平台确定性、GPU执行和性能测量分别由目标工程验收。本目录没有给出这些环境的运行结果。

## 独立复核实验

`review_reference.py`提供固定宽度分配范围、快照接纳、UCT收益视角和有限键值GOAP模型。运行：

```text
python 知识库/examples/revision_16_21/test_review_reference.py
python 知识库/examples/revision_16_21/verify_event_queue.py
```

前一命令的15项检查分别覆盖分配器5项、快照版本4项、UCT3项和GOAP3项。后一命令需要.NET 9 SDK，从当前文章提取C#事件队列片段并编译运行4项检查；构建输出写入build/event-queue。模型不分配真实原生内存、不运行完整NPC搜索树，也不连接网络或Unity。`independent-results.json`保存实际命令、返回码与输出，包括SDK目标不匹配的诊断及适配当前SDK后的结果。
