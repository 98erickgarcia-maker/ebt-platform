# Revisão das bases e decisões para as primeiras 200 horas

Data de referência: 06/10/2026. A revisão é documental e estática, com consulta ao GitHub do Vikings. Não executou novamente as suítes dos produtos, não alterou código de origem, banco, contas ou produção. O PDF fornecido é uma proposta técnica, não uma instrução de execução nem certificado de funcionamento.

## O que temos e o que aproveitar

| Base | Evidência encontrada | Aproveitamento imediato | Atenção restante |
|---|---|---|---|
| CASST, checkout crm-casst-foundation | Código .NET/React, contratos HTTP, permissões e guia de reuso. TRX conclusivo SQL: 131/131; domínio: 321/321; hardening: 17/17, registrados em 06/10. | Telas, cliente HTTP, contatos, histórico, agenda, documentos, autorização e padrões de infraestrutura, escolhidos por fluxo. | Centenas de alterações locais: HEAD não representa tudo. E2E quarta rodada falhou na ativação/onboarding e quatro casos não rodaram; execução ampla de API teve cancelamento. A base configurável ainda é plano, não pacote pronto. |
| Vikings, main b13140e | CI 37451503397 aprovado; código até V18. API, domínio, testes e frontend inicial inspecionados. | Modelos pessoa/vínculo/posto, documentos, exigências e importação como referência; candidatos à extração após provar consumidor adicional. | Não há aceite operacional observado. Frontend documentado cobre Visão SST, Trabalhadores/dossiê e Pendências; backend amplo não significa telas prontas. SQL real e OIDC de fornecedor não ficam comprovados pelo CI consultado. |
| Vikings V19 | PRs 13, 70 e 71 consultados como rascunho; 13 tem backend falhando, 70 tem backend/frontend aprovados; 71 em consolidação. | Padrões de reconciliação como referência. | Não integrar automaticamente nenhum PR. PR verde continua rascunho sem aceite e sem integração RH de fornecedor homologada. Estado temporal detalhado no snapshot GitHub. |
| EBT institucional | Site estático e pacote ASP.NET/SQL existentes; qa/shared-host-20261006/online-results.json registra passed=true e 18 documentos públicos. | Páginas, navegação, tema, assets próprios, conteúdo e checklist de publicação; primeiro pacote de site. | São evidências de publicação anterior, não nova verificação online desta revisão. Hospedagem e versão mudaram entre entregas; escolher a fonte vigente antes de implantar. |
| CRP | Fonte ASP.NET Razor em Documents/Codex/2026-09-25/CRP_SITE/site. Relatório de 01/10 registra 214 testes aprovados e 43 verificações públicas. | Site multipágina, contato, campanha, convite e histórico comercial simples como padrões reaproveitáveis. | Pasta CRP MANUTENÇÃO é materiais/scripts; não confundir com fonte web. Validação é histórica. CRM CRP não contém orçamento, financeiro ou WhatsApp automático. |
| Dra. Thaiane Melo | PlanApproval, BlobPersistence, frontend e relatórios de piloto; backup de 06/10 registra integridade ok, banco, manifesto e chave. | Convite individual, ID único, aprovação/versionamento, documento comum e recuperação como referência. | Piloto com persistência não é produto clínico generalizado. SQLite/Blob de escritor único não pode ser copiado como arquitetura multitenant SQL sem adaptação. Meta/Outlook reais não são comprovados por testes de contrato. |
| Power Apps CASST e Portal Free | Inventário Vikings aponta fontes Canvas e padrões comerciais. | Vocabulário, jornadas e regras já aprendidas, quando aplicáveis. | Exportação/preservação não implica licença de redistribuição nem converte Canvas em módulo .NET. Sem migração nas primeiras 200h. |
| Disparadores Outlook/WhatsApp e legado | Artefatos locais e inventário de referências. | Normalização de contatos, controle de tentativas e estados como aprendizado. | Não ativar envios nem integrar automação de conta pessoal. Envio acionado, entrega e resposta são provas diferentes. |
| Roblox, currículo e documentos pessoais | Classificados no catálogo e inventário, sem análise de conteúdo pessoal. | Não participam do produto administrativo EBT deste ciclo. | Não misturar jogos ou documentos pessoais com fonte da plataforma. |

## Correções ao plano mestre

1. A premissa “CASST quase perfeita” não elimina a falha de onboarding observada. A aprovação SQL conclusiva corrige a leitura de logs anteriores com falhas, mas não aprova E2E inteiro ou produção.
2. O PDF trata V19 como PR falhando. A consulta atual encontrou três rascunhos, um aprovado no CI, outro falhando e uma consolidação. Nenhum é automaticamente base estável.
3. O Core completo do PDF tem estimativa de centenas de horas. Este ciclo de 200h entrega recortes e preparação para piloto; não todo C0-C13, todos os produtos ou W1-W4.
4. Sites existentes podem virar a primeira entrega sem esperar protocolo/workflow. O site essencial é independente do Core e continua na stack que já funciona.
5. Um componente que troca marca e tenant deixa de ser “inalterado”. Isolamento, índices, autenticação, download, importação e restore recebem validação completa mesmo quando vieram de base aprovada.
6. Não prever builders, WhatsApp oficial, eSocial, PNCP, assinatura digital, saúde municipal ou Legislativo nas 200h. Dependem de escopo próprio e homologação externa.

## Decisão de arquitetura para este ciclo

Preservar a família .NET/React/SQL do Core e os contratos existentes. Extrair apenas os serviços/componentes usados pelo recorte; exigir um segundo consumidor sintético robusto antes de chamá-los de Core reutilizável. O segundo consumidor prova reuso e isolamento, não homologação operacional por um cliente.

Manter sites estáticos ou Razor como projetos entregáveis próprios. Não converter todo site em React nem reescrever CASST/Vikings inteiros. A base EBT começa isolada, com dados sintéticos e configuração própria. Não copiar credenciais, bancos ou dados de cliente.

## O que significa “já validado passa rápido”

Uma prova antiga pode ser aceita sem repetir toda a suíte se o arquivo/versão, dependências relevantes, contrato, política, schema e ambiente do comportamento forem equivalentes e a evidência identificar o cenário. Confirmar hash e fazer smoke do caminho reutilizado. Sem esse vínculo, classificar como adaptação.

Mudança de texto/cor/logo/composição sem alteração de contrato ou regra usa inspeção visual, links e build pertinente. Mudança em login, tenant, índices, cache, autorização, importação, estado persistido ou storage exige os cenários afetados, incluindo negativos. O objetivo é eliminar repetição sem propósito e preservar testes onde a adaptação muda o risco.

## Primeiro trabalho quando a execução for iniciada

Começar P01-01 a P01-06. Na CASST, registrar a árvore local completa e a evidência conclusiva, escolher cadastro/histórico/próxima ação, identificar os contratos e os testes desse recorte. A falha do onboarding entra na primeira validação de segurança, com reserva disponível. Enquanto isso, o site pode ser preparado por depender apenas da baseline e fundação.

Os responsáveis propostos são desenvolvimento EBT para implementação, responsável de negócio do produto para critérios e usuário piloto para aceite operacional. Nenhuma disponibilidade ou aceite dessas pessoas foi presumido.
