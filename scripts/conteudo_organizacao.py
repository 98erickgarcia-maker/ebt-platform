"""Documentos de gestão, arquitetura, produto e operação do planejamento EBT."""

DOCUMENTS = {
'docs/gestao/ESCOPO_E_RESULTADOS.md': '''# Escopo e resultados do ciclo

## Identificação

Projeto: EBT Platform. Base de planejamento: 06/10/2026. Capacidade: 200 horas-pessoa, sendo 180h de trabalho planejado e 20h de reserva. A organização documental deste pedido não representa consumo ou execução das 180h futuras. A fonte de horas, IDs, critérios e status é planejamento/backlog_200_horas.json.

## Objetivo

Priorizar Connect com cadastro/histórico/tarefas, resposta por API e webhook, documentos privados e candidato operacional. Site e Flow ficam no backlog posterior; CASST é fonte seletiva, sem copiar integralmente sua estrutura. Construir fronteiras reutilizáveis apenas onde um segundo consumidor demonstrar que a generalização é útil. As primeiras entregas são configuração e extração focal, seguidas de regras novas com testes proporcionais.

## Contrato de escopo interno

| Pacote | Incluído | Não incluído neste ciclo |
|---|---|---|
| Site, adiado | Até cinco páginas e manual no backlog posterior; zero horas neste ciclo | CMS completo, transparência e painel complexo |
| CRM | Pessoa/organização/contato, histórico, até cinco etapas fixas, responsável, próxima ação e importação QA de até 100 linhas | Financeiro, propostas completas, OS, estoque, inbox coletivo, WhatsApp oficial |
| Documentos/tarefas | Uma categoria comercial, arquivo privado, revisão, versão, download autorizado, tarefa e prazo | Prontuário, assinatura digital, canal externo automático e GED completo |
| Comunicação Connect | Texto recebido, resposta do atendente por API, webhook de status e recuperação | Campanha, chatbot, omnichannel e inbox coletivo avançado |
| Flow, adiado | Um protocolo/fluxo fixo no backlog posterior; zero horas neste ciclo | Designer, timers e workflow amplo |

O número de páginas/etapas/linhas é um limite do pacote. Nenhum limite arbitrário de arquivo, sessão, retenção ou usuários é inventado: esses parâmetros ficam registrados como decisão pendente e são fechados nos tickets correspondentes.

## Marcos

Segurança: 64h cumulativas. CRM: 92h. CRM/tarefas: 104h. Comunicação API/webhook: 140h. Documentos: 164h. Candidato interno: 180h. Site e Flow adiados fora do ciclo. Reserva: 20h consumíveis antes ou depois desses marcos, com registro de causa. A soma é de esforço; espera por credencial ou aceite altera calendário sem ser automaticamente hora técnica.

## Condição de entrega

Uma capacidade avança quando tem entrada satisfeita, saída concreta, cenário aprovado na versão correta e limite documentado. Empacotamento em QA pode estar pronto sem aceite operacional. Venda/implantação específica deve explicitar conteúdo, ambiente, custo de terceiros, dados autorizados e responsável. Este documento não determina preço, SLA contratual ou licença comercial.

## Mudança de escopo

Toda mudança tem motivo, tickets afetados, horas, dependências e impacto em testes. Alterar um rótulo não justifica renomear banco/API. Acrescentar integração ou vertical não pode ser disfarçado como reserva. Se faltar capacidade, recortar/adiar GED com impacto explícito no candidato, preservando segurança, recuperação e comunicação essencial. Site e Flow já estão adiados. Alteração da distribuição 180/20 requer instrução explícita do usuário.
''',

'docs/gestao/GOVERNANCA_E_RESPONSABILIDADES.md': '''# Governança e responsabilidades propostas

## Papéis

Os papéis abaixo ainda precisam de pessoas confirmadas. O registro não atribui obrigações a Thaiane, Erick, CASST, Vikings ou cliente por inferência.

| Papel | Responsabilidade | Evidência |
|---|---|---|
| Responsável pelo projeto EBT | Priorizar escopo, resolver decisões e acompanhar orçamento | Registro de decisão e mudança |
| Desenvolvimento EBT | Executar recorte, preservar fontes, registrar versão e resultado | PR/commit e ficha de entrega |
| Revisão técnica | Conferir contrato, segurança, migração e consequências em consumidores | Parecer proporcional ao recorte |
| Responsável de negócio | Confirmar fluxo/campos/resultado esperado | Critérios e motivo das decisões |
| Usuário piloto | Executar cenários e registrar aceite ou rejeição | Ficha de homologação com autoria/data |
| Operação | Preparar ambiente, recuperação e diagnóstico | Runbooks e ensaios |

Uma mesma pessoa pode acumular funções quando adequado, mas não se deve inventar revisão independente ou aceite de cliente. A equipe real e a disponibilidade devem ser registradas antes do piloto operacional.

## Entrada, saída e pausa de trabalho

Entrada: ticket identificado, dependências satisfeitas, fonte congelada, ambiente permitido e critério verificável. Saída: resultado, commit/hash, cenário, ambiente, evidência sanitizada, limitação e tempo real. Impedimento: natureza, dono proposto, próximo passo e recortes que ainda podem avançar.

Um impedimento de site não bloqueia automaticamente CRM. Falha de isolamento compartilhado impede todos os consumidores dessa fronteira. A reserva pode ser usada desde a primeira fase. Não registrar horas de espera como trabalho feito quando ninguém trabalhou.

## Estados

planejado -> em_execucao -> em_verificacao -> demonstrado_qa -> homologado_usuario -> liberado. bloqueado exige causa e dependência. Um caso falho retorna ao trabalho/verificação; um gate aprovado para uma versão não autoriza outra versão sem avaliar o diff.

demonstrado_qa exige registro verificável. homologado_usuario exige autoria, instante e cenário do usuário. liberado exige pacote/ambiente definido e, quando houver implantação, a prova específica da implantação. As duas últimas condições não foram satisfeitas pelo planejamento.

## Controle de esforço

Horas do ticket já incluem implementação, verificação e registro. Registrar horas reais separadamente das estimadas. Trabalho extra deve ter causa e ticket/reserva associados. Não somar as mesmas quatro horas ao ticket original e à reserva. O template de esforço registra um identificador único por sessão para permitir reconciliação.

## Rotina de fechamento

1. Conferir resultado e cenário do ticket.
2. Registrar tempo real e alteração de trilha, se houver.
3. Atualizar a fonte de status do backlog com a prova correspondente.
4. Executar verificadores documentais e revisar diff.
5. Fechar gate quando todas as dependências e casos aplicáveis passaram.
6. Salvar no GitHub o conteúdo revisado, sem presumir deploy ou envio.
''',

'docs/gestao/DECISOES_PENDENTES.md': '''# Decisões pendentes e gatilhos

Todas as linhas são pendências de execução, não impedimentos da entrega documental atual. O ticket indica onde a decisão cabe no orçamento. Valores ou pessoas ausentes permanecem a confirmar.

| ID | Decisão | Opções delimitadas / critério | Fechar em | Impacto se faltar |
|---|---|---|---|---|
| D01 | Fluxo e versão CASST de origem | Cadastro/histórico/próxima ação com árvore completa e cenário aprovado | P01-01 a P01-04 | Impede extração do recorte |
| D02 | Direitos de uso de código e ativos | Origem/licença/autoria e autorização comercial por componente | P01-05 | Componente pendente fica fora do pacote |
| D03 | Base do site | EBT estático ou CRP Razor conforme canal/admin necessário | P03-01 | Impede fechar pacote site, não a segurança do Core |
| D04 | Estratégia de autenticação | Preservar fonte adequada; confirmar cookie/token, provedor e claims | P04-02 | Impede G-SEG |
| D05 | Escopo de tenant e carteira | Vínculo autenticado; ação e recurso definidos no servidor | P04-01/P04-03 | Impede qualquer consumidor protegido |
| D06 | QA SQL/storage e chaves | Destinos exclusivos e reprodução de fixtures; sem reutilizar banco real | P02-05 | Impede provas de banco/arquivo |
| D07 | Política de documento | Categoria comercial, tamanho/tipo, revisão, scan e retenção parametrizados | P06-01/P06-03 | Arquivo sem prova de liberação permanece restrito |
| D08 | Onboarding da origem | Reproduzir falha observada e fechar jornada no recorte EBT | P04-11 | Impede G-SEG/G-CRM |
| D09 | Funil e regra de duplicidade | Até cinco etapas; normalização sem unir empresas/pessoas por telefone | P05-01/P05-02/P05-06 | Impede consistência do cadastro |
| D10 | Protocolo e concorrência | Um tipo, tenant/ano, índice e sequência transacional definidos | P08-01/P08-02 | Impede G-FLOW |
| D11 | Participantes e aceite do piloto | Pessoas reais e disponibilidade confirmadas; dados autorizados | P09-07 | Candidato QA pode existir; aceite real permanece pendente |
| D12 | Implantação futura | Domínio/host/config/contas/retorno do cliente escolhido | Depois de gate pertinente | Não prometer publicação específica |
| D13 | Próxima ação e tarefa | Fonte coerente, pendência principal e fechamento sem duas cópias editáveis | P05-05/P07-01 | Impede composição consistente do Connect |
| D14 | Exportação do CRM | Confirmar recurso existente, formato, colunas, limite e escopo do filtro | P01-04/P05-03 | Não ampliar exportação por inferência |
| D15 | Primeiro canal de comunicação | WhatsApp oficial candidato; conta própria de QA, versão, scopes, janela/template e custos | P11-01 | G-MSG permanece pendente sem acesso/prova |
| D16 | API/webhook e recuperação | Assinatura, dedupe, outbox, callbacks, envio desconhecido e ledger no restore | P11-02 a P11-12 | Impede resposta externa confiável |

## Como registrar resolução

Usar templates/DECISAO.md com decisão, motivo, fonte, pessoa responsável, data, tickets/contratos afetados e reversibilidade. Se mudar arquitetura, complementar ADR. Se mudar orçamento/escopo, registrar a instrução do usuário. A sugestão técnica e a confirmação do negócio ficam separadas.
''',

'docs/gestao/RISCOS_E_CONTINGENCIA.md': '''# Riscos concretos e uso da reserva

| Risco | Evidência ou origem | Sinal de ocorrência | Resposta | Reserva |
|---|---|---|---|---|
| R01, árvore incompleta | CASST/CRP têm mudanças locais | Snapshot difere do HEAD e omite arquivo produtor | Congelar árvore pertinente e comparar hashes | P10-03 se afetar extração |
| R02, ativação bloqueada | E2E CASST quarta rodada falhou no onboarding | Login não abre próxima tela do fluxo | Reproduzir causa; preservar critério; revalidar jornada | P10-01 |
| R03, fronteira de empresa nova | Generalização prevista | ID direto, cache ou gravação acessa A por B | Bloquear consumidores; corrigir e provar SQL/API | P10-02 |
| R04, referência temporal inadequada | CI/PR/provas são snapshots | Fonte/PR mudou desde inventário | Reconsultar versão e diffs relevantes antes da extração | Dentro do ticket; P10-03 se houver retrabalho |
| R05, binário/metadata/chave divergentes | Documento e restore são composição crítica | Hash divergente ou aplicação restaurada não lê arquivo | Não confirmar liberação; recuperar conjunto consistente | P10-04 |
| R06, configuração escondida | Bases dependem de ambiente | Clone não compila/inicia sem arquivo privado | Documentar opções e testar QA exclusivo | P10-04 |
| R07, abstração sem reuso | Core configurável ainda é plano | Segundo consumidor precisa copiar regra | Reduzir extração ao comum comprovado | P10-03 |
| R08, homologação indisponível | Usuário real não foi confirmado | Não há pessoa/ambiente para executar aceite | Fechar candidato QA com pendência explícita | P10-05 somente se houver trabalho real |
| R09, esforço acima da capacidade | Timeboxes são estimativas | Saldo projetado excede 200h | Reestimar; adiar P08 antes de cortar proteção | 20h totais, sem duplicar consumo |

A reserva não é cinco tarefas obrigatórias. Registrar defeito, ticket afetado, trabalho feito e consumo. Se o evento não ocorrer, as horas continuam livres. Serviços externos, novos módulos e custo de licença não são absorvidos sem mudança explícita de escopo.

## Critério de corte

Não remover casos de isolamento, autorização por ID, migração ou recuperação do recorte para cumprir prazo. Suspender o recorte afetado quando a prova falhar. Site/Flow estão adiados; uma mudança de fila por impedimento precisa de realocação explícita. Se a reserva se esgotar, fechar o que passou e transportar esforço restante a uma proposta revisada.
''',

'docs/arquitetura/ARQUITETURA_E_FRONTEIRAS.md': '''# Arquitetura candidata e fronteiras do recorte

Status: desenho para implementação futura. Fonte da direção: PDF fornecido e bases revisadas. A estrutura abaixo não afirma que pastas, serviços ou endpoints já existem na EBT Platform.

## Composição

Connect mantém a família .NET, React/TypeScript e SQL Server/Azure SQL da origem adequada, selecionada pela baseline. Comunicação usa inbox/outbox duráveis no SQL e worker no serviço; ver [desenho de API/webhook](CONNECT_API_E_WEBHOOK.md). Site/Flow estão adiados. O backend começa como monólito com fronteiras explícitas, sem exigir broker separado, cache distribuído ou microserviços.

```mermaid
flowchart LR
  Web[Interface Connect] --> Api[API autenticada]
  Api --> Access[Contexto de empresa e autorização]
  Access --> CRM[Contatos e histórico]
  Access --> GED[Documentos privados]
  Access --> Tasks[Tarefas]
  Access --> Msg[Conversa e mensagens]
  CRM --> SQL[(SQL QA)]
  GED --> SQL
  Tasks --> SQL
  Msg --> SQL
  Provider[Canal oficial] --> Hook[Webhook autenticado]
  Hook --> SQL
  SQL --> Worker[Worker inbox/outbox]
  Worker --> Provider
  GED --> Storage[(Storage privado QA)]
  Api --> Audit[Auditoria e correlação]
```

O diagrama é candidato. Recebimento do webhook, fila de resposta, aceite do provedor e entrega são estados separados. Storage e identidade são interfaces/contratos da composição; credenciais não entram no domínio.

## Responsabilidade por fronteira

| Fronteira | Pode fazer | Depende de | Não deve fazer |
|---|---|---|---|
| Apresentação | Coletar entrada, mostrar contexto/erro/resultado | Contrato API e configuração de marca | Autorizar pelo simples desaparecimento de botão |
| Identidade/contexto | Resolver usuário, empresa, perfil e escopo válidos | Identidade autenticada e vínculo ativo | Confiar no TenantId editável do cliente |
| Aplicação | Coordenar caso de uso e transação | Domínio e interfaces | Espalhar autenticação ou storage em cada tela |
| Domínio do recorte | Preservar estados, invariantes e IDs | Dados autorizados do caso de uso | Dependência de UI ou provedor externo |
| Persistência | Garantir índices, vínculo, concorrência e atomicidade | Schema versionado e contexto | Copiar bancos reais para fixtures |
| Arquivos | Armazenar/recuperar binário privado por contrato | Metadado e autorização por recurso | Tratar key/URL como permissão suficiente |
| Auditoria | Registrar ator, empresa, operação e resultado confirmado | Identidade e correlação confiáveis | Registrar token, senha ou anexo sensível no evento |

## Regra de extração

O recorte só vira componente compartilhado quando tem origem/hash, contrato neutro suficiente para dois consumidores, configuração de marca/contexto, autorização e teste pertinente nos dois. Uma cópia de cada produto não satisfaz o critério. Nem tudo do Vikings deve virar entidade dinâmica; vínculo trabalhista permanece domínio específico quando não é comum ao CRM.

## Organização futura de código

Criar apenas diretórios/soluções necessários à primeira implementação autorizada. Candidatos: src/Ebt.Api, src/Ebt.Web, modules para capacidades extraídas, tests por tipo, infrastructure para configuração/runbooks aplicáveis. Os nomes são sugestões; P02-02 fecha caminhos reais e comandos. Não criar uma árvore de dezenas de módulos vazios para aparentar implementação.
''',

'docs/arquitetura/DADOS_E_INVARIANTES.md': '''# Modelo conceitual de dados e invariantes

Status: contrato candidato, a confrontar com fonte em P01/P05. Nomes técnicos existentes devem ser preservados quando compatíveis. Nenhuma tabela/migration foi criada por este documento.

| Conceito | Campos essenciais candidatos | Vínculo e regra |
|---|---|---|
| Empresa/contexto | ID interno, nome/configuração, estado do vínculo | Contexto resolvedor por identidade; registro compartilhado entre clientes tem escopo explícito |
| Usuário e vínculo | Subject/ID confiável, empresa, perfil/permissões, ativo | Sessão inválida ou vínculo inativo não autoriza acesso |
| Pessoa/organização/contato | ID interno existente, nome, canais mínimos, empresa | Uma identidade dentro do contexto; não unir pessoas globalmente por telefone/CPF |
| Interação | ID, contato, autor, instante/direção/tipo/texto permitido | Nota interna distinta de conversa; histórico antigo não altera última conversa por conveniência |
| Próxima ação/tarefa | ID, origem, responsável, prazo, estado, resultado/motivo | Responsável no escopo; conclusão/cancelamento preservam trilha |
| Documento/versão | ID, entidade ligada, tenant, categoria, key, MIME/tamanho/hash, versão, estado | Binário privado; versão antiga preservada; versão nova exige decisão própria |
| Revisão documental | Documento/versão, ator, instante, decisão/motivo | Não aprovar bytes diferentes silenciosamente; repetir comando não duplica evento |
| Protocolo | ID, tenant/ano/tipo/número, interessado, responsável, estado, versão | Número único por escopo; ID interno não é substituído pelo número exibido |
| Movimento | Protocolo, estado anterior/novo, origem/destino, ator, instante, resultado | Estado e histórico coerentes na mesma operação confirmada |
| Auditoria | Ator, empresa, operação, vínculo, instante, correlação, resultado | Conteúdo minimizado; resultado não inventa sucesso antes do commit |
| Operação repetível | Empresa, ação, chave lógica, resultado/estado, prazo de validade decidido | Mesma operação não produz novos registros após resposta perdida |

## Regras transversais

1. Nome de exibição não muda ID, enum, tabela ou endpoint persistido.
2. Vínculos entre módulos preservam a empresa; consultar FK de outro tenant não contorna autorização.
3. Unicidade global da fonte é revisada somente onde a regra exige independência por empresa.
4. Cada escrita crítica define concorrência: token de versão existente, ETag ou equivalente compatível. P01 registra o mecanismo; nenhum nome é imposto sem conferência.
5. Datas de evento persistem com referência temporal inequívoca; UI exibe Brasília. Vencimento sem horário ou sem prazo tem regra fechada antes de testar.
6. Mudança relevante de estado preserva histórico e exige operação autorizada.
7. Cadastro, evento e metadados que precisam ser atômicos compartilham limite transacional definido. Storage fora da transação SQL requer estado pendente e reconciliação explícita.
8. Soft delete, retenção e eliminação não são aplicados universalmente por estilo. Fechar política da categoria no recorte.

## Identidade de pessoas

CRM usa identidade de cadastro; SST acrescenta emprego/alocação/exposição temporal. Matrícula externa, telefone ou nome não substituem o ID interno. Empregador não é tomador. Este ciclo não migra vínculos Vikings nem constrói cadastro pessoal global de todos os clientes EBT.

## Concorrência do protocolo

P08-02 deve registrar a estratégia SQL escolhida: incremento/linha de sequência protegido, transação e índice único do escopo, ou mecanismo equivalente comprovado. Não aceitar apenas calcular max+1 no código. O teste disputa duas requisições, repete uma chave de operação e verifica estado após falha/rollback.
''',

'docs/arquitetura/CONTRATOS_E_COMPATIBILIDADE.md': '''# Operações candidatas e compatibilidade

O catálogo é de operações esperadas, não de URLs já implementadas. P01-04 associa cada operação a endpoint, método, DTO, política e produtor/consumidor reais. Contrato existente compatível é reaproveitado; breaking change tem versão ou migração explícita.

| Operação | Entrada mínima candidata | Resultado confirmado | Casos que não confirmam sucesso |
|---|---|---|---|
| Criar contato | Nome/canal mínimo e chave de repetição quando pertinente | ID interno e estado persistido | Entrada inválida, empresa indevida, repetição conflitante |
| Listar/buscar | Filtros e paginação limitada | Itens somente do escopo | Token inválido, filtro não permitido |
| Registrar interação | Contato, tipo/direção, instante, texto permitido | Evento ligado ao mesmo ID | Cadastro ausente, perfil proibido, commit falho |
| Definir próxima ação | Contato/origem, responsável, prazo/descrição, versão | Estado e histórico persistidos | Responsável inativo, versão obsoleta |
| Mudar etapa | ID, etapa permitida, versão esperada | Etapa atual e trilha | Transição indevida, conflito |
| Preparar importação | Layout fixo, até 100 registros sintéticos | Preview/erros sem mutação definitiva | Linha inválida, arquivo fora do layout |
| Confirmar importação | Operação preparada e chave de repetição | Resultado persistido por linha/lote | Layout alterado, confirmação sem preview válido |
| Enviar documento | Entidade/categoria e arquivo permitido | Metadado/hash/versão pendente | Tipo/tamanho inválido, storage falho |
| Revisar documento | ID/versão, decisão/motivo, versão esperada | Decisão da versão exata | Arquivo substituído, ator proibido, concorrência |
| Baixar documento | ID do recurso, sessão autorizada | Bytes corretos ou acesso autorizado temporário | Outro tenant, categoria restrita, binário inexistente |
| Concluir tarefa | ID, resultado, versão | Estado e trilha de conclusão | Sem resultado, recurso alheio, conflito |
| Abrir protocolo | Tipo/ano, interessado, responsável, chave de operação | ID e número único | Vínculo de B, repetição incompatível, transação falha |
| Tramitar/concluir | Protocolo, ação autorizada, versão e resultado quando requerido | Estado + evento coerentes | Estado inválido, segunda atualização obsoleta |

## Padrão transversal

Erro estruturado tem código seguro e correlação sem dados desnecessários. A semântica de 401/403/404/409 e validação deve ser conferida no contrato existente: identidade ausente, ação proibida, recurso indisponível ao contexto, concorrência e entrada inválida não se confundem. Não mudar status/corpo HTTP apenas para simplificar teste.

Para comandos repetíveis, registrar escopo da chave, armazenamento do resultado, duração e comportamento para payload diferente. Para edição concorrente, registrar fonte do token e resposta de conflito. Para arquivos, cliente HTTP reusa tratamento de sessão e diagnóstico de download.

## Quadro de contrato por ticket

Usar templates/CONTRATO.md: operação; fonte; endpoint/método reais; DTO request/response; ID de origem; vínculos; policy; efeitos/cache; repetição; concorrência; erro; consumidor adicional; cenário; versão. Campos não descobertos ficam pendentes, sem exemplo apresentado como API operacional.
''',

'docs/arquitetura/PERMISSOES_CANDIDATAS.md': '''# Matriz candidata de acesso do piloto

P04-01 confirma a matriz com o responsável de negócio. Os nomes de papéis abaixo organizam a conversa; não são roles criadas ou contas reais. Permissão de empresa, carteira/recurso e ação é conferida no servidor.

| Ação | Administração do contexto | Operação designada | Consulta designada | Apoio técnico |
|---|---|---|---|---|
| Consultar contatos | Dentro do contexto permitido | Dentro da carteira permitida | Somente carteira autorizada | Não recebe conteúdo por padrão |
| Criar/alterar contato | Se a policy autorizar | Se a policy autorizar | Negado | Negado por padrão |
| Registrar interação/próxima ação | Se autorizado no recurso | Se autorizado no recurso | Negado | Negado por padrão |
| Importar o recorte | Ação específica autorizada | Somente se delegada | Negado | Não concede importação por suporte |
| Enviar documento | Categoria/recurso permitidos | Categoria/recurso permitidos | Negado | Negado por padrão |
| Revisar/liberar documento | Permissão explícita de revisão | Somente se delegada | Negado | Não concede revisão por suporte |
| Baixar documento | Categoria/recurso permitidos | Categoria/recurso permitidos | Somente categoria liberada ao papel | Negado por padrão |
| Alterar tarefa/protocolo | Policy e recurso permitem | Designação/escopo permitem | Negado | Negado por padrão |
| Consultar auditoria | Ação específica e conteúdo minimizado | Apenas histórico funcional permitido | Apenas histórico permitido | Diagnóstico sanitizado quando autorizado |
| Configurar identidade/perfis | Permissão administrativa específica | Negado por padrão | Negado | Somente autorização específica e auditada |

## Casos mínimos de fronteira

Usuário de B tentando ID de A; operador fora da carteira; consulta tentando escrita; sessão revogada; usuário sem vínculo; troca A/B com cache; arquivo restrito; exportação fora do escopo; header adulterado; cadastro/arquivo de B vinculado a processo de A. Esses casos são mapeados aos tickets e não dispensados por origem já testada.

Ausência de botão não substitui recusa de API. Perfil admin não confere automaticamente acesso a categoria sensível ou a todos os clientes. Não criar usuários reais para preencher a matriz do planejamento.
''',

'docs/produtos/SITE_ESSENCIAL.md': '''# Site essencial: recorte adiado

## Resultado

Um site de até cinco páginas com marca e conteúdo fornecidos/autorizados, navegação consistente, contato definido e manual. Recorte adiado, com 12h anteriores a reestimar; zero horas alocadas neste ciclo. IDs P03-01 a P03-06 preservados no backlog posterior. O pacote independe do Core novo e da correção do onboarding CRM.

## Jornada e páginas

| Página | Conteúdo/ação | Critério |
|---|---|---|
| Home | Empresa, proposta clara, serviços e acesso ao contato | Identidade correta, links válidos, sem promessa sem prova |
| Serviços | Oferta e caminho de contato | Serviços fornecidos/revisados, sem páginas vazias |
| Sobre | Empresa/equipe com material autorizado | Nome/foto/origem conferidos, sem métricas inventadas |
| Contato | Canal manual ou formulário existente escolhido | Resultado coerente com a ação efetiva |
| Privacidade | Informação alinhada à coleta realmente usada | Conteúdo revisável, sem certificar conformidade universal |

Selecionar EBT estático ou CRP Razor, justificando necessidade de persistência/admin já existente. Reusar layout/tokens/assets próprios. Não adicionar um novo CMS para fechar este pacote.

## Formulário e canal

No canal manual, abrir conversa/link é apenas abertura. No formulário servidor, confirmar somente após registro persistido; testar erro/timeout, preservar campos e oferecer alternativa correta. O site sozinho não promete registrar uma oportunidade CRM sem integração demonstrada.

## Matriz focal

Home e contato em celular/computador; menu e foco de teclado; imagens/links; fluxo de formulário/canal; estado de erro; proteção de painel privado existente. R1 somente se contrato/ambiente relevante não mudar. Ao tocar gravação/autorização, promover para R2/N.

## Pacote de entrega

Fonte selecionada/versionada, configuração de identidade, conteúdo/assets autorizados, relatório focal, canal efetivo, manual, requisitos de host/domínio e retorno. Hospedagem e publicação do cliente permanecem decisões de implantação; nenhum serviço pago é escolhido por este documento.
''',

'docs/produtos/CRM_CONNECT_INICIAL.md': '''# Cadastro e jornada CRM do EBT Connect

## Resultado e janela

Cadastro único, organização, contatos, histórico, até cinco etapas fixas, responsável e próxima ação. Segurança P04 e funcionalidades P05 fecham até 92h cumulativas; tarefas P07 completam o checkpoint em 104h e comunicação P11 fecha em 140h; duas configurações sintéticas usam a mesma regra. Isso não é Connect completo do plano mestre.

## Fluxo

Login/ativação -> lista -> criar contato -> abrir detalhe -> registrar conversa ou nota -> definir responsável/prazo -> mudar etapa -> recarregar -> consultar histórico. A mesma identidade acompanha todo o encadeamento.

## Recortes de interface

Lista: busca/paginação/filtro e estados carregar/vazio/erro/negado. Detalhe: identificação, organização, canais mínimos, etapa e origem. Histórico: autor, instante, tipo/direção e sequência. Próxima ação: responsável ativo, prazo e descrição. Alteração: resultado persistido ou falha recuperável; concorrência preserva entradas e pede nova conferência.

## Regras

Normalização de canal não une pessoas de empresas diferentes. Cadastro e interação usam contratos da fonte quando compatíveis. Nota interna não conta como conversa. Uma conversa antiga não substitui a última pela ordem de inserção. Responsável deve existir no escopo. Rótulo configurável não renomeia enum/ID. Cache lista/detalhe é invalidado conforme o resultado.

## Importação delimitada

Um layout fixo e até 100 contatos sintéticos. Área de preparação com preview/erros, confirmação explícita e resultado persistido/idempotente. Não é importador universal nem autorização para processar planilhas reais. A necessidade comercial de maior volume recebe medição e proposta própria.

## Aceite

G-SEG vigente; jornada QA em A/B; permissão por perfil/carteira e ID direto; repetição/conflito; cadastro único após reload; duas marcas sem forks de regra; manual e limites. P05 não implementa canal externo; resposta por API/webhook pertence a P11 e G-MSG. Fora: inbox coletivo avançado, campanha automática, chatbot, financeiro, OS e proposta comercial completa. Ver docs/produtos/ENTREGA_EBT_CONNECT.md.
''',

'docs/produtos/DOCUMENTOS_E_TAREFAS.md': '''# Documentos privados e composição com tarefas do Connect

## Documento

Escolher uma categoria comercial e seu vínculo com contato/processo. P06 entrega metadado, binário privado, hash/versão, revisão/decisão e download autorizado. Estados candidatos: pendente -> revisado/liberado ou rejeitado, com decisão explícita por versão. Nomes finais respeitam o contrato adequado da fonte.

Upload novo não é aprovação; revisão não é assinatura digital. Falha de storage mantém operação sem confirmação de liberação. Nova versão não reescreve arquivo anterior nem herda aprovação. Download revalida recurso/tenant/categoria, inclusive quando a entrega de bytes usa URL temporária.

A política de scan/liberação deve ser fechada no recorte. Sem a dependência necessária, a demonstração usa fixture confiável em QA e não libera arquivos arbitrários amplamente. Retenção, tamanho e tipos são parâmetros de decisão, não números inventados no planejamento.

## Tarefa

P07 já entrega em 104h a tarefa com contato de origem, responsável, prazo, estado e resultado. Ligação documental é demonstrada em P06-02/P06-08 após o GED, sem bloquear a tarefa comercial inicial. Criar -> acompanhar -> concluir ou cancelar, com motivo/resultado e histórico. Idempotência do fechamento, concorrência e regra temporal precisam do cenário pertinente. Exibição de pendência interna não implica e-mail, calendário ou WhatsApp enviado.

## Composição

O mesmo cadastro pode ter documento e tarefa; vínculo por ID e empresa preserva autorização. Uma tarefa pendente não concede direito ao arquivo. Documento revisado não encerra tarefa automaticamente sem regra especificada. Métrica da tarefa reconcilia com a lista e o período.

## Entrega

Até 164h cumulativas: fluxo GED de uma categoria, tarefa ligada, prova negativa de acesso, versão/retry/conflito, restore de banco/arquivo/chave e manual. Não é plataforma clínica, GED integral ou assinatura eletrônica homologada.
''',

'docs/produtos/FLOW_PILOTO.md': '''# Pacote 4: protocolo e tramitação mínima

## Delimitação

Recorte adiado fora deste ciclo; tickets P08-01 a P08-08 e estimativa anterior de 24h preservados no backlog posterior. Nenhuma janela cumulativa vigente ou hora alocada. Reestimar após gates de segurança, documentos e tarefas. Escopo anterior: um tipo de protocolo, numeração por tenant/ano e três estados fixos.

## Estado e ação candidata

| Estado atual | Ação | Próximo estado | Requisitos |
|---|---|---|---|
| Ausente | Abrir protocolo | Aberto | Interessado/responsável válidos, tipo/ano, chave da operação |
| Aberto | Iniciar análise | Em análise | Ator autorizado no recurso e versão vigente |
| Em análise | Concluir | Concluído | Resultado, ator autorizado e versão vigente |
| Concluído | Consultar | Concluído | Consulta autorizada; não modifica decisão |

Outras transições ficam negadas no piloto até especificação própria. Reabertura/rejeição/despacho complexo não são acrescentados por estética. O responsável de negócio confirma esta tabela em P08-01.

## Consistência

Número visível não substitui ID interno. Sequência e abertura são transacionais em SQL com unicidade por escopo. Mesma chave/payload retorna o protocolo existente; chave incompatível não cria duplicata. Interessado, documento e responsável de outra empresa são recusados. Estado e movimento confirmado mantêm coerência; versão obsoleta retorna conflito.

## Cenários

Criações concorrentes; reenvio após resposta perdida; duas pessoas tramitem o mesmo registro; estado inválido; usuário consulta tentando alterar; ID de B; anexo privado; falha transacional; reload e restart. SQL real é necessário para índice/concorrência; execução em memória não satisfaz G-FLOW.

## Limite de produto

O recorte é uma tramitação fixa com parte das capacidades iniciais W1/W2. Não implementa W3/W4, designer, condições dinâmicas, timers, e-SIC, sigilo público regulado ou assinatura. Se segurança/reuso consumirem a reserva, transportar este pacote ao ciclo seguinte e não declará-lo entregue.
''',

'docs/produtos/CANDIDATO_E_IMPLANTACAO.md': '''# Candidato para piloto e implantação futura

P09 compõe resultados que passaram em seus próprios gates. A capacidade de 16h cobre manifesto, jornadas integradas, ensaios de migration/restore, operação e preparação do aceite. Marco de 180h futuras, não produção.

## Dossiê do candidato

Commit/versão; hashes do pacote; configuração sem segredos; fontes/licenças; migrations aplicáveis; resultado por ticket/caso/gate; ambiente; consumidor A/B; relatórios e capturas sanitizados; manual; rollback/forward fix; restore; limitações; saldo/reserva; lista de pendências.

## Entrada do piloto real

Confirmar organização, fluxo contratado, usuários reais e perfis, pessoa que homologa, dados autorizados, ambiente/domínio, credenciais mantidas fora do repositório, suporte acordado e janela de implantação. Instalar o pacote que corresponde ao manifesto. Não usar snapshots de cliente como fixture por conveniência.

## Critério de aceite

Usuário executa a jornada combinada, registra resultado, data, identidade e ressalvas. Desenvolvedor não assina em nome do cliente. Texto de aceite preparado e links abertos não são execução ou aprovação. Resultado parcial mantém lista de cenários pendentes e bloqueios.

## Depois do candidato

Medir esforço da primeira implantação e operação, estabilizar o recorte e repetir segundo consumidor. Só então ampliar notificações/integrações, Flow W3/W4, Portal/CMS ou produto específico. Não converter este candidato em proposta de plataforma regulada completa.
''',
}

