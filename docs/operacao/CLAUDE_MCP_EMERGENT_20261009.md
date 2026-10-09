# Claude, MCP e credenciais Emergent, 09/10/2026

## Estado observado nesta versão

- VPS `177.153.38.72`, n8n 2.42.6 e Caddy 2.10.2 por digest. n8n escuta apenas em loopback; HTTPS público na porta 443 usa certificado Let's Encrypt do domínio `mcp.ebtenterprise.com.br`. `curl` externo sem desativar a verificação TLS confirmou `/healthz` HTTP 200, metadata OAuth e recurso MCP apontando para o mesmo HTTPS; `/mcp-server/http` sem token retorna HTTP 401. Ambos os containers estão `healthy`.
- Certificado do domínio válido até 07/01/2027; `certbot renew --cert-name mcp.ebtenterprise.com.br --dry-run` concluiu com sucesso. `ebt-mcp-cert-renew.timer` habilitado para verificar duas vezes ao dia; o deploy hook reinicia o proxy apenas quando um certificado é realmente renovado. A unidade de renovação terminou com `Result=success` e `ExecMainStatus=0`; renovação real futura ainda não foi observada.
- n8n MCP ativo. Na última tela autenticada, 0 workflows habilitados, 0 agentes expostos, 0 clientes conectados. URL pública para Claude.ai: `https://mcp.ebtenterprise.com.br/mcp-server/http`. Callback OAuth foi reduzido de qualquer URL para uma URL confiável: `https://claude.ai/api/mcp/auth_callback`, conforme documentação da Anthropic. Nenhuma concessão de acesso ao Claude foi feita.
- KingHost confirmou a inserção do registro A `mcp.ebtenterprise.com.br` para a VPS. Resolução pública e HTTPS pelo domínio foram comprovados; o domínio substituiu o IP na configuração do gateway e do n8n. DNS raiz/www e registros de e-mail foram preservados. O endereço HTTPS por IP deixou de ser servido pelo gateway.
- Duas credenciais Emergent distintas foram importadas no cofre cifrado do n8n. O export não descriptografado confirmou os IDs e nomes. Falta a proxy base URL da conta Emergent; plano, restrição de IP, saldo e autenticidade das chaves não foram testados. A credencial OpenAI anterior permanece pendente e a recebida em 09/10 continua sem teste pago. `allow_paid_api=false` no runner.
- Dez papéis sequenciais e timers da VPS permanecem ativos. Às 20h52 BRT, checkpoint do runner: `quota`, tarefa `FLOW-01`, lista `completed` vazia e `progress_at=null`; retomada permitida pelo cooldown às 23h57 BRT. Consulta SQLite somente leitura confirmou as execuções n8n 4, 5 e 6 com `success` às 20h15, 20h30 e 20h45 BRT. Isso comprova agendamento e acionamento da bridge, sem concluir programação nem aprovar um módulo.

## Economia de créditos e operação por comandos

A pedido do usuário, a automação de chat `ebt-agentes-e-vps-a-cada-15-minutos` foi pausada. Os timers Linux e o workflow n8n de 15 minutos continuam ativos. Consulta de serviços, leitura de checkpoint sanitizado, renovação TLS e acionamento da bridge são operações determinísticas, sem chamada de modelo. Os alertas automáticos neste chat ficam pausados; o estado sanitizado continua disponível na VPS. A programação pelo runner ainda depende da cota da conta Codex. APIs pagas continuam desabilitadas e não substituem a cota automaticamente.

SSH, Docker Compose, systemd, Certbot, SQLite em modo somente leitura e Git foram utilizados diretamente para configuração e verificação. O navegador foi limitado ao DNS autenticado e às telas de integração; a concessão OAuth ao Claude exige conferência no ato. Instalar o endpoint MCP não fornece um modelo Claude ao runner nem transfere créditos entre contas.

## Separação de permissões

Claude.ai alcança servidores MCP a partir da nuvem da Anthropic. Um túnel SSH no computador do usuário não serve como URL do conector. O n8n exige OAuth e permite escolher permissões por cliente. A autorização final do Claude deve ser conferida no ato, limitada ao escopo necessário. O workflow de controle da VPS não foi habilitado no MCP e as credenciais não foram ligadas a um fluxo de chamadas pagas.

O acesso público HTTPS expõe a tela de login do n8n. A API pública do n8n continua desativada e o cookie seguro está habilitado. O timer de renovação e o teste simulado passaram; a primeira renovação real futura ainda deve ser observada. Não expor o workflow privado de controle da VPS ao MCP por inferência.

## Referências primárias

- n8n MCP, OAuth, tokens e callback: https://docs.n8n.io/connect/connect-to-n8n-mcp-server/
- n8n URL de MCP separado: https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables/deployment/
- Anthropic, MCP remoto do Claude: https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp
- Anthropic, callback OAuth: https://support.anthropic.com/en/articles/11503834-building-custom-connectors-via-remote-mcp-servers
- Let's Encrypt, certificado de IP e Certbot: https://letsencrypt.org/2026/03/11/shorter-certs-certbot
- Emergent Universal LLM Key: https://help.emergent.sh/the-universal-llm-key

## Operação e rollback

Configuração versionada: `deployment/n8n/compose.yaml` e `deployment/mcp-gateway/`. Na VPS: `/opt/ebt-engineering/n8n`, `/opt/ebt-engineering/mcp-gateway`, `/etc/letsencrypt-ebt-mcp` e `/etc/systemd/system/ebt-mcp-cert-renew.*`. A composição original do n8n foi guardada como `compose.yaml.pre-ip-mcp-20261009`; a etapa intermediária por IP como `compose.yaml.pre-domain-20261009`. O gateway também preserva os arquivos `*.pre-domain-20261009`. Nenhuma chave ou certificado privado pertence ao GitHub.

Para interromper a exposição pública, executar `docker compose down` em `/opt/ebt-engineering/mcp-gateway`. Para voltar o n8n ao URL local, restaurar a composição anterior e executar `docker compose up -d --wait` no diretório n8n, preservando volume, banco e chave de cifra. Confirmar `/healthz`, execução agendada e o estado dos timers após qualquer rollback.
