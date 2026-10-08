# Prospecção da Emergent integrada à plataforma EBT

Data: 07/10/2026. Estado: especificação da adaptação aprovada pelo usuário nesta conversa; código da interface recuperado. A restauração visual das telas atuais EBT foi autorizada separadamente e está em validação; a integração funcional da prospecção ainda não foi implementada.

## Resultado solicitado

Trazer para este projeto o módulo de contatos e prospecção que já programamos em `entregas/emergent-prospeccao-v1`, usando a interface da prévia como referência. O usuário informou que a versão atual da Emergent não foi salva no GitHub e pediu a implementação aqui. Pediu também que toda a interface retorne ao padrão anterior e que o projeto seja entregue funcionando.

A autorização para executar existe. Esta revisão define a adaptação arquitetural para evitar a substituição dos módulos, da autenticação ou dos dados que já existem na EBT. A especificação foi aprovada; a revisão do plano e a escolha de execução, exigidas pela skill de planejamento aplicada, estão pendentes.

O destino é `src/frontend` e `src/backend/Ebt.Platform.Api`, no projeto EBT Connect. A entrega recuperada permanece preservada como fonte. Nenhum salvamento ou exportação adicional da Emergent é condição para construir esta adaptação local.

## Fontes e limites conhecidos

| Fonte observada | Uso nesta integração | Limite da evidência |
|---|---|---|
| `entregas/emergent-fontes-recuperadas-2026-10-07/frontend-da-previa/src` | 22 arquivos originais JS/JSX/CSS da prévia, incluindo a área de prospecção | Recuperados do source map público, com hashes. Não incluem backend, manifesto, lockfile nem Secrets da prévia |
| `entregas/emergent-prospeccao-v1` | Regras, templates, receitas, filtros, filas, conectores e comportamento que programamos | Implementação original FastAPI/React/MongoDB; testes anteriores não aprovam a adaptação SQL/.NET |
| `entregas/emergent-fontes-recuperadas-2026-10-07/github-app-mail-main` | Referência do disparador Graph e dos nomes de configuração | Versão anterior: commit `00939998ed18313941af8646795e5684ba7e93a5`; autenticação e telas diferem da prévia |
| `src/frontend/src/App.tsx`, `api.ts`, `style.css` | Login, contexto, navegação e componentes da plataforma local | Código atual consultado; nesta etapa não foi reconstruído ou testado novamente |
| `src/backend/Ebt.Platform.Api` | Autorização, CRM, tarefas, documentos, conversas e persistência | Preservar a implementação atual e as alterações locais preexistentes |

As páginas Assistente, Rascunhos e Classificar da prévia chamam `/api/ai/...`. O backend dessas páginas não está no material recuperado. O escopo pedido é o módulo que já programamos: templates e regras sem LLM. Não apresentar geração por IA como integrada ou contratar provedor para suprir esse backend ausente.

## Abordagem selecionada

**Adaptar o módulo à stack atual .NET/React/SQL.** A interface aproveita o conteúdo, os fluxos e as regras do módulo recuperado, mas usa o cliente HTTP e a sessão da EBT. O servidor implementa as capacidades de prospecção no schema EBT, preservando os contratos atuais.

Alternativa de manter FastAPI/MongoDB como serviço adicional exigiria outra operação, armazenamento e ponte de identidade. Reconstruir o aplicativo antigo inteiro perderia contratos atuais do Connect e ainda não recuperaria o backend de IA da prévia. A adaptação à base existente evita esses dois problemas e mantém uma única identidade de contato.

## Padrão de toda a interface

Referência confirmada pelo usuário: “padrão ebt enterprise”, de alto padrão. Fonte visual conferida em `C:/Users/Ivair Silva/Documents/ChatGPT/EBT ENTERPRISE SITE/site/public/assets/premium.css` e na marca oficial `ebt-logo-240.webp`: preto `#101112`, branco suave `#f5f4f0`, destaque laranja `#ff8b46`, texto escuro em superfícies claras e tipografia Segoe UI. Depois, o usuário forneceu três referências de telas e esclareceu que elas não devem ser copiadas exatamente, pois existem decisões posteriores. A composição adotada usa menu/login pretos e área de trabalho clara, com tabelas, cartões e formulários legíveis, preservando fluxos e capacidades atuais. Não usar o tema verde-petróleo do Connect anterior nem o verde-limão da Emergent como identidade da entrega.

