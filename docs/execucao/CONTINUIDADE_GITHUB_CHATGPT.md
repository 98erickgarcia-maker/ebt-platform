# Continuidade EBT Enterprise: GitHub, Codex e ChatGPT normal

## Objetivo e contrato

Salvar cada incremento revisado no repositório autorizado e permitir retomada pela próxima sessão com acesso efetivo. Repositório: `98erickgarcia-maker/ebt-platform`. A branch de checkpoints está em `planejamento/continuidade_github.json`. Checkout e `main` permanecem preservados; o checkpoint usa índice temporário e referência própria.

Entradas: caminhos/hashes revisados, arquivos atuais, estado de continuidade, credencial Git existente e origem aprovada. Saídas: commit local, manifesto dentro do commit, confirmação de SHA remoto e recibo em `tmp/continuidade/ultimo_checkpoint.json`.

Condição implementada: **informar `saved_github` somente se arquivos permitidos estiverem revisados, passarem pelos controles, o push terminar e o SHA remoto corresponder ao commit**. Em falha, registrar impedimento, preservar o commit local disponível e repetir sem force push.

## Ao concluir um incremento

Revisar diff, testes pertinentes e atualizar estado; depois:

```powershell
python scripts/checkpoint_github.py --approve --push
```

`--approve` registra revisão dos bytes pelo operador/agente. Scanner permanece obrigatório. Agendador nunca usa essa flag. `--push` repete conteúdo revisado; `--dry-run` valida sem commit/push ou alteração do manifesto.

Hashes de texto usam LF, conforme a política Git do repositório, para funcionar em Windows/Linux. Binários permanecem intactos. Isso não reescreve a fonte local nem substitui o hash de um artefato de produto histórico: provas anteriores devem ser reconciliadas com sua própria versão/formato.

Novos arquivos entram explicitamente em `files` após revisão. Binários precisam de `binary_sha256` fixo, atualizado somente depois de conferir conteúdo. Arquivo previsto ausente interrompe o checkpoint sem apagar remoto por inferência. Exclusão definitiva exige mudança Git própria revisada; o checkpoint conserva arquivos herdados.

Recusar `.env` privado, chaves/certificados, banco/backup, `tmp/`, dependências/build, `entregas/` e links fora do workspace. Scanner procura padrões conhecidos de segredo e omite valores encontrados. Não identifica toda credencial/dado pessoal possível; revisão de conteúdo/caminhos permanece necessária.

## Agendamento sem consumir créditos

```powershell
powershell -NoProfile -File scripts/Register-CheckpointTask.ps1 -Mode Install
powershell -NoProfile -File scripts/Register-CheckpointTask.ps1 -Mode Status
powershell -NoProfile -File scripts/Register-CheckpointTask.ps1 -Mode Remove
```

A tarefa nativa Windows verifica a cada cinco minutos e repete o push de arquivos já revisados. Roda com usuário conectado, sem elevação/API/modelo, em janela oculta. Exige computador ligado, sessão, rede e autenticação Git válidas. Não trabalha no produto nem aprova conteúdo novo. Divergência de branch/remote interrompe envio. Log: `tmp/continuidade/agendador.log`; última falha fica separada do último envio bem-sucedido.

Afirmar agendamento ativo somente após observar instalação/execução. Não criar automação de IA para o salvamento, pois dependeria da capacidade que se pretende poupar.

## Retomar no projeto normal ChatGPT

1. Abrir o projeto EBT Enterprise escolhido pelo usuário e usar o [prompt de retomada](../../prompts/RETOMAR_EBT_ENTERPRISE.md). Não existe troca automática de sessão.
2. Usar o acesso/plugin GitHub disponível ou anexar `tmp/continuidade/EBT_ENTERPRISE_CONTINUIDADE.zip`, produzido pelo exportador. Link privado não comprova leitura.
3. Conferir branch/SHA, `continuidade/CHECKPOINT.json` e `planejamento/estado_continuidade.json`; ler instruções obrigatórias e diff desde a última prova.
4. Conferir ferramentas efetivas. Com escrita GitHub, confirmar commit remoto. Com leitura apenas, entregar patch sem alegar envio. Sem acesso, usar o pacote e declarar sua idade.
5. Continuar planejamento/revisão; implementar módulos somente com autorização específica vigente. Esta revisão cria continuidade, sem executar módulos futuros.
6. Se faltar a próxima prova, registrar `AGUARDANDO_CODEX_EXECUCAO`, `AGUARDANDO_CODEX_NAVEGADOR` ou impedimento correspondente. Continuar trabalho independente. Se já estiver no Codex, seguir com ferramentas disponíveis.

## Fim de capacidade e recuperação

O produto não conhece saldo do Codex nem controla sessões ChatGPT. Não foi confirmado executor capaz de detectar limite e transferir agente automaticamente. Checkpoints são preventivos: salvar por incremento e antes de interromper, sem esperar o último crédito.

Falha de push permite retomada por commit local/ZIP revisado, sem anunciar salvamento remoto. Conflito remoto exige ler e reconciliar; não usar reset/clean/force. Computador desligado não envia. Interrupção antes da revisão deixa mudanças posteriores ao checkpoint apenas no computador.

Projetos agrupam chats/arquivos/instruções; plugins oferecem ferramentas conforme plano, workspace e acesso. Fontes oficiais consultadas em 07/10/2026: [projetos e plugins](https://learn.chatgpt.com/docs/use-chatgpt), [limites de uso](https://learn.chatgpt.com/docs/pricing). Não estabelecem aqui transferência automática nem comprovam ferramentas na conversa normal do usuário.

## Verificação e rollback

Executar `python -m unittest discover -s tests -p test_checkpoint_github.py -v` e `python scripts/verificar_continuidade.py`. Os testes Git usam remote bare local e massa sintética. CI de produto, SQL/restore Azure, navegador e aceite são separados. Não implantar automaticamente a branch de checkpoint.

Remover o agendamento com `-Mode Remove` preserva código, commits e alterações. Retomar pelo SHA remoto confirmado. Incorporar em `main` exige diff/CI/reconciliação dos trabalhos paralelos; esta revisão não faz esse merge.
