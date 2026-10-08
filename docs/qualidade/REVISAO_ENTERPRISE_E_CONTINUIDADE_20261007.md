# Revisão de coerência EBT Enterprise e continuidade

07/10/2026. Aplicada a skill PromptSpellSmith Master nos modos audit/project/agent, com módulos EBT, GitHub, frontend/backend e automações. Resultado: **a direção original é coerente; os documentos, a versão de trabalho e os limites de prova precisavam de reconciliação. A Enterprise inteira ainda não está homologada.**

Escopo: planejamento integral, inspeção estrutural de código/contratos e processo de continuidade. Não reexecutou Azure, banco de cliente, navegador ou envio real. Não corrigiu os defeitos funcionais previamente reproduzidos, não implementou novos módulos, não publicou produto e não alterou orçamento/status de tickets.

## Evidência e identidade desde o início

O PDF inicial tem 14 páginas e foi extraído localmente como contexto. Preservados Core C0–C13, Connect, Flow, Portal, Contracts, SST, Legislativo e entrada condicionada de Educação/Saúde. [Visão consolidada](../arquitetura/EBT_ENTERPRISE_SISTEMA_COMPLETO.md).

O planejamento vigente tem 70 entregas/180h e cinco reservas/20h; 75 tickets, 17 pacotes e 238 cenários documentais. Site/Flow continuam adiados, com 14 tickets/36h preservados fora do ciclo. Essa revisão não contabiliza horas consumidas nem transforma a matriz em testes executados.

O checkout começou em `main` local `43a42bfe0b1daf07a96a3cacb19a9ff2b265bc5d`; o `origin/main` observado foi `fdc3a9fa76c713c41323739ba816491293a6381a`. São histórias divergentes a partir do planejamento anterior. Havia centenas de alterações/arquivos locais, incluindo o runtime Connect e provas posteriores. `main` remoto sozinho não representava esse runtime. Preservado o checkout/índice; snapshot em branch própria, sem merge/force/deploy.

Também existem branches remotas de fundação/PAC-05, com projetos `Ebt.Api`, `Ebt.Application`, `Ebt.Domain` e testes próprios. O Connect local usa `Ebt.Platform.Api` e uma UI própria. Não foram misturadas: convergência exige escolha de versão, diff de contratos, migração e gates, nunca somar automaticamente dois runtimes como se fossem um só.

O conector GitHub confirmou visibilidade **pública** nesta revisão, superando a nota histórica de repositório privado. Somente caminhos revisados/sanitizados entram no checkpoint; artefatos de contas, configurações privadas e entregas externas são excluídos. Não foi alterada a visibilidade do repositório.

## Achados e ações

| Prioridade | Achado verificável | Ação desta revisão / próximo passo |
|---|---|---|
| P1 | Runtime local não estava representado em `main` remoto; havia histórias/implementações paralelas | Checkpoint revisado em branch própria e retomada por SHA. Integrar em main só após reconciliação e CI |
| P1 | Revisão funcional anterior reproduziu troca de contato com recursos antigos acionáveis e confirmação de resposta sem destinatário identificado | Preservar R01/R02 como bloqueios de aceite. Código `openContact` atual conferido, sem alteração; reprovações históricas não foram reexecutadas aqui |
| P1 | Scanner real, restore Azure e aceite operacional têm registros pendentes | Manter pendências por versão/ambiente. Continuidade Git não certifica segurança/recuperação do produto |
| P2 | README afirmava entrega online e, no mesmo arquivo, “Nenhum serviço foi contratado ou conectado” | Corrigir a frase no resultado gerado, qualificando a proposta histórica e as provas posteriores |
| P2 | Marca/fundação/primeiro produto podiam ser lidos como projetos concorrentes ou redução da Enterprise a Connect | Consolidar família Enterprise, fundação Platform e produtos menores; preservar roadmap integral |
| P2 | Instrução “salvar” não constituía controle técnico de push/releitura | Implementar condição por hashes revisados, índice isolado, commit local, push e SHA remoto |
| P2 | Pedido de continuidade por limite de créditos não tinha contrato entre sessões | Prompt independente da skill local, estado estruturado e ZIP do commit revisado; sem promessa de transferência automática |
| P2 | Reuso de dois tenants poderia ser confundido com Core universal | Documentar isolamento versus generalização por consumidores pertinentes |
| P2 | Gerador não incluía todas as extensões na lista de fontes com hash | Incluir `live_docs.py` e `enterprise_planejado.py` no manifesto de entradas, preservando a proteção de gerados |

