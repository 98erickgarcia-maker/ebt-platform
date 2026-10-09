# Revisão comercial Connect: CASST, Vikings e Mail

Referência: 09/10/2026. Candidato 0.3.0 em verificação. Não confundir com 0.2.0 publicada.

## Histórico visual antes da implementação

Foram lidas 64 sessões locais acessíveis do CRM CASST (973 mensagens). A busca encontrou 68 pedidos com termos de telas/visualização/ícones/templates em 25 sessões, incluindo pedidos funcionais e duplicados. Não é uma contagem de redesigns, nem acesso a todo o histórico externo. Foram inspecionadas quatro pranchas de prospecção/detalhe/diálogos/visão diária e os guias de 17, 20 e 24/09. As oito imagens originais mencionadas no histórico não foram todas recuperadas.

Decisões aplicadas: identidade EBT preservada; contexto, responsável e próxima ação próximos do contato; necessidade expansível; telefone acessível; modelos por canal e objetivo; mensagens preparadas preservam versão; formulário dentro do viewport; consulta e paginação reais; loading, erro, vazio e repetição revisados. Pranchas CASST não autorizam acrescentar pedidos/financeiro ao Connect.

## Funções adaptadas

| Origem | Connect candidato | Limite |
|---|---|---|
| CASST | Busca Ctrl K real, histórico/tarefas/organizações paginados, nome de organização fora da primeira página, agenda por janela, exportação ICS, duplicidade contextual | Exportação não é sincronização Outlook; duplicidade é aviso autorizado |
| Vikings | Contexto por ID, origem explícita, revisão com motivo, falha preservada e segregação de informação | Regras trabalhistas/clínicas não foram copiadas |
| Mail | Modelos locais, prévia personalizada, rascunhos, aprovação, lote de até 100 IDs, revisão preservada, limites diários, intervalo, pausa, supressão e fila SQL | Sem IA obrigatória, sem envio real homologado e sem campanha externa executada |
| Pedido atual | Qualificação, cargo/decisor informado, necessidade, canal/horário, venda → cliente ativo no mesmo ID | Connect termina na venda e mantém relacionamento comercial; operação/financeiro seguem fora |

## Substituição do MongoDB

O produto suportado implementa essas funções em .NET/EF Core/SQL Server no schema ebt_connect do banco existente. Sessões/usuários → Users/Sessions/Memberships; leads → Contacts; mensagens/modelos → MailDrafts/MailTemplates; logs → MailRevisions/Interactions/Audit; settings/suppression/quotas → MailSettings/MailSuppressions/MailQuotas; importação → Imports. `scripts/verify_sql_runtime.py` impede dependências MongoDB no build/runtime suportado. Pacotes Mail/Emergent antigos são preservados como fontes históricas, fora do build, deploy e launcher atual. Não executou migração de dados reais nem removeu MongoDB de outros projetos/da máquina.

## Outlook e confirmação automática

O worker grava a reserva antes do HTTP e registra automaticamente o resultado Graph no histórico do contato. Resposta 202 é aceite pela Microsoft, sem confirmação manual normal. Timeout/5xx/crash deixam resultado incerto, sem repetição automática. Leitura/entrega exigem eventos ou mecanismos próprios; não são inferidos. Ver [contrato oficial Microsoft](https://learn.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0#response). Caixa app-only permanece pendente de configuração e consentimento no Connect; nenhuma mensagem real foi enviada.

## Outros aplicativos e pendências anotadas

CASST: corrigir contador baseado só na página, busca visual sem função, rótulo ICS e paginação/retentativa/sessão nas telas amplas. Vikings: reduzir concentração de tela, preservar segregação clínica e provar integração de origem/versão/reconciliação. Flow/Contracts/SST: pedidos, execução, contratos, financeiro, treinamentos/certificados e obrigações pertencem aos seus recortes, com gates próprios.

Connect: importação Excel com mapeamento de colunas e validação ampliada permanece pendente; atual importação CSV controlada é preservada. OAuth Microsoft individual, leitura dos Itens Enviados para reconciliação automática de resultado incerto e assinatura/recebimento de e-mail dependem de contratos/permissões adicionais. Aprovação de arquivo exige scanner autorizado; Azure continua sem scanner ativo. Restore Azure isolado e aceite operacional não estão comprovados.

## Verificação

API/SQL: 12 cenários aprovados na massa local EbtPlatformQa_Review20261008. Protocolo Mail: 12 cenários HTTP simulados aprovados. Worker SQL: 8 cenários aprovados, incluindo intervalo medido, quota, concorrência, aceite automático no histórico e opt-out. Frontend: 9 testes de contexto aprovados. Build frontend/backend aprovados. Browser: 22 cenários locais aprovados. CI da fonte/deploy possuem registro separado; nenhum gate amplo é promovido por esse documento.

Foi encontrada e corrigida a disputa entre reserva e quota: outra réplica deve aguardar uma operação processing antes de reservar ou pausar por limite. Recuperação de processing expirada pausa a fila e mantém unknown sem reenvio. Testes do Mail original: 18 casos focais aprovados; dois testes dependentes de MongoDB parado não são prova do produto SQL adaptado.

Orçamento 180h de entregas + 20h de reserva preservado; horas reais não estimadas como realizadas.

A publicação exercitou o script SQL idempotente e identificou resolução antecipada dos objetos na regra RLS. O ALTER SECURITY POLICY foi encapsulado em SQL dinâmico. Novo ensaio local migrou uma base sintética exclusiva até a versão anterior e executou o script revisado duas vezes, sem duplicar tabelas/migrations. O mesmo caminho foi acrescentado ao CI antes de publicar; a migração EF comum isoladamente não cobria esse defeito.
