# Docker, n8n, modelos e GitHub EBT

n8n 2.42.6 instalado na VPS com imagem oficial fixada por digest. Painel e bridge escutam somente loopback. Volume exclusivo, limite de768MB/128processos, sem Docker socket, chave GitHub ou perfil Codex montados no container. Servicos comerciais e DNS preservados.

Workflow EbtEngineering15min01 publicado: ManualTrigger e ScheduleTrigger15min solicitam POST na bridge privada. Credencial de cabecalho exclusiva cifrada pelo n8n, sem exportacao ao GitHub. A bridge aceita somente endpoints fixos e corpo vazio, limita repeticoes e retorna estado sanitizado. Solicita apenas watcher/runner via systemctl sem shell. Durante cooldown somente watcher; timers systemd permanecem fallback e o lock evita sobreposicao.

57 testes locais passaram. Executar workflow pela CLI do n8n passou ao vivo: quota, runnerQueuedfalse, observerQueuedtrue. Export publicado confirmado. Esta prova nao demonstra a primeira execucao automatica agendada nem chamada real de IA durante a cota. Python task runner do n8n nao esta instalado; este fluxo nao usa node Python.

## Credenciais de modelos (09/10/2026)

Painel privado: http://localhost:5678, com tunel SSH ativo neste computador. Para reabrir o tunel:

```powershell
ssh -N -L 127.0.0.1:5678:127.0.0.1:5678 -o ExitOnForwardFailure=yes root@177.153.38.72
```

No painel, abra Credentials. A lista atualmente contem:

| Entrada | Estado comprovado | Proximo requisito |
|---|---|---|
| OpenAI EBT - chave recebida 09-10 | Chave fornecida pelo usuario importada no cofre cifrado do n8n; exportacao sem decriptar confirmou o registro. Nenhuma chamada de API foi feita. | Rotacionar a chave exposta em conversa, substituir no cofre e testar autenticacao sob limite de gasto definido. |
| OpenAI anterior - chave pendente | Cadastro vazio. Nenhuma chave anterior foi encontrada nas fontes locais examinadas ou no n8n. | Inserir a chave anterior, se ainda for desejada e valida. |
| Emergent Universal - chave e endpoint pendentes | Cadastro Header Auth vazio. | Obter a Universal API Key e a proxy base URL em Account Settings -> Universal API Key do Emergent; validar plano e IP de origem antes de testar. |

O painel e privado via tunel SSH. Nao colocar chave em commit, screenshot ou arquivo publico. A chave ja exposta em conversa deve ser revogada apos substituicao. O Emergent documenta que acesso ao proxy externo e restrito por plano/IP: https://help.emergent.sh/the-universal-llm-key .

Estas credenciais ainda nao estao vinculadas aos modelos do runner. O runner usa a conta Codex e continua com allow_paid_apifalse. Para utilizar API na programacao, definir modelo/limite de gasto e revisar a integracao. Nenhuma chamada paga foi iniciada. Faturamento API e separado do ChatGPT.

EasyPanel/Traefik nao foram instalados neste recorte. Publicar painel futuramente exige dominio/HTTPS/acesso. Rollback: parar o container n8n; timers originais continuam. Preservar volume e chave de cifragem. Orçamento180h entregas+20h reserva permanece; nao implica aceite do usuario nem Enterprise completa.
