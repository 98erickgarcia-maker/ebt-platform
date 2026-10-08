$ErrorActionPreference = 'Stop'
$platformRoot = Split-Path $PSScriptRoot -Parent
$env:EBT_RUNTIME_CONFIG = Join-Path $platformRoot 'tmp/runtime/local-config.json'
$env:Platform__InspectionOutput = Join-Path $platformRoot 'evidencias/azure_sql_compartilhado_metadados.json'
$env:ConnectionStrings__Platform = 'Server=tcp:sql-crm-casst-dev-crmenterprise98.database.windows.net,1433;Initial Catalog=sqldb-crm-casst-dev-v2;Encrypt=True;TrustServerCertificate=False;Connection Timeout=20'
try {
    $platformSqlToken = & az account get-access-token --resource https://database.windows.net/ --query accessToken -o tsv
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($platformSqlToken)) { throw 'Sem token Azure SQL para inspeção' }
    $env:EBT_SQL_ACCESS_TOKEN = $platformSqlToken.Trim()
    & dotnet run --no-build --project (Join-Path $platformRoot 'src/backend/Ebt.Platform.Api/Ebt.Platform.Api.csproj') -- --inspect-azure
    if ($LASTEXITCODE -ne 0) { throw 'Inspeção somente leitura não foi concluída' }
} finally {
    Remove-Item Env:EBT_SQL_ACCESS_TOKEN -ErrorAction SilentlyContinue
    Remove-Item Env:ConnectionStrings__Platform -ErrorAction SilentlyContinue
    Remove-Item Env:Platform__InspectionOutput -ErrorAction SilentlyContinue
    $platformSqlToken = $null
}
