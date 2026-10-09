# Revisão geral de PRs e sequência de conclusão — 09/10/2026

## Escopo e resultado observado

Inventário inicial: **27 PRs abertos em cinco repositórios** de `98erickgarcia-maker`. Foram lidos metadados, bases e descrições, consultados workflows de evento pull_request no SHA indicado e aprofundados diffs/logs relevantes. Não foi feita revisão linha a linha de todos os arquivos de todos os produtos; revisão geral, testes focalizados e aceite operacional são etapas diferentes.

Resultado das consultas de CI: **19 com os checks retornados em sucesso; 6 com ao menos uma falha; 2 sem execução de PR retornada**. Alguns sucessos são apenas validação documental. O conector consulta a primeira página de workflows de pull_request; ausência nessa consulta não prova ausência de push, dispatch, check-runs ou verificações externas. Os SHAs abaixo delimitam a observação; qualquer atualização exige nova consulta.

Nenhum merge, deploy, alteração de credenciais, migração, envio real, instalação ou reinício de VPS foi realizado. As marcas e bases EBT, CASST, Vikings e Nutrição continuam separadas. Esta fila não amplia silenciosamente o orçamento/escopo de 180h de entregáveis +20h de reserva registrado no planejamento anterior.

## Inventário inicial completo

Os números são relativos ao repositório de cada grupo. `Verde observado` NÃO significa pronto para integrar ou publicado.

