# Alternativas de layout para o frontend EBT

Status: propostas, não interfaces publicadas. A comparação na conversa usa somente registros fictícios e interações locais. Nenhum layout foi aplicado às fontes.

## Workspace, recomendação inicial para o CRM

Navegação lateral enxuta; título/busca/filtros; lista central e detalhe contextual do registro selecionado. Histórico e próxima ação permanecem ligados ao cadastro. A opção reduz troca de páginas durante atendimento e permite comparar vários registros. No celular, lista e detalhe se alternam com retorno que preserva a seleção.

Boa escolha quando o trabalho é localizar um contato, entender histórico e agir sobre o mesmo ID. Exige evitar tabela com colunas excessivas, garantir contexto do selecionado e não usar drawer estreito para formulário complexo.

## Foco em tarefas, alternativa para rotina diária

Navegação superior compacta; próximas ações como entrada; seleção abre o mesmo cadastro e seus vínculos abaixo. Busca/lista completa continuam disponíveis. A opção organiza o dia por responsável/prazo e reduz a necessidade de conhecer todos os módulos para executar um retorno.

Boa escolha quando a prioridade é o que fazer agora. Exige acesso claro ao cadastro completo, reconciliação de prazo/estado com o backend e ausência de métricas decorativas. Uma pendência não significa conversa enviada ou tarefa realizada.

## Escolha e consistência

Recomendo Workspace como shell de cadastro/CRM e uma visão de próximas ações dentro do mesmo shell quando P07 estiver implementado. Os dois exemplos exploram entradas diferentes para a mesma identidade, não duas aplicações com contratos separados. Ainda não há aprovação visual do usuário.

Avaliar: identificar empresa/perfil; encontrar cadastro; abrir sem perder filtro; localizar histórico; definir próxima ação; entender sucesso/erro; voltar no celular e usar teclado. Priorizar a variante que completa a jornada com menos dúvida, sem esconder informação necessária. Não usar gosto de cor como único critério.

Um novo shell pode ser aplicado a um recorte novo sem substituir todos os frontends antigos. Sites institucionais e portal de cliente conservam necessidades próprias; compartilham marca/primitivas quando adequado, não obrigatoriamente o mesmo menu administrativo.

## Escopo das 200h

As propostas detalham o trabalho de interface já previsto no recorte. Implementar padrão mínimo em uma tela completa antes de expandir. O ticket P05-07 (3h) não promete reescrita de todas as telas ou catálogo completo. Se a transformação exceder o orçamento, medir e reestimar/cortar escopo; expansão geral vai ao backlog pós-ciclo. Nenhuma hora ou estado dos 77 tickets foi alterado.

## Navegação

[Contrato visual](PADRAO_VISUAL_E_COMPONENTES.md) | [Prioridades](REVISAO_E_PRIORIDADES.md) | [Pacotes](../execucao/PACOTES_CODEX.md)
