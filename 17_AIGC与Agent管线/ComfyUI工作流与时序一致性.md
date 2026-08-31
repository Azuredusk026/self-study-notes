# ComfyUI 工作流与时序一致性

ComfyUI 把模型加载、条件、采样、解码和后处理显式组织成节点图。它适合作为可复现生成管线，但前提是把 Workflow、Model、Custom Node、输入和输出一起版本化。

## 基础图

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

## Workflow 是管线资产

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

## 模型与路径

不要让 Workflow 依赖某台电脑的绝对路径。使用受控 Model Registry、逻辑 ID 和配置映射到本地缓存。

启动时校验需要的 Model Hash。名称相同但内容不同的文件不能视为同一依赖。

模型下载与许可应由独立步骤处理，生成 Worker 只读取批准 Registry。不要让 Custom Node 在执行中任意联网下载未知文件。

## Parameter Group

将常调参数集中为输入节点或 API Schema：

- Prompt/Negative Prompt；
- Seed；
- Width/Height/Batch；
- Step/CFG/Sampler/Scheduler；
- Denoise Strength；
- Control/IP-Adapter/LoRA Weight；
- Mask/Reference/Output Format。

节点内部散落的 Magic Number 很难审查。参数要有单位、范围和默认值，非法组合在排队前拒绝。

## Queue 与批处理

ComfyUI Server 可通过 API 提交 Workflow 和读取 History/Output。生产调度还需要外围 Job 状态：

```text
Pending -> Validating -> Queued -> Running
        -> Succeeded / Failed / Cancelled
```

Job 记录 Workflow Hash、Input Hash、Worker、GPU、开始结束时间和输出。相同 Job 是否复用缓存由管线明确决定，不能只依赖节点内部 Cache。

Batch 应限制并发、VRAM 和磁盘。OOM 后无限重试会持续挤占 Worker；可以降低 Batch/Resolution 或转到更大 GPU，但必须记录已改变参数。

## Custom Node 风险

Custom Node 本质是可执行代码。风险包括：

- 任意文件/网络访问；
- 依赖冲突和安装脚本；
- 更新后 API/结果变化；
- 无人维护或 License 不清；
- Pickle/Model 加载安全；
- 隐式修改全局环境。

生产环境使用白名单、固定 Commit、隔离环境和代码审查。升级先跑 Golden Workflow，不在工作日直接拉最新版本。

## 输出与 Metadata

输出文件名应来自 Job/Asset ID，不以 Prompt 直接拼接路径。Prompt 可能包含非法字符、隐私内容或过长文本。

Sidecar Manifest 保存：

- 完整 Workflow/参数；
- Model/Node Hash；
- Seed 与输入文件 Hash；
- 输出 Hash、分辨率、颜色空间；
- Parent Job/Variation；
- 审核状态和后处理记录。

图片 Metadata 可作为方便入口，但发布系统不应只依赖可能被编辑软件清除的嵌入字段。

## 时序一致性为什么难

逐帧独立生成时，每帧虽然 Prompt 相同，随机采样仍会改变：

- 轮廓和局部几何；
- 纹理、图案与文字；
- 光照和颜色；
- 遮挡关系；
- 小物件的出现/消失；
- Normal/Depth 等技术通道。

视频看起来会 Flicker、Boiling 或形体漂移。只固定 Seed 不能解决，因为每帧输入结构和去噪轨迹不同。

## 约束分层

可以从强到弱组合：

1. 固定输入几何/渲染序列；
2. 每帧 Depth/Normal/Pose/Edge ControlNet；
3. 首帧/角色参考的 IP-Adapter；
4. 前一帧 Warp 后作为 Img2Img 输入；
5. 共享或相关噪声/Latent；
6. Temporal Module/Video Diffusion；
7. 输出后 Temporal Filter 与人工修复。

结构控制保证大形，参考条件保证身份/风格，Temporal Model 负责跨帧特征。单一方法通常不能同时解决全部问题。

## Optical Flow Warp

已知前一帧图像 $I_{t-1}$ 和 Flow $F_{t-1\rightarrow t}$，可把历史 Warp 到当前：

$$
\hat I_t(\mathbf{x})=I_{t-1}(\mathbf{x}-F(\mathbf{x}))
$$

$\hat I_t$ 作为 Img2Img 初始图或一致性参考。

Flow 在 Disocclusion、快速运动、反射、透明和 Motion Blur 区域不可靠。需要 Occlusion/Confidence Mask：可信区域保留历史，新出现区域重新生成。

反复 Warp 会累积拉伸和模糊。应定期用 Keyframe 重新锚定，并让当前结构 Control 修正漂移。

## Latent 与噪声一致性

相邻帧使用完全独立 Noise 会增加闪烁；使用相关 Noise 可让细节更连贯。但相机/物体运动后，同一 Latent 像素不再对应同一表面。

更稳妥的是按 Motion/Flow Warp Latent 或 Feature，并对 Disocclusion 注入新 Noise。具体可行性取决于模型和节点实现，不能把像素 Flow 无条件直接套到任意 Latent Scale。

