# EBT Flow — protocolo fixo, validação e limites

## Recorte implementado

- `GET /api/flow/v1/protocols`: até 100 protocolos recentes, filtrados por tenant/carteira.
- `POST /api/flow/v1/protocols`: assunto, chave idempotente e número por tenant/ano. App lock transacional por tenant protege chave e sequência; rollback abrange protocolo e movimento.
- `POST /api/flow/v1/protocols/{id}/transition`: open → in_review → complete, versão If-Match e resultado obrigatório ao concluir.
- `GET /api/flow/v1/protocols/{id}/history`: movimentos, resultado, autor e data; acesso por ID também respeita tenant/carteira.
- SQL `ebt_flow` com RLS de filtro/bloqueio própria. Cada conexão direta define `ebt_tenant` e desativa `ebt_system`; autorização de carteira permanece no servidor.
- Runtime recebe SELECT/INSERT/UPDATE somente em Protocols e SELECT/INSERT em Movements. Alteração direta do histórico e DDL não são concedidos.

## Evidência atual de QA

`evidencias/flow_protocol_sql_qa_20261009.json` registra 28 verificações aprovadas em **novo banco SQL local exclusivo**, com hashes de script/fonte/cenário. Build backend Release aprovado sem avisos/erros antes dessa execução.

Comando: `python tests/integration/flow_protocol_qa.py`. O teste gera configuração/senhas sintéticas privadas, inicializa um banco `EbtPlatformQa_Flow_<unique>`, aplica a migração duas vezes e exige transação encerrada. Cobre 16 criações concorrentes com sequência contígua, oito replays simultâneos com ID único, mismatch, tenant B, carteira alheia, reader, entradas inválidas, versão/transição negada, histórico persistido e resultado.

Provas SQL incluem leitura RLS sem contexto/tenant A, INSERT de B bloqueado para principal restrito, grants por objeto sem UPDATE de histórico/DDL, falha sintética de movimento com rollback integral, reinício com sessão/histórico preservados e backup COPY_ONLY/CHECKSUM restaurado em **outro banco local QA**, com hashes iguais de Protocols/Movements. Não sobrescreve banco de origem nem toca produção.

## Gates de publicação

1. Fixar SHA candidato e conferir CI/build frontend/backend e UI integrada nas larguras previstas. Hash de QA identifica os arquivos testados; qualquer mudança funcional posterior exige repetir os cenários afetados.
2. Conferir host existente, identidade, versão anterior, recovery e destino compartilhado autorizado antes da migração. `--flow-database` exige destino Azure específico, hash aprovado, prefixo do script e grants nos objetos explícitos.
3. Registrar migração, preservação dos demais schemas, revisão/digest e testes HTTPS/autenticados online em prova separada. QA local e build não comprovam publicação.
4. Disponibilidade no catálogo só acompanha a implantação realmente verificada. Aceite operacional do usuário é posterior e não é inferido de CI ou smoke.

## Limites do recorte

Este é o primeiro módulo de protocolo/tramitação fixa. Não inclui vínculo com contato, anexos privados ou tarefas vinculadas no protocolo, workflows configuráveis, notificações, assinatura digital ou homologação de cliente. EBT AURA é linguagem visual; não um segundo aplicativo executável. A comprovação de restore é sintética/local e não equivale a ensaio PITR do Azure compartilhado. Orçamento global continua 180h de entregas + 20h de reserva; horas reais não foram inferidas destes testes.
