# Docker, n8n, modelos e GitHub EBT

n8n 2.42.6 instalado na VPS com imagem oficial fixada por digest. Painel e bridge escutam somente loopback. Volume exclusivo, limite de768MB/128processos, sem Docker socket, chave GitHub ou perfil Codex montados no container. Servicos comerciais e DNS preservados.

Workflow EbtEngineering15min01 publicado: ManualTrigger e ScheduleTrigger15min solicitam POST na bridge privada. Credencial de cabecalho exclusiva cifrada pelo n8n, sem exportacao ao GitHub. A bridge aceita somente endpoints fixos e corpo vazio, limita repeticoes e retorna estado sanitizado. Solicita apenas watcher/runner via systemctl sem shell. Durante cooldown somente watcher; timers systemd permanecem fallback e o lock evita sobreposicao.

57 testes locais passaram. Executar workflow pela CLI do n8n passou ao vivo: quota, runnerQueuedfalse, observerQueuedtrue. Export publicado confirmado. Esta prova nao demonstra a primeira execucao automatica agendada nem chamada real de IA durante a cota. Python task runner do n8n nao esta instalado; este fluxo nao usa node Python.

## Cadastrar API OpenAI

Painel privado: http://localhost:5678, com tunel SSH ativo neste computador. Para reabrir o tunel:

```powershell
ssh -N -L 127.0.0.1:5678:127.0.0.1:5678 -o ExitOnForwardFailure=yes root@177.153.38.72
```

Na primeira visita crie sua conta owner e defina sua senha. Depois abra Credentials -> OpenAI EBT - inserir chave -> API Key -> Save. A credencial foi criada vazia com Base URL oficial https://api.openai.com/v1. Nao colocar chave em chat, commit, screenshot ou arquivo publico.

Esta credencial ainda nao esta vinculada aos modelos do runner. O runner usa a conta Codex e continua com allow_paid_apifalse. Para utilizar API na programacao, definir modelo/limite de gasto e revisar a integracao. Nenhuma chamada paga foi iniciada. Faturamento API e separado do ChatGPT.

EasyPanel/Traefik nao foram instalados neste recorte. Publicar painel futuramente exige dominio/HTTPS/acesso. Rollback: parar o container n8n; timers originais continuam. Preservar volume e chave de cifragem. Orçamento180h entregas+20h reserva permanece; nao implica aceite do usuario nem Enterprise completa.
