param([ValidateSet('Install','Status','Remove')][string]$Mode = 'Status')
$ErrorActionPreference = 'Stop'
$checkpointRoot = Split-Path -Parent $PSScriptRoot
$checkpointName = 'EBT-Enterprise-GitHub-Reviewed-Checkpoint'
$existingCheckpointTask = Get-ScheduledTask -TaskName $checkpointName -ErrorAction SilentlyContinue
$checkpointRunner = Join-Path $PSScriptRoot 'Run-Checkpoint.ps1'
if ($existingCheckpointTask -and $existingCheckpointTask.Actions.Arguments -notlike ('*' + $checkpointRunner + '*')) {
    throw 'Uma tarefa com esse nome pertence a outro destino. Não foi alterada.'
}
if ($Mode -eq 'Remove') {
    if ($existingCheckpointTask) { Unregister-ScheduledTask -TaskName $checkpointName -Confirm:$false }
    Write-Output 'Agendamento removido; arquivos, commits e branch preservados.'
    exit 0
}
if ($Mode -eq 'Install') {
    $checkpointPython = (Get-Command python -ErrorAction Stop).Source
    $checkpointGit = (Get-Command git -ErrorAction Stop).Source
    # Validate destination/config before installing anything. No secret or cloud service is created.
    & $checkpointPython (Join-Path $PSScriptRoot 'checkpoint_github.py') --dry-run
    if ($LASTEXITCODE -ne 0) { throw 'O manifesto ainda precisa de revisão. Agendamento não instalado.' }
    $checkpointArguments = '-NoProfile -NonInteractive -WindowStyle Hidden -File "' + $checkpointRunner + '" -Python "' + $checkpointPython + '"'
    $checkpointAction = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $checkpointArguments -WorkingDirectory $checkpointRoot
    $checkpointTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(5) -RepetitionInterval (New-TimeSpan -Minutes 5)
    $checkpointPrincipal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
    $checkpointSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 4) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName $checkpointName -Action $checkpointAction -Trigger $checkpointTrigger -Principal $checkpointPrincipal -Settings $checkpointSettings -Description 'Retry reviewed EBT checkpoints without AI credits, deployment, secrets or force push.' -Force | Out-Null
}
if (Get-ScheduledTask -TaskName $checkpointName -ErrorAction SilentlyContinue) {
    Get-ScheduledTask -TaskName $checkpointName | Select-Object TaskName, State
    Get-ScheduledTaskInfo -TaskName $checkpointName | Select-Object LastRunTime, LastTaskResult, NextRunTime
} else { Write-Output 'Agendamento não instalado.' }
