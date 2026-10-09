# Outlook no Connect: configuração e prova

Situação de 09/10/2026: código da fila e confirmação automática implementados; o servidor Connect ainda não possui configuração Mail. Rascunhos e modelos funcionam sem a Microsoft. Nenhum envio externo foi executado nesta revisão.

## Vínculo exclusivo

O servidor aceita uma caixa Microsoft explicitamente vinculada a um tenant da EBT. As chaves de configuração são `Mail__PlatformTenantId`, `Mail__MicrosoftTenantId`, `Mail__ClientId`, `Mail__ClientSecret`, `Mail__Sender` e `Mail__Enabled`. GUIDs devem identificar o vínculo correto; Sender deve ser a caixa autorizada. ClientSecret permanece em secret do Azure, referenciado pelo ambiente, sem arquivo versionado, log ou frontend. Não reutilizar credenciais de CASST ou do app-mail histórico.

O cliente usa client_credentials e o recurso Microsoft Graph, sem redirecionamentos ou repetição HTTP automática. Permissão delegada de uma sessão Outlook antiga não demonstra autorização app-only. A administração Microsoft deve confirmar a autorização de envio e restringir o aplicativo à caixa pretendida. O [RBAC de aplicações Exchange](https://learn.microsoft.com/en-us/exchange/permissions-exo/application-rbac) permite limitar recursos; permissões amplas concedidas separadamente no Entra podem ampliar o acesso e precisam ser conferidas. Este documento não executa concessão de permissões.

## Validação para ativação

1. Confirmar caixa existente, tenant EBT e aplicativo correto, com autorização restrita à caixa. Não contratar caixa/plano nesta etapa.
2. Configurar secrets/ambiente no host existente, preservando identidade SQL, proteção de sessão e os outros canais. Inicialmente manter a fila pausada.
3. Conferir `/api/connect/v1/mail/status` autenticado: vínculo correto e configuração reconhecida. `configured=true` indica parâmetros presentes; não comprova consentimento, mailbox ou envio.
4. Com destinatário de teste explicitamente autorizado, preparar/revisar/aprovar uma mensagem sem anexo, limite diário pequeno e intervalo definido. Só então solicitar envio e conferir o retorno e a mensagem na caixa de teste. Esta revisão não autoriza campanha para clientes.
5. Verificar uma única interação automática no CRM, quota, conteúdo exato, rastreabilidade da operação e ausência de repetição. Um retorno [Graph 202](https://learn.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0#response) representa aceite, sem prova de entrega/leitura.
6. Anexo exige versão aprovada e inspeção autorizada. Com scanner Azure pendente, não contornar esse bloqueio.

Timeout/reinício/resultado incerto pausam a fila e exigem conferência antes de reconciliar. A integração atual não lê automaticamente Itens Enviados nem sincroniza calendário. Exportação ICS é importação manual. Leitura de caixa/calendário requer contrato e permissões próprios; não acrescentar Mail.Read/Calendars.ReadWrite apenas para enviar.
