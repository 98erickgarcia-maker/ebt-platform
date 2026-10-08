$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$configPath=Join-Path $root 'tmp/runtime/wazvox-qa-config.json'
$config=Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
if ($config.ConnectionStrings.Platform -ne 'Server=localhost;Database=EbtPlatformQa_20261007Migrated;Integrated Security=True;Encrypt=True;TrustServerCertificate=True') {throw 'Somente fixture local exclusiva'}
if ($config.WazVox.Connections.PSObject.Properties.Count -gt 0) {throw 'QA não permite credenciais externas'}
if (Get-ChildItem Env: | Where-Object { $_.Name -match '^(WazVox|Meta)__Connections__.+__(ApiKey|AccessToken)$' -and $_.Value }) {throw 'Remova credenciais de provedor do ambiente antes da QA sintética'}
$env:ASPNETCORE_ENVIRONMENT='Development'
$env:EBT_RUNTIME_CONFIG=$configPath
$env:MSBuildEnableWorkloadResolver='false'
Set-Location -LiteralPath (Join-Path $root 'src/backend/Ebt.Platform.Api')
& dotnet (Join-Path $root 'src/backend/Ebt.Platform.Api/bin/Debug/net10.0/Ebt.Platform.Api.dll') --urls http://127.0.0.1:5186
exit $LASTEXITCODE
