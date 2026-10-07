# LoRA训练

少量角色图可以教会模型身份，也可能把背景和姿势一起记住。LoRA固定基础权重，学习低秩增量；训练数据和Caption先区分目标与可变因素，验证集再检查未见视角与组合条件。

## 适配器怎样学习目标概念

### LoRA

Low-Rank Adaptation（LoRA）把权重增量近似为低秩分解：

$$
W'=W+\lambda BA
$$

$A/B$ 的秩远小于原矩阵维度，训练和文件规模较小。训练常冻结基础权重，只优化低秩增量。推理时可以合并增量，也可以在前向计算中应用适配器；式中的 $\lambda$ 合并了所采用的 rank/alpha 缩放与用户强度约定。

LoRA 可学习角色、服装、材质、物体或风格，但结果受数据和 Caption 强烈影响。它不能弥补来源混乱、构图单一和错误标注。

### LoRA 数据

先定义目标概念和非目标因素。数据应：

- 有明确授权和来源；
- 覆盖希望泛化的视角、光照和背景；
- 避免所有图片同一姿势/构图；
- 去除水印、重复、低质量和错误样本；
- 记录 Crop/Resize/Caption 处理；
- 划分训练与固定验证集。

若所有角色图都在白背景，LoRA 可能把白背景当概念一部分。若 Caption 没区分服装和角色，特征也会纠缠。

### Caption 与 Tag

Caption 描述图像内容与可变因素；Trigger Word 指向目标概念。是否标注某个特征取决于希望模型把它当可控变量还是概念固有部分。

自动 Caption 可生成初稿，但要人工检查身份、颜色、数量和构图。错误 Caption 会稳定地教给模型错误关系。

Tag 顺序、Shuffle、Dropout 和自然语言/标签风格与训练脚本相关，应锁定配置并做对照实验。

### 训练与过拟合

训练配置先固定基础模型、分辨率和数据分桶，再确定网络 rank/alpha、学习率、批量与优化器。训练步数和是否更新文本编码器也需记录，方便区分数据变化与参数变化的影响。

过拟合表现：

- 构图和背景重复；
- Prompt 难以改变姿势/服装；
- 训练图细节被直接复现；
- 高权重才像，降低权重就失去概念；
- 与其他 LoRA/Control 组合崩坏。

不能只看训练 Loss。用固定 Prompt Matrix 比较不同 Checkpoint 和 Weight，检查相似度、可控性、泛化和副作用。

## 资产化

模型与适配器应像资产管理：

- Model ID、文件 Hash、License/Source；
- Compatible Base/Architecture；
- Training Dataset Manifest；
- Config、Script/Library Version；
- Trigger/Recommended Weight；
- Validation Grid；
- Known Failure/Forbidden Use；
- Owner、Review、Retire State。

来源不明的 Model/LoRA 不进入正式生产。文件名写“final_v2”无法替代版本和血缘。

## 基线评估

模型评估不能只挑最好看的图。建立 Prompt Matrix，覆盖：

- 角色/物体身份；
- 正侧背与远近景；
- 不同光照、背景、材质；
- 手部、文字、重复结构等高风险内容；
- 与 ControlNet/IP-Adapter/多个 LoRA 的组合；
- 项目禁止内容和来源风险。

保存全部 Seed，而不是只保存成功样本。统计失败类型、人工选择率和精修时间，才能判断新 Model/LoRA 是否真的提高生产效率。

自动指标可衡量图文、参考相似度或结构误差，但不能独立决定资产质量。最终评估同时看 Prompt 可控性、跨 Seed 稳定性、与管线兼容、许可和人工返工。

## 数据与隐私

训练、参考图和 Prompt 可能包含未公开角色、项目截图或个人数据。外部 API 前应经过数据分类和批准，明确服务是否保存输入、用于训练、部署区域和删除策略。

日志与样例图同样需要访问控制。为了复现保存完整 Prompt，不代表它可以进入公开报告。

## 低秩增量

数学机制伪代码中W为冻结基础矩阵，A、B维数使BA与W相同，scale匹配训练rank/alpha及用户强度。

```text
output = W*x + scale*B*(A*x)
train A,B on authorized data
validate held-out prompts, views and conditions
```

## 验证方法

保存训练配置、数据manifest与检查点，比较固定Prompt/Seed矩阵，不按单张最好结果选模型。检查身份、背景纠缠、其他LoRA组合和低权重表现，许可与敏感数据独立记录。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[17_AIGC与Agent管线/扩散模型]]
- [[17_AIGC与Agent管线/生成条件控制]]

## 参考资料

- Ho et al., *Denoising Diffusion Probabilistic Models*.
- Rombach et al., *High-Resolution Image Synthesis with Latent Diffusion Models*.
- Zhang et al., *Adding Conditional Control to Text-to-Image Diffusion Models*.
- Hu et al., *LoRA: Low-Rank Adaptation of Large Language Models*.
- Hugging Face Diffusers and ComfyUI official documentation.
