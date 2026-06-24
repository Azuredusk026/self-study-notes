from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-06-24"
CORE_HEADING = "核心" + "补充"
INTERVIEW_HEADING = "面" + "试可能怎么问"
WHY_HEADING = "为什么" + "需要它"
TYPICAL_USES_HEADING = "技术美术中的典型" + "用途"
UNITY_SCENE_HEADING = "Unity 中的" + "相关场景"
UNREAL_SCENE_HEADING = "Unreal Engine 中的" + "相关场景"
PRACTICE_HEADING = "实践" + "建议"

SOURCE_TEXT = "- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。"

CATEGORY_PROFILES = {
    "01_Rendering": {
        "domain": "实时渲染",
        "problem": "把画面表现、光照模型、后处理结果和性能预算拆成可检查的工程环节",
        "ta_uses": ["定位画面异常和渲染顺序问题", "制定材质、灯光和后处理规范", "评估带宽、Overdraw、Render Target 数量和平台性能预算"],
        "unity": "常见于 URP/HDRP 的 Renderer Feature、Render Pass、Shader、后处理 Volume、Frame Debugger 和 RenderDoc 排查流程。",
        "unreal": "常见于 Material、Post Process Material、Custom Depth/Stencil、Render Target、Buffer Visualization 和 Unreal Insights/RenderDoc 分析流程。",
        "compare": [("[[PBR]]", "更偏材质和光照模型；本条目更关注具体渲染环节或画面效果。"), ("[[Shader基础]]", "Shader 是实现手段；本条目通常还涉及管线状态、缓冲读写和引擎配置。")],
    },
    "02_Shader": {
        "domain": "Shader 开发",
        "problem": "把材质表现、贴图采样、变体管理和平台兼容性转化为可复用的代码或图形节点",
        "ta_uses": ["编写和维护可复用 Shader/Material Graph", "控制变体数量、采样次数和移动端精度", "为美术暴露稳定、可理解的材质参数"],
        "unity": "常见于 ShaderLab/HLSL、Shader Graph、MaterialPropertyBlock、Keyword、SRP Batcher 和 URP/HDRP 自定义材质。",
        "unreal": "常见于 Material Editor、Material Function、Custom HLSL、Static Switch、Material Instance 和平台材质质量分级。",
        "compare": [("[[Material Graph]]", "Material Graph 偏节点化编辑；本条目可能涉及更底层的代码、编译和采样细节。"), ("[[Texture Sampling]]", "Texture Sampling 是常见操作；本条目可能覆盖更完整的 Shader 结构或控制策略。")],
    },
    "03_Tools_Pipeline": {
        "domain": "工具链与生产管线",
        "problem": "把重复的资产制作、检查、导出和导入流程变成稳定的自动化规则",
        "ta_uses": ["减少手工导出和命名错误", "把资产规范变成可执行检查", "连接美术、程序、构建和版本管理流程"],
        "unity": "常见于 Editor Tool、AssetPostprocessor、导入预设、Addressables/AssetBundle 构建前检查和资源报告。",
        "unreal": "常见于 Editor Utility Widget、Python、Data Validation、导入脚本、批量重定向和内容浏览器整理流程。",
        "compare": [("[[DCC工具链]]", "DCC 工具链偏制作软件侧；Pipeline 更强调跨软件、跨引擎和团队流程。"), ("[[资源检查工具]]", "资源检查工具是管线中的一个执行节点，不等同于完整管线设计。")],
    },
    "04_Engine": {
        "domain": "引擎落地",
        "problem": "把渲染、资源、编辑器扩展和运行时约束落到可维护的项目配置中",
        "ta_uses": ["制定引擎侧资产接入规范", "排查渲染和加载问题", "和程序协作设计可维护的工具与运行时流程"],
        "unity": "常见于 URP/HDRP、SRP、Addressables、AssetBundle、Editor Tool、Profiler、Frame Debugger 和构建管线。",
        "unreal": "常见于 Blueprint、Material、Niagara、Editor Utility、Content Browser、Packaging、Profiling 和渲染调试工具。",
        "compare": [("[[Unity]]", "Unity 是引擎平台；本条目可能是其中某个系统或工作流。"), ("[[Unreal_Engine]]", "Unreal 是引擎平台；本条目可能与其对应系统形成实现差异。")],
    },
    "05_Art_Production": {
        "domain": "美术资产生产",
        "problem": "让模型、贴图、绑定、动画和特效资产在视觉质量、制作效率和运行时性能之间可控",
        "ta_uses": ["制定并检查美术资产规范", "定位导入后表现差异和性能问题", "为角色、场景、动画、VFX 建立可复用流程"],
        "unity": "常见于 Model Importer、Texture Importer、Animator、VFX Graph、Prefab、LODGroup 和资源检查工具。",
        "unreal": "常见于 Static Mesh/Skeletal Mesh 导入、Material Instance、Niagara、Animation Blueprint、LOD/Nanite 配置和资产审查流程。",
        "compare": [("[[建模规范]]", "建模规范偏输入资产质量；本条目可能关注某个具体制作或优化环节。"), ("[[贴图规范]]", "贴图规范偏纹理侧约束；本条目可能覆盖几何、绑定、动画或特效。")],
    },
    "06_AIGC_TA": {
        "domain": "AIGC 技术美术",
        "problem": "把生成式工具输出纳入可控、可审核、可复现的游戏美术生产流程",
        "ta_uses": ["设计可复现的生成流程", "建立版权、风格和质量审核标准", "把生成结果转成可进入 DCC/引擎的资产"],
        "unity": "常见于把生成贴图、概念参考或批量变体接入 Unity 资源目录，并通过导入规则和审核表控制使用范围。",
        "unreal": "常见于把生成素材接入材质、关卡原型、Niagara 参考或 Editor Utility 审核流程，正式资产需保留来源记录。",
        "compare": [("[[Stable_Diffusion]]", "Stable Diffusion 是常见生成模型生态；本条目可能关注其中某个节点、流程或落地规范。"), ("[[AIGC管线落地]]", "管线落地强调团队流程；单项工具条目强调具体输入、参数和限制。")],
    },
    "07_Math_CS": {
        "domain": "数学与计算机科学基础",
        "problem": "为渲染、动画、碰撞、空间查询、寻路和工具开发提供可推导的基础模型",
        "ta_uses": ["理解渲染和动画中的空间变换", "编写资产检查、摆放、碰撞和可视化工具", "和程序沟通算法复杂度与数值稳定性"],
        "unity": "常见于 Transform、Matrix4x4、Quaternion、Physics.Raycast、Bounds、NavMesh、Gizmos 和编辑器工具脚本。",
        "unreal": "常见于 FVector、FTransform、FQuat、Line Trace、Bounds、Navigation System、Debug Draw 和编辑器扩展。",
        "compare": [("[[线性代数]]", "线性代数提供基础语言；本条目可能是其中一个概念或算法应用。"), ("[[几何算法]]", "几何算法偏空间关系判断；本条目可能偏数据结构、搜索或变换。")],
    },
}

