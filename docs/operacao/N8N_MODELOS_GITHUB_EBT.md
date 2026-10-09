# Docker, n8n, modelos e GitHub EBT

n8n 2.42.6 instalado na VPS com imagem oficial fixada por digest. Os listeners do n8n e da bridge escutam somente loopback; o painel n8n e o MCP são acessíveis pelo proxy HTTPS autenticado em `mcp.ebtenterprise.com.br`. Volume exclusivo, limite de 768 MB/128 processos, sem Docker socket, chave GitHub ou perfil Codex montados no container. Serviços comerciais e DNS preexistentes preservados.

Workflow EbtEngineering15min01 publicado: ManualTrigger e ScheduleTrigger15min solicitam POST na bridge privada. Credencial de cabecalho exclusiva cifrada pelo n8n, sem exportacao ao GitHub. A bridge aceita somente endpoints fixos e corpo vazio, limita repeticoes e retorna estado sanitizado. Solicita apenas watcher/runner via systemctl sem shell. Durante cooldown somente watcher; timers systemd permanecem fallback e o lock evita sobreposicao.

57 testes locais passaram. Executar workflow pela CLI do n8n passou ao vivo: quota, runnerQueuedfalse, observerQueuedtrue. Export publicado confirmado. Em 09/10, a interface registrou execucoes automaticas bem-sucedidas as 19h45 (ID2) e 20h00 (ID3), horario de Sao Paulo. Elas comprovam o agendamento e o acionamento da bridge, nao programacao concluida por IA durante a cota. Python task runner do n8n nao esta instalado; este fluxo nao usa node Python. Snapshot detalhado: [VERIFICACAO_AGENTES_MCP_20261009.md](VERIFICACAO_AGENTES_MCP_20261009.md).

## Credenciais de modelos (09/10/2026)

Painel HTTPS da VPS: https://mcp.ebtenterprise.com.br. O listener do n8n continua restrito a `127.0.0.1:5678` e o proxy termina TLS na porta 443. O túnel SSH permanece uma via de manutenção local; com `N8N_SECURE_COOKIE=true`, a autenticação do navegador deve usar HTTPS. Para inspecionar a porta local sem autenticar:

```powershell
ssh -N -L 127.0.0.1:5678:127.0.0.1:5678 -o ExitOnForwardFailure=yes root@177.153.38.72
```

No painel, abra Credentials. A lista atualmente contem:

| Entrada | Estado comprovado | Proximo requisito |
|---|---|---|
| OpenAI EBT - chave recebida 09-10 | Chave fornecida pelo usuario importada no cofre cifrado do n8n; exportacao sem decriptar confirmou o registro. Nenhuma chamada de API foi feita. | Rotacionar a chave exposta em conversa, substituir no cofre e testar autenticacao sob limite de gasto definido. |
| OpenAI anterior - chave pendente | Cadastro vazio. Nenhuma chave anterior foi encontrada nas fontes locais examinadas ou no n8n. | Inserir a chave anterior, se ainda for desejada e valida. |
| Emergent Universal 1 e 2 | Duas chaves distintas fornecidas em 09/10 importadas como credenciais Header Auth cifradas no n8n. Exportação sem descriptografar confirmou os dois registros; nenhuma chamada externa foi feita. | Obter a proxy base URL em Account Settings -> Universal API Key do Emergent; validar plano, IP de origem e limite de custo antes de testar ou usar no runner. |

Nao colocar chave em commit, screenshot ou arquivo publico. As chaves expostas em conversa devem ser revogadas apos substituicao. O Emergent documenta que acesso ao proxy externo e restrito por plano/IP: https://help.emergent.sh/the-universal-llm-key .

Estas credenciais ainda nao estao vinculadas aos modelos do runner. O runner usa a conta Codex e continua com allow_paid_apifalse. Para utilizar API na programacao, definir modelo/limite de gasto e revisar a integracao. Nenhuma chamada paga foi iniciada. Faturamento API e separado do ChatGPT.

EasyPanel/Traefik não foram instalados neste recorte. HTTPS usa Caddy fixado por digest e certificado público para `mcp.ebtenterprise.com.br`, com resolução DNS, smoke TLS, metadata OAuth e teste simulado de renovação aprovados. O MCP ainda exige autorização individual no Claude; URL pública e metadata válida não comprovam cliente conectado. Detalhes em [CLAUDE_MCP_EMERGENT_20261009.md](CLAUDE_MCP_EMERGENT_20261009.md). Rollback: parar o gateway; n8n e timers originais continuam. Preservar volume e chave de cifragem. Orçamento de 180h de entregas + 20h de reserva permanece; não implica aceite do usuário nem Enterprise completa.

Para economizar créditos, a supervisão continua nos timers Linux e no n8n a cada 15 minutos, sem chamadas de modelo para observar o estado. A checagem duplicada pela automação de IA neste chat foi pausada, incluindo seus avisos automáticos. O runner continua sujeito à cota da conta Codex; API paga permanece desabilitada. Administração e consultas passam prioritariamente por comandos SSH, evitando rodadas de navegador quando uma interface oficial de comando atende à operação.
