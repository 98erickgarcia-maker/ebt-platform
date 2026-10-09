$ErrorActionPreference = 'Stop'
$inv = Get-Content evidencias/inventario_fontes.json -Raw | ConvertFrom-Json
$ids = @('F01','F02','F03','F10','F11','F13','F17','F19','F21','F26')
$refs = foreach ($r in $inv.referencias | Where-Object id -in $ids) {
  $exists = Test-Path -LiteralPath $r.path
  $hash = if ($exists) { (Get-FileHash -LiteralPath $r.path -Algorithm SHA256).Hash.ToLower() } else { $null }
  [ordered]@{ id=$r.id; path=$r.path; exists=$exists; sha256=$hash; historical_sha256=$r.sha256; equivalent=($hash -eq $r.sha256) }
}
$projects = foreach ($p in $inv.projetos | Where-Object nome -in @('CASST','Vikings','EBT institucional','CRP aplicação','Nutrição')) {
  $files = @(rg --files $p.path -g '*LICENSE*' -g '*NOTICE*' -g '*COPYING*' -g '!node_modules' -g '!bin' -g '!obj' -g '!outputs' -g '!output')
  [ordered]@{ project=$p.nome; source=$p.path; license_notice_files=$files; limitation='Busca de nomes em arquivos não ignorados; não abrange contratos externos nem dependências instaladas.' }
}
$casst = ($inv.projetos | Where-Object nome -eq 'CASST').path
$frontend = Join-Path $casst 'src/frontend/package.json'
$lockpath = Join-Path $casst 'src/frontend/package-lock.json'
$pkg = Get-Content -LiteralPath $frontend -Raw | ConvertFrom-Json -AsHashtable
$lock = Get-Content -LiteralPath $lockpath -Raw | ConvertFrom-Json -AsHashtable
$npm = foreach ($entry in $lock.packages.GetEnumerator()) {
  if ($entry.Key -ne '') { [ordered]@{ package_path=$entry.Key; version=$entry.Value.version; declared_license=$entry.Value.license; dev=$entry.Value.dev } }
}
$nuget = foreach ($project in @(rg --files (Join-Path $casst 'src/backend') -g '*.csproj' -g '!obj' -g '!bin')) {
  [xml]$xml = Get-Content -LiteralPath $project -Raw
  foreach ($ref in $xml.Project.ItemGroup.PackageReference) {
    if ($ref.Include) { [ordered]@{ project=$project.Substring($casst.Length+1); package=$ref.Include; version=$ref.Version; license_status='Não verificada: exige pacote exato e licença/NOTICE.' } }
  }
}
$result = [ordered]@{ collected_utc=[DateTime]::UtcNow.ToString('o'); scope='P01-05; metadados somente leitura, sem cópia de código, assets, cliente ou credenciais'; references=@($refs); projects=@($projects); frontend_manifest_sha256=(Get-FileHash $frontend).Hash.ToLower(); frontend_lock_sha256=(Get-FileHash $lockpath).Hash.ToLower(); direct_dependencies=$pkg.dependencies; npm_locked_packages=@($npm); nuget_direct_references=@($nuget) }
$result | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath evidencias/execucao/PAC-01/direitos/inventario.json -Encoding utf8