DOCUMENTS.update({
'docs/execucao/COMO_EXECUTAR_E_CONTINUAR.md': '''# Roteiro de execução e continuidade

## Estado atual

O repositório contém planejamento finalizado e detalhado. Os 77 itens de produto estão planejados; a documentação concluída não os marca executados. Começar por P01-01 quando houver solicitação de implementar o plano.

## Uma entrega por recorte

1. Abrir a ficha em docs/execucao/entregas e o resumo da fase.
2. Confirmar entrada e dependências; os aliases Pxx-GATE correspondem ao gate real da fase.
3. Conferir fonte e diff pertinente; congelar a versão do recorte sem tocar alterações de terceiros.
4. Implementar os passos específicos da ficha, com dados sintéticos e ambiente próprio.
5. Aplicar R1/R2/N ao comportamento realmente alterado. Se mudar segurança/schema/contrato/storage, subir a trilha.
6. Registrar saída, testes/cenários, versão, ambiente, limitações e horas reais.
7. Salvar evidência sanitizada e atualizar status com caminho da prova.
8. Conferir o gate e o impacto no consumidor seguinte. Um ticket de gate não dispensa os anteriores.

## Ordem e dependência

As janelas do orçamento definem a ordem padrão de uma pessoa, sem pressupor equipe paralela. O grafo distingue dependência funcional e ordem de esforço: site e segurança dependem da fundação, mas o site pode continuar se o onboarding CRM estiver bloqueado. Isso não autoriza duas pessoas ou duas frentes consumirem as mesmas horas.

## Ficha e prova

A ficha detalha entrega, origem, passos, cenários, falha conhecida, campos de evidência e composição das horas. Os cenários estão planejados, não executados. A prova deve identificar versão/hash e ambiente; uma captura de tela não comprova persistência/SQL, e uma suíte de domínio não comprova integração real.

## Atualização de status

Editar planejamento/backlog_200_horas.json para horas reais, estado e referência de evidência. Guardar registros operacionais em evidencias/execucao/ quando de fato existirem. Não preencher resultados/aceites sintéticos para aparentar avanço. Gerar novamente as fichas com organizar_projeto.py e conferir diffs. Conteúdo gerado é protegido contra sobrescrita silenciosa de edições manuais.

## Comandos documentais

```powershell
python scripts/verificar_plano.py
python scripts/verificar_organizacao.py
```

Os comandos verificam documentos e dados do planejamento; não constroem, testam ou publicam os produtos. O gerador histórico planejar.py não deve ser usado para recriar a baseline e apagar organização/estados. Para a organização atual, usar scripts/organizar_projeto.py.

## Troca de chat ou colaborador

Enviar caminho/repositório, commit, ticket ativo, gate, fonte congelada, o que passou, falha/bloqueio, prova, horas reais, reserva consumida e próximo passo. Consulte CONTINUAR_EM_OUTRO_CHAT.md. Ler apenas o README não substitui a ficha do ticket e as instruções da fonte.
''',

'docs/qualidade/ESTRATEGIA_DE_EVIDENCIAS.md': '''# Estratégia de evidências e verificação proporcional

## Níveis separados

| Nível | O que demonstra | O que não demonstra |
|---|---|---|
| Documento/inspeção | Estrutura, contrato e proposta identificados | Execução funcional |
| Build/teste local | Cenários daquela versão e ambiente | Aceite do cliente ou produção |
| CI | Workflow e casos executados no commit consultado | Tudo que não faz parte daquele workflow |
| QA autenticado | Jornada dos perfis e dados usados | Integração de fornecedor sem sandbox/prova |
| Homologação do usuário | Aceite do cenário com autoria e versão | Escopos não executados |
| Produção verificada | Revisão implantada, saúde e smoke do escopo | Ausência universal de defeitos ou conformidade ampla |

## Reusar prova

Associar cenário, versão/hash, configuração relevante, ambiente e resultado. Confirmar equivalência do comportamento; diferenças em schema, policy, cache, DTO, conexão ou storage invalidam a dispensa de regressão do caso afetado. Evidence histórica da revisão permanece em inventario_fontes.json e github_vikings_snapshot.json com sua data. Não atualizar seus timestamps para aparentar uma consulta nova.

## Casos

planejamento/cenarios_verificacao.json define cenário por ticket e estado nao_executado. Cada cenário é um recorte verificável, não necessariamente um novo teste automático. Usar suíte existente que realmente cobre o comportamento; adicionar caso novo apenas quando regra/fronteira/defeito novo exigir.

R1: origem/hash/diff, smoke e visual/build pertinente. R2: contrato, resultado persistido, vínculo e consumidores afetados. N: negativas, SQL real, idempotência, concorrência e recuperação pertinentes ao critério. RES: selecionar casos afetados pelo incidente real. Não repetir indiscriminadamente a suíte inteira a cada alteração textual.

## Registro mínimo

ID de cenário/ticket; versão/hash; fonte/config relevante; ambiente; dados sintéticos; passos; expectativa; observado; comando/artefato de prova; resultado; limite; autoria/data. Resultado nao_aplicavel exige motivo aprovado para o recorte e não pode excluir o único caso de segurança/banco que sustenta o gate.

## Falhas históricas

CASST: SQL conclusivo aprovado é distinto de retestes anteriores falhos; onboarding continua pendência observada na revisão de origem. Vikings: main/PR têm prova temporal de CI, sem aceite operacional. EBT/CRP/Nutrição: publicação/backup registrados são históricos, sem repetição atual por esta organização documental.

## Sanitização

Não versionar token, senha, string de conexão privada, banco, documento real ou convite individual. Capturas/logs pertinentes devem limitar dados à massa sintética e aos campos de diagnóstico seguros. Guardar bytes privados e credenciais no ambiente apropriado, fora da documentação de consulta.
''',

'docs/operacao/AMBIENTES_E_CONFIGURACAO.md': '''# Runbook candidato: ambientes e configuração

Status: procedimento para futura implementação. Nenhum ambiente EBT de produto foi provisionado pela organização documental.

## Pré-requisitos

Ticket autorizado, fonte do recorte, nomes reais dos destinos QA e usuário com acesso necessário. Separar desenvolvimento, QA sintético, piloto real e produção. Nome de recurso e conexão devem ser confirmados antes de qualquer ação.

## Passos

1. Registrar aplicação/versão, finalidade, banco, storage, identidade, chaves e responsáveis.
2. Validar que o destino pertence ao EBT QA escolhido, sem reutilizar CASST/CRP/Nutrição/Vikings reais.
3. Mapear nomes de opções e origem dos valores privados; manter exemplos sem credenciais.
4. Definir diferença Dev/QA: modo de headers de desenvolvimento não autentica fora de Dev.
5. Conferir opções obrigatórias e falha segura quando ausentes; evitar fallback de conexão.
6. Iniciar somente com massa sintética. Conferir health e um registro persistido.
7. Registrar comandos reais e resultado; retirar do manual valores privados e links de convite.

## Verificação e retorno

Clone/config documentados iniciam no QA autorizado. Config incorreta não toca outro banco. Antes de trocar opção, salvar configuração segura anterior e definir retorno. Não apagar/recriar destino calculado sem confirmar caminho absoluto e escopo. Registrar pendência se ambiente/credencial ainda não existir.
''',

'docs/operacao/MIGRACAO_E_COMPATIBILIDADE.md': '''# Runbook candidato: migration e compatibilidade

## Entrada

Migration do recorte, versão anterior sintética, destino QA conferido, backup consistente, índices e consumidores que serão afetados. Responsável técnico confirma a estratégia de retorno; ausência desses itens impede execução da migração daquele recorte.

## Procedimento

1. Registrar schema/versão atuais e lista de migrations aplicadas.
2. Conferir diff gerado, unicidade por tenant, campos opcionais/obrigatórios, FKs e efeitos nos IDs existentes.
3. Aplicar em banco vazio de QA para provar instalação nova.
4. Aplicar em cópia sintética da versão anterior para provar atualização.
5. Comparar contagens, IDs/vínculos, estado e cenários críticos, incluindo permissão e concorrência em SQL.
6. Ensaiar rollback seguro ou forward fix conforme desenho. Downgrade destrutivo não substitui recuperar dados.
7. Guardar comando, versão, resultado e evidência sanitizada; manter falhas anteriores separadas do resultado conclusivo.

## Saída

Ambos os caminhos passam; consumidores usam contratos compatíveis; retorno é conhecido e ensaiado. Nenhuma migração antiga é reescrita para ocultar diferença histórica. Produção real exige destino/janela/backup/autoridade específicos e não foi autorizada por este runbook.
''',

'docs/operacao/BACKUP_E_RESTAURACAO.md': '''# Runbook candidato: backup e restore integrado

## Escopo

Banco, binários privados, chaves de proteção e configuração necessária para interpretar os dados. A consistência deve corresponder à arquitetura SQL/storage escolhida; o desenho SQLite/Blob do portal não é copiado automaticamente para o Core.

## Ensaio QA

1. Identificar versão do código/schema e conjunto de dados sintéticos a recuperar.
2. Garantir janela consistente entre banco e arquivos conforme mecanismo da implementação.
3. Capturar manifesto de arquivos, hashes, contagens e referência segura das chaves.
4. Selecionar destino exclusivo, diferente da origem e sem credencial real reaproveitada.
5. Restaurar conjunto e conferir integridade do banco e presença dos bytes necessários.
6. Iniciar a aplicação restaurada com a configuração correta.
7. Executar login sintético, consulta por ID e download autorizado; comparar hash.
8. Tentar acesso de B e perfil sem permissão; o restore não pode remover políticas.
9. Registrar duração medida, resultado, versão, limitações e procedimentos de limpeza do QA confirmado.

## Aceite

Aplicação abre os dados certos e o arquivo baixado é idêntico. Arquivo de backup criado, arquivo ZIP íntegro ou comando de restore sem erro não bastam isoladamente. Nenhum RPO/RTO comercial foi fixado; medir no ambiente real e acordar antes de prometer prazo de recuperação.
''',

'docs/operacao/RELEASE_E_RETORNO.md': '''# Runbook candidato: release, smoke e retorno

## Candidato

Identificar commit e manifesto; conferir gates do recorte; listar migrations/config; preservar versão anterior, dados e caminho de recuperação. Pacote e resultado de build não significam que houve deploy.

## QA e piloto

1. Confirmar destino e identidade do operador antes de executar qualquer implantação.
2. Conferir config sem expor segredos; distinguir revisão nova e anterior.
3. Instalar candidato em QA permitido; aplicar somente migration ensaiada pertinente.
4. Verificar saúde/prontidão e a jornada do recorte, não apenas status Running.
5. Conferir a versão servida, assets/contratos, proteção de rotas, negativo de tenant e persistência.
6. Registrar tempo, revision/commit/digest se existirem, resultado, captura sanitizada e limitações.
7. Piloto real exige participantes/aceite; usar ficha própria com autoria.

## Retorno

Se health/jornada/isolamento falhar, interromper expansão, preservar diagnóstico e retornar conforme estratégia validada. Não misturar rollback de código com rollback de banco destrutivo. Corrigir por forward fix quando essa for a única via segura aos dados. Conferir saúde e jornada após retorno.

## Produção

Somente no escopo autorizado e ambiente confirmado. Nenhum comando específico de Azure/DNS é inventado antes de conhecer a infraestrutura. Não mexer em MX, serviço pago ou banco de outro cliente a partir do planejamento. Registro de release preenchido depois da operação, não como intenção.
''',

'docs/operacao/ACESSOS_E_INCIDENTES.md': '''# Runbook candidato: acesso e incidente

## Acesso

Confirmar organização, vínculo, perfil, carteira e categoria de documento. Convite individual tem uso/expiração/revogação conforme implementação; usuário define própria senha. Não criar conta real presumida, senha compartilhada ou aprovação em nome de terceiro. Suporte recebe diagnóstico minimizado, não acesso clínico/administrativo irrestrito.

## Incidente

1. Registrar ação, URL/rota sem dados sensíveis, instante, perfil/contexto, status e traceId.
2. Distinguir esperado, observado e tipo: acesso, persistência, arquivo, migração, contrato ou serviço externo.
3. Reproduzir em QA com massa sintética, preservando a fonte e o resultado original.
4. Avaliar consumidores e dados afetados. Vazamento de tenant/categoria suspende a capacidade afetada até conter e provar correção.
5. Aplicar menor correção adequada; registrar teste pertinente e efeito em migration/contrato/cache.
6. Repetir o cenário e regressões afetadas; usar reserva se houver trabalho extra registrado.
7. Fechar com causa, versão corrigida, resultado, medida preventiva e pendências.

Falha simulada prova recuperação da simulação, não reprodução do incidente histórico. Erro “SQL” não determina causa sozinho. Notificação ao usuário/cliente, quando necessária, depende de autorização e destinatário definidos; este runbook não envia mensagens.
''',

'docs/arquitetura/adr/ADR-001_REAPROVEITAMENTO.md': '''# ADR-001: preservar fontes e extrair recortes

Status: direção de planejamento; confirmação técnica do recorte em P02-01. Contexto: CASST/Vikings já fornecem domínio/UI/infra, mas possuem regras e alterações próprias.

Decisão recomendada: manter contratos/IDs, selecionar fluxo e extrair somente capacidade comum com segundo consumidor robusto. Marca/vocabulário configuráveis não autorizam renomear persistência. Não absorver PR draft Vikings sem sua revisão/gate.

Alternativas consideradas: reescrita integral (alto retrabalho e perda de conhecimento); cópia independente por cliente (correções divergentes); abstração universal antecipada (complexidade sem uso). Consequência: baseline e prova de compatibilidade precedem extração; nem todo domínio SST vira Core.

Revisitar se o recorte não puder ser licenciado, generalizado ou isolado com custo proporcional. Tickets: P01-01/P01-05/P02-01/P05-08.
''',

'docs/arquitetura/adr/ADR-002_TENANT_E_IDENTIDADE.md': '''# ADR-002: empresa e escopo resolvidos no servidor

Status: direção de proteção do planejamento; desenho concreto a confirmar em P04. Contexto: trocar de cliente/tenant é uma nova fronteira mesmo quando o código veio de fonte validada.

Decisão recomendada: contexto derivado de identidade/vínculo ativo, autorização por ação/recurso, índices e cache compatíveis com o tenant. SQL real deve provar negativas e concorrência pertinentes. O modo DevHeader da fonte não deve autenticar fora de Development.

Alternativas rejeitadas para o recorte: TenantId editável como autoridade, isolamento só por UI, cache global sem escopo, admin técnico com acesso irrestrito. Consequência: G-SEG bloqueia consumidores quando há vazamento. Cookie/OIDC/JWT/provedor permanecem escolha específica, sem inventar um novo mecanismo de login.

Revisitar separação por banco se risco/contrato/carga exigir; não está comprometida no ciclo inicial. Tickets: P04-01 a P04-12.
''',

'docs/arquitetura/adr/ADR-003_DOCUMENTO_E_TRANSACAO.md': '''# ADR-003: arquivo privado e decisão por versão

Status: desenho candidato a confirmar em P06. Contexto: banco guarda metadado e storage guarda bytes; os dois não compartilham necessariamente a mesma transação.

Decisão recomendada: upload inicialmente pendente, hash dos bytes efetivos, autorização por recurso no download e revisão associada à versão exata. Falha fora da transação não produz sucesso falso; reconciliação/compensação fica explícita. Restore abrange banco, binários e chaves necessárias.

Alternativas inadequadas: arquivo público com link secreto como única proteção; sobrescrever aprovação passada; chamar aprovação interna de assinatura digital; backup apenas SQL sem conferir bytes.

Consequência: scan/política de liberação ausentes mantêm restrição; provedor privado real é escolhido em P02-05/P06. Tickets: P06-01 a P06-08/P09-06.
''',

'docs/arquitetura/adr/ADR-004_PROTOCOLO_FIXO.md': '''# ADR-004: protocolo com fluxo fixo antes do engine

Status: proposta de recorte a confirmar em P08-01. Contexto: um engine configurável excede a capacidade reservada ao primeiro Flow.

Decisão recomendada: um tipo, estados abertos/em análise/concluídos, ator definido, número único por tenant/ano e mudança de estado/histórico coerentes. Concorrência e idempotência são provadas no SQL real. Não usar max+1 sem proteção.

Alternativas adiadas: designer, branching, formulários dinâmicos, timers, W3/W4 e portal externo. Consequência: produto é piloto manual delimitado; futuras capacidades recebem novo escopo. Se a reserva se esgotar, adiar este pacote em vez de cortar testes de segurança.

Tickets: P08-01 a P08-08. Reavaliar após demanda recorrente e resultado do piloto.
''',
})

