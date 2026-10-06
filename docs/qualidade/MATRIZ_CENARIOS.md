# Matriz de cenários por entrega

Casos abaixo são planejados e não executados. Linhas são cenários, não obrigação de um teste automático novo. A prova existente equivalente pode ser reutilizada conforme versão/fronteira.

## P01 | G0

| Caso | Ticket | Trilha | Cenário específico |
|---|---|---|---|
| P01-01-C01 | [P01-01](../execucao/entregas/P01-01.md) | R2 | Hash reproduzido |
| P01-01-C02 | [P01-01](../execucao/entregas/P01-01.md) | R2 | untracked pertinente incluído |
| P01-01-C03 | [P01-01](../execucao/entregas/P01-01.md) | R2 | comparação sem escrita nas fontes |
| P01-02-C01 | [P01-02](../execucao/entregas/P01-02.md) | R1 | SQL conclusivo separado do anterior |
| P01-02-C02 | [P01-02](../execucao/entregas/P01-02.md) | R1 | onboarding continua pendente |
| P01-02-C03 | [P01-02](../execucao/entregas/P01-02.md) | R1 | provas não se estendem a módulos ausentes |
| P01-03-C01 | [P01-03](../execucao/entregas/P01-03.md) | R2 | Uma jornada completa e demonstrável |
| P01-03-C02 | [P01-03](../execucao/entregas/P01-03.md) | R2 | até cinco etapas do funil |
| P01-03-C03 | [P01-03](../execucao/entregas/P01-03.md) | R2 | sem requisito financeiro escondido |
| P01-04-C01 | [P01-04](../execucao/entregas/P01-04.md) | R2 | Produtor e consumidor concordam |
| P01-04-C02 | [P01-04](../execucao/entregas/P01-04.md) | R2 | campo e cardinalidade registrados |
| P01-04-C03 | [P01-04](../execucao/entregas/P01-04.md) | R2 | nenhum endpoint inventado como existente |
| P01-05-C01 | [P01-05](../execucao/entregas/P01-05.md) | R2 | Cada item escolhido tem origem |
| P01-05-C02 | [P01-05](../execucao/entregas/P01-05.md) | R2 | pendência impede uso comercial daquele item |
| P01-05-C03 | [P01-05](../execucao/entregas/P01-05.md) | R2 | dado de cliente ausente |
| P01-06-C01 | [P01-06](../execucao/entregas/P01-06.md) | R2 | Gate indica passaram/pendências |
| P01-06-C02 | [P01-06](../execucao/entregas/P01-06.md) | R2 | recorte afetado não inicia vermelho |
| P01-06-C03 | [P01-06](../execucao/entregas/P01-06.md) | R2 | bases não foram alteradas |
## P02 | G1

| Caso | Ticket | Trilha | Cenário específico |
|---|---|---|---|
| P02-01-C01 | [P02-01](../execucao/entregas/P02-01.md) | N | ADR identifica recomendações e decisões ainda abertas |
| P02-01-C02 | [P02-01](../execucao/entregas/P02-01.md) | N | site preserva stack existente |
| P02-01-C03 | [P02-01](../execucao/entregas/P02-01.md) | N | Core não promete C0-C13 |
| P02-02-C01 | [P02-02](../execucao/entregas/P02-02.md) | N | Build backend e frontend reproduzíveis |
| P02-02-C02 | [P02-02](../execucao/entregas/P02-02.md) | N | arquivo de solução real |
| P02-02-C03 | [P02-02](../execucao/entregas/P02-02.md) | N | sem arquivo privado implícito |
| P02-03-C01 | [P02-03](../execucao/entregas/P02-03.md) | N | Config ausente falha com mensagem segura |
| P02-03-C02 | [P02-03](../execucao/entregas/P02-03.md) | N | Dev não usa produção |
| P02-03-C03 | [P02-03](../execucao/entregas/P02-03.md) | N | secret não aparece em repositório |
| P02-04-C01 | [P02-04](../execucao/entregas/P02-04.md) | N | Dados próprios em A/B |
| P02-04-C02 | [P02-04](../execucao/entregas/P02-04.md) | N | cópia de cadastro real ausente |
| P02-04-C03 | [P02-04](../execucao/entregas/P02-04.md) | N | fixtures reproduzíveis |
| P02-05-C01 | [P02-05](../execucao/entregas/P02-05.md) | N | Destino exclusivo conferido |
| P02-05-C02 | [P02-05](../execucao/entregas/P02-05.md) | N | tentativa com alvo produção recusada |
| P02-05-C03 | [P02-05](../execucao/entregas/P02-05.md) | N | binário e metadado separados |
| P02-06-C01 | [P02-06](../execucao/entregas/P02-06.md) | R2 | 401 tratado |
| P02-06-C02 | [P02-06](../execucao/entregas/P02-06.md) | R2 | erro não vira sucesso |
| P02-06-C03 | [P02-06](../execucao/entregas/P02-06.md) | R2 | download inválido tem diagnóstico seguro |
| P02-07-C01 | [P02-07](../execucao/entregas/P02-07.md) | N | CI bloqueia falha real |
| P02-07-C02 | [P02-07](../execucao/entregas/P02-07.md) | N | health representa dependências definidas |
| P02-07-C03 | [P02-07](../execucao/entregas/P02-07.md) | N | traceId não contém cadastro |
| P02-08-C01 | [P02-08](../execucao/entregas/P02-08.md) | N | Health e persistência conferidos |
| P02-08-C02 | [P02-08](../execucao/entregas/P02-08.md) | N | clone reproduz |
| P02-08-C03 | [P02-08](../execucao/entregas/P02-08.md) | N | nada declarado produção |
## P03 | G-SITE

