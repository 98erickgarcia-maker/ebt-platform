"""Agrupa os tickets existentes; não cria horas, módulos nem evidências de produto."""
import json

# Fase, intervalo inclusivo, nome, saída integrada e foco específico da revisão.
PACK_ROWS = [
('P01',1,6,'Baseline e contrato do primeiro recorte','Fonte congelada, fluxo escolhido e mapa dos contratos reutilizáveis','Confrontar versão/hash e cenário; localizar a falha de onboarding e os limites do reuso'),
('P02',1,4,'Estrutura, configuração e dados sintéticos','Estrutura executável e configuração própria para dois consumidores','Conferir reprodução dos comandos, separação de configuração e ausência de dados reais'),
('P02',5,8,'Banco, storage, diagnóstico e CI','Persistência de QA e fundação demonstradas no ambiente identificado','Exercitar erro HTTP, salvar/recarregar, diagnóstico sanitizado e os critérios de G1'),
('P03',1,6,'Site essencial completo','Pacote de site com navegação, identidade, contato, manual e retorno','Percorrer páginas em celular/computador; conferir canal efetivo e diferenças da fonte aprovada'),
('P04',1,4,'Identidade e escopo de tenant','Identidade alimenta o contexto e restringe consultas/gravações','Tentar manipular tenant recebido do cliente e cruzar leitura/gravação entre A e B'),
('P04',5,8,'SQL, autorização por recurso e cache','Banco e autorização mantêm o isolamento inclusive em acesso por ID','Conferir migration/índices no SQL real, ID direto, cache e troca de perfil'),
('P04',9,12,'Auditoria, proteção da sessão e onboarding','Onboarding e trilha de auditoria fecham o gate de segurança','Reproduzir onboarding, verificar negativas, proteção de sessão e ausência de segredo nos eventos'),
('P05',1,3,'Cadastro único, busca e paginação','Pessoa/organização cadastradas uma vez e recuperadas na consulta','Conferir duplicidade, ID estável, vínculos, recarregamento e paginação com dados sintéticos'),
('P05',4,6,'Histórico, próxima ação e funil','Interação, responsável, próxima ação e mudança de etapa persistem juntos','Percorrer jornada comercial e conferir autoria, ordenação, negativa de perfil e tenant'),
('P05',7,10,'Segundo consumidor, importação e fechamento do CRM','CRM demonstrável em dois consumidores, com importação delimitada e manual','Conferir marca sem fork de regra, repetição da importação e resultado persistido de G-CRM'),
('P06',1,4,'Documento privado e acesso autorizado','Documento vinculado pode ser enviado e baixado apenas por ator autorizado','Exercitar upload inválido, acesso por ID, negativa de B e falha entre metadado e arquivo'),
('P06',5,8,'Versões, concorrência e recuperação documental','Revisão/versionamento e restore preservam documento e histórico','Conferir repetição, concorrência, hash dos bytes restaurados e segundo consumidor de G-GED'),
('P07',1,6,'Tarefas vinculadas e prazos','Tarefa passa por criação, conclusão/cancelamento e atualização das pendências','Reconciliar contador, prazo/atraso, histórico e alterações permitidas/proibidas de G-TASK'),
('P08',1,4,'Protocolo, numeração e consulta','Protocolo vincula interessado/documento e apresenta histórico coerente','Criar concorrente e repetir solicitação no SQL real; conferir unicidade e vínculos'),
('P08',5,8,'Tramitação e encerramento do Flow','Uma transição autorizada e encerramento deixam resultado auditável','Negar transição inválida, conferir atomicidade estado/histórico e recuperação de G-FLOW'),
('P09',1,4,'Reconciliação e jornadas integradas','Versão candidata reúne site, CRM e Flow/documentos do recorte','Confrontar manifesto com evidências e percorrer jornadas em A/B sem esconder pendências'),
('P09',5,8,'Migration, restore, operação e candidato','Candidato tem ensaio de atualização/retorno, recuperação e roteiro de piloto','Conferir retorno ensaiado, banco/arquivos restaurados, limites e autoria real do aceite'),
]

