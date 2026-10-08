# Backlog detalhado: 200 horas

Execução autorizada em 07/10/2026: [estado real e provas](qualidade/STATUS_IMPLEMENTACAO_CONNECT.md). Este documento preserva o plano/contrato candidato; não promover seus estados ou casos em lote.


Revisão de prioridade: 07/10/2026. Connect com tarefas e comunicação é a primeira demonstração prevista, em 140h cumulativas, com checkpoint CRM/tarefas em 104h. Site e Flow ficam no backlog posterior. As janelas seguem a nova ordem; nenhuma hora real de execução foi presumida. Todos os itens ativos estão planejados. RES representa capacidade contingente, sem entrega funcional presumida.

## P01 | Baseline e escolha do reaproveitamento | 12h | acumulado 12h

Resultado: Mapa de fontes congeladas e primeiro fluxo escolhido. Gate: G0. Origem: CASST, Vikings, EBT, CRP e Nutrição.

### P01-01 | Congelar fontes e hashes do fluxo escolhido | 2h | R2

- Dependências: nenhuma.
- Janela de esforço: 0-2h.
- Aceite: Snapshot inclui arquivos modificados e não rastreados; um commit antigo não substitui o conteúdo local.
- Evidência: Registro P01-01: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P01-02 | Separar evidência aprovada, incompleta e histórica | 2h | R1

- Dependências: P01-01.
- Janela de esforço: 2-4h.
- Aceite: Cada capacidade tem arquivo, data, versão e nível de prova; falhas antigas e repetições finais ficam distintas.
- Evidência: Registro P01-02: versão/hash, ambiente, cenário e resultado conforme trilha R1.
- Composição: implementação 1.5h, verificação 0.25h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P01-03 | Escolher o fluxo mínimo do primeiro CRM | 2h | R2

- Dependências: P01-02.
- Janela de esforço: 4-6h.
- Aceite: Escopo fechado: contato, organização, histórico, responsável e próxima ação; financeiro e OS ficam fora.
- Evidência: Registro P01-03: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P01-04 | Mapear contratos e vínculos desse fluxo | 2h | R2

- Dependências: P01-03.
- Janela de esforço: 6-8h.
- Aceite: Registrar IDs, endpoints, produtor, consumidor, cache e efeito após salvar sem renomear contratos persistidos.
- Evidência: Registro P01-04: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P01-05 | Conferir direitos de uso e dependências | 2h | R2

- Dependências: P01-04.
- Janela de esforço: 8-10h.
- Aceite: Registrar autoria/licenças e pendências do código/assets; componente com direito de uso incerto não entra no pacote comercial.
- Evidência: Registro P01-05: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P01-06 | Fechar baseline e ordem dos pequenos PRs | 2h | R2

- Dependências: P01-05.
- Janela de esforço: 10-12h.
- Aceite: G0 registra o que pode ser copiado, adaptado ou apenas consultado; nenhuma extração parte de teste relevante falhando.
- Evidência: Registro P01-06: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P02 | Fundação mínima para trabalhar | 16h | acumulado 28h

Resultado: Ambiente EBT isolado e verificações automatizadas. Gate: G1. Origem: Padrões de CI/HTTP/UI das fontes; composição nova.

### P02-01 | Registrar arquitetura e limite do Core inicial | 2h | N

- Dependências: P01-GATE.
- Janela de esforço: 12-14h.
- Aceite: ADR mantém .NET/React/SQL para o Core e permite site estático/Razor existente; nenhuma reescrita por estética de stack.
- Evidência: Registro P02-01: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P02-02 | Criar estrutura e comandos reproduzíveis | 2h | N

- Dependências: P02-01.
- Janela de esforço: 14-16h.
- Aceite: Clone limpo tem instruções e versões explícitas; um comando compila API e outro interface.
- Evidência: Registro P02-02: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P02-03 | Separar configuração e segredos por ambiente | 2h | N