Aplicar os mesmos tokens e componentes ao login, ativação, Meu dia, Relacionamentos, Tarefas, Conversas, Documentos, Configurações e nova área Prospecção. As seis abas internas — Painel, Contatos, Prospecção automática, Templates, Conexões e Custos — devem seguir esse padrão. Não importar os seletores globais do `App.css` escuro da prévia sobre a aplicação EBT.

Preservar a composição atual das telas existentes: menu, cabeçalho, lista, detalhe contextual e formulários. Acrescentar uma entrada Prospecção à navegação. A lista de prospecção abre o mesmo contato do CRM. Configurações e Conexões apresentam os mesmos canais e seus estados reais.

Consistência inclui bordas, raios, espaçamento, estados, tipografia, foco e legibilidade, além das cores. Conferir 320, 390, 768 e 1366px, zoom e teclado. Tabelas podem ter rolagem própria; a página inteira não deve exigir rolagem horizontal. Foco de diálogo, Escape e retorno ao controle seguem o comportamento existente.

## Identidade e modelo de dados

1. `Contact` continua sendo a identidade do contato e `Organization` a da empresa. Histórico, tarefas, conversas e documentos mantêm esses IDs. Não criar uma segunda coleção de leads que se descole do CRM.
2. Acrescentar metadados de prospecção vinculados ao contato: CNPJ da empresa, CNAE, UF, município, papel do contato, site, LinkedIn, qualidade do e-mail, fonte e data, situação de revisão e supressão. Situacão de revisão não substitui as cinco etapas comerciais atuais.
3. CNPJ fica como texto normalizado, com suporte numérico e alfanumérico segundo as regras do módulo. Deduplicar catálogo por tenant/CNPJ e manter carteira. Mais de uma pessoa pode pertencer à mesma empresa. A criação automática inicial usa uma chave externa estável para impedir repetir o mesmo contato; contatos adicionais são explícitos.
4. O catálogo importado registra fonte, URL e data. Não atribuir consentimento, e-mail verificado ou decisor confirmado a partir da presença na base. Seleção por UF/município/CNAE consulta o catálogo local; não tratar BrasilAPI como busca de empresas.
5. Novas entidades: catálogo empresarial, receita e execução, template e versão, aprovação e operação de e-mail, supressão e consumo mensal. FKs, índices, filtros, barreira RLS e acesso direto por ID respeitam o tenant. Entidades ligadas a contatos também respeitam carteira.
6. A próxima ação continua derivada de `ContactTask`. Eventos da prospecção alimentam `Interaction`, com autoria, instante e referência da operação. Evidências técnicas da fila complementam esse histórico sem inventar interações entregues.

## Autenticação e contratos

Reutilizar `AccessScope`, sessão revogável, cookie HttpOnly, CSRF e o cliente `api.ts`. O servidor resolve tenant, usuário, perfil e carteira. A interface não define o espaço de dados e não armazena tokens Graph.

Preservar `/api/connect/v1` e `/api/auth` existentes. Registrar novas rotas em `/api/connect/v1/prospecting`. O componente recuperado deixa de chamar diretamente `/api/prospecting` e `REACT_APP_BACKEND_URL`. Adaptadores tipados traduzem seus campos para os contratos EBT.

Administrador configura canais, importa catálogo e edita templates. Operador consulta e trabalha apenas na carteira autorizada, prepara mensagens e executa receitas que pertencem a ela. Perfil de consulta lê dados permitidos e não recebe controles de alteração. Todas as negativas são verificadas no servidor.

Mutações repetíveis usam chave de idempotência; alterações usam versão otimista. Tentativa repetida com outro conteúdo gera conflito. Paginação, filtros, exportação e evidência recebem o mesmo isolamento das consultas normais.

## Fluxos do módulo

### Catálogo e receitas

Importação limitada com preview, erros por linha e confirmação; fonte obrigatória; atualização sem duplicação ou mudança implícita de carteira. Receita define nome, UF, município, CNAE, lote de 1 a 100, intervalo de 1 a 720 horas e limite mensal configurado.

