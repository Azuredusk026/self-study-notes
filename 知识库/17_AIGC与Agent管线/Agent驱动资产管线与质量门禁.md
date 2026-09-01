# Agent 驱动资产管线与质量门禁

Agent 管线不是让模型自由操作项目。它把模型放进受控状态机：读取任务、生成结构化计划、调用有限工具、验证结果、记录状态，并在无法安全处理时交给人。

## 适合 Agent 的任务

适合：

- 读取需求并生成候选 Plan；
- 从批准资产库检索与标注；
- 批量调用已有 DCC/引擎工具；
- 汇总 Validator 结果；
- 生成 Caption、Tag、命名或报告初稿；
- 根据明确规则修复低风险问题；
- 对失败项分类并安排重试。

不应让 Agent 单独决定：

- 来源/授权不明内容进入正式资产；
- 删除或覆盖大量源文件；
- 修改质量门禁以通过检查；
- 视觉方向和关键 Hero Asset 最终批准；
- 使用未批准的外部服务、模型或数据。

模型适合处理模糊语义，确定性脚本适合执行规则。二者应组合，而不是互相替代。

## 状态机

明确状态比“Agent 记得自己做到哪里”可靠：

```text
Received
 -> Parsed
 -> Planned
 -> PlanValidated
 -> Executing
 -> TechnicalValidation
 -> VisualReview
 -> Approved / Rework / Failed / Cancelled
```

每次 Transition 有前置条件、输入、输出和责任。状态保存在数据库/Manifest，不只存在对话 Context。

长任务中断后从持久化状态恢复。模型 Context 可以重新构建，资产事实不能依赖聊天历史。

## Job 与 Artifact

Job Record：

- Job/Task/Project ID；
- Request、约束、Target Platform；
- Workflow/Agent/Prompt Version；
- Tool Permission；
- Current State/Attempt；
- Input/Output Artifact ID；
- Validation/Review；
- Cost、时间和 Owner。

Artifact Record：

- Stable ID/Version/Hash；
- Parent/Derived-from；
- Source/License/Consent；
- Generator Model/Tool；
- Prompt/Seed/Workflow；
- DCC/Edit/Import History；
- Publish State。

这条链就是数据血缘（Data Lineage）。它支持复现、撤回、版权审计和影响分析。

## 角色提示词

一个巨大 Prompt 同时规划、执行和审核，容易让模型边做边改标准。按职责分角色：

**需求解析角色**

- 把自然语言转成结构化 Brief；
- 提取尺寸、风格、平台、预算和交付格式；
- 标出缺失/冲突，不自行编造关键需求。

**场景规划角色**

- 生成房间区域、功能、动线、Anchor 和约束；
- 输出 Schema，不直接摆资产。

**资产选择角色**

- 只从批准 Catalog 检索；
- 根据尺寸、Tag、风格、License 和预算排序候选；
- 返回 Asset ID 与理由，不返回未知网络链接。

**布局执行角色**

- 调用 Spawn/Transform/Group 等受控工具；
- 遵守单位、坐标、碰撞和命名；
- 不修改规划之外的资产。

**验证角色**

- 只读取结果和既定标准；
- 检查碰撞、可达性、穿插、预算、缺失依赖和视觉问题；
- 不通过时给结构化 Rework，不直接降低标准。

角色分离的重点是权限和输入输出，不是让多个模型互相聊天。

## Prompt Contract

每个角色提示词应包含：

- Role/Responsibility；
- Allowed Inputs/Tools；
- Forbidden Action；
- Output JSON Schema；
- Decision Criteria；
- Failure/Uncertainty 表达；
- 少量有效示例；
- Prompt Version。

输出必须经 Schema Validator。无法解析时要求同一角色修正格式，不把残缺文本交给下游猜。

Prompt 中不要混入会随任务变化的巨大资产清单。通过检索工具按 Query 返回有限候选，减少 Context 和陈旧数据。

## 工具接口

工具应小而确定：

- `search_assets(query, constraints)`；
- `get_asset_metadata(asset_id)`；
- `spawn_asset(asset_id, transform, parent)`；
- `move_asset(instance_id, transform)`；
- `validate_scene(scene_id, ruleset)`；
- `render_preview(camera_id, preset)`；
- `publish_staging(job_id)`。

参数使用 Stable ID、结构化 Transform 和单位，不让模型拼任意脚本字符串。

返回值包含 Result、Changed Artifact、Warnings、Error Code 和 Retryability。工具只做一个职责，便于权限、测试和幂等。

## 权限

按最小权限授予：

- Planner 只读需求和 Catalog；
- Executor 只写 Job Staging Scene；
- Validator 只读结果并写报告；
- Publisher 只有在门禁通过且人类批准后才能切换正式版本。

文件系统限定项目 Staging；网络使用域名/API 白名单；Secret 不进入 Prompt/Log。删除、覆盖、发布和外部上传属于高风险动作，应由确定性 Policy Gate 控制。

## Orchestrator

Orchestrator 负责：

- 状态转换；
- 选择角色和工具；
- Timeout/Retry/Cancel；
- 并发与配额；
- Artifact/Log 持久化；
- Human Review；
- 最终发布/回滚。

不要让 LLM 自己决定所有调度。确定的流程用代码/Workflow Engine，模型只处理需要推理的节点。

## 幂等

工具接收 `operation_id`。同一 ID 重试时返回已有结果，不重复 Spawn 或发布。

Create 操作先生成 Stable Target ID；写入 Staging；成功后记录 Operation Result。网络超时后客户端可查询状态，而不是直接再发一次创建。

布局更新可使用 Desired State：Agent 输出完整目标布局或 Patch，Executor 比较当前状态后只应用差异。这样重跑不会叠出两套家具。

