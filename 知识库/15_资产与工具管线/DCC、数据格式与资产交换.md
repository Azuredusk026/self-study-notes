# DCC、数据格式与资产交换

资产交换的目标不是“文件能打开”，而是让几何、材质、骨骼、动画、单位和依赖在不同软件之间保持可解释。每经过一次 Export/Import，都会发生数据模型映射，也就多一次丢失语义的机会。

## 制作源、交换格式与运行时格式

三类数据职责不同：

- **Authoring Source**：`.ma/.mb`、`.blend`、`.hip`、`.spp` 等，保留历史、节点、图层和制作信息；
- **Interchange Format**：FBX、USD、glTF 等，在工具间传递约定范围的数据；
- **Runtime Asset**：引擎 Cook 后的 Mesh、Texture、Animation、Material 和 Bundle，针对加载、内存和平台优化。

FBX 适合作为交换边界，不适合直接作为游戏运行时格式。运行时通常需要预转换布局、压缩、分包、依赖和平台数据。

制作源应保留以便返修，但构建机器不一定每次重新执行整个 DCC 历史。是否提交导出中间产物取决于团队能否稳定、快速、合法地在 CI 重建。

## DCC 的职责

Maya 常用于角色建模、Rig、动画和引用式制作；Blender 覆盖通用建模、动画与开源脚本流程；Houdini 擅长属性驱动、程序化几何、地形、VFX 和批处理；Substance 工具负责材质图与纹理烘焙。

管线不应要求所有软件采用同一内部结构。应统一的是交付契约：

- 哪些对象进入导出集；
- 名称、类型和稳定 ID；
- 单位、轴向、Pivot 和 Transform；
- Normal、Tangent、UV、Vertex Color；
- Skeleton、Bind Pose、Animation Range；
- 材质槽、贴图语义与颜色空间；
- LOD、Collision、Socket 和 Metadata。

## 坐标系

交换前要明确：

- Left-handed / Right-handed；
- Up Axis 是 Y 还是 Z；
- Forward Axis 的正负方向；
- 一单位表示米、厘米还是其他；
- Matrix 使用行/列向量约定；
- UV 原点和 Texture V 方向；
- Triangle Winding 与 Front Face。

轴转换不是只交换 Position 分量。Normal、Tangent、Animation、Camera、Light、Constraint 和 Negative Scale 都要按同一变换处理。

若坐标转换改变 Handedness，三角形 Winding 或 Tangent Sign 需要同步翻转。否则会出现背面剔除、Normal Map 方向和动画镜像错误。

## Transform 与 Pivot

Freeze/Apply Transform 会把 Object Transform 烘进几何，但也可能改变子层级、Rig 和动画语义。工具需要区分静态 Mesh、Skinned Mesh、Socket 和 Group Node，不能对全部对象执行同一清理命令。

Pivot 决定摆放、旋转、物理和工具交互。常见约定：

- 建筑模块使用网格角点或对齐基准；
- 道具使用重心或接地点；
- 角色 Root 在脚底中心；
- 门、轮子等使用实际旋转轴；
- 程序化资产输出稳定的 Pivot/Bounds。

导出前自动移动到原点再恢复场景是一种高风险操作。更稳妥的是在临时副本或导出矩阵中转换，保证失败也不污染源文件。

## 几何语义

交换内容至少包括 Position、Index、Normal、Tangent、UV、Color、Material Slot 和 Skin Data。

DCC 的一个 Point 可能因硬边、UV 缝或材质边界在引擎拆成多个 Vertex。导出前统计与导入后统计应分别记录，不能用源点数直接判断运行时预算。

是否三角化需要明确。不同 DCC/Importer 对 N-gon 的三角化可能不同，导致 Normal、Bake 和 Morph Target 不一致。关键资产通常在受控步骤三角化，并保留可编辑源版本。

## Normal 与 Tangent

Normal 可以导入、重新计算或混合处理。Tangent 必须和 UV、Normal Map 编码及引擎切线基一致。

若烘焙器使用 MikkTSpace，而引擎重新生成另一套 Tangent，接缝处会产生误差。管线应记录：

