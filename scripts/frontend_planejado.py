"""Revisão focal e propostas de interface; não modifica fontes nem implementa módulos."""
import json

IMPROVEMENTS=[
('UX-01','Alta','Consolidar contrato visual e retirar sobreposições confirmadas','Uma fonte de tokens e componentes; CSS por escopo sem nova camada global de correção',['P02-01','P02-02','P05-07']),
('UX-02','Alta','Organizar navegação por fluxo e capacidade ativa','Acesso claro a início, contatos, tarefas, documentos e protocolo; perfil e empresa visíveis',['P04-01','P05-07']),
('UX-03','Alta','Eliminar affordances de função inexistente','Busca local real e ações executáveis; função futura não parece disponível',['P05-03','P05-07']),
('UX-04','Alta','Escolher layout com lista e detalhe contextual','Selecionar cadastro sem perder filtro/página; identidade única e ações vinculadas',['P05-02','P05-03','P05-07']),
('UX-05','Alta','Padronizar formulários, mensagens e estados','Rótulo, validação, loading/vazio/erro/negado/conflito, resultado persistido e retomada',['P05-02','P05-04','P06-03']),
('UX-06','Alta','Separar página, componentes e acesso a dados','Tela compõe componentes e hooks/adapters; contrato e regra permanecem rastreáveis',['P02-06','P05-07','P05-08']),
('UX-07','Alta','Conferir responsividade e acessibilidade','Teclado, foco, reflow, contraste, alvos e conteúdo sem perda nos tamanhos previstos',['P03-05','P05-07','P09-03']),
('UX-08','Média','Tornar lista e histórico consistentes','Tabela com alinhamento/rótulos; horário/autoria coerentes; filtros mantidos e estado de conflito',['P05-03','P05-04','P07-04']),
('UX-09','Média','Estabelecer checklist de interface por pacote','Revisão do conjunto e prova de navegador ligada ao commit/ambiente',['P05-10','P06-08','P07-06','P08-08','P09-01']),
('UX-10','Baixa','Expandir catálogo e refatorar todas as telas legadas','Avaliar após padrão escolhido e primeira tela integrada aprovada; reestimar escopo',['P09-08']),
]

STANDARD='''# Contrato visual candidato para EBT

Status: proposta para o primeiro recorte. Cores, composição e variante final ainda precisam de escolha visual; contratos, IDs, histórico, integração e autorização permanecem preservados. O desenho não aprova os módulos.

## Estrutura da aplicação

- Shell único: marca EBT configurável, empresa/ambiente identificados, perfil, navegação e área de conteúdo. Identidade não deve depender de texto do nome para mudar regra de negócio.
- Navegação do recorte: início, contatos/organizações, tarefas, documentos e protocolo quando ativos. Configurações no lugar previsível. Recurso futuro não aparece como ação pronta; permissões reais são verificadas no servidor.
- Cabeçalho de página: título curto, contexto e uma ação principal. Busca/filtros pertencem à lista atual até existir contrato de busca global.
- Área de trabalho: lista conserva busca, filtro e posição quando um registro é aberto. Detalhe sempre mostra a mesma identidade e vínculos; salvar invalida o dado afetado e demonstra o resultado após reload.
- Conteúdo do cadastro: resumo, histórico, próxima ação, documentos e tarefas vinculadas, conforme capacidade entregue. Não duplicar pessoa/organização para adequar layout.

## Fundamentos e componentes previstos

| Camada | Contrato candidato | Evitar |
|---|---|---|
| Tokens | Paleta semântica, tipografia, espaçamento 4/8/12/16/24/32px, raios e elevação coerentes | Cor, tamanho e sombra diferentes por tela sem motivo |
| Shell/navegação | AppShell e itens derivados de capacidade/perfil, com foco e ação real | Copiar o menu inteiro CASST para um produto menor |
| Título/ações | PageHeader, ação primária, secundária e perigosa identificadas | Várias ações principais disputando atenção |
| Lista | Toolbar, busca local, filtros, linhas, paginação e seleção preservada | Transformar todo dado em cartão decorativo |
| Formulário | Field, label, ajuda, erro, obrigatoriedade, validação e estado de gravação | Placeholder como único rótulo ou input que perde dado na falha |
| Estado | Loading, EmptyState, ErrorState, ForbiddenState e conflito específico | Página vazia sem explicar o próximo passo |
| Registro | RecordHeader, HistoryList, NextAction e vínculos reais | Criar histórico novo apenas para mudar a aparência |
| Overlay | Dialog/Drawer com foco, Escape, retorno ao controle e fundo inerte | Modal sem teclado ou bloqueio de ações necessárias |

Os nomes são candidatos de componentes, não declaração de que já existem. Adaptar/reutilizar primitivas compatíveis antes de criar outras. Colocar variante/tamanho no contrato; não anexar outra folha global para corrigir uma página isolada.

## Organização do código na implementação

Manter React/TypeScript quando essa for a base escolhida. Separar shell, tokens, primitivas e módulos; páginas compõem componentes, hooks/adapters cuidam de dados e contratos existentes continuam sendo a fonte das operações. Não escolher nova biblioteca visual só para trocar aparência. Se uma dependência for proposta, comparar licença, acessibilidade, custo de migração e compatibilidade antes de alterar o projeto.

Consolidar CSS gradualmente: rastrear import/selector/computed style, migrar um grupo por vez e retirar uma regra apenas após conferir consumidores. Contagem de !important ou arquivo minificado orienta investigação; não autoriza exclusão automática.

## Estados obrigatórios conforme o fluxo

Mostrar carregamento sem conteúdo enganoso; vazio inicial diferente de busca sem resultados; erro com recuperação; acesso negado sem expor dados; submissão sem clique duplicado; sucesso apenas após resposta confirmada; conflito sem perder entrada; arquivo restrito e validação de upload com motivo. Consulta não exibe ações de alteração e o servidor continua protegendo a operação.

## Responsividade e acessibilidade

Conferir 320, 390, 768 e 1366px, teclado e zoom/reflow. No celular, detalhe ocupa a coluna e preserva retorno à lista; tabela tem apenas rolagem própria quando bidimensionalmente necessária. Campos precisam de rótulo, erro associado, foco visível e anúncio pertinente de status.

Referência: [WCAG 2.2](https://www.w3.org/TR/WCAG22/). Texto comum pede contraste mínimo 4,5:1 e texto grande 3:1, conforme definições/exceções. O mínimo AA de alvo é 24×24 CSS px ou condições de espaçamento/exceções; usar 44px como escolha de conforto para toque quando couber. Foco deve permanecer visível e não totalmente oculto; reflow preserva conteúdo a 320 CSS px conforme o critério. Esta proposta não é certificação de conformidade.

## Navegação

[Revisão e prioridades](REVISAO_E_PRIORIDADES.md) | [Alternativas](ALTERNATIVAS_DE_LAYOUT.md) | [Revisão e aceite](REVISAO_ACEITE_FRONTEND.md)
'''

