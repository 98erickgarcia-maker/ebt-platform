# Revisão focal dos frontends e prioridades

Data: 06/10/2026. Inspeção estática de arquivos específicos CASST, Vikings e Nutrição; não executou as aplicações nem observou suas telas online. Fontes não alteradas. Arquivos/versões/hashes estão no [snapshot](../../evidencias/revisao_frontend_fontes.json). A revisão não conclui que nenhum frontend foi bem desenvolvido.

## Constatações e hipóteses

| Base | Constatação no código lido | Implicação / sugestão | Limite da prova |
|---|---|---|---|
| CASST | main.tsx importa tokens e quatro folhas de apresentação, com crm-design-system.css por último. Há 33 ocorrências de !important nas quatro folhas. | Consolidar regras e conferir consumidores/computed styles antes de remover overrides; uma quinta camada seria fonte de manutenção. | Contagem não prova conflito renderizado; não foram examinados todos os seletores. |
| CASST | AppShell possui controle de foco/teclado no drawer, navegação por perfil, 28 ocorrências NavLink (incluindo ramificações) e teste próprio. | Preservar essas bases; reduzir menu ao recorte EBT, sem copiar todas as verticais. | Ocorrência não equivale a 28 itens simultaneamente visíveis; testes não foram executados aqui. |
| CASST | AppShell.tsx:156 apresenta busca como div e atalho visual; título informa planejamento. Notificação desabilitada em :158. | Busca deve ser local e funcional até existir contrato global; recurso futuro deve ter apresentação inequívoca. | Constatação de markup, não relato de falha autenticada atual. |
| Vikings | App.tsx concentra estados/dados, helpers e fluxos em código muito condensado; CSS também condensado. | Separar apresentação, dados e jornadas antes de ampliar; formatação ajuda revisar mas não substitui melhoria de contrato. | Densidade do arquivo não prova defeito ou baixa qualidade; snapshot atual difere da revisão histórica. |
| Nutrição | AppLayout separa áreas cliente/equipe/CRM por rotas/perfil; tokens e workspace próprios. | Preservar contexto por público e reutilizar padrões, sem forçar menu administrativo no portal de cliente. | Inspeção focal; não certifica jornada atual ou backend. |

## Versões e arquivos inspecionados

### CASST

HEAD local: `046e7c62359220aaf6ab30832f0fbff5b6f675f0`. O snapshot identifica hashes dos arquivos da árvore local; HEAD sozinho não representa alterações não commitadas.

| Arquivo relativo à fonte | Linhas | Observação quantitativa |
|---|---:|---|
| `src/frontend/src/main.tsx` | 22 | Conteúdo focal inspecionado |
| `src/frontend/src/layout/AppShell.tsx` | 189 | Conteúdo focal inspecionado |
| `src/frontend/src/styles/tokens.css` | 32 | 0 !important |
| `src/frontend/src/styles/global.css` | 342 | 6 !important |
| `src/frontend/src/styles/professional-refresh.css` | 684 | 4 !important |
| `src/frontend/src/styles/approved-commercial-ux.css` | 45 | 21 !important |
| `src/frontend/src/styles/crm-design-system.css` | 477 | 2 !important |
| `src/frontend/src/pages/ContactCenterPage.tsx` | 161 | Conteúdo focal inspecionado |
| `src/frontend/src/layout/AppShell.test.tsx` | 86 | Conteúdo focal inspecionado |

### Vikings

HEAD local: `d41d47923c7386fd926a92b3c29e525c1b307adf`. O snapshot identifica hashes dos arquivos da árvore local; HEAD sozinho não representa alterações não commitadas.

| Arquivo relativo à fonte | Linhas | Observação quantitativa |
|---|---:|---|
| `src/VikingsSst.Web/src/App.tsx` | 57 | Conteúdo focal inspecionado |
| `src/VikingsSst.Web/src/styles.css` | 5 | 0 !important |

### Nutrição

HEAD local: `ce57413cbf18dda264221e2ea93a5cb97df3ec41`. O snapshot identifica hashes dos arquivos da árvore local; HEAD sozinho não representa alterações não commitadas.

| Arquivo relativo à fonte | Linhas | Observação quantitativa |
|---|---:|---|
| `web/frontend/src/design/AppLayout.tsx` | 15 | Conteúdo focal inspecionado |
| `web/frontend/src/design/tokens.css` | 6 | 3 !important |
| `web/frontend/src/design/workspace.css` | 15 | 0 !important |

## Sugestões e vínculo com o plano

| ID | Prioridade | Sugestão | Tickets para avaliar |
|---|---|---|---|
| UX-01 | Alta | Consolidar contrato visual e retirar sobreposições confirmadas | P02-01, P02-02, P05-07 |
| UX-02 | Alta | Organizar navegação por fluxo e capacidade ativa | P04-01, P05-07 |
| UX-03 | Alta | Eliminar affordances de função inexistente | P05-03, P05-07 |
| UX-04 | Alta | Escolher layout com lista e detalhe contextual | P05-02, P05-03, P05-07 |
| UX-05 | Alta | Padronizar formulários, mensagens e estados | P05-02, P05-04, P06-03 |
| UX-06 | Alta | Separar página, componentes e acesso a dados | P02-06, P05-07, P05-08 |
| UX-07 | Alta | Conferir responsividade e acessibilidade | P03-05, P05-07, P09-03 |
| UX-08 | Média | Tornar lista e histórico consistentes | P05-03, P05-04, P07-04 |
| UX-09 | Média | Estabelecer checklist de interface por pacote | P05-10, P06-08, P07-06, P08-08, P09-01 |
| UX-10 | Baixa | Expandir catálogo e refatorar todas as telas legadas | P09-08 |

Prioridade é recomendação de produto, não defeito comprovado nem tarefa nova concluída. A meta é padronizar um fluxo inteiro, medir e só então ampliar. O orçamento e os 77 estados continuam preservados. Não absorver uma reescrita completa no ticket de marca/vocabulário.

[Contrato visual e componentes](PADRAO_VISUAL_E_COMPONENTES.md) | [Alternativas de layout](ALTERNATIVAS_DE_LAYOUT.md) | [Revisão e aceite](REVISAO_ACEITE_FRONTEND.md)
