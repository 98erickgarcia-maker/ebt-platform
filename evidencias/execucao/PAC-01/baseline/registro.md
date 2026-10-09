# P01-01 / P01-02 — baseline técnica e classificação

Execução real em 09/10/2026, ambiente Windows local, checkout CASST `crm-casst-foundation`, HEAD `046e7c62359220aaf6ab30832f0fbff5b6f675f0`. Evidência produzida exclusivamente no projeto EBT PLATAFORM. Fonte consultada somente por leitura; sem build, suíte, migração, banco, deploy ou envio. Registro de tempo medido pelos metadados de criação: de 17:35:36.822320 UTC (script) a 17:38:31.336386 UTC (registro), 174.514 segundos / 0.04848h na janela de elaboração/captura. É limite inferior: leituras anteriores e verificação posterior não foram cronometradas, portanto o esforço integral não é afirmado como medido. Não representa consumo automático das 4h estimadas. Sem reserva consumida.

## P01-01

`manifesto-fonte.json`: 594 arquivos técnicos, incluindo 135 não rastreados do superset inicial `src/tests/workflows`; também manifests de dependências presentes. SHA-256 dos bytes locais, comparação com bytes HEAD e segunda leitura independente do primeiro hash no mesmo processo. `status-fonte.json` registra branch/HEAD, contagem total e estados locais. Caminhos não técnicos foram substituídos por hash para não divulgar nomes de clientes. Nenhum conteúdo privado da fonte foi copiado.

| Caso | Resultado observado |
|---|---|
| C01 hash reproduzido | Segunda leitura de todos os arquivos resultou em hashes iguais; execução atual, conforme manifesto. |
| C02 untracked pertinente | 135 arquivos técnicos não rastreados incluídos, com hash de conteúdo local. Seleção definitiva do recorte depende do mapa P01-03/P01-04. |
| C03 sem escrita na fonte | Comandos exclusivamente de leitura; status antes/depois idêntico, sem alteração por esta tarefa. Isso não prova inexistência de escrita por processo externo em arquivos ignorados. |

Limite: o manifesto é metadado, não snapshot recuperável dos bytes modificados/não rastreados. Ainda falta congelamento recuperável autorizado e sanitizado da versão escolhida. O superset não afirma que todos os contratos transitivos foram fechados. Não aprova G0 por si só.

## P01-02

Contadores, horários internos dos TRX e hashes dos artefatos foram extraídos para `evidencias-historicas.json`; logs brutos não foram copiados. Horário de modificação de log é identificado como metadado, não hora confirmada de execução. Versão das suítes históricas sem manifesto contemporâneo permanece indeterminada, mesmo com HEAD atual igual ao inventário de 06/10.

| Capacidade / fonte | Prova e cenário | Nível e classificação | Limite |
|---|---|---|---|
| SQL CASST, `infra-sql-conclusivo.trx` | 131 executados / 131 aprovados / 0 falhas; times internos no JSON | Resultado aprovado histórico local para cenário da suíte | Sem vínculo reproduzível entre árvore executada e árvore atual; não certifica EBT nem produção. |
| SQL anterior, `infra-sql-final.trx` | 130 aprovados / 1 falha, 131 executados | Histórico anterior com falha | Nome final não é certificado; separado do conclusivo. |
| SQL anterior, `infra-sql-retest.trx` e regressão `20261006003533` | 113 aprovados / 16 falhas, 129 executados | Histórico com falhas | Não substitui reteste conclusivo de outra execução. |
| Domínio, regressão `20261006003416.trx` | 321 executados / 321 aprovados | Aprovado histórico local | Nome de arquivo não significa validação SQL deste conjunto. |
| Hardening, `e2e-hardening-final.log` | Contadores Node: tests 17, pass 17, fail 0, cancelled 0 | Aprovado histórico local, suíte Node | Não equivale a onboarding E2E de navegador completo; presença da palavra cancelled com valor 0 não significa cancelamento. |
| Onboarding, `e2e-quarta.log` | 1 failed / 4 did not run e referência a onboarding/ativação | Incompleto histórico local | Onboarding continua pendente; não corrigido nem retestado nesta tarefa. |
| API ampla, `testes-backend-final.log` | Marcador de cancelamento no log | Incompleto histórico local | Não afirmar suíte completa aprovada. |
| Vikings | Revisão documental existente: main b13140e, CI 37451503397 | Histórico CI reportado por `docs/REVISAO_BASES.md` | Não foi reconsultado nesta sub-tarefa; não aprova SQL real/OIDC/aceite operacional. |
| EBT institucional | Revisão documental: QA de 06/10 passed=true / 18 documentos públicos | Histórico de publicação reportado | Não houve nova consulta online nem homologação da versão atual. |
| CRP | Revisão documental: 214 testes e 43 verificações em 01/10 | Histórico reportado | Não prova novo consumidor EBT ou capacidades comerciais ausentes. |
| Nutrição | Revisão documental: backup/integridade de 06/10 e piloto | Histórico piloto reportado | Não certifica arquitetura SQL multitenant nem Meta/Outlook reais. |

C01: SQL conclusivo separado das falhas anteriores pelos contadores reais. C02: onboarding mantido pendente. C03: nenhuma prova estendida a módulo ausente, novo consumidor, tenant, contrato, schema ou storage. Nessas fronteiras R2/N permanece obrigatório; R1 documental não certifica reuso funcional.

## Comandos e continuidade

Leitura: `Get-Content` nos documentos e AGENTS; `rg --files` e `rg -n` nos caminhos técnicos e evidências; `git -C <fonte> status --porcelain=v1 --untracked-files=all`, `ls-files`, `rev-parse HEAD`, `branch --show-current`, `show HEAD:<arquivo>`; SHA-256 e parsing XML/log via Python. Captura: `python evidencias/execucao/PAC-01/baseline/capturar_baseline.py`. A captura levou aproximadamente dois minutos e encerrou com exit code 0. Complemento dos manifests de dependências também passou na segunda leitura de hash. Resultados atuais são metadados estáticos; nenhuma suíte funcional executada.

Próximo passo: conciliar produtores/consumidores escolhidos em P01-03/P01-04, direitos P01-05 e congelamento recuperável antes de fechar G0. Backlog, documentos gerados e status de produto não alterados por esta sub-tarefa. Autoria técnica: agente Codex baseline; nenhum aceite humano presumido.
