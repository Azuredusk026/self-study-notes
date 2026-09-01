param(
    [string]$VaultRoot = (Split-Path -Parent $PSScriptRoot),
    [int]$ExpectedFormalCount = 69,
    [switch]$AllowPendingCoverage
)

$ErrorActionPreference = 'Stop'
$failures = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()

function Add-Failure {
    param([string]$Message)
    $failures.Add($Message)
}

function Get-PublicMarkdownFiles {
    $paths = @(& git -c core.quotepath=false -C $VaultRoot ls-files --cached --others --exclude-standard -- '*.md')
    if ($LASTEXITCODE -ne 0) {
        throw '无法通过 Git 获取公开 Markdown 清单。'
    }

    foreach ($path in $paths) {
        $relativePath = $path.Replace('/', '\\')
        $fullPath = Join-Path $VaultRoot $relativePath
        if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
            Get-Item -LiteralPath $fullPath
        }
    }
}

function Resolve-WikiLink {
    param(
        [string]$Target,
        [hashtable]$PathIndex,
        [hashtable]$NameIndex
    )

    $normalized = ($Target -split '#', 2)[0].Trim().Replace('\', '/')
    if (-not $normalized) { return $true }
    if (-not $normalized.EndsWith('.md')) { $normalized += '.md' }

    if ($PathIndex.ContainsKey($normalized.ToLowerInvariant())) { return $true }

    $leaf = [System.IO.Path]::GetFileNameWithoutExtension($normalized).ToLowerInvariant()
    return $NameIndex.ContainsKey($leaf) -and $NameIndex[$leaf].Count -eq 1
}

$formalListPath = Join-Path $VaultRoot 'docs\正式文章清单.md'
$inventoryPath = Join-Path $VaultRoot 'docs\manifests\source-inventory.tsv'

if (-not (Test-Path -LiteralPath $formalListPath)) {
    throw "Formal article list not found: $formalListPath"
}
if (-not (Test-Path -LiteralPath $inventoryPath)) {
    throw "Source inventory not found: $inventoryPath"
}

$formalPaths = @(
    foreach ($line in Get-Content -LiteralPath $formalListPath -Encoding UTF8) {
        if ($line -match '\| `([^`]+\.md)` \|') {
            $matches[1].Replace('\', '/')
        }
    }
)
$uniqueFormalPaths = @($formalPaths | Sort-Object -Unique)

if ($formalPaths.Count -ne $ExpectedFormalCount) {
    Add-Failure "正式文章数量为 $($formalPaths.Count)，预期为 $ExpectedFormalCount。"
}
if ($uniqueFormalPaths.Count -ne $formalPaths.Count) {
    Add-Failure '正式文章清单包含重复路径。'
}

$formalContents = @{}
$titleToPaths = @{}
foreach ($relativePath in $uniqueFormalPaths) {
    $fullPath = Join-Path $VaultRoot $relativePath
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        Add-Failure "正式文章不存在：$relativePath"
        continue
    }

    $content = Get-Content -LiteralPath $fullPath -Raw -Encoding UTF8
    $formalContents[$relativePath] = $content
    $h1Matches = [regex]::Matches($content, '(?m)^#\s+([^#].*?)\s*$')
    if ($h1Matches.Count -ne 1) {
        Add-Failure "正式文章必须恰好有一个 H1：$relativePath（当前 $($h1Matches.Count) 个）"
    }
    else {
        $title = $h1Matches[0].Groups[1].Value.Trim()
        if (-not $titleToPaths.ContainsKey($title)) {
            $titleToPaths[$title] = [System.Collections.Generic.List[string]]::new()
        }
        $titleToPaths[$title].Add($relativePath)
    }

    if ($content.Trim().Length -lt 900) {
        Add-Failure "正式文章内容过浅：$relativePath（$($content.Trim().Length) 字符）"
    }

    if ($relativePath -notlike '知识库/00_知识库说明/*' -and
        $content -match '(?im)(?:^|\s)(TODO|TBD)(?:\s|$)|待补充|占位内容') {
        Add-Failure "正式文章包含未收口占位内容：$relativePath"
    }

    if ($content -match '\[\[(?:TA-Encyclopedia|system_prompt)') {
        Add-Failure "正式文章仍链接旧结构：$relativePath"
    }
}

foreach ($entry in $titleToPaths.GetEnumerator()) {
    if ($entry.Value.Count -gt 1) {
        Add-Failure "重复 H1：$($entry.Key) -> $($entry.Value -join '；')"
    }
}

$allMarkdown = @(Get-PublicMarkdownFiles)
$pathIndex = @{}
$nameIndex = @{}
foreach ($file in $allMarkdown) {
    $relativePath = $file.FullName.Substring($VaultRoot.Length + 1).Replace('\', '/')
    $pathIndex[$relativePath.ToLowerInvariant()] = $relativePath
    $leaf = $file.BaseName.ToLowerInvariant()
    if (-not $nameIndex.ContainsKey($leaf)) {
        $nameIndex[$leaf] = [System.Collections.Generic.List[string]]::new()
    }
    $nameIndex[$leaf].Add($relativePath)
}

$linkSources = @($uniqueFormalPaths) + @('README.md')
$inboundFormal = @{}
foreach ($relativePath in $linkSources | Sort-Object -Unique) {
    $fullPath = Join-Path $VaultRoot $relativePath
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) { continue }
    $content = Get-Content -LiteralPath $fullPath -Raw -Encoding UTF8
    foreach ($match in [regex]::Matches($content, '\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')) {
        $target = $match.Groups[1].Value.Trim()
        if (-not (Resolve-WikiLink -Target $target -PathIndex $pathIndex -NameIndex $nameIndex)) {
            Add-Failure "断裂 Wikilink：$relativePath -> [[$target]]"
            continue
        }

        $normalized = ($target -split '#', 2)[0].Trim().Replace('\', '/')
        if (-not $normalized.EndsWith('.md')) { $normalized += '.md' }
        $resolved = $null
        if ($pathIndex.ContainsKey($normalized.ToLowerInvariant())) {
            $resolved = $pathIndex[$normalized.ToLowerInvariant()]
        }
        else {
            $leaf = [System.IO.Path]::GetFileNameWithoutExtension($normalized).ToLowerInvariant()
            if ($nameIndex.ContainsKey($leaf) -and $nameIndex[$leaf].Count -eq 1) {
                $resolved = $nameIndex[$leaf][0]
            }
        }
        if ($resolved -and $resolved -in $uniqueFormalPaths -and $resolved -ne $relativePath) {
            $inboundFormal[$resolved] = $true
        }
    }
}

foreach ($relativePath in $uniqueFormalPaths) {
    if ($relativePath -eq '00_知识库说明/知识地图.md') { continue }
    if (-not $inboundFormal.ContainsKey($relativePath)) {
        Add-Failure "正式文章没有来自正式入口或其他正式文章的入链：$relativePath"
    }
}

$allowedStatuses = @(
    '已覆盖',
    '重复内容已覆盖',
    '保留治理'
)
if ($AllowPendingCoverage) {
    $allowedStatuses += '待覆盖核验'
}
$inventoryRows = @(Import-Csv -LiteralPath $inventoryPath -Delimiter "`t")

$trackedPrivatePaths = @(& git -c core.quotepath=false -C $VaultRoot ls-files | Where-Object {
    $_ -match '(^|/)文字记录(/|$)' -or
        $_ -match '文字记录.*\.zip$' -or
        $_ -match '^\.obsidian/workspace.*\.json$' -or
        $_ -match '(^|/)\.env(?:\.|$)' -or
        $_ -match '\.(?:key|pem|p12|pfx|secret)$'
})
foreach ($path in $trackedPrivatePaths) {
    Add-Failure "公开仓库仍跟踪私密或本机状态文件：$path"
}

foreach ($row in $inventoryRows | Where-Object {
    $_.source_path -match '(^|[\\/])文字记录([\\/]|$)' -or
        $_.source_path -match '文字记录.*\.zip$' -or
        $_.source_path -match '(^|[\\/])\.obsidian[\\/]workspace.*\.json$'
}) {
    Add-Failure "公开来源台账包含私密路径：$($row.source_path)"
}

$slideTitlePath = Join-Path $VaultRoot 'docs\manifests\pptx-slide-titles.tsv'
if (Test-Path -LiteralPath $slideTitlePath) {
    $privateSlideRows = @(Import-Csv -LiteralPath $slideTitlePath -Delimiter "`t" | Where-Object {
        $_.source_path -match '(^|[\\/])文字记录([\\/]|$)' -or
            $_.source_path -match '文字记录.*\.zip$'
    })
    if ($privateSlideRows.Count -gt 0) {
        Add-Failure "公开幻灯片索引包含 $($privateSlideRows.Count) 条私密来源预览。"
    }
}

$courseRoots = @(
    '课程记录\Games104', '课程记录\图形工程', '课程记录\图形学',
    '课程记录\数据结构和算法', '课程记录\C++基础', '课程记录\编辑器设计',
    '课程记录\游戏AI', '课程记录\游戏网络', '课程记录\ACT'
)
$courseFiles = @()
foreach ($courseRoot in $courseRoots) {
    $coursePath = Join-Path $VaultRoot $courseRoot
    $rootFiles = @(Get-ChildItem -LiteralPath $coursePath -File -Filter '*.md')
    $courseFiles += $rootFiles
    foreach ($file in $rootFiles) {
        if ($file.Name -notmatch '^\d{2}-.+\.md$') {
            Add-Failure "课程笔记命名不符合两位序号规则：$courseRoot/$($file.Name)"
        }
    }
}

$renameManifestPath = Join-Path $VaultRoot 'docs\manifests\course-renames.tsv'
if (-not (Test-Path -LiteralPath $renameManifestPath)) {
    Add-Failure '缺少课程笔记命名映射：docs/manifests/course-renames.tsv'
}
else {
    foreach ($row in Import-Csv -LiteralPath $renameManifestPath -Delimiter "`t") {
        if (Test-Path -LiteralPath (Join-Path $VaultRoot $row.old_path)) {
            Add-Failure "课程笔记旧路径仍存在：$($row.old_path)"
        }
        if (-not (Test-Path -LiteralPath (Join-Path $VaultRoot $row.new_path) -PathType Leaf)) {
            Add-Failure "课程笔记新路径不存在：$($row.new_path)"
        }
    }
}

$coveragePath = Join-Path $VaultRoot 'docs\manifests\course-coverage.tsv'
if (-not (Test-Path -LiteralPath $coveragePath -PathType Leaf)) {
    Add-Failure '缺少课程章节覆盖台账：docs/manifests/course-coverage.tsv'
}
else {
    $coverageRows = @(Import-Csv -LiteralPath $coveragePath -Delimiter "`t")
    $coverageIndex = @{}
    foreach ($row in $coverageRows) {
        $sourcePath = $row.source_path.Replace('\', '/')
        $key = "$sourcePath|$($row.section_line)"
        if ($coverageIndex.ContainsKey($key)) {
            Add-Failure "课程章节覆盖台账包含重复行：$key"
        }
        $coverageIndex[$key] = $row

        if (-not $row.target_article) {
            Add-Failure "课程章节没有目标文章：$key"
        }
        if ($row.coverage_status -match '非\s*TA|跳过|不相关') {
            Add-Failure "课程章节使用了禁止的跳过状态：$key -> $($row.coverage_status)"
        }
        $allowedCoverageStatuses = @('已覆盖', '重复内容已覆盖')
        if ($AllowPendingCoverage) { $allowedCoverageStatuses += '已映射' }
        if ($row.coverage_status -notin $allowedCoverageStatuses) {
            Add-Failure "课程章节覆盖状态无效：$key -> $($row.coverage_status)"
        }

        foreach ($targetArticle in $row.target_article -split '；') {
            $normalizedTarget = $targetArticle.Trim().Replace('\', '/')
            if (-not $normalizedTarget) { continue }
            if (-not $AllowPendingCoverage -and
                -not (Test-Path -LiteralPath (Join-Path $VaultRoot $normalizedTarget) -PathType Leaf)) {
                Add-Failure "课程章节目标文章不存在：$key -> $normalizedTarget"
            }
        }
    }

    $expectedCoverageKeys = @{}
    foreach ($file in $courseFiles) {
        $relative = $file.FullName.Substring($VaultRoot.Length + 1).Replace('\', '/')
        $lineNumber = 0
        foreach ($line in Get-Content -LiteralPath $file.FullName -Encoding UTF8) {
            $lineNumber++
            if ($line -match '^##\s+') {
                $key = "$relative|$lineNumber"
                $expectedCoverageKeys[$key] = $true
                if (-not $coverageIndex.ContainsKey($key)) {
                    Add-Failure "公开课程章节未进入覆盖台账：$key"
                }
            }
        }
    }
    foreach ($key in $coverageIndex.Keys) {
        if (-not $expectedCoverageKeys.ContainsKey($key)) {
            Add-Failure "覆盖台账包含过期章节：$key"
        }
    }
}

foreach ($group in $inventoryRows | Group-Object migration_status) {
    if ($group.Name -notin $allowedStatuses) {
        Add-Failure "迁移台账仍有非终态：$($group.Name)（$($group.Count) 项）"
    }
}

foreach ($row in $inventoryRows | Where-Object migration_status -eq '已退役') {
    $retiredPath = Join-Path $VaultRoot $row.source_path
    if (Test-Path -LiteralPath $retiredPath) {
        Add-Failure "已退役来源仍存在：$($row.source_path)"
    }
}
foreach ($row in $inventoryRows | Where-Object migration_status -eq '排除') {
    $excludedPath = Join-Path $VaultRoot $row.source_path
    if (Test-Path -LiteralPath $excludedPath) {
        Add-Failure "已排除来源仍存在：$($row.source_path)"
    }
}

$conceptValidatorPath = Join-Path $VaultRoot 'scripts\validate-course-concepts.ps1'
if (-not (Test-Path -LiteralPath $conceptValidatorPath -PathType Leaf)) {
    Add-Failure '缺少课程概念覆盖验证脚本。'
}
else {
    try {
        & $conceptValidatorPath -VaultRoot $VaultRoot
    }
    catch {
        Add-Failure $_.Exception.Message
    }
}

Write-Host "正式文章：$($uniqueFormalPaths.Count)"
Write-Host "来源台账：$($inventoryRows.Count)"
Write-Host "警告：$($warnings.Count)"
Write-Host "失败：$($failures.Count)"

foreach ($warning in $warnings) { Write-Warning $warning }
foreach ($failure in $failures) { Write-Host "[FAIL] $failure" -ForegroundColor Red }

if ($failures.Count -gt 0) { exit 1 }
Write-Host '个人知识库验证通过。' -ForegroundColor Green
