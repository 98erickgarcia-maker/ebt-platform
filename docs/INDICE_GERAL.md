# Índice geral do projeto EBT Platform

Versão de organização 1.1. Navegação completa para consulta, execução futura e continuidade. 72 entregas + cinco reservas, 200h; nenhum módulo de produto declarado executado.

## Base e orçamento

- [PLANO 200 HORAS](PLANO_200_HORAS.md).
- [BACKLOG 200 HORAS](BACKLOG_200_HORAS.md).
- [REVISAO BASES](REVISAO_BASES.md).
- [VALIDACAO E GATES](VALIDACAO_E_GATES.md).
- [FONTES E LIMITES](FONTES_E_LIMITES.md).
- [CHANGELOG](CHANGELOG.md).

## Gestão

- [ESCOPO E RESULTADOS](gestao/ESCOPO_E_RESULTADOS.md).
- [GOVERNANCA E RESPONSABILIDADES](gestao/GOVERNANCA_E_RESPONSABILIDADES.md).
- [DECISOES PENDENTES](gestao/DECISOES_PENDENTES.md).
- [RISCOS E CONTINGENCIA](gestao/RISCOS_E_CONTINGENCIA.md).

## Arquitetura e decisões

- [ARQUITETURA E FRONTEIRAS](arquitetura/ARQUITETURA_E_FRONTEIRAS.md).
- [DADOS E INVARIANTES](arquitetura/DADOS_E_INVARIANTES.md).
- [CONTRATOS E COMPATIBILIDADE](arquitetura/CONTRATOS_E_COMPATIBILIDADE.md).
- [PERMISSOES CANDIDATAS](arquitetura/PERMISSOES_CANDIDATAS.md).
- [ADR-001 REAPROVEITAMENTO](arquitetura/adr/ADR-001_REAPROVEITAMENTO.md).
- [ADR-002 TENANT E IDENTIDADE](arquitetura/adr/ADR-002_TENANT_E_IDENTIDADE.md).
- [ADR-003 DOCUMENTO E TRANSACAO](arquitetura/adr/ADR-003_DOCUMENTO_E_TRANSACAO.md).
- [ADR-004 PROTOCOLO FIXO](arquitetura/adr/ADR-004_PROTOCOLO_FIXO.md).

## Produtos

- [SITE ESSENCIAL](produtos/SITE_ESSENCIAL.md).
- [CRM CONNECT INICIAL](produtos/CRM_CONNECT_INICIAL.md).
- [DOCUMENTOS E TAREFAS](produtos/DOCUMENTOS_E_TAREFAS.md).
- [FLOW PILOTO](produtos/FLOW_PILOTO.md).
- [CANDIDATO E IMPLANTACAO](produtos/CANDIDATO_E_IMPLANTACAO.md).

## Execução

- [COMO EXECUTAR E CONTINUAR](execucao/COMO_EXECUTAR_E_CONTINUAR.md).
- [DEPENDENCIAS](execucao/DEPENDENCIAS.md).

## Qualidade

- [ESTRATEGIA DE EVIDENCIAS](qualidade/ESTRATEGIA_DE_EVIDENCIAS.md).
- [MATRIZ CENARIOS](qualidade/MATRIZ_CENARIOS.md).

## Operação

- [AMBIENTES E CONFIGURACAO](operacao/AMBIENTES_E_CONFIGURACAO.md).
- [MIGRACAO E COMPATIBILIDADE](operacao/MIGRACAO_E_COMPATIBILIDADE.md).
- [BACKUP E RESTAURACAO](operacao/BACKUP_E_RESTAURACAO.md).
- [RELEASE E RETORNO](operacao/RELEASE_E_RETORNO.md).
- [ACESSOS E INCIDENTES](operacao/ACESSOS_E_INCIDENTES.md).

## Templates

