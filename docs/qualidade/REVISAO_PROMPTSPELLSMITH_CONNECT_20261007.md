# Revisão EBT Connect com PromptSpellSmith Master

07/10/2026. Revisão do produto implementado, usando os módulos EBT, GitHub e frontend/backend da skill, com inspeção de código, build e reproduções em SQL/HTTP/browser local. Resultado: **dois achados de prioridade alta e três de prioridade média**. Os dois primeiros devem ser corrigidos antes do aceite operacional: permitem agir sob contexto visual incorreto ou sem identificar o destinatário.

O código-fonte foi preservado. Foram acrescentados somente este relatório e artefatos de revisão; os builds atualizaram seus arquivos gerados. O banco local exclusivo de QA recebeu registros sintéticos para reprodução. Não houve alteração em Azure, credenciais de produção, módulos-fonte, orçamento ou estados dos gates; nenhum envio real foi realizado.

## Base e limite da evidência

- Regras consultadas: `AGENTS.md`, `docs/REVISAO_BASES.md` e `docs/VALIDACAO_E_GATES.md`.
- Árvore local de trabalho sobre HEAD `4c185f761b2b5e212800464f4b450167a26c1b88`. Esse commit contém o planejamento e não representa sozinho o runtime: `src/`, `tests/`, `sql/`, `deployment/` e o workflow do produto estavam sem rastreamento no início da revisão. Alterações preexistentes foram preservadas.
- Os 67 arquivos técnicos listados no manifesto local `0.1.5-live` tiveram hashes conferidos e correspondem aos arquivos atuais. A comparação de início/fim da revisão confirmou 68 arquivos-fonte preservados.
- Runtime revisado: build Release atual, `Development`, `http://127.0.0.1:5191`, SQL local `EbtPlatformQa_20261007Migrated`. A interface foi reconstruída do código atual. A instância temporária foi encerrada ao final.
- Os registros de 26 verificações online da versão 0.1.3 e de dez verificações reais WazVox da 0.1.5 são históricos. Não foram contabilizados como novas verificações de produção nesta revisão.
- Mantidos **180h de entregas + 20h de reserva**. Estimativas não foram convertidas em horas consumidas. Os 238 cenários documentais continuam distintos dos testes executados.

[Resumo verificável](../../evidencias/revisao_promptspellsmith_20261007/resumo_validacao.json), [reproduções](../../evidencias/revisao_promptspellsmith_20261007/review_checks.json) e [hashes das fontes](../../evidencias/revisao_promptspellsmith_20261007/fontes_preservadas.json).

## Achados priorizados

### R01 — Alto / P1: recursos de outros contatos continuam acionáveis durante a troca

**Local:** `src/frontend/src/App.tsx:569–576`, com ações em `795–825` e renderização em `1446–1459`.

`openContact` troca o cabeçalho e o contato selecionado sem limpar tarefas, documentos, notas ou a lista de conversas. As ações dessas listas continuam habilitadas enquanto a nova consulta está em andamento. Ao voltar à lista, o carregamento global também pode alimentar esses estados antes da abertura do próximo contato. Se a consulta seguinte falhar, os recursos antigos podem permanecer sob o novo cabeçalho.

**Reprodução:** criados contatos A/B e uma tarefa exclusiva de A. Retardada somente a consulta de tarefas de B, abriu-se B e apareceu a tarefa de A com o botão **Encerrar** habilitado. A tarefa de A foi efetivamente encerrada pelo formulário enquanto a tela identificava B. O backend autorizou a operação sobre A; a falha é a associação visual incorreta, não uma prova de acesso entre tenants.

**Correção:** limpar ou vincular os recursos ao ID selecionado antes de exibi-los; publicar o detalhe e seus recursos como um conjunto coerente; impedir ações até o carregamento do contexto correspondente. Manter esse cuidado também no erro de carregamento. Acrescentar regressão com resposta retardada e falha HTTP.

[Captura da reprodução](../../evidencias/revisao_promptspellsmith_20261007/contato-b-tarefa-a.png).

### R02 — Alto / P1: conversas podem permitir resposta sem identificar o destinatário

**Local:** `src/frontend/src/App.tsx:1617–1620` e `1637–1641`; projeção da API em `src/backend/Ebt.Platform.Api/MessagingEndpoints.cs:24–26`.

A identificação usa `contacts.find(...)`, mas `contacts` contém somente a página de 25 registros com os filtros da área de relacionamentos. A consulta de conversas retorna outro conjunto de até 100 itens e fornece apenas `contactId`, sem nome ou destinatário. Contatos fora da página/filtro aparecem como **Contato vinculado**, e o painel mostra **Conversa**, sem telefone.

