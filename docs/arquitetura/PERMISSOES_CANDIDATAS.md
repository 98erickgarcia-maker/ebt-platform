# Matriz candidata de acesso do piloto

P04-01 confirma a matriz com o responsável de negócio. Os nomes de papéis abaixo organizam a conversa; não são roles criadas ou contas reais. Permissão de empresa, carteira/recurso e ação é conferida no servidor.

| Ação | Administração do contexto | Operação designada | Consulta designada | Apoio técnico |
|---|---|---|---|---|
| Consultar contatos | Dentro do contexto permitido | Dentro da carteira permitida | Somente carteira autorizada | Não recebe conteúdo por padrão |
| Criar/alterar contato | Se a policy autorizar | Se a policy autorizar | Negado | Negado por padrão |
| Registrar interação/próxima ação | Se autorizado no recurso | Se autorizado no recurso | Negado | Negado por padrão |
| Importar o recorte | Ação específica autorizada | Somente se delegada | Negado | Não concede importação por suporte |
| Enviar documento | Categoria/recurso permitidos | Categoria/recurso permitidos | Negado | Negado por padrão |
| Revisar/liberar documento | Permissão explícita de revisão | Somente se delegada | Negado | Não concede revisão por suporte |
| Baixar documento | Categoria/recurso permitidos | Categoria/recurso permitidos | Somente categoria liberada ao papel | Negado por padrão |
| Alterar tarefa/protocolo | Policy e recurso permitem | Designação/escopo permitem | Negado | Negado por padrão |
| Consultar auditoria | Ação específica e conteúdo minimizado | Apenas histórico funcional permitido | Apenas histórico permitido | Diagnóstico sanitizado quando autorizado |
| Configurar identidade/perfis | Permissão administrativa específica | Negado por padrão | Negado | Somente autorização específica e auditada |

## Casos mínimos de fronteira

Usuário de B tentando ID de A; operador fora da carteira; consulta tentando escrita; sessão revogada; usuário sem vínculo; troca A/B com cache; arquivo restrito; exportação fora do escopo; header adulterado; cadastro/arquivo de B vinculado a processo de A. Esses casos são mapeados aos tickets e não dispensados por origem já testada.

Ausência de botão não substitui recusa de API. Perfil admin não confere automaticamente acesso a categoria sensível ou a todos os clientes. Não criar usuários reais para preencher a matriz do planejamento.
