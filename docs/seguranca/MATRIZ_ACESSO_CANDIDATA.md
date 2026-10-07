# Matriz de acesso candidata — EBT Platform

Status: candidata do PAC-05. G-SEG permanece pendente até PAC-07.

| Papel | Ler registro | Criar/alterar registro | Baixar anexo | Diagnóstico técnico |
|---|---:|---:|---:|---:|
| Administrador | sim | sim | sim | sim |
| Operador | sim | sim | sim | não |
| Consulta | sim | não | sim | não |
| Suporte técnico | não | não | não | sim, sem conteúdo do cliente |

Regras:

- tenant vem da identidade ativa conhecida pelo servidor;
- header, query string e body não escolhem tenant;
- suporte técnico não ganha acesso a registros/anexos por ser suporte;
- autorização de recurso é feita no servidor;
- sessão QA/Development é sintética e não representa identidade de produção;
- login sintético é indisponível fora de QA/Development.
