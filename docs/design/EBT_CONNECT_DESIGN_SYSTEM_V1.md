# EBT Connect Design System v1

Status: **baseline visual para implementação**. Produto-alvo: **EBT Platform**. Módulo inicial: **EBT Connect**.

## 1. Identidade

A interface pública e autenticada deste módulo usa somente a identidade EBT.

- Produto: `EBT Connect`.
- Plataforma: `EBT Platform`.
- Empresa: `EBT Enterprise`.
- Preto: `#111214`.
- Grafite: `#1B1D20`.
- Off-white: `#F6F6F4`.
- Laranja de ação: `#FF853E`.
- Verde de sucesso: reservado a concluído/positivo.
- Vermelho: reservado a crítico/atrasado.
- Amarelo: reservado a atenção.
- Azul/violeta: categorias secundárias, nunca identidade principal.

**Regra:** nomes e marcas de produtos-fonte não aparecem no EBT Connect. Identificadores persistidos de uma fonte também não são renomeados apenas por estética durante extração; a neutralização ocorre na nova fronteira EBT.

## 2. Shell oficial

O shell é a base reutilizável da EBT Platform:

1. sidebar proprietária EBT;
2. topbar;
3. área principal;
4. estados globais de feedback;
5. navegação responsiva;
6. tokens e componentes compartilhados.

### Sidebar

A sidebar não deve parecer um menu SaaS genérico.

- bloco de marca EBT no topo;
- grupos visuais recolhíveis;
- ícones consistentes;
- item ativo com trilho/acento laranja e superfície grafite elevada;
- estado hover discreto;
- área de conta compacta na base;
- opção futura de modo compacto sem mudar as rotas.

Grupos iniciais do Connect:

- **Relacionamento:** Dashboard, Empresas, Contatos, Prospecção, Pipeline, Agenda.
- **Inteligência:** Relatórios.
- **Configuração:** Configurações.

Módulos futuros entram por grupo/capacidade; não devem criar um segundo shell.

### Topbar

- busca global com contrato real antes de ser habilitada;
- atalhos rápidos;
- notificações somente quando houver fonte real;
- identidade do usuário/perfil;
- breadcrumb/contexto quando necessário.

Nenhum controle deve parecer funcional se ainda for apenas decorativo.

## 3. Componentes obrigatórios

A primeira implementação deve consolidar os seguintes componentes antes de duplicar estilos por página:

- `EbtShell`
- `EbtSidebar`
- `EbtTopbar`
- `EbtPageHeader`
- `EbtButton`
- `EbtIconButton`
- `EbtCard`
- `EbtKpiCard`
- `EbtStatusBadge`
- `EbtFilterBar`
- `EbtDataGrid`
- `EbtTabs`
- `EbtDrawer`
- `EbtDialog`
- `EbtTimeline`
- `EbtEmptyState`
- `EbtErrorState`
- `EbtSkeleton`

Abstrair somente quando o segundo uso provar que o contrato é realmente compartilhado.

## 4. Telas de referência

As nove telas aprovadas funcionam como mapa visual da família do produto, não como promessa de que todas entram no primeiro pacote funcional.

| Tela | Papel no design system | Situação funcional no Connect inicial |
|---|---|---|
| Login | autenticação e identidade | entra após fundação de segurança |
| Dashboard | visão de ação | usar apenas métricas derivadas de dados reais |
| Empresas | lista principal | entra no CRM inicial |
| Empresa detalhe | contexto + timeline + próxima ação | entra no CRM inicial |
| Contatos | diretório vinculado | entra no CRM inicial |
| Prospecção | entrada e qualificação | entra no CRM inicial |
| Pipeline | até cinco etapas | entra no CRM inicial |
| Agenda | próxima ação e compromissos | entra no CRM inicial |
| Relatórios | leitura gerencial | somente após contratos transacionais estáveis |

## 5. Regras de interação

- Um KPI clicável abre exatamente o conjunto contado.
- Lista, detalhe e exportação usam o mesmo critério de filtro.
- Mover etapa registra origem, destino, ator, instante e conflito.
- Próxima ação possui responsável, prazo e descrição.
- Histórico diferencia conversa, nota interna, alteração de etapa e tarefa.
- Ação de salvar deve mostrar `salvando`, `salvo`, erro recuperável ou conflito.
- Duplo clique/repetição não deve criar duplicidade quando a operação for idempotente.
- Alteração concorrente preserva a entrada do usuário e pede nova conferência.

## 6. Estados de interface

Cada tela precisa prever:

- carregando;
- vazio;
- erro;
- sem permissão;
- offline/indisponível quando aplicável;
- salvando;
- salvo;
- conflito;
- ação concluída;
- atraso;
- conteúdo parcial/paginado.

Zero não substitui erro. Lista vazia não substitui falha de carregamento.

## 7. Tabelas

O `EbtDataGrid` deve padronizar:

- busca;
- filtros;
- ordenação;
- paginação;
- seleção;
- ações por linha;
- ação em massa somente quando existir regra real;
- estados vazio/erro/loading;
- densidade desktop;
- transformação em cards/linhas empilhadas no mobile.

## 8. Responsividade e acessibilidade

- desktop é referência de densidade;
- tablet reduz colunas e prioriza conteúdo;
- mobile converte sidebar em drawer e tabela em apresentação responsiva;
- navegação completa por teclado;
- foco visível;
- contraste suficiente;
- área de toque adequada;
- sem depender apenas de cor para estado;
- `prefers-reduced-motion` respeitado.

## 9. Microinterações

- transições curtas e discretas;
- hover sem deslocamento excessivo;
- skeleton em carregamento;
- confirmação visual após persistência;
- nenhuma animação que atrase tarefa ou esconda estado real.

## 10. Critério para reproduzir em outros módulos

Um módulo da EBT Platform somente cria variante própria quando houver necessidade de domínio comprovada. Caso contrário, reutiliza tokens, shell, cabeçalho, cards, filtros, tabelas, timeline, dialogs e estados deste Design System.
