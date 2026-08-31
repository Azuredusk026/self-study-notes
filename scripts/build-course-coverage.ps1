param(
    [string]$VaultRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$targetPath = Join-Path $VaultRoot 'docs\manifests\course-targets.tsv'
$coveragePath = Join-Path $VaultRoot 'docs\manifests\course-coverage.tsv'
$courseRoots = @(
    'Games104', '图形工程', '图形学', '数据结构和算法', 'C++基础',
    '编辑器设计', '游戏AI', '游戏网络', 'ACT'
)

if (-not (Test-Path -LiteralPath $targetPath -PathType Leaf)) {
    throw "课程目标映射不存在：$targetPath"
}

$targets = @(Import-Csv -LiteralPath $targetPath -Delimiter "`t")
$targetIndex = @{}
foreach ($target in $targets) {
    $key = $target.source_path.Replace('\', '/')
    if ($targetIndex.ContainsKey($key)) {
        throw "课程目标映射包含重复路径：$key"
    }
    $targetIndex[$key] = $target
}

$courseFiles = @(
    foreach ($courseRoot in $courseRoots) {
        Get-ChildItem -LiteralPath (Join-Path $VaultRoot $courseRoot) -File -Filter '*.md'
    }
)
$coursePaths = @{}
foreach ($file in $courseFiles) {
    $relative = $file.FullName.Substring($VaultRoot.Length + 1).Replace('\', '/')
    $coursePaths[$relative] = $file
    if (-not $targetIndex.ContainsKey($relative)) {
        throw "课程笔记缺少目标映射：$relative"
    }
}
foreach ($key in $targetIndex.Keys) {
    if (-not $coursePaths.ContainsKey($key)) {
        throw "课程目标映射指向不存在的公开笔记：$key"
    }
}

$coverageRows = foreach ($relative in $coursePaths.Keys | Sort-Object) {
    $file = $coursePaths[$relative]
    $target = $targetIndex[$relative]
    $lineNumber = 0
    $sectionCount = 0
    foreach ($line in Get-Content -LiteralPath $file.FullName -Encoding UTF8) {
        $lineNumber++
        if ($line -match '^##\s+(.+?)\s*$') {
            $sectionCount++
            [pscustomobject]@{
                source_path = $relative
                section_line = $lineNumber
                section_heading = $matches[1].Trim()
                target_article = $target.target_article
                coverage_status = $target.coverage_status
                notes = $target.notes
            }
        }
    }
    if ($sectionCount -eq 0) {
        throw "课程笔记没有 H2 章节：$relative"
    }
}

$coverageRows | ConvertTo-Csv -Delimiter "`t" -NoTypeInformation |
    Set-Content -LiteralPath $coveragePath -Encoding UTF8

Write-Host "Wrote $coveragePath"
Write-Host "Mapped $($courseFiles.Count) course notes and $($coverageRows.Count) H2 sections."
