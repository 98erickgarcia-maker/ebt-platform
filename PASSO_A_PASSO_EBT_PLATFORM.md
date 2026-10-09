# EBT Platform online - 09/10/2026

Abra [EBT Platform](https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io), entre com seu acesso existente e escolha **Acessar Connect**. A entrada agora mostra Aplicativos; o Connect conserva relacionamentos, tarefas, conversas, documentos e configuracoes. Em celular, o menu fica no botao do canto superior. Para voltar ao catalogo, escolha Aplicativos.

EBT Enterprise e a familia; EBT Platform e a fundacao comum. Connect esta disponivel. Flow, Portal, Sites, Contracts, SST, Legislativo, Educacao e Saude aparecem como planejados, sem simular modulos funcionais.

## Publicacao e provas

- Versao 0.2.0, fonte [18a454c](https://github.com/98erickgarcia-maker/ebt-platform/commit/18a454c725478819ab79a3f032e4321ca0e74d76).
- Revisao Azure `ebt-connect-hml--platform020-18a454c`, saudavel e recebendo o trafego no modo Single.
- Imagem `acrcrmcasstprod2608.azurecr.io/ebt-platform@sha256:3cbba51b9440fff7f042f650d8396dd6a9eca218cf2c37d115450f39ed9d6ad1`, compilada do pacote revisado, sem runtime privado.
- [Prova online](evidencias/platform_online_20261009.json): 26 checks HTTP, navegador desktop/mobile, sessao anterior aceita e IDs dos contatos consultados preservados. Telas privadas inspecionadas; nenhum novo envio ou cadastro de cliente.
- [Prova SQL Azure](evidencias/platform_azure_apply_20261009.json): catalogo aditivo `ebt_platform` no banco existente `sqldb-crm-casst-dev-v2`. Estruturas e contagens das outras 110 tabelas permaneceram iguais. Isso nao e comparacao completa do conteudo de todas as linhas.
- Identidade da aplicacao le somente o catalogo da Platform; nao recebeu escrita/DDL ou acesso aos schemas de outros produtos. Connect continua em `ebt_connect`, sem mover dados ou trocar IDs.
- QA local: 19/19 navegador, 8/8 catalogo SQL/HTTP, 27/27 regressao Connect; SQL aplicado duas vezes sem duplicatas. Build e continuidade GitHub aprovados para a fonte publicada.

O loop HTTPS anterior foi corrigido incluindo apenas os dois peers internos observados na lista explicita de proxies, com IPv4 e mapeamentos IPv6. A observacao protegida foi desativada. Firewall temporario SQL removido. Plano do banco, identidade, segredos, keyring, ingress, escala e recursos foram preservados.

## Continuidade

Use o checkout `.worktrees/revisao-github-20261008`, a branch `codex/ebt-enterprise-continuity-reviewed-20261008` e [o prompt de retomada](prompts/RETOMAR_EBT_ENTERPRISE.md). Revise antes de salvar:

```powershell
python scripts/checkpoint_github.py --approve --push
python scripts/exportar_continuidade.py
```

Confirme o SHA remoto e o recibo `tmp/continuidade/ultimo_checkpoint.json`. O pacote `tmp/continuidade/EBT_ENTERPRISE_CONTINUIDADE.zip` contem apenas bytes revisados. O agendador repete `--push`; recusa conteudo novo sem revisao e depende do computador/sessao/rede. No ChatGPT normal, forneca acesso efetivo ao GitHub ou anexe o ZIP. Nao existe transferencia automatica de sessao/creditos.

## Retorno e limites

Configuracao anterior esta em `tmp/platform-release/app-before.private.json`, fora do Git/ZIP. Se for necessario retornar o codigo, mantenha a configuracao atual de proxy corrigida e publique a imagem anterior com um sufixo novo:

```powershell
az containerapp update --resource-group rg-crm-casst-prod --name ebt-connect-hml --image acrcrmcasstprod2608.azurecr.io/ebt-connect@sha256:1f8deb8c1fb948441c3f56942be16137d724535ed521ad62ec97f171f32af815 --revision-suffix rollback-015-20261009
```

Confirme latestReady, HTTPS, login e leitura depois do retorno. A area SQL aditiva pode permanecer; nao apagar catalogo nem restaurar/excluir o banco para voltar a imagem. Nao reativar r015 sem a configuracao corrigida de proxies, pois o loop HTTPS foi observado nessa configuracao antiga.

Os peers do ingresso Azure podem mudar: se houver novo loop, observar os peers com a rota temporaria protegida, revisar enderecos exatos e remover a observacao depois. Nao habilitar confianca universal em headers.

O envio real WazVox da 0.1.5 e evidencia historica. Scanner privado real, restore Azure isolado e aceite operacional permanecem pendentes; documentos sem resultado clean nao sao liberados em producao. Publicacao deste recorte nao conclui todos os modulos/gates Enterprise. Orcamento preservado em 180h de entregas + 20h de reserva, sem consumo ficticio.