| Caso | Ticket | Trilha | Cenário específico |
|---|---|---|---|
| P03-01-C01 | [P03-01](../execucao/entregas/P03-01.md) | R1 | Escolha única explícita |
| P03-01-C02 | [P03-01](../execucao/entregas/P03-01.md) | R1 | source e versão identificados |
| P03-01-C03 | [P03-01](../execucao/entregas/P03-01.md) | R1 | somente funções comprovadas aproveitadas |
| P03-02-C01 | [P03-02](../execucao/entregas/P03-02.md) | R2 | Conteúdo muda por config |
| P03-02-C02 | [P03-02](../execucao/entregas/P03-02.md) | R2 | contato correto por marca |
| P03-02-C03 | [P03-02](../execucao/entregas/P03-02.md) | R2 | assets autorizados |
| P03-03-C01 | [P03-03](../execucao/entregas/P03-03.md) | R1 | Links e assets válidos |
| P03-03-C02 | [P03-03](../execucao/entregas/P03-03.md) | R1 | retorno/menu coerentes |
| P03-03-C03 | [P03-03](../execucao/entregas/P03-03.md) | R1 | layout mobile e desktop |
| P03-04-C01 | [P03-04](../execucao/entregas/P03-04.md) | R2 | Registro consultável quando aplicável |
| P03-04-C02 | [P03-04](../execucao/entregas/P03-04.md) | R2 | erro mostra ausência de confirmação |
| P03-04-C03 | [P03-04](../execucao/entregas/P03-04.md) | R2 | wa.me é descrito como abertura |
| P03-05-C01 | [P03-05](../execucao/entregas/P03-05.md) | R1 | Sem overflow externo |
| P03-05-C02 | [P03-05](../execucao/entregas/P03-05.md) | R1 | teclado alcança controles |
| P03-05-C03 | [P03-05](../execucao/entregas/P03-05.md) | R1 | visitante não acessa painel privado |
| P03-06-C01 | [P03-06](../execucao/entregas/P03-06.md) | R2 | Pacote reproduz |
| P03-06-C02 | [P03-06](../execucao/entregas/P03-06.md) | R2 | checklist de entrada do cliente |
| P03-06-C03 | [P03-06](../execucao/entregas/P03-06.md) | R2 | publicação futura claramente condicionada |
## P04 | G-SEG