- [ENTREGA](../templates/ENTREGA.md).
- [CONTRATO](../templates/CONTRATO.md).
- [DECISAO](../templates/DECISAO.md).
- [BUG](../templates/BUG.md).
- [GATE](../templates/GATE.md).
- [ACEITE PILOTO](../templates/ACEITE_PILOTO.md).
- [RELEASE](../templates/RELEASE.md).
- [ESFORCO](../templates/ESFORCO.md).

## Dez fases e todas as fichas

### [P01 | Baseline e escolha do reaproveitamento](execucao/fases/P01.md)

- [P01-01 | Congelar fontes e hashes do fluxo escolhido](execucao/entregas/P01-01.md) (2h, R2).
- [P01-02 | Separar evidência aprovada, incompleta e histórica](execucao/entregas/P01-02.md) (2h, R1).
- [P01-03 | Escolher o fluxo mínimo do primeiro CRM](execucao/entregas/P01-03.md) (2h, R2).
- [P01-04 | Mapear contratos e vínculos desse fluxo](execucao/entregas/P01-04.md) (2h, R2).
- [P01-05 | Conferir direitos de uso e dependências](execucao/entregas/P01-05.md) (2h, R2).
- [P01-06 | Fechar baseline e ordem dos pequenos PRs](execucao/entregas/P01-06.md) (2h, R2).

### [P02 | Fundação mínima para trabalhar](execucao/fases/P02.md)

- [P02-01 | Registrar arquitetura e limite do Core inicial](execucao/entregas/P02-01.md) (2h, N).
- [P02-02 | Criar estrutura e comandos reproduzíveis](execucao/entregas/P02-02.md) (2h, N).
- [P02-03 | Separar configuração e segredos por ambiente](execucao/entregas/P02-03.md) (2h, N).
- [P02-04 | Criar massa sintética para dois consumidores](execucao/entregas/P02-04.md) (2h, N).
- [P02-05 | Montar banco e storage exclusivos de QA](execucao/entregas/P02-05.md) (2h, N).
- [P02-06 | Reaproveitar cliente HTTP e padrões de erro](execucao/entregas/P02-06.md) (2h, R2).
- [P02-07 | Configurar CI mínimo e diagnóstico seguro](execucao/entregas/P02-07.md) (2h, N).
- [P02-08 | Demonstrar fundação e registrar G1](execucao/entregas/P02-08.md) (2h, N).

### [P03 | Primeiro pacote: site essencial reutilizável](execucao/fases/P03.md)

- [P03-01 | Escolher uma única base de site existente](execucao/entregas/P03-01.md) (2h, R1).
- [P03-02 | Centralizar marca, contato e serviços do pacote](execucao/entregas/P03-02.md) (2h, R2).
- [P03-03 | Reaproveitar páginas e navegação](execucao/entregas/P03-03.md) (2h, R1).
- [P03-04 | Conferir formulário e canal efetivo](execucao/entregas/P03-04.md) (2h, R2).
- [P03-05 | Executar regressão visual e de acesso focal](execucao/entregas/P03-05.md) (2h, R1).
- [P03-06 | Preparar entrega, manual e retorno do site](execucao/entregas/P03-06.md) (2h, R2).

### [P04 | Identidade, isolamento e auditoria](execucao/fases/P04.md)

- [P04-01 | Definir matriz usuário, empresa e ação](execucao/entregas/P04-01.md) (3h, N).
- [P04-02 | Reusar sessão/login com limites claros](execucao/entregas/P04-02.md) (3h, R2).
- [P04-03 | Definir TenantContext a partir da identidade](execucao/entregas/P04-03.md) (3h, N).
- [P04-04 | Aplicar escopo a consultas e gravações](execucao/entregas/P04-04.md) (3h, N).
- [P04-05 | Criar índices e migration do recorte](execucao/entregas/P04-05.md) (3h, N).
- [P04-06 | Conferir SQL/RLS do recorte com banco real](execucao/entregas/P04-06.md) (3h, N).
- [P04-07 | Implementar autorização por recurso](execucao/entregas/P04-07.md) (3h, N).
- [P04-08 | Isolar cache, sessão e troca de perfil](execucao/entregas/P04-08.md) (3h, R2).
- [P04-09 | Reusar evento de auditoria com minimização](execucao/entregas/P04-09.md) (3h, R2).
- [P04-10 | Conferir proteção de cookies ou tokens](execucao/entregas/P04-10.md) (3h, R2).
- [P04-11 | Fechar onboarding e cenários negativos](execucao/entregas/P04-11.md) (3h, N).
- [P04-12 | Demonstrar G-SEG com dois consumidores](execucao/entregas/P04-12.md) (3h, N).