WORKFLOW = '''# Execução pelo Codex com pacotes maiores

## Decisão e limites

Decisão do usuário em 06/10/2026: pacotes maiores e revisão mais profunda, mantendo 200h. Os 17 pacotes agrupam as mesmas 72 tarefas de 180h; as cinco reservas mantêm 20h. Implementação, revisão, verificação e registro já integram os tickets. A nova organização não promete funcionalidades extras nem qualidade sem falhas.

Os números são estimativas de esforço de engenharia, não horas garantidas de execução do Codex, consumo de tokens ou prazo de uma sessão. Medir esforço real e capacidade demonstrada durante a execução; revisar a previsão sem preencher progresso fictício.

## Unidade de trabalho

Escolher um pacote de 8–12h estimadas por vez. Ler a ficha do pacote e os tickets internos; executar as tarefas na ordem das dependências. O pacote pode atravessar várias sessões/chats. Manter checkpoints pequenos de código para localizar regressões e retomar trabalho, sem pedir confirmação por rotina a cada checkpoint autorizado.

Agrupamento é uma unidade de acompanhamento, não dispensa gates. Um pacote que termina antes do gate da fase prepara uma capacidade parcial; não certifica a fase inteira. Nenhum pacote autoriza implantação em produção, contratação ou envio a terceiros.

## Ciclo de qualidade por pacote

1. Inspecionar checkout, AGENTS.md aplicáveis, alterações preexistentes, fontes e evidências. Confirmar entrada, critérios e contratos; registrar decisão real quando houver mudança.
2. Implementar os tickets em recortes verificáveis. Usar dados sintéticos; manter contratos e separação de tenant. Escolher comandos reais da fonte antes de executá-los, sem inventar sucesso de comando indisponível.
3. Conferir cada caminho afetado durante a implementação. Reuso equivalente recebe smoke focal; nova fronteira exige negativos e persistência/integridade proporcionais. Não adiar falha conhecida de segurança para a rodada online.
4. Ao fechar o pacote, revisar o diff completo em uma passagem própria: regra de negócio, autorização, contrato, schema/migration, storage, efeitos em consumidores, erros, UX e recuperação aplicáveis. Registrar achado com arquivo/linha, impacto e reprodução; identificar claramente se foi revisão do mesmo agente. Não chamar essa passagem de revisão independente.
5. Corrigir os achados e executar a regressão pertinente. Repetir revisão/verificação somente diante de nova mudança, falha ou dúvida ainda não resolvida. Não adicionar abstrações, funcionalidades ou suítes redundantes para aparentar excelência.
6. Demonstrar a saída integrada do pacote, além do aceite dos tickets. Registrar versão/hash, ambiente, comandos/resultado, casos pertinentes, limitações, esforço real e próximo pacote.
7. Salvar no GitHub o diff do pacote revisado e verificar o commit remoto. CI documental deste repositório verifica planejamento; CI de aplicação precisa existir e rodar na implementação. GitHub salvo não comprova deploy.

## Desenvolvimento primeiro e homologação online

Preferência: construir o recorte parte por parte, integrar e verificar localmente, depois realizar a rodada online de homologação. O QA inicial pode ser local isolado com banco SQL real e storage privado adequado ao cenário. Mock isolado não prova SQL, provedor de identidade, storage real ou canal externo.

Preparar configuração e comandos de implantação na fundação. Registrar desde então o que depende do ambiente online; cada evidência deve nomear onde foi obtida. Quando um critério exigir provedor/ambiente ainda indisponível, manter critério/gate pendente e avançar somente no trabalho independente ou que não pressuponha a fronteira aprovada.

A homologação online entra no fechamento integrado/operação do recorte e no esforço de verificação previsto, não somente na reserva. Se as condições do provedor ou o tempo necessário excederem a capacidade, registrar causa e reestimar/cortar escopo conforme o plano. Código pronto localmente, QA online, aceite do usuário e produção são estados distintos.

## Condições de conclusão e impedimento

Concluir tecnicamente um pacote exige tickets aplicáveis demonstrados no ambiente registrado, resultado integrado observado, comandos pertinentes aprovados, achados bloqueantes resolvidos e prova por versão. Contrato/tenant/persistência ainda não demonstrados impedem consumidores dependentes. Problema cosmético sem efeito no aceite pode ser registrado com impacto e decisão explícita de adiamento.

Dependência externa, credencial ou decisão faltante gera impedimento com próximo passo, não prova simulada. Se o pacote exceder sua estimativa, registrar realizado/restante e usar a política de reserva/corte; não reduzir testes essenciais para fechar a soma. As 200h são limite de planejamento, não garantia de excelência universal.

## Continuidade e orientação reutilizável

Usar [registro de pacote](../../templates/PACOTE_CODEX.md), [77 fichas](../INDICE_GERAL.md) e [pacotes](PACOTES_CODEX.md). No fim de cada sessão, deixar pacote/ticket ativo, último commit verificado, cenário que passou/falhou, decisões, arquivos alterados, dependência, esforço/saldo e próximo comando pertinente. Confirmar estado real ao retomar.

Exemplo de solicitação para uma implementação futura, que precisa ser enviada pelo usuário:

```text
Execute o PAC-01 do planejamento EBT. Leia AGENTS.md, a ficha do pacote e seus tickets.
Preserve fontes e alterações preexistentes. Implemente o recorte autorizado,
confira critérios e faça uma passagem de revisão do diff antes de fechar.
Corrija falhas e registre apenas provas observadas, com versão e ambiente.
Mantenha as 180h de entregas e 20h de reserva, sem ampliar funcionalidades.
Ao concluir, salve no GitHub e informe resultado, limites e próximo pacote.
```

Este exemplo é conteúdo documental; sua presença não inicia implementação. Não pressupõe subagentes, revisão independente, agendamento, modelo específico ou continuidade ilimitada.

## Base metodológica

A sequência de critérios explícitos, revisão, correção, validação e registro foi adaptada ao nosso orçamento. A documentação oficial exemplifica [ciclos de revisão e reparo com contrato claro](https://developers.openai.com/cookbook/examples/codex/build_iterative_repair_loops_with_codex) e [marcos verificáveis com estado persistido em arquivos](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex). São referências de método; não certificam os nossos módulos nem estimam seu prazo.
'''

