# Backlog detalhado: 200 horas

Todos os itens estão planejados. Horas incluem verificação e registro; os cinco itens RES são reserva, não entregas funcionais. Dependência de gate refere-se ao fechamento do bloco indicado.

## P01 | Baseline e escolha do reaproveitamento | 12h | acumulado 12h

Resultado: Mapa de fontes congeladas e primeiro fluxo escolhido. Gate: G0. Origem: CASST, Vikings, EBT, CRP e Nutrição.

### P01-01 | Congelar fontes e hashes do fluxo escolhido | 2h | R2

- Dependências: nenhuma.
- Aceite: Snapshot inclui arquivos modificados e não rastreados; um commit antigo não substitui o conteúdo local.
- Evidência: Registro P01-01: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P01-02 | Separar evidência aprovada, incompleta e histórica | 2h | R1

- Dependências: P01-01.
- Aceite: Cada capacidade tem arquivo, data, versão e nível de prova; falhas antigas e repetições finais ficam distintas.
- Evidência: Registro P01-02: versão/hash, ambiente, cenário e resultado conforme trilha R1.
- Composição: implementação 1.5h, verificação 0.25h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P01-03 | Escolher o fluxo mínimo do primeiro CRM | 2h | R2

- Dependências: P01-02.
- Aceite: Escopo fechado: contato, organização, histórico, responsável e próxima ação; financeiro e OS ficam fora.
- Evidência: Registro P01-03: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P01-04 | Mapear contratos e vínculos desse fluxo | 2h | R2

- Dependências: P01-03.
- Aceite: Registrar IDs, endpoints, produtor, consumidor, cache e efeito após salvar sem renomear contratos persistidos.
- Evidência: Registro P01-04: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P01-05 | Conferir direitos de uso e dependências | 2h | R2

- Dependências: P01-04.
- Aceite: Registrar autoria/licenças e pendências do código/assets; componente com direito de uso incerto não entra no pacote comercial.
- Evidência: Registro P01-05: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P01-06 | Fechar baseline e ordem dos pequenos PRs | 2h | R2

- Dependências: P01-05.
- Aceite: G0 registra o que pode ser copiado, adaptado ou apenas consultado; nenhuma extração parte de teste relevante falhando.
- Evidência: Registro P01-06: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P02 | Fundação mínima para trabalhar | 16h | acumulado 28h

Resultado: Ambiente EBT isolado e verificações automatizadas. Gate: G1. Origem: Padrões de CI/HTTP/UI das fontes; composição nova.

### P02-01 | Registrar arquitetura e limite do Core inicial | 2h | N

- Dependências: P01-GATE.
- Aceite: ADR mantém .NET/React/SQL para o Core e permite site estático/Razor existente; nenhuma reescrita por estética de stack.
- Evidência: Registro P02-01: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P02-02 | Criar estrutura e comandos reproduzíveis | 2h | N

- Dependências: P02-01.
- Aceite: Clone limpo tem instruções e versões explícitas; um comando compila API e outro interface.
- Evidência: Registro P02-02: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P02-03 | Separar configuração e segredos por ambiente | 2h | N

- Dependências: P02-02.
- Aceite: Exemplos sem credenciais; falta de configuração privada gera erro seguro, sem fallback para cliente real.
- Evidência: Registro P02-03: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P02-04 | Criar massa sintética para dois consumidores | 2h | N

- Dependências: P02-03.
- Aceite: Dois perfis de empresa têm dados identificados e próprios; nenhum cadastro de cliente real é copiado.
- Evidência: Registro P02-04: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P02-05 | Montar banco e storage exclusivos de QA | 2h | N

- Dependências: P02-04.
- Aceite: Script aponta só ao ambiente EBT de teste; recusa destino de produção e mantém fontes intactas.
- Evidência: Registro P02-05: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P02-06 | Reaproveitar cliente HTTP e padrões de erro | 2h | R2

- Dependências: P02-05.
- Aceite: Contrato de erro, expiração e download passa pelos testes pertinentes; chamada não mostra sucesso sem resposta confirmada.
- Evidência: Registro P02-06: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P02-07 | Configurar CI mínimo e diagnóstico seguro | 2h | N

