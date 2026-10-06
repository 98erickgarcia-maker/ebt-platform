# EBT Platform | Planejamento incremental

Primeiras **200 horas**, organizadas em **77 pequenos itens**: 72 entregas planejadas e 5 reservas condicionais.

Comece pelo [plano executivo](docs/PLANO_200_HORAS.md) e pelo [backlog detalhado](docs/BACKLOG_200_HORAS.md). O [PDF consolidado](output/pdf/EBT_Plano_Primeiras_200_Horas.pdf) reúne revisão, fases, critérios e fontes.

Este é um repositório de planejamento. Não afirma que o novo Core ou os módulos planejados estão implementados ou publicados. As fontes CASST/Vikings/EBT/CRP/Nutrição permanecem nos projetos originais.

## Conferir o planejamento

```powershell
python scripts/verificar_plano.py
```

Para gerar novamente os documentos, `scripts/planejar.py` requer Python, reportlab e acesso às fontes/CLI GitHub listados no script. Ele grava somente neste repositório e não executa testes das aplicações. Regerar atualiza o inventário temporal; não é necessário para consultar o plano ou verificar orçamento/dependências.
