param(
    [string]$VaultRoot = (Split-Path -Parent $PSScriptRoot),
    [int]$ExpectedFormalCount = 55
)

$ErrorActionPreference = 'Stop'
$failures = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()

function Add-Failure {
    param([string]$Message)
    $failures.Add($Message)
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

    if ($relativePath -notlike '00_知识库说明/*' -and
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

$allMarkdown = @(Get-ChildItem -LiteralPath $VaultRoot -Recurse -File -Filter '*.md' | Where-Object {
    $_.FullName -notmatch '\\.git\\|\\.obsidian\\'
})
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
    '已迁移',
    '已筛选迁移',
    '已拆分迁移',
    '重复来源已覆盖',
    '保留归档',
    '排除',
    '保留治理',
    '已退役'
)
$inventoryRows = @(Import-Csv -LiteralPath $inventoryPath -Delimiter "`t")
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

Write-Host "正式文章：$($uniqueFormalPaths.Count)"
Write-Host "来源台账：$($inventoryRows.Count)"
Write-Host "警告：$($warnings.Count)"
Write-Host "失败：$($failures.Count)"

foreach ($warning in $warnings) { Write-Warning $warning }
foreach ($failure in $failures) { Write-Host "[FAIL] $failure" -ForegroundColor Red }

if ($failures.Count -gt 0) { exit 1 }
Write-Host 'Technical Art 知识库验证通过。' -ForegroundColor Green