**Reprodução:** filtrou-se a lista pelo nome de A e abriu-se Conversas. Dezessete itens ficaram sem identificação, inclusive B. Após carregar as mensagens de uma dessas conversas, o painel continuou sem identificar a pessoa. Ao escrever um rascunho sintético, **Confirmar resposta** ficou habilitado. Não foi acionado envio.

**Correção:** retornar a identificação autorizada do contato no contrato da conversa, com referência clara ao destinatário; renderizar essa informação independentemente do cache paginado de contatos. Bloquear confirmação quando o destinatário não estiver identificado. Testar filtros, mudança de página e mais de 25 contatos.

[Captura com mensagens carregadas e confirmação habilitada](../../evidencias/revisao_promptspellsmith_20261007/conversas-sem-identificacao.png).

### R03 — Médio / P2: transferência de carteira interrompe a conversa do canal

**Local:** `src/backend/Ebt.Platform.Api/CrmEndpoints.cs:89–94`; processamento em `src/backend/Ebt.Platform.Api/ConnectWorker.cs:118–121`.

O administrador pode alterar a carteira de um contato já ligado a um canal, sem reconciliar ou impedir o vínculo existente. A conversa permanece apontando para o canal da carteira anterior. As próximas entradas são recusadas pelo worker com `channel_portfolio_changed`; não há operação pública para transferir a conversa ou tratar essa quarentena.

**Reprodução:** uma conversa sintética estava funcionando. A transferência do contato de `principal` para `outra` foi aceita. O próximo webhook recebeu ACK 200, mas a mensagem não apareceu na conversa. Consulta SQL local confirmou um envelope recente em quarentena com esse diagnóstico. O envelope foi preservado; a mensagem ficou indisponível no fluxo normal de atendimento.

**Correção:** enquanto não existir transferência segura, bloquear a mudança incompatível com um erro 409 explicativo. Para suportar transferência, definir vínculo do canal, responsável, permissões, conversa e tratamento da quarentena em uma operação consistente. Não remover a negativa do worker: ela protege o isolamento.

### R04 — Médio / P2: a interface perde a referência necessária para revogar chaves

**Local:** `src/frontend/src/App.tsx:1857–1861`; endpoints em `src/backend/Ebt.Platform.Api/Security.cs:171–181`.

A criação retorna ID, validade e token, mas a interface guarda somente o token. A API permite revogar pelo ID, porém não possui listagem de chaves emitidas e a interface não oferece revogação. Após sair da tela/sessão, o administrador não consegue localizar e revogar uma chave antiga pelo fluxo do produto.

**Reprodução:** criada uma chave sintética; `GET /api/admin/api-keys` retornou 405. A revogação por ID funciona e foi usada para invalidar a chave desta revisão. Portanto, o mecanismo de revogação existe, mas falta torná-lo utilizável para chaves anteriores.

**Correção:** listar somente metadados autorizados — ID, nome, titular, validade e estado — e oferecer revogação por empresa. Nunca listar novamente o segredo nem o hash. Testar revogação, expiração, tenant B e perda de permissão do titular.

### R05 — Médio / P2: convite para conta existente não tem caminho de vinculação

**Local:** `src/backend/Ebt.Platform.Api/Security.cs:144–166`.

O administrador consegue preparar um convite para um e-mail existente em outra empresa. A ativação retorna 409 `existing_user` e manda o administrador vincular a conta, mas os endpoints de equipe só listam e alteram vínculos já existentes. Não há fluxo autenticado de aceitação/vinculação desse convite.

**Reprodução:** a empresa B preparou um convite para uma conta sintética existente apenas em A. A ativação falhou com 409 `existing_user`. Não houve envio de e-mail, redefinição de senha ou novo vínculo.

**Correção:** permitir que o titular autenticado aceite um convite válido e receba somente o vínculo autorizado. Preservar a senha e exigir correspondência entre conta e convite. Se isso ficar fora do recorte imediato, recusar a preparação desse convite e documentar um procedimento administrativo real. Testar pessoa errada, convite expirado/repetido e acesso A/B.

## Coerência entre backend e interface

| Capacidade | Backend atual | Interface atual | Conclusão da revisão |
|---|---|---|---|
| Identidade, perfis e empresa | Cookie/CSRF, sessão revogável e revalidação de vínculos | Login, seletor de empresa e ações por perfil | Preservar; duas negativas específicas passaram nesta rodada |
| Contato e organização | ID, etapa, carteira, responsável, concorrência e idempotência | Lista e detalhe contextual | Corrigir a associação dos recursos ao contato antes de expandir telas |
| Tarefas e próxima ação | Prazo/resultado e próxima ação derivada | Meu dia, tarefas e detalhe | Preservar regra derivada; corrigir R01 |
| Importação | Preview e confirmação atômica delimitada | CSV com revisão prévia | Código inspecionado; suíte completa não reexecutada |
| Comunicação | Envelope durável/cifrado, deduplicação, outbox e estado incerto | Conversa com confirmação humana e consulta periódica | Corrigir identidade do destinatário e transferência de carteira |
| Documentos | Versões, hash, revisão, quota e bloqueio de aprovação sem scan em produção | Upload, versões, revisão e download | Scanner real e recuperação Azure continuam pendências de gate |
| Chaves e equipe | Criação/revogação e edição de vínculos | Preparação de chave/convite | Completar os caminhos operacionais R04/R05 |

