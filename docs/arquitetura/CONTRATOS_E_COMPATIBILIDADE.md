# Operações candidatas e compatibilidade

O catálogo é de operações esperadas, não de URLs já implementadas. P01-04 associa cada operação a endpoint, método, DTO, política e produtor/consumidor reais. Contrato existente compatível é reaproveitado; breaking change tem versão ou migração explícita.

| Operação | Entrada mínima candidata | Resultado confirmado | Casos que não confirmam sucesso |
|---|---|---|---|
| Criar contato | Nome/canal mínimo e chave de repetição quando pertinente | ID interno e estado persistido | Entrada inválida, empresa indevida, repetição conflitante |
| Listar/buscar | Filtros e paginação limitada | Itens somente do escopo | Token inválido, filtro não permitido |
| Registrar interação | Contato, tipo/direção, instante, texto permitido | Evento ligado ao mesmo ID | Cadastro ausente, perfil proibido, commit falho |
| Definir próxima ação | Contato/origem, responsável, prazo/descrição, versão | Estado e histórico persistidos | Responsável inativo, versão obsoleta |
| Mudar etapa | ID, etapa permitida, versão esperada | Etapa atual e trilha | Transição indevida, conflito |
| Preparar importação | Layout fixo, até 100 registros sintéticos | Preview/erros sem mutação definitiva | Linha inválida, arquivo fora do layout |
| Confirmar importação | Operação preparada e chave de repetição | Resultado persistido por linha/lote | Layout alterado, confirmação sem preview válido |
| Enviar documento | Entidade/categoria e arquivo permitido | Metadado/hash/versão pendente | Tipo/tamanho inválido, storage falho |
| Revisar documento | ID/versão, decisão/motivo, versão esperada | Decisão da versão exata | Arquivo substituído, ator proibido, concorrência |
| Baixar documento | ID do recurso, sessão autorizada | Bytes corretos ou acesso autorizado temporário | Outro tenant, categoria restrita, binário inexistente |
| Concluir tarefa | ID, resultado, versão | Estado e trilha de conclusão | Sem resultado, recurso alheio, conflito |
| Abrir protocolo | Tipo/ano, interessado, responsável, chave de operação | ID e número único | Vínculo de B, repetição incompatível, transação falha |
| Tramitar/concluir | Protocolo, ação autorizada, versão e resultado quando requerido | Estado + evento coerentes | Estado inválido, segunda atualização obsoleta |

## Padrão transversal

Erro estruturado tem código seguro e correlação sem dados desnecessários. A semântica de 401/403/404/409 e validação deve ser conferida no contrato existente: identidade ausente, ação proibida, recurso indisponível ao contexto, concorrência e entrada inválida não se confundem. Não mudar status/corpo HTTP apenas para simplificar teste.

Para comandos repetíveis, registrar escopo da chave, armazenamento do resultado, duração e comportamento para payload diferente. Para edição concorrente, registrar fonte do token e resposta de conflito. Para arquivos, cliente HTTP reusa tratamento de sessão e diagnóstico de download.

## Quadro de contrato por ticket

Usar templates/CONTRATO.md: operação; fonte; endpoint/método reais; DTO request/response; ID de origem; vínculos; policy; efeitos/cache; repetição; concorrência; erro; consumidor adicional; cenário; versão. Campos não descobertos ficam pendentes, sem exemplo apresentado como API operacional.
