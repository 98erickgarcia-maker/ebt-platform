# Pesquisa e revisão — 07/10/2026

## O que a revisão confirmou

O relatório anterior do Connect (`docs/qualidade/REVISAO_PROMPTSPELLSMITH_CONNECT_20261007.md`, no repositório EBT) continua registrando cinco problemas: dados antigos durante troca de contato; conversas sem destinatário identificável; mudança de carteira com canal ativo; ausência de listagem/revogação na tela de chaves; convite de usuário já existente sem caminho de vinculação completo. Esta entrega não altera esses fontes .NET. Transfere os aprendizados para a extensão: limpar e vincular estado ao ID atual, mostrar destinatário, usar versionamento/isolamento e não presumir integrações autenticadas.

A CASST foi consultada somente como fonte de padrões, no checkout `crm-casst-foundation`: `ContactCenterPage.tsx`, `QuickInteractionDialog.tsx`, `CommunicationTemplateCatalog.cs` e contratos/serviços de prospecção. Foram observados verificação antes do cadastro, controle de duplicidade, histórico ligado ao registro, próxima ação, retorno e templates com variáveis. Nenhum cliente, credencial, histórico ou ativo CASST foi copiado. A biblioteca EBT foi escrita para este pacote; o template SST é genérico e deve ser ajustado à empresa realmente responsável pelo serviço.

No histórico do aplicativo Emergent foi encontrado o backend FastAPI/MongoDB fornecido pelo usuário. Ele importa `email_engine` e `graph_mailer`, que não foram disponibilizados. `generate_email` é chamado quando o lead não tem assunto/corpo; sem o arquivo não é possível provar qual provedor/modelo/preço está sendo usado. A fila do backend fornecido roda em memória, marca sucesso de `graph_mailer` como `sent`, dispõe de rota temporária de login e de limpeza global. A extensão oferece fila persistida, estados de evidência e bloqueia essas rotas de teste. Sua integração exige conferir a configuração real do mailer, sem afirmar que já houve conexão real nesta entrega.

## O que acrescentar na parte inicial/contatos

| Necessidade | Entregue no código | Uso |
|---|---|---|
| Contexto do contato | CNPJ, empresa, responsável/cargo, CNAE, cidade/UF, origem/data, qualidade do e-mail, score e motivos | Evitar abordagem sem contexto ou dado inventado |
| Próxima ação | Texto/data e contador de vencidos | Organizar retorno em vez de depender da memória |
| Links | mailto, tel, wa.me, site, LinkedIn e mapa | Abrir destino diretamente; abertura não é envio |
| Templates como CASST | Apresentação EBT, retorno, SST, WhatsApp; variáveis/versionamento/prévia | Regra e clique, sem IA |
| Outlook automático | Reuso MS_/AZURE_ e remetente do disparador | Autenticação de aplicação; OAuth individual é alternativa |
| Evidência de e-mail | Aprovação/digest, ID imutável, HTTP/request-id, reconciliação de Itens Enviados e JSON exportável | Não exigir foto ou captura da interface |
| Prospecção automática | Receitas, importação, dedupe, score, lote, pausa, cursor e orçamento | Descobrir empresas dentro da base importada |
| WhatsApp oficial | Cloud API de template, orçamento e webhook assinado | Aprender/provar o canal oficial; sem automação por QR |

## Fontes atuais e decisão de custo

1. [Microsoft Graph: criar mensagem](https://learn.microsoft.com/en-us/graph/api/user-post-messages?view=graph-rest-1.0) exige `Mail.ReadWrite` para rascunhos. [Enviar rascunho](https://learn.microsoft.com/en-us/graph/api/message-send?view=graph-rest-1.0) exige `Mail.Send`. As duas permissões precisam existir no registro de aplicação para o modo automático; `User.Read` de login não é suficiente.
2. [IDs imutáveis e Itens Enviados](https://learn.microsoft.com/en-us/graph/outlook-immutable-id) descreve criar o rascunho com `Prefer: IdType="ImmutableId"`, enviá-lo e recuperar a cópia pelo mesmo ID. Foi implementado esse caminho, com consulta posterior e tentativas limitadas. [sendMail](https://learn.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0) esclarece que aceitação HTTP não equivale à entrega. Por isso os estados são distintos.
3. [Receita Federal: cadastros abertos](https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/cadastros) permite preparar uma base empresarial local com fonte/data. [Metadados CNPJ](https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf) descrevem arquivos separados. O pacote não baixa/processa toda a base nacional automaticamente: importa um recorte normalizado e limitado.
4. [Cálculo do CNPJ alfanumérico](https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/documentos-tecnicos/cnpj/manual-dv-cnpj.pdf) fundamenta a validação de letras com valores ASCII menos 48 e módulo 11. Isso evita perder novos registros ao aceitar somente números.
5. [BrasilAPI](https://github.com/BrasilAPI/BrasilAPI) oferece consulta por identificador e pede uso responsável. Consulta por CNPJ conhecido não descobre empresas por cidade/CNAE; não foi usada como fonte ilimitada de scraping ou polling. O custo de manutenção de uma base importada deve ser incluído na operação.
6. [WhatsApp: preços oficiais](https://business.whatsapp.com/products/platform-pricing) variam por mercado/categoria, e cobrança e entrega são conceitos ligados. A janela de atendimento e situações de gratuidade não tornam toda campanha gratuita. [Política comercial](https://www.whatsapp.com/legal/business-policy/) exige opt-in e templates aprovados para iniciar abordagens, além de respeitar opt-out e caminho para humano. O código guarda a evidência e não confunde link direto com API oficial.
7. [Emergent: implantação](https://help.emergent.sh/deploying-web) e [gestão de créditos](https://help.emergent.sh/managing-credit-usage) foram pesquisados. Valores/tiers precisam ser conferidos no plano e ambiente real: a economia adotada aqui é evitar outro app/deployment, chamadas de IA por contato e provedores pagos de descoberta. Não foi calculado desconto percentual sem fatura do aplicativo atual.
8. [MongoDB: migração Motor/PyMongo Async](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/) orienta a API assíncrona atual. O pacote aceita o banco assíncrono recebido pela aplicação e não faz migração implícita do projeto Motor existente.

Custos variáveis de IA/descoberta no código: zero chamadas. WhatsApp possui reserva por tentativa com uma tarifa conservadora configurada, não uma fatura oficial. O simulador compara valores informados pelo operador. Hospedagem/Microsoft 365/BSP/manutenção não são declarados gratuitos. Nenhuma nova contratação ou publicação em produção foi executada.

## Status honesto

Código e testes locais não provam conta Microsoft/Meta autenticada nem envio real. Testes de API usam provedores simulados e dados sintéticos. O E2E observa a UI local; não é prova de envio externo. MongoDB real possui teste próprio e workflow CI. A extensão é escopo adicional, mantendo 180h de entregas e 20h de reserva do planejamento original; os gates existentes não foram promovidos.