- Normal 导入策略；
- Tangent 生成器与版本；
- DirectX/OpenGL Normal Map 的 Y 通道约定；
- Hard Edge 与 UV Seam 规则；
- 负缩放/镜像的 Tangent Handedness。

## 骨骼与动画

交换 Skeleton 时需要稳定 Joint Name、Parent、Bind Pose、Inverse Bind Matrix 和 Skin Weight。重名、额外 Group、Namespace 清理和非均匀 Scale 都可能破坏绑定。

动画导出应明确：

- Frame Rate 与起止帧；
- 是否 Bake Constraint/IK 到 Joint Track；
- Root Motion 轨道；
- Euler Filter 与 Quaternion 插值；
- 是否包含 Scale；
- Clip 划分、Event/Curve 的额外传递方式。

FBX 能保存动画曲线，但自定义 Rig Graph、控制器逻辑和 DCC Constraint 不会自动成为引擎运行时 Rig。交付前一般 Bake 到约定 Skeleton。

## FBX

FBX 生态广、DCC 与引擎支持成熟，适合 Mesh/Skeleton/Animation 交换。但它的数据模型和 SDK 复杂，不同软件版本与选项可能产生不同结果。

稳定 FBX 管线应固定：

- Exporter/Importer 版本；
- Binary/ASCII 与 FBX Version；
- Axis/Unit Conversion；
- Triangulate、Smoothing、Tangent；
- Bake Animation 与 Sampling；
- Embed Media 是否禁止；
- 导出选择集和命名。

不要让艺术家每次手工点一遍选项。工具应保存 Preset，导出后生成 Manifest，并在引擎侧验证实际结果。

## glTF

glTF 面向高效传输和运行时场景表达，常见内容包括 Mesh、PBR Material、Texture、Skin、Animation、Camera 和 Node Hierarchy。`.glb` 可把 JSON 与 Buffer/Texture 打包为单文件。

它的 Metallic-Roughness 材质语义较清楚，适合 Viewer、Web 和跨工具预览。但复杂 DCC 历史、项目自定义 Shader、完整 Rig 和引擎特性仍需要 Extension 或额外数据。

使用 Extension 前要确认生产端、消费端和验证器都支持。文件符合 glTF Schema 不代表目标引擎正确实现该 Extension。

## USD

OpenUSD 不只是一个“更大的 FBX”。它提供 Scene Description、Layer、Reference、Payload、Variant、Composition 和 Schema，用于大型内容协作与非破坏组合。

典型价值：

- Layout 引用 Modeling Asset，而不复制几何；
- LookDev Layer 覆盖材质，不修改模型层；
- Variant Set 切换造型、LOD 或材质；
- Payload 延迟加载重内容；
- Namespace 和 Prim Path 提供稳定场景地址；
- 多部门通过 Layer Stack 组合意见。

USD 的强项是场景组合与数据治理，不保证所有 DCC/引擎支持相同 Schema、MaterialX、Rig 或实时行为。项目需要定义支持子集和 Flatten/Cook 边界。

## 材质与贴图

DCC Shader Graph 很少能一比一转换成引擎 Shader。更可靠的交换方式是传递语义参数和纹理：Base Color、Normal、Metallic、Roughness、AO、Emissive、Opacity 等，再由引擎创建受控 Material Template/Instance。

同时记录：

- 颜色贴图使用 sRGB，数据贴图使用 Linear；
- Normal Map 类型与通道；
- 通道打包布局；
- UDIM、Texture Set 和 Tile 命名；
- Relative Path/Asset ID，而不是某台机器绝对路径；
- Source Texture 与平台压缩产物的关系。

### Assimp 场景遍历与纹理去重

Assimp 的 `aiScene` 保存根节点、网格数组、材质数组和动画。节点构成场景层级，每个节点通过索引引用 `scene->mMeshes`。导入器应递归累积节点变换，再处理节点引用的网格；只遍历全局网格数组会丢失实例关系和节点局部变换。