- Dependências: P02-02.
- Janela de esforço: 16-18h.
- Aceite: Exemplos sem credenciais; falta de configuração privada gera erro seguro, sem fallback para cliente real.
- Evidência: Registro P02-03: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P02-04 | Criar massa sintética para dois consumidores | 2h | N

- Dependências: P02-03.
- Janela de esforço: 18-20h.
- Aceite: Dois perfis de empresa têm dados identificados e próprios; nenhum cadastro de cliente real é copiado.
- Evidência: Registro P02-04: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P02-05 | Montar banco e storage exclusivos de QA | 2h | N

- Dependências: P02-04.
- Janela de esforço: 20-22h.
- Aceite: Script aponta só ao ambiente EBT de teste; recusa destino de produção e mantém fontes intactas.
- Evidência: Registro P02-05: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P02-06 | Reaproveitar cliente HTTP e padrões de erro | 2h | R2

- Dependências: P02-05.
- Janela de esforço: 22-24h.
- Aceite: Contrato de erro, expiração e download passa pelos testes pertinentes; chamada não mostra sucesso sem resposta confirmada.
- Evidência: Registro P02-06: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P02-07 | Configurar CI mínimo e diagnóstico seguro | 2h | N

- Dependências: P02-06.
- Janela de esforço: 24-26h.
- Aceite: PR roda build/typecheck/testes pertinentes; health e traceId não expõem dados ou segredos.
- Evidência: Registro P02-07: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P02-08 | Demonstrar fundação e registrar G1 | 2h | N

- Dependências: P02-07.
- Janela de esforço: 26-28h.
- Aceite: Aplicação inicia em QA, faz health e persiste dado sintético; comandos e limites documentados.
- Evidência: Registro P02-08: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P04 | Identidade, isolamento e auditoria | 36h | acumulado 64h

Resultado: Base segura para primeiro CRM em dois contextos sintéticos. Gate: G-SEG. Origem: CASST como base; referências Vikings; generalização nova.

### P04-01 | Definir matriz usuário, empresa e ação | 3h | N

- Dependências: P02-GATE.
- Janela de esforço: 28-31h.
- Aceite: Administrador, operador e consulta têm escopos explícitos; suporte técnico não recebe dado sensível automaticamente.
- Evidência: Registro P04-01: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-02 | Reusar sessão/login com limites claros | 3h | R2

- Dependências: P04-01.
- Janela de esforço: 31-34h.
- Aceite: Login/logout/expiração validados no fluxo EBT; cabeçalhos de desenvolvimento não autenticam ambiente não Dev.
- Evidência: Registro P04-02: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-03 | Definir TenantContext a partir da identidade | 3h | N

- Dependências: P04-02.
- Janela de esforço: 34-37h.
- Aceite: Header/body manipulados não alteram empresa; conta sem vínculo ativo tem acesso recusado.
- Evidência: Registro P04-03: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-04 | Aplicar escopo a consultas e gravações | 3h | N

- Dependências: P04-03.
- Janela de esforço: 37-40h.
- Aceite: Listagem e mutação são autorizadas no servidor; tenant B não consulta ou modifica IDs de A.
- Evidência: Registro P04-04: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-05 | Criar índices e migration do recorte | 3h | N

- Dependências: P04-04.
- Janela de esforço: 40-43h.
- Aceite: Unicidade é por tenant onde aplicável; migration sobe em banco vazio e no snapshot sintético anterior.
- Evidência: Registro P04-05: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-06 | Conferir SQL/RLS do recorte com banco real | 3h | N

- Dependências: P04-05.
- Janela de esforço: 43-46h.
- Aceite: Testes de leitura/escrita com contexto A/B aprovados; falha de fixture não é aceita como prova de isolamento.
- Evidência: Registro P04-06: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-07 | Implementar autorização por recurso | 3h | N

- Dependências: P04-06.
- Janela de esforço: 46-49h.
- Aceite: ID direto, exportação e download revalidam permissão; esconder menu não concede nem retira acesso.
- Evidência: Registro P04-07: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-08 | Isolar cache, sessão e troca de perfil | 3h | R2