| Caso | Ticket | Trilha | Cenário específico |
|---|---|---|---|
| P04-01-C01 | [P04-01](../execucao/entregas/P04-01.md) | N | Permissão definida por operação |
| P04-01-C02 | [P04-01](../execucao/entregas/P04-01.md) | N | negativa explícita |
| P04-01-C03 | [P04-01](../execucao/entregas/P04-01.md) | N | técnico não recebe documento restrito automaticamente |
| P04-02-C01 | [P04-02](../execucao/entregas/P04-02.md) | R2 | Sessão válida acessa recorte |
| P04-02-C02 | [P04-02](../execucao/entregas/P04-02.md) | R2 | expirada é negada |
| P04-02-C03 | [P04-02](../execucao/entregas/P04-02.md) | R2 | header debug fora de Dev não autentica |
| P04-03-C01 | [P04-03](../execucao/entregas/P04-03.md) | N | Header/body adulterados não trocam empresa |
| P04-03-C02 | [P04-03](../execucao/entregas/P04-03.md) | N | usuário sem vínculo é negado |
| P04-03-C03 | [P04-03](../execucao/entregas/P04-03.md) | N | contexto não deriva de nome visual |
| P04-04-C01 | [P04-04](../execucao/entregas/P04-04.md) | N | A não lê nem escreve B |
| P04-04-C02 | [P04-04](../execucao/entregas/P04-04.md) | N | listagem e ID direto equivalentes |
| P04-04-C03 | [P04-04](../execucao/entregas/P04-04.md) | N | mutação cruzada não persiste |
| P04-05-C01 | [P04-05](../execucao/entregas/P04-05.md) | N | Banco vazio e snapshot anterior migram |
| P04-05-C02 | [P04-05](../execucao/entregas/P04-05.md) | N | duplicidade no mesmo tenant negada |
| P04-05-C03 | [P04-05](../execucao/entregas/P04-05.md) | N | independência A/B preservada |
| P04-06-C01 | [P04-06](../execucao/entregas/P04-06.md) | N | Leitura cruzada vazia/negada |
| P04-06-C02 | [P04-06](../execucao/entregas/P04-06.md) | N | insert indevido recusado |
| P04-06-C03 | [P04-06](../execucao/entregas/P04-06.md) | N | suíte pertinente verde sem ignorar caso crítico |
| P04-07-C01 | [P04-07](../execucao/entregas/P04-07.md) | N | ID de B negado |
| P04-07-C02 | [P04-07](../execucao/entregas/P04-07.md) | N | operador sem escopo negado |
| P04-07-C03 | [P04-07](../execucao/entregas/P04-07.md) | N | export não amplia carteira |
| P04-08-C01 | [P04-08](../execucao/entregas/P04-08.md) | R2 | Logout limpa |
| P04-08-C02 | [P04-08](../execucao/entregas/P04-08.md) | R2 | troca A/B não mostra dado anterior |
| P04-08-C03 | [P04-08](../execucao/entregas/P04-08.md) | R2 | resposta de contexto antigo descartada |
| P04-09-C01 | [P04-09](../execucao/entregas/P04-09.md) | R2 | Evento após escrita confirmada |
| P04-09-C02 | [P04-09](../execucao/entregas/P04-09.md) | R2 | erro não fabrica sucesso |
| P04-09-C03 | [P04-09](../execucao/entregas/P04-09.md) | R2 | senha/token/anexo restrito ausentes |
| P04-10-C01 | [P04-10](../execucao/entregas/P04-10.md) | R2 | CSRF inválido recusado quando aplicável |
| P04-10-C02 | [P04-10](../execucao/entregas/P04-10.md) | R2 | sessão revogada negada |
| P04-10-C03 | [P04-10](../execucao/entregas/P04-10.md) | R2 | headers seguros pertinentes |
| P04-11-C01 | [P04-11](../execucao/entregas/P04-11.md) | N | Ativação abre tela prevista |
| P04-11-C02 | [P04-11](../execucao/entregas/P04-11.md) | N | token inválido/reutilizado negado |
| P04-11-C03 | [P04-11](../execucao/entregas/P04-11.md) | N | timeout ampliado não substitui correção |
| P04-12-C01 | [P04-12](../execucao/entregas/P04-12.md) | N | Permitido e negado demonstrados |
| P04-12-C02 | [P04-12](../execucao/entregas/P04-12.md) | N | vazamento bloqueia gate |
| P04-12-C03 | [P04-12](../execucao/entregas/P04-12.md) | N | banco real identificado |
## P05 | G-CRM

