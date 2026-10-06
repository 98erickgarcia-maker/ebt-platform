# Pacotes maiores para executar pelo Codex

17 pacotes de 8–12h estimadas agrupam as mesmas 72 entregas (180h). As cinco reservas mantêm 20h. Os 77 tickets, critérios e dependências originais permanecem. Agrupamento e documentação não comprovam execução.

| Pacote | Resultado | Tickets | Horas | Gate ao fechar fase |
|---|---|---|---:|---|
| [PAC-01](pacotes/PAC-01.md) | Baseline e contrato do primeiro recorte | P01-01 a P01-06 | 12h | G0 |
| [PAC-02](pacotes/PAC-02.md) | Estrutura, configuração e dados sintéticos | P02-01 a P02-04 | 8h | Parcial; gate pendente |
| [PAC-03](pacotes/PAC-03.md) | Banco, storage, diagnóstico e CI | P02-05 a P02-08 | 8h | G1 |
| [PAC-04](pacotes/PAC-04.md) | Site essencial completo | P03-01 a P03-06 | 12h | G-SITE |
| [PAC-05](pacotes/PAC-05.md) | Identidade e escopo de tenant | P04-01 a P04-04 | 12h | Parcial; gate pendente |
| [PAC-06](pacotes/PAC-06.md) | SQL, autorização por recurso e cache | P04-05 a P04-08 | 12h | Parcial; gate pendente |
| [PAC-07](pacotes/PAC-07.md) | Auditoria, proteção da sessão e onboarding | P04-09 a P04-12 | 12h | G-SEG |
| [PAC-08](pacotes/PAC-08.md) | Cadastro único, busca e paginação | P05-01 a P05-03 | 9h | Parcial; gate pendente |
| [PAC-09](pacotes/PAC-09.md) | Histórico, próxima ação e funil | P05-04 a P05-06 | 9h | Parcial; gate pendente |
| [PAC-10](pacotes/PAC-10.md) | Segundo consumidor, importação e fechamento do CRM | P05-07 a P05-10 | 10h | G-CRM |
| [PAC-11](pacotes/PAC-11.md) | Documento privado e acesso autorizado | P06-01 a P06-04 | 12h | Parcial; gate pendente |
| [PAC-12](pacotes/PAC-12.md) | Versões, concorrência e recuperação documental | P06-05 a P06-08 | 12h | G-GED |
| [PAC-13](pacotes/PAC-13.md) | Tarefas vinculadas e prazos | P07-01 a P07-06 | 12h | G-TASK |
| [PAC-14](pacotes/PAC-14.md) | Protocolo, numeração e consulta | P08-01 a P08-04 | 12h | Parcial; gate pendente |
| [PAC-15](pacotes/PAC-15.md) | Tramitação e encerramento do Flow | P08-05 a P08-08 | 12h | G-FLOW |
| [PAC-16](pacotes/PAC-16.md) | Reconciliação e jornadas integradas | P09-01 a P09-04 | 8h | Parcial; gate pendente |
| [PAC-17](pacotes/PAC-17.md) | Migration, restore, operação e candidato | P09-05 a P09-08 | 8h | G-RC |

## Qualidade e orçamento

Revisão própria do diff e demonstração integrada fazem parte da verificação já estimada. Não acrescentar 17 revisões como horas extras nem usar a reserva para ocultar esse esforço. Registrar custo real; se faltar capacidade, seguir reserva/corte previsto. As horas não garantem prazo do Codex nem qualidade absoluta.

[Método de execução e revisão](EXECUCAO_PELO_CODEX.md) | [Catálogo estruturado](../../planejamento/pacotes_codex.json) | [Validação e gates](../VALIDACAO_E_GATES.md)