| Repositório | PR | SHA observado | CI | Diagnóstico e próxima ação |
|---|---:|---|---|---|
| ebt-platform | 2 | f015259976a42ceee68bf8cbedf74dc2074aaa87 | Verde observado | PAC02. Preservar dependência da fundação PAC01. |
| ebt-platform | 3 | 332a04761459a4eb658efec99916d53521366f0c | Verde observado | PAC03 SQL/Azurite QA; depende do #2. |
| ebt-platform | 5 | e8e310277f1e9b40827d7344756f84fd5a199714 | Verde observado | Pacote Emergent isolado; não incorporar como se fosse runtime .NET nativo. |
| ebt-platform | 6 | e84ad5e8def9b8b3001475cda6fcf73610a17804 | Verde observado | PAC05 identidade/tenant; base #3. |
| ebt-platform | 7 | 900cac70c3e9323e50d61ef0aa3c7d75b0ca9112 | Verde observado | PAC06 RLS/SQL; base #6. |
| ebt-platform | 8 | 044e8a536686088206193a1c9907be7dd6458ba8 | Verde documental | Planejamento PAC07, base #7; não confundir com funcionalidades concluídas. |
| ebt-platform | 9 | b57ab86f44da655f35a549a90c05bb60d175989c | FALHA | Build EBT Connect: run37709330415. Mapear a consolidação antes de corrigir/integrar. |
| ebt-platform | 10 | f345bacccc1266229be6ef564f8bbc580e526822 | Verde observado | Guia anterior de seis frentes; conciliar com #21 e issue14. |
| ebt-platform | 11 | 658bade690dc39d5245e00fa012280758661fdd1 | FALHA | Continuidade: run37719184150. Verificar inclusão de R04/R05 no #13. |
| ebt-platform | 12 | 7624584621600df806a81586321f98d313d1a91b | FALHA | Continuidade: run37820262448. Verificar inclusão de R01/R02 no #13. |
| ebt-platform | 13 | e366dde04598bdee7e072e61ab4713cfd9738162 | Verde observado | Consolidação R01–R05; comparar diffs, não integrar duplicado. |
| ebt-platform | 15 | 2ff1007060f60622a53335c712575cbe3903649f | Verde observado | Navegação responsiva; revisão visual independente ainda necessária. |
| ebt-platform | 16 | 9b5c546b80151901850875c3a91f9ecb8a87daea | Verde observado | GraphMail rejeita token inválido; homologação de caixa real não comprovada. |
| ebt-platform | 20 | 18becc351bb945c27aa61444088d0b6dfbf0d7fd | Verde observado | Rastreio do Production Watch; CI do PR não demonstra recorrência do cron. |
| ebt-platform | 21 | 1e3039179f5ede8d61e5b37c23cf6c0f9d8cb046 | Verde documental | Coordenação em três frentes, não três agentes autônomos comprovados. |
| ebt-platform | 22 | 3051bb6c15910bc0cebf8bb6ed3c25c3e65a1b96 | Verde observado | FLOW+AURA Meu dia/Contato360; depende do #15. |
| app-mail | 1 | 3b6536f7df76e382d11bcffb735e6e9e5dbb9030 | Sem run retornado | Verificar CI e sobreposição das proteções de envio antes de consolidar. |
| app-mail | 2 | 294f43efffcfded8cb87c6a66c8d54b124a4bffc | FALHA | Run37897003343: duas falhas de pontuação e frontend sem yarn.lock. |
| app-mail | 3 | 2e31d59ea104e9e697536cdec40494e1fbc46681 | Sem run retornado | Remetente protegido V4; não habilitar um segundo remetente. |
| app-mail | 4 | af3dd94e9149609403cdbd8c49e05ce4fa77e22f | Verde observado | Coleta de 284 contatos históricos; não significa 2.000 coletados ou contatos habilitados a envio. |
| grupo-vikings-sst | 13 | 8770baab2c176d141fd53b4c8471e8e9434e9d40 | FALHA | Run37448450203. Conferir se a fundação foi superada pelas consolidações, sem fechamento automático. |
| grupo-vikings-sst | 70 | ea1d3ac0daa173e99d502ba55c548b39d519df8a | Verde observado | O texto RED está desatualizado em relação ao CI observado; não inferir homologação de fornecedor. |
| grupo-vikings-sst | 71 | 67f74b18572d16bbd83716454c224505e6ed5030 | Verde observado | V19 persistente; comparar inclusão no #73. |
| grupo-vikings-sst | 72 | d99988ed3d7e21257e414fc91d7275a9c7b0bfe4 | Verde observado | V20 operacional; descrição RED não corresponde ao CI observado. |
| grupo-vikings-sst | 73 | 35b53ef92fd5965bfb07ca969fa5c801ee8fe9bf | Verde observado | Candidato consolidado; aceite V25 e integrações externas ainda separados. |
| site-nutricao | 1 | 9f82f8a5d2b2d91021e1f755bfffe5615f9ac980 | Verde observado | Rotina CRM/Outlook; proteção de troca de conta durante preparo ainda não incorporada. |
| crm-casst-web | 1 | b7aaab9dce95571b3125670f49c64935a595236d | FALHA | Verify foundation run37420497527; diagnóstico da causa deve preceder nova alteração. |

Para localizar cada evidência: `https://github.com/98erickgarcia-maker/REPOSITORIO/pull/NUMERO` e `.../actions/runs/ID`. O inventário é um snapshot, não uma transação global entre os cinco projetos.

## Mudanças concretas desta rodada

### EBT Platform #23 — auditor de PRs

Branch `feat/pr-audit-readonly-20261009`, candidato `18d9d45900cf577185768e717a949c4abd887b8a`.

Coleta somente leitura, comparação por SHA, última tentativa de workflow, revisões independentes, paginação limitada, detecção de snapshot alterado, proteção de logs e gravação atômica. Testes: 29 na primeira rodada; após revisão de qualidade, 31 na segunda, incluindo 1.000 cenários sintéticos determinísticos. CI remota: EBT PR Audit run37972298919 e planejamento run37972298453, ambos sucesso.

Não são 1.000 revisões integrais de produtos. O cliente HTTP local não teve rede; as observações reais vieram do conector. O PR permanece draft; coleta manual em Actions depende da integração autorizada na main. Guia: docs/operacao/AUDITOR_PRS_20261009.md na branch do PR23.

### app-mail #5 — correção de pontuação