TEMPLATES = {
'ENTREGA.md': '''# Registro de entrega

- Ticket e critério: a preencher.
- Versão/commit/hash e origem: a preencher.
- Responsável/autoria e instante: a preencher.
- Ambiente e massa sintética: a preencher.
- Entrada/dependências satisfeitas: a preencher.
- Arquivos/contratos alterados e efeitos em consumidores: a preencher.
- Trilha inicial e efetiva; motivo de mudança: a preencher.
- Cenários/comandos; expectativa e observado: a preencher.
- Resultado e caminhos de evidência sanitizada: a preencher.
- Limitações e dependências externas não testadas: a preencher.
- Horas reais, sessão de esforço e reserva associada: a preencher.
- Estado comprovado e próximo passo: a preencher.

Este template vazio não é prova de execução.
''',
'CONTRATO.md': '''# Registro de contrato do recorte

Operação; ticket; fonte/hash; endpoint/método reais; DTO de entrada/saída; ID de origem; vínculos/cardinalidades; policy e escopo; efeito no histórico/cache; chave idempotente; concorrência; erros; consumidores; cenários; versão; compatibilidade/migration; pendências. Preencher conforme código encontrado, sem apresentar exemplos como endpoints existentes.
''',
'DECISAO.md': '''# Registro de decisão

ID/ticket; assunto; status (proposta/confirmada/substituída); opções; recomendação; decisão efetiva; motivo; fonte/prova; pessoa responsável; instante; impacto no orçamento/contratos/dados; autorização de mudança de escopo quando pertinente; reversibilidade; ADR relacionado; próxima revisão. Campo ausente permanece pendente.
''',
'BUG.md': '''# Registro de falha

ID/ticket; ambiente/versão; instante/traceId sanitizado; esperado/observado; reprodução; prova; dado sintético; causa confirmada ou hipótese; consumidores afetados; correção; teste pertinente; regressão; resultado; migration/contrato; reserva/tempo real; medida preventiva; pendência. Separar incidente observado de simulação.
''',
'GATE.md': '''# Fechamento de gate

Fase/gate; versão; tickets pertinentes; dependências; cenários e evidências; falhas não resolvidas; itens não aplicáveis com motivo; responsável pela conferência; resultado (pendente/aprovado/bloqueado); data; consumidores liberados naquele escopo; próximo passo. Gate não aprova produção automaticamente.
''',
'ACEITE_PILOTO.md': '''# Aceite de piloto

Produto/escopo; cliente/organização; versão/ambiente; identidade de quem executou; data; jornada e cenários; esperado/observado; resultado por caso; ressalvas; dados autorizados; decisões pendentes; responsável de negócio; confirmação efetiva do usuário; próximo passo. Não preencher autoria, execução ou aceite em nome de terceiro.
''',
'RELEASE.md': '''# Registro de release

Produto; versão/commit; manifesto; ambiente/destino conferido; operador autorizado; gates; config segura; migrations; backup/restore; versão anterior; comando real; resultado de implantação; revisão/digest/URL quando existirem; health/smoke/jornada; prova pós-operação; rollback/forward fix; limitação; pendências. Pacote preparado não comprova deploy.
''',
'ESFORCO.md': '''# Sessão de esforço

ID único da sessão; ticket afetado; pessoa; data; atividade executada; horas reais; alocação normal ou reserva; ID da reserva se usado; causa do extra; prova da atividade; saldo conciliado. Não atribuir a mesma hora ao ticket original e à reserva. Hora estimada não é hora trabalhada.
''',
}
