# ComfyUI工作流

节点图能连通，只证明接口类型可接，不能证明模型和Latent语义匹配。ComfyUI工作流把模型、节点版本、参数与输入一起固定，再由队列保存执行和产物状态。失败恢复依赖这份记录。

## 工作流怎样可重复执行

### 基础图

典型 Text-to-Image：

```text
Checkpoint Loader
  -> Model -----------------> Sampler
  -> Text Encoder -> Positive/Negative Condition -> Sampler
  -> VAE -----------------------------------------> Decode

Empty Latent -> Sampler -> Denoised Latent -> VAE Decode -> Save
```

Checkpoint Loader 可能同时返回 Model、Text Encoder 和 VAE。工作流也可显式替换 VAE、加载多个 LoRA 或使用不同 Text Encoder。

线连通只表示类型兼容，不表示语义正确。错误 VAE、Control Model、Latent Format 或 Resolution 仍可能产出图像。

### Workflow 是管线资产

正式 Workflow 至少记录：

- Workflow ID/Version；
- ComfyUI Commit/Release；
- Custom Node Package 与 Commit；
- Model/VAE/LoRA/ControlNet 文件 Hash；
- 默认参数与允许覆盖范围；
- 输入/输出 Schema；
- 示例输入和 Golden Output；
- GPU/精度与已知兼容性；
- Owner、Review 与变更记录。

只保存截图无法重建节点、Widget 和连接。只保存 JSON 但不保存依赖版本，也可能因节点升级改变结果。

### 模型与路径

不要让 Workflow 依赖某台电脑的绝对路径。使用受控 Model Registry、逻辑 ID 和配置映射到本地缓存。

启动时校验需要的 Model Hash。名称相同但内容不同的文件不能视为同一依赖。

模型下载与许可应由独立步骤处理，生成 Worker 只读取批准 Registry。不要让 Custom Node 在执行中任意联网下载未知文件。

### Parameter Group

将常调参数集中为输入节点或 API Schema：

- Prompt/Negative Prompt；
- Seed；
- Width/Height/Batch；
- Step/CFG/Sampler/Scheduler；
- Denoise Strength；
- Control/IP-Adapter/LoRA Weight；
- Mask/Reference/Output Format。

节点内部散落的 Magic Number 很难审查。参数要有单位、范围和默认值，非法组合在排队前拒绝。

### Queue 与批处理

ComfyUI Server 可通过 API 提交 Workflow 和读取 History/Output。生产调度还需要外围 Job 状态：

```text
Pending -> Validating -> Queued -> Running
        -> Succeeded / Failed / Cancelled
```

Job 记录 Workflow Hash、Input Hash、Worker、GPU、开始结束时间和输出。相同 Job 是否复用缓存由管线明确决定，不能只依赖节点内部 Cache。

Batch 应限制并发、VRAM 和磁盘。OOM 后无限重试会持续挤占 Worker；可以降低 Batch/Resolution 或转到更大 GPU，但必须记录已改变参数。

### Custom Node 风险

Custom Node 本质是可执行代码。风险包括：

- 任意文件/网络访问；
- 依赖冲突和安装脚本；
- 更新后 API/结果变化；
- 无人维护或 License 不清；
- Pickle/Model 加载安全；
- 隐式修改全局环境。

生产环境使用白名单、固定 Commit、隔离环境和代码审查。升级先跑 Golden Workflow，不在工作日直接拉最新版本。

### 输出与 Metadata

输出文件名应来自 Job/Asset ID，不以 Prompt 直接拼接路径。Prompt 可能包含非法字符、隐私内容或过长文本。

Sidecar Manifest 保存：

- 完整 Workflow/参数；
- Model/Node Hash；
- Seed 与输入文件 Hash；
- 输出 Hash、分辨率、颜色空间；
- Parent Job/Variation；
- 审核状态和后处理记录。

图片 Metadata 可作为方便入口，但发布系统不应只依赖可能被编辑软件清除的嵌入字段。

## 失败恢复

- 保存每帧 Job/Condition/Seed/Model/Output；
- 单帧失败可重跑，不重算整段；
- OOM 可切 Worker 或降安全参数，并标记变更；
- 输出写 Staging，整段验证后发布；
- Custom Node 异常保留输入和 Stack；
- Keyframe 人工批准后锁定，传播任务不得静默覆盖。

## 验证方法

固定模型和节点hash跑Golden Workflow，比较输出与环境。测试缺模型、OOM、部分输出和重试，参数降级形成新的Variation。视频一致性属于独立问题，单帧种子不保证跨帧身份。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[17_AIGC与Agent管线/Agent资产管线]]
- [[17_AIGC与Agent管线/扩散模型]]
- [[17_AIGC与Agent管线/视频生成时序一致性]]

## 参考资料

- ComfyUI Official Documentation.
- Hugging Face Diffusers video and image-to-image documentation.
- Rerender A Video and TokenFlow papers，视频重绘与特征传播参考。
- Optical Flow and temporal reprojection literature.
