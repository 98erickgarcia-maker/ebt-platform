# EBT Platform: primeiras 200 horas e primeiras entregas

**77 pequenos itens: 72 entregas planejadas (180h) e 5 reservas condicionais (20h).** Estimativa em horas-pessoa, com implementação, verificação e registro incluídos. Cada item tem 2-4h. Este repositório contém o planejamento, não a implementação dos módulos.

A estratégia é reaproveitar o que tem prova e conferir somente o caminho afetado. A generalização de tenant, autenticação, autorização, índices, documentos e contratos novos recebe atenção maior. Primeiro preparar site essencial e CRM simples; depois documento/tarefas e um Flow piloto de escopo fixo.

## Primeiros projetos a entregar

| Ordem | Pacote | Janela cumulativa | Resultado após gate | Limite |
|---|---|---:|---|---|
| 1 | Site essencial reaproveitável | 28-40h | Até cinco páginas, contato, identidade e manual, demonstrados em QA | Não é Portal/CMS/transparência completo; publicação real depende do cliente/ambiente. |
| 2 | CRM simples / Connect inicial | 40-104h | Segurança + contato/organização/histórico/etapa/próxima ação em dois contextos sintéticos | Sem inbox multiusuário, WhatsApp oficial, financeiro ou OS. |
| 3 | Documentos e tarefas do recorte | 104-140h | Documento privado revisado/versionado + responsável/prazo/resultado | GED limitado; sem assinatura digital nem escalonamento externo. |
| 4 | Flow piloto | 140-164h | Um protocolo e um fluxo fixo com tramitação auditada | Novo; sem designer, branching, W3/W4, timers ou portal público. |
| 5 | Candidato para piloto interno | 164-180h | Jornadas integradas, migration/restore, manifesto e manual | Homologação real e produção ainda exigem execução/aceite próprios. |
| Reserva | Correções e homologação | 20h utilizáveis em qualquer fase | Proteção do orçamento e dos gates | Se faltar capacidade, Flow sai do ciclo; segurança não sai. |

As janelas são ordem de consumo de esforço, não datas, e pressupõem os gates anteriores. Evidência histórica é conferida por versão/escopo, sem retestar tudo por rotina. Nenhum ticket deve ser marcado concluído apenas por reutilizar código.

## Distribuição das 200 horas

| Bloco | Horas | Acumulado | Pequenos itens | Saída |
|---|---:|---:|---:|---|
| P01 Baseline e escolha do reaproveitamento | 12h | 12h | 6 | Mapa de fontes congeladas e primeiro fluxo escolhido |
| P02 Fundação mínima para trabalhar | 16h | 28h | 8 | Ambiente EBT isolado e verificações automatizadas |
| P03 Primeiro pacote: site essencial reutilizável | 12h | 40h | 6 | Pacote de site pronto para demonstração e implantação delimitada |
| P04 Identidade, isolamento e auditoria | 36h | 76h | 12 | Base segura para primeiro CRM em dois contextos sintéticos |
| P05 Segundo pacote: CRM simples / Connect inicial | 28h | 104h | 10 | CRM demonstrável com cadastro único e próxima ação |
| P06 Documentos privados, recorte GED | 24h | 128h | 8 | Um fluxo de documento com versão, permissão e histórico |
| P07 Tarefas e prazos ligados ao cadastro | 12h | 140h | 6 | Pendências internas com responsável e histórico |
| P08 Terceiro pacote: protocolo e tramitação mínima | 24h | 164h | 8 | Flow piloto com um tipo de protocolo e um fluxo fixo |
| P09 Empacotamento e homologação interna | 16h | 180h | 8 | Release candidato do recorte, sem alegar produção |
| P10 Reserva protegida de correção | 20h | 200h | 5 | Capacidade para corrigir e homologar sem aumentar escopo |

**Total: 200h.** Referência do PDF: Core completo estimado em ~300-500h com CASST reutilizável; este recorte não promete substituí-lo por um Core integral de 200h.

## Leitura e execução

- [Revisão do que existe](REVISAO_BASES.md).
- [77 itens com aceite e dependência](BACKLOG_200_HORAS.md).
- [Validação proporcional e gates](VALIDACAO_E_GATES.md).
- [Fontes e limites](FONTES_E_LIMITES.md).
- [Dados estruturados do backlog](../planejamento/backlog_200_horas.json).
- [PDF consolidado](../output/pdf/EBT_Plano_Primeiras_200_Horas.pdf).
