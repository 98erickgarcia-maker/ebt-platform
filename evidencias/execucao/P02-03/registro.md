# P02-03 — configuração e segredos por ambiente

Data: 07/10/2026.

Versão executada: `03e0928d2670fe14fa7d96c20037efee0ddbcab7`.

## Implementação

- base: `appsettings.json`, sem segredo;
- Development: massa sintética habilitada e nenhuma configuração privada exigida;
- Production: massa sintética desligada e presença de configuração privada obrigatória;
- nenhum valor de conexão foi versionado;
- `PrivateConfigurationGuard` falha com mensagem genérica.

## Testes

Teste `Missing_required_private_configuration_fails_with_safe_message`:

- ausência de configuração obrigatória gera falha;
- mensagem retornada: `Configuração privada obrigatória não foi fornecida.`;
- nome da variável privada não aparece na mensagem.

Teste `Development_configuration_does_not_read_production_secret`:

- Development não consulta configuração privada de produção.

CI:

- etapa `Verificar padrões de segredo rastreados`: **success**;
- auditoria de dependências backend/frontend: **success**.

## Casos

- P02-03-C01 — config ausente falha com mensagem segura: **validado**.
- P02-03-C02 — Dev não usa produção: **validado**.
- P02-03-C03 — secret não aparece em arquivo rastreado: **validado para os padrões automatizados e arquivos desta fundação**.

## Limite

A varredura é uma barreira preventiva, não substitui secret scanning corporativo futuro nem revisão de credenciais em provedores externos.