### [P05 | Segundo pacote: CRM simples / Connect inicial](execucao/fases/P05.md)

- [P05-01 | Fixar contrato mínimo de pessoa e organização](execucao/entregas/P05-01.md) (3h, R2).
- [P05-02 | Reaproveitar cadastro e prevenção de duplicidade](execucao/entregas/P05-02.md) (3h, R2).
- [P05-03 | Reaproveitar lista, busca e paginação](execucao/entregas/P05-03.md) (3h, R1).
- [P05-04 | Reaproveitar histórico de interações](execucao/entregas/P05-04.md) (3h, R2).
- [P05-05 | Reaproveitar responsável e próxima ação](execucao/entregas/P05-05.md) (3h, R2).
- [P05-06 | Configurar funil simples e mudança de etapa](execucao/entregas/P05-06.md) (3h, R2).
- [P05-07 | Aplicar marca e vocabulário a uma tela completa](execucao/entregas/P05-07.md) (3h, R2).
- [P05-08 | Rodar segundo consumidor sem forks de regra](execucao/entregas/P05-08.md) (3h, N).
- [P05-09 | Preparar importação de planilha limpa do recorte](execucao/entregas/P05-09.md) (2h, R2).
- [P05-10 | Demonstrar G-CRM e manual de implantação](execucao/entregas/P05-10.md) (2h, R2).

### [P06 | Documentos privados, recorte GED](execucao/fases/P06.md)

- [P06-01 | Delimitar documento comercial do piloto](execucao/entregas/P06-01.md) (3h, R2).
- [P06-02 | Reaproveitar metadados e vínculo](execucao/entregas/P06-02.md) (3h, R2).
- [P06-03 | Adaptar upload privado e validações](execucao/entregas/P06-03.md) (3h, R2).
- [P06-04 | Garantir download com autorização por ID](execucao/entregas/P06-04.md) (3h, N).
- [P06-05 | Reaproveitar revisão e nova versão](execucao/entregas/P06-05.md) (3h, R2).
- [P06-06 | Conferir falha, repetição e concorrência](execucao/entregas/P06-06.md) (3h, N).
- [P06-07 | Conferir recuperação de banco e arquivo](execucao/entregas/P06-07.md) (3h, N).
- [P06-08 | Demonstrar G-GED com segundo consumidor](execucao/entregas/P06-08.md) (3h, N).

### [P07 | Tarefas e prazos ligados ao cadastro](execucao/fases/P07.md)

- [P07-01 | Fixar contrato da tarefa vinculada](execucao/entregas/P07-01.md) (2h, R2).
- [P07-02 | Reaproveitar criação, lista e filtros](execucao/entregas/P07-02.md) (2h, R1).
- [P07-03 | Reaproveitar conclusão e cancelamento](execucao/entregas/P07-03.md) (2h, R2).
- [P07-04 | Conferir datas e indicação de atraso](execucao/entregas/P07-04.md) (2h, R2).
- [P07-05 | Exibir pendência interna sem canal externo](execucao/entregas/P07-05.md) (2h, R2).
- [P07-06 | Demonstrar G-TASK e métricas básicas](execucao/entregas/P07-06.md) (2h, R2).

### [P08 | Terceiro pacote: protocolo e tramitação mínima](execucao/fases/P08.md)