- Dependências: P04-07.
- Janela de esforço: 49-52h.
- Aceite: Troca de empresa/perfil e logout limpam dados; resposta/cache de A nunca aparece em B.
- Evidência: Registro P04-08: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-09 | Reusar evento de auditoria com minimização | 3h | R2

- Dependências: P04-08.
- Janela de esforço: 52-55h.
- Aceite: Ator, empresa, instante, operação e correlação persistem; senha/token/conteúdo clínico ficam ausentes.
- Evidência: Registro P04-09: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-10 | Conferir proteção de cookies ou tokens | 3h | R2

- Dependências: P04-09.
- Janela de esforço: 55-58h.
- Aceite: Estratégia reaproveitada tem expiração/revogação e CSRF quando aplicável; negativas têm testes específicos.
- Evidência: Registro P04-10: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-11 | Fechar onboarding e cenários negativos | 3h | N

- Dependências: P04-10.
- Janela de esforço: 58-61h.
- Aceite: E2E login, ativação e próxima tela funciona; pendência CASST no onboarding é reproduzida/solucionada no recorte, sem mascarar timeout.
- Evidência: Registro P04-11: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-12 | Demonstrar G-SEG com dois consumidores | 3h | N

- Dependências: P04-11.
- Janela de esforço: 61-64h.
- Aceite: Matriz A/B e permitido/proibido aprovada no banco real; vazamento bloqueia avanço de todos os módulos dependentes.
- Evidência: Registro P04-12: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P05 | Cadastro e jornada CRM do EBT Connect | 28h | acumulado 92h

Resultado: CRM demonstrável com cadastro único e próxima ação. Gate: G-CRM. Origem: Fluxo comercial CASST; referências de cadastro Nutrição/CRP.

### P05-01 | Fixar contrato mínimo de pessoa e organização | 3h | R2

- Dependências: P04-GATE.
- Janela de esforço: 64-67h.
- Aceite: ID interno permanece estável; contato não é recadastrado por cada módulo nem confundido com vínculo trabalhista.
- Evidência: Registro P05-01: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-02 | Reaproveitar cadastro e prevenção de duplicidade | 3h | R2

- Dependências: P05-01.
- Janela de esforço: 67-70h.
- Aceite: Cadastro/repetição/reload mantêm um contato no tenant; regra de telefone não une pessoas de empresas diferentes.
- Evidência: Registro P05-02: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-03 | Reaproveitar lista, busca e paginação | 3h | R2

- Dependências: P05-02.
- Janela de esforço: 70-73h.
- Aceite: Filtros, vazio, erro e acesso negado cobertos no recorte; busca e exportação respeitam escopo.
- Evidência: Registro P05-03: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-04 | Reaproveitar histórico de interações | 3h | R2

- Dependências: P05-03.
- Janela de esforço: 73-76h.
- Aceite: Autoria e data preservadas; nota interna e conversa são distintas; falha ao salvar mantém o texto.
- Evidência: Registro P05-04: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-05 | Reaproveitar responsável e próxima ação | 3h | R2

- Dependências: P05-04.
- Janela de esforço: 76-79h.
- Aceite: Somente responsável ativo/autorizado; salvar e consultar em outra tela mostram o mesmo prazo persistido.
- Evidência: Registro P05-05: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-06 | Configurar funil simples e mudança de etapa | 3h | R2

- Dependências: P05-05.
- Janela de esforço: 79-82h.
- Aceite: Até cinco etapas do fluxo fixo; alteração persiste histórico e recusa edição concorrente obsoleta.
- Evidência: Registro P05-06: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-07 | Aplicar marca e vocabulário a uma tela completa | 3h | R2

- Dependências: P05-06.
- Janela de esforço: 82-85h.
- Aceite: Marca, menu, título, vazio e impressão do recorte usam configuração sem alterar enums/IDs técnicos.
- Evidência: Registro P05-07: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-08 | Rodar segundo consumidor sem forks de regra | 3h | N