## Direção de produto e arquitetura

A identidade EBT, a hierarquia visual, os ícones e o shell são coerentes. Na viewport de 390 × 844, Conversas não apresentou rolagem horizontal. Esses resultados não aprovam todas as telas, estados, acessibilidade ou uso operacional.

O **detalhe do relacionamento** é o candidato mais útil a módulo de referência: reúne cadastro, histórico, próxima ação, tarefas, conversa e documento. Deve primeiro passar pelos estados de carregamento, erro, conflito e troca de contexto; depois seus componentes podem orientar as demais telas.

`App.tsx` concentra aproximadamente 79 KB de navegação, carregamento, formulários e ações. A melhoria recomendada é dividir gradualmente por jornadas e associar cada conjunto de dados ao contexto que o produziu. Isso ajuda a corrigir R01/R02 sem trocar a identidade ou recomeçar a aplicação.

Preservar IDs, contratos, filtros de tenant/carteira, schema `ebt_connect`, histórico, versões, idempotência, retenção e política de resultado incerto. Evitar extração ampla de Core, novo storage, novos canais, campanhas ou builders neste ajuste. Mudança de contrato, segurança ou vínculo de canal exige os cenários afetados da trilha N/R2; não recebe R1 por herdar código testado.

## Sequência sugerida e aceite das correções

1. **R01:** contexto do contato e bloqueio de ações; demonstrar que A nunca é acionado sob B, inclusive com latência e erro.
2. **R02:** identificação própria na conversa; demonstrar nome/destinatário corretos após filtro, paginação e mais de 25 contatos, sem liberar dados de outra carteira.
3. **R03:** impedir transferência incompatível ou implementar transferência explícita; comprovar recebimento, histórico e negativa A/B depois da mudança.
4. **R04/R05:** completar revogação e aceite de convite existente; testar perfil, tenant, expiração e repetição.
5. **Fechamento do recorte:** executar a regressão integrada pertinente uma vez, registrar versão/hash e rever apenas os gates dependentes. Preservar o orçamento 180h + 20h; registrar eventual consumo real e ajustar prioridades conforme os critérios existentes.

Continuam pendentes de prova própria: CI hospedada do runtime, restore em Azure, scanner privado real e aceite do usuário. Arquivos do runtime e seu workflow precisam estar versionados antes de depender de clone/CI para reproduzir a publicação. O filtro de tarefas usa o rótulo **Antes de** e limite exclusivo; essa semântica foi conferida no código e não foi classificada como defeito.

## Verificações executadas nesta rodada

| Verificação | Resultado observado |
|---|---|
| `dotnet build src/backend/Ebt.Platform.Api/Ebt.Platform.Api.csproj --no-restore -c Release` | Aprovado: zero avisos e zero erros |
| `npm run build`, em `src/frontend` | TypeScript e build Vite aprovados |
| Testes de protocolo WazVox, Release, adapters simulados | 17 verificações aprovadas; sem envio ao provedor |
| Testes de proxy, Release, `--proxy` | Dez verificações aprovadas |
| `python scripts/verificar_organizacao.py --no-write` | Aprovado: 180h + 20h, 75 tickets e 238 cenários documentais não executados |
| `npm audit --omit=dev --json` | Zero vulnerabilidades reportadas nas dependências de produção; não cobre dependências de desenvolvimento nem toda a segurança da aplicação |
| Revisão focada SQL/HTTP/browser | Cinco controles positivos aprovados e cinco achados reproduzidos |
| SQL local após transferência | Confirmada quarentena recente `channel_portfolio_changed` |
| Manifesto `0.1.5-live` | 67 hashes técnicos conferidos, sem divergência |
| Comparação das fontes no início/fim | 68 arquivos preservados, sem adição ou alteração nesses diretórios |

Os cinco controles positivos foram: fixture/recebimento durável A/B, negativa de leitura por ID do tenant A em B, negativa de criação por leitor, ausência de overflow horizontal no mobile de Conversas e health SQL do runtime revisado. Essa cobertura não substitui a suíte completa SQL/HTTP, os quatro testes originais de browser ou a homologação real.

Os scripts de reprodução e capturas estão em `evidencias/revisao_promptspellsmith_20261007/`. Uma primeira execução do roteiro encontrou erro na liberação da interceptação de rede do próprio teste; o roteiro foi corrigido e executado integralmente novamente. Esse erro não foi atribuído ao produto.
