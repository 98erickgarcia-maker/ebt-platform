"""Package public source and exported runtime; private files are never inputs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import zipfile

root = Path(__file__).resolve().parents[1]
publication = json.loads((root / 'evidencias/azure_connect_publicacao.json').read_text(encoding='utf-8'))
if publication.get('published') is not True:
    raise RuntimeError('A verified publication is required for this online package')
version = publication['version']
if not re.fullmatch(r'\d+\.\d+\.\d+', version):
    raise RuntimeError('Invalid release version')
output = root / f'tmp/release/EBT_Plataform_Connect_{version}_Online_Solucao.zip'
allowed = {'.cs', '.csproj', '.ts', '.tsx', '.css', '.html', '.json', '.py', '.ps1', '.md', '.sql', '.yml', '.yaml', '.props', '.targets'}
excluded = {'bin', 'obj', 'node_modules', 'dist', 'wwwroot', '__pycache__', 'playwright-report', 'test-results', '.git'}
sources = []
for name in ['src', 'scripts', 'tests', 'deployment', 'docs', 'planejamento', 'templates', 'sql', 'evidencias', '.config', '.github']:
    sources += [p for p in (root / name).rglob('*') if p.is_file() and not any(x in excluded for x in p.relative_to(root).parts) and (p.suffix in allowed or p.name == 'Dockerfile') and p.name != 'manifesto_connect_local.json']
sources += [p for p in root.iterdir() if p.is_file() and (p.suffix == '.md' or p.name in {'.env.example', '.gitignore', '.gitattributes'})]
sources.append(root / 'evidencias/connect_primeira_entrega_online.png')
secrets = [value.encode() for value in json.loads(os.environ.get('EBT_DELIVERY_AUDIT_SECRETS', '[]')) if len(value) >= 16]
records = []


def add(archive, relative, data):
    if any(value in data for value in secrets) or re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bEAA[A-Za-z0-9]{65,}', data):
        raise RuntimeError('Private credential detected in ' + relative)
    archive.writestr('EBT_PLATAFORM/' + relative, data)
    records.append({'path': relative, 'sha256': hashlib.sha256(data).hexdigest()})


readme = f'''# EBT Connect - solução {version} online

Publicado: https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io

1. Leia PASSO_A_PASSO_PUBLICACAO_CONNECT.md para acesso e provas.
2. Leia PASSO_A_PASSO_EBT_CONNECT.md para uso e execução local sintética.
3. Código .NET/React em src/, testes em tests/, SQL em sql/, implantação em deployment/.
4. Aplicação compilada e frontend pronto em runtime/, exigindo ASP.NET Core Runtime 10 e configuração privada própria.
5. MANIFESTO_ENTREGA.json registra os hashes dos arquivos deste ZIP.

Banco pago compartilhado existente, schema ebt_connect e identidade exclusiva do Connect. Sem banco novo ou alteração dos outros produtos. Primeira entrega: 26 verificações ao vivo e reinício; continuidade 0.1.4: probes HTTP/SQL e sessão preservada na troca de imagem.

Credenciais, certificados, tokens, bancos, configurações privadas e dados de clientes não acompanham este pacote. Não há senha no ZIP. Consulte evidencias/connect_wazvox_real_015.json para recebimento, resposta e leitura reais após correção do contrato de status. Scanner, recuperação Azure, CI hospedada e aceite continuam pendentes. Evidências históricas conservam suas versões; planejamento não é prova de execução.
'''
with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for path in sorted(set(sources)):
        add(archive, path.relative_to(root).as_posix(), path.read_bytes())
    runtime = root / f'tmp/release/connect-azure-{version}'
    if not (runtime / 'Ebt.Platform.Api.dll').is_file():
        raise RuntimeError('Compiled runtime missing for this release')
    for path in sorted(runtime.rglob('*')):
        if path.is_file():
            add(archive, 'runtime/' + path.relative_to(runtime).as_posix(), path.read_bytes())
    spec = root / 'tmp/integracao-wazvox/wazvox-v1.json'
    if spec.is_file():
        add(archive, 'docs/api/wazvox-openapi-v1.json', spec.read_bytes())
    add(archive, 'LEIA_PRIMEIRO_ENTREGA.md', readme.encode())
    manifest = {'generatedUtc': datetime.now(timezone.utc).isoformat(), 'version': version, 'published': True, 'privateCredentialsIncluded': False, 'files': records}
    archive.writestr('EBT_PLATAFORM/MANIFESTO_ENTREGA.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
with zipfile.ZipFile(output) as archive:
    assert archive.testzip() is None
    assert all(hashlib.sha256(archive.read('EBT_PLATAFORM/' + row['path'])).hexdigest() == row['sha256'] for row in records)
digest = hashlib.sha256(output.read_bytes()).hexdigest()
previous = root / 'evidencias/manifesto_connect_local.json'
old_manifest = json.loads(previous.read_text(encoding='utf-8'))
old_version = old_manifest['version'].removesuffix('-live')
history = root / f'evidencias/manifesto_connect_local_{old_version}.json'
if not history.exists():
    history.write_bytes(previous.read_bytes())
source_hashes = [{'path': p.relative_to(root).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(sources))]
previous.write_text(json.dumps({'version': version + '-live', 'generatedUtc': datetime.now(timezone.utc).isoformat(), 'published': True, 'azureSchemaApplied': True, 'containsRealCredentials': False, 'artifact': {'path': str(output.relative_to(root)), 'sha256': digest, 'bytes': output.stat().st_size}, 'imageDigest': publication['imageDigest'], 'files': source_hashes, 'liveProof': 'evidencias/connect_primeira_entrega_online.json', 'continuationProof': 'evidencias/connect_continuidade_disponibilidade.json', 'realMessagingProof': 'evidencias/connect_wazvox_real_015.json'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'zip': str(output), 'bytes': output.stat().st_size, 'files': len(records), 'integrity': 'passed', 'manifestHashes': 'passed', 'privateSecretComparison': bool(secrets), 'sha256': digest}))
