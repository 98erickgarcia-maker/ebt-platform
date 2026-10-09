# EBT Enterprise - supervisao 24x7

**Escopo:** EBT Platform / EBT Connect; sem alterar o produto publicado.

## Agentes implementados

1. **Disponibilidade**: sondas HTTP /health/live e /health/ready com status, contrato JSON e versao.
2. **Releases**: compara as versoes dos endpoints de disponibilidade.
3. **Seguranca**: prova negativa basica, exigindo 401/403 de endpoints privados sem sessao.
4. **Frontend**: valida entrada HTML React e existencia de bundles JS/CSS no mesmo host.
5. **Incidentes**: abre/atualiza uma unica issue do bot com estado/sintomas; fecha apenas a propria issue quando as sondas voltam a passar.
6. **Qualidade**: testes de regressao (sem rede, massa sintetica) cobrem erros, abuso de URLs, permissao anonima, vazamento e estado do incidente.
7. **Evidencias**: salva JSON com horario, tentativas, HTTP e versao (sem corpos de resposta, contatos, segredos ou tokens).

Estes executores sao Python deterministico e GitHub Actions, nao modelos de IA gastando tokens permanentemente.

## Agendamento e limitacoes

- Frequencia configurada: **a cada 15 minutos, dia e noite** (minutos 07, 22, 37 e 52 UTC).
- GitHub Actions scheduled workflows executam **somente na branch padrao**. Este PR precisa ser revisado e integrado a main antes de haver agendamento.
- O GitHub pode atrasar/dispensar execucoes em periodos de sobrecarga e suspender cron em repositorios publicos inativos. Nao representa disponibilidade garantida de 100%.
- Publicacao/alerta em Issues so fica habilitado na main, com permissao issues:write e autoria do bot. Alteracoes locais nao enviam alertas.
- A execucao tem uma segunda tentativa curta; ausencia de rede/HTTP 429 vira INCONCLUSIVE. Nao executar reinicios cegos ou reenvios automaticos.
- Nao ha credencial Azure no monitor; ele NAO executa deploy, migration SQL, comandos administrativos, acessos autenticados, contatos, Outlook ou WhatsApp.
- A verificacao de acesso anonimo NAO demonstra isolamento de dados entre tenants, nem auditoria de todas as rotas.

## Execucao reproduzivel

Rodar na raiz do repositorio:

    python -m unittest discover -s tests/ops -v
    python scripts/ops/production_watch.py --output production-watch.json

CI: .github/workflows/ebt-production-watch.yml. Na branch operacional, o push executa QA e sondas sem notificacao. Em pull_request, apenas QA. Quando estiver em main, o cron e as notificacoes passam a operar.

## Fonte e fronteiras

- Repositorio: https://github.com/98erickgarcia-maker/ebt-platform
- Branch de runtime analisada: codex/ebt-enterprise-continuity-reviewed-20261008 @ 0177b5cad13a3003de5f240d7bea432cba825e47.
- Guia de publicacao Connect 0.3.0 indica fonte bde34225781702f08158f9d832956c4ec326b469.
- Host monitorado: https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io
- A main atual do repositorio tem sobretudo documentos e planejamento, nao o runtime completo. Esta implementacao e aditiva e independe da mesclagem de branches de runtime.
- O nome do host inclui hml; ter ASPNETCORE_ENVIRONMENT=Production nao substitui homologacao operacional. Confirmar na Azure antes de declaracoes de producao final.

## Ativacao segura

1. Revisar o diff deste PR e os resultados da suite.
2. Integrar somente arquivos de ops em main; NAO integrar automaticamente PRs anteriores.
3. Executar workflow_dispatch e conferir artefato JSON e permissionamento das issues.
4. Conferir uma execucao cron real posterior; confirmar que a conta recebe notificacoes do GitHub.
5. Para observabilidade completa, configurar alertas Azure Monitor e testes autenticos com contas sinteticas restritas em ambiente separado.
6. Para agentes de desenvolvimento autonomos 24x7, projetar uma segunda esteira com runners dedicados, orcamento/limites, PRs isolados, revisao e deploy controlado. Nao autorizar merge/deploy automatico com base apenas em um monitor de disponibilidade.

**Rollback:** desabilitar apenas o workflow no GitHub Actions. Nenhuma alteracao no Azure ou banco foi introduzida.

## Verificacao versus hipotese

Um arquivo agendado no GitHub nao e prova de que o schedule ja disparou. Testes de unidade nao sao verificacao de rede. Uma issue nao garante entrega push/e-mail. Registro de publicacao anterior nao substitui health e aceite atuais.
