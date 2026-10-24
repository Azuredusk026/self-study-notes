# 个人游戏开发知识库

这是一套以原理、机制和工程验证为核心的个人 Obsidian 知识库。

内容覆盖图形学、游戏引擎、编程、算法、物理、Gameplay、游戏 AI、网络、工具管线和 AIGC。相关概念按主要技术问题组织，重点解释问题来源、执行机制、工程代价与验证方法。

正式知识位于 `知识库/` 下编号 00 至 26 的目录，共 214 篇主题内容，其中 196 篇专题、18 篇导读；另有 5 篇说明，总计 219 页。

## 入口

- [知识地图](知识库/00_知识库说明/知识地图.md)：领域目录与工程阅读路线。
- [学习与维护方法](知识库/00_知识库说明/学习与维护方法.md)：阅读、补充、来源和验证规则。
- [术语表](知识库/00_知识库说明/术语表.md)：统一叫法与检索入口。

## 知识结构

- `01–12`：数学、GPU 与光栅化、Shader、光照、纹理、后处理、几何、动画、VFX、风格化渲染和光线追踪。
- `13–17`：渲染架构、性能、资产与工具管线、编程和 AIGC。
- `18–21`：游戏物理、Gameplay、游戏 AI 和游戏网络。
- `22–26`：渲染引擎实现、运行系统、音频、UI 与 GPU 驱动几何。

## 阅读方式

使用 Obsidian 打开仓库根目录，从知识地图进入。需要定向查找正式文章时使用：

```text
path:"知识库" 关键词
```

导读帮助读者选择专题；专题展开机制、实现、成本和失效条件。“相关主题”连接必要的前置知识、执行依赖、对照技术和延伸内容。

## 仓库内容

Git 仓库发布 README、`知识库/`、`skills/` 与 `AGENTS.md`。知识库配套的正式样例、图源和资产登记随正文发布；`docs/`、课程来源、`scripts/`、`CHANGELOG.md` 和机器缓存用于本机维护。

## 作者标准与验收

- [技术中文写作规范](知识库/00_知识库说明/技术中文写作规范.md)：以输入、动作和因果组织解释。
- [知识库实施规范](知识库/00_知识库说明/知识库实施规范.md)：文章边界、命名、归属与九维验收。
- [描边](知识库/11_NPR与风格化渲染/描边.md)：机制推理、代码上下文和分层验证的文风标杆。

项目技能位于 `skills/`，分别维护粒度、写作、事实与技术图代码。文章按主问题和行业习惯命名，正文深度由机制、实现和证据共同判断。

[范围与证据报告](skills/kb-structure-audit/references/revision-report.md)记录全文复读和验收范围；[逐篇质量矩阵](skills/kb-structure-audit/article-quality-matrix.json)记录九个维度的状态、依据及 `revision_review`。规范核对、数学实验、代码编译、引擎运行、帧捕获和性能测量分别登记，阅读结论时以该项实际证据为准。

[机制深度复读记录](skills/kb-structure-audit/references/depth-review-report.md)记录按正文独立推演要求进行的逐篇审查、问题与修订，进度和实际证据分别登记。

[保留文章逐机制复读记录](skills/kb-structure-audit/references/retained-review-report.md)记录48篇保留文章的机制审查、具体反例与实际验证范围。

[主要机制与衔接复读记录](skills/kb-structure-audit/references/chain-review-report.md)记录48篇文章的完整机制交接、最终反例、当前正文与实际验证范围。

[跨机制接口复读记录](skills/kb-structure-audit/references/interface-review-report.md)记录40篇文章的接口推演、失败反例与分阶段证据。

[执行规则复读记录](skills/kb-structure-audit/references/execution-review-report.md)记录30篇文章的统一执行规则、正文顺序与恢复反例。

[执行语义与恢复接口复读记录](skills/kb-structure-audit/references/semantic-review-report.md)记录18篇文章的消费接口、取消传播、恢复状态和全文反证。

[连续执行与恢复复读记录](skills/kb-structure-audit/references/continuity-review-report.md)记录15篇文章的连续案例、补偿承接、异步消费与恢复反例。

[冲突续行与决策重放复读记录](skills/kb-structure-audit/references/resume-review-report.md)记录13篇文章的跨对象版本、并发析构、异步决策重放及全文反证。

[未交付命令与二次回放复读记录](skills/kb-structure-audit/references/delivery-review-report.md)记录13篇文章的命令续行、恢复记录消费、读取版本及全文反证。
