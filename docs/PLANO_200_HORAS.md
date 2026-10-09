# EBT Platform: primeiras 200 horas com Connect primeiro

Execução autorizada em 07/10/2026: [estado real e provas](qualidade/STATUS_IMPLEMENTACAO_CONNECT.md). Este documento preserva o plano/contrato candidato; não promover seus estados ou casos em lote.


Revisão de prioridade: 07/10/2026. O usuário pediu revisão começando pelo EBT Connect e autorizou a escolha do planejamento mais válido. Este plano prioriza uma jornada comercial completa antes do site e do GED. Implementação dos módulos permanece planejada.

**70 entregas, 180h; cinco reservas condicionais, 20h. Total: 200 horas-pessoa.** Implementação, verificação e registro estão incluídos. Site e Flow, 14 tickets/36h, ficam no backlog posterior; 12 tickets/36h de comunicação entram no ciclo. IDs existentes são preservados; a numeração de fase/pacote identifica o recorte, não sua posição na fila.

## Primeiras entregas e prova necessária

| Ordem | Resultado candidato | Janela de esforço | Gate e limite |
|---|---|---:|---|
| Preparação | Baseline e fundação isolada | 0-28h | G0/G1; nenhuma jornada comercial homologada |
| 1a | Segurança do Connect | 28-64h | G-SEG; SQL real, onboarding e negativas A/B |
| 1b | Cadastro, histórico, funil e próxima ação | 64-92h | G-CRM; ainda falta a jornada completa de tarefas |
| 1c | Connect com tarefas do contato | 92-104h | G-TASK; checkpoint dentro da primeira entrega |
| 1 | EBT Connect inicial com API e webhook | 104-140h | G-MSG mais G0/G1/G-SEG/G-CRM/G-TASK vigentes; demonstração em QA |
| 2 | Documentos privados | 140-164h | G-GED; upload, versão, revisão, download e recuperação |
| 3 | Candidato integrado e operação | 164-180h | G-RC; migration/restore, manifesto e preparação do aceite |
| Reserva | Correções comprovadas | 20h utilizáveis em qualquer fase | Sem funcionalidade nova ou consumo obrigatório |

As linhas 1a/1b/1c são checkpoints dentro das 140h do Connect, sem dupla contagem. WhatsApp oficial é o primeiro canal candidato, com conta/versão/escopos e homologação a confirmar. Demonstração em QA, homologação do usuário e liberação são estados separados. G-RC integrado permanece em 180h; antecipar uma implantação do Connect exige pacote operacional próprio, provas e replanejamento explícito. Site e Flow não são dependências do candidato deste ciclo.

## Distribuição das 200 horas

| Fase | Horas | Janela | Acumulado | Itens | Saída |
|---|---:|---:|---:|---:|---|
| P01 Baseline e escolha do reaproveitamento | 12h | 0-12h | 12h | 6 | Mapa de fontes congeladas e primeiro fluxo escolhido |
| P02 Fundação mínima para trabalhar | 16h | 12-28h | 28h | 8 | Ambiente EBT isolado e verificações automatizadas |
| P04 Identidade, isolamento e auditoria | 36h | 28-64h | 64h | 12 | Base segura para primeiro CRM em dois contextos sintéticos |
| P05 Cadastro e jornada CRM do EBT Connect | 28h | 64-92h | 92h | 10 | CRM demonstrável com cadastro único e próxima ação |
| P07 Tarefas e prazos ligados ao cadastro | 12h | 92-104h | 104h | 6 | Tarefas do contato e composição CRM/tarefas do Connect |
| P11 Comunicação Connect por API e webhook | 36h | 104-140h | 140h | 12 | Receber, responder e acompanhar status de texto no canal homologado |
| P06 Documentos privados, recorte GED | 24h | 140-164h | 164h | 8 | Um fluxo de documento com versão, permissão e histórico |
| P09 Empacotamento e homologação interna | 16h | 164-180h | 180h | 8 | Candidato Connect/comunicação/documentos com operação e recuperação |
| P10 Reserva protegida de correção | 20h | 180-200h | 200h | 5 | Capacidade para corrigir e homologar sem aumentar escopo |

## Decisões desta revisão

P07 depende do cadastro/CRM e da segurança vigente. A primeira origem da tarefa é o contato; GED deixa de bloquear essa jornada. O contrato pode manter tipos de origem compatíveis com a fonte, mas vínculo documental só é demonstrado após P06-02/P06-08. Próxima ação e tarefa devem usar uma fonte de estado consistente, definida antes de implementar, sem duas cópias editáveis de prazo/responsável. P11 é capacidade nova de 36h, com contratos próprios e gate G-MSG, usando referências oficiais externas ao CASST.

Lista/busca do CRM e criação/lista de tarefas usam R2 como ponto de partida. Qualquer fronteira nova de tenant, autorização, schema, contrato ou storage recebe N nos cenários afetados. R1 fica restrito a componentes e cenários cuja equivalência estiver demonstrada.

O PDF consolidado de 06/10/2026 permanece preservado como histórico, com a ordem antiga. Esta revisão, o backlog JSON e as fichas regeneradas têm precedência para a próxima execução. Nenhuma evidência histórica foi atualizada para aparentar execução nova.

## Leitura e execução futura

- [Contrato da primeira entrega Connect](produtos/ENTREGA_EBT_CONNECT.md).
- [Resposta por API e webhook](arquitetura/CONNECT_API_E_WEBHOOK.md).
- [Site e Flow adiados](../planejamento/backlog_apos_200_horas.json).
- [Revisão do projeto e correções de planejamento](qualidade/REVISAO_PROJETO_CONNECT.md).
- [Backlog detalhado](BACKLOG_200_HORAS.md).
- [Dependências e gates](execucao/DEPENDENCIAS.md).
- [Pacotes na ordem de esforço](execucao/PACOTES_CODEX.md).
- [Validação proporcional](VALIDACAO_E_GATES.md).
- [Fonte de horas e status](../planejamento/backlog_200_horas.json).
- [PDF histórico de 06/10/2026](../output/pdf/EBT_Plano_Primeiras_200_Horas.pdf).