- Dependências: P02-06.
- Aceite: PR roda build/typecheck/testes pertinentes; health e traceId não expõem dados ou segredos.
- Evidência: Registro P02-07: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P02-08 | Demonstrar fundação e registrar G1 | 2h | N

- Dependências: P02-07.
- Aceite: Aplicação inicia em QA, faz health e persiste dado sintético; comandos e limites documentados.
- Evidência: Registro P02-08: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P03 | Primeiro pacote: site essencial reutilizável | 12h | acumulado 40h

Resultado: Pacote de site pronto para demonstração e implantação delimitada. Gate: G-SITE. Origem: EBT institucional e CRP; sem depender do Core novo.

### P03-01 | Escolher uma única base de site existente | 2h | R1

- Dependências: P01-GATE, P02-GATE.
- Aceite: Comparar EBT estático e CRP Razor e escolher conforme pedido; escopo até cinco páginas, conteúdo fornecido.
- Evidência: Registro P03-01: versão/hash, ambiente, cenário e resultado conforme trilha R1.
- Composição: implementação 1.5h, verificação 0.25h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P03-02 | Centralizar marca, contato e serviços do pacote | 2h | R2

- Dependências: P03-01.
- Aceite: Duas marcas sintéticas aparecem por configuração; conteúdo e fotos autorizados têm origem registrada.
- Evidência: Registro P03-02: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P03-03 | Reaproveitar páginas e navegação | 2h | R1

- Dependências: P03-02.
- Aceite: Home, serviços, sobre, contato e privacidade navegam em celular/computador; links e assets válidos.
- Evidência: Registro P03-03: versão/hash, ambiente, cenário e resultado conforme trilha R1.
- Composição: implementação 1.5h, verificação 0.25h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P03-04 | Conferir formulário e canal efetivo | 2h | R2

- Dependências: P03-03.
- Aceite: Se houver registro servidor, validar persistência e falha; wa.me é abertura manual e aparece descrito assim.
- Evidência: Registro P03-04: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P03-05 | Executar regressão visual e de acesso focal | 2h | R1

- Dependências: P03-04.
- Aceite: Conferir páginas alteradas, foco, contraste e overflow; painel privado existente continua protegido.
- Evidência: Registro P03-05: versão/hash, ambiente, cenário e resultado conforme trilha R1.
- Composição: implementação 1.5h, verificação 0.25h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P03-06 | Preparar entrega, manual e retorno do site | 2h | R2

- Dependências: P03-05.
- Aceite: Demo e pacote reproduzíveis com escopo fechado; publicação real permanece condicionada ao ambiente e aceite do cliente.
- Evidência: Registro P03-06: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P04 | Identidade, isolamento e auditoria | 36h | acumulado 76h

Resultado: Base segura para primeiro CRM em dois contextos sintéticos. Gate: G-SEG. Origem: CASST como base; referências Vikings; generalização nova.

### P04-01 | Definir matriz usuário, empresa e ação | 3h | N

- Dependências: P02-GATE.
- Aceite: Administrador, operador e consulta têm escopos explícitos; suporte técnico não recebe dado sensível automaticamente.
- Evidência: Registro P04-01: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-02 | Reusar sessão/login com limites claros | 3h | R2

- Dependências: P04-01.
- Aceite: Login/logout/expiração validados no fluxo EBT; cabeçalhos de desenvolvimento não autenticam ambiente não Dev.
- Evidência: Registro P04-02: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-03 | Definir TenantContext a partir da identidade | 3h | N

- Dependências: P04-02.
- Aceite: Header/body manipulados não alteram empresa; conta sem vínculo ativo tem acesso recusado.
- Evidência: Registro P04-03: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-04 | Aplicar escopo a consultas e gravações | 3h | N

- Dependências: P04-03.
- Aceite: Listagem e mutação são autorizadas no servidor; tenant B não consulta ou modifica IDs de A.
- Evidência: Registro P04-04: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-05 | Criar índices e migration do recorte | 3h | N

- Dependências: P04-04.
- Aceite: Unicidade é por tenant onde aplicável; migration sobe em banco vazio e no snapshot sintético anterior.
- Evidência: Registro P04-05: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-06 | Conferir SQL/RLS do recorte com banco real | 3h | N

