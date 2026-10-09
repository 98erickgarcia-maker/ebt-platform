param(
    [ValidateSet('inspect','apply')][string]$Operation = 'inspect',
    [ValidatePattern('^[a-fA-F0-9]{64}$')][string]$ApprovedSha256
)
$ErrorActionPreference = 'Stop'
$platformRoot = Split-Path $PSScriptRoot -Parent
if ($Operation -eq 'apply' -and !$ApprovedSha256) { throw 'Reviewed script SHA is required.' }
$env:EBT_RUNTIME_CONFIG = Join-Path $platformRoot 'tmp/runtime/local-config.json'
$env:ConnectionStrings__Platform = 'Server=tcp:sql-crm-casst-dev-crmenterprise98.database.windows.net,1433;Initial Catalog=sqldb-crm-casst-dev-v2;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30'
$env:Platform__CatalogOperation = $Operation
$env:Platform__CatalogScript = Join-Path $platformRoot 'sql/platform-catalog.sql'
$env:Platform__CatalogApprovedSha256 = $ApprovedSha256
$env:Platform__CatalogReport = Join-Path $platformRoot ('evidencias/platform_azure_' + $Operation + '_20261009.json')
try {
    $platformSqlToken = & az account get-access-token --resource https://database.windows.net/ --query accessToken -o tsv
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($platformSqlToken)) { throw 'Temporary Azure SQL token unavailable.' }
    $env:EBT_SQL_ACCESS_TOKEN = $platformSqlToken.Trim()
    & dotnet (Join-Path $platformRoot 'src/backend/Ebt.Platform.Api/bin/Release/net10.0/Ebt.Platform.Api.dll') --platform-database
    if ($LASTEXITCODE -ne 0) { throw 'Database operation failed; preserve evidence and inspect before retry.' }
} finally {
    foreach ($platformVariable in @('EBT_SQL_ACCESS_TOKEN','EBT_RUNTIME_CONFIG','ConnectionStrings__Platform','Platform__CatalogOperation','Platform__CatalogScript','Platform__CatalogApprovedSha256','Platform__CatalogReport')) {
        Remove-Item -LiteralPath ('Env:' + $platformVariable) -ErrorAction SilentlyContinue
    }
    $platformSqlToken = $null
}
