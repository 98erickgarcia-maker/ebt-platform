param([switch]$Initialize, [switch]$Build, [ValidateRange(1024,65535)][int]$Port = 5186)
$ErrorActionPreference = 'Stop'
$platformRoot = Split-Path $PSScriptRoot -Parent
$runtimePath = Join-Path $platformRoot 'tmp/runtime'
New-Item -ItemType Directory -Path $runtimePath -Force | Out-Null
$configPath = Join-Path $runtimePath 'local-config.json'
if (!(Test-Path -LiteralPath $configPath)) {
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes)
    $rng.Dispose()
    $qaSecret = [BitConverter]::ToString($bytes).Replace('-','').ToLowerInvariant()
    $runtimeConfig = @{
        ConnectionStrings = @{ Platform = 'Server=localhost;Database=EbtPlatformQa_20261007Migrated;Integrated Security=True;Encrypt=True;TrustServerCertificate=True' }
        Platform = @{ KeyPath = (Join-Path $runtimePath 'keys'); RunWorkers = $true }
        Qa = @{ Password = ('EbtQa9!' + $qaSecret.Substring(0,24)); AccessFile = (Join-Path $runtimePath 'qa-access.json'); AppSecret = $qaSecret; VerifyToken = ('verify-' + $qaSecret) }
    }
    $runtimeConfig | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $configPath -Encoding utf8
}
$env:ASPNETCORE_ENVIRONMENT = 'Development'
$env:EBT_RUNTIME_CONFIG = $configPath
$env:MSBuildEnableWorkloadResolver = 'false'
$project = Join-Path $platformRoot 'src/backend/Ebt.Platform.Api/Ebt.Platform.Api.csproj'
if ($Build) { & dotnet build $project; if ($LASTEXITCODE -ne 0) { throw 'Build falhou' } }
if ($Initialize) { & dotnet run --no-build --project $project -- --init-qa; if ($LASTEXITCODE -ne 0) { throw 'Inicialização QA falhou' }; return }
& dotnet run --no-build --project $project --urls "http://127.0.0.1:$Port"
exit $LASTEXITCODE