- Dependências: P04-05.
- Aceite: Testes de leitura/escrita com contexto A/B aprovados; falha de fixture não é aceita como prova de isolamento.
- Evidência: Registro P04-06: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-07 | Implementar autorização por recurso | 3h | N

- Dependências: P04-06.
- Aceite: ID direto, exportação e download revalidam permissão; esconder menu não concede nem retira acesso.
- Evidência: Registro P04-07: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-08 | Isolar cache, sessão e troca de perfil | 3h | R2

- Dependências: P04-07.
- Aceite: Troca de empresa/perfil e logout limpam dados; resposta/cache de A nunca aparece em B.
- Evidência: Registro P04-08: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-09 | Reusar evento de auditoria com minimização | 3h | R2

- Dependências: P04-08.
- Aceite: Ator, empresa, instante, operação e correlação persistem; senha/token/conteúdo clínico ficam ausentes.
- Evidência: Registro P04-09: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-10 | Conferir proteção de cookies ou tokens | 3h | R2

- Dependências: P04-09.
- Aceite: Estratégia reaproveitada tem expiração/revogação e CSRF quando aplicável; negativas têm testes específicos.
- Evidência: Registro P04-10: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-11 | Fechar onboarding e cenários negativos | 3h | N

- Dependências: P04-10.
- Aceite: E2E login, ativação e próxima tela funciona; pendência CASST no onboarding é reproduzida/solucionada no recorte, sem mascarar timeout.
- Evidência: Registro P04-11: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P04-12 | Demonstrar G-SEG com dois consumidores | 3h | N

- Dependências: P04-11.
- Aceite: Matriz A/B e permitido/proibido aprovada no banco real; vazamento bloqueia avanço de todos os módulos dependentes.
- Evidência: Registro P04-12: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P05 | Segundo pacote: CRM simples / Connect inicial | 28h | acumulado 104h

Resultado: CRM demonstrável com cadastro único e próxima ação. Gate: G-CRM. Origem: Fluxo comercial CASST; referências de cadastro Nutrição/CRP.

### P05-01 | Fixar contrato mínimo de pessoa e organização | 3h | R2

- Dependências: P04-GATE.
- Aceite: ID interno permanece estável; contato não é recadastrado por cada módulo nem confundido com vínculo trabalhista.
- Evidência: Registro P05-01: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-02 | Reaproveitar cadastro e prevenção de duplicidade | 3h | R2

- Dependências: P05-01.
- Aceite: Cadastro/repetição/reload mantêm um contato no tenant; regra de telefone não une pessoas de empresas diferentes.
- Evidência: Registro P05-02: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-03 | Reaproveitar lista, busca e paginação | 3h | R1

- Dependências: P05-02.
- Aceite: Filtros, vazio, erro e acesso negado cobertos no recorte; busca e exportação respeitam escopo.
- Evidência: Registro P05-03: versão/hash, ambiente, cenário e resultado conforme trilha R1.
- Composição: implementação 2.5h, verificação 0.25h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-04 | Reaproveitar histórico de interações | 3h | R2

- Dependências: P05-03.
- Aceite: Autoria e data preservadas; nota interna e conversa são distintas; falha ao salvar mantém o texto.
- Evidência: Registro P05-04: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-05 | Reaproveitar responsável e próxima ação | 3h | R2

- Dependências: P05-04.
- Aceite: Somente responsável ativo/autorizado; salvar e consultar em outra tela mostram o mesmo prazo persistido.
- Evidência: Registro P05-05: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-06 | Configurar funil simples e mudança de etapa | 3h | R2

- Dependências: P05-05.
- Aceite: Até cinco etapas do fluxo fixo; alteração persiste histórico e recusa edição concorrente obsoleta.
- Evidência: Registro P05-06: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-07 | Aplicar marca e vocabulário a uma tela completa | 3h | R2

- Dependências: P05-06.
- Aceite: Marca, menu, título, vazio e impressão do recorte usam configuração sem alterar enums/IDs técnicos.
- Evidência: Registro P05-07: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-08 | Rodar segundo consumidor sem forks de regra | 3h | N

- Dependências: P05-07.
- Aceite: Duas configurações usam o mesmo serviço/componente versionado e massa própria; nenhum hard-code CASST necessário.
- Evidência: Registro P05-08: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-09 | Preparar importação de planilha limpa do recorte | 2h | R2

