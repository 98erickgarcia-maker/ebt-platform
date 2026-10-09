# Roteiro de execução e continuidade

## Estado atual

O repositório contém planejamento finalizado e detalhado. Os 77 itens permanecem planejados no backlog; os estados ainda não foram reconciliados com os registros documentais P01-01 a P01-06 de 07/10/2026. Os módulos do produto ainda não foram implementados.

Ao retomar, consultar a [baseline de 07/10](PAC01_BASELINE_EBT_CONNECT_2026-10-07.md), os registros em evidencias/execucao/P01-01 a P01-06 e o [fechamento do G0](../../evidencias/execucao/P01-06/registro.md). O G0 documental libera a fundação PAC-02 condicionado ao CI documental verde do commit efetivamente mesclado. Ele não comprova runtime, segurança multiempresa ou produção.

Antes de alterar estados, reconciliar os critérios antigos com a fonte escolhida: P01-01 ainda exige a árvore local modificada/não rastreada, excluída da baseline remota; P01-04 inclui consumidor, cache e efeito após salvar, cuja prova depende da implementação. Preservar essas pendências e as horas reais sem preenchimento por inferência.

Quando a implementação da fundação estiver em escopo e a condição do G0 estiver verificada, seguir PAC-02A (estrutura), PAC-02B (Design System e shell) e PAC-02C (configuração e dados sintéticos). Não reiniciar PAC-01 por rotina; reabrir o gate apenas se mudar fonte, recorte ou condição relevante. Esta orientação atualiza a continuidade documental, sem executar módulos.

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

## Pacotes maiores, decisão 1.2

Para execução pelo Codex, acompanhar [17 pacotes](PACOTES_CODEX.md) e aplicar o [ciclo de revisão e continuidade](EXECUCAO_PELO_CODEX.md). Os mesmos 72 tickets continuam sendo checkpoints internos; as 180h incluem revisão/verificação/registro e a reserva permanece 20h. Consultar a baseline e os registros de 07/10 antes de continuar; o próximo pacote de implementação é PAC-02, respeitando as condições do G0 e o escopo autorizado.
