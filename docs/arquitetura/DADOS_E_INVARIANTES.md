# Modelo conceitual de dados e invariantes

Status: contrato candidato, a confrontar com fonte em P01/P05. Nomes técnicos existentes devem ser preservados quando compatíveis. Nenhuma tabela/migration foi criada por este documento.

| Conceito | Campos essenciais candidatos | Vínculo e regra |
|---|---|---|
| Empresa/contexto | ID interno, nome/configuração, estado do vínculo | Contexto resolvedor por identidade; registro compartilhado entre clientes tem escopo explícito |
| Usuário e vínculo | Subject/ID confiável, empresa, perfil/permissões, ativo | Sessão inválida ou vínculo inativo não autoriza acesso |
| Pessoa/organização/contato | ID interno existente, nome, canais mínimos, empresa | Uma identidade dentro do contexto; não unir pessoas globalmente por telefone/CPF |
| Interação | ID, contato, autor, instante/direção/tipo/texto permitido | Nota interna distinta de conversa; histórico antigo não altera última conversa por conveniência |
| Próxima ação/tarefa | ID, origem, responsável, prazo, estado, resultado/motivo | Responsável no escopo; conclusão/cancelamento preservam trilha |
| Documento/versão | ID, entidade ligada, tenant, categoria, key, MIME/tamanho/hash, versão, estado | Binário privado; versão antiga preservada; versão nova exige decisão própria |
| Revisão documental | Documento/versão, ator, instante, decisão/motivo | Não aprovar bytes diferentes silenciosamente; repetir comando não duplica evento |
| Protocolo | ID, tenant/ano/tipo/número, interessado, responsável, estado, versão | Número único por escopo; ID interno não é substituído pelo número exibido |
| Movimento | Protocolo, estado anterior/novo, origem/destino, ator, instante, resultado | Estado e histórico coerentes na mesma operação confirmada |
| Auditoria | Ator, empresa, operação, vínculo, instante, correlação, resultado | Conteúdo minimizado; resultado não inventa sucesso antes do commit |
| Operação repetível | Empresa, ação, chave lógica, resultado/estado, prazo de validade decidido | Mesma operação não produz novos registros após resposta perdida |

## Regras transversais

1. Nome de exibição não muda ID, enum, tabela ou endpoint persistido.
2. Vínculos entre módulos preservam a empresa; consultar FK de outro tenant não contorna autorização.
3. Unicidade global da fonte é revisada somente onde a regra exige independência por empresa.
4. Cada escrita crítica define concorrência: token de versão existente, ETag ou equivalente compatível. P01 registra o mecanismo; nenhum nome é imposto sem conferência.
5. Datas de evento persistem com referência temporal inequívoca; UI exibe Brasília. Vencimento sem horário ou sem prazo tem regra fechada antes de testar.
6. Mudança relevante de estado preserva histórico e exige operação autorizada.
7. Cadastro, evento e metadados que precisam ser atômicos compartilham limite transacional definido. Storage fora da transação SQL requer estado pendente e reconciliação explícita.
8. Soft delete, retenção e eliminação não são aplicados universalmente por estilo. Fechar política da categoria no recorte.

## Identidade de pessoas

CRM usa identidade de cadastro; SST acrescenta emprego/alocação/exposição temporal. Matrícula externa, telefone ou nome não substituem o ID interno. Empregador não é tomador. Este ciclo não migra vínculos Vikings nem constrói cadastro pessoal global de todos os clientes EBT.

## Concorrência do protocolo

P08-02 deve registrar a estratégia SQL escolhida: incremento/linha de sequência protegido, transação e índice único do escopo, ou mecanismo equivalente comprovado. Não aceitar apenas calcular max+1 no código. O teste disputa duas requisições, repete uma chave de operação e verifica estado após falha/rollback.
