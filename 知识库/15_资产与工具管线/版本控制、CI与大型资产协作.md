# 版本控制、CI 与大型资产协作

游戏项目同时包含文本源码和不可合并的二进制资产。版本控制方案要解决历史、带宽、锁、分支、权限和构建，不只是“能提交大文件”。

## 文本与二进制的差异

代码、JSON、YAML 等文本可以 Diff 和 Merge。`.psd`、`.blend`、`.mb`、贴图、音频等二进制通常只能整体替换。

两人同时编辑同一二进制时，最后必须选一个版本或人工在 DCC 重做合并。工具无法凭字节差异理解“保留 A 的角色、B 的灯光”。

因此协作策略包括：

- Exclusive Lock；
- 按资产/关卡/图层拆分文件；
- Ownership 与任务划分；
- 在可组合格式中使用 Layer/Reference；
- 尽早同步和短生命周期分支。

## Git 的对象历史

普通 Git Clone 会获得分支可达历史对象。大二进制每次更新都产生新 Blob，即使删除当前文件，历史仍持续占空间。

Git 擅长分支与文本合并，但大型资产库会遇到 Clone、Fetch、Checkout 和仓库维护成本。只把 ZIP 提交进 Git 不能获得增量或可审查历史。

## Git LFS

Git LFS 用小型 Pointer File 替代 Git 中的大文件内容，真实对象存储在 LFS Server。`.gitattributes` 决定哪些 Pattern 经过 LFS Filter。

Pointer 大致记录 Version、Object ID 和 Size。Checkout 时 Smudge/Filter 下载真实内容。

它解决 Git 主对象库被大文件快速撑大的问题，但不自动解决：

- 二进制 Merge；
- 服务器存储与带宽配额；
- 已经以普通 Git 提交的大文件历史；
- CI 是否拉取 LFS；
- 文件锁流程；
- 海量小文件的 Metadata/Checkout 开销。

`.gitattributes` 应在大文件首次提交前配置并进入版本控制。把历史迁移到 LFS 会重写 Commit ID，需要团队统一计划，不能个人随意执行。

## Git LFS Lock

对不可合并格式可启用 Lockable。用户编辑前锁文件，提交后解锁。工具可在 DCC 打开/保存时显示锁 Owner。

锁是协作协议，不是完整权限系统。离线编辑、绕过客户端或强制解锁仍可能产生冲突。团队要定义：谁能强制解锁、请假/离职锁如何处理、锁多久提醒。

## Perforce Helix Core

Perforce 是集中式 Version Control，常用于大型游戏资产。基本概念：

- Depot 保存版本；
- Workspace 映射本地文件；
- Changelist 组织一次提交；
- File Type 可设置 Binary、Text、Exclusive Lock；
- Stream 组织主线与分支；
- Shelve 用于共享未提交改动和 Review。

集中式模型便于权限、锁和大型二进制管理。成员可以只同步 Workspace View 需要的目录，不必获得全部历史内容。

代价是服务器运维、网络依赖、Workspace/Stream 规则和管理员治理。错误的 View 或大规模自动 Reconcile 也会制造大量无关变更。

## PlasticSCM / Unity Version Control

PlasticSCM（Unity Version Control）提供 Changeset、Branch、Merge、Lock 和面向非程序用户的 Gluon 工作流。Gluon 允许用户选择性下载和提交，不要求理解完整分支模型。

它适合需要分支能力、同时有大量美术成员的团队。实际采用前需要验证：

- 云/自建服务与区域网络；
- 大文件存储和计费；
- Lock Rule；
- Unity/IDE/DCC 集成；
- CI CLI 和 Service Account；
- 分支/合并与美术日常流程。

工具名称、许可证和服务能力可能变化，应以当前官方文档为准。

## 选择方案

不是简单按团队人数决定。要测：

- 资产总量、日增量和单文件大小；
- 文本/二进制比例；
- 分支与 Release 数量；
- 地域、网络和远程办公；
- 锁的频率与粒度；
- 权限与外包隔离；
- CI/Build Farm 并发；
- 备份、灾备、审计和成本。

用真实项目样本做 Clone/Sync、Switch、提交、锁、CI 和恢复演练，比根据宣传功能表选择可靠。

## 文件粒度

版本控制无法弥补不合理的资产结构。一个 20 GB 单体 Level 会让锁和提交都难以并行。

可拆分：

- World Partition/Level Instance/Sublevel；
- Prefab/Blueprint/Scene Object；
- USD Layer/Reference；
- 材质、模型、动画与贴图独立资产；
- 配置与生成缓存分离。

拆得过细又会增加引用、加载和文件数量。边界应对应 Ownership、并行编辑和运行时职责。

## Generated File

Generated/Derived Data 分三类：

- 可快速确定重建：忽略并缓存；
- 重建昂贵但确定：共享 Build Cache/Artifact；
- 不可稳定重建或需要审查：作为正式资产版本化。

忽略规则、LFS Pattern 和 Build Output 目录要由管线维护。个人临时文件、Autosave、Library/DerivedDataCache 不应进入提交。

## 资产 CI

一次资产变更可执行：

1. Checkout 正确 Commit/Changelist 和 LFS/Depot 内容；
2. 恢复锁定的工具与依赖版本；
3. 计算受影响资产；
4. 运行 Validator/Importer/Cook；
5. 比较预算、引用和 Golden Result；
6. 发布 Report、Artifact 和 Manifest；
7. 失败时阻止合入或发布。

