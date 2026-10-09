# PAC-01 — primeira rodada de execução EBT

Data: 09/10/2026. Checkout: EBT PLATAFORM, worktree 5842. Base EBT: `43a42bfe0b1daf07a96a3cacb19a9ff2b265bc5d`. Coordenação: Codex; três agentes para baseline/evidências, recorte/contratos e direitos/dependências. O limite solicitado de até dez agentes foi respeitado; esta sessão permite três agentes auxiliares simultâneos.

Autorização: pedido atual inicia a execução do roteiro; observação posterior restringe todas as edições ao EBT PLATAFORM. Projetos-fonte foram consultados somente em leitura. Alteração preexistente `.codex/` foi preservada e fica fora do commit da rodada. Orçamento mantido: 180h de entregas e 20h de reserva.

## Resultado concreto e limites

Executada a inspeção e produção dos artefatos de baseline do PAC-01. Nenhum módulo funcional EBT, banco, ambiente de QA ou aplicação foi implementado nesta rodada. G0 permanece pendente; PAC-02 não foi iniciado. Seguir exatamente o roteiro impede iniciar a fundação antes do fechamento do gate.

| Ticket | Artefato produzido | Estado desta rodada / pendência |
|---|---|---|
| P01-01 | [Manifesto](baseline/manifesto-fonte.json), [status sanitizado](baseline/status-fonte.json), [registro](baseline/registro.md) | Em verificação: hashes incluem modificados/untracked; manifesto de metadados não é snapshot recuperável dos bytes |
| P01-02 | [Classificação histórica](baseline/evidencias-historicas.json) e registro baseline | Em verificação: resultados separados e limites explicitados; os logs não vinculam toda árvore executada ao conteúdo atual |
| P01-03 | [Ficha do fluxo](contratos/registro.md) | Em verificação: organização prospect/pessoa/histórico/próxima ação escolhidos; jornada e adaptação para cinco etapas ainda sem demonstração |
| P01-04 | Mapa no registro contratos e [20 hashes selecionados](contratos/fontes-hashes.json) | Em verificação: mapeamento estático realizado; concordância runtime e riscos de cache não validados |
| P01-05 | [Matriz e limites](direitos/registro.md), [inventário](direitos/inventario.json) | Em verificação: autorização operacional reconhecida; direitos específicos de terceiros e licenças do pacote selecionado não encerrados |
| P01-06 | Este registro, fila abaixo e revisão integrada | Bloqueado para fechar G0 pela versão recuperável e reconciliação das provas anteriores |

Os estados de execução são registrados no backlog canônico; documentos de cenários/pacotes continuam catálogos de planejamento e não certificados de execução. As horas estimadas dos tickets não foram lançadas como horas reais. A atividade dos agentes não foi integralmente instrumentada: `horas_reais=0` mantém o contador anterior, não afirma ausência de esforço. Baseline mediu 174,514 segundos entre a criação do script e do registro, limite inferior de atividade, sem leituras anteriores e verificações posteriores. Esse valor parcial não permite totalizar horas-pessoa da rodada. Reserva não acionada.

## G0 e condições da próxima fase

G0 não aprovado. A baseline identifica conteúdo atual, mas não preserva uma versão recuperável sanitizada do recorte. Os resultados históricos de SQL/domínio/hardening continuam históricos; não certificam equivalência à árvore local nem ao futuro consumidor EBT. Onboarding continua pendente para G-SEG. A ausência de LICENSE em repositório privado não impede automaticamente código próprio; itens de terceiros sem permissão específica ficam fora do pacote comercial.

Não copiar diretamente o domínio Customer: fora de Testing ele exige proposta aceita ou exceção de gestor. O recorte proposto usa Prospect + Person/vínculo + CommercialInteraction, sem proposta/financeiro/OS. A fonte tem sete estados persistidos; cinco etapas ativas são uma proposta de adaptação, mantendo resultados terminais e IDs. Isso ainda não é comportamento implementado.

Lacunas para a implementação EBT: conferir cache da lista após conclusão/cancelamento na agenda; consulta de edição de interação sem prefixo tenant pode escapar da limpeza de sessão. São achados estáticos, sem exploração ou falha runtime demonstrada. Segurança, tenancy, contrato, schema e storage novos exigem N; extração/adaptação do fluxo exige R2.

## Fila concreta e continuidade

1. Salvar e revisar este recorte de evidência no repositório EBT, sem incluir `.codex/` ou conteúdo privado das fontes.
2. Fechar P01-01/P01-04/P01-05 com versão recuperável do recorte selecionado dentro do EBT, revisão de sanitização, direitos/origem por componente e seleção das dependências. Usar código próprio/autorizado; excluir materiais e identidades dos clientes. Nenhuma escrita nos projetos-fonte.
3. Reconciliar os cenários documentais P01 e registrar o G0 com o que pode ser copiado, adaptado ou apenas consultado. Não exigir G-SEG antecipadamente, mas não iniciar extração de recorte com falha relevante conhecida sem tratamento definido.
4. Somente com G0 aprovado, iniciar PAC-02: ADR .NET/React/SQL, estrutura/comandos, configuração própria e massa sintética A/B. G1 permanece aberto até a fase completar suas provas; não confundir SQL real com mock.

## Verificação e revisão

[Reconfirmação de hashes](verificacao_hashes.json): executada pelo coordenador sobre a baseline final, independente da coleta do agente. [Verificação dos contratos](contratos/verificacao.json): hashes do recorte recalculados pelo agente contratos. [Revisão independente](direitos/revisao_independente.md): agente direitos; referências de linhas inconsistentes foram corrigidas pelo agente contratos antes do fechamento.

Os comandos documentais `python scripts/verificar_plano.py` e `python scripts/verificar_organizacao.py --no-write` verificam orçamento, links, catálogo e hashes do planejamento. Não executam testes de aplicações. Seus resultados da rodada serão preservados em `verificacao_documental.json`. Testes de produto, SQL real, browser, homologação, aceite e deploy não foram realizados.

GitHub: commit/push e conferência remota são passos de salvamento da rodada; este registro não antecipa resultado remoto nem CI online.