- Dependências: P05-07.
- Janela de esforço: 85-88h.
- Aceite: Duas configurações usam o mesmo serviço/componente versionado e massa própria; nenhum hard-code CASST necessário.
- Evidência: Registro P05-08: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-09 | Preparar importação de planilha limpa do recorte | 2h | R2

- Dependências: P05-08.
- Janela de esforço: 88-90h.
- Aceite: Até 100 contatos sintéticos, layout fixo, preview/validação e confirmação idempotente; dados inválidos não gravam parcialmente.
- Evidência: Registro P05-09: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-10 | Demonstrar G-CRM e manual de implantação | 2h | R2

- Dependências: P05-09.
- Janela de esforço: 90-92h.
- Aceite: Login -> contato -> histórico -> próxima ação -> reload em QA; implantação real depende de contrato, credenciais e aceite.
- Evidência: Registro P05-10: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P07 | Tarefas e prazos ligados ao cadastro | 12h | acumulado 104h

Resultado: Tarefas do contato e composição CRM/tarefas do Connect. Gate: G-TASK. Origem: Agenda/atividades CASST e ActionItem Vikings.

### P07-01 | Fixar contrato da tarefa vinculada | 2h | R2

- Dependências: P05-GATE.
- Janela de esforço: 92-94h.
- Aceite: Tarefa possui contato existente de origem, responsável, prazo e estado; próxima ação/tarefa têm fonte coerente, sem cadastro paralelo. Vínculo documental só é exercitado após P06.
- Evidência: Registro P07-01: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P07-02 | Reaproveitar criação, lista e filtros | 2h | R2

- Dependências: P07-01.
- Janela de esforço: 94-96h.
- Aceite: Salvar/reload e filtros de responsável/vencimento funcionam; lista mantém tenant e perfil.
- Evidência: Registro P07-02: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P07-03 | Reaproveitar conclusão e cancelamento | 2h | R2

- Dependências: P07-02.
- Janela de esforço: 96-98h.
- Aceite: Conclusão tem resultado/evidência; cancelamento tem motivo e preserva histórico; repetição é segura.
- Evidência: Registro P07-03: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P07-04 | Conferir datas e indicação de atraso | 2h | R2

- Dependências: P07-03.
- Janela de esforço: 98-100h.
- Aceite: Brasília, virada de dia e prazo vazio têm regra definida; relógio controlado valida atraso sem esperar tempo real.
- Evidência: Registro P07-04: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P07-05 | Exibir pendência interna sem canal externo | 2h | R2

- Dependências: P07-04.
- Janela de esforço: 100-102h.
- Aceite: Operador vê próxima ação persistida na aplicação; contato, detalhe e tarefa mostram responsável/prazo coerentes e fechamento retira a pendência. Estado interno não é apresentado como mensagem enviada.
- Evidência: Registro P07-05: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P07-06 | Demonstrar G-TASK e métricas básicas | 2h | R2

- Dependências: P07-05.
- Janela de esforço: 102-104h.
- Aceite: Contador reconcilia com listagem/período; somente usuário permitido altera tarefa. Jornada CRM/tarefas mantém o mesmo ID após nova sessão, com G-SEG/G-CRM vigentes na versão final.
- Evidência: Registro P07-06: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P11 | Comunicação Connect por API e webhook | 36h | acumulado 140h

Resultado: Receber, responder e acompanhar status de texto no canal homologado. Gate: G-MSG. Origem: Desenho EBT; referências oficiais Chatwoot, Meta, Stripe e Microsoft.

### P11-01 | Fixar canal, conta de QA e versão do provedor | 3h | N

- Dependências: P04-GATE, P05-GATE, P07-GATE.
- Janela de esforço: 104-107h.
- Aceite: Conta/conexão pertence ao tenant; versão, escopos, janela/template, direitos e custos estão registrados; sem contratação ou conta real por inferência.
- Evidência: Registro P11-01: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P11-02 | Definir mensagens, conversas e contrato de resposta | 3h | N

