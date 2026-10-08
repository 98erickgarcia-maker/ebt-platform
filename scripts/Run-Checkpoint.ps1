param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$checkpointRoot = Split-Path -Parent $PSScriptRoot
$checkpointLog = Join-Path $checkpointRoot 'tmp\continuidade\agendador.log'
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $checkpointLog) | Out-Null
$env:PYTHONIOENCODING = 'utf-8'
$env:GIT_TERMINAL_PROMPT = '0'
$env:GCM_INTERACTIVE = 'Never'
# The scheduler retries reviewed snapshots only. It cannot approve changed bytes.
& $Python (Join-Path $PSScriptRoot 'checkpoint_github.py') --push *> $checkpointLog
exit $LASTEXITCODE
