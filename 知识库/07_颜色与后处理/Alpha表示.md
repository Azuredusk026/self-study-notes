# Alpha表示

透明边缘出现黑线，常是RGB填充、预乘方式和Blend State不一致。Alpha可以是覆盖，也可以是项目数据，首先要确定含义。Straight与Premultiplied保存颜色的方式不同，过滤与合成必须沿同一表示。

## 覆盖与合成

### Alpha通道语义

sRGB 格式的非线性转换通常只作用于 RGB，Alpha 保持线性数值。Alpha 可能代表：

- Coverage/Opacity；
- Mask；
- Smoothness；
- 其他项目数据。

因此一张 Base Color 的 RGB 可以按 sRGB 解码，Alpha 仍作为线性 Mask 使用。

Alpha的语义由资产元数据、导入器与Shader共同约定，文件扩展名不能充分说明它表示覆盖率还是材质参数。

### 线性混合

如果 RGB 仍在 sRGB 编码空间就做混合，中间颜色会偏暗。正确过程是先解码 RGB 到 Linear，在线性 Render Target 上混合，最终显示时再编码。

硬件对 sRGB Render Target 可以在写入时自动编码，对 sRGB Texture 可以在采样时自动解码。是否发生转换由资源格式和 View 决定，不是 Shader 变量名决定。

### 两种颜色表示

完整混合方程与排序见 [[02_GPU与光栅化管线/透明合成]]。本页关注制作与过滤，防止RGB与覆盖数据采用不一致的表示。

#### Straight Alpha

非预乘表示保存颜色 $C$ 和覆盖率 $\alpha$。合成到不透明背景时，源贡献为 $\alpha C$，常用RGB混合因子为 `SRC_ALPHA` 与 `ONE_MINUS_SRC_ALPHA`。

透明像素中的RGB也会参与过滤。相邻两个纹素是红色不透明 `(1,0,0,1)` 和黑色透明 `(0,0,0,0)`，各取一半后得到 `(0.5,0,0,0.5)`；再按非预乘规则覆盖黑背景，红色贡献只有0.25。有效覆盖实际是一半红色，期望贡献应为0.5，因此出现黑边。

#### Premultiplied Alpha

预乘表示保存 $C_p=\alpha C$ 和 $\alpha$。对上例先预乘再过滤，结果同样为 `(0.5,0,0,0.5)`，但合成的RGB源因子为 `ONE`，贡献因此是0.5。RGB目的因子仍为 `ONE_MINUS_SRC_ALPHA`；若目标Alpha也代表覆盖，Alpha因子应单独使用 `ONE` 与 `ONE_MINUS_SRC_ALPHA`，得到 $\alpha_o=\alpha_s+(1-\alpha_s)\alpha_d$。

过滤需要计算 $\sum_iw_i\alpha_iC_i$，而采样后再预乘得到的是 $(\sum_iw_i\alpha_i)(\sum_iw_iC_i)$，两者一般不相等。因此预乘应发生在纹素过滤和mip生成之前，不能仅靠片元着色器最后乘一次Alpha修复资源黑边。

源图片若是sRGB非预乘颜色，制作顺序为解码RGB、在线性空间预乘、按需要编码存储，再生成遵守同一表示的mip。运行时sRGB视图解码后得到线性预乘值。Alpha始终保持自己的线性覆盖数值。

```text
linearRGB = DecodeSRGB(sourceRGB)
premultipliedRGB = linearRGB * alpha
storedRGB = EncodeSRGB(premultipliedRGB)  // 仅当目标文件使用sRGB编码
```

这是资产转换伪代码，逐通道转换函数见 [[07_颜色与后处理/颜色空间]]。普通非发光覆盖素材在Alpha为0时预乘RGB为0；若项目允许零Alpha携带非零RGB来表示加法发光，需单独定义这种混合语义。恢复非预乘颜色需要除以Alpha，Alpha为0时不能恢复已丢失的颜色，应采用指定填充值。

### UI颜色链路

常见原因：

- UI 纹理 sRGB 标记错误；
- Shader 手动 Gamma 转换和硬件转换重复；
- Straight/Premultiplied Alpha 与 Blend State 不一致；
- UI 在 HDR/Tone Mapping 前绘制，被曝光和曲线改变；
- UI 在后处理后绘制，却仍使用场景颜色假设；
- RenderTexture 格式和颜色空间不一致。

排查时要画出完整链路，而不是只切换项目 Gamma/Linear 设置。

## 验证方法

用有色边缘和零Alpha像素比较过滤，再检查Shader输出与blend因子。预乘在线性RGB进行，RGB编码与Alpha数值转换分开。透明层排序与OIT由透明合成说明。

[test_post.py](../examples/revision/test_post.py) 用上述红色/透明两纹素检查先预乘再过滤的贡献。混合方程已核对，GPU混合状态和实际纹理导入尚未运行。

## 相关主题

- [[02_GPU与光栅化管线/透明合成]]
- [[25_UI与文本/文字渲染]]
- [[07_颜色与后处理/颜色空间]]
- [[07_颜色与后处理/HDR与曝光]]

## 参考资料

- [[02_GPU与光栅化管线/透明合成]]：Over合成、RGB与Alpha因子及对应接口资料。
- [W3C CSS Color 4：Interpolation with premultiplied alpha](https://www.w3.org/TR/css-color-4/#interpolation-alpha)，预乘后插值的规则。
