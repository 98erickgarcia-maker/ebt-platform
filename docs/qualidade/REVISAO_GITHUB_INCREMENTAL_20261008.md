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

## Próxima parte

Completar R03 (mudança de carteira de contato com canal) e a interface de inventário/revogação e convite para conta existente. Repetir negativas pertinentes e revisar o diff antes do checkpoint. Continuidade deve registrar os hashes efetivamente revisados, sem desligar seu controle para esconder a falha de CI.

## Limites

[Estado estruturado](../../evidencias/revisao_github_incremental_20261008.json). Gates e [pendências do produto](STATUS_IMPLEMENTACAO_CONNECT.md) permanecem separados. Scanner privado real, restore Azure isolado e aceite operacional requerem suas próprias provas. Sem deploy, migração Azure, envio real, merge em main ou transferência automática de sessão.
