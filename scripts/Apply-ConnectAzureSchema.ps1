param([Parameter(Mandatory=$true)][ValidatePattern('^[a-fA-F0-9]{64}$')][string]$ApprovedSha256)
$ErrorActionPreference='Stop'
$platformRoot=Split-Path $PSScriptRoot -Parent
$env:EBT_RUNTIME_CONFIG=Join-Path $platformRoot 'tmp/runtime/local-config.json'
$env:Platform__MigrationScript=Join-Path $platformRoot 'sql/connect-migrations.sql'
$env:Platform__MigrationApprovedSha256=$ApprovedSha256
$env:Platform__MigrationOutput=Join-Path $platformRoot 'evidencias/azure_connect_schema_aplicado.json'
$env:ConnectionStrings__Platform='Server=tcp:sql-crm-casst-dev-crmenterprise98.database.windows.net,1433;Initial Catalog=sqldb-crm-casst-dev-v2;Encrypt=True;TrustServerCertificate=False;Connection Timeout=20'
try {
    $platformSqlToken=& az account get-access-token --resource https://database.windows.net/ --query accessToken -o tsv
    if($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($platformSqlToken)){throw 'Sem token temporário Azure SQL'}
    $env:EBT_SQL_ACCESS_TOKEN=$platformSqlToken.Trim()
    & dotnet (Join-Path $platformRoot 'src/backend/Ebt.Platform.Api/bin/Release/net10.0/Ebt.Platform.Api.dll') --apply-reviewed-schema
    if($LASTEXITCODE -ne 0){throw 'Implantação de schema não concluída; conferir evidência antes de repetir'}
} finally {
    foreach($name in @('EBT_SQL_ACCESS_TOKEN','ConnectionStrings__Platform','Platform__MigrationScript','Platform__MigrationApprovedSha256','Platform__MigrationOutput','EBT_RUNTIME_CONFIG')){Remove-Item -LiteralPath ('Env:'+ $name) -ErrorAction SilentlyContinue}
    $platformSqlToken=$null
}