Branch `fix/opportunity-priority-ceilings-20261009`, candidato `6cf99babeb0171659dbd312b1e6daa58fa02443b`, empilhado sobre #2.

Reproduzidas duas falhas nos nove testes originais. O bônus por domínio próprio elevava reclamação de B para A e comentário de C para B. A correção limita o score desses sinais, mantendo pedidos explícitos, revisão manual e proibição de envio automático. Doze testes focais passaram em duas rodadas locais; bytes conferidos com os blobs remotos.

CI run37972475022: **business_rules PASS**, job113962332311. **frontend_build FAIL**, job113962331998, ainda antes da instalação/build. A árvore da base não tem lockfile e o workflow exige frontend/yarn.lock. A correção deste bloqueio está em Q03; não removemos verificações nem fabricamos dependências para simular sucesso.

## Sequência programada

A fonte legível por máquina é `planejamento/fila_prs_20261009.json`, nesta branch até integração. São 14 pacotes: dois incrementos já implementados e 12 de continuidade, revisão ou homologação. Um pacote pode resultar em mais de um PR pequeno; não abrir PRs vazios só para aumentar a contagem.

**Primeira prioridade:** Q03 lockfile/build real do app-mail, Q04 base canônica EBT, Q10 causa do CI CASST e Q07 comprovação de recorrência do monitor. Esses recortes são independentes quando não disputam arquivos. Um executor mantém uma implementação por vez; no máximo duas novas implementações simultâneas, com branches próprias.

**Revisões de funcionalidades existentes:** Q05 conclui avaliação de #15/#22; Q06 revisa #16; Q08 consolida o app-mail com um único remetente; Q09 verifica o candidato Vikings #73 contra propostas antigas; Q12 protege a troca de conta no CRM da Nutrição. Trabalhar sobre os PRs já existentes quando o recorte já estiver implementado.

**Aprimoramentos posteriores:** Q11 separa correções restantes CASST; Q13 extrai componentes pequenos e estende o padrão visual EBT somente após a base e as telas anteriores serem validadas. Não iniciar outro redesenho amplo que sobreponha #22.

**Conclusão:** Q14 prepara um candidato de release por produto, com versão, gates aplicáveis, evidências, riscos, rollback, responsável e go/no-go. Um produto pode alcançar seus próprios gates sem esperar outro repositório; a conclusão do portfólio exige todos os escopos aplicáveis. Fornecedor, identidade real, scanner/restauração Azure, VPS e aceite operacional ausentes são bloqueios explícitos, não testes fictícios.

## Protocolo de execução e revisão

Antes de escrever, ler instruções do repositório, issue14, fila, PR atual, SHA e trabalhos paralelos. Comentário em issue não é lock transacional. Reservar recorte sem sobreposição e rever a base remota antes de publicar. Se a base mudou, recalcular o diff e invalidar aprovações antigas.

Cada entrega registra tarefa, base, candidato, arquivos, defeito reproduzido, testes e resultados PASS/FAIL/BLOCKED, revisão funcional, revisão de segurança/regressão, limitações e próximo passo. CI verde, revisão aprovada, homologação e publicação são estados distintos. Não atualizar hashes de continuidade cegamente; demonstrar o conteúdo realmente revisado.

Repetição útil significa variar riscos/cenários e corrigir defeitos. Duas tentativas idênticas que falham exigem diagnóstico, não mais 998 reexecuções iguais. Ausência de defeito encontrado não é prova de perfeição. Falta de ambiente interrompe aquele recorte, mas permite avançar em outro independente.

A tarefa nativa de engenharia deve ser atualizada, não duplicada, para consultar esta fila a cada execução horária, verificar o estado atual e executar no máximo um incremento autorizado. Não declarar execução contínua na VPS ou três agentes autônomos sem evidência. O Production Watch, separado, possui cron; a consulta observou apenas um schedule bem-sucedido em main, run37962877132, criado em 09/10/2026 16:57:56Z. Uma ocorrência não demonstra recorrência confiável.
