$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$encryptedKey=(Get-Content -LiteralPath (Join-Path $root 'tmp/private-integrations/wazvox-key.dpapi') -Raw).Trim()
$secure=ConvertTo-SecureString $encryptedKey
$credential=New-Object PSCredential('wazvox',$secure)
$headers=@{Authorization=('Bearer '+$credential.GetNetworkCredential().Password)}
$observed=[ordered]@{generatedUtc=[DateTimeOffset]::UtcNow.ToString('o');provider='wazvox';baseUrl='https://app.wazvox.com/api/v1';checks=@()}
foreach($endpoint in @('me','numbers','webhook-subscriptions')) {
 try {
  $response=Invoke-WebRequest -UseBasicParsing -Uri ('https://app.wazvox.com/api/v1/'+$endpoint) -Headers $headers
  $parsed=$response.Content | ConvertFrom-Json
  if ($endpoint -eq 'me' -and ($parsed.data.tenantName -ne 'EBTenterprise' -or $parsed.data.apiKeyName -ne 'EBT Connect')) {throw 'Conta ou chave divergente'}
  if ($endpoint -eq 'numbers') {
   $selected=@($parsed.data | Where-Object { $_.phoneNumberId -eq '1295941046927902' -and $_.wabaId -eq '1532581995165944' -and $_.registered -eq $true -and $_.connectionStatus -eq 'connected' })
   if ($selected.Count -ne 1) {throw 'Número configurado divergente ou desconectado'}
   $observed.numberRegistered=$true; $observed.numberConnected=$true; $observed.onboardingMode=$selected[0].onboardingMode
  }
  $response.Content | Set-Content -LiteralPath (Join-Path $root ('tmp/private-integrations/wazvox-'+$endpoint+'.json')) -Encoding utf8
  $observed.checks+=@{endpoint=$endpoint;httpStatus=[int]$response.StatusCode;passed=([int]$response.StatusCode -eq 200)}
 } catch { $observed.checks+=@{endpoint=$endpoint;passed=$false;errorType=$_.Exception.GetType().Name}; }
}
$headers.Clear(); $credential=$null
$observed | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $root 'evidencias/integracao_wazvox_leitura.json') -Encoding utf8
$observed | ConvertTo-Json -Depth 5