Worker usa cursor, agendamento, lease e contador persistidos. Reservar o consumo e avançar o lote de forma atômica; dois workers não podem repetir registros nem exceder o limite. Pausa impede novos lotes e reinício retoma do ponto confirmado. Uma base vazia exibe instrução para importar catálogo, sem simular empresas encontradas.

### Contatos e templates

Classificação explicável mostra os fatores e a qualidade da fonte. Revisão altera metadados com controle de versão, mantém histórico e permite supressão com motivo. Exportação traz apenas o conjunto autorizado e neutraliza fórmulas em CSV.

Templates de apresentação e retorno são locais e versionados. O preenchimento mostra destinatário, assunto e corpo; variável ausente bloqueia aprovação. Alteração de contato, destinatário, remetente ou template invalida a prévia aprovada. O digest usa os valores efetivamente exibidos e a versão do template.

### Outlook

Conector automático application usa configuração exclusivamente do servidor e a caixa remetente autorizada. O app-mail usa `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET` e `SENDER_MAILBOX`; o módulo original usa `MS_*`/`AZURE_*`. O adaptador aceita um conjunto completo e coerente por conexão e não mistura tenant de um aplicativo com segredo de outro. Configuração de login Microsoft continua distinta de autorização para envio.

Conexão pertence a um tenant/carteira e guarda referência de Secrets. Nenhuma credencial fica na interface, em TXT, ZIP, logs ou repositório. Não alterar DNS, MX, SPF, licença ou contratar caixa postal para implementar o conector.

Fila durável exige destinatário e texto revisados, digest aprovado e agendamento. Rascunho e envio são operações diferentes. Criar rascunho com ID imutável, persistir esse ID antes de solicitar envio e reconciliar com Itens Enviados. HTTP 202 significa aceitação da solicitação; não comprova entrega ou leitura. Timeout ou falha ambígua produz resultado incerto e impede reenvio automático.

Registrar evidência sanitizada com IDs do provedor, estados, timestamps e digest, acessível apenas ao contexto autorizado. Supressão cancela operações pendentes do contato. Envio fica desativado por padrão até configuração e teste controlado autorizado; este pedido não especifica destinatários de campanha.

O modo delegated alternativo do pacote pode ser preservado como adaptador opcional com cache protegido, estado de uso único e vínculo à sessão. Não substituir o login EBT nem exigir um login Microsoft adicional no fluxo application.

### WhatsApp e custos

O botão manual preenche `wa.me`, registra texto, telefone e versão preparados. Abrir a conversa não confirma envio. As conversas atuais WazVox permanecem no módulo Conversas, com o mesmo contato e prova de status já prevista pelo Connect.

Preservar a capacidade do pacote de template oficial Meta como conector desativado até configuração e homologação própria. Exige opt-in documentado, template/idioma/parâmetros aprovados, destinatário confirmado, assinatura do webhook, deduplicação e orçamento atômico. Não converter o adapter atual de resposta de texto WazVox em campanha de template por inferência.

Custos exibem cálculo com parâmetros fornecidos pelo usuário, consumo de registros e limites. Distinguir cálculo de fatura efetiva; não atribuir redução percentual sem base nem apresentar uma tarifa Meta única como universal. Sem serviço pago ou LLM novo.

## Erros, reinício e segurança

401 pede novo acesso; 403 não revela o registro; 409 preserva entrada e orienta atualizar. Troca de empresa ou carteira limpa seleções, prévias e cache; respostas atrasadas são descartadas pelo cliente. Falha de conexão mostra estado real e permite corrigir configuração sem apagar a fila.

Workers verificam vínculo ativo, acesso da carteira, supressão, conexão, aprovação e limite antes da operação. Reinício preserva cursores e operações incertas. Auditoria recebe ações e referências, sem Secrets ou conteúdo desnecessário. Importações, templates, respostas e sites são dados, nunca instruções executáveis.

## Validação e entrega

