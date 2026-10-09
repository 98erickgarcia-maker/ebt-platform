# Revisão independente do PAC-01

09/10/2026. Revisão estática somente leitura das saídas dos outros agentes; alterações limitadas a este diretório direitos. Não declara gate, runtime ou homologação. Duração desta revisão não medida desde início.

## Achados acionáveis

1. **P2 — referências de linha incompatíveis com versão hashada.** `contratos/registro.md` cita ProspectContracts.cs:334 e intervalo 283-327, enquanto `contratos/fontes-hashes.json` registra 324 linhas. Cita CommercialInteractionContracts.cs:309, mas o arquivo tem 296 linhas. A consulta atual confirma CompletionResponse nas linhas 289-291. Corrigir todas as referências com base nos arquivos congelados antes de afirmar rastreabilidade das regras. Não invalida automaticamente os nomes de contratos, mas impede localizar a prova citada.
2. **P2 — reconciliar última coleta antes do fechamento.** Durante a leitura, `baseline/manifesto-fonte.json` continha 594 arquivos e `verificacao_hashes.json` registrava 589 hashes. Pode resultar de atualização concorrente do agente baseline; não foi atribuída falsidade à evidência. Rodar a verificação final depois de estabilizar saídas e confirmar escopo/contagem compatíveis.
3. **Condição explícita — G0 não está automaticamente fechado.** O registro contratos deixa C01/C02 de P01-03 e C01 de P01-04 pendentes/parciais. Os testes históricos não têm manifesto da árvore executada. Direitos específicos de componentes/identidade de clientes precisam reconciliar lista selecionada e autorização observada. Consolidar critério documental vs demonstração de QA, sem elevar o produto a demonstrado ou homologado por haver hashes.

## Verificações sem achado adicional

- Os 20 arquivos de `contratos/fontes-hashes.json` têm correspondentes com hashes iguais em `baseline/manifesto-fonte.json` na leitura desta revisão.
- Baseline informa segunda passagem de hashes e status da fonte inalterado. Caminhos fora do recorte técnico são representados por hashes; não foram copiados conteúdos de cliente.
- Evidência histórica traz contadores TRX e ressalva explícita de ausência de vínculo à árvore atual. Não foi confundida com teste novo.
- Registro contratos distingue sete estados persistidos de cinco etapas propostas, idempotência automática de POST manual e SQLite de SQL real; preserva negativos de tenant, carteira, concorrência e cache para QA futuro.
- Reprodução do coletor direitos já estava corrigida para `pwsh -NoProfile -File ...`, compatível com `ConvertFrom-Json -AsHashtable`. `pwsh` existe no ambiente. Não executar via Windows PowerShell 5; nenhum arquivo de outros agentes foi alterado para corrigir instruções.

## Limites

Na revisão não havia registro consolidado PAC-01/P01-06 nem fechamento do registro baseline, somente JSONs/script; ausência registrada como limite temporal. Não houve leitura integral de todas as fontes nem execução funcional. As saídas podem mudar após esta revisão; coordenador deve verificar correções e manifesto final antes de declarar gate. Nenhum segredo ou dado real foi copiado para esta revisão.

## Reavaliação de fechamento

Consulta posterior em 09/10/2026 após entrega do consolidado:

- Achado 1 **resolvido**: `contratos/registro.md` agora cita ProspectContracts.cs:315-321 e :280-313, CommercialInteractionContracts.cs:289. Essas referências cabem nos arquivos congelados; CompletionResponse foi conferido em :289-291. `contratos/verificacao.json` registra a rechecagem estática aprovada dos hashes. Isso resolve as referências apontadas, sem alegar revisão integral de toda linha do mapa.
- Achado 2 **resolvido**: `verificacao_hashes.json` de 2026-10-09T17:39:57.771288+00:00 informa `passed=true`, `hashes_checked=594`, erros vazios; coincide com a baseline final. Não é backup ou teste funcional.
- Condição G0 **aberta e corretamente declarada** em `PAC-01/registro.md`: versão recuperável sanitizada, reconciliação dos critérios e permissões específicas pendentes. PAC-02 não foi iniciado. Consolidado distingue planejamento, inspeção, QA, homologação e salvamento remoto.
- Registro baseline e consolidado agora usam 174,514 segundos como limite inferior da janela observada por metadados. Nenhuma soma de horas-pessoa ou equivalência a estimativa foi inferida.
- Limite temporal anterior sobre ausência de consolidação **resolvido**: registro PAC-01 e baseline estão disponíveis e foram lidos. Limitações de teste funcional, licenças efetivas e preservação recuperável permanecem.

Não foram encontrados novos achados acionáveis nessa reavaliação focal. A inspeção parcial de documentos/metadados não certifica ausência global de segredos ou dados pessoais no repositório ou fontes. Nenhuma afirmação desse alcance deve ser derivada da revisão.
