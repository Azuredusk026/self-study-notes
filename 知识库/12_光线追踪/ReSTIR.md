# ReSTIR

光源很多时，一个像素只看几次候选容易漏掉重要贡献。ReSTIR用reservoir保留代表样本与统计量，再跨帧和邻域重新评估候选。复用增加有效候选，也带来相关性与可见性偏差，权重必须在目标像素重算。

## 候选样本怎样跨时空复用

### ReSTIR

Reservoir-based Spatiotemporal Importance Resampling（ReSTIR）用 Reservoir 保存许多候选中的代表样本及其统计权重。

Weighted Reservoir Sampling 处理第 $i$ 个候选权重 $w_i$ 时，以概率 $w_i/W_i$ 替换当前样本，其中 $W_i=\sum_{j=1}^{i}w_j$。最终只保存一个样本、权重和候选数，不必保存全部候选。

ReSTIR DI 的典型过程：

1. 当前像素从光源分布生成少量候选；
2. 根据 Target Function 计算重要性权重；
3. 与重投影的 Temporal Reservoir 合并；
4. 与邻居 Spatial Reservoir 合并；
5. 对最终样本做可见性测试；
6. 用 Reservoir 统计量构造估计。

Temporal/Spatial Reuse 使一个像素间接利用更多候选，但也带来相关性、Bias 和错误复用。必须检查 Geometry/Normal/Material 相似性，限制 History Age 和重复候选数。

### ReSTIR 的可见性问题

若每个候选都先发 Shadow Ray，复用的收益会被可见性成本吃掉。很多实现先用未遮挡贡献选 Reservoir，只对最终样本测试 Visibility。

但遮挡后权重可能与目标分布不匹配，产生高方差或 Bias。Visibility Reuse、Pairwise MIS 和具体 ReSTIR 变体有不同修正，不能把基础 Reservoir 公式直接当完整实现。

## 加权reservoir更新

基础伪代码输入非负有限权重，累计W大于零时用w/W替换。它只说明单流采样，不是完整ReSTIR估计器。

```text
W += w
M += 1
if random01() < w/W: selected = candidate
```

完整实现还保存目标函数与归一化权重，对时空reservoir合并处理候选数、重评估和MIS。可见性结果是否复用按具体变体核对。

## 验证方法

离散候选权重已知时统计选择频率，再与直接采样参考比较积分均值。目标像素改变、遮挡出现与历史重复时检查重评估、候选计数和年龄，不能只观察降噪后的颜色。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[01_数学与采样/Monte Carlo采样]]
- [[12_光线追踪/实时光追采样]]
- [[12_光线追踪/光追降噪]]

## 参考资料

- Bitterli et al., *Spatiotemporal Reservoir Resampling for Real-Time Ray Tracing with Dynamic Direct Lighting*.
- Schied et al., *Spatiotemporal Variance-Guided Filtering*.
- NVIDIA, *Real-Time Denoising With Spatiotemporal Variance-Guided Filtering*.
- Heitz et al., *A Fast and Robust Method for Avoiding Self-Intersection*.