- Dependências: P05-08.
- Aceite: Até 100 contatos sintéticos, layout fixo, preview/validação e confirmação idempotente; dados inválidos não gravam parcialmente.
- Evidência: Registro P05-09: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P05-10 | Demonstrar G-CRM e manual de implantação | 2h | R2

- Dependências: P05-09.
- Aceite: Login -> contato -> histórico -> próxima ação -> reload em QA; implantação real depende de contrato, credenciais e aceite.
- Evidência: Registro P05-10: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P06 | Documentos privados, recorte GED | 24h | acumulado 128h

Resultado: Um fluxo de documento com versão, permissão e histórico. Gate: G-GED. Origem: CASST, Vikings e PlanDocument Nutrição como referências.

### P06-01 | Delimitar documento comercial do piloto | 3h | R2

- Dependências: P04-GATE, P05-GATE.
- Aceite: Uma categoria e um vínculo contato/processo; nenhuma promessa de prontuário, assinatura digital ou GED completo.
- Evidência: Registro P06-01: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P06-02 | Reaproveitar metadados e vínculo | 3h | R2

- Dependências: P06-01.
- Aceite: Tenant, entidade, categoria, autor, MIME, tamanho e hash persistem com ID estável.
- Evidência: Registro P06-02: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P06-03 | Adaptar upload privado e validações | 3h | R2

- Dependências: P06-02.
- Aceite: Arquivo permitido grava; excesso de tamanho/MIME inválido e path traversal são recusados; arquivo novo fica pendente.
- Evidência: Registro P06-03: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P06-04 | Garantir download com autorização por ID | 3h | N

- Dependências: P06-03.
- Aceite: Somente perfil e tenant permitidos baixam; storage não é público e URL temporária não contorna autorização.
- Evidência: Registro P06-04: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P06-05 | Reaproveitar revisão e nova versão | 3h | R2

- Dependências: P06-04.
- Aceite: Revisão/rejeição têm ator/motivo; nova versão não sobrescreve a evidência anterior nem a aprovação passada.
- Evidência: Registro P06-05: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 2.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P06-06 | Conferir falha, repetição e concorrência | 3h | N

- Dependências: P06-05.
- Aceite: Resposta perdida/retry não cria duplicata; falha de storage não deixa metadado confirmado sem binário.
- Evidência: Registro P06-06: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P06-07 | Conferir recuperação de banco e arquivo | 3h | N

- Dependências: P06-06.
- Aceite: Restore isolado recupera metadados/binário/chaves; hash baixado confere; scan externo ausente mantém arquivo sem liberação ampla.
- Evidência: Registro P06-07: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P06-08 | Demonstrar G-GED com segundo consumidor | 3h | N

- Dependências: P06-07.
- Aceite: Enviar -> revisar -> liberar -> baixar, negar B e restaurar em QA; scan/assinatura externos permanecem bloqueados até homologação.
- Evidência: Registro P06-08: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P07 | Tarefas e prazos ligados ao cadastro | 12h | acumulado 140h

Resultado: Pendências internas com responsável e histórico. Gate: G-TASK. Origem: Agenda/atividades CASST e ActionItem Vikings.

### P07-01 | Fixar contrato da tarefa vinculada | 2h | R2

- Dependências: P05-GATE, P06-GATE.
- Aceite: Tarefa possui contato/documento de origem, responsável, prazo e estado; não cria cadastro paralelo.
- Evidência: Registro P07-01: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P07-02 | Reaproveitar criação, lista e filtros | 2h | R1

- Dependências: P07-01.
- Aceite: Salvar/reload e filtros de responsável/vencimento funcionam; lista mantém tenant e perfil.
- Evidência: Registro P07-02: versão/hash, ambiente, cenário e resultado conforme trilha R1.
- Composição: implementação 1.5h, verificação 0.25h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P07-03 | Reaproveitar conclusão e cancelamento | 2h | R2

- Dependências: P07-02.
- Aceite: Conclusão tem resultado/evidência; cancelamento tem motivo e preserva histórico; repetição é segura.
- Evidência: Registro P07-03: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P07-04 | Conferir datas e indicação de atraso | 2h | R2

