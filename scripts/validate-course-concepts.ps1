param(
    [string]$VaultRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$manifestPath = Join-Path $VaultRoot 'docs\manifests\course-concept-targets.tsv'

if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw '缺少课程概念覆盖台账：docs/manifests/course-concept-targets.tsv'
}

$rows = @(Import-Csv -LiteralPath $manifestPath -Delimiter "`t")
if ($rows.Count -eq 0) {
    throw '课程概念覆盖台账为空。'
}

$failures = [System.Collections.Generic.List[string]]::new()
$keys = @{}

foreach ($row in $rows) {
    $key = "$($row.concept)|$($row.target_article)"
    if ($keys.ContainsKey($key)) {
        $failures.Add("课程概念覆盖台账包含重复行：$key")
    }
    $keys[$key] = $true

    if ($row.coverage_status -ne '已覆盖') {
        $failures.Add("课程概念状态不是终态：$($row.concept) -> $($row.coverage_status)")
    }

    $targetPath = Join-Path $VaultRoot $row.target_article
    if (-not (Test-Path -LiteralPath $targetPath -PathType Leaf)) {
        $failures.Add("课程概念目标文章不存在：$($row.concept) -> $($row.target_article)")
        continue
    }

    $content = Get-Content -LiteralPath $targetPath -Raw -Encoding UTF8
    $aliases = @($row.aliases -split '\|' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    if ($aliases.Count -eq 0) {
        $failures.Add("课程概念没有检索别名：$($row.concept)")
    }
    elseif (-not ($aliases | Where-Object { $content.IndexOf($_, [System.StringComparison]::OrdinalIgnoreCase) -ge 0 })) {
        $failures.Add("目标文章未命中课程概念：$($row.concept) -> $($row.target_article)")
    }

    foreach ($source in $row.source_examples -split '；') {
        $sourcePath = $source.Trim()
        if (-not $sourcePath) { continue }
        if ($sourcePath -match '文字记录') {
            $failures.Add("课程概念台账包含私密来源：$($row.concept)")
        }
        elseif (-not (Test-Path -LiteralPath (Join-Path $VaultRoot $sourcePath) -PathType Leaf)) {
            $failures.Add("课程概念证据来源不存在：$($row.concept) -> $sourcePath")
        }
    }
}

Write-Host "课程概念：$($rows.Count)"
Write-Host "概念失败：$($failures.Count)"
foreach ($failure in $failures) {
    Write-Host "[FAIL] $failure" -ForegroundColor Red
}

if ($failures.Count -gt 0) {
    throw '课程概念覆盖验证失败。'
}

Write-Host '课程概念覆盖验证通过。' -ForegroundColor Green
