# EBT — painel com aprovação humana

Este pacote instala um painel privado na VPS EBT existente. Você escolhe uma conversa do ChatGPT do Chrome Linux, confere o texto e clica em **Aprovo este texto e autorizo enviar**. A VPS insere e clica em Enviar uma vez. A preparação e a colagem não chamam modelos nem dependem de um turno Codex. A resposta continua usando sua conta e os limites do ChatGPT. O painel não altera assinatura, cota ou normas dos provedores e não certifica conformidade.

## Acesso no Windows

Na pasta `deployment/manual-chat`, dê dois cliques em `ABRIR_EBT_MANUAL.cmd`. Requer OpenSSH e autenticação SSH previamente autorizada para a VPS `177.153.38.72`; nenhuma chave SSH está no ZIP. Mantenha o terminal aberto. O painel é `http://127.0.0.1:5810/`; a tela Chrome é `http://127.0.0.1:5801/vnc.html?autoconnect=1&resize=scale`. Se a página abrir antes da conexão, recarregue depois que o túnel estiver ativo. Portas já ocupadas exigem conferir o túnel existente, sem encerrar processos por inferência.

No Linux/macOS ou terminal Windows, alternativa:

```sh
ssh -NT -L 127.0.0.1:5810:127.0.0.1:5810 -L 127.0.0.1:5801:127.0.0.1:5800 -o ExitOnForwardFailure=yes -o ServerAliveInterval=10 -o ServerAliveCountMax=6 root@177.153.38.72
```

Não desabilite a validação da chave SSH. Troca de rede pode interromper o túnel; refaça o acesso. As portas não são públicas.

## Teste de fluxo

1. No Chrome Linux, autentique sua própria conta, abra uma conversa e selecione **Extra High**, se disponível. Preferencialmente use uma conversa exclusiva para o teste, sem rascunho e sem resposta em andamento.
2. No painel, **Atualizar chats** e selecionar a conversa exata. Mantenha **Teste da trava — sem alteração de projeto**.
3. Clique em **Preparar texto para revisão**. Essa etapa não envia mensagem. Confira o destino e o texto; marque a autorização e clique no botão verde apenas quando estiver de acordo.
4. O resultado **Mensagem observada no ChatGPT** comprova que a mensagem foi vista na conversa. A resposta esperada é `TRAVA MANUAL CONFIRMADA`. Confirme a resposta na tela. Sem essa observação, não declarar teste positivo ao vivo.
5. Para programação, selecione um dos dez papéis FLOW, confira suas dependências no GitHub e repita a revisão. Escolher um papel não conclui a tarefa nem promove um gate. O painel não aprova release ou faz deploy.

Se houver rascunho, resposta em andamento, aviso de limite do workspace, ausência de Extra High, conversa duplicada/fechada ou mudança de estado, a ação é bloqueada. Aprovação expira em cinco minutos e é consumida antes da execução. Resultado incerto nunca é repetido automaticamente: conferir a tela antes de preparar outra mensagem. Não coloque senhas, chaves de API ou dados de clientes nos prompts.

## CONTINUE a cada 15 minutos — autorização posterior de 09/10

O pedido posterior do usuário autoriza repetir apenas **CONTINUE**, a cada 900 segundos, no chat Linux identificado como **Verificar tarefas do GitHub**. A VPS usa `ebt-chat-continue.timer`, independentemente do Codex. O destino real fica em `/etc/ebt-continue-chat.json`, privado e excluído do ZIP/GitHub. Essa autorização da rotina fixa não aprova outros textos, novas conversas, releases, pagamentos ou envios externos. O painel mantém aprovação individual para os demais textos.

O timer começa 15 minutos após ser ativado. Resposta em andamento pula o ciclo, sem acumular mensagens. Limite, rascunho, perda da sessão/modelo ou erro interrompem os envios até revisão manual. Tentativa incerta nunca é reenviada automaticamente; a rotina não confirma conclusão de programação. Após reinício da VPS, o timer volta a contar 15 minutos e não compensa ciclos perdidos. Mensagens usam os limites normais da assinatura.

Verificação e interrupção no Linux:

```sh
systemctl status ebt-chat-continue.timer
cat /var/lib/ebt-chat-continue/state.json
systemctl disable --now ebt-chat-continue.timer
```

Para retomar após pausa: confira a conversa e eventuais rascunhos primeiro, execute `python3 /opt/ebt-engineering/manual-chat/continue_chat.py --resume`, e ative `systemctl enable --now ebt-chat-continue.timer`. `--resume` não envia imediatamente. Se houver um lock de navegador após encerramento inesperado, revise processos/conversa antes de qualquer remoção manual. A instalação do pacote não arma novos envios automaticamente.

## Instalação

Copie este pacote para um diretório temporário privado da VPS e extraia. A instalação é explícita; não é um script acionado pelo agendador. Requer Docker/Compose e o ambiente EBT já existente, Node 24 em `/opt/ebt-engineering/node/bin/node`, perfil Chrome privado, manifesto de dez papéis e checkpoint. O instalador recusa pré-requisitos ausentes e não cria credenciais nem substitui o manifesto. Na raiz extraída:

```sh
sh deployment/manual-chat/instalar-vps.sh
```

O instalador guarda configurações anteriores com `.before-manual-*` e reinicia apenas o navegador/painel. A sessão fica no perfil persistente; autenticação adicional pode ser exigida pelo provedor. Salve rascunhos antes de atualizar. Não executa runner, migrações, APIs de modelo ou deploy de produto. Orçamento de planejamento permanece 180h + 20h.

O servidor HTTP 5810 fica em loopback. O Chrome usa CDP 9222 somente dentro do container, sem publicar essa porta; o auxiliar não lê cookies, tokens, senhas ou respostas da IA. O serviço usa Docker para executar apenas um auxiliar fixo no container e precisa do acesso de manutenção existente da VPS. Não dar esse serviço a usuários não confiáveis. A interface exige origem local, JSON, prévia exata, aprovação única e rejeita rascunho/ocupação. A imagem Selenium inicia Chrome com `--no-sandbox`; o isolamento é o container sem root/capabilities e o acesso privado SSH. Não incluir credenciais de infraestrutura no navegador.

## Verificação e retorno

```sh
python3 -m unittest discover -s tests/ops -p 'test_*chat.py' -v
node --test tests/ops/test_insert_chat.mjs
systemctl is-active ebt-manual-chat.service
curl -fsS http://127.0.0.1:5810/healthz
```

Os testes locais são sintéticos; o teste positivo da conta depende da aprovação humana do texto exibido. Para parar somente o painel: `systemctl disable --now ebt-manual-chat.service`. Para remover o CDP, restaurar o `launch-chrome.sh` e o Compose do backup anterior e reiniciar somente o navegador. Preservar os perfis. Runner, n8n e watcher não dependem do painel e continuam sujeitos a suas próprias condições.

Confira `MANIFESTO_SHA256.json` contra os arquivos extraídos. O ZIP não contém chaves, senhas, cookies, perfil de navegador, dados de cliente ou banco. Não foi autorizada prospecção externa automática ou envio de WhatsApp/e-mail por este pacote.
