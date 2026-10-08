# Sincronização da sequência EBT Enterprise

Consulta em 08/10/2026, UTC. Este registro coordena as linhas acessíveis no GitHub e prepara trabalho paralelo. O chat `01a1190a-c397-7422-9b3e-0b8943be5038` não pôde ser lido: `read_thread` não está disponível nesta sessão. Não há confirmação de comunicação direta com a outra sessão nem de seu trabalho ainda não publicado.

## Base comum observada

Repositório: [98erickgarcia-maker/ebt-platform](https://github.com/98erickgarcia-maker/ebt-platform). Base desta coordenação: `codex/ebt-enterprise-continuity-20261007`, SHA `efba4e1f1df422d0d0b394f3c00b360624ce245b`, confirmado com `git ls-remote`. Essa é a base publicada de continuidade encontrada nesta consulta; o proprietário da sessão original deve conferir alterações posteriores antes de integrar.

No mesmo SHA, [build 37712661852](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37712661852) e [continuidade 37712661809](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37712661809) terminaram com `success`. São provas de CI daquela versão. A publicação Connect 0.1.5 e o texto real WazVox são registros históricos, sem nova execução ao vivo neste trabalho.

Usar [estado de continuidade](../../planejamento/estado_continuidade.json), [estado do Connect](../qualidade/STATUS_IMPLEMENTACAO_CONNECT.md) e [revisão funcional](../qualidade/REVISAO_PROMPTSPELLSMITH_CONNECT_20261007.md). O backlog de 75 tickets e 238 cenários permanece baseline de planejamento. Orçamento: 180h de entregas + 20h de reserva; horas reais não foram inferidas.

## Reconciliação das linhas

| Linha | Estado observado | Decisão para acelerar |
|---|---|---|
| `main`, `fdc3a9f` | Baseline G0; não contém o runtime mais recente | Retomar o Connect pelo checkpoint publicado, conferindo o SHA |
| [#2](https://github.com/98erickgarcia-maker/ebt-platform/pull/2) → [#3](https://github.com/98erickgarcia-maker/ebt-platform/pull/3) → [#6](https://github.com/98erickgarcia-maker/ebt-platform/pull/6) → [#7](https://github.com/98erickgarcia-maker/ebt-platform/pull/7) | PRs draft empilhados, runtime sintético `Ebt.Api` distinto de `Ebt.Platform.Api` | Aproveitar contratos/provas pertinentes após comparar; evitar reimplementar a fundação integral no Connect |
| [#8](https://github.com/98erickgarcia-maker/ebt-platform/pull/8) | Plano PAC-07; quatro tarefas/12 casos planejados | Reconciliar com sessão, CSRF, auditoria e convite já presentes no Connect; não iniciar pela numeração PAC |
| [#9](https://github.com/98erickgarcia-maker/ebt-platform/pull/9), `b57ab86` | Snapshot alternativo com candidatos de cliente/scanner/CI | Selecionar mudanças por contrato/cenário; não substituir a árvore de continuidade pelo snapshot |
| [#5](https://github.com/98erickgarcia-maker/ebt-platform/pull/5) | Pacote Emergent isolado, stack e finalidade próprias | Manter a integração fora da sequência atual até existir recorte pertinente |

A comparação das árvores do #9 e da base atual apresenta 83 arquivos diferentes, incluindo ausência dos scripts/documentos/testes de continuidade e de assets/Brand/navegação no snapshot #9. Preservar esses caminhos durante a reconciliação. Isso é comparação de snapshots, não uma previsão de exclusões por um merge Git.

O [CI 37709330415 do #9](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37709330415) tem build aprovado e job QA reprovado na etapa `Private loopback ClamAV fixture`; SQL/browser posteriores foram ignorados. Portanto, não usar esse run como prova completa de scanner/SQL/browser.

## Ordem de integração

1. Conferir a base remota e comparar os candidatos de #9; registrar origem, caminhos, cenário e SHA aceito.
2. Corrigir e provar R01/R02 antes do aceite operacional: ações de recursos A não podem aparecer sob contato B, inclusive com latência/erro; conversa precisa identificar o destinatário com filtros, paginação e mais de 25 contatos.
3. Tratar R03–R05 com contratos e negativas: carteira/canal, revogação operável de chaves e convite para conta existente.
4. Validar a versão integrada; fechar as provas próprias de scanner privado, restauração Azure isolada com hashes e aceite do recorte.
5. Após estabilizar o piloto, escolher segundo consumidor e extrair apenas capacidades comprovadamente duplicadas. Site/Flow e demais produtos conservam seus recortes e gates.

R01/R02 continuam abertos na base observada. As mudanças de #9 em `api.ts` protegem gerações antigas de sessão/tenant; não resolvem, por si, a troca entre contatos no mesmo contexto. `openContact` e a identificação baseada em `contacts.find(...)` ainda precisam de correção/prova específica. Nenhum achado foi fechado por este documento.

## Frentes paralelas propostas

As frentes abaixo estão planejadas. Não representam agentes de produto em execução ou disponibilidade da outra sessão.

| Frente | Responsabilidade exclusiva | Passagem e condição de integração |
|---|---|---|
| Integração | Base/SHA, comparação de #9, documentos e checkpoint | Receber incrementos pequenos; único escritor do estado compartilhado |
| Interface R01/R02 | `App.tsx` e jornadas de contato/conversa | Um único dono do arquivo; provar latência, erro, paginação/filtros e ausência de ações A sob B |
| Conversa/carteira R02/R03 | `MessagingEndpoints.cs`, `CrmEndpoints.cs`, worker e DTO | Combinar contrato de identificação com interface antes de editar `api.ts`; preservar negativas de tenant/carteira |
| Administração R04/R05 | `Security.cs` e contratos de chave/convite | Um único dono do arquivo; UI integrada depois pelo dono de `App.tsx`; não expor segredos |
| Scanner/recuperação | Candidatos `CommercialScanner.cs`, `DocumentSafety.cs`, `DocumentEndpoints.cs`; roteiro de restore | Revisão/provas isoladas; acesso privado/Azure e eventual publicação dependem do escopo vigente |
| CI/evidência | Workflow e fixtures SQL/ClamAV/Chromium | Reparar a fixture de #9 antes de usá-la; registrar exatamente os cenários executados/ignorados por SHA |

Testes/revisões e preparação de contratos podem avançar em paralelo. Arquivos compartilhados, migrations e estado de continuidade recebem um único integrador. Se uma frente depender de credenciais ou aceite, continuar as independentes. A velocidade deve ser medida por incrementos integrados e provas concluídas; não há ganho numérico medido nesta revisão.

## Checkpoint e passagem para a sessão original

Esta coordenação é publicada em `codex/ebt-enterprise-continuity-sync-20261008`, com base fixada em `efba4e1`, por [configuração isolada](../../planejamento/checkpoint_sincronizacao_20261008.json). O destino padrão em `continuidade_github.json` permanece a branch original. O script usa a branch do config, não a do checkout; nunca executar o config padrão para publicar trabalho desta branch isolada.

Após revisar os bytes e os validadores, publicar a coordenação:

```sh
python scripts/checkpoint_github.py --config planejamento/checkpoint_sincronizacao_20261008.json --approve --push
```

O SHA confirmado no recibo e no remoto prova salvamento. O checkpoint gera seu próprio `continuidade/CHECKPOINT.json`; na integração, regenerar esse manifesto para a branch de destino, preservando contribuições concorrentes. Não copiar cegamente o manifesto da coordenação. O [estado estruturado desta revisão](../../planejamento/sincronizacao_sequencia_20261008.json) registra fontes, limites e frentes.

Passagem reproduzível: ler este documento/JSON pelo GitHub, comparar a branch original com o SHA observado, reservar os arquivos de cada frente, executar um incremento autorizado e devolver commit + cenário + resultado + pendência. Validar a superfície afetada uma vez; repetir após nova mudança, falha ou dúvida relevante. Salvar cada incremento revisado com confirmação remota. Não há transferência automática entre chats, alteração de módulos, merge, deploy, consumo medido de horas ou promoção de gates nesta entrega.
