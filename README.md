# EBT Platform | Projeto organizado para execução incremental

**Planejamento finalizado. Implementação dos módulos ainda planejada.**

200 horas-pessoa: 72 entregas pequenas (180h) e cinco reservas condicionais (20h). A organização preserva o orçamento e torna cada recorte consultável por entrada, saída, passo, cenário, fonte e gate.

## Comece aqui

- [Índice geral de todos os documentos](docs/INDICE_GERAL.md).
- [Plano executivo e primeiras entregas](docs/PLANO_200_HORAS.md).
- [Roteiro para executar e continuar](docs/execucao/COMO_EXECUTAR_E_CONTINUAR.md).
- [Dependências e gates](docs/execucao/DEPENDENCIAS.md).
- [Backlog resumido](docs/BACKLOG_200_HORAS.md).
- [PDF consolidado com manual detalhado](output/pdf/EBT_Plano_Primeiras_200_Horas.pdf).
- [Continuidade em outro chat](CONTINUAR_EM_OUTRO_CHAT.md).

## Ordem de entregas

| Resultado candidato | Esforço cumulativo | Marco |
|---|---:|---|
| Site essencial | 40h | G-SITE |
| Segurança e CRM simples | 104h | G-SEG / G-CRM |
| Documentos privados e tarefas | 140h | G-GED / G-TASK |
| Protocolo e tramitação piloto | 164h | G-FLOW |
| Candidato interno e operação | 180h | G-RC |
| Reserva condicional | 20h utilizáveis em qualquer fase | Sem obrigação de consumo |

## Onde está cada informação

| Diretório | Finalidade |
|---|---|
| docs/gestao | Escopo, resultados, responsabilidades, decisões e contingência |
| docs/arquitetura | Fronteiras, dados, operações, permissões e ADRs candidatos |
| docs/produtos | Site, CRM, documentos/tarefas, Flow e candidato |
| docs/execucao/fases | Dez fases com entradas, tickets e gates |
| docs/execucao/entregas | 77 fichas individuais com passos e cenários específicos |
| docs/qualidade | Matriz de casos e níveis de evidência |
| docs/operacao | Configuração, migration, restore, release, acesso e incidente |
| templates | Oito registros reutilizáveis, sem resultados preenchidos |
| planejamento | Fonte do orçamento/status e catálogos estruturados derivados |
| evidencias | Provas históricas da revisão e verificações documentais atuais |
| output/pdf | Documento principal para leitura/compartilhamento |
| scripts | Geradores e verificadores documentais, não código dos produtos |

## Verificar sem instalar a plataforma

```powershell
python scripts/verificar_plano.py
python scripts/verificar_organizacao.py
```

A verificação estrutural usa Python 3.12+ e sua biblioteca padrão. A conferência de conteúdo PDF usa PyMuPDF quando disponível; renderização e atualização do PDF exigem PyMuPDF/reportlab. Esses comandos não executam as suítes CASST/Vikings nem acessam bancos ou implantam aplicações.

## Fonte de verdade e edição

Horas/IDs/status: planejamento/backlog_200_horas.json. Conteúdo específico das fichas: scripts/catalogo_organizacao.py. Documentos de organização: scripts/conteudo_organizacao.py. Gerar com scripts/organizar_projeto.py; o manifesto detecta alterações manuais em gerados e impede sobrescrita silenciosa. Atualizações planejadas devem ser revisadas pelo diff.

O gerador histórico scripts/planejar.py fica protegido para não apagar a organização posterior. Fontes CASST/Vikings/EBT/CRP/Nutrição permanecem nos repositórios originais. Configuração candidata não é módulo implementado; prova histórica não certifica extração futura. Reuso comprovado recebe conferência focal e nova fronteira de segurança/schema/contrato/storage recebe validação maior.
