# Revisão GitHub e incrementos seguros do Connect — 08/10/2026

A solicitação atual autoriza revisão e correções em partes verificadas. A base Enterprise completa, os produtos menores e o orçamento 180h + 20h permanecem. Não foram inferidas horas consumidas, homologação ou publicação.

## Atualizações observadas

- `main` permanece em `fdc3a9f`; não recebeu estas correções.
- [PR 12](https://github.com/98erickgarcia-maker/ebt-platform/pull/12), `7624584621600df806a81586321f98d313d1a91b`: limpa recursos na troca de contato e projeta nome/destinatário imutável da conversa. Build `37820262517` aprovado; continuidade `37820262448` falhou por hashes de revisão antigos em três arquivos.
- [PR 11](https://github.com/98erickgarcia-maker/ebt-platform/pull/11), `658bade690dc39d5245e00fa012280758661fdd1`: metadados/revogação de chaves e aceite autenticado de convite existente. Build `37719184165` aprovado; a interface não foi completada por esse PR.
- [PR 10](https://github.com/98erickgarcia-maker/ebt-platform/pull/10), `f345bacccc1266229be6ef564f8bbc580e526822`: coordenação documental da sequência; não implementa os módulos nem comprova trabalho de outra sessão.
- As linhas PAC usam `Ebt.Api`, distinto de `Ebt.Platform.Api`. O candidato do PR 9 tem alterações de scanner/cliente/CI, mas sua prova SQL/browser não foi concluída no run registrado. Não substituir os runtimes ou aprovar todos os candidatos por build verde.

## Parte 1 — integração do código revisado

Os commits de R01/R02 e do backend R04/R05 foram selecionados da mesma base `efba4e1` para uma branch isolada. A árvore original em `main` não foi substituída. Dois seletores dos testes remotos não correspondiam aos textos reais da UI; foram corrigidos. O login da fixture agora escolhe explicitamente tenant A, pois o aceite do convite adiciona uma segunda empresa ao operador. Isso evita que a ordem dos GUIDs determine o cenário.

Backend Debug e frontend compilados. SQL/HTTP executado em banco novo `EbtPlatformQa_Review20261008`, local, com senha/canais sintéticos exclusivos: 27/27 cenários aprovados. O teste não envia ao provedor. Os testes de browser foram ampliados para latência, erro HTTP, mais de 25 contatos, filtro e bloqueio de destinatário não identificado; resultado final registrado na evidência da revisão.

## Sequência planejada após a parte 1 (concluída abaixo)

Completar R03 (mudança de carteira de contato com canal) e a interface de inventário/revogação e convite para conta existente. Repetir negativas pertinentes e revisar o diff antes do checkpoint. Continuidade deve registrar os hashes efetivamente revisados, sem desligar seu controle para esconder a falha de CI.

## Limites

[Estado estruturado](../../evidencias/revisao_github_incremental_20261008.json). Gates e [pendências do produto](STATUS_IMPLEMENTACAO_CONNECT.md) permanecem separados. Scanner privado real, restore Azure isolado e aceite operacional requerem suas próprias provas. Sem deploy, migração Azure, envio real, merge em main ou transferência automática de sessão.

## Parte 2 — correções completas em QA

R03 agora recusa com 409 a transferência de carteira de contatos vinculados a conversa, preservando versão/histórico. O primeiro vínculo de canal compartilha o lock de contato com a edição; a negativa do worker permanece. Transferência de contato sem conversa continua permitida, com isolamento por carteira.

R04 inclui inventário de metadados e revogação na interface, sem consultar novamente o segredo; reload preserva o ID. R05 inclui entrar com conta existente a partir do link, aceitar autenticado, selecionar a nova empresa e impedir administração para leitor. Convites simultâneos do mesmo titular são serializados. O resultado tardio de resposta/paginação não altera rascunho/versão de outra conversa.

Verificação final desta parte: 27/27 SQL/HTTP, 7/7 cenários focados R02-R05, 16/16 browser sem casos ignorados, 17 verificações do protocolo e dez do proxy. Backend/frontend compilados. Uma execução intermediária dos roteiros concorrentes excedeu a quota compartilhada de autenticação; a fixture passou a controlar suas operações. O limite do produto não foi aumentado. Os testes antigos usam tenant explícito e guardam novas capturas em tmp, preservando as capturas históricas.

A parte 1 foi salva em `e34ad441bb7ad81b1ec641dae39d14dcd1935ede`: [build 37870433485](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37870433485) e [continuidade 37870433478](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37870433478) aprovados.

## Regressões reproduzidas antes da parte 3

A seleção de testes do PR 9 reproduziu seis falhas em sete casos no cliente atual: JSON tardio, troca de usuário com mesmo tenant/perfil, download após logout, destino externo de download, CSRF antigo e erro 401 de sessão anterior. O candidato será selecionado somente para este cliente e seus testes; nenhum runtime/scanner alternativo foi importado. As falhas foram encerradas nos cenários da parte 3 descrita abaixo.

## Parte 3 — proteção de sessão e downloads

Selecionado somente o cliente de `b57ab86f44da655f35a549a90c05bb60d175989c` e suas regressões; preservada a projeção de conversa R02 e todo o runtime Connect atual. A geração é conferida após ler JSON/blob/erro/CSRF; trocar o usuário no mesmo tenant/perfil também invalida chamadas antigas. Downloads exigem destino API na mesma origem e não clicam após logout. CSRF concorrente é compartilhado na geração correta; headers do chamador não são alterados.

Antes: seis falhas em sete regressões. Depois: 9/9 testes unitários (sete originais mais dois positivos), frontend build aprovado e 16/16 browser novamente aprovados sem ignorados. Auditoria npm de produção reportou zero vulnerabilidades conhecidas; isso não certifica toda a segurança do sistema. O workflow do produto passa a executar os unitários. SQL/browser continuam identificados como prova local.

A parte 2 foi salva em `e21fd82140a7af17868d1441985e7a86b78252e1`: [build 37872064452](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37872064452) e [continuidade 37872064449](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37872064449) aprovados. O último SHA deve ser confirmado no recibo e no GitHub após salvar esta parte.

[Preservação da origem](../../evidencias/fontes_originais_preservadas_20261008.json): 70 arquivos técnicos originais, HEAD e conteúdo de staging preservados; Git pode atualizar o cache de stat do índice ao consultar status. A integração usa `.worktrees/revisao-github-20261008` e a branch `codex/ebt-enterprise-continuity-reviewed-20261008`; não substitui a árvore original ou produção.

## Resultado e sequência segura

R01–R05 receberam correções e provas nos cenários descritos. Nenhum erro foi detectado na rodada final desses cenários. Isso não demonstra perfeição da Enterprise completa, scanner privado real, restore Azure isolado, aceite de usuário, Meta direto ou canais adicionais. Manter 180h + 20h, sem horas reais fictícias.

Próximo recorte: conferir a versão final, fechar scanner privado com prova por versão, ensaiar restore em destino Azure isolado com hashes e obter aceite operacional. Preparar cada recorte com seus critérios/rollback e autorização vigente; não extrair todo o Core ou iniciar novos módulos por inferência. A família Enterprise e seus produtos permanecem íntegros.

O checkpoint passou 16/16 testes. JavaScript (.js/.mjs/.cjs) usa revisão UTF-8 e hashes canônicos, mantendo recusa de segredos, NUL e UTF-8 inválido.

Nova atualização concorrente: `codex/ebt-enterprise-continuity-pac-review-20261008`, SHA `f8b00fde`. CI de build passou, mas o job QA falhou em confirmar a versão do ClamAV real (run 37872942384). Não foi incorporada a homologação de scanner ou restore dessa branch. O protocolo do scanner e a guarda de liberação são avaliados separadamente a partir de `cf206647`.

## Parte 4 — scanner e liberação de documentos

A regressão reproduziu `stream: OK` sem terminador como aprovação indevida. A correção exige terminador NUL e resposta completa; resposta incompleta/erro indisponibiliza a liberação, detecção de malware retorna bloqueio. O cancelamento da requisição alcança o scanner. Aprovação e download verificam o estado de scan: produção requer `clean`; Development permite apenas `clean`/`not_scanned`, nunca `infected`/`error`.

Selecionados CommercialScanner, DocumentSafety e DocumentEndpoints de `cf206647`; o teste de protocolo foi ampliado para conferir código/status de erro. Não foram importados o workflow de SQL/ClamAV real ou o restore do candidato concorrente. Provas: 10/10 cenários TCP/guarda simulados, backend Debug/Release sem erros/avisos, 27/27 SQL/HTTP repetidos na versão corrigida. O CI passa a executar os dez cenários do scanner. Scanner real privado e restauração Azure continuam pendentes.

A parte 3 foi salva em `9aeed36f558c435509d4256d20d1ac19612f32f7`, com [build aprovado](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37873167479) e [continuidade aprovada](https://github.com/98erickgarcia-maker/ebt-platform/actions/runs/37873167432). Conferir o último SHA no recibo e remoto após a parte 4.