| Recorte | Critério observável |
|---|---|
| Frontend inteiro | Build e navegação em todas as telas; estados loading/vazio/erro/consulta; visual coerente nas quatro larguras; teclado, diálogos e foco; sem erro de console |
| CRM integrado | Contato originado em receita aparece em Relacionamentos com o mesmo ID; nota/tarefa/documento continuam após reload; cadastro anterior permanece íntegro |
| Segurança nova — trilha N | SQL sintético A/B, carteira, acesso direto por ID, leitor sem mutação, CSRF, troca de contexto, exportação e evidência negativas |
| Catálogo/worker — trilha N | Repetição da importação, duas execuções concorrentes, deduplicação, limite mensal, pausa, retomada e persistência após reinício |
| Aprovação/fila — trilha N | Mudança de template/contato invalida digest; supressão interrompe; repetição não duplica; falha ambígua não reenvia; rascunho e aceitação não viram entrega |
| Conectores | Contratos Graph/Meta com respostas simuladas; prova real só com caixa/número controlado e teste autorizado; WazVox atual preservado |
| Recuperação | Migration revisada, backup e retorno ensaiados em QA próprio; manifesto dos arquivos e comandos/resultados sanitizados |

Usar testes sintéticos específicos das regras e regressão dos consumidores afetados. Testes históricos do pacote não são resultados da adaptação. Não declarar build, isolamento, envio, homologação ou publicação concluídos antes da prova correspondente.

Antes de editar, registrar hashes e backup dos arquivos afetados, pois este checkout contém muitas alterações preexistentes. Isolar o diff e não executar reset/clean, inclusão ampla no Git ou publicação de mudanças acumuladas. Alterações SQL deste trabalho são testadas no banco local exclusivo de QA, sem aplicar migration ao banco compartilhado por inferência.

Entrega revisável: fontes adaptados, manifesto e testes, comparação visual de todas as telas, manual local e rollback. A publicação online permanece uma etapa específica com candidato validado; recuperação de fonte não significa publicação.

## Sequência para o plano de execução

Revisão posterior solicitada pelo usuário: confrontar também os achados R01–R05 de `docs/qualidade/REVISAO_PROMPTSPELLSMITH_CONNECT_20261007.md` com o código atual e fechar os cenários dependentes antes de ampliar o produto. As imagens não autorizam apresentar busca global, login Google/Microsoft, notificações, valores de vendas, pipeline financeiro ou relatórios inexistentes como capacidades prontas.

1. Congelar a baseline local e fechar o padrão visual escolhido; preservar as duas fontes recuperadas.
2. Preparar ambiente QA próprio, modelo/contratos de prospecção e testes de isolamento e identidade do CRM.
3. Adaptar Painel, Contatos e Templates ao shell EBT; provar cadastro/histórico/tarefa no mesmo ID.
4. Integrar catálogo, receitas e worker; provar concorrência, consumo, pausa e reinício.
5. Adaptar Outlook, aprovação, fila e evidências; preservar WhatsApp manual e integrar o template oficial sob configuração explícita.
6. Concluir Conexões/Custos e validar todas as páginas e os consumidores atuais, com manifesto e limites honestos.

Esta sequência não é uma promoção dos gates nem uma estimativa nova de horas. A baseline continua em 180h de entregas e 20h de reserva. A extensão e sua adaptação são escopo adicional autorizado, ainda sem consumo real apurado; não debitar a reserva por conveniência nem afirmar que cabem nela.

## Fora deste recorte

Cadências automáticas dos dias 0/3/7, inbox delta, bot de WhatsApp, filas multiatendente e requisitos COREN são os Pedidos 2, 3 e 4 do pacote e permanecem posteriores. A integração não converte todos os módulos e verticais do planejamento EBT em produto pronto. Não copiar dados de clientes, credenciais, anexos comerciais reais ou bancos dos projetos-fonte.

## Situação no fim desta preparação

Interface pública recuperada: sim, 22 fontes com manifesto. Código original de prospecção disponível: sim. Backend atual da Emergent recuperado: não. Restauração da identidade EBT nas telas atuais: aplicada localmente, com validação em andamento. Adaptação funcional da prospecção ao EBT Connect, testes desta adaptação e publicação: ainda não realizados. A especificação foi aprovada e o plano está em revisão; obter backend da Emergent ou salvá-lo no GitHub deixou de ser pré-requisito para a abordagem selecionada.
