# Riscos concretos e uso da reserva

| Risco | Evidência ou origem | Sinal de ocorrência | Resposta | Reserva |
|---|---|---|---|---|
| R01, árvore incompleta | CASST/CRP têm mudanças locais | Snapshot difere do HEAD e omite arquivo produtor | Congelar árvore pertinente e comparar hashes | P10-03 se afetar extração |
| R02, ativação bloqueada | E2E CASST quarta rodada falhou no onboarding | Login não abre próxima tela do fluxo | Reproduzir causa; preservar critério; revalidar jornada | P10-01 |
| R03, fronteira de empresa nova | Generalização prevista | ID direto, cache ou gravação acessa A por B | Bloquear consumidores; corrigir e provar SQL/API | P10-02 |
| R04, referência temporal inadequada | CI/PR/provas são snapshots | Fonte/PR mudou desde inventário | Reconsultar versão e diffs relevantes antes da extração | Dentro do ticket; P10-03 se houver retrabalho |
| R05, binário/metadata/chave divergentes | Documento e restore são composição crítica | Hash divergente ou aplicação restaurada não lê arquivo | Não confirmar liberação; recuperar conjunto consistente | P10-04 |
| R06, configuração escondida | Bases dependem de ambiente | Clone não compila/inicia sem arquivo privado | Documentar opções e testar QA exclusivo | P10-04 |
| R07, abstração sem reuso | Core configurável ainda é plano | Segundo consumidor precisa copiar regra | Reduzir extração ao comum comprovado | P10-03 |
| R08, homologação indisponível | Usuário real não foi confirmado | Não há pessoa/ambiente para executar aceite | Fechar candidato QA com pendência explícita | P10-05 somente se houver trabalho real |
| R09, esforço acima da capacidade | Timeboxes são estimativas | Saldo projetado excede 200h | Reestimar; adiar P08 antes de cortar proteção | 20h totais, sem duplicar consumo |

A reserva não é cinco tarefas obrigatórias. Registrar defeito, ticket afetado, trabalho feito e consumo. Se o evento não ocorrer, as horas continuam livres. Serviços externos, novos módulos e custo de licença não são absorvidos sem mudança explícita de escopo.

## Critério de corte

Não remover casos de isolamento, autorização por ID, migração ou recuperação do recorte para cumprir prazo. Suspender o recorte afetado quando a prova falhar. Site/Flow estão adiados; uma mudança de fila por impedimento precisa de realocação explícita. Se a reserva se esgotar, fechar o que passou e transportar esforço restante a uma proposta revisada.
