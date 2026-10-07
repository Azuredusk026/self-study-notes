# Monte Carlo采样

半球上有无数入射方向，有限预算只能取一部分。样本出现得更频繁，不代表那一块应被重复计算；Monte Carlo用采样密度修正贡献，再通过重要性分布降低方差。

## 积分估计

### Monte Carlo Integration

要计算积分：

$$
I=\int_D f(x)\,dx
$$

如果从概率密度 $p(x)$ 中抽取 $N$ 个样本，可以估计：

$$
I\approx\frac{1}{N}\sum_{i=1}^{N}\frac{f(x_i)}{p(x_i)}
$$

每个样本用 $1/p(x_i)$ 修正被抽到的概率。否则更常被抽到的区域会被重复计算，估计产生偏差。

Monte Carlo 的典型误差大致按 $O(1/\sqrt N)$ 下降。想让误差减半，样本数通常需要增加到约四倍。这也是实时路径追踪必须依赖重要性采样、降噪和时域累积的原因。

### 概率密度不是概率

连续分布中，$p(x)$ 是密度。某个精确点的概率通常为零，区间概率才是密度的积分。

概率密度需要满足：

$$
p(x)\ge 0,\qquad \int_Dp(x)\,dx=1
$$

在半球方向采样中，还要注意使用的是立体角概率密度，而不是普通二维面积密度。

## 采样分布

### 重要性采样（Importance Sampling）

如果 $f(x)$ 在少数区域很大，均匀采样会浪费大量样本。重要性采样让 $p(x)$ 尽量接近 $|f(x)|$ 的形状，把样本集中到贡献大的区域。

在材质采样中，可以让方向分布接近 BRDF 高光瓣；在环境光采样中，可以让样本更多落在亮区域。

重要性采样不会凭空减少工作。它减少的是估计方差。采样分布与被积函数不匹配时，收益会下降，甚至产生极端权重和亮点噪声。

### 均匀半球和余弦加权半球

Lambert 漫反射积分包含 $\cos\theta$。如果使用余弦加权半球采样，概率密度为：

$$
p(\omega)=\frac{\cos\theta}{\pi}
$$

它把更多样本分配给法线附近，因为这些方向的余弦贡献更大。代入估计式后，部分余弦项会与 PDF 抵消，方差通常比均匀半球采样更低。

### 低差异序列

纯随机样本会聚团，也会留下空洞。Halton、Hammersley、Sobol 等低差异序列尽量均匀覆盖采样域，适合像素采样、环境光和积分。

它们不是传统随机数。实际使用还可能需要 Scrambling 或 Cranley-Patterson Rotation，避免不同像素之间出现结构化图案。

### 多重重要性采样

一个积分可能有多种好分布。例如直接光照既可以按光源采样，也可以按 BRDF 采样。多重重要性采样（Multiple Importance Sampling，MIS）组合多种估计，并降低某一种策略在不适合区域产生的高方差。

## 离散重要性采样

输入 `weights` 是非负函数值，`cdf` 保存归一化前缀和。采样返回离散索引及其概率质量：

```cpp
Sample DrawFromCdf(Span<float> weights, Span<float> cdf, float u)
{
    if (weights.empty()) return {};
    cdf[0] = weights[0];
    for (int i = 1; i < weights.size(); ++i)
        cdf[i] = cdf[i - 1] + weights[i];
    float total = cdf.back();
    if (total <= 0.0f) {
        int index = Min((int)(u * weights.size()), weights.size() - 1);
        return { index, 1.0f / weights.size() };
    }
    int index = UpperBound(cdf, u * total);
    return { index, weights[index] / total };
}
```

离散求和时除以概率质量；用于面积或方向积分时，还需处理采样测度转换。所有权重为零时，示例回退到均匀采样；调用方也可以跳过该分布。可用常量函数验证：只要 PDF 与采样分布一致，多次估计的均值都应接近解析结果。

## 验证方法

对常量函数与已知多项式积分比较均值和方差，逐步增加样本数。连续密度、离散概率质量和立体角测度分别核对。CDF查找应使用严格大于目标值的首项，跳过零权重区间；输入u限制到[0,1)，权重非负且有限。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

本机CPU验证：CDF零权重区间由 [completion_reference.py](../examples/mechanisms/completion_reference.py) 检查，运行 `python 知识库/examples/mechanisms/completion_reference.py`。这些检查验证模型，不包含GPU执行或实际网络故障注入。

## 相关主题

- [[04_光照模型与PBR/BRDF与微表面模型]]
- [[12_光线追踪/光线求交与BVH]]
- [[01_数学与采样/球谐光照]]

## 参考资料

- Matt Pharr, Wenzel Jakob, Greg Humphreys, *Physically Based Rendering*.
- Peter-Pike Sloan, *Stupid Spherical Harmonics Tricks*.
- Ravi Ramamoorthi and Pat Hanrahan, *An Efficient Representation for Irradiance Environment Maps*.
