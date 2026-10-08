# Cenário recomendado para o EBT Connect atual

07/10/2026. Revisão solicitada pelo usuário após fornecer três referências visuais e esclarecer que existem decisões aprovadas posteriormente. As imagens orientam identidade e composição; não substituem contratos, decisões posteriores ou evidência de funcionamento.

## Decisão de apresentação

Manter o padrão institucional EBT Enterprise: menu e apresentação de login pretos, marca oficial, destaque laranja e superfícies claras para trabalhar. A área de conteúdo clara favorece listas, histórico, formulários e documentos. Usar a mesma tipografia, espaçamento, botões e estados em todas as telas, com a organização funcional atual preservada.

As referências mostram boa hierarquia: título e ação principal, filtros próximos da lista, status legíveis e detalhe organizado. Aplicar esses princípios sem copiar nomes, valores, logos de clientes, fotos de pessoas, datas, contagens ou funcionalidades ilustrativas. Não incluir valores de vendas fictícios para aproximar o painel das imagens.

## Precedência do material

| Material consultado | Papel na decisão atual |
|---|---|
| Instruções atuais do usuário | Destino local, identidade EBT, preservação das mudanças aprovadas depois das imagens e análise para escolher o melhor cenário |
| `docs/superpowers/specs/2026-10-07-emergent-na-plataforma-ebt-design.md` | Especificação da integração de prospecção aprovada nesta conversa |
| `docs/arquitetura/DECISAO_IMPLEMENTACAO_20261007.md` e código atual | Sessão, SQL/schema, IDs, próxima ação derivada, importação e política de envio incerto |
| `docs/qualidade/STATUS_IMPLEMENTACAO_CONNECT.md` | Estado registrado da implementação/publicação anterior, sem convertê-lo em nova prova online |
| `docs/qualidade/REVISAO_PROMPTSPELLSMITH_CONNECT_20261007.md` | Achados reproduzidos do runtime atual que precisam ser tratados antes do aceite e da expansão |
| `docs/PLANO_200_HORAS.md`, `VALIDACAO_E_GATES.md`, `gestao/ESCOPO_E_RESULTADOS.md` | Ordem, limites, 180h + 20h e critérios de prova; documentos de planejamento não são testes executados |
| `docs/REVISAO_BASES.md`, `arquitetura/DADOS_E_INVARIANTES.md`, `CONTRATOS_E_COMPATIBILIDADE.md` | Preservação das bases, IDs, vínculos, isolamento, versão e compatibilidade |
| Documentos de frontend, incluindo padrão, alternativas, prioridades e aceite | Lista/detalhe contextual, navegação real, estados, foco e responsividade |
| `entregas/emergent-prospeccao-v1/docs/ESPECIFICACAO.md` e `PEDIDOS_EMERGENT.md` | Funcionalidades já programadas do Pedido 1; Pedidos 2/3/4 continuam posteriores |
| Três imagens fornecidas e CSS institucional EBT consultado | Referência visual e marca; nenhuma imagem aprova backend ou substitui decisões posteriores |

O PDF histórico e as fichas antigas continuam preservados. Trechos antigos que dizem “planejamento apenas” não revogam a autorização posterior de programação; trechos que descrevem publicação anterior não aprovam automaticamente esta nova versão.

## O que preservar e o que concluir

| Fluxo | Cenário recomendado |
|---|---|
| Login e empresa | Manter o acesso EBT e contexto autorizado. Botões Google/Microsoft das imagens só cabem quando os provedores realmente estiverem implementados |
| Meu dia | Pendências e próximas ações reais, ligadas ao responsável e mesmo contato. Sem gamificação ou números comerciais decorativos |
| Relacionamentos | Cadastro único, busca/filtro/paginação e detalhe do mesmo ID. Empresa é a organização comercial; tenant é o contexto de acesso |
| Próxima ação | Continuar derivada de tarefa aberta, sem uma segunda cópia editável de prazo/responsável |
| Conversas | Identificar pessoa/destinatário independentemente da página de contatos; preservar WazVox e estados distintos de aceite, envio, entrega e leitura |
| Documentos | Preservar vínculo, versão, revisão e download privado. O restauro visual não aprova scanner ou restore Azure |
| Configurações | Manter perfis/carteiras, tornar revogação de chaves utilizável e fechar convite existente sem redefinir senha |
| Prospecção | Adaptar o módulo recuperado ao CRM atual, com catálogo local, revisão, receitas, templates, aprovação, Outlook, WhatsApp manual, limites e evidências |
| Pipeline e agenda das imagens | São referências de apresentação. O sistema atual tem cinco etapas e tarefas; novos contratos de oportunidade/valor/calendário não devem ser inventados para imitar o mockup |
| Relatórios, notificações e busca global | Mostrar apenas consultas/ações implementadas. Não acrescentar sino, atalho ou gráfico que pareça funcionar sem contrato e resultado real |

## Prioridade de correção confirmada pela revisão

1. R01: impedir recursos do contato A sob o cabeçalho de B durante carga/erro; liberar ações apenas no contexto confirmado.
2. R02: identificar corretamente destinatários de conversas fora da página/filtro de contatos e bloquear resposta sem identificação.
3. R03: impedir transferência de carteira incompatível com o canal enquanto não existir transferência consistente.
4. R04: listar metadados de chaves e revogar pelo ID sem reapresentar Secrets.
5. R05: completar aceitação autenticada do convite para conta existente, com correspondência de titular e proteção de senha.

Esses achados vieram de revisão anterior, confrontada nesta rodada com os arquivos atuais; a correção ainda precisa de seus testes específicos. Não foram marcados resolvidos apenas por aparecerem no plano.

Durante a validação atual foi reproduzido outro defeito: clicar no item da página atual enquanto a carga inicial está pendente invalida a resposta, mas não inicia uma substituta. Isso mantém “Atualizando dados…” permanentemente. Foi criado um teste determinístico que falhou antes da correção; a navegação passou a iniciar a carga substituta e o teste passou. Essa correção é distinta de R01.

## Critério de conclusão

Frontend consistente não significa projeto inteiro concluído. A entrega exige build, jornadas com persistência, estados negativos, isolamento, fila/recuperação, revisão dos conectores, visual em 320/390/768/1366px e registro dos resultados na versão correta. Provas locais, históricas, reais e publicação permanecem separadas.

O [plano de implementação](../superpowers/plans/2026-10-07-emergent-na-ebt.md) agora começa pelo fechamento dos achados da base, seguido da adaptação funcional. A identidade visual está aplicada localmente. Build e cinco testes de navegador passaram, incluindo a regressão da navegação; login e seis telas foram conferidos em quatro larguras, sem overflow de página, falha no contraste medido ou erro inesperado de console. O escopo do contraste considera texto em superfícies sólidas e não é certificação completa de acessibilidade. [Resultados e versão](../../evidencias/enterprise_ui_verificacao_20261007.json). Nenhuma publicação ou alteração do banco compartilhado foi realizada nesta rodada.
