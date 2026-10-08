# Contrato visual candidato para EBT

Status: proposta para o primeiro recorte. Cores, composição e variante final ainda precisam de escolha visual; contratos, IDs, histórico, integração e autorização permanecem preservados. O desenho não aprova os módulos.

## Estrutura da aplicação

- Shell único: marca EBT configurável, empresa/ambiente identificados, perfil, navegação e área de conteúdo. Identidade não deve depender de texto do nome para mudar regra de negócio.
- Navegação do recorte: início, contatos/organizações, tarefas, documentos e protocolo quando ativos. Configurações no lugar previsível. Recurso futuro não aparece como ação pronta; permissões reais são verificadas no servidor.
- Cabeçalho de página: título curto, contexto e uma ação principal. Busca/filtros pertencem à lista atual até existir contrato de busca global.
- Área de trabalho: lista conserva busca, filtro e posição quando um registro é aberto. Detalhe sempre mostra a mesma identidade e vínculos; salvar invalida o dado afetado e demonstra o resultado após reload.
- Conteúdo do cadastro: resumo, histórico, próxima ação, documentos e tarefas vinculadas, conforme capacidade entregue. Não duplicar pessoa/organização para adequar layout.

## Fundamentos e componentes previstos

| Camada | Contrato candidato | Evitar |
|---|---|---|
| Tokens | Paleta semântica, tipografia, espaçamento 4/8/12/16/24/32px, raios e elevação coerentes | Cor, tamanho e sombra diferentes por tela sem motivo |
| Shell/navegação | AppShell e itens derivados de capacidade/perfil, com foco e ação real | Copiar o menu inteiro CASST para um produto menor |
| Título/ações | PageHeader, ação primária, secundária e perigosa identificadas | Várias ações principais disputando atenção |
| Lista | Toolbar, busca local, filtros, linhas, paginação e seleção preservada | Transformar todo dado em cartão decorativo |
| Formulário | Field, label, ajuda, erro, obrigatoriedade, validação e estado de gravação | Placeholder como único rótulo ou input que perde dado na falha |
| Estado | Loading, EmptyState, ErrorState, ForbiddenState e conflito específico | Página vazia sem explicar o próximo passo |
| Registro | RecordHeader, HistoryList, NextAction e vínculos reais | Criar histórico novo apenas para mudar a aparência |
| Overlay | Dialog/Drawer com foco, Escape, retorno ao controle e fundo inerte | Modal sem teclado ou bloqueio de ações necessárias |

Os nomes são candidatos de componentes, não declaração de que já existem. Adaptar/reutilizar primitivas compatíveis antes de criar outras. Colocar variante/tamanho no contrato; não anexar outra folha global para corrigir uma página isolada.

## Organização do código na implementação

Manter React/TypeScript quando essa for a base escolhida. Separar shell, tokens, primitivas e módulos; páginas compõem componentes, hooks/adapters cuidam de dados e contratos existentes continuam sendo a fonte das operações. Não escolher nova biblioteca visual só para trocar aparência. Se uma dependência for proposta, comparar licença, acessibilidade, custo de migração e compatibilidade antes de alterar o projeto.

Consolidar CSS gradualmente: rastrear import/selector/computed style, migrar um grupo por vez e retirar uma regra apenas após conferir consumidores. Contagem de !important ou arquivo minificado orienta investigação; não autoriza exclusão automática.

## Estados obrigatórios conforme o fluxo

Mostrar carregamento sem conteúdo enganoso; vazio inicial diferente de busca sem resultados; erro com recuperação; acesso negado sem expor dados; submissão sem clique duplicado; sucesso apenas após resposta confirmada; conflito sem perder entrada; arquivo restrito e validação de upload com motivo. Consulta não exibe ações de alteração e o servidor continua protegendo a operação.

## Responsividade e acessibilidade

Conferir 320, 390, 768 e 1366px, teclado e zoom/reflow. No celular, detalhe ocupa a coluna e preserva retorno à lista; tabela tem apenas rolagem própria quando bidimensionalmente necessária. Campos precisam de rótulo, erro associado, foco visível e anúncio pertinente de status.

Referência: [WCAG 2.2](https://www.w3.org/TR/WCAG22/). Texto comum pede contraste mínimo 4,5:1 e texto grande 3:1, conforme definições/exceções. O mínimo AA de alvo é 24×24 CSS px ou condições de espaçamento/exceções; usar 44px como escolha de conforto para toque quando couber. Foco deve permanecer visível e não totalmente oculto; reflow preserva conteúdo a 320 CSS px conforme o critério. Esta proposta não é certificação de conformidade.

## Navegação

[Revisão e prioridades](REVISAO_E_PRIORIDADES.md) | [Alternativas](ALTERNATIVAS_DE_LAYOUT.md) | [Revisão e aceite](REVISAO_ACEITE_FRONTEND.md)