R03–R05 da [revisão anterior](REVISAO_PROMPTSPELLSMITH_CONNECT_20261007.md) permanecem no plano de correção: transferência de carteira/canal, revogação operável de chaves e vínculo de convite de conta existente. O relatório anterior identifica reproduções, correções propostas e limites. Nenhum desses cinco achados foi fechado por documentação ou checkpoint.

## Coerência backend/interface/plano

| Jornada | Código conferido | Relação com o início | Limite |
|---|---|---|---|
| Identidade/empresa/perfil | `Program.cs`, `Security.cs`, `Data.cs`, `TenantSqlContext.cs` | Recorte Tenancy/Identity/Audit | Inspeção focal; novas fronteiras exigem N |
| Relacionamentos/histórico | `CrmEndpoints.cs`, `Models.cs`, `App.tsx` | Connect CON1 e candidatos People/Context | ID/carteira do recorte, sem pessoa universal entre produtos |
| Próxima ação/tarefas | Endpoints CRM e telas Meu dia/Tarefas | Tarefas básicas iniciais | Sem motor SLA/escalonamento amplo |
| Conversas/resposta/status | `MessagingEndpoints.cs`, `WazVoxEndpoints.cs`, worker e UI | Comunicação priorizada no ciclo revisado | Prova registrada de texto 0.1.5; sem homologar Meta/campanhas/mídia |
| Documentos privados | `DocumentEndpoints.cs`, modelos e UI | GED delimitado | Produção recusa aprovação sem scan clean; scanner/restore ainda têm gates próprios |
| Site/Flow/Portal/Contracts/SST | PDF, backlog posterior, revisão das fontes | Família integral preservada | Roadmap; não endpoints implementados por esta revisão |

Recomendação visual preservada: Relacionamentos como módulo de referência, depois componentes compartilhados e estados de loading/erro/conflito/contexto. Não reescrever o frontend inteiro ou renomear schema/API por mudança de rótulo.

## Avaliação da skill e contrato revisado

O núcleo da skill é compatível com o projeto: recuperação de contrato, carregamento progressivo, fronteira de instrução, ferramentas reais, máquina de estados, gates e evidência. Foi estendido no repositório por [contrato do agente](../../prompts/AGENTE_EBT_ENTERPRISE.md), sem alterar a skill global ou memórias. Não havia razão para substituir sua arquitetura universal.

As extensões concretas acrescentam identidade Enterprise/Platform/produtos, escopo atual, salvamento mecânico, comportamento sem acesso, retomada e distinção checkpoint/deploy. O [prompt curto](../../prompts/RETOMAR_EBT_ENTERPRISE.md) permite iniciar a próxima sessão sem depender de caminho local da skill.

## Critérios de aceite do processo

- Revisão documental preserva orçamento/IDs/gates e links/hashes dos gerados.
- Lint estrito dos dois prompts, sem ERROR/WARN pendente.
- Testes Git com remote bare local: SHA remoto, índice/checkout preservados, repetição, revisão obrigatória, falha/retry, edição concorrente, divergência remota, secrets, arquivos privados/ausentes, dry-run, binário fixo, lock e fixtures sintéticas.
- Confirmação real do SHA da branch no GitHub; isso prova salvamento, sem aprovar produto ou merge em main.
- ZIP exporta somente bytes revisados do commit, com hashes e integridade, nunca a árvore privada atual.
- Agendador só é declarado ativo mediante prova de registro/execução; usa revisão existente, não consome API e não muda chat.

Resultados da execução desta revisão ficam em [evidência sanitizada](../../evidencias/enterprise_continuidade_20261007.json). Consultar o SHA remoto correspondente para retomar, sem interpretar esse arquivo como telemetria ao vivo.

## Próxima sequência

1. Revisar checkpoint e convergir as linhas de trabalho em recorte próprio, preservando suas histórias. CI hospedada de build/protocolo/proxy/documentos foi observada aprovada no SHA 92e4006; CI de continuidade foi aprovada no SHA 330845f depois de corrigir fetch-depth do checkout. Consultar os runs na evidência, sem promover gates de produto por esse resultado.
2. Autorizar correções R01/R02 e executar latência/erro, paginação/filtros e identificação do destinatário.
3. Planejar R03–R05 com contratos/negativas pertinentes; repetir a regressão afetada.
4. Conferir CI da próxima mudança, fechar scanner privado, restauração Azure isolada e aceite do recorte.
5. Só depois extrair Core e escolher o próximo produto, mantendo a Enterprise completa e o limite 180h + 20h.