| Caso | Ticket | Trilha | Cenário específico |
|---|---|---|---|
| P05-01-C01 | [P05-01](../execucao/entregas/P05-01.md) | R2 | Um ID atravessa telas |
| P05-01-C02 | [P05-01](../execucao/entregas/P05-01.md) | R2 | matrícula não vira identidade universal |
| P05-01-C03 | [P05-01](../execucao/entregas/P05-01.md) | R2 | nomes de UI não renomeiam chaves |
| P05-02-C01 | [P05-02](../execucao/entregas/P05-02.md) | R2 | Mesmo comando não duplica |
| P05-02-C02 | [P05-02](../execucao/entregas/P05-02.md) | R2 | cadastro recarrega |
| P05-02-C03 | [P05-02](../execucao/entregas/P05-02.md) | R2 | telefone de B não provoca fusão com A |
| P05-03-C01 | [P05-03](../execucao/entregas/P05-03.md) | R1 | Busca formatada encontra dentro do escopo |
| P05-03-C02 | [P05-03](../execucao/entregas/P05-03.md) | R1 | vazio/erro claros |
| P05-03-C03 | [P05-03](../execucao/entregas/P05-03.md) | R1 | limites de página respeitados |
| P05-04-C01 | [P05-04](../execucao/entregas/P05-04.md) | R2 | Falha mantém texto |
| P05-04-C02 | [P05-04](../execucao/entregas/P05-04.md) | R2 | conversa antiga não vira última indevidamente |
| P05-04-C03 | [P05-04](../execucao/entregas/P05-04.md) | R2 | reload preserva autoria |
| P05-05-C01 | [P05-05](../execucao/entregas/P05-05.md) | R2 | Lista e detalhe refletem mesmo valor |
| P05-05-C02 | [P05-05](../execucao/entregas/P05-05.md) | R2 | responsável indevido negado |
| P05-05-C03 | [P05-05](../execucao/entregas/P05-05.md) | R2 | ausência de prazo explícita |
| P05-06-C01 | [P05-06](../execucao/entregas/P05-06.md) | R2 | Etapa persiste |
| P05-06-C02 | [P05-06](../execucao/entregas/P05-06.md) | R2 | edição antiga conflita |
| P05-06-C03 | [P05-06](../execucao/entregas/P05-06.md) | R2 | retorno respeita estados permitidos |
| P05-07-C01 | [P05-07](../execucao/entregas/P05-07.md) | R2 | Config A/B muda apresentação |
| P05-07-C02 | [P05-07](../execucao/entregas/P05-07.md) | R2 | operação mantém contrato |
| P05-07-C03 | [P05-07](../execucao/entregas/P05-07.md) | R2 | sem hard-code CASST no recorte |
| P05-08-C01 | [P05-08](../execucao/entregas/P05-08.md) | N | Mesma regra sem fork |
| P05-08-C02 | [P05-08](../execucao/entregas/P05-08.md) | N | dados separados |
| P05-08-C03 | [P05-08](../execucao/entregas/P05-08.md) | N | correção no componente vale nos dois |
| P05-09-C01 | [P05-09](../execucao/entregas/P05-09.md) | R2 | Preview não grava |
| P05-09-C02 | [P05-09](../execucao/entregas/P05-09.md) | R2 | inválido não confirma |
| P05-09-C03 | [P05-09](../execucao/entregas/P05-09.md) | R2 | reenvio não duplica e resultado por linha existe |
| P05-10-C01 | [P05-10](../execucao/entregas/P05-10.md) | R2 | ID único após reload |
| P05-10-C02 | [P05-10](../execucao/entregas/P05-10.md) | R2 | gate segurança vigente |
| P05-10-C03 | [P05-10](../execucao/entregas/P05-10.md) | R2 | manual sem prometer integração externa |
## P06 | G-GED