ALTERNATIVES='''# Alternativas de layout para o frontend EBT

Status: propostas, não interfaces publicadas. A comparação na conversa usa somente registros fictícios e interações locais. Nenhum layout foi aplicado às fontes.

## Workspace, recomendação inicial para o CRM

Navegação lateral enxuta; título/busca/filtros; lista central e detalhe contextual do registro selecionado. Histórico e próxima ação permanecem ligados ao cadastro. A opção reduz troca de páginas durante atendimento e permite comparar vários registros. No celular, lista e detalhe se alternam com retorno que preserva a seleção.

Boa escolha quando o trabalho é localizar um contato, entender histórico e agir sobre o mesmo ID. Exige evitar tabela com colunas excessivas, garantir contexto do selecionado e não usar drawer estreito para formulário complexo.

## Foco em tarefas, alternativa para rotina diária

Navegação superior compacta; próximas ações como entrada; seleção abre o mesmo cadastro e seus vínculos abaixo. Busca/lista completa continuam disponíveis. A opção organiza o dia por responsável/prazo e reduz a necessidade de conhecer todos os módulos para executar um retorno.

Boa escolha quando a prioridade é o que fazer agora. Exige acesso claro ao cadastro completo, reconciliação de prazo/estado com o backend e ausência de métricas decorativas. Uma pendência não significa conversa enviada ou tarefa realizada.

## Escolha e consistência

Recomendo Workspace como shell de cadastro/CRM e uma visão de próximas ações dentro do mesmo shell quando P07 estiver implementado. Os dois exemplos exploram entradas diferentes para a mesma identidade, não duas aplicações com contratos separados. Ainda não há aprovação visual do usuário.

Avaliar: identificar empresa/perfil; encontrar cadastro; abrir sem perder filtro; localizar histórico; definir próxima ação; entender sucesso/erro; voltar no celular e usar teclado. Priorizar a variante que completa a jornada com menos dúvida, sem esconder informação necessária. Não usar gosto de cor como único critério.

Um novo shell pode ser aplicado a um recorte novo sem substituir todos os frontends antigos. Sites institucionais e portal de cliente conservam necessidades próprias; compartilham marca/primitivas quando adequado, não obrigatoriamente o mesmo menu administrativo.

## Escopo das 200h

As propostas detalham o trabalho de interface já previsto no recorte. Implementar padrão mínimo em uma tela completa antes de expandir. O ticket P05-07 (3h) não promete reescrita de todas as telas ou catálogo completo. Se a transformação exceder o orçamento, medir e reestimar/cortar escopo; expansão geral vai ao backlog pós-ciclo. Nenhuma hora ou estado dos 77 tickets foi alterado.

## Navegação

[Contrato visual](PADRAO_VISUAL_E_COMPONENTES.md) | [Prioridades](REVISAO_E_PRIORIDADES.md) | [Pacotes](../execucao/PACOTES_CODEX.md)
'''

