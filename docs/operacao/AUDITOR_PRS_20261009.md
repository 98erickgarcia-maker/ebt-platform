# Auditor de PRs — 09/10/2026

## Entrega

`scripts/ops/pr_audit.py` coleta metadados de PRs abertos, refs/SHAs, workflows de pull_request, revisões e nomes de arquivos. Identifica sobreposição de arquivos, não conflitos ou duplicações comprovados. Somente GET; nenhum merge, deploy, escrita remota, envio, SQL, acesso à VPS ou API de IA.

Os repositórios permitidos são ebt-platform, app-mail, grupo-vikings-sst, site-nutricao e crm-casst-web do proprietário 98erickgarcia-maker. Código, marcas e dados desses produtos continuam separados.

## Reprodução

Python 3.10 ou superior, biblioteca padrão; não há instalação de dependências.

```sh
python -m unittest discover -s tests/ops -p test_pr_audit.py -v
python -m py_compile scripts/ops/pr_audit.py tests/ops/test_pr_audit.py
python scripts/ops/pr_audit.py --repo ebt-platform --output pr-audit.json
```

Para os cinco repositórios, omitir `--repo`. Uma credencial de leitura pode ser fornecida por `GH_TOKEN` no ambiente seguro; nunca no código, relatório ou linha de comando. Sem autenticação, a cota pública pode ser insuficiente. O programa não contorna quotas nem repete requisições automaticamente. Uma rodada completa pode requerer várias requisições por PR; prefira o repositório específico.

Saída 0 significa **coleta completa nos limites descritos**, não aprovação dos PRs. Saída 2 é coleta parcial/instável; saída 3 é falha ao gravar a saída. Paginação limitada a 1.000 registros por coleção, com erro explícito se a coleção ultrapassar o limite. O JSON usa gravação atômica; falha antes da substituição preserva o relatório anterior.

## Interpretação

- `NOT_RUN`: nenhum workflow de evento pull_request retornado para esse SHA; não afirma ausência de todos os outros tipos de CI.
- `FAIL`, `WAITING_CI`, `NOT_PROVEN`, `MISSING_REQUIRED_WORKFLOW`: não promover para pronto.
- `PASS_CONFIGURED_CI`: os IDs de workflow explicitamente configurados e os demais observados passaram. A tabela REQUIRED cobre somente PRs EBT 13/15/16/20/21/22, conforme inspeção desta data; não representa rulesets do GitHub.
- `OBSERVED_CI_SUCCESS`: somente os workflows encontrados passaram, sem garantia de cobertura completa.
- `HEAD_OR_BASE_MOVED`: descartar a decisão e recolher nova evidência.
- `APPROVAL_OBSERVED_THREADS_NOT_CHECKED`: aprovação de outra conta no SHA observado; não substitui conferência de threads, autorização ou aceite operacional.

O inventário também retorna até 100 execuções schedule recentes do ebt-platform. Uma única execução, ou uma reexecução do mesmo ID, não prova recorrência. O auditor não instala cron nem corrige o monitor.

## Limites obrigatórios

Não revisa diffs automaticamente; não cobre check-runs externos, commit statuses, rulesets, threads de revisão, produção, interface visual, integração real com provedores ou critérios de negócio. Workflows que testam commits de merge precisam ter sua base efetiva reconferida. Metadados são um snapshot não transacional: nova revisão, nova execução ou mudança posterior exige revalidação mesmo sem alteração do HEAD.

A CI deste PR executa apenas testes offline. O job de coleta real só pode executar por workflow_dispatch na main após integração autorizada. Criar o PR não ativa uma rotina contínua. A tarefa nativa de engenharia continua sendo separada e deve usar os conectores disponíveis.

## Verificação realizada

Primeira rodada local: 29 testes passaram. Revisão de qualidade detectou a necessidade de tratar schema inválido como resultado parcial e validar números de PR antes da consulta; segunda rodada: 31 testes passaram. Um teste executa 1.000 cenários sintéticos determinísticos, variando SHA, workflows exigidos, falhas, cancelamento, espera, skip e reexecuções. Não são 1.000 revisões integrais dos produtos.

A consulta real aos projetos foi realizada pelo conector GitHub, não pelo cliente HTTP deste script: a rede do ambiente local estava indisponível. Aprovação de CI hospedada deve ser conferida no SHA candidato, sem inferir sucesso pelo teste local.

## Critério para continuar

Ler a fila de engenharia e PRs atuais, escolher somente um incremento com dependências satisfeitas, reproduzir o defeito, testar, rever funcionalidade e segurança, publicar draft e verificar o SHA remoto. Não repetir mil vezes uma suíte idêntica para inflar evidência. Parar o recorte se houver credencial/aceite ausente ou risco de produção; avançar somente para outro recorte independente autorizado.