- Dependências: P11-01.
- Janela de esforço: 107-110h.
- Aceite: Uma conversa referencia contato/empresa/canal; API tem idempotência, concorrência, paginação e erro seguro; nota interna não gera envio.
- Evidência: Registro P11-02: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P11-03 | Validar assinatura e handshake do webhook | 3h | N

- Dependências: P11-02.
- Janela de esforço: 110-113h.
- Aceite: Assinatura é conferida nos bytes originais antes de efeitos; desafio GET é separado do POST; conexão/tenant vêm do mapeamento confiável do canal.
- Evidência: Registro P11-03: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P11-04 | Persistir entrada e deduplicar eventos | 3h | N

- Dependências: P11-03.
- Janela de esforço: 113-116h.
- Aceite: ACK somente após recebimento durável; repetição e lote não duplicam mensagens; falha antes do commit permite retry; tipos novos não desaparecem silenciosamente.
- Evidência: Registro P11-04: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P11-05 | Processar evento e vincular contato e conversa | 3h | N

- Dependências: P11-04.
- Janela de esforço: 116-119h.
- Aceite: Worker idempotente normaliza mensagem; IDs externos são escopados por conexão/tenant; remetente não une pessoas de empresas diferentes.
- Evidência: Registro P11-05: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P11-06 | Registrar resposta e outbox na mesma transação | 3h | N

- Dependências: P11-05.
- Janela de esforço: 119-122h.
- Aceite: Resposta autorizada e intenção de envio persistem juntas; 202 informa fila, mesma chave/payload retorna a mesma operação e payload diferente conflita.
- Evidência: Registro P11-06: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P11-07 | Enviar texto pelo adapter oficial delimitado | 3h | N

- Dependências: P11-06.
- Janela de esforço: 122-125h.
- Aceite: Worker valida conexão, autorização/política vigente e destinatário da conversa; conserva ID externo; aceite do provedor não significa entrega.
- Evidência: Registro P11-07: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P11-08 | Conciliar callbacks e eventos fora de ordem | 3h | N

- Dependências: P11-07.
- Janela de esforço: 125-128h.
- Aceite: Sent/delivered/read/failed são eventos distintos; duplicata não duplica histórico; callback anterior à resposta da API fica pendente e depois é conciliado.
- Evidência: Registro P11-08: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P11-09 | Tratar timeout, retry e envio desconhecido | 3h | N

- Dependências: P11-08.
- Janela de esforço: 128-131h.
- Aceite: Timeout após POST não reenvia automaticamente sem prova de idempotência do provedor; estado desconhecido e diagnóstico seguro permitem reconciliação auditada.
- Evidência: Registro P11-09: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P11-10 | Mostrar conversa e resposta na interface Connect | 3h | N

- Dependências: P11-09.
- Janela de esforço: 131-134h.
- Aceite: Histórico tem direção/autor/instante e estados reais; rascunho sobrevive à falha; conflito e consulta negada são visíveis; notas permanecem internas.
- Evidência: Registro P11-10: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P11-11 | Validar jornada e negativas do canal | 3h | N

- Dependências: P11-10.
- Janela de esforço: 134-137h.
- Aceite: Receber/responder/status passa em QA A/B, assinatura inválida, ID direto, repetição, queda de worker e restore; mock não homologa Meta.
- Evidência: Registro P11-11: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P11-12 | Demonstrar G-MSG e manual de operação | 3h | N

- Dependências: P11-11.
- Janela de esforço: 137-140h.
- Aceite: Versão final reúne G-SEG/G-CRM/G-TASK/G-MSG, prova do canal, pendências e runbook; sem acesso externo, gate fica pendente e entrega local é identificada como tal.
- Evidência: Registro P11-12: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P06 | Documentos privados, recorte GED | 24h | acumulado 164h

Resultado: Um fluxo de documento com versão, permissão e histórico. Gate: G-GED. Origem: CASST, Vikings e PlanDocument Nutrição como referências.

### P06-01 | Delimitar documento comercial do piloto | 3h | R2