REVIEW='''# Revisão e aceite de frontend por pacote

## Entrada

Pacote/ticket, commit e versão do destino, layout candidato, perfil, tenant/carteira, registros sintéticos, rota/jornada, critérios de negócio e origem. Revisar texto de tarefa e decisão de layout antes de produzir componentes. Código de teste e interface são entregues juntos no recorte autorizado.

## Passagem própria de revisão

Conferir diff completo: primitivas reaproveitadas, fontes únicas de token, ausência de override global sem motivo, nomenclatura, ID/vínculos, contratos, cache e estados. Conferir ação existente, foco/teclado, semântica de formulário, responsividade e permissão real. Identificar autoria da revisão; a mesma IA revisando não equivale a revisão independente.

## Verificação automatizada prevista

Build/lint/tipos pertinentes; componentes com regras relevantes; jornada de navegador com salvar/reload, filtro/seleção mantidos e mesma identidade; perfis/tenant A/B e ID direto; estados erro/vazio/negado/conflito quando aplicáveis; teclado/Escape/retorno de foco; larguras previstas e captura vinculada à versão. Ferramenta de acessibilidade automática ajuda, mas não comprova toda WCAG ou compreensão do fluxo. Reutilizar os cenários existentes por versão/escopo; não criar testes redundantes por cada componente meramente visual.

## Inspeção visual e jornada

- Cabeçalho e ações têm hierarquia clara e nomes iguais para operações equivalentes.
- Busca informa seu escopo e produz resultado; ação futura não aparenta pronta.
- Menu mostra contexto e capacidades disponíveis sem esconder funções essenciais.
- Formulário conserva dados em falha e mostra motivo/recuperação.
- Lista/detalhe usam a mesma identidade; retorno preserva filtros e posição.
- Salvar demonstra persistência após reload, não apenas toast.
- Sem corte, sobreposição ou perda de ação em celular; teclado alcança ações e o foco retorna corretamente.
- Status usa texto além de cor, contraste e alvos conferidos conforme o contrato.
- Perfil de consulta não altera; operações por ID continuam autorizadas no backend.

Registrar resultado observado e a imagem realmente inspecionada, com rota, largura, estado, usuário sintético e versão. Screenshot capturado não é automaticamente screenshot revisado. Se já estiver no Codex, continuar normalmente com navegador disponível; sinalizar passagem apenas por ferramenta/acesso realmente ausente.

## Fechamento

O gate de interface é parte dos gates de produto existentes, sem estado adicional fictício. Falha de jornada/identidade/autorização bloqueia dependentes; problema cosmético tem impacto e decisão registrados. Aceite visual do usuário complementa testes técnicos. Salvar no GitHub não comprova publicação nem conformidade.

Usar [template](../../templates/REVISAO_FRONTEND.md) e [revisão local/online](../qualidade/REVISAO_AUTOMATIZADA_LOCAL_E_ONLINE.md). O [contrato visual](PADRAO_VISUAL_E_COMPONENTES.md) define a referência, e o [catálogo de melhorias](../../planejamento/melhorias_frontend.json) mantém sugestões separadas do backlog executado.
'''

TEMPLATE='''# Revisão de frontend

- Pacote/ticket, layout proposto/aprovado e motivo: a preencher.
- Versão, ambiente, rota, largura, perfil e massa sintética: a preencher.
- ID/vínculos/contratos e consumidores preservados: a preencher.
- Componentes/tokens e regras CSS alterados/retirados: a preencher.
- Achados com arquivo/linha, impacto, reprodução e correção: a preencher.
- Comandos/casos pertinentes, esperado/observado e evidência: a preencher.
- Captura realmente inspecionada e resultado visual: a preencher.
- Salvar/reload, filtro/seleção, erro/negado/conflito e teclado: a preencher.
- Aceite real do usuário quando existir, autoria/data e ressalvas: a preencher.
- Horas reais, pendências, commit remoto conferido e próximo passo: a preencher.

Template vazio não certifica interface ou autoriza remodelagem de todos os módulos.
'''