TEMPLATE = '''# Registro de pacote Codex

- Pacote, tickets e saída integrada: a preencher.
- Sessão/checkout, alterações preexistentes e fontes/versões: a preencher.
- Entradas/dependências/decisões confirmadas: a preencher.
- Commits/checkpoints e contratos/dados afetados: a preencher.
- Implementação e aceite por ticket: a preencher.
- Revisão do diff: autor/agente, versão, achado/local/impacto e correção: a preencher.
- Comandos/casos, ambiente, expectativa, resultado e prova sanitizada: a preencher.
- Demonstração integrada e gates aprovados/pendentes no escopo: a preencher.
- Dependências externas, limites e impedimentos: a preencher.
- Esforço real, sessões únicas, realizado/restante e saldo de reserva: a preencher.
- GitHub: commit remoto conferido e resultado de CI pertinente: a preencher.
- Próximo pacote/ticket e primeiro passo para retomar: a preencher.

Template vazio não comprova execução. Mesma passagem do agente não equivale a revisão independente; comando planejado não equivale a comando aprovado.
'''

AUTOMATION = '''# Revisão automatizada local e online

## Decisão de execução

Visualizar online significa principalmente executar código de verificação contra o endereço de homologação. A conferência manual complementa a automação na avaliação visual e no aceite de negócio. Esta especificação é futura: este repositório ainda não contém suíte de aplicação/browser implementada.

Os testes ficam em projeto/pasta de QA apropriada à stack escolhida, separados do código funcional. Os mesmos cenários aplicáveis podem rodar localmente e em homologação com configuração de destino, usuários sintéticos e adaptadores próprios do ambiente. Escolher ferramenta/comandos durante a fundação, conforme os projetos-fonte, sem presumir framework instalado.

## Camadas e prova esperada

| Camada | Conferência automatizada | Prova e limite |
|---|---|---|
| Código e contrato | Build, lint/tipos pertinentes, domínio e consumidores afetados | Comando/saída/commit; não comprova ambiente online |
| API e persistência | Regras, entradas inválidas, salvar/recarregar, concorrência e idempotência no banco real | Asserções e IDs sintéticos; mock não comprova SQL |
| Navegador | Abrir URL, autenticar usuário de teste, navegar, preencher, salvar e reabrir registro | Resultado por cenário, trace/capturas sanitizadas; abrir página sozinho não comprova fluxo |
| Segurança | Tenant A/B, ID direto, negativa de ação, sessão/troca de perfil e documento privado | Resultado esperado/observado de permissão; resposta 200 isolada não basta |
| Ambiente online | Identificar versão implantada, health/configuração, sessão, banco e storage do destino | URL, ambiente, versão e dados persistidos; pacote gerado não comprova deploy |
| Visual e negócio | Capturas em larguras previstas e comparação pertinente; percurso do usuário | Automação ajuda a localizar diferenças, mas não substitui leitura visual ou aceite real do piloto |

Os cenários são os [234 casos já planejados](MATRIZ_CENARIOS.md); esta organização não cria uma nova bateria obrigatória por cima de todos eles. Selecionar os casos afetados conforme R1/R2/N, registrar casos não aplicáveis com motivo e fechar a jornada integrada no pacote pertinente.

## Cobertura online do recorte

1. Site: páginas/links, navegação em celular/computador e canal/formulário no ambiente de QA. Quando houver serviço externo, usar destino de teste/sandbox; recebimento real só é comprovado com a evidência correspondente.
2. Segurança: onboarding, sessão, tenant A/B, consultas/gravações e acesso por ID, incluindo negativas e troca de perfil/cache.
3. CRM: cadastrar, impedir duplicidade pertinente, registrar interação/etapa/próxima ação e recuperar a mesma identidade após reload e nova sessão.
4. Documentos: upload válido/inválido, versão/revisão, download autorizado e negado, repetição/falha e conferência de bytes quando aplicável.
5. Tarefas/Flow: responsável/prazo/resultado, transição autorizada/negada, histórico coerente, concorrência e idempotência do protocolo no SQL real.
6. Operação: atualização/retorno e restore em recursos isolados destinados ao ensaio, com comparação de banco/arquivo e registro de versão. Não executar teste destrutivo em banco de produção.

## Configuração e execução

Definir endereço-base, ambiente, versão esperada, identificação da massa e usuários de QA. Segredos entram por configuração segura, nunca pelo commit/relatório. Antes de criar dados, confirmar que o destino é o QA autorizado. Cada execução usa identificador próprio para evitar colisão; limpeza só alcança registros sintéticos explicitamente criados para aquele teste.

O runner deve encerrar com falha quando a expectativa não for satisfeita e salvar relatório por caso, ambiente e versão. Separar falha do produto de indisponibilidade do ambiente e teste não executado. Retentativa limitada e justificada não pode esconder resultado intermitente; guardar falha inicial e resultado da correção.

Preferência acordada: rodar verificações locais durante a construção dos 17 pacotes; realizar a rodada online do recorte na homologação final. As condições externas ainda não conferidas ficam pendentes. Uma evidência exigida por gate não pode ser substituída por simulação; consumidores dependentes aguardam ou recebem recorte independente explícito.

CI de aplicação deve chamar os comandos pertinentes e produzir artefatos sanitizados. Execução contra homologação ocorre quando o ambiente/versão de destino estiver disponível e autorizado. A CI atual deste repositório permanece documental; não declarar estes testes rodados só porque ela passou.

## Conferência visual e aceite

O Codex pode examinar capturas ou percorrer o navegador quando essas ferramentas estiverem disponíveis e o acesso for permitido. Registrar o que foi efetivamente visto, larguras/rotas e limitações; não tratar screenshot gerado como screenshot inspecionado. A opinião do usuário sobre o fluxo, legibilidade e adequação ao negócio é registrada no aceite real do piloto.

Automação local/online, inspeção visual, homologação pelo usuário e liberação em produção permanecem evidências distintas. Revisão e verificação estão dentro das 180h; a reserva de 20h cobre contingência comprovada.

## Navegação

[Execução pelo Codex](../execucao/EXECUCAO_PELO_CODEX.md) | [Pacotes](../execucao/PACOTES_CODEX.md) | [Estratégia de evidências](ESTRATEGIA_DE_EVIDENCIAS.md) | [Validação e gates](../VALIDACAO_E_GATES.md)
'''

