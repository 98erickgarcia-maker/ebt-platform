# Chat Linux: painel manual e CONTINUE a cada 15 minutos

Pedido explícito posterior do usuário em 09/10/2026: repetir CONTINUE onde ele pediu continuação, a cada 15 minutos. A rotina fixa foi configurada na conversa **Verificar tarefas do GitHub** do Chrome Linux. O endereço da conversa e a sessão ficam privados na VPS, fora do pacote e do checkpoint GitHub. Outros prompts continuam exigindo aprovação individual no painel.

## Evidência desta revisão

- Painel loopback `127.0.0.1:5810` ativo; preparação do texto de teste observada na interface, checkbox desmarcado e envio desabilitado. Nenhum teste positivo de envio manual foi acionado.
- Chrome autenticado, conversa selecionada com Extra alto, sem rascunho, aviso de limite ou resposta em andamento na verificação. A sessão e as cotas podem mudar.
- `ebt-chat-continue.timer` ativo e aguardando, com `OnActiveSec=15min` e `OnUnitActiveSec=15min`, sem compensação de ciclos perdidos. Verificação do helper em serviço transitório com as proteções de systemd retornou `ready_dry_run`.
- Estado inicial `armed`, zero envios observados. Primeiro envio agendado ainda pendente na evidência desta revisão. Não confundir timer ativo, mensagem enviada, resposta concluída e tarefa de programação aprovada.
- Testes locais: 18 casos Python e 2 casos Node aprovados. Incluem autorização/destino fixos, intervalo persistente, resposta em andamento, limite/rascunho/sessão, tentativa incerta e mudança de destino.
- Timers anteriores do runner e watcher continuaram ativos. Não houve promoção de gates, mudança de dados de produto, deploy de módulos ou chamada de API de modelo nesta configuração.

## Comportamento e acesso

O script envia apenas CONTINUE à conversa configurada. Resposta em andamento pula o ciclo sem fila; limite, rascunho, perda de sessão/modelo ou erro pausam os envios até revisão manual. Antes de enviar, a tentativa é registrada; interrupção ou resultado incerto não provoca reenvio automático. Um lock também impede envio simultâneo pelo painel e pela rotina. A rotina não interpreta a resposta como programação concluída e não aprova publicação.

Abra `ABRIR_EBT_MANUAL.cmd` do pacote para o túnel privado. Para parar a rotina na VPS: `systemctl disable --now ebt-chat-continue.timer`. Retomada e instalação estão em `deployment/manual-chat/LEIA_PRIMEIRO.md`. Nenhuma chave, cookie ou perfil acompanha o ZIP. Os limites normais do ChatGPT continuam aplicáveis; não há recarga ou contratação automática. A operação desta rotina Linux não desperta o Codex.