- Dependências: P07-03.
- Aceite: Brasília, virada de dia e prazo vazio têm regra definida; relógio controlado valida atraso sem esperar tempo real.
- Evidência: Registro P07-04: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P07-05 | Exibir pendência interna sem canal externo | 2h | R2

- Dependências: P07-04.
- Aceite: Operador vê próxima ação na aplicação; estado não é apresentado como e-mail/WhatsApp enviado.
- Evidência: Registro P07-05: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P07-06 | Demonstrar G-TASK e métricas básicas | 2h | R2

- Dependências: P07-05.
- Aceite: Contador reconcilia com listagem e período; somente o usuário permitido altera tarefa alheia.
- Evidência: Registro P07-06: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P08 | Terceiro pacote: protocolo e tramitação mínima | 24h | acumulado 164h

Resultado: Flow piloto com um tipo de protocolo e um fluxo fixo. Gate: G-FLOW. Origem: Novo, usando contratos de pessoas/documentos/tarefas.

### P08-01 | Especificar fluxo e numeração do piloto | 3h | N

- Dependências: P04-GATE, P06-GATE, P07-GATE.
- Aceite: Um tipo, sequência por tenant/ano, um responsável e estados aberto/em análise/concluído; sem designer.
- Evidência: Registro P08-01: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P08-02 | Criar protocolo e sequência transacional | 3h | N

- Dependências: P08-01.
- Aceite: Criação concorrente em SQL não repete número; retry da mesma operação devolve o mesmo protocolo.
- Evidência: Registro P08-02: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P08-03 | Vincular interessado, documento e responsável | 3h | N

- Dependências: P08-02.
- Aceite: IDs existentes usados; anexos privados e interessado do tenant correto; inexistente/empresa divergente é recusado.
- Evidência: Registro P08-03: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P08-04 | Criar consulta e histórico de movimentação | 3h | N

- Dependências: P08-03.
- Aceite: Listagem/detalhe/consulta por ID aplicam sigilo e tenant; histórico mantém origem, destino e ator.
- Evidência: Registro P08-04: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P08-05 | Implementar uma transição manual autorizada | 3h | N

- Dependências: P08-04.
- Aceite: Aberto -> em análise exige perfil previsto e versão atual; transição inválida não modifica estado.
- Evidência: Registro P08-05: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P08-06 | Implementar encerramento com resultado | 3h | N

- Dependências: P08-05.
- Aceite: Concluído exige resultado; segundo encerramento não duplica evento; edição concorrente gera conflito seguro.
- Evidência: Registro P08-06: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P08-07 | Conferir falhas e persistência do fluxo | 3h | N

- Dependências: P08-06.
- Aceite: Caminho feliz, ID de B, reenvio, duas pessoas, reload/restart e rollback transacional conferidos em SQL.
- Evidência: Registro P08-07: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P08-08 | Demonstrar G-FLOW e limites do piloto | 3h | N

- Dependências: P08-07.
- Aceite: Abrir -> anexar -> tramitar -> concluir -> consultar auditado; W1/W2 parcial, sem W3/W4, timers ou portal público.
- Evidência: Registro P08-08: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 1.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P09 | Empacotamento e homologação interna | 16h | acumulado 180h

Resultado: Release candidato do recorte, sem alegar produção. Gate: G-RC. Origem: Composição nova e regressões dos recortes.

### P09-01 | Reconciliar resultados e versão entregue | 2h | R2

- Dependências: P03-GATE, P05-GATE, P06-GATE, P07-GATE, P08-GATE.
- Aceite: Manifesto identifica hash/commit, configuração e testes; evidência de um módulo não certifica os outros.
- Evidência: Registro P09-01: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P09-02 | Conferir jornada de site e cadastro | 2h | R2

- Dependências: P09-01.
- Aceite: Jornada do site escolhido até canal/registro real de QA; nenhum CRM automático é presumido no pacote só site.
- Evidência: Registro P09-02: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P09-03 | Conferir jornada CRM em dois consumidores | 2h | N

- Dependências: P09-02.
- Aceite: Usuários permitidos/proibidos repetem contato, histórico e tarefa; contratos e IDs iguais nas configurações.
- Evidência: Registro P09-03: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P09-04 | Conferir jornada Flow e documento privado | 2h | N

