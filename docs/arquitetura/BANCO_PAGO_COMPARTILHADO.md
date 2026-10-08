# Banco pago compartilhado — decisão confirmada

**Estado vigente de 07/10/2026:** primeira entrega publicada e 26 verificações ao vivo aprovadas. [Acesso e provas](../../PASSO_A_PASSO_PUBLICACAO_CONNECT.md). Banco pago compartilhado preservado; valor variável autorizado posteriormente. Referências abaixo a host inexistente/F1/R$30 fixos descrevem o cenário anterior e foram superadas por esta publicação. Fluxo real de texto WazVox demonstrado na 0.1.5; scanner, CI hospedada, restore Azure e aceite continuam pendentes.


07/10/2026. Correção expressa do usuário: manter o banco pago sustentando os projetos por enquanto, preservar dados e conexões existentes e não exigir integração entre os projetos.

Destino mantido: **sqldb-crm-casst-dev-v2**, SQL Azure existente, plano Basic. Não transferir os projetos para o banco gratuito `sqldb-crm-casst-dev`, não criar outro banco e não mudar SKU por esta decisão.

Cada aplicação permanece independente, com seus links, usuários e regras de acesso. Compartilhar o banco não exige conectar as aplicações entre si, sincronizar seus dados, unificar logins ou misturar registros. Preservar configurações de conexão dos sistemas já publicados; nenhum ajuste nelas foi realizado por esta decisão.

A inspeção de 07/10 confirmou estruturas dos projetos nos schemas `dbo`, `crp`, `ebt_site`, `thaiane` e `ebt_connect`. Isso comprova a presença das estruturas, sem substituir a verificação de conexão/fluxo de cada aplicação. A aplicação de oito migrations do Connect preservou o catálogo dos outros schemas.

Somente a aplicação nova Connect precisará de sua configuração interna de acesso ao mesmo banco quando houver hospedagem aprovada disponível. Essa configuração cabe à implantação; não exige que o usuário conecte os projetos entre si. A identidade própria proposta limita as permissões do Connect, mantendo o mesmo banco.

Dados, tabelas, identidades e conexões dos outros produtos ficam preservados. Qualquer migração, unificação de aplicações/login ou integração entre projetos exige escopo próprio. Capacidade de armazenamento observada não é prova de carga/desempenho conjunto.

Estado: banco compartilhado ativo e schema Connect aplicado; aplicação Connect ainda não publicada por cota F1 zero e limite de gasto adicional somente R$ 30 fixos. [Registro de publicação](../../evidencias/azure_connect_publicacao.json) e [guia de retomada](../../PASSO_A_PASSO_PUBLICACAO_CONNECT.md).