| Caso | Ticket | Trilha | Cenário específico |
|---|---|---|---|
| P06-01-C01 | [P06-01](../execucao/entregas/P06-01.md) | R2 | Categoria única especificada |
| P06-01-C02 | [P06-01](../execucao/entregas/P06-01.md) | R2 | vínculo claro |
| P06-01-C03 | [P06-01](../execucao/entregas/P06-01.md) | R2 | política pendente explícita |
| P06-02-C01 | [P06-02](../execucao/entregas/P06-02.md) | R2 | Metadado aponta arquivo correto |
| P06-02-C02 | [P06-02](../execucao/entregas/P06-02.md) | R2 | vínculo cruzado negado |
| P06-02-C03 | [P06-02](../execucao/entregas/P06-02.md) | R2 | versão identificada |
| P06-03-C01 | [P06-03](../execucao/entregas/P06-03.md) | R2 | Inválido/excesso/path traversal negados |
| P06-03-C02 | [P06-03](../execucao/entregas/P06-03.md) | R2 | falha não libera |
| P06-03-C03 | [P06-03](../execucao/entregas/P06-03.md) | R2 | arquivo novo pendente |
| P06-04-C01 | [P06-04](../execucao/entregas/P06-04.md) | N | A autorizado baixa |
| P06-04-C02 | [P06-04](../execucao/entregas/P06-04.md) | N | B negado |
| P06-04-C03 | [P06-04](../execucao/entregas/P06-04.md) | N | URL ou key não contorna escopo |
| P06-05-C01 | [P06-05](../execucao/entregas/P06-05.md) | R2 | Versão anterior permanece |
| P06-05-C02 | [P06-05](../execucao/entregas/P06-05.md) | R2 | rejeição rastreável |
| P06-05-C03 | [P06-05](../execucao/entregas/P06-05.md) | R2 | aprovação antiga não libera nova versão |
| P06-06-C01 | [P06-06](../execucao/entregas/P06-06.md) | N | Retry retorna identidade lógica |
| P06-06-C02 | [P06-06](../execucao/entregas/P06-06.md) | N | metadado sem binário não confirma |
| P06-06-C03 | [P06-06](../execucao/entregas/P06-06.md) | N | versão obsoleta conflita |
| P06-07-C01 | [P06-07](../execucao/entregas/P06-07.md) | N | Integridade ok |
| P06-07-C02 | [P06-07](../execucao/entregas/P06-07.md) | N | arquivo baixado idêntico |
| P06-07-C03 | [P06-07](../execucao/entregas/P06-07.md) | N | chave necessária recuperada |
| P06-07-C04 | [P06-07](../execucao/entregas/P06-07.md) | N | pendência scan mantém restrição |
| P06-08-C01 | [P06-08](../execucao/entregas/P06-08.md) | N | Jornada válida |
| P06-08-C02 | [P06-08](../execucao/entregas/P06-08.md) | N | B não baixa A |
| P06-08-C03 | [P06-08](../execucao/entregas/P06-08.md) | N | recuperação provada |
| P06-08-C04 | [P06-08](../execucao/entregas/P06-08.md) | N | assinatura externa não inventada |
## P07 | G-TASK

| Caso | Ticket | Trilha | Cenário específico |
|---|---|---|---|
| P07-01-C01 | [P07-01](../execucao/entregas/P07-01.md) | R2 | Tarefa aponta cadastro existente |
| P07-01-C02 | [P07-01](../execucao/entregas/P07-01.md) | R2 | origem preservada |
| P07-01-C03 | [P07-01](../execucao/entregas/P07-01.md) | R2 | responsável elegível |
| P07-02-C01 | [P07-02](../execucao/entregas/P07-02.md) | R1 | Salvar/reload conferidos |
| P07-02-C02 | [P07-02](../execucao/entregas/P07-02.md) | R1 | filtro retorna origem correta |
| P07-02-C03 | [P07-02](../execucao/entregas/P07-02.md) | R1 | acesso negado claro |
| P07-03-C01 | [P07-03](../execucao/entregas/P07-03.md) | R2 | Conclusão repetida não duplica |
| P07-03-C02 | [P07-03](../execucao/entregas/P07-03.md) | R2 | cancelamento rastreável |
| P07-03-C03 | [P07-03](../execucao/entregas/P07-03.md) | R2 | estado indevido recusado |
| P07-04-C01 | [P07-04](../execucao/entregas/P07-04.md) | R2 | Virada de dia correta |
| P07-04-C02 | [P07-04](../execucao/entregas/P07-04.md) | R2 | sem prazo não vira atraso |
| P07-04-C03 | [P07-04](../execucao/entregas/P07-04.md) | R2 | timezone do host não muda regra |
| P07-05-C01 | [P07-05](../execucao/entregas/P07-05.md) | R2 | Painel mostra registro persistido |
| P07-05-C02 | [P07-05](../execucao/entregas/P07-05.md) | R2 | próxima ação acessível |
| P07-05-C03 | [P07-05](../execucao/entregas/P07-05.md) | R2 | nenhum envio externo declarado |
| P07-06-C01 | [P07-06](../execucao/entregas/P07-06.md) | R2 | Contador bate com lista |
| P07-06-C02 | [P07-06](../execucao/entregas/P07-06.md) | R2 | filtro/perfil muda contexto |
| P07-06-C03 | [P07-06](../execucao/entregas/P07-06.md) | R2 | consulta não altera tarefa |
## P08 | G-FLOW

