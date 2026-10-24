# Monte Carlo采样

半球上有无数入射方向，有限预算只能取一部分。样本出现得更频繁，不代表那一块应被重复计算；Monte Carlo用采样密度修正贡献，再通过重要性分布降低方差。

## 积分估计

### 随机积分估计

要计算积分：

$$
I=\int_D f(x)\,dx
$$

如果从概率密度 $p(x)$ 中抽取 $N$ 个样本，可以估计：

$$
I\approx\frac{1}{N}\sum_{i=1}^{N}\frac{f(x_i)}{p(x_i)}
$$

每个样本用 $1/p(x_i)$ 修正被抽到的概率，因为期望中的采样密度会与分母抵消，留下原积分。这个推导要求所有非零贡献区域都有正采样概率；漏掉一个区域，再多样本也无法补回它的贡献。

当样本独立、估计量方差有限时，均值的标准差按 $O(1/\sqrt N)$ 下降。想让误差减半，样本数通常需要增加到约四倍。这也是实时路径追踪必须依赖重要性采样、降噪和时域累积的原因。

### 概率密度与概率质量

连续分布中，$p(x)$ 是密度。某个精确点的概率通常为零，区间概率才是密度的积分。

概率密度需要满足：

$$
p(x)\ge 0,\qquad \int_Dp(x)\,dx=1
$$

在半球方向采样中，还要注意使用的是立体角概率密度，而不是普通二维面积密度。

## 采样分布

### 重要性采样

如果 $f(x)$ 在少数区域很大，均匀采样会浪费大量样本。重要性采样让 $p(x)$ 尽量接近 $|f(x)|$ 的形状，把样本集中到贡献大的区域。

在材质采样中，可以让方向分布接近 BRDF 高光瓣；在环境光采样中，可以让样本更多落在亮区域。

重要性采样不会凭空减少工作。它减少的是估计方差。采样分布与被积函数不匹配时，收益会下降，甚至产生极端权重和亮点噪声。

### 均匀半球与余弦加权采样

密度必须与实际生成方向的过程一致。取两个独立的均匀数`u,v∈[0,1)`，均匀半球可令`z=u、phi=2πv`，再取`r=sqrt(1-z²)`与方向`(r cos(phi),r sin(phi),z)`。这里均匀的是立体角，密度为`1/(2π)`；把极角theta直接均匀生成会在极点聚集，因为球面面积元还包含`sin(theta)`。

余弦半球则令`r=sqrt(u)、phi=2πv、z=sqrt(1-u)`。单位圆盘面积元为`r dr dphi`，平方根把均匀u转换成均匀圆盘面积；投影到半球后，密度变为`z/π`。两种生成式都先在局部+Z半球工作，再用以表面法线为第三轴的正交基变到世界空间。基底的构造与退化处理见 [[07_颜色与后处理/屏幕空间AO]]。

假设常量环境辐亮度为2、Lambert反照率为0.6。被积函数是`f(L)=0.6/π * 2 * NoL`，解析出射值为1.2。均匀半球的单样本贡献是`2.4*NoL`，随方向变化；余弦半球除以`NoL/π`后，每个有效样本恰好贡献1.2。方差降低来自密度消掉了方向变化，不能在除PDF后再次乘NoL。u严格小于1避免生成密度为零的地平线端点；更一般的采样器仍需明确处理零贡献和退化输入。

### 多重重要性采样

环境有一盏很小的亮灯，而材质高光也很窄时，按灯采样和按BRDF采样各擅长一部分方向。直接把两份完整估计相加会把同一积分算两次。MIS在每个样本上分配权重，并要求各策略的权重在共同支持域内相加为1。

对两种策略各取一个样本，平衡启发式取`wA(L)=pA(L)/(pA(L)+pB(L))`、`wB(L)=1-wA(L)`，估计为`wA(LA)*f(LA)/pA(LA) + wB(LB)*f(LB)/pB(LB)`。这里是两个各自含一个样本的加权估计之和，不能再除以2。策略各取nA、nB个样本时，权重分子换成`nA*pA`和`nB*pB`，每份策略内部再除以自己的样本数。

若某方向`pA=0.8/sr、pB=0.2/sr`，两份权重为0.8和0.2；两个加权项中的系数分别为`0.8/0.8=1`和`0.2/0.2=1`。其期望乘回各自密度后，合计仍是`(0.8+0.2)*f`。这个局部计算说明权重分区如何保持积分，不能把恰好取到相同方向的两份数值当成一般输出。

每个策略需要能评估另一策略在当前方向上的密度，而且使用同一测度。面积光的面积密度必须先乘`distance²/abs(lightNormal·(-L))`转换为立体角密度。把`1/m²`与`1/sr`直接相加，MIS权重就失去含义。某策略密度为零时另一策略可以负责覆盖；两者都为零的非零贡献区域仍会被漏掉。

## 离散重要性采样

