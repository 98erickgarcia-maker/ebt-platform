"""Document/process checks only; never certify product operation or a remote push."""
import json
from pathlib import Path
import re
from checkpoint_github import digest, load_snapshot

ROOT=Path(__file__).resolve().parents[1]


def main():
    state=json.loads((ROOT/'planejamento/estado_continuidade.json').read_text(encoding='utf-8'))
    config=json.loads((ROOT/'planejamento/continuidade_github.json').read_text(encoding='utf-8'))
    errors=[]
    def check(ok,message):
        if not ok:errors.append(message)
    check(state['budget']['delivery_hours']==180 and state['budget']['reserve_hours']==20,'Orçamento mudou.')
    check(state['budget']['actual_hours'] is None,'Horas reais não podem ser inventadas.')
    check(state['automatic_chat_transfer'] is False,'Transferência automática não comprovada.')
    check(state['automatic_new_content_approval'] is False,'Agendador não pode aprovar conteúdo novo.')
    check(state['no_product_gate_promotion'] is True,'Checkpoint não promove gates.')
    check(config['branch'].startswith('codex/'),'Branch de checkpoint inválida.')
    snapshot=load_snapshot(ROOT,config)
    for entry in config['files']:
        check(digest(snapshot[entry['path']])==entry['reviewed_sha256'],'Conteúdo sem revisão: '+entry['path'])
    process=(ROOT/'scripts/Run-Checkpoint.ps1').read_text(encoding='utf-8')
    command=next(x for x in process.splitlines() if x.startswith('& '))
    check('--approve' not in command and '--push' in command,'Runner do agendador viola revisão.')
    instruction=(ROOT/'AGENTS.md').read_text(encoding='utf-8')
    check('checkpoint_github.py --approve --push' in instruction,'Regra de salvar não persistida.')
    catalog=(ROOT/'docs/arquitetura/EBT_ENTERPRISE_SISTEMA_COMPLETO.md').read_text(encoding='utf-8')
    for name in ('Core','Connect','Flow','Portal','Contracts','SST','Legislativo','Educação','Saúde'):
        check(name in catalog,'Produto original não preservado: '+name)
    paths=['docs/arquitetura/EBT_ENTERPRISE_SISTEMA_COMPLETO.md','docs/execucao/CONTINUIDADE_GITHUB_CHATGPT.md',
           'docs/qualidade/REVISAO_ENTERPRISE_E_CONTINUIDADE_20261007.md','prompts/AGENTE_EBT_ENTERPRISE.md','prompts/RETOMAR_EBT_ENTERPRISE.md']
    for path in paths:
        file=ROOT/path
        check(file.is_file(),'Documento ausente: '+path)
        if not file.is_file():continue
        for target in re.findall(r'\]\(([^)]+)\)',file.read_text(encoding='utf-8')):
            if '://' not in target and not target.startswith('#'):
                check((file.parent/target.split('#')[0]).exists(),'Link quebrado: '+path+' -> '+target)
    report={'passed':not errors,'errors':errors,'files_reviewed':len(snapshot),
            'delivery_hours':180,'reserve_hours':20,'product_gates_promoted':False,
            'scope':'contrato de continuidade, caminhos/hashes, orçamento e documentos; sem teste de produto ou envio remoto'}
    print(json.dumps(report,ensure_ascii=True,indent=2))
    if errors:raise SystemExit(1)


if __name__=='__main__':main()
