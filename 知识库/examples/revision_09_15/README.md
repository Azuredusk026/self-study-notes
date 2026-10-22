# 动画、渲染与工具机制检查

`reference.py` 是 Python 3.10 及以上版本可运行的标量模型。`test_reference.py` 用 14 项检查验证正交基底的旋转共轭、单位平面尺度下的虹膜视差符号、Face SDF 角度阈值，有限离散域的 RIS 权重与期望，以及事务前置条件失败、补偿继续执行和成功路径。事务模型的单步写入回调须原子成功或自行恢复部分修改，返回原始失败与各次补偿错误。

在仓库根目录执行：

```powershell
python 知识库/examples/revision_09_15/test_reference.py
python 知识库/examples/revision_09_15/verify.py
```

第二条命令要求 `dxc` 位于 PATH，或通过 `DXC_PATH` 指定；还需要 Git 和 Bash，Windows 默认定位 Git 安装目录的 `bin/bash.exe`，也可通过 `KB_BASH_PATH` 指定。`test_ci_excerpt.py` 抽取资产 CI 正文的 Bash 检查，在临时仓库运行五项测试：中文与空格文件名、英文及中文非指针拒绝，以及暂存区与工作区内容不一致的两个方向。这些 Git 检查不验证 LFS 对象服务、凭据和指针完整格式。

`verify.py` 还从当前文章抽取九段 HLSL，为片段补齐最小输入并按 `ps_6_0` 编译，随后将测试输出、编译器版本与片段哈希写入 `results.json`。临时编译文件保存在系统临时目录并在退出时清理。

这些检查没有创建图形设备。CPU 数学结果和 HLSL 编译均不能替代引擎运行、真实贴图与几何输入、GPU 捕获或性能测量。RIS 检查覆盖基础估计关系，没有实现整帧时空复用和可见性修正。