def build_packages(data):
    items={t['id']:t for t in data['itens']}
    packs=[]
    for number,(phase,start,end,name,output,review) in enumerate(PACK_ROWS,1):
        ids=[f'{phase}-{i:02}' for i in range(start,end+1)]
        tasks=[items[i] for i in ids]
        packs.append(dict(id=f'PAC-{number:02}',fase=phase,nome=name,tickets=ids,
            horas=sum(t['horas'] for t in tasks),
            implementacao_h=sum(t['implementacao_h'] for t in tasks),
            verificacao_h=sum(t['verificacao_h'] for t in tasks),
            registro_h=sum(t['registro_h'] for t in tasks),
            inicio_h=tasks[0]['inicio_h'],fim_h=tasks[-1]['fim_h'],
            saida_integrada=output,revisao_especifica=review,
            estado='planejado',evidencia=None,
            documento=f'docs/execucao/pacotes/PAC-{number:02}.md'))
    owners={ticket:p['id'] for p in packs for ticket in p['tickets']}
    gate_owners={f'{phase["id"]}-GATE':owners[phase['tickets'][-1]] for phase in data['fases'] if phase['id']!='P10'}
    for p in packs:
        deps={dep for tid in p['tickets'] for dep in items[tid]['dependencias'] if dep not in p['tickets']}
        p['dependencias_tickets_gates']=sorted(deps)
        p['dependencias_pacotes']=sorted({owners.get(d,gate_owners.get(d)) for d in deps}-{None,p['id']})
        phase=next(f for f in data['fases'] if f['id']==p['fase'])
        p['gate_fase']=phase['gate']
        p['fecha_gate_fase']=phase['tickets'][-1] in p['tickets']
    flat=[t for p in packs for t in p['tickets']]
    assert len(flat)==len(set(flat))==72 and set(flat)=={t['id'] for t in items.values() if t['trilha']!='RES'}
    assert sum(p['horas'] for p in packs)==180 and all(8<=p['horas']<=12 for p in packs)
    return dict(versao='1.2',decisao='Pacotes maiores e revisão mais profunda, mantendo 200h',
        fonte_orcamento='planejamento/backlog_200_horas.json',total_h=200,entregas_h=180,reserva_h=20,
        horas_incluem_revisao_verificacao_registro=True,
        reservas=[t['id'] for t in items.values() if t['trilha']=='RES'],pacotes=packs)

