# Cadastro e jornada CRM do EBT Connect

## Resultado e janela

Cadastro único, organização, contatos, histórico, até cinco etapas fixas, responsável e próxima ação. Segurança P04 e funcionalidades P05 fecham até 92h cumulativas; tarefas P07 completam o checkpoint em 104h e comunicação P11 fecha em 140h; duas configurações sintéticas usam a mesma regra. Isso não é Connect completo do plano mestre.

## Fluxo

Login/ativação -> lista -> criar contato -> abrir detalhe -> registrar conversa ou nota -> definir responsável/prazo -> mudar etapa -> recarregar -> consultar histórico. A mesma identidade acompanha todo o encadeamento.

## Recortes de interface

Lista: busca/paginação/filtro e estados carregar/vazio/erro/negado. Detalhe: identificação, organização, canais mínimos, etapa e origem. Histórico: autor, instante, tipo/direção e sequência. Próxima ação: responsável ativo, prazo e descrição. Alteração: resultado persistido ou falha recuperável; concorrência preserva entradas e pede nova conferência.

## Regras

Normalização de canal não une pessoas de empresas diferentes. Cadastro e interação usam contratos da fonte quando compatíveis. Nota interna não conta como conversa. Uma conversa antiga não substitui a última pela ordem de inserção. Responsável deve existir no escopo. Rótulo configurável não renomeia enum/ID. Cache lista/detalhe é invalidado conforme o resultado.

## Importação delimitada

Um layout fixo e até 100 contatos sintéticos. Área de preparação com preview/erros, confirmação explícita e resultado persistido/idempotente. Não é importador universal nem autorização para processar planilhas reais. A necessidade comercial de maior volume recebe medição e proposta própria.

## Aceite

G-SEG vigente; jornada QA em A/B; permissão por perfil/carteira e ID direto; repetição/conflito; cadastro único após reload; duas marcas sem forks de regra; manual e limites. P05 não implementa canal externo; resposta por API/webhook pertence a P11 e G-MSG. Fora: inbox coletivo avançado, campanha automática, chatbot, financeiro, OS e proposta comercial completa. Ver docs/produtos/ENTREGA_EBT_CONNECT.md.
