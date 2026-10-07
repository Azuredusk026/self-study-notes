---
name: kb-structure-audit
description: 审计知识库文章边界、标题、目录领域与语义层级，生成逐篇主归属和迁移方案；用于结构与分类审查。
---

# 文章粒度与结构审计

读取 [实施规范](../../知识库/00_知识库说明/知识库实施规范.md)。用 [audit.py](scripts/audit.py) 提取围栏外标题、链接、代码、图片和语言候选，再复读全文作决定。

一句话说明主问题。比较主要章节的输入输出、前提、实现、验证、来源和独立检索意图。一个问题的替代方案集中比较；不同问题分归属；只有概述的材料先放导读。查找现有主归属，重复机制按章节合并。

输出字段为路径、主问题、`boundary_action`、`content_actions`、`title_review`、`category_review`、章节归属、目标、理由、置信度、受影响反链与九维质量矩阵。脚本输出结构事实和候选，编辑判断单独记录；脚本只读仓库。

标题审查先读全文和实际主归属，按实施规范生成不同定位的候选。完整可复用流程见 [标题审查提示词](references/title-review-prompt.md)，仅在标题任务中读取。三术语并列与长标题作为复读线索，SPLIT是语义判断，采用命名按授权同步H1、文件及引用。

分类任务读取 [分类审查提示词](references/category-review-prompt.md)。先定义完整领域使命，再逐篇判断问题、模型、读者、学习与维护边界，数量只触发复查。方案见 [领域审查](category-review.json)，迁移采用按对应授权执行。

写作复读覆盖全部文章，边界KEEP不会排除语言、结构和事实工作。已是导读的文章按关系与路线验收，避免重复建立其已有专篇。

实施前产生迁移映射，迁移后核对来源、图片、参考、地图、术语和反链。当前范围由用户批准的实施规范决定。

[validate.py](scripts/validate.py)核对链接、围栏、标题跨级、地图、登记资产、质量矩阵和已采用命名的一致性。运行 `python skills/kb-structure-audit/scripts/validate.py <仓库根>`；检查器只报告确定的不变量，语义层级、标题质量与语言由复读判断。

批量实施验收运行 `python skills/kb-structure-audit/scripts/batch_validate.py <仓库根>`，核对冻结路径与H1、正文批次覆盖、最终哈希、锚点、反链、术语重复和当前章节映射。隔离夹具检查运行 `python skills/kb-structure-audit/scripts/test_batch_validate.py <仓库根>`。检查结果只证明这些不变量，全文结论与证据范围见 [批量迁移验收报告](references/batch-acceptance-report.md)。

全库工作状态见 [article-quality-matrix.json](article-quality-matrix.json)，只在全库计划或迁移进度任务中读取。新建、拆分和评审后同步路径、正文动作与质量状态。

当前标题方案见 [title-review.json](title-review.json)，命名迁移见 [rename-map.json](rename-map.json)。标题方案包含全文理解、不同候选与采用状态；映射连接历史审计中的原路径和当前页面，历史验证记录保持其原始含义。

标题采用的覆盖度与执行记录见 [title-adoption-pilot.json](title-adoption-pilot.json)和 [采用报告](references/title-adoption-report.md)。领域方案与逐篇归属见 [分类报告](references/category-pattern-report.md)，审查结论与实际迁移分别记录。
