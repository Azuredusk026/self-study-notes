param(
    [string]$VaultRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'

$manifestDir = Join-Path $VaultRoot 'docs\manifests'
New-Item -ItemType Directory -Force -Path $manifestDir | Out-Null
$inventoryPath = Join-Path $manifestDir 'source-inventory.tsv'
$courseTargetsPath = Join-Path $manifestDir 'course-targets.tsv'
$existingRows = @{}
if (Test-Path -LiteralPath $inventoryPath) {
    foreach ($row in Import-Csv -Delimiter "`t" -LiteralPath $inventoryPath) {
        $existingRows[$row.source_path] = $row
    }
}

$courseTargets = @{}
if (Test-Path -LiteralPath $courseTargetsPath) {
    foreach ($row in Import-Csv -Delimiter "`t" -LiteralPath $courseTargetsPath) {
        $normalizedSource = $row.source_path.Replace('\', '/')
        $courseTargets[$normalizedSource] = $row
    }
}

function Get-TopicMapping {
    param(
        [string]$RelativePath,
        [string]$Extension
    )

    $path = $RelativePath.Replace('/', '\')
    $top = ($path -split '\\')[0]
    $name = [System.IO.Path]::GetFileNameWithoutExtension($path)

    if ($path -match '^TA-Encyclopedia\\01_Rendering\\') {
        if ($name -match 'Alpha|Depth|Early-Z|Rasterization|Stencil|Z-Test') { return @('02 GPU 与光栅化管线', '待迁移') }
        if ($name -match 'BRDF|Fresnel|IBL|Lambert|Light Probe|Metallic|PBR|Reflection Probe|Roughness') { return @('04 光照模型与 PBR', '待迁移') }
        if ($name -match 'Shadow') { return @('05 光照、阴影与 GI', '待迁移') }
        if ($name -match 'Bloom|Depth of Field|SSAO|Tone Mapping') { return @('07 颜色管理与后处理', '待迁移') }
        if ($name -match 'NPR|Toon') { return @('11 NPR 与风格化渲染', '待迁移') }
        if ($name -match 'Overdraw') { return @('14 性能分析与优化', '待迁移') }
        if ($name -match 'Vertex Shader|Fragment Shader') { return @('03 Shader 编程', '待迁移') }
        return @('13 引擎渲染与资源架构', '待迁移')
    }

    if ($path -match '^TA-Encyclopedia\\02_Shader\\') {
        if ($name -match 'Space$|Clip Space|Object Space|Screen Space|Tangent Space|View Space|World Space') { return @('01 数学、采样与信号', '待迁移') }
        if ($name -match 'Mipmap|Texture Sampling|UV与贴图采样') { return @('06 纹理技术', '待迁移') }
        if ($name -match 'Normal Map') { return @('04 光照模型与 PBR', '待迁移') }
        if ($name -match 'Dissolve') { return @('10 粒子、VFX 与模拟', '待迁移') }
        if ($name -match 'SDF') { return @('11 NPR 与风格化渲染', '待迁移') }
        if ($name -match '后处理') { return @('07 颜色管理与后处理', '待迁移') }
        if ($name -match 'GPU Instancing') { return @('13 引擎渲染与资源架构', '待迁移') }
        return @('03 Shader 编程', '待迁移')
    }

    if ($path -match '^TA-Encyclopedia\\03_Tools_Pipeline\\') { return @('15 美术资产与工具管线', '待迁移') }
    if ($path -match '^TA-Encyclopedia\\04_Engine\\') {
        if ($name -match 'Niagara') { return @('10 粒子、VFX 与模拟', '待迁移') }
        if ($name -match 'Editor|Python') { return @('15 美术资产与工具管线', '待迁移') }
        return @('13 引擎渲染与资源架构', '待迁移')
    }
    if ($path -match '^TA-Encyclopedia\\05_Art_Production\\') {
        if ($name -match 'Animation|Blend Shape|Morph|Rig|Root Motion|Skinning|动画|绑定') { return @('09 动画系统', '待迁移') }
        if ($name -match 'VFX') { return @('10 粒子、VFX 与模拟', '待迁移') }
        if ($name -match 'Texture|UV|Texel|Atlas|贴图') { return @('06 纹理技术', '待迁移') }
        if ($name -match 'Draw Call|LOD') { return @('14 性能分析与优化', '待迁移') }
        return @('08 几何与网格', '待迁移')
    }
    if ($path -match '^TA-Encyclopedia\\06_AIGC_TA\\') { return @('17 AIGC 与 Agent 管线', '待迁移') }
    if ($path -match '^TA-Encyclopedia\\07_Math_CS\\') {
        if ($name -match 'BVH|Ray|AABB|OBB|空间') { return @('12 光线追踪与现代渲染', '待迁移') }
        if ($name -match 'A星|Dijkstra|Graph|游戏AI') { return @('16 编程与数据结构', '待覆盖核验') }
        return @('01 数学、采样与信号', '待迁移')
    }
    if ($path -match '^TA-Encyclopedia\\(00_Index|90_Templates|91_Sources|92_Codex)\\') { return @('docs 过程与旧规则', '已退役') }
    if ($path -match '^TA-Encyclopedia\\(\.gitignore|AGENTS\.md|README\.md)$') { return @('docs 过程与旧规则', '已退役') }
    if ($path -match '^TA-Encyclopedia\\') { return @('docs 过程与旧规则', '已退役') }

    switch ($top) {
        'Games104' { return @('多领域：游戏引擎课程', '待覆盖核验') }
        '图形工程' { return @('多领域：图形工程课程', '待覆盖核验') }
        '图形学' { return @('多领域：图形学课程', '待覆盖核验') }
        '数据结构和算法' { return @('16 编程与数据结构', '待覆盖核验') }
        'C++基础' { return @('16 编程与数据结构', '待覆盖核验') }
        '编辑器设计' { return @('15 资产与工具管线', '待覆盖核验') }
        '游戏AI' { return @('20 游戏 AI', '待覆盖核验') }
        '游戏网络' { return @('21 游戏网络', '待覆盖核验') }
        'ACT' { return @('19 Gameplay 与游戏框架', '待覆盖核验') }
    }

    if ($path -match '^C\+\+') { return @('16 编程与数据结构', '待覆盖核验') }
    if ($path -match '^TA_Algorithm_Practice') { return @('16 编程与数据结构', '待覆盖核验') }
    if ($path -in @('.gitattributes', '.gitignore')) { return @('项目治理', '保留治理') }
    if ($path -match '^system_prompt\.md$') { return @('docs 过程与旧规则', '已退役') }
    if ($path -match '^未命名\.canvas$') { return @('无有效内容', '排除') }
    if ($path -match '^AGENTS\.md$') { return @('项目治理', '保留治理') }
    return @('待人工判断', '待筛选')
}

function Get-MarkdownTitle {
    param([string]$Path)
    if ([System.IO.Path]::GetExtension($Path) -notin @('.md', '.txt')) { return '' }
    $line = Get-Content -LiteralPath $Path -Encoding UTF8 -TotalCount 80 |
        Where-Object { $_ -match '^#\s+\S' } |
        Select-Object -First 1
    if ($line) { return ($line -replace '^#\s+', '').Trim() }
    return ''
}

function Get-PublicFiles {
    $paths = @(& git -c core.quotepath=false -C $VaultRoot ls-files --cached --others --exclude-standard)
    if ($LASTEXITCODE -ne 0) {
        throw '无法通过 Git 获取公开文件清单。'
    }

    foreach ($path in $paths) {
        if ([string]::IsNullOrWhiteSpace($path)) { continue }
        $relative = $path.Replace('/', '\\')
        if ($relative -match '(^|\\)文字记录(\\|$)' -or
            $relative -match '文字记录.*\.zip$') {
            continue
        }

        $fullPath = Join-Path $VaultRoot $relative
        if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
            Get-Item -LiteralPath $fullPath
        }
    }
}

$files = @(Get-PublicFiles | Where-Object {
    $relative = $_.FullName.Substring($VaultRoot.Length + 1)
    $_.FullName -notmatch '\\.git\\|\\.obsidian\\|\\.idea\\|\\docs\\|\\scripts\\' -and
        $relative -notmatch '^(?:0[0-9]|1[0-9]|2[0-9])_[^\\]+\\' -and
        $relative -notin @('README.md', 'CHANGELOG.md')
})

$rows = foreach ($file in $files) {
    $relative = $file.FullName.Substring($VaultRoot.Length + 1)
    $normalizedRelative = $relative.Replace('\', '/')
    $mapping = Get-TopicMapping -RelativePath $relative -Extension $file.Extension.ToLowerInvariant()
    $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $status = $mapping[1]
    $targetArticle = ''
    $notes = ''
    if ($courseTargets.ContainsKey($normalizedRelative)) {
        $courseTarget = $courseTargets[$normalizedRelative]
        $status = $courseTarget.coverage_status
        $targetArticle = $courseTarget.target_article
        $notes = $courseTarget.notes
    }
    elseif ($existingRows.ContainsKey($relative)) {
        $existing = $existingRows[$relative]
        if ($existing.sha256 -eq $hash -and
            $existing.migration_status -in @('已覆盖', '重复内容已覆盖', '保留治理')) {
            $status = $existing.migration_status
            $targetArticle = $existing.target_article
            $notes = $existing.notes
        }
    }
    [pscustomobject]@{
        source_path = $relative
        file_type = $(if ($file.Extension) { $file.Extension.ToLowerInvariant() } else { '(none)' })
        bytes = $file.Length
        sha256 = $hash
        title = Get-MarkdownTitle -Path $file.FullName
        target_domain = $mapping[0]
        migration_status = $status
        target_article = $targetArticle
        notes = $notes
    }
}

$rows | Sort-Object source_path | ConvertTo-Csv -Delimiter "`t" -NoTypeInformation |
    Set-Content -LiteralPath $inventoryPath -Encoding UTF8

$duplicates = $rows | Group-Object sha256 | Where-Object Count -gt 1
$duplicatePath = Join-Path $manifestDir 'duplicate-files.tsv'
$duplicateRows = foreach ($group in $duplicates) {
    foreach ($item in $group.Group) {
        [pscustomobject]@{
            sha256 = $group.Name
            duplicate_count = $group.Count
            source_path = $item.source_path
        }
    }
}
if ($duplicateRows) {
    $duplicateRows | ConvertTo-Csv -Delimiter "`t" -NoTypeInformation |
        Set-Content -LiteralPath $duplicatePath -Encoding UTF8
}
else {
    "sha256`tduplicate_count`tsource_path" |
        Set-Content -LiteralPath $duplicatePath -Encoding UTF8
}

$headingPath = Join-Path $manifestDir 'markdown-headings.tsv'
$headingRows = foreach ($file in $files | Where-Object Extension -eq '.md') {
    $relative = $file.FullName.Substring($VaultRoot.Length + 1)
    $lineNumber = 0
    foreach ($line in Get-Content -LiteralPath $file.FullName -Encoding UTF8) {
        $lineNumber++
        if ($line -match '^(#{1,3})\s+(.+?)\s*$') {
            [pscustomobject]@{
                source_path = $relative
                line = $lineNumber
                level = $matches[1].Length
                heading = $matches[2]
            }
        }
    }
}
$headingRows | ConvertTo-Csv -Delimiter "`t" -NoTypeInformation |
    Set-Content -LiteralPath $headingPath -Encoding UTF8

Add-Type -AssemblyName System.IO.Compression.FileSystem
$slideTitlePath = Join-Path $manifestDir 'pptx-slide-titles.tsv'
$slideTitleRows = foreach ($file in $files | Where-Object Extension -eq '.pptx') {
    $relative = $file.FullName.Substring($VaultRoot.Length + 1)
    $archive = [System.IO.Compression.ZipFile]::OpenRead($file.FullName)
    try {
        $slideEntries = $archive.Entries | Where-Object {
            $_.FullName -match '^ppt/slides/slide(\d+)\.xml$'
        } | Sort-Object { [int]([regex]::Match($_.FullName, 'slide(\d+)').Groups[1].Value) }

        foreach ($entry in $slideEntries) {
            $slideNumber = [int]([regex]::Match($entry.FullName, 'slide(\d+)').Groups[1].Value)
            $stream = $entry.Open()
            $reader = [System.IO.StreamReader]::new($stream, [System.Text.Encoding]::UTF8)
            try {
                [xml]$xml = $reader.ReadToEnd()
                $texts = @($xml.SelectNodes("//*[local-name()='t']") |
                    ForEach-Object { ([string]$_.InnerText).Trim() } |
                    Where-Object { $_ })
                [pscustomobject]@{
                    source_path = $relative
                    slide = $slideNumber
                    title = $(if ($texts.Count -gt 0) { $texts[0] } else { '' })
                    text_preview = (($texts | Select-Object -First 6) -join ' | ')
                }
            }
            finally {
                $reader.Dispose()
                $stream.Dispose()
            }
        }
    }
    finally {
        $archive.Dispose()
    }
}
if ($slideTitleRows) {
    $slideTitleRows | ConvertTo-Csv -Delimiter "`t" -NoTypeInformation |
        Set-Content -LiteralPath $slideTitlePath -Encoding UTF8
}
else {
    "source_path`tslide`ttitle`ttext_preview" |
        Set-Content -LiteralPath $slideTitlePath -Encoding UTF8
}

$summaryPath = Join-Path $manifestDir 'audit-summary.txt'
$summary = @(
    "schema_version`t1",
    "source_files`t$($rows.Count)",
    "source_bytes`t$(($rows | Measure-Object bytes -Sum).Sum)",
    "duplicate_hash_groups`t$($duplicates.Count)",
    ''
    'by_type'
)
$summary += $rows | Group-Object file_type | Sort-Object Count -Descending |
    ForEach-Object { "$($_.Name)`t$($_.Count)`t$(($_.Group | Measure-Object bytes -Sum).Sum)" }
$summary += ''
$summary += 'by_target_domain'
$summary += $rows | Group-Object target_domain | Sort-Object Name |
    ForEach-Object { "$($_.Name)`t$($_.Count)" }
$summary += ''
$summary += 'by_migration_status'
$summary += $rows | Group-Object migration_status | Sort-Object Name |
    ForEach-Object { "$($_.Name)`t$($_.Count)" }
$summary | Set-Content -LiteralPath $summaryPath -Encoding UTF8

Write-Host "Wrote $inventoryPath"
Write-Host "Wrote $duplicatePath"
Write-Host "Wrote $headingPath"
Write-Host "Wrote $slideTitlePath"
Write-Host "Wrote $summaryPath"
Write-Host "Audited $($rows.Count) source files."
