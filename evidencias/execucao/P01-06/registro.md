# P01-06 — registro de execução

Data: 07/10/2026.

## Baseline

O baseline do EBT Connect está em:

- `docs/execucao/PAC01_BASELINE_EBT_CONNECT_2026-10-07.md`;
- `docs/design/EBT_CONNECT_DESIGN_SYSTEM_V1.md`;
- `evidencias/execucao/P01-01/source-manifest.json`.

## Fila de implementação

1. estrutura real do produto;
2. Design System e shell EBT;
3. dados sintéticos e configuração A/B;
4. SQL/diagnóstico/CI;
5. segurança/tenant;
6. CRM Connect funcional.

## Cenários

- P01-06-C01 — gate indica passou/pendências: **validado**; G0 libera somente a fundação PAC-02.
- P01-06-C02 — recorte não inicia vermelho: **validado para o contrato escolhido**; testes funcionais relevantes da fonte passaram, enquanto dependências vulneráveis/SQL E2E foram explicitamente excluídos como baseline.
- P01-06-C03 — bases não foram alteradas: **validado**; o trabalho desta fase está somente na EBT Platform.

## Resultado

G0 **aprovado para início do PAC-02**, desde que o commit mesclado preserve CI documental verde. O gate não aprova runtime, produção, tenancy ou segurança da nova plataforma.
