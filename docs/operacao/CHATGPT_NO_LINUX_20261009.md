# ChatGPT normal no Chrome da VPS Linux

Em 09/10/2026 o usuário pediu navegador Linux com perfil persistente e autorizou trocar o Firefox por Chrome. Chrome foi instalado na VPS existente; a página inicial do ChatGPT foi observada na tela, sem autenticação. O comando manual abriu uma segunda aba na mesma janela, preservando o perfil. Nenhum prompt foi enviado. O perfil anterior do Firefox ficou preservado em `/var/lib/ebt-linux-chat`.

## Abrir no Linux

```bash
ebt-abrir-chat
ebt-abrir-chat --status
ebt-abrir-chat --url https://chatgpt.com/c/UUID-REAL
```

O último exemplo exige substituir o marcador pelo UUID da conversa. O script instalado em `/usr/local/bin/ebt-abrir-chat` vem de `scripts/ops/linux_chat.py`. Aceita somente HTTPS da página inicial de `chatgpt.com` ou conversas `/c/UUID`, sem credenciais, porta, query ou fragmento. Usa argumentos separados, sem shell. Inicia o container quando necessário e pede ao Chrome uma nova aba pelo perfil existente, sem forçar reinício da janela. Atualização posterior da configuração Compose ainda pode recriar o container: não executar durante um rascunho importante.

`--status` verifica processo Chrome, container e publicação exclusiva em loopback. `browser_open_requested` prova apenas a solicitação; login e conteúdo da página precisam de evidência visual. O script nunca lê cookies, copia tokens, envia prompts ou afirma autenticação. Os timers não acionam esse comando.

## Tela privada e autenticação

No computador com SSH autorizado, manter o túnel ativo:

```bash
ssh -NT -L 127.0.0.1:5800:127.0.0.1:5800 -o ExitOnForwardFailure=yes -o ServerAliveInterval=10 -o ServerAliveCountMax=6 root@177.153.38.72
```

Abrir `http://127.0.0.1:5800/vnc.html?autoconnect=1&resize=scale` no mesmo computador. A tela exibida pertence ao Chrome da VPS. Troca de rede pode derrubar SSH: refazer o túnel e abrir uma aba nova. Não desabilitar a validação da chave SSH.

Entrar na conta diretamente nessa tela. A autenticação web não é transferida automaticamente da conta Codex nem do navegador Windows. O perfil mantém a sessão enquanto o provedor a considerar válida; nova autenticação pode ser exigida. Não enviar senha ou código de confirmação no chat. Login no ChatGPT não remove automaticamente o bloqueio do runner nem dá escrita GitHub ao navegador.

## Configuração e limites

- Imagem SeleniumHQ `selenium/standalone-chrome`, fixada em `sha256:7efe71e7e4a83bdf574b26bd354690928075e8f443223d2ced16a2c208eae1d7`.
- Compose `/opt/ebt-engineering/linux-chat/compose.yaml`; container `ebt-linux-chat`; perfil Chrome exclusivo `/var/lib/ebt-linux-chat-chrome`, proprietário UID 1200, diretório 0700. Conta local sem login `ebt-chrome`; processo no container UID/GID 1200:1201.
- noVNC 7900 publicado apenas como `127.0.0.1:5800`. Portas VNC 5900, X11 e WebDriver não são publicadas. Supervisor exclusivo inicia Xvfb, VNC, noVNC e Chrome; Selenium Grid, gravação e WebDriver não são iniciados. Incremento posterior habilitou CDP 9222 exclusivamente dentro do container para o painel de aprovação humana, sem publicar essa porta. Node e auxiliar fixo montados somente leitura; nenhum cookie/token é lido pelo auxiliar. Ver `deployment/manual-chat/LEIA_PRIMEIRO.md` para o fluxo autorizado de uma mensagem por aprovação humana.
- Limites 2 GiB RAM, 1,5 CPU, 1024 processos/threads e memória compartilhada de até 2 GiB dentro do limite do container. Uso observado após abertura: aproximadamente 577 MiB; VPS tinha cerca de 2,4 GiB disponíveis naquele instante.
- Processo sem root, sem capabilities, `no-new-privileges`; sem modo privilegiado e sem volumes de SSH, Git, Docker socket, modelos ou n8n. A imagem Selenium inicia Chrome com `--no-sandbox`; a proteção interna do Chrome fica reduzida, com isolamento mantido pelo container e acesso via SSH. Não adicionar credenciais de infraestrutura ao navegador.
- Healthcheck combina HTTP da tela com processo Chrome. Isso não prova autenticação. Verificação visual confirmou o ChatGPT carregado, inclusive a aba aberta pelo comando manual.

## Agentes e verificação

O runner foi acionado manualmente às 21h31 de Brasília em 09/10/2026 e terminou com sucesso operacional, respeitando cooldown. Checkpoint continuava `quota`, tarefa `FLOW-01`, lista `completed` vazia, próxima tentativa prevista para 23h57m48. Esse horário é uma tentativa agendada, não prova de liberação da cota. Dez papéis seguem configurados com concorrência um. Runner/watch timers e bridge estavam ativos; n8n e gateway continuaram rodando. Não contar navegador ou monitor como programação concluída.

Testes: `python -m unittest discover -s tests/ops -p test_linux_chat.py -v` — quatro testes passaram: restrição de URL, recusa de publicação pública/portas extras, ausência de alegação de login/envio e rejeição antes de iniciar processos. Compose validado, container saudável, comando manual e tela verificados. Configurações anteriores foram copiadas com sufixo `.before-*` na VPS antes da substituição. Não há custo/plano novo, chamada de API de modelo ou promoção de gates de produto neste incremento. Orçamento permanece 180h + 20h.

Para parar somente o navegador: `docker compose -f /opt/ebt-engineering/linux-chat/compose.yaml stop`. Preservar ambos os perfis privados; não copiar para Git/ZIP. Encerrar o túnel com Ctrl+C. Runner, watcher, gateway e n8n são serviços separados.

Referências: [SeleniumHQ Docker e noVNC](https://github.com/SeleniumHQ/docker-selenium), [autenticação ChatGPT/Codex](https://learn.chatgpt.com/docs/auth).
