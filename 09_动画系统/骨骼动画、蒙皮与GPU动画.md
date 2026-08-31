# 骨骼动画、蒙皮与 GPU 动画

骨骼动画把高维的逐顶点运动压缩成少量关节变换，再用蒙皮权重恢复表面运动。要理解实现，关键是分清 Bind Pose、当前 Pose、局部空间和模型空间。

## Skeleton 与 Joint

Skeleton 是一棵层级树。引擎实际保存的是 Joint 的局部变换、父索引和绑定信息。“Bone”通常只是相邻 Joint 之间的可视化连杆。

标准骨架有两个工程价值：

- 动画、动捕和 Retargeting 可以复用；
- 工具能依赖稳定的命名、拓扑、Root 和挂点。

Root 一般作为角色整体位移基准，Pelvis 负责身体重心和蹲起等局部运动。武器、特效和镜头挂点应有明确的 Attachment Joint，避免依赖易变化的网格节点。

## 局部 Pose 到模型空间

动画轨道通常保存 Joint 相对父节点的 Translation、Rotation、Scale。局部数据更容易压缩，也能保持骨长和层级关系。

对第 $i$ 个 Joint：

$$
M_i^{model}(t)=M_{parent(i)}^{model}(t)M_i^{local}(t)
$$

从 Root 按父子顺序累积，就能得到全部 Joint 的当前模型空间矩阵。若父节点还没计算，子节点结果一定错误，因此 Skeleton 常按拓扑顺序存储。

旋转应在局部空间插值。直接插值两个模型空间 Joint 位置，可能让骨骼在中间帧伸缩或走不自然的直线。

## Bind Pose 与 Inverse Bind Matrix

Bind Pose 是蒙皮权重建立时的参考姿态。顶点在绑定时位于模型空间，但每个 Joint 有自己的绑定模型空间变换 $B_i$。

$B_i^{-1}$ 先把绑定姿态顶点从模型空间变到 Joint 的绑定局部空间。当前 Pose 的模型空间矩阵 $M_i(t)$ 再把它带到当前姿态：

$$
S_i(t)=M_i(t)B_i^{-1}
$$

$S_i(t)$ 就是第 $i$ 个 Joint 的 Skinning Matrix。模型“炸开”常见原因是矩阵乘法顺序、行列约定、坐标系或 Inverse Bind Matrix 错误。

## Linear Blend Skinning

一个顶点可以受多根 Joint 影响。Linear Blend Skinning（LBS）计算：

$$
\mathbf{p}'=\sum_{i=1}^{n}w_iS_i(t)\mathbf{p},\qquad \sum_i w_i=1
$$

Normal 也要随变换更新。若 Skinning Matrix 含非均匀缩放，应使用正确的逆转置或避免在骨架中使用破坏正交性的缩放。

LBS 简单、稳定、硬件友好，但手腕等部位大角度扭转时容易出现 Candy Wrapper，弯曲关节也可能丢体积。常见改善：

- 增加 Twist Joint 并重新分配权重；
- 使用 Corrective Blendshape；
- Dual Quaternion Skinning（DQS）；
- 对关键关节使用局部 RBF/Pose Driver 修形。

DQS 更能保持刚体旋转和体积，但对 Scale、混合管线和资产支持要求更高。

## Skin Weight 的实际约束

每个顶点影响骨骼数越多，Vertex Shader 读取和矩阵运算越多。移动端常限制为 4 个 Influence；高端角色可能允许 8 个，但需要实测。

导入或发布时应检查：

- 权重和是否接近 1；
- 是否引用不存在或被裁剪的 Joint；
- 微小无意义权重是否清理；
- 关节弯曲处的权重梯度是否连续；
- LOD 删骨后权重是否正确转移到保留父骨骼。

只在 Bind Pose 检查权重不够。应使用肩、肘、腕、胯、膝等极限测试 Pose 观察塌陷、拉伸和穿插。

## CPU 与 GPU Skinning

CPU Skinning 在 CPU 计算变形顶点，再上传动态 Vertex Buffer。优点是 CPU 侧容易访问最终几何，也能兼容部分碰撞或旧管线；缺点是计算和上传带宽随顶点数增长。

GPU Skinning 把 Joint Palette 放入 Constant Buffer、Structured Buffer 或 Texture，由 Vertex/Compute Shader 计算。它减少 CPU 顶点工作，但 GPU 每个相关 Pass 都可能重复蒙皮。

Compute Skinning 可以先把结果写入 Buffer，供 Depth、Shadow、GBuffer 等 Pass 复用。代价是额外显存、写带宽、Barrier 和调度。是否更快取决于角色数量、Pass 数和平台。

## Bone Palette 与分段

一次 Draw 能访问的 Joint 数受常量空间和平台限制。导入器可能按骨骼集合拆 Mesh Section，使每段只包含有限 Palette。

拆分会增加 Draw Call。工具应同时考虑：

- 每个 Section 的 Bone Count；
- 材质 Submesh；
- 顶点在 Section 边界的复制；
- LOD 和影子 Pass 是否需要全部骨骼。

## Animation Texture

大量同类角色可把每帧 Joint Matrix、Dual Quaternion 或已蒙皮顶点烘焙到 Texture/Buffer。实例只保存 Clip、Time、Frame 和 Blend 参数。

两种常见方案：

- **Bone Animation Texture**：存 Joint 变换，Vertex Shader 仍按权重蒙皮；
- **Vertex Animation Texture**：直接存每帧顶点位置/法线，运行时采样更直接，但数据量大且不易重新组合骨骼动作。

时间插值需要采样相邻帧。两个 Clip 混合会增加双份读取。直接线性插值矩阵会破坏正交性，较稳妥的做法是分别存 TRS 或 Dual Quaternion 后插值。

## 更新与渲染顺序

常见执行顺序是：

1. 推进动画时间并采样 Clip；
2. 混合 Local Pose；
3. 执行 IK、Constraint 和程序化修正；
4. 累积 Model Space Pose；
5. 与物理或布料交换数据；
6. 生成 Skinning Palette；
7. 提交渲染和 Motion Vector。

Motion Vector 必须使用当前与上一帧一致的变形结果。只保存 Object Transform 而忽略上一帧骨骼 Pose，会让蒙皮角色的 TAA 和 Motion Blur 拖影。

## 验证方法

- 在 Bind Pose 验证 $M_iB_i^{-1}$ 接近单位变换。
- 可视化 Skeleton、Joint Axes、Influence 和 Weight Sum。
- 固定一个顶点，逐步打印每个 Joint 的加权贡献。
- 比较 CPU/GPU Skinning 输出和 Normal 方向。
- 在 RenderDoc 检查 Bone Buffer、Influence 和 Vertex Shader 输入。
- 对极限 Pose、LOD 切换、Motion Vector 和阴影 Pass 做回归。

## 相关主题

- [[01_数学与采样/向量、矩阵与空间变换]]
- [[01_数学与采样/旋转、四元数与插值]]
- [[13_引擎渲染与资源架构/Draw Call、Batching与GPU Instancing]]
- [[14_性能分析与优化/帧时间、瓶颈与GPU成本]]

## 参考资料

- Kavan et al., *Skinning with Dual Quaternions*.
- Unity Manual, *Skinned Mesh Renderer* and *Animation compression*.
- Unreal Engine Documentation, *Skeletal Mesh Animation System*.