- Dependências: P04-GATE, P05-GATE.
- Janela de esforço: 140-143h.
- Aceite: Uma categoria e um vínculo contato/processo; nenhuma promessa de prontuário, assinatura digital ou GED completo.
- Evidência: Registro P06-01: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P06-02 | Reaproveitar metadados e vínculo | 3h | R2

- Dependências: P06-01.
- Janela de esforço: 143-146h.
- Aceite: Tenant, entidade, categoria, autor, MIME, tamanho e hash persistem com ID estável.
- Evidência: Registro P06-02: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P06-03 | Adaptar upload privado e validações | 3h | R2

- Dependências: P06-02.
- Janela de esforço: 146-149h.
- Aceite: Arquivo permitido grava; excesso de tamanho/MIME inválido e path traversal são recusados; arquivo novo fica pendente.
- Evidência: Registro P06-03: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P06-04 | Garantir download com autorização por ID | 3h | N

- Dependências: P06-03.
- Janela de esforço: 149-152h.
- Aceite: Somente perfil e tenant permitidos baixam; storage não é público e URL temporária não contorna autorização.
- Evidência: Registro P06-04: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P06-05 | Reaproveitar revisão e nova versão | 3h | R2

- Dependências: P06-04.
- Janela de esforço: 152-155h.
- Aceite: Revisão/rejeição têm ator/motivo; nova versão não sobrescreve a evidência anterior nem a aprovação passada.
- Evidência: Registro P06-05: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P06-06 | Conferir falha, repetição e concorrência | 3h | N

- Dependências: P06-05.
- Janela de esforço: 155-158h.
- Aceite: Resposta perdida/retry não cria duplicata; falha de storage não deixa metadado confirmado sem binário.
- Evidência: Registro P06-06: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P06-07 | Conferir recuperação de banco e arquivo | 3h | N

- Dependências: P06-06.
- Janela de esforço: 158-161h.
- Aceite: Restore isolado recupera metadados/binário/chaves; hash baixado confere; scan externo ausente mantém arquivo sem liberação ampla.
- Evidência: Registro P06-07: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P06-08 | Demonstrar G-GED com segundo consumidor | 3h | N

- Dependências: P06-07.
- Janela de esforço: 161-164h.
- Aceite: Enviar -> revisar -> liberar -> baixar, negar B e restaurar em QA; scan/assinatura externos permanecem bloqueados até homologação. Composição documento/tarefa existente preserva origem e não concede acesso ao arquivo por ter tarefa.
- Evidência: Registro P06-08: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P09 | Empacotamento e homologação interna | 16h | acumulado 180h

Resultado: Candidato Connect/comunicação/documentos com operação e recuperação. Gate: G-RC. Origem: Composição nova e regressões dos recortes.

### P09-01 | Reconciliar resultados e versão entregue | 2h | R2

- Dependências: P05-GATE, P07-GATE, P11-GATE, P06-GATE.
- Janela de esforço: 164-166h.
- Aceite: Manifesto identifica hash/commit, configuração e testes; evidência de um módulo não certifica os outros.
- Evidência: Registro P09-01: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P09-02 | Conferir jornada de contato e tarefas | 2h | R2

- Dependências: P09-01.
- Janela de esforço: 166-168h.
- Aceite: Cadastro, histórico, próxima ação e tarefa usam o mesmo ID; resultado persiste após nova sessão e a jornada de consulta não permite escrita.
- Evidência: Registro P09-02: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P09-03 | Conferir jornada CRM em dois consumidores | 2h | N

- Dependências: P09-02.
- Janela de esforço: 168-170h.
- Aceite: Usuários permitidos/proibidos repetem contato, histórico e tarefa; contratos e IDs iguais nas configurações.
- Evidência: Registro P09-03: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P09-04 | Conferir jornada de comunicação e documento privado | 2h | N

- Dependências: P09-03.
- Janela de esforço: 170-172h.
- Aceite: Mensagem recebida, resposta, callbacks e documento autorizado usam o contato correto; A/B, falha/repetição e restore preservam evidência e não disparam reenvio incerto.
- Evidência: Registro P09-04: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P09-05 | Ensaiar atualização de banco e retorno | 2h | N