CI 要使用专用 Service Account，最小权限，并处理 DCC/Engine License。不要把个人账号和 Token 写进脚本。

## 缓存

DCC 转换、纹理压缩、Shader Compile 和 Cook 都昂贵。Cache Key 应包含 Source Hash、Settings、Tool Version、Platform 和 Dependency。

缓存命中结果仍要验证 Metadata。错误 Cache Key 会复用过期产物，比没有缓存更难查。

缓存应有容量、淘汰、命中率和污染恢复策略。CI 日志记录 Cache Hit/Miss 及耗时，才能判断收益。

## 变更范围与依赖

只检查本次直接修改文件可能漏掉下游。Texture 改变会影响 Material、Prefab、Level 和 Bundle。需要 Asset Dependency Graph 或 Import Database 计算受影响集合。

全库检查最可靠但反馈慢。实践中：

- Pre-submit 检查直接资产和关键反向依赖；
- Merge CI 构建受影响 Bundle/Scene；
- Nightly 做全库 Cook 与预算扫描；
- Release 做目标平台完整构建。

## 分支、主干与合入队列

二进制资产不适合长期分支。两个分支分别修改同一场景或源文件，数周后几乎无法自动合并。资产团队通常更适合短生命周期任务分支、频繁同步主干和明确锁定。

一次 Changelist/Changeset 应表达一个可审查工作单元。模型、贴图、材质和引用调整若共同构成同一交付，应一起提交，避免主干出现“模型已换但材质还没来”的中间状态。

大型团队可使用 Merge Queue：候选变更先在目标主干最新状态上 Rebase/Merge，运行 Validator、Cook 和测试，通过后再按队列合入。这样减少多个“各自在旧主干上通过 CI”的变更连续合入后互相破坏。

Release Branch 要限制内容回灌。修复应有明确 Cherrypick/Integrate 记录，避免同一二进制在主干和发布分支被独立修改后无法判断哪个是权威版本。

## 二进制资产审查

Code Review 页面看不到 `.fbx` 或 `.uasset` 的有意义 Diff。管线可以自动生成 Review Artifact：

- 前后 Turntable/Screenshot/Video；
- Bounds、Vertex、Material、Bone、Texture 和内存差异；
- 引用增加/删除与 Bundle 影响；
- Validator 结果和预算变化；
- DCC Source、Importer Setting 和工具版本；
- Scene/Prefab 的结构化语义 Diff。

Perforce Shelve、Git PR Artifact 或 Plastic Changeset Preview 都可承载这些结果。审查者关注视觉和数据变化，而不是对无法阅读的二进制文件直接批准。

自动截图要固定相机、灯光、曝光、背景和引擎版本。否则环境变化会制造无意义 Diff。

## 锁与任务系统

锁信息应出现在 DCC/Editor 内，而不是等保存失败才发现。资产面板可以显示 Owner、任务、分支、锁时间和联系方式。

锁最好与任务边界一致：一个人负责角色 Mesh，另一人仍可编辑独立动画和材质。若所有内容嵌在一个源文件里，锁粒度只能粗化，这也是拆分源资产的理由。

长时间锁应自动提醒，但不能在用户仍有未提交修改时自动释放。强制解锁前先联系 Owner、保存 Shelve/备份，并留下审计记录。

## 跨职能合作

技术规则要和美术、策划、程序共同制定。有效流程：

1. 用实际失败案例和性能数据说明问题；
2. 定义可交付结果与责任边界；
3. 先提供本地快速检查和清楚修法；
4. 再把同一规则放入 CI 门禁；
5. 对合理例外设置 Owner 和到期时间；
6. 统计高频失败，优先改工具而不是反复培训。

冲突不应只靠“谁的职位高”。区分视觉目标、技术约束、排期和工具缺口，用可复现测试讨论取舍。

## 故障与恢复

- 定期验证 Server Backup 可恢复，不只确认备份任务成功。
- 演练误删、错误提交、锁遗留和 LFS 对象缺失。
- CI Artifact 有保留期与不可变版本号。
- Release 使用 Tag/Label/Changelist + Manifest 可复现。
- 大规模迁移先在镜像库验证，并冻结写入窗口。

版本控制不是备份的替代品。权限误操作、服务器损坏和恶意删除都需要独立备份与审计。

## 验证清单

- 新成员从空机器完成 Sync、工具安装、打开项目和首次构建。
- 两名用户测试 Lock/冲突/强制解锁和二进制恢复。
- CI 验证 LFS/Perforce/Plastic 内容完整，不接受 Pointer 当真实资产。
- 模拟 Cache Miss 和服务不可用，确认错误清楚且不发布残缺结果。
- 测试分支切换、场景拆分、Shelve/Review 和 Release 回滚。
- 统计同步时间、仓库/Depot 增长、LFS 带宽、Cache 命中与构建时长。

## 相关主题

- [[知识库/15_资产与工具管线/资产导入、验证与发布]]
- [[知识库/15_资产与工具管线/编辑器工具与批处理架构]]
- [[知识库/17_AIGC与Agent管线/Agent驱动资产管线与质量门禁]]

## 参考资料

- Git LFS Documentation, *Pointer files*, *Tracking* and *Locking*.
- Perforce Helix Core Documentation, *Streams*, *File types*, *Shelving* and *Protections*.
- Unity Version Control Documentation, *Branches*, *Locks* and *Gluon*.
- Unity and Unreal Engine build automation and asset pipeline documentation.
