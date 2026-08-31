param(
    [Parameter(Mandatory = $true)]
    [string]$TargetDomain,

    [Parameter(Mandatory = $true)]
    [string]$TargetArticles,

    [string]$Status = '已迁移',

    [string]$Notes = '已在正式主题中去重、核验并吸收。',

    [string]$VaultRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$inventoryPath = Join-Path $VaultRoot 'docs\manifests\source-inventory.tsv'

if (-not (Test-Path -LiteralPath $inventoryPath)) {
    throw "Migration inventory not found: $inventoryPath"
}

$rows = Import-Csv -Delimiter "`t" -LiteralPath $inventoryPath
$updated = 0

foreach ($row in $rows) {
    if ($row.target_domain -eq $TargetDomain) {
        $row.migration_status = $Status
        $row.target_article = $TargetArticles
        $row.notes = $Notes
        $updated++
    }
}

if ($updated -eq 0) {
    throw "No source rows matched target domain: $TargetDomain"
}

$rows | ConvertTo-Csv -Delimiter "`t" -NoTypeInformation |
    Set-Content -LiteralPath $inventoryPath -Encoding UTF8

Write-Host "Updated $updated source rows for $TargetDomain."