| Caso | Ticket | Trilha | Cenário específico |
|---|---|---|---|
| P08-01-C01 | [P08-01](../execucao/entregas/P08-01.md) | N | Fluxo aberto/em análise/concluído definido |
| P08-01-C02 | [P08-01](../execucao/entregas/P08-01.md) | N | numeração única |
| P08-01-C03 | [P08-01](../execucao/entregas/P08-01.md) | N | sem designer |
| P08-02-C01 | [P08-02](../execucao/entregas/P08-02.md) | N | Duas criações não repetem número |
| P08-02-C02 | [P08-02](../execucao/entregas/P08-02.md) | N | mesma chave retorna mesmo protocolo |
| P08-02-C03 | [P08-02](../execucao/entregas/P08-02.md) | N | rollback não cria sucesso |
| P08-03-C01 | [P08-03](../execucao/entregas/P08-03.md) | N | Inexistente negado |
| P08-03-C02 | [P08-03](../execucao/entregas/P08-03.md) | N | B não vira interessado de A |
| P08-03-C03 | [P08-03](../execucao/entregas/P08-03.md) | N | download mantém política GED |
| P08-04-C01 | [P08-04](../execucao/entregas/P08-04.md) | N | Consulta por ID de B negada |
| P08-04-C02 | [P08-04](../execucao/entregas/P08-04.md) | N | sigilo coerente |
| P08-04-C03 | [P08-04](../execucao/entregas/P08-04.md) | N | histórico não pode ser reescrito pela UI |
| P08-05-C01 | [P08-05](../execucao/entregas/P08-05.md) | N | Ator autorizado avança |
| P08-05-C02 | [P08-05](../execucao/entregas/P08-05.md) | N | consulta não muda |
| P08-05-C03 | [P08-05](../execucao/entregas/P08-05.md) | N | evento e estado são coerentes |
| P08-06-C01 | [P08-06](../execucao/entregas/P08-06.md) | N | Sem resultado negado |
| P08-06-C02 | [P08-06](../execucao/entregas/P08-06.md) | N | reenvio não duplica |
| P08-06-C03 | [P08-06](../execucao/entregas/P08-06.md) | N | conflito não sobrescreve decisão |
| P08-07-C01 | [P08-07](../execucao/entregas/P08-07.md) | N | Número único |
| P08-07-C02 | [P08-07](../execucao/entregas/P08-07.md) | N | histórico consistente |
| P08-07-C03 | [P08-07](../execucao/entregas/P08-07.md) | N | B negado |
| P08-07-C04 | [P08-07](../execucao/entregas/P08-07.md) | N | restart mantém protocolo |
| P08-08-C01 | [P08-08](../execucao/entregas/P08-08.md) | N | Jornada completa em QA |
| P08-08-C02 | [P08-08](../execucao/entregas/P08-08.md) | N | gate GED vigente |
| P08-08-C03 | [P08-08](../execucao/entregas/P08-08.md) | N | W3/W4 e consulta pública continuam fora |
## P09 | G-RC

