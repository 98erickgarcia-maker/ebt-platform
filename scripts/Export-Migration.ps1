$ErrorActionPreference='Stop'
$platformRoot=Split-Path $PSScriptRoot -Parent
$env:MSBuildEnableWorkloadResolver='false'
$sqlPath=Join-Path $platformRoot 'sql/connect-migrations.sql'
& dotnet tool run dotnet-ef migrations script --idempotent --no-build --project (Join-Path $platformRoot 'src/backend/Ebt.Platform.Api') --output $sqlPath
if ($LASTEXITCODE -ne 0) {throw 'Exportação da migration falhou'}
$migrationSql=[System.IO.File]::ReadAllText($sqlPath)
$header=@'
-- EBT-only schema. No CREATE DATABASE or other product schema mutations.
-- Reviewed target: existing sqldb-crm-casst-dev-v2; local rehearsal: EbtPlatformQa_*.
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET ARITHABORT ON;
SET NUMERIC_ROUNDABORT OFF;
SET XACT_ABORT ON;
GO
IF DB_NAME() <> N'sqldb-crm-casst-dev-v2' AND LEFT(DB_NAME(),14) <> N'EbtPlatformQa_'
    THROW 51011, 'Wrong EBT shared or synthetic QA database.', 1;
IF SCHEMA_ID(N'ebt_connect') IS NOT NULL AND OBJECT_ID(N'ebt_connect.__EFMigrationsHistory') IS NULL
   AND EXISTS(SELECT 1 FROM sys.tables WHERE schema_id=SCHEMA_ID(N'ebt_connect'))
    THROW 51012, 'Existing EBT tables without reviewed migration history.', 1;
GO
'@
[System.IO.File]::WriteAllText($sqlPath,$header+"`n"+$migrationSql,(New-Object System.Text.UTF8Encoding($false)))
Write-Output 'Migration idempotente exportada com destino e opções SQL explícitos.'
