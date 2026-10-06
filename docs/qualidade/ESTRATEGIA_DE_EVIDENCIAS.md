# Estratégia de evidências e verificação proporcional

## Níveis separados

| Nível | O que demonstra | O que não demonstra |
|---|---|---|
| Documento/inspeção | Estrutura, contrato e proposta identificados | Execução funcional |
| Build/teste local | Cenários daquela versão e ambiente | Aceite do cliente ou produção |
| CI | Workflow e casos executados no commit consultado | Tudo que não faz parte daquele workflow |
| QA autenticado | Jornada dos perfis e dados usados | Integração de fornecedor sem sandbox/prova |
| Homologação do usuário | Aceite do cenário com autoria e versão | Escopos não executados |
| Produção verificada | Revisão implantada, saúde e smoke do escopo | Ausência universal de defeitos ou conformidade ampla |

## Reusar prova

Associar cenário, versão/hash, configuração relevante, ambiente e resultado. Confirmar equivalência do comportamento; diferenças em schema, policy, cache, DTO, conexão ou storage invalidam a dispensa de regressão do caso afetado. Evidence histórica da revisão permanece em inventario_fontes.json e github_vikings_snapshot.json com sua data. Não atualizar seus timestamps para aparentar uma consulta nova.

## Casos

planejamento/cenarios_verificacao.json define cenário por ticket e estado nao_executado. Cada cenário é um recorte verificável, não necessariamente um novo teste automático. Usar suíte existente que realmente cobre o comportamento; adicionar caso novo apenas quando regra/fronteira/defeito novo exigir.

R1: origem/hash/diff, smoke e visual/build pertinente. R2: contrato, resultado persistido, vínculo e consumidores afetados. N: negativas, SQL real, idempotência, concorrência e recuperação pertinentes ao critério. RES: selecionar casos afetados pelo incidente real. Não repetir indiscriminadamente a suíte inteira a cada alteração textual.

## Registro mínimo

ID de cenário/ticket; versão/hash; fonte/config relevante; ambiente; dados sintéticos; passos; expectativa; observado; comando/artefato de prova; resultado; limite; autoria/data. Resultado nao_aplicavel exige motivo aprovado para o recorte e não pode excluir o único caso de segurança/banco que sustenta o gate.

## Falhas históricas

CASST: SQL conclusivo aprovado é distinto de retestes anteriores falhos; onboarding continua pendência observada na revisão de origem. Vikings: main/PR têm prova temporal de CI, sem aceite operacional. EBT/CRP/Nutrição: publicação/backup registrados são históricos, sem repetição atual por esta organização documental.

## Sanitização

Não versionar token, senha, string de conexão privada, banco, documento real ou convite individual. Capturas/logs pertinentes devem limitar dados à massa sintética e aos campos de diagnóstico seguros. Guardar bytes privados e credenciais no ambiente apropriado, fora da documentação de consulta.
