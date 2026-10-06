# ADR-001: preservar fontes e extrair recortes

Status: direção de planejamento; confirmação técnica do recorte em P02-01. Contexto: CASST/Vikings já fornecem domínio/UI/infra, mas possuem regras e alterações próprias.

Decisão recomendada: manter contratos/IDs, selecionar fluxo e extrair somente capacidade comum com segundo consumidor robusto. Marca/vocabulário configuráveis não autorizam renomear persistência. Não absorver PR draft Vikings sem sua revisão/gate.

Alternativas consideradas: reescrita integral (alto retrabalho e perda de conhecimento); cópia independente por cliente (correções divergentes); abstração universal antecipada (complexidade sem uso). Consequência: baseline e prova de compatibilidade precedem extração; nem todo domínio SST vira Core.

Revisitar se o recorte não puder ser licenciado, generalizado ou isolado com custo proporcional. Tickets: P01-01/P01-05/P02-01/P05-08.
