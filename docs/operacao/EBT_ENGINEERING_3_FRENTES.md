# EBT Engineering Master: 3 frentes

Atualizacao 2026-10-09. Documento de orquestracao do EBT Enterprise. A fonte de verdade e o GitHub: tarefas e evidencias na issue #14, commits/PRs e GitHub Actions. Nao ha transferencia automatica de historico entre conversas nem execucao de tres modelos continuamente.

## 1. CHAT-01 — Coordenacao e controle (dono do plano)

- Consultar issue #14 e comentarios, GitHub PRs, commits e checks desde a ultima rodada; verificar HEAD de cada branch, risco e conflito de arquivos.
- Priorizar um unico incremento curto e independente para CHAT-02 e um para CHAT-03 por rodada, sem solicitar trabalho duplicado. Respeitar escopo da issue #14.
- Reconciliar revisoes dos PRs #15 e #16. O verificador de continuidade exige hashes de codigo previamente REVISTO; comparar diff, requisitos e testes antes de registrar uma nova aprovacao. Nunca substituir hashes cegamente para esconder o erro.
- Registrar uma unica sintese da rodada com resultados das tres frentes, data/hora da verificacao, SHA, PR, evidencia e proximo passo. Notificar somente mudancas materiais.
- O CHAT-01 nao aprova sozinho revisao cruzada independente, nao faz merge automatico e nao implanta recursos.

## 2. CHAT-02 — Frontend e experiencia visual

- Fonte de runtime: branch codex/ebt-enterprise-continuity-reviewed-20261008 (referencia historica 0177b5cad13a3003de5f240d7bea432cba825e47); atualizar o HEAD antes de usar.
- Primeira tarefa EBT-EM-001: revisar PR #15 (feat/chat02-ebt-shell-qa-20261009), verificar acessibilidade de menu mobile, Escape/foco, reflow, navegacao Platform / Connect, testes Playwright e responsividade 320/390/768/1366.
- Proxima etapa visual, somente apos fechamento da revisao e registro do novo escopo: implementar a linguagem EBT FLOW + AURA primeiro em Meu dia, depois Contato 360. Preservar preto #111214, grafite #1B1D20, off-white #F6F6F4, laranja #FF853E e logo EBT oficial.
- Evitar interface com dezenas de caixas quadradas identicas; usar composicao fluida, curvas e leve profundidade, sem comprometer densidade de tabelas, acesso por teclado, movimento reduzido ou comportamento real.
- Para cada alteracao: diff pequeno, commit em branch isolada, teste pertinente, evidencias visual e funcional, PR draft. Marcar BLOQUEADO quando navegador ou SDK nao estiver disponivel; nunca inventar screenshots ou testes.
- Escritas do recorte EBT-EM-001: src/frontend/src/App.tsx, src/frontend/src/style.css, src/frontend/src/PlatformApplications.tsx, src/frontend/e2e/navigation.spec.ts, src/frontend/e2e/platform.spec.ts. Outros arquivos exigem nova atribuicao coordenada.

## 3. CHAT-03 — Backend, integrações e testes

- Primeira tarefa EBT-EM-002: revisar PR #16 (test/chat03-ebt-graphmail-fail-safe-20261009) em GraphMail.cs e MailChecks.cs. Executar apenas testes sinteticos/fakes para tokens ausentes ou invalidos, caixa bloqueada, HTTP 403, 429, 5xx, transporte incerto, isolamento da caixa e nao repeticao automatica de envio incerto.
- Registrar falhas por causa raiz e prova; se houver correcao pequena autorizada, branch propria e PR draft. Cuidado especial com fronteiras de tenant, fila persistente SQL, autenticacao e dados sensiveis.
- Nao enviar emails de teste reais, nao mudar secrets, worker, migrations, Azure, banco ou caixas de producao. Nao transformar aceite Graph em prova de entrega/leitura.
- Escritas iniciais: src/backend/Ebt.Platform.Api/GraphMail.cs e tests/WazVox.ProtocolTests/MailChecks.cs. Escopos adicionais exigem atribuicao coordenada.

## Operacao e fluxo de informacoes