```cpp
void VisitNode(const aiScene& scene, const aiNode& node,
               const Matrix4& parentToRoot)
{
    Matrix4 nodeToRoot = parentToRoot * Convert(node.mTransformation);
    for (unsigned i = 0; i < node.mNumMeshes; ++i) {
        const aiMesh& mesh = *scene.mMeshes[node.mMeshes[i]];
        ImportMesh(mesh, *scene.mMaterials[mesh.mMaterialIndex], nodeToRoot);
    }
    for (unsigned i = 0; i < node.mNumChildren; ++i)
        VisitNode(scene, *node.mChildren[i], nodeToRoot);
}
```

矩阵乘法顺序取决于库与引擎的向量约定。导入后可用一个带父子旋转和非均匀缩放的测试层级核对结果。Assimp 材质纹理类型是来源格式的语义提示，例如 Diffuse、Normals、Metalness；它不保证与项目 PBR 槽位一一对应。导入层应建立明确映射，并保留无法识别的属性供诊断。

同一纹理可能被多个 Mesh 和材质引用。去重键应使用规范化后的资源标识，例如模型目录加相对路径、内嵌纹理 ID 和颜色空间语义。只按文件名缓存会把不同目录的同名纹理合并；只按完整路径缓存又可能把同图的 Base Color 与 Linear 数据视图错误复用。验证时统计场景声明的纹理引用数、唯一资源数和实际 GPU 资源数。

## Metadata 与 Sidecar

交换格式无法稳定表达的项目数据，可使用 Custom Property、USD Schema 或 Sidecar Manifest。Manifest 可保存：

- Asset ID、类型、版本；
- Source/Exporter/Tool Version；
- 输出文件和 Hash；
- LOD/Collision/Material 映射；
- 依赖列表；
- 作者、时间和发布状态。

Metadata 名称与类型应有 Schema。随意塞字符串会把解析和兼容问题推迟到下游。

## Reference、Copy 与 Round-trip

跨工具传递时先决定是引用还是复制。Reference 保留来源关系、文件小，但下游必须能解析路径、版本和权限；Copy/Snapshot 自包含，适合交付，却容易与原始资产分叉。

不应默认承诺无损 Round-trip。FBX 从 Maya 导入 Blender、修改后再回 Maya，节点、Constraint、材质和切线可能已经改变。更稳妥的流程指定每类数据的 Authoritative Source 和单向发布方向：例如 Rig 由 Maya 权威维护，材质贴图由 Substance 发布，引擎只保存 Import Setting 和运行时实例。

确实需要双向编辑时，应使用稳定 ID 和明确冲突规则，而不是按对象名称猜映射。每次回写生成变更预览，区分新增、修改、删除和无法表达的数据。

## 版本兼容

DCC Scene、Plugin 与交换格式都存在版本。新版本保存的源文件可能无法被旧构建机打开；Exporter 升级也可能改变三角化、动画采样或材质输出。

项目应记录 DCC/Plugin 版本矩阵，并让 Launcher 或环境脚本启动正确版本。升级先在副本上用 Golden Asset 批量转换和回归，确认可回滚后再更新项目锁定版本。

## 验证方法

- 建立 Golden Asset：带硬边、镜像 UV、负缩放、骨骼、动画、Morph、多个材质和 LOD。
- 在 DCC 导出后与引擎导入后比较 Bounds、Vertex、Normal、UV、Bone、Clip 和 Material Slot。
- 输出坐标轴、Tangent Frame、Skeleton 和 Root Motion 可视化。
- 固定 DCC、Plugin、Exporter 和 Importer 版本，在升级前批量回归 Golden Asset。
- 对 FBX/glTF/USD 使用官方验证器或 SDK 读取测试，不只检查文件存在。

## 相关主题

- [[08_几何与网格/网格数据、缓存与几何处理]]
- [[09_动画系统/骨骼动画、蒙皮与GPU动画]]
- [[15_资产与工具管线/资产导入、验证与发布]]

## 参考资料

- Autodesk, *FBX SDK Documentation*.
- Khronos Group, *glTF 2.0 Specification*.
- Alliance for OpenUSD, *OpenUSD Documentation*.
- Autodesk Maya, Blender and SideFX Houdini scripting/export documentation.
