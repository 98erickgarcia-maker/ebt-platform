"""Export only the reviewed checkpoint bytes, never the current dirty/private tree."""
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile
from checkpoint_github import CheckpointError, atomic_json, digest, git, safe_path, scan


def export(root):
    config=json.loads((root/'planejamento/continuidade_github.json').read_text(encoding='utf-8'))
    sha=git(root,'rev-parse','refs/heads/'+config['branch'])
    manifest=json.loads(git(root,'show',sha+':continuidade/CHECKPOINT.json'))
    paths=[x['path'] for x in manifest['files']]+['continuidade/CHECKPOINT.json']
    output=root/'tmp/continuidade/EBT_ENTERPRISE_CONTINUIDADE.zip'
    output.parent.mkdir(parents=True,exist_ok=True)
    temp=output.with_suffix('.zip.new')
    pins={e['path']:e.get('binary_sha256') for e in config['files']}
    with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            safe_path(path)
            result=subprocess.run(['git','-C',str(root),'show',sha+':'+path],capture_output=True,timeout=30)
            if result.returncode:raise CheckpointError('Arquivo ausente no commit: '+path)
            data=result.stdout
            if scan(path,data,pins.get(path)):raise CheckpointError('Possível segredo no commit: '+path)
            expected=next((x['sha256'] for x in manifest['files'] if x['path']==path),None)
            if expected and digest(data)!=expected:raise CheckpointError('Hash divergente: '+path)
            archive.writestr(path,data)
        archive.writestr('LEIA_PRIMEIRO.txt',
            'EBT Enterprise - pacote revisado de continuidade\nCommit: '+sha+
            '\nBranch: '+config['branch']+'\nAbra prompts/RETOMAR_EBT_ENTERPRISE.md.\n'
            'Pacote de código e planejamento; não é backup de dados nem prova de deploy.\n')
    os.replace(temp,output)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:raise CheckpointError('Falha de integridade do ZIP.')
    report={'commit':sha,'branch':config['branch'],'path':str(output),'sha256':digest(output.read_bytes()),
            'bytes':output.stat().st_size,'files':len(paths)+1,'includes_private_runtime':False,
            'proof':'bytes revisados do commit local; confirmar SHA remoto separadamente'}
    atomic_json(root/'tmp/continuidade/exportacao.json',report)
    return report


if __name__=='__main__':
    try:print(json.dumps(export(Path(__file__).resolve().parents[1]),ensure_ascii=True,indent=2))
    except (CheckpointError,OSError,ValueError,KeyError,subprocess.TimeoutExpired) as exc:
        print(str(exc) if isinstance(exc,CheckpointError) else 'Falha de exportação; dados privados omitidos.')
        sys.exit(1)
