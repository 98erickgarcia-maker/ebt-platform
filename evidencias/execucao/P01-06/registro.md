# P01-06 — registro de execução

Data: 07/10/2026.

## Baseline

O baseline do EBT Connect está em:

- `docs/execucao/PAC01_BASELINE_EBT_CONNECT_2026-10-07.md`;
- `docs/design/EBT_CONNECT_DESIGN_SYSTEM_V1.md`.

## Fila de implementação

1. estrutura real do produto;
2. Design System e shell EBT;
3. dados sintéticos e configuração A/B;
4. SQL/diagnóstico/CI;
5. segurança/tenant;
6. CRM Connect funcional.

## Cenários

- P01-06-C01 — gate indica passou/pendências: **registrado no baseline**.
- P01-06-C02 — recorte não inicia vermelho: **nenhum teste runtime EBT existe ainda; início de código depende de PAC-02**.
- P01-06-C03 — bases não alteradas: **validado para esta execução**.

G0 é candidato a fechamento após revisão do diff e CI documental desta branch.