- Dependências: P09-04.
- Janela de esforço: 172-174h.
- Aceite: Banco sintético anterior migra, contagens/IDs se mantêm; rollback ou forward fix documentado e ensaiado.
- Evidência: Registro P09-05: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P09-06 | Ensaiar restore integrado e diagnóstico | 2h | N

- Dependências: P09-05.
- Janela de esforço: 174-176h.
- Aceite: Banco, arquivo e chaves recuperados em destino exclusivo; incidente tem traceId e procedimento de retorno.
- Evidência: Registro P09-06: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P09-07 | Preparar operação e aceite do piloto | 2h | R2

- Dependências: P09-06.
- Janela de esforço: 176-178h.
- Aceite: Manual, responsáveis propostos, escopo de suporte e ficha de aceite disponíveis; aceite de usuário real ainda precisa ocorrer.
- Evidência: Registro P09-07: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P09-08 | Fechar candidato e backlog após 200h | 2h | R2

- Dependências: P09-07.
- Janela de esforço: 178-180h.
- Aceite: Candidato identifica gates/provas/pendências, esforço real e reserva; site/Flow permanecem adiados. Homologação do usuário e produção não são declaradas por fechamento de orçamento.
- Evidência: Registro P09-08: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P10 | Reserva protegida de correção | 20h | acumulado 200h

Resultado: Capacidade para corrigir e homologar sem aumentar escopo. Gate: CONDICIONAL. Origem: Contingência, consumida por necessidade.

### P10-01 | Reserva: onboarding e fixture de regressão | 4h | RES

- Dependências: defeito comprovado no recorte afetado.
- Janela de esforço: 180-184h.
- Aceite: Usar somente se login/harness bloquear os recortes; registrar defeito, horas reais e teste que deixou de falhar.
- Evidência: Registro P10-01: versão/hash, ambiente, cenário e resultado conforme trilha RES.
- Composição: implementação 0h, verificação 0h, registro 0h, reserva 4h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P10-02 | Reserva: isolamento e migração | 4h | RES

- Dependências: defeito comprovado no recorte afetado.
- Janela de esforço: 184-188h.
- Aceite: Usar para falha de tenant/SQL; reduzir funcionalidades opcionais se exigir mais tempo, sem cortar teste de segurança.
- Evidência: Registro P10-02: versão/hash, ambiente, cenário e resultado conforme trilha RES.
- Composição: implementação 0h, verificação 0h, registro 0h, reserva 4h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P10-03 | Reserva: extração e contratos do segundo consumidor | 4h | RES

- Dependências: defeito comprovado no recorte afetado.
- Janela de esforço: 188-192h.
- Aceite: Resolver acoplamento descoberto sem copiar regra por cliente; reavaliar custo/benefício da extração.
- Evidência: Registro P10-03: versão/hash, ambiente, cenário e resultado conforme trilha RES.
- Composição: implementação 0h, verificação 0h, registro 0h, reserva 4h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P10-04 | Reserva: documentos, recuperação e ambiente | 4h | RES

- Dependências: defeito comprovado no recorte afetado.
- Janela de esforço: 192-196h.
- Aceite: Fechar storage/restore/ambiente do recorte; falha de provedor externo não autoriza ativá-lo sem prova.
- Evidência: Registro P10-04: versão/hash, ambiente, cenário e resultado conforme trilha RES.
- Composição: implementação 0h, verificação 0h, registro 0h, reserva 4h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P10-05 | Reserva: rodada adicional de homologação | 4h | RES

- Dependências: defeito comprovado no recorte afetado.
- Janela de esforço: 196-200h.
- Aceite: Repetir somente casos afetados por correção e fechar evidência; sobra mantém capacidade livre, sem inventar módulo.
- Evidência: Registro P10-05: versão/hash, ambiente, cenário e resultado conforme trilha RES.
- Composição: implementação 0h, verificação 0h, registro 0h, reserva 4h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.
