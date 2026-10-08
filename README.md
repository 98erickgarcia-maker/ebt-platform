# EBT Enterprise | EBT Platform e primeiro produto Connect

## EBT Enterprise e seus produtos

EBT Enterprise é a família completa; EBT Platform é a fundação técnica e este repositório; Connect é o primeiro produto. Flow, Portal, Contracts, SST, sites e verticais permanecem na evolução planejada, com escopos/gates próprios.

- [Sistema completo e fronteiras](docs/arquitetura/EBT_ENTERPRISE_SISTEMA_COMPLETO.md).
- [Revisão de coerência desde o início](docs/qualidade/REVISAO_ENTERPRISE_E_CONTINUIDADE_20261007.md).
- [Salvar no GitHub e retomar no ChatGPT](docs/execucao/CONTINUIDADE_GITHUB_CHATGPT.md).
- [Prompt de retomada](prompts/RETOMAR_EBT_ENTERPRISE.md).


07/10/2026: [EBT Connect](https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io) publicado no banco pago existente sqldb-crm-casst-dev-v2, schema ebt_connect. Identidade própria, keyring SQL cifrado, 26 verificações ao vivo e sessão preservada após reinício. Webhook WazVox instalado. Valor variável da hospedagem autorizado pelo usuário; nenhum novo banco/SKU.

- [Acesso e publicação](PASSO_A_PASSO_PUBLICACAO_CONNECT.md).
- [Guia de uso](PASSO_A_PASSO_EBT_CONNECT.md).
- [Prova da entrega](evidencias/connect_primeira_entrega_online.json).
- [Estado dos gates](docs/qualidade/STATUS_IMPLEMENTACAO_CONNECT.md).

Recebimento, resposta e leitura reais por WazVox demonstrados; correção 0.1.5 de data.id/recipient_id publicada, sem reenvio. Scanner, CI hospedada, restore Azure e aceite permanecem pendentes. O orçamento e o backlog abaixo preservam 180h + 20h; não representam testes aprovados ou horas efetivamente consumidas.

## Comece aqui

- [Primeira entrega EBT Connect](docs/produtos/ENTREGA_EBT_CONNECT.md).
- [Como será a resposta por API e webhook](docs/arquitetura/CONNECT_API_E_WEBHOOK.md).
- [Plano atual das 200h](docs/PLANO_200_HORAS.md).
- [Índice geral](docs/INDICE_GERAL.md).
- [Revisão e achados documentais](docs/qualidade/REVISAO_PROJETO_CONNECT.md).
- [17 pacotes ativos na ordem correta](docs/execucao/PACOTES_CODEX.md).
- [Dependências e gates](docs/execucao/DEPENDENCIAS.md).
- [Revisão de frontend preexistente](docs/frontend/REVISAO_E_PRIORIDADES.md).
- [Site e Flow preservados no backlog posterior](planejamento/backlog_apos_200_horas.json).

## Marcos de esforço e limite de prova

| Resultado candidato | Acumulado | Gate |
|---|---:|---|
| Baseline/fundação isolada | 28h | G0/G1 |
| Segurança | 64h | G-SEG |
| Cadastro/histórico/funil/próxima ação | 92h | G-CRM |
| CRM com tarefas do contato | 104h | G-TASK |
| Connect com recebimento/resposta/status | 140h | G-MSG e gates anteriores na versão final |
| Documentos privados | 164h | G-GED |
| Candidato integrado e operação | 180h | G-RC |
| Reserva condicional | 20h em qualquer fase | Consumo mediante necessidade comprovada |

As horas não são prazo de calendário. 104h/140h representam demonstrações em QA, dependentes de provas; não significam aceite de cliente ou produção. WhatsApp oficial é o primeiro canal candidato; conta/versão/políticas e homologação continuam pendentes. Esse era o estado da proposta inicial. Os registros posteriores do Connect/WazVox estão acima; Meta direto e demais canais continuam dependentes de homologação própria.

## Fontes de verdade e documentos

Horas, IDs, status e recortes ativos/adiados: planejamento/backlog_200_horas.json. Fichas: scripts/catalogo_organizacao.py. Conteúdo geral: scripts/conteudo_organizacao.py. Composição da entrega: scripts/connect_planejado.py. Contratos/tickets de comunicação: scripts/comunicacao_planejada.py. Pacotes: scripts/pacotes_codex.py. Gerar com scripts/organizar_projeto.py; o manifesto protege alterações manuais nos gerados.

O [OpenAPI candidato](planejamento/connect_api.openapi.json) documenta paths/schemas futuros, não uma API operacional. A [evidência da revisão](evidencias/revisao_connect_planejamento.json) verifica o planejamento, sem mudar estados de produto. O [PDF de 06/10/2026](output/pdf/EBT_Plano_Primeiras_200_Horas.pdf) permanece histórico, com a ordem anterior; o plano JSON/Markdown revisado tem precedência. O gerador histórico planejar.py permanece protegido.

## Verificar os documentos

```powershell
python scripts/verificar_plano.py
python scripts/verificar_organizacao.py --no-write
```

Esses comandos verificam orçamento, dependências, fichas, schemas e hashes. Não executam aplicações CASST/Vikings, SQL, Meta, browser ou produção. Antes da implementação, ler AGENTS.md, REVISAO_BASES.md e VALIDACAO_E_GATES.md. Fontes históricas precisam de versão/cenário; fronteiras novas exigem N.