def emit_packages(data,emit,link):
    registry=build_packages(data)
    emit('planejamento/pacotes_codex.json',json.dumps(registry,ensure_ascii=False,indent=2))
    items={t['id']:t for t in data['itens']}
    overview='# Pacotes maiores para executar pelo Codex\n\n17 pacotes de 8–12h estimadas agrupam as mesmas 72 entregas (180h). As cinco reservas mantêm 20h. Os 77 tickets, critérios e dependências originais permanecem. Agrupamento e documentação não comprovam execução.\n\n'
    overview+='| Pacote | Resultado | Tickets | Horas | Gate ao fechar fase |\n|---|---|---|---:|---|\n'
    for p in registry['pacotes']:
        path=p['documento']
        overview+=f"| {link('docs/execucao/PACOTES_CODEX.md',path,p['id'])} | {p['nome']} | {p['tickets'][0]} a {p['tickets'][-1]} | {p['horas']}h | {p['gate_fase'] if p['fecha_gate_fase'] else 'Parcial; gate pendente'} |\n"
        card=f"# {p['id']} | {p['nome']}\n\nEstado: planejado. {p['horas']}h estimadas ({p['implementacao_h']:g}h implementação, {p['verificacao_h']:g}h verificação/revisão e {p['registro_h']:g}h registro). Capacidade já contida nos tickets, sem acréscimo. Janela de esforço: {p['inicio_h']}-{p['fim_h']}h.\n\n"
        card+='## Resultado integrado\n\n'+p['saida_integrada']+'.\n\n'
        card+='## Dependências\n\n'
        card+=(', '.join(link(path,f'docs/execucao/pacotes/{d}.md',d) for d in p['dependencias_pacotes']) or 'Sem pacote anterior obrigatório.')+'\n\n'
        card+='Tickets/gates externos: '+(', '.join(p['dependencias_tickets_gates']) or 'nenhum')+'. As dependências originais são mantidas; ordenar por pacote não substitui sua prova.\n\n'
        card+='## Tarefas internas e aceite original\n\n| Ticket | Resultado/atividade | Horas | Trilha |\n|---|---|---:|---|\n'
        for tid in p['tickets']:
            t=items[tid]
            card+=f"| {link(path,f'docs/execucao/entregas/{tid}.md',tid)} | {t['titulo']} | {t['horas']}h | {t['trilha']} |\n"
        card+='\nLer e cumprir os critérios/cenários de cada ficha. A saída integrada complementa os aceites individuais.\n\n'
        card+='## Revisão específica do conjunto\n\n'+p['revisao_especifica']+'.\n\n'
        card+='1. Revisar o diff do conjunto após implementar os recortes; apontar achados com local/impacto/prova.\n2. Corrigir falhas e executar comandos/casos pertinentes ao risco. Reavaliar trilha se a fronteira mudou.\n3. Demonstrar a saída integrada em ambiente identificado; registrar versão, persistência/negativas quando aplicáveis e limites.\n4. Reconciliar critérios dos tickets, horas reais e próximo passo; conferir o commit remoto ao salvar.\n\n'
        card+='## Gate e ambiente\n\n'
        card+=(f"Este pacote contém o fechamento de {p['gate_fase']}; exige todas as provas aplicáveis da fase." if p['fecha_gate_fase'] else f"Este pacote é parcial. {p['gate_fase']} continua pendente até o pacote final da fase e suas provas.")+' Não equivale a produção.\n\n'
        card+='Preferência de execução: desenvolver e conferir localmente primeiro; homologação online do recorte posteriormente. Mock não prova provedor real. Se a evidência de uma fronteira estiver indisponível, manter critério/gate pendente e impedir o consumidor que dela depende; continuar apenas trabalho independente.\n\n'
        card+='## Fechamento e continuidade\n\n'+link(path,'templates/PACOTE_CODEX.md','Registro do pacote')+' | '+link(path,'docs/execucao/EXECUCAO_PELO_CODEX.md','Ciclo de execução/revisão')+' | '+link(path,'docs/execucao/PACOTES_CODEX.md','Todos os pacotes')+'\n\n'
        card+='Não criar registros de resultado antes da execução. As horas não são previsão de duração da sessão do Codex.\n'
        emit(path,card)
    overview+='\n## Qualidade e orçamento\n\nRevisão própria do diff e demonstração integrada fazem parte da verificação já estimada. Não acrescentar 17 revisões como horas extras nem usar a reserva para ocultar esse esforço. Registrar custo real; se faltar capacidade, seguir reserva/corte previsto. As horas não garantem prazo do Codex nem qualidade absoluta.\n\n'
    overview+=link('docs/execucao/PACOTES_CODEX.md','docs/execucao/EXECUCAO_PELO_CODEX.md','Método de execução e revisão')+' | '+link('docs/execucao/PACOTES_CODEX.md','planejamento/pacotes_codex.json','Catálogo estruturado')+' | '+link('docs/execucao/PACOTES_CODEX.md','docs/VALIDACAO_E_GATES.md','Validação e gates')+'\n'
    emit('docs/execucao/PACOTES_CODEX.md',overview)
    return registry
