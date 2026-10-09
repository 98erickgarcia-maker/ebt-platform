# Retomada EBT Enterprise - revisao vigente de 09/10/2026

**Estado vigente de 09/10/2026:** Connect 0.3.0 publicado, fonte `bde34225781702f08158f9d832956c4ec326b469`, revisão `ebt-connect-hml--connect030-bde3422`. Qualificação, cliente ativo, templates e e-mail/fila em SQL. CI aprovado e 34 checks HTTP online + navegador desktop/mobile. Microsoft real ainda pendente. Leia `PASSO_A_PASSO_CONNECT_PROSPECCAO_MAIL.md` e `evidencias/connect_commercial_online_20261009.json` no checkout revisado. Referências anteriores a 0.2.0 abaixo são históricas.

A versao revisada esta em `.worktrees/revisao-github-20261008`. Preserve a arvore original e suas alteracoes; nao publique suas fontes por cima do snapshot revisado.

EBT Platform 0.2.0 esta online: https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io

O pedido explicito de criar a area exclusiva no banco compartilhado e colocar online autorizou esta publicacao. Schema `ebt_platform` aditivo, Connect em `ebt_connect`, demais schemas e plano do banco preservados. Connect disponivel; oito aplicativos futuros explicitamente planejados.

Fonte publicada: `18a454c725478819ab79a3f032e4321ca0e74d76`; revisao Azure `ebt-connect-hml--platform020-18a454c`. Provas em `evidencias/platform_online_20261009.json` e `evidencias/platform_azure_apply_20261009.json` no checkout revisado.

GitHub: https://github.com/98erickgarcia-maker/ebt-platform/tree/codex/ebt-enterprise-continuity-reviewed-20261008

O SHA do checkpoint mais recente fica em `tmp/continuidade/ultimo_checkpoint.json` do checkout revisado. Verifique o SHA remoto. O checkpoint documental pode ser posterior ao SHA usado para compilar a imagem.

Leia `PASSO_A_PASSO_EBT_PLATFORM.md`, `docs/qualidade/REVISAO_GITHUB_INCREMENTAL_20261008.md`, `planejamento/estado_continuidade.json` e `prompts/RETOMAR_EBT_ENTERPRISE.md` nesse checkout. Pacote revisado: `tmp/continuidade/EBT_ENTERPRISE_CONTINUIDADE.zip`, sem runtime privado/dados de clientes.

Enterprise continua a familia completa, Platform a fundacao e Connect o primeiro produto. Orcamento 180h + 20h preservado; sem horas ficticias ou promocao global dos gates. Scanner real, restore Azure isolado e aceite operacional continuam com prova propria. O envio WazVox real demonstrado na 0.1.5 e historico, nao foi reexecutado nesta publicacao.

No ChatGPT normal, abrir o prompt de retomada com acesso efetivo ao GitHub ou anexar o ZIP. Nao ha transferencia automatica de sessao/creditos. No Codex, continuar com as ferramentas disponiveis.

Apos incremento autorizado: revisar diff/caminhos/segredos, atualizar estado e executar `python scripts/checkpoint_github.py --approve --push` no checkout revisado. O agendador usa somente `--push`, sem aprovar conteudo novo ou fazer deploy. Depende de Windows ligado, sessao e rede/GitHub; nao depende de creditos de IA para repetir snapshots revisados.