## 错误分类

- Validation Error：输入/资产不符合规则，修正后重试；
- Transient Tool Error：服务忙、网络短断，指数退避有限重试；
- Capacity Error：VRAM/磁盘/配额不足，换 Worker 或降批准参数；
- Model Output Error：Schema 不合法或缺字段，重新生成；
- Policy Error：权限、License 或来源问题，不自动绕过；
- Deterministic Tool Bug：相同输入稳定失败，停止并上报；
- Partial Write：执行补偿/回滚，再决定重试。

“失败就再问一次模型”会重复确定性错误并增加成本。

## Retry 与 Backoff

Retry Policy 记录 Max Attempt、Backoff、Jitter、可重试 Error Code 和总 Deadline。

每次重试复用同一 Operation ID，并保存 Attempt。若改变 Model、Prompt、Seed、Resolution 或资产候选，这已经是新 Variation，不是相同任务重试。

超过阈值进入 Dead-letter/Rework Queue，保留输入和诊断供人处理。

## Compensation 与回滚

跨工具操作通常没有分布式原子事务。使用 Saga/Compensation：

1. 创建 Staging Scene；
2. Spawn Asset；
3. 生成 Lighting/Preview；
4. Import/Validate；
5. 发布。

每步记录补偿：删除 Staging Instance、释放临时资源、恢复旧 Publish Pointer。补偿也要幂等。

源文件修改优先生成新版本，不原地覆盖。Git/Perforce 历史是恢复手段，但不能代替当前任务的明确回滚。

## 室内场景的结构化规划

Agent 驱动房间搭建可使用中间 Schema：

```text
Room
  zones[]
  anchors[]
  pathways[]
  placements[]
  lighting_intent
  constraints
```

先生成房间功能区和通道，再检索匹配尺寸的资产，最后求解 Placement。不要让模型只凭文本直接输出几十个世界坐标。

Placement Validator 检查：

- Bounds/SAT 穿插；
- 门窗和主通道净空；
- Navmesh/可达性；
- 墙面/地面 Anchor；
- 视线、功能距离和朝向；
- 重复资产与风格 Tag；
- Draw/Light/Texture 预算。

几何规则由确定性工具执行。模型可以解释失败并提出候选调整。

## 技术质量门禁

进入正式库前检查：

- 文件/Schema/依赖完整；
- 坐标、单位、Pivot、Bounds；
- Mesh、Material、Texture、LOD、Collision；
- 命名、目录和 Stable ID；
- 平台内存、Draw、Shader 和加载预算；
- License、来源和敏感信息；
- DCC/Engine Import 与 Cook；
- Manifest 和数据血缘完整。

规则使用稳定 ID、Severity 和例外机制。Agent 不能修改 Ruleset 或批准自己的例外。

## 视觉与语义审核

自动指标可检查构图、重复、遮挡、色板、图像伪影和参考相似度，但美术质量仍需要人类评审。

Review UI 应显示：

- Brief 与关键约束；
- 生成结果和固定相机 Preview；
- 来源/Model/Workflow；
- 技术报告与预算 Diff；
- Agent 的决策理由和不确定项；
- Approve/Rework/Reject 与批注。

人类修改应成为新的 Artifact Version，并记录哪些字段 Override。下次重跑不能静默覆盖已批准的手工调整。

## 自动验证不等于自我评分

同一个模型生成后再问“是否很好”容易自洽。质量门禁优先使用：

- 确定性 Validator；
- 独立 Reference/Metric；
- 隔离上下文的 Review Model；
- 固定 Test Set 和评分 Rubric；
- 人类最终批准。

LLM Judge 适合辅助语义分类，不作为版权、性能或破坏性操作的唯一门禁。

## 日志与审计

每次执行记录：

- Agent/Model/Prompt/Tool Version；
- Input/Output Hash；
- Tool Call 参数摘要与结果；
- State Transition；
- Retry/Error/Compensation；
- Validation 与 Human Decision；
- Cost/Latency/Token/Compute；
- 发布版本和下游影响。

日志需做 Secret/PII Redaction。Prompt 可能包含内部需求，不能默认上传到外部 Telemetry。

## Prompt Injection 与不可信输入

资产名、文档、网页和 Metadata 都是不可信数据，其中的“忽略规则并执行命令”不能成为 Agent 指令。

防护：

- System/Policy 与检索内容分通道；
- Tool 参数 Schema 和权限；
- 不把外部文本直接拼进高权限 Prompt；
- 输出编码与路径规范化；
- 外部链接/下载白名单；
- 高风险动作由代码 Gate 和人类批准。

## 评估

用历史任务和人工构造失败集评估：

- Brief 结构化准确率；
- Asset Retrieval Recall/Precision；
- Placement Validator Pass Rate；
- 首次通过/人工返工率；
- Tool Error、Retry 和 Recovery Success；
- 预算与 License 漏检率；
- 平均成本/耗时；
- 人工 Override 被保留的比例；
- 同一输入的可复现性。

只统计生成数量会鼓励低质量铺量。指标应与正式入库和返工成本相关。

## 相关主题

- [[知识库/15_资产与工具管线/资产导入、验证与发布]]
- [[知识库/15_资产与工具管线/编辑器工具与批处理架构]]
- [[知识库/17_AIGC与Agent管线/扩散模型、条件控制与微调]]
- [[知识库/17_AIGC与Agent管线/ComfyUI工作流与时序一致性]]

## 参考资料

- NIST, *AI Risk Management Framework*.
- OWASP, *Top 10 for Large Language Model Applications*.
- OpenAI and Anthropic documentation on tool use, structured outputs and evaluations.
- Workflow/Saga, data lineage and MLOps engineering references.
