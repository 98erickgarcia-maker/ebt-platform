# G1 — Fundação mínima para trabalhar

Fase: P02 — Fundação mínima para trabalhar.

Gate: **G1**.

Data: 07/10/2026.

Versão conferida: `4df19c2fd84da1b06d5e4f8bda283cf4860e3473`.

Resultado: **APROVADO PARA O ESCOPO DE FUNDAÇÃO QA**.

## Tickets pertinentes

- P02-01 — arquitetura e limite do Core: validado no PAC-02;
- P02-02 — estrutura/build reproduzível: validado no PAC-02;
- P02-03 — configuração/segredos: validado no PAC-02;
- P02-04 — massa sintética A/B: validado no PAC-02;
- P02-05 — banco/storage QA: validado;
- P02-06 — cliente HTTP/erros: validado;
- P02-07 — CI/diagnóstico seguro: validado;
- P02-08 — demonstração integrada: validado.

## Evidência mínima exigida pelo gate

| Evidência G1 | Resultado |
|---|---|
| ambiente isolado | SQL Server + Azurite efêmeros exclusivos do CI |
| build reproduzível | workflow de fundação verde em checkout limpo |
| CI pertinente | runs `37686069814`, `37686069941` e `37686069789` verdes |
| health | live/ready e dependências SQL/Blob verificadas |
| massa própria | consumidores/registro/anexo exclusivamente sintéticos |
| persistência QA | save/reload SQL + upload/download Blob demonstrados |

## Negativas e segurança do gate

- destino fora do padrão QA é recusado;
- nomes com indicação de produção são recusados;
- ausência de configuração privada de QA falha com mensagem segura;
- health não expõe connection string/senha;
- traceId não contém cadastro;
- binário não é armazenado como coluna do metadado SQL;
- workflow não acessa nenhum banco/storage externo de cliente.

## Falhas encontradas durante execução

Duas falhas de compilação foram detectadas pelo CI durante o desenvolvimento e corrigidas antes deste gate:

1. literal inválido na normalização de content type em C#;
2. parameter properties incompatíveis com o modo TypeScript estrito.

Nenhuma falha do gate permanece aberta no commit conferido.

## Consumidores liberados neste escopo

Somente desenvolvimento/QA da fundação EBT Platform com massa sintética.

## Não aplicável / não aprovado por G1

- produção;
- login real;
- sessão/CSRF final;
- autorização;
- isolamento de tenant A/B por SQL;
- acesso por ID negativo;
- onboarding E2E;
- dados ou credenciais de cliente;
- backup/restore de produção;
- implantação 24/7.

Esses itens pertencem aos gates posteriores, principalmente G-SEG.

## Próximo passo

Avançar para o próximo pacote do planejamento sem tratar G1 como autorização de produção. A próxima fronteira crítica para uso multiempresa é segurança/tenant; qualquer módulo de negócio que dependa disso deve permanecer bloqueado até seu gate.