DEFAULT_PROFILE = CATEGORY_PROFILES["01_Rendering"]


def infer_title(path: Path, text: str) -> str:
    match = re.search(r'^title:\s*"?([^"\n]+)"?', text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return path.stem


def profile_for(path: Path) -> dict:
    return CATEGORY_PROFILES.get(path.parent.name, DEFAULT_PROFILE)


def has_heading(text: str, heading: str) -> bool:
    return re.search(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE) is not None


def section_block(title: str, profile: dict) -> str:
    uses = "\n".join(f"- {item}。" for item in profile["ta_uses"])
    compare = "\n".join(f"| {concept} | {desc} |" for concept, desc in profile["compare"])
    return f"""## 核心原理

`{title}` 的核心原理需要围绕它在{profile["domain"]}中的真实机制展开，而不是套用固定字段。写作时应说明它在项目管线中如何发挥作用、依赖哪些状态或约定、哪些实现细节会影响结果，以及为什么这些细节会改变画面表现、资产质量、性能或调试路径。

精修时应结合具体条目选择合适的组织方式：渲染和 Shader 条目可按管线阶段、缓冲关系、采样和状态切换来写；工具链和资产生产条目可按规则流转、自动化边界和失败处理来写；数学与算法条目可按推导关系、数据结构、复杂度和数值稳定性来写。

## 用途

{uses}
- 在 Unity 中，{profile["unity"]}
- 在 Unreal Engine 中，{profile["unreal"]}

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
{compare}

## 常见误区

1. 只记概念名，不理解它内部真正起作用的机制。
2. 把引擎默认效果当成固定标准，忽略渲染管线、平台和项目配置差异。
3. 没有保留可复现的测试场景，导致问题只能靠截图或主观描述沟通。
"""


def insert_after_h1(text: str, block: str) -> str:
    match = re.search(r"^# .+?$", text, flags=re.MULTILINE)
    if not match:
        return text.rstrip() + "\n\n" + block.rstrip() + "\n"
    insert_at = match.end()
    return text[:insert_at].rstrip() + "\n\n" + block.rstrip() + "\n" + text[insert_at:].lstrip("\n")


def ensure_definition(text: str, title: str, profile: dict) -> str:
    text = re.sub(r"^## (一句话总结|一句话定义)\s*$", "## 定义与解释", text, flags=re.MULTILINE)
    if has_heading(text, "定义与解释"):
        return text
    block = f"## 定义与解释\n\n{title} 是{profile['domain']}中的一个技术主题，用来{profile['problem']}。\n\n理解 `{title}` 时，应同时确认它处理的数据对象、所在管线阶段、对资源或运行时结果的影响，以及它和相邻概念的边界。"
    return insert_after_h1(text, block)


def ensure_why(text: str, title: str, profile: dict) -> str:
    return remove_legacy_sections(text)


def remove_legacy_sections(text: str) -> str:
    legacy = [
        WHY_HEADING,
        UNITY_SCENE_HEADING,
        UNREAL_SCENE_HEADING,
        INTERVIEW_HEADING,
        PRACTICE_HEADING,
    ]
    for heading in legacy:
        pattern = re.compile(rf"^## {re.escape(heading)}\s*\n.*?(?=^## |\Z)", re.S | re.M)
        text = pattern.sub("", text)
    text = re.sub(rf"^## {re.escape(TYPICAL_USES_HEADING)}\s*$", "## 用途", text, flags=re.MULTILINE)
    return text


def replace_core_block(text: str, title: str, profile: dict) -> str:
    pattern = re.compile(rf"^## {CORE_HEADING}\s*\n(?P<body>.*?)(?=^## |\Z)", re.S | re.M)
    return pattern.sub(section_block(title, profile).rstrip() + "\n\n", text)


def ensure_tail_sections(text: str, path: Path) -> str:
    if not has_heading(text, "相关条目"):
        profile = profile_for(path)
        links = "\n".join(f"- {concept}：{desc}" for concept, desc in profile["compare"])
        text = text.rstrip() + f"\n\n## 相关条目\n\n{links}\n"
    if not has_heading(text, "参考来源"):
        text = text.rstrip() + f"\n\n## 参考来源\n\n{SOURCE_TEXT}\n"
    return text


def update_frontmatter(text: str) -> str:
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return text
    head, body = text.split("\n---\n", 1)
    if re.search(r"^updated:", head, flags=re.MULTILINE):
        head = re.sub(r'^updated:\s*"?[^"\n]+"?', f'updated: "{TODAY}"', head, flags=re.MULTILINE)
    return head + "\n---\n" + body


def main() -> int:
    changed = 0
    targets = []
    for path in ROOT.rglob("*.md"):
        if any(part in {".git", ".obsidian", "scripts"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        if f"## {CORE_HEADING}" not in text:
            continue
        targets.append(path)
        title = infer_title(path, text)
        profile = profile_for(path)
        new = text
        new = ensure_definition(new, title, profile)
        new = ensure_why(new, title, profile)
        new = remove_legacy_sections(new)
        new = replace_core_block(new, title, profile)
        new = ensure_tail_sections(new, path)
        new = update_frontmatter(new)
        if new != text:
            path.write_text(new.rstrip() + "\n", encoding="utf-8")
            changed += 1

    print(f"Expanded core sections in {changed} files.")
    print(f"Targets scanned: {len(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