以下是C++机制片段，`Span`、`Sample`、`UpperBound`由宿主提供；`UpperBound`返回严格大于目标的首项索引。输入权重非负且有限，`u`位于[0,1)，调用者提供与权重等长的暂存数组。非空输入的项数须能由int表示。总和须有限；全零权重走均匀回退，其他输入的总和必须为正。每个正权重还须在工作精度下形成非零CDF区间，并得到可表示的正概率；片段会拒绝吞项或概率下溢。异常类型来自`<stdexcept>`。空输入返回的`Sample`必须带无效索引，不能默认为有效第零项。

```cpp
Sample DrawFromCdf(Span<float> weights, Span<float> cdf, float u)
{
    if (weights.empty()) return {};
    cdf[0] = weights[0];
    for (int i = 1; i < weights.size(); ++i) {
        cdf[i] = cdf[i - 1] + weights[i];
        if (!std::isfinite(cdf[i]) ||
            (weights[i] > 0.0f && cdf[i] <= cdf[i - 1]))
            throw std::range_error("CDF interval is not representable");
    }
    float total = cdf.back();
    if (total <= 0.0f) {
        int index = Min((int)(u * weights.size()), weights.size() - 1);
        return { index, 1.0f / weights.size() };
    }
    for (int i = 0; i < weights.size(); ++i)
        if (weights[i] > 0.0f && weights[i] / total == 0.0f)
            throw std::range_error("sample probability underflow");
    float target = Min(u * total, std::nextafter(total, 0.0f));
    int index = UpperBound(cdf, target);
    return { index, weights[index] / total };
}
```

离散求和时除以概率质量；用于面积或方向积分时，还需处理采样测度转换。所有权重为零时，示例回退到均匀采样；调用方也可以跳过该分布。可用常量函数验证：只要 PDF 与采样分布一致，多次估计的均值都应接近解析结果。

### CDF边界与重用

权重为`[0,1,0,3,0]`时，前缀为`[0,1,1,4,4]`。`u=0`应选索引1，`u=0.25`应选索引3。严格大于目标的查找会跳过没有宽度的区间。即使`u<1`，浮点乘法也可能把`u*total`舍入成`total`；代码将目标限制到总和前一个可表示值，避免查找返回数组末尾。`std::nextafter`来自`<cmath>`。

权重`[16777216,1]`以32位float累计时，第二个前缀仍是16777216，正权重1没有对应区间。按最大值缩放仍可能保留同样的相对精度问题；接口应拒绝这类输入，再由调用者选择更高精度、分层分布或受约束的权重范围。随机数生成器也有有限分辨率，应与最小概率和允许偏差一起验证。这份CDF是有限精度近似，不能据实数积分公式宣称任意动态范围下严格无偏。

构建前缀需要O(n)时间，一次二分查找需要O(log n)。同一分布需要多次抽样时，先建一次前缀再重复查找；若每次都重建，优化查找也不能消除线性构建成本。

### 低差异序列

纯随机样本会聚团，也会留下空洞。Halton、Hammersley、Sobol 等低差异序列尽量均匀覆盖采样域，适合像素采样、环境光和积分。

它们不是传统随机数。实际使用还可能需要 Scrambling 或 Cranley-Patterson Rotation，避免不同像素之间出现结构化图案。

## 验证方法

对常量函数与已知多项式积分比较均值和方差，逐步增加样本数。连续密度、离散概率质量和立体角测度分别核对。CDF查找应使用严格大于目标值的首项，跳过零权重区间；输入u限制到[0,1)，权重非负且有限。

本页C++是依赖宿主类型的机制片段。[正文抽取宿主](../examples/fullread_review/verify.py)补齐Span、Sample与查找接口，以Clang和C++17编译并运行8类边界检查；工作精度为32位float，完整积分器与GPU未运行。Python参考模型和边界测试见 [math_models.py](../examples/revision/math_models.py) 与 [test_math.py](../examples/revision/test_math.py)，运行 `python 知识库/examples/revision/test_math.py`；该测试只覆盖离散CDF、球谐解析例与一维噪声。

本机CPU验证：CDF零权重区间由 [completion_reference.py](../examples/mechanisms/completion_reference.py) 检查，运行 `python 知识库/examples/mechanisms/completion_reference.py`。这些检查验证CDF区间选择，不包含GPU执行或完整积分器。

## 相关主题

- [[04_光照模型与PBR/BRDF与微表面模型]]
- [[12_光线追踪/光线求交与BVH]]
- [[01_数学与采样/球谐光照]]

## 参考资料

- Matt Pharr, Wenzel Jakob, Greg Humphreys, *Physically Based Rendering*.
- PBRT第四版第2章：概率测度、估计量与重要性采样；球谐投影见对应专篇。

- [CDF逆映射与采样域，2026-10-07核读](https://pbr-book.org/4ed/Monte_Carlo_Integration/Sampling_Using_the_Inversion_Method)。