def emit_frontend(snapshot,emit):
    doc='# Revisão focal dos frontends e prioridades\n\nData: 06/10/2026. Inspeção estática de arquivos específicos CASST, Vikings e Nutrição; não executou as aplicações nem observou suas telas online. Fontes não alteradas. Arquivos/versões/hashes estão no [snapshot](../../evidencias/revisao_frontend_fontes.json). A revisão não conclui que nenhum frontend foi bem desenvolvido.\n\n'
    doc+='## Constatações e hipóteses\n\n'
    doc+='| Base | Constatação no código lido | Implicação / sugestão | Limite da prova |\n|---|---|---|---|\n'
    doc+='| CASST | main.tsx importa tokens e quatro folhas de apresentação, com crm-design-system.css por último. Há 33 ocorrências de !important nas quatro folhas. | Consolidar regras e conferir consumidores/computed styles antes de remover overrides; uma quinta camada seria fonte de manutenção. | Contagem não prova conflito renderizado; não foram examinados todos os seletores. |\n'
    doc+='| CASST | AppShell possui controle de foco/teclado no drawer, navegação por perfil, 28 ocorrências NavLink (incluindo ramificações) e teste próprio. | Preservar essas bases; reduzir menu ao recorte EBT, sem copiar todas as verticais. | Ocorrência não equivale a 28 itens simultaneamente visíveis; testes não foram executados aqui. |\n'
    doc+='| CASST | AppShell.tsx:156 apresenta busca como div e atalho visual; título informa planejamento. Notificação desabilitada em :158. | Busca deve ser local e funcional até existir contrato global; recurso futuro deve ter apresentação inequívoca. | Constatação de markup, não relato de falha autenticada atual. |\n'
    doc+='| Vikings | App.tsx concentra estados/dados, helpers e fluxos em código muito condensado; CSS também condensado. | Separar apresentação, dados e jornadas antes de ampliar; formatação ajuda revisar mas não substitui melhoria de contrato. | Densidade do arquivo não prova defeito ou baixa qualidade; snapshot atual difere da revisão histórica. |\n'
    doc+='| Nutrição | AppLayout separa áreas cliente/equipe/CRM por rotas/perfil; tokens e workspace próprios. | Preservar contexto por público e reutilizar padrões, sem forçar menu administrativo no portal de cliente. | Inspeção focal; não certifica jornada atual ou backend. |\n\n'
    doc+='## Versões e arquivos inspecionados\n\n'
    for project in snapshot['projetos']:
        doc+=f"### {project['projeto']}\n\nHEAD local: `{project['head']}`. O snapshot identifica hashes dos arquivos da árvore local; HEAD sozinho não representa alterações não commitadas.\n\n"
        doc+='| Arquivo relativo à fonte | Linhas | Observação quantitativa |\n|---|---:|---|\n'
        for f in project['arquivos']:
            extra=f"{f['ocorrencias_important']} !important" if 'ocorrencias_important' in f else 'Conteúdo focal inspecionado'
            doc+=f"| `{f['path']}` | {f['linhas']} | {extra} |\n"
        doc+='\n'
    doc+='## Sugestões e vínculo com o plano\n\n| ID | Prioridade | Sugestão | Tickets para avaliar |\n|---|---|---|---|\n'
    improvements=[]
    for ident,priority,title,outcome,tickets in IMPROVEMENTS:
        doc+=f"| {ident} | {priority} | {title} | {', '.join(tickets)} |\n"
        improvements.append(dict(id=ident,prioridade=priority,sugestao=title,resultado_proposto=outcome,tickets_relacionados=tickets,
            estado='proposto',evidencia_implementacao=None,impacto_orcamento='Avaliar recorte mínimo nos tickets existentes; expansão geral exige reestimativa/decisão, sem alterar 180h+20h'))
    doc+='\nPrioridade é recomendação de produto, não defeito comprovado nem tarefa nova concluída. A meta é padronizar um fluxo inteiro, medir e só então ampliar. O orçamento e os 77 estados continuam preservados. Não absorver uma reescrita completa no ticket de marca/vocabulário.\n\n'
    doc+='[Contrato visual e componentes](PADRAO_VISUAL_E_COMPONENTES.md) | [Alternativas de layout](ALTERNATIVAS_DE_LAYOUT.md) | [Revisão e aceite](REVISAO_ACEITE_FRONTEND.md)\n'
    emit('docs/frontend/REVISAO_E_PRIORIDADES.md',doc)
    emit('docs/frontend/PADRAO_VISUAL_E_COMPONENTES.md',STANDARD)
    emit('docs/frontend/ALTERNATIVAS_DE_LAYOUT.md',ALTERNATIVES)
    emit('docs/frontend/REVISAO_ACEITE_FRONTEND.md',REVIEW)
    emit('templates/REVISAO_FRONTEND.md',TEMPLATE)
    emit('planejamento/melhorias_frontend.json',json.dumps(dict(versao='1.2',escopo='sugestões de frontend; não execução',fonte='evidencias/revisao_frontend_fontes.json',itens=improvements),ensure_ascii=False,indent=2))