- [P08-01 | Especificar fluxo e numeração do piloto](execucao/entregas/P08-01.md) (3h, N).
- [P08-02 | Criar protocolo e sequência transacional](execucao/entregas/P08-02.md) (3h, N).
- [P08-03 | Vincular interessado, documento e responsável](execucao/entregas/P08-03.md) (3h, N).
- [P08-04 | Criar consulta e histórico de movimentação](execucao/entregas/P08-04.md) (3h, N).
- [P08-05 | Implementar uma transição manual autorizada](execucao/entregas/P08-05.md) (3h, N).
- [P08-06 | Implementar encerramento com resultado](execucao/entregas/P08-06.md) (3h, N).
- [P08-07 | Conferir falhas e persistência do fluxo](execucao/entregas/P08-07.md) (3h, N).
- [P08-08 | Demonstrar G-FLOW e limites do piloto](execucao/entregas/P08-08.md) (3h, N).

### [P09 | Empacotamento e homologação interna](execucao/fases/P09.md)

- [P09-01 | Reconciliar resultados e versão entregue](execucao/entregas/P09-01.md) (2h, R2).
- [P09-02 | Conferir jornada de site e cadastro](execucao/entregas/P09-02.md) (2h, R2).
- [P09-03 | Conferir jornada CRM em dois consumidores](execucao/entregas/P09-03.md) (2h, N).
- [P09-04 | Conferir jornada Flow e documento privado](execucao/entregas/P09-04.md) (2h, N).
- [P09-05 | Ensaiar atualização de banco e retorno](execucao/entregas/P09-05.md) (2h, N).
- [P09-06 | Ensaiar restore integrado e diagnóstico](execucao/entregas/P09-06.md) (2h, N).
- [P09-07 | Preparar operação e aceite do piloto](execucao/entregas/P09-07.md) (2h, R2).
- [P09-08 | Fechar candidato e backlog após 200h](execucao/entregas/P09-08.md) (2h, R2).

### [P10 | Reserva protegida de correção](execucao/fases/P10.md)

- [P10-01 | Reserva: onboarding e fixture de regressão](execucao/entregas/P10-01.md) (4h, RES).
- [P10-02 | Reserva: isolamento e migração](execucao/entregas/P10-02.md) (4h, RES).
- [P10-03 | Reserva: extração e contratos do segundo consumidor](execucao/entregas/P10-03.md) (4h, RES).
- [P10-04 | Reserva: documentos, recuperação e ambiente](execucao/entregas/P10-04.md) (4h, RES).
- [P10-05 | Reserva: rodada adicional de homologação](execucao/entregas/P10-05.md) (4h, RES).

## Dados, evidências e leitura offline

- [backlog_200_horas.json](../planejamento/backlog_200_horas.json).
- [detalhamento_entregas.json](../planejamento/detalhamento_entregas.json).
- [cenarios_verificacao.json](../planejamento/cenarios_verificacao.json).
- [gates_e_dependencias.json](../planejamento/gates_e_dependencias.json).
- [governanca.json](../planejamento/governanca.json).
- [manifesto_organizacao.json](../planejamento/manifesto_organizacao.json).
- [inventario_fontes.json](../evidencias/inventario_fontes.json).
- [github_vikings_snapshot.json](../evidencias/github_vikings_snapshot.json).
- [verificacao_plano.json](../evidencias/verificacao_plano.json).
- [verificacao_organizacao.json](../evidencias/verificacao_organizacao.json).
- [EBT_Plano_Primeiras_200_Horas.pdf](../output/pdf/EBT_Plano_Primeiras_200_Horas.pdf).
- [EBT_Planejamento_Codigo_Plataforma.pdf](referencias/EBT_Planejamento_Codigo_Plataforma.pdf).
- [CONTINUAR_EM_OUTRO_CHAT.md](../CONTINUAR_EM_OUTRO_CHAT.md).