- Dependências: P09-03.
- Aceite: Operador executa o fluxo fixo inteiro; consulta cruzada e download proibido continuam negados.
- Evidência: Registro P09-04: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P09-05 | Ensaiar atualização de banco e retorno | 2h | N

- Dependências: P09-04.
- Aceite: Banco sintético anterior migra, contagens/IDs se mantêm; rollback ou forward fix documentado e ensaiado.
- Evidência: Registro P09-05: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P09-06 | Ensaiar restore integrado e diagnóstico | 2h | N

- Dependências: P09-05.
- Aceite: Banco, arquivo e chaves recuperados em destino exclusivo; incidente tem traceId e procedimento de retorno.
- Evidência: Registro P09-06: versão/hash, ambiente, cenário e resultado conforme trilha N.
- Composição: implementação 0.75h, verificação 1h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P09-07 | Preparar operação e aceite do piloto | 2h | R2

- Dependências: P09-06.
- Aceite: Manual, responsáveis propostos, escopo de suporte e ficha de aceite disponíveis; aceite de usuário real ainda precisa ocorrer.
- Evidência: Registro P09-07: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P09-08 | Fechar candidato e backlog após 200h | 2h | R2

- Dependências: P09-07.
- Aceite: G-RC lista o que passou, bloqueios e próximas entregas; publicação/piloto real só com ambiente e autorização correspondentes.
- Evidência: Registro P09-08: versão/hash, ambiente, cenário e resultado conforme trilha R2.
- Composição: implementação 1.25h, verificação 0.5h, registro 0.25h, reserva 0h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

## P10 | Reserva protegida de correção | 20h | acumulado 200h

Resultado: Capacidade para corrigir e homologar sem aumentar escopo. Gate: CONDICIONAL. Origem: Contingência, consumida por necessidade.

### P10-01 | Reserva: onboarding e fixture de regressão | 4h | RES

- Dependências: defeito comprovado no recorte afetado.
- Aceite: Usar somente se login/harness bloquear os recortes; registrar defeito, horas reais e teste que deixou de falhar.
- Evidência: Registro P10-01: versão/hash, ambiente, cenário e resultado conforme trilha RES.
- Composição: implementação 0h, verificação 0h, registro 0h, reserva 4h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P10-02 | Reserva: isolamento e migração | 4h | RES

- Dependências: defeito comprovado no recorte afetado.
- Aceite: Usar para falha de tenant/SQL; reduzir funcionalidades opcionais se exigir mais tempo, sem cortar teste de segurança.
- Evidência: Registro P10-02: versão/hash, ambiente, cenário e resultado conforme trilha RES.
- Composição: implementação 0h, verificação 0h, registro 0h, reserva 4h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P10-03 | Reserva: extração e contratos do segundo consumidor | 4h | RES

- Dependências: defeito comprovado no recorte afetado.
- Aceite: Resolver acoplamento descoberto sem copiar regra por cliente; reavaliar custo/benefício da extração.
- Evidência: Registro P10-03: versão/hash, ambiente, cenário e resultado conforme trilha RES.
- Composição: implementação 0h, verificação 0h, registro 0h, reserva 4h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P10-04 | Reserva: documentos, recuperação e ambiente | 4h | RES

- Dependências: defeito comprovado no recorte afetado.
- Aceite: Fechar storage/restore/ambiente do recorte; falha de provedor externo não autoriza ativá-lo sem prova.
- Evidência: Registro P10-04: versão/hash, ambiente, cenário e resultado conforme trilha RES.
- Composição: implementação 0h, verificação 0h, registro 0h, reserva 4h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.

### P10-05 | Reserva: rodada adicional de homologação | 4h | RES

- Dependências: defeito comprovado no recorte afetado.
- Aceite: Repetir somente casos afetados por correção e fechar evidência; sobra mantém capacidade livre, sem inventar módulo.
- Evidência: Registro P10-05: versão/hash, ambiente, cenário e resultado conforme trilha RES.
- Composição: implementação 0h, verificação 0h, registro 0h, reserva 4h.
- Estado: planejado. Responsável proposto: desenvolvimento EBT.
