# Decisões pendentes e gatilhos

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