固定 Latent 也可能让纹理粘在 Screen Space。要检查细节是随对象、UV 还是相机移动。

## Keyframe 与传播

先人工确认 Keyframe，再向前后传播：

1. 选镜头/动作变化明显的 Keyframe；
2. 固定角色、材质和风格参考；
3. 在 Keyframe 间传播 Flow/Condition；
4. 对 Disocclusion 和形体变化重新生成；
5. 检查接缝并局部 Inpaint；
6. 保存 Keyframe/Propagation 关系。

长镜头不应从第一帧一路单向传播，误差会积累。分段后在边界做双向传播或重叠 Blend。

## 时序法线生成

单图 Normal Estimator 只能从外观猜几何，存在尺度、凹凸和光照歧义。逐帧预测会让法线方向和细节跳动。

先统一技术语义：

- Camera/View Space 还是 World Space；
- OpenGL/DirectX Y 方向；
- 值域 `[-1,1]` 如何编码到 `[0,1]`；
- Background/Invalid Mask；
- 是否单位化；
- Camera Intrinsic/Extrinsic；
- 是否需要 Tangent-space Normal。

仅对 RGB Normal 做时间平均会缩短向量并跨表面污染。应解码到向量、按 Motion Warp、使用 Depth/Mask/Confidence 拒绝，再归一化。

## Normal Temporal Filter

对当前法线 $\mathbf{n}_t$ 与重投影历史 $\mathbf{n}_h$，先检查：

- Depth/Position 差；
- Object/Instance ID；
- Flow Confidence；
- 法线夹角；
- Disocclusion。

有效时可在向量空间 Nlerp：

$$
\mathbf{n}'=\operatorname{normalize}((1-w)\mathbf{n}_t+w\mathbf{n}_h)
$$

稳定区域增大 $w$，运动边界和新出现区域减小 $w$。如果当前预测与几何 Depth Gradient 冲突，应降低历史或重新估计。

对离线序列可双向处理，利用前后帧；实时流程只能使用过去历史，延迟策略不同。

## 多通道一致性

生成 Base Color、Normal、Depth、Mask 等多个通道时，不能各自独立生成后再假设对齐。

优先让它们共享同一几何/结构源，或由一个主通道派生。若模型分别预测，必须验证：

- 边界和 Object ID 对齐；
- Normal 与 Depth Gradient 一致；
- Mask 没有时序跳变；
- 纹理细节不会在 Normal 中产生假几何；
- 分辨率、Crop 和镜头参数一致。

## 曝光与颜色稳定

结构稳定时，自动曝光、VAE 解码和每帧生成的色彩仍可能闪动。输入序列先固定 Color Space、Exposure 和 Tone Mapping；输出比较应在线性或明确的显示空间进行。

可以用稳定区域估计每帧 Luminance/Color Transform，但要排除大幅运动、闪光和真实灯光变化。把真实变化也强行归一化，会让效果失去能量。

颜色校正参数应平滑并限制变化速度。Keyframe 已批准的颜色可以作为 Anchor，镜头切换时重置历史，不把上一镜头统计带入下一镜头。

## 时序质量指标

单帧质量检查之外：

- Warping Error：Flow Warp 后的颜色/特征差；
- Temporal LPIPS/Feature Distance；
- Mask IoU 和轮廓漂移；
- Normal Angular Error/Frame Difference；
- Flicker Frequency/Energy；
- Identity/Style Embedding Stability；
- 人工检查关键动作、遮挡和镜头切换。

指标不能代替观看。过度平滑可获得较小帧差，却让细节拖影和失去响应。

## 失败恢复

- 保存每帧 Job/Condition/Seed/Model/Output；
- 单帧失败可重跑，不重算整段；
- OOM 可切 Worker 或降安全参数，并标记变更；
- 输出写 Staging，整段验证后发布；
- Custom Node 异常保留输入和 Stack；
- Keyframe 人工批准后锁定，传播任务不得静默覆盖。

## 验证方法

- 用静态镜头验证随机 Flicker，再逐步加入运动、遮挡和镜头切换。
- 分别关闭 Flow、ControlNet、IP-Adapter、Temporal Module，确定各项贡献。
- 输出 Flow、Occlusion、History Weight、Normal Angle 和 Reject Reason。
- 对循环动画检查首尾连接。
- 用固定 Workflow 在环境升级前后跑 Golden Sequence。
- 记录帧耗时、VRAM 峰值、失败率、重试和人工修复比例。

## 相关主题

- [[02_GPU与光栅化管线/抗锯齿与时域采样]]
- [[17_AIGC与Agent管线/扩散模型、条件控制与微调]]
- [[17_AIGC与Agent管线/Agent驱动资产管线与质量门禁]]

## 参考资料

- ComfyUI Official Documentation.
- Hugging Face Diffusers video and image-to-image documentation.
- Rerender A Video and TokenFlow papers，视频重绘与特征传播参考。
- Optical Flow and temporal reprojection literature.
