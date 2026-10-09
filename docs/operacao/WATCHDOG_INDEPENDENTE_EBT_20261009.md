# Supervisão independente de recorrência

Preparado para VPS; não instalado nem ativado. Usa somente biblioteca padrão Python 3.12, API GitHub GET e estado local. Não requer OpenAI, ChatGPT, banco ou credenciais de outros produtos.

## Operação prevista

`python3 scripts/ops/schedule_watchdog.py --state /var/lib/ebt-watch/state.json`

Para repositório privado, disponibilizar GH_TOKEN por provisionamento autorizado com leitura de Actions e issues; não colocar valor no repositório. Sem acesso, retorna CONNECTION_ERROR, nunca PASS. HTTP 401/403/404/429 são dependência de acesso/provedor; erros de payload ou persistência retornam MONITOR_ERROR. Mensagens de exceção e tokens não são registrados. Redirecionamentos são recusados.

Consulta até dez páginas de execuções de 100 itens para encontrar o último schedule da main. Ausência continua FAIL mesmo quando o limite de busca é atingido. Issues abertas são paginadas; paginação incompleta de issues é MONITOR_ERROR. Falhas/cancelamentos da main na janela consultada permanecem no relatório, mesmo após schedule posterior aprovado. Recuperação do último schedule não apaga essas falhas históricas.

PASS comprova apenas um schedule recente concluído com sucesso e ausência de falhas na janela. Não comprova recorrência sustentada, disponibilidade da aplicação ou homologação. Mais de 90 minutos, falta de schedule, resultado incompleto ou diferente de success são FAIL. Issues [EBT OPS] abertas são registradas separadamente; a lista new_incidents só inclui números ainda não vistos. Não cria, fecha nem envia incidentes. changed indica mudança de estado observado; sem alteração, os registros periódicos permanecem disponíveis no journal.

Estado JSON substituído atomicamente; preserva última observação válida em falha de conexão. Estado corrompido não é sobrescrito. Executar um único timer por arquivo de estado; chamadas manuais simultâneas com o timer não são suportadas. Códigos: 0 PASS, 2 FAIL, 3 CONNECTION_ERROR/MONITOR_ERROR.

## Preparação para Linux

Exemplos em templates/systemd/ebt-schedule-watchdog.service e .timer. O timer verifica a cada cinco minutos; systemd não inicia outra instância do mesmo oneshot enquanto ele estiver executando. Timeout de oito minutos comporta o limite de paginação e timeout HTTP de 20 segundos, sem alterar qualquer timeout do produto.

Antes de uma instalação autorizada, administrador deve criar usuário/grupo ebt-watch, disponibilizar checkout revisado em /opt/ebt-platform e configurar arquivo /etc/ebt-watch.env com permissões restritas. StateDirectory mantém o estado em /var/lib/ebt-watch com modo 0700; serviço usa ProtectSystem, ProtectHome e NoNewPrivileges. Validar units com systemd-analyze verify no Linux. Não foi executado nesta sessão Windows. Instalação/ativação e provisionamento de credencial são ações futuras separadas.

## Verificação

`python -m unittest discover -s tests/ops -v` usa transportes simulados para as notificações existentes e não executa o watchdog contra rede. Não chama deploy, restart, workflow_dispatch ou APIs de escrita. Workflow ebt-watchdog-tests.yml executa apenas esses testes e diff check em branch isolada.
