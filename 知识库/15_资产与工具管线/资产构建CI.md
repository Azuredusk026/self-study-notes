# 资产构建CI

构建机拿到的是LFS指针，导入器仍可能报文件损坏。资产CI先确认真实输入和工具版本，再按依赖执行验证、构建与发布。缓存键包括源、配置和依赖，才能让增量结果与干净构建一致。

## 资产 CI

一次资产变更可执行：

1. Checkout 正确 Commit/Changelist 和 LFS/Depot 内容；
2. 恢复锁定的工具与依赖版本；
3. 计算受影响资产；
4. 运行 Validator/Importer/Cook；
5. 比较预算、引用和 Golden Result；
6. 发布 Report、Artifact 和 Manifest；
7. 失败时阻止合入或发布。

CI 要使用专用 Service Account，最小权限，并处理 DCC/Engine License。不要把个人账号和 Token 写进脚本。

## 缓存

DCC 转换、纹理压缩、Shader Compile 和 Cook 都昂贵。Cache Key 应包含 Source Hash、Settings、Tool Version、Platform 和 Dependency。

缓存命中结果仍要验证 Metadata。错误 Cache Key 会复用过期产物，比没有缓存更难查。

缓存应有容量、淘汰、命中率和污染恢复策略。CI 日志记录 Cache Hit/Miss 及耗时，才能判断收益。

## 变更范围与依赖

只检查本次直接修改文件可能漏掉下游。Texture 改变会影响 Material、Prefab、Level 和 Bundle。需要 Asset Dependency Graph 或 Import Database 计算受影响集合。

全库检查最可靠但反馈慢。实践中：

- Pre-submit 检查直接资产和关键反向依赖；
- Merge CI 构建受影响 Bundle/Scene；
- Nightly 做全库 Cook 与预算扫描；
- Release 做目标平台完整构建。

## CI 中检查 LFS 指针

大型二进制文件应在仓库中保存为 LFS 指针。下面的 Bash 检查暂存区中常见大型资产是否仍是普通 Git Blob：

```bash
git diff --cached --name-only --diff-filter=ACM | while IFS= read -r path; do
  case "$path" in
    *.psd|*.fbx|*.wav|*.mp4)
      if ! git show ":$path" \
        | head -n 1 \
        | grep -qx 'version https://git-lfs.github.com/spec/v1'; then
        echo "应由 Git LFS 跟踪: $path" >&2
        exit 1
      fi
      ;;
  esac
done
```

管道直接检查暂存 Blob 的首行，不把二进制内容放入 Shell 变量。规则中的扩展名应与项目 `.gitattributes` 和资产类型表一致。仅检查扩展名不能识别改名或自定义容器，CI 还可结合文件大小和文件头。验证时分别提交一个 LFS 文件和一个普通 Blob，确保失败能指向具体路径。

## 验证方法

在干净工作区与缓存工作区构建同一输入，对比输出hash和诊断。修改依赖、工具版本或导入设置应触发正确节点；缺LFS、部分失败与发布中断保留可诊断状态。完整发布机制以资产构建与发布为主归属。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[15_资产与工具管线/资产构建与发布]]
- [[15_资产与工具管线/大型资产版本控制]]

## 参考资料

- Git LFS Documentation, *Pointer files*, *Tracking* and *Locking*.
- Perforce Helix Core Documentation, *Streams*, *File types*, *Shelving* and *Protections*.
- Unity Version Control Documentation, *Branches*, *Locks* and *Gluon*.
- Unity and Unreal Engine build automation and asset pipeline documentation.
