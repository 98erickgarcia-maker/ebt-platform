"""Keep the umbrella identity and continuity references after existing generators."""


def finalize_enterprise_documents(generated, emit):
    readme = generated['README.md']
    first, tail = readme.split('\n', 1)
    overview = '''
## EBT Enterprise e seus produtos

EBT Enterprise é a família completa; EBT Platform é a fundação técnica e este repositório; Connect é o primeiro produto. Flow, Portal, Contracts, SST, sites e verticais permanecem na evolução planejada, com escopos/gates próprios.

- [Sistema completo e fronteiras](docs/arquitetura/EBT_ENTERPRISE_SISTEMA_COMPLETO.md).
- [Revisão de coerência desde o início](docs/qualidade/REVISAO_ENTERPRISE_E_CONTINUIDADE_20261007.md).
- [Salvar no GitHub e retomar no ChatGPT](docs/execucao/CONTINUIDADE_GITHUB_CHATGPT.md).
- [Prompt de retomada](prompts/RETOMAR_EBT_ENTERPRISE.md).

'''
    emit('README.md', '# EBT Enterprise | EBT Platform e primeiro produto Connect\n' + overview + tail)
    # Preserve the historical proposal while removing its contradictory blanket statement.
    readme = generated['README.md'].replace(
        'Nenhum serviço foi contratado ou conectado.',
        'Esse era o estado da proposta inicial. Os registros posteriores do Connect/WazVox estão acima; Meta direto e demais canais continuam dependentes de homologação própria.')
    emit('README.md', readme)
    continuation = generated['CONTINUAR_EM_OUTRO_CHAT.md']
    emit('CONTINUAR_EM_OUTRO_CHAT.md', continuation + '''
## Retomada da EBT Enterprise completa

Ler [visão integral](docs/arquitetura/EBT_ENTERPRISE_SISTEMA_COMPLETO.md), [estado de continuidade](planejamento/estado_continuidade.json), [contrato do agente](prompts/AGENTE_EBT_ENTERPRISE.md) e [prompt para o ChatGPT normal](prompts/RETOMAR_EBT_ENTERPRISE.md). Repositório: 98erickgarcia-maker/ebt-platform; branch em planejamento/continuidade_github.json. Conferir SHA remoto e continuidade/CHECKPOINT.json antes de continuar.

Depois de cada incremento revisado: `python scripts/checkpoint_github.py --approve --push`. Falha não é salvamento remoto. Exportar pacote revisado com `python scripts/exportar_continuidade.py`; não incluir tmp/private-integrations. A tarefa Windows só repete conteúdo já revisado, sem executar produto nem transferir sessões automaticamente. Seguir [procedimento](docs/execucao/CONTINUIDADE_GITHUB_CHATGPT.md).
''')
    path = 'docs/execucao/CHATGPT_NORMAL_E_PASSAGEM_CODEX.md'
    emit(path, generated[path] + '''
## Checkpoint implementado nesta revisão

A descrição anterior de ausência de runner pertence ao complemento original. A revisão de 07/10/2026 adiciona ferramenta de checkpoint e pacote de continuidade, sem transferência automática de chat. Seguir [contrato atual](CONTINUIDADE_GITHUB_CHATGPT.md), [estado](../../planejamento/estado_continuidade.json) e [prompt de retomada](../../prompts/RETOMAR_EBT_ENTERPRISE.md). A instalação/execução do agendador deve ser comprovada separadamente.
''')
    path = 'docs/INDICE_GERAL.md'
    emit(path, generated[path] + '''
## EBT Enterprise: visão completa e continuidade

- [Sistema completo](arquitetura/EBT_ENTERPRISE_SISTEMA_COMPLETO.md).
- [Revisão de coerência](qualidade/REVISAO_ENTERPRISE_E_CONTINUIDADE_20261007.md).
- [Continuidade GitHub/ChatGPT](execucao/CONTINUIDADE_GITHUB_CHATGPT.md).
- [Contrato do agente](../prompts/AGENTE_EBT_ENTERPRISE.md).
- [Prompt de retomada](../prompts/RETOMAR_EBT_ENTERPRISE.md).
- [Estado estruturado](../planejamento/estado_continuidade.json).
''')
