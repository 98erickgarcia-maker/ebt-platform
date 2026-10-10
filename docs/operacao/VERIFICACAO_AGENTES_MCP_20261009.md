# Verificacao de agentes e MCP - 09/10/2026, 20h06 BRT

## Estado observado

| Componente | Evidencia nesta verificacao | Conclusao |
|---|---|---|
| Runner na VPS | Manifesto `planejamento/engineering_blocks.json`: 10 papeis, 10 tarefas FLOW-01 a FLOW-10, concorrencia 1. Checkpoint remoto: `current_task=FLOW-01`, `completed=[]`, `calls_today=1`, `status=quota`. | Dez papeis configurados; nenhuma tarefa comprovadamente concluida. Nao sao dez processos simultaneos. |
| Cota | Checkpoint remoto registra `cooldown_until=2026-10-10T02:57:48Z` (09/10, 23h57 BRT). `allow_paid_api=false`; fallback configurado para aguardar. | Runner aguarda fim do cooldown e novo ciclo do timer. A credencial OpenAI do n8n nao e fallback do runner. |
| VPS | `ebt-engineering-runner.timer` e `ebt-engineering-watch.timer` ativos; bridge `active`; container n8n `healthy`. | Agendamento e infraestrutura vivos, sem prova de codigo novo. |
| Watcher | Ultima observacao: `state=blocked`, `code=quota`, `changed=false`. O script retorna 2 para estados bloqueados, por contrato, e o systemd mostra a ultima unidade como `failed`. | Falha do servico de observacao e sinal de bloqueio do trabalho; nao foi mascarada como sucesso. O timer continua ativo. |
| n8n | Workflow `EbtEngineering15min01` publicado; execucoes automaticas 2 (19h45) e 3 (20h00) com status Success na interface. | Cadencia de 15 minutos comprovada para dois ciclos. Sucesso do workflow significa pedido aceito pela bridge, nao tarefa FLOW aprovada. |
| MCP n8n | Settings > Instance-level MCP: habilitado; 0 workflows enabled, 0 agents exposed, 0 connected clients. Agents Preview: nenhum agente criado. | Nenhum cliente externo tem acesso observado. Os dez papeis do runner nao sao agentes nativos do n8n. |

O MCP integrado do n8n pode pesquisar, executar, criar e editar workflows conforme as permissoes concedidas. Nao habilitamos o workflow de engenharia para MCP: isso ampliaria a capacidade de acionar o controlador, sem beneficio para a supervisao ja operacional. O painel permanece acessivel por tunel SSH local. A tela mostra `Allowed callback URLs: All`; antes de conectar um cliente OAuth, definir e validar os callbacks confiaveis. Referencia: https://docs.n8n.io/connect/connect-to-n8n-mcp-server/ .

Foi criada uma automacao de acompanhamento neste chat, a cada 15 minutos, para verificar a VPS por leitura e avisar somente mudanca relevante, falha nova ou progresso comprovado. Ela nao substitui os timers da VPS e nao inicia chamadas pagas. A proxima prova de programacao exige artefato/diff e criterios de FLOW-01, apos uma execucao real sem bloqueio.

Este snapshot nao altera o orcamento de 180h de entregas + 20h de reserva, a politica de publicacao ou o estado dos modulos.