1. O supervisor horario existente pode percorrer as tres frentes em uma unica rodada, em sequencia. A plataforma atingiu o limite de 10 automacoes ativas ao tentar criar uma tarefa independente adicional. Nao desativar nem copiar tarefas comerciais do usuario para abrir espaco.
2. Na rodada, ler este arquivo, a issue #14 e o estado remoto atual de ambos PRs. Marcar para cada parte: NOT_STARTED, IN_PROGRESS, WAITING_CI, REVIEW_PENDING, PASS, FAIL ou BLOCKED. Nao inferir atividade continua apenas de um cron habilitado.
3. CHAT-01 atua primeiro (estado, atribuições, riscos), CHAT-02 em seguida (frontend) e CHAT-03 ao final (backend/testes). A atividade sequencial em uma automacao NAO equivale a tres executores paralelos.
4. Para editar: confirmar permissão de escrita, branch e SHA atual antes da chamada, trabalhar com paths isolados, nunca usar force-push; se branch mudou, interromper e reconciliar. Nunca acionar deploy, merge, migração, emails reais ou servicos pagos sem autorizacao especifica.
5. Criar ou atualizar PRs ao inves de modificar main diretamente. Testes em GitHub Actions e hashes exigem provas do commit exato. Uma falha de continuidade por hash nao deve ser ignorada e tampouco significa necessariamente erro de compilacao.
6. Registrar marcos materiais na issue #14 quando a ferramenta permitir, com TASK_ID, branch, SHA base/candidato, diff, PASS/FAIL/BLOCKED/NOT_RUN, link da prova e proximo passo. Consultar comentarios antes para nao duplicar; preservar dados e autorias.
7. Ao terminar cada rodada, retornar uma resposta unica com as tres secoes e link direto aos PRs. Se nada importante mudou, nao notificar. O ChatGPT so recebe resultados quando a automacao efetivamente executa; mensagens de um chat nao passam automaticamente a outro chat.

## Monitores de operacao e Teams

- O EBT Production Watch ja tem verificacoes externas read-only e workflow cron configurado a cada 15 minutos. Build/push verde NAO comprova cron real; exigir ao menos uma execucao com event=schedule.
- O workflow EBT Teams Notifications existe na main apos PR #18, mas a entrega real ao Teams depende do secret TEAMS_WORKFLOWS_WEBHOOK_URL e do workflow criado no Teams. Sem isso, testes verdes sao apenas testes, nao prova de recebimento.
- A automacao EBT Sentinela 24h permanece separada e nao corrige codigo nem altera ambiente.

## Estado inicial verificado (09/10/2026)

- Coordenacao: issue #14 existe; controle documentado e dependencias explicitas.
- Frontend: PR #15 aberto como draft, HEAD ac7044e1ea8890bc899837b59a050d9965e042a4. Build EBT Connect aprovado; continuidade recusou tres arquivos sem nova revisao registrada.
- Backend: PR #16 aberto como draft, HEAD f963715b4a9feb05ddbaf04ab55bc28aa6afce3e. Build EBT Connect aprovado; continuidade recusou dois arquivos sem nova revisao registrada.
- Main de observabilidade: f1a370d51d00bc8e0c87f065f9020658c3822cad. Nao corresponde automaticamente ao runtime publicado; revalidar sempre.
- A instalacao deste guia nao altera PRs #15/#16, nao libera hashes e nao implica redesenho implementado.

## Criterio de aceite da orquestracao

- Guia acessivel por SHA no GitHub e referencia incluida no supervisor horario.
- A verificacao posterior produz um relatorio de tres partes baseado em estados reais; sem marcacao ficticia de progresso.
- Para completar os dois primeiros PRs: revisao real, atualizacao autorizada do manifesto apos revisao, testes com CI verde no SHA exato e revisao cruzada; depois decisao de merge separada.
- Para operacao Teams: webhook configurado e mensagem confirmada no canal.
- Para desenvolver com agentes independentes 24/7: runners Codex/LLM propriamente provisionados, cotas, bloqueio de conflitos e permissao de PRs. O agendamento ChatGPT e o GitHub Actions nao produzem uma frota persistente de agentes por si so.

Referencias: https://github.com/98erickgarcia-maker/ebt-platform/issues/14 , https://github.com/98erickgarcia-maker/ebt-platform/pull/15 , https://github.com/98erickgarcia-maker/ebt-platform/pull/16 , https://github.com/98erickgarcia-maker/ebt-platform/pull/18 .