| Caso | Ticket | Trilha | Cenário específico |
|---|---|---|---|
| P09-01-C01 | [P09-01](../execucao/entregas/P09-01.md) | R2 | Todos os recortes rastreáveis |
| P09-01-C02 | [P09-01](../execucao/entregas/P09-01.md) | R2 | prova temporal preservada |
| P09-01-C03 | [P09-01](../execucao/entregas/P09-01.md) | R2 | versão exibida concorda |
| P09-02-C01 | [P09-02](../execucao/entregas/P09-02.md) | R2 | Origem e confirmação coerentes |
| P09-02-C02 | [P09-02](../execucao/entregas/P09-02.md) | R2 | falha é distinguida |
| P09-02-C03 | [P09-02](../execucao/entregas/P09-02.md) | R2 | site manual não promete CRM automático |
| P09-03-C01 | [P09-03](../execucao/entregas/P09-03.md) | N | Mesmo ID nas telas |
| P09-03-C02 | [P09-03](../execucao/entregas/P09-03.md) | N | outro tenant não lê |
| P09-03-C03 | [P09-03](../execucao/entregas/P09-03.md) | N | duas configurações sem fork |
| P09-04-C01 | [P09-04](../execucao/entregas/P09-04.md) | N | Fluxo completo persistido |
| P09-04-C02 | [P09-04](../execucao/entregas/P09-04.md) | N | permissões coerentes nos módulos |
| P09-04-C03 | [P09-04](../execucao/entregas/P09-04.md) | N | estado e arquivo reconciliados |
| P09-05-C01 | [P09-05](../execucao/entregas/P09-05.md) | N | Dados preservados |
| P09-05-C02 | [P09-05](../execucao/entregas/P09-05.md) | N | esquema compatível |
| P09-05-C03 | [P09-05](../execucao/entregas/P09-05.md) | N | forward fix ou rollback ensaiado |
| P09-06-C01 | [P09-06](../execucao/entregas/P09-06.md) | N | Login/consulta/download conferidos |
| P09-06-C02 | [P09-06](../execucao/entregas/P09-06.md) | N | traceId útil |
| P09-06-C03 | [P09-06](../execucao/entregas/P09-06.md) | N | nenhum dado restrito em log |
| P09-07-C01 | [P09-07](../execucao/entregas/P09-07.md) | R2 | Manual completo |
| P09-07-C02 | [P09-07](../execucao/entregas/P09-07.md) | R2 | campos pendentes explícitos |
| P09-07-C03 | [P09-07](../execucao/entregas/P09-07.md) | R2 | nenhum aceite preenchido por inferência |
| P09-08-C01 | [P09-08](../execucao/entregas/P09-08.md) | R2 | 180h e consumo reserva claros |
| P09-08-C02 | [P09-08](../execucao/entregas/P09-08.md) | R2 | Flow retirado se gate não passou |
| P09-08-C03 | [P09-08](../execucao/entregas/P09-08.md) | R2 | produção não declarada |
## P10 | CONDICIONAL

| Caso | Ticket | Trilha | Cenário específico |
|---|---|---|---|
| P10-01-C01 | [P10-01](../execucao/entregas/P10-01.md) | RES | Causa e correção registradas |
| P10-01-C02 | [P10-01](../execucao/entregas/P10-01.md) | RES | sucesso com mesmo critério |
| P10-01-C03 | [P10-01](../execucao/entregas/P10-01.md) | RES | saldo da reserva atualizado |
| P10-02-C01 | [P10-02](../execucao/entregas/P10-02.md) | RES | Fixture não mascara falha |
| P10-02-C02 | [P10-02](../execucao/entregas/P10-02.md) | RES | migration ensaiada |
| P10-02-C03 | [P10-02](../execucao/entregas/P10-02.md) | RES | gate continua bloqueado até prova |
| P10-03-C01 | [P10-03](../execucao/entregas/P10-03.md) | RES | Correção única serve aos dois |
| P10-03-C02 | [P10-03](../execucao/entregas/P10-03.md) | RES | origem/versionamento preservados |
| P10-03-C03 | [P10-03](../execucao/entregas/P10-03.md) | RES | custo real registrado |
| P10-04-C01 | [P10-04](../execucao/entregas/P10-04.md) | RES | Recuperação validada |
| P10-04-C02 | [P10-04](../execucao/entregas/P10-04.md) | RES | falha de provedor distinta |
| P10-04-C03 | [P10-04](../execucao/entregas/P10-04.md) | RES | autorização de liberação permanece |
| P10-05-C01 | [P10-05](../execucao/entregas/P10-05.md) | RES | Só casos necessários repetidos |
| P10-05-C02 | [P10-05](../execucao/entregas/P10-05.md) | RES | prova tem versão |
| P10-05-C03 | [P10-05](../execucao/entregas/P10-05.md) | RES | saldo não consumido permanece reserva |
