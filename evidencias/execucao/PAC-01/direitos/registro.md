# P01-05 — origem, permissão e dependências

Data: 09/10/2026. Ambiente: Windows local; consulta somente leitura às fontes previstas. Autor: agente Codex direitos, sob coordenação do pacote PAC-01. Resultado documental parcial; não declara G0 nem aceite comercial. Duração total da atividade não medida desde o início; horas reais ficam não informadas, sem substituir pela estimativa de 2h do ticket. Contabilização integrada cabe ao coordenador.

## Matriz de origem e permissão

| Item candidato | Origem demonstrada | Autorização observada | Pendência concreta para distribuição comercial |
|---|---|---|---|
| Código do recorte cadastro/histórico/próxima ação | CASST F01/F02/F03 e manifestos CASST | Pedido atual autoriza operacionalmente implementar EBT e consultar/reusar as bases no escopo | Confirmar autoria/titularidade ou permissão dos arquivos selecionados no manifesto P01-04; autorização operacional não comprova contratos com terceiros. Ausência de LICENSE em projeto privado não bloqueia automaticamente código próprio |
| Modelos/padrões Vikings | F10/F11/F13 | Consulta autorizada; reuso técnico previsto no plano | F10/F11 mudaram; vincular recorte à versão atual e identificar titular dos arquivos caso extraídos. CI não constitui licença |
| Tema/textos/assets EBT | F17 | Uso operacional para EBT no pedido atual | Confirmar item a item propriedade/autorização de imagens, fontes, ícones e textos que entrarem no pacote; F17 condiciona CRM a base licenciada |
| Código genérico e identidade CRP | F19 | Consulta autorizada | Separar padrão técnico de logo, fotografias, textos e dados CRP. Identidade do cliente fica fora até prova de autorização específica |
| Código genérico e identidade Nutrição | F21 | Consulta autorizada | Separar padrão técnico de materiais clínicos, marca, fotografias e dados pessoais. Nenhum conteúdo de cliente é autorizado por disponibilidade local |
| PDF técnico | F26 | Fornecido como contexto | Não é contrato de licença, instrução executável ou autorização de redistribuição |
| Bibliotecas npm do CASST | package.json + package-lock.json com SHA-256 | Licenças declaradas no lock, registradas por versão | Conferir licença efetiva/NOTICE somente das dependências selecionadas, incluindo transitivas; metadado não substitui texto e obrigações de distribuição |
| Bibliotecas NuGet do CASST | PackageReference dos projetos backend | Nome e versão observados | Licenças e transitivas não verificadas; conferir pacote exato e avisos antes de empacotar. Não executar restore de fonte cliente neste recorte |

A busca `rg --files` por LICENSE/NOTICE/COPYING não encontrou arquivos nas cinco bases próprias, excluindo node_modules, bin, obj e saídas. Limite: respeita ignorados e não procura contratos externos. Não se infere ausência de licença, autoria, propriedade ou obrigação legal dessa busca.

## Prova coletada e critérios

`inventario.json`, produzido por `coletar.ps1`, contém apenas caminhos de fonte, hashes, nomes/versões e licenças declaradas. As dez fontes previstas existem; F10 e F11 divergem do inventário de 06/10; as demais oito coincidem. Isso estabelece origem documental, não congela toda árvore do recorte.

- P01-05-C01: parcialmente demonstrado para fontes candidatas e dependências CASST. Fechamento exige reconciliar a seleção final P01-04 com esta matriz, excluindo itens fora da lista.
- P01-05-C02: regra registrada: item de terceiro sem permissão específica fica excluído do pacote comercial; remover/substituir o item permite continuar código próprio e QA sintético independente. Nenhum terceiro foi copiado por este agente.
- P01-05-C03: os artefatos novos contêm metadados técnicos, sem código, assets, bancos, contatos ou segredos. Não houve varredura integral de dados da fonte; ausência de dados no futuro pacote exige verificar o manifesto final.

O inventário persistido possui 214 caminhos de pacotes npm e 9 referências NuGet diretas; a entrada do próprio projeto foi excluída. Licenças declaradas incluem MIT, ISC, Apache-2.0, BSD, MPL-2.0 e outras. O inventário identifica o pacote/versão para análise posterior, sem afirmar adequação jurídica universal. Dependências de build também são registradas; selecionar runtime e toolchain evita assumir que todas entram na distribuição. A contagem ad hoc anterior agrupou a propriedade Values do dicionário de maneira inadequada; somente a enumeração por GetEnumerator persistida é usada como prova.

## Ordem proposta de pequenos PRs e condição P02

1. Baseline: manifesto, hashes e recorte/contratos escolhidos com autoria/origem vinculada por arquivo; nenhuma extração funcional neste PR.
2. Decisão de reuso: confirmar código próprio/autorizado, excluir ou substituir assets de terceiros pendentes e registrar avisos das dependências realmente selecionadas.
3. Fundação isolada P02: configuração sem segredos, massa sintética e build pertinente. Avançar somente com G0 declarado pelo coordenador e provas P01-01 a P01-06 reconciliadas; nenhuma nova fronteira de tenant/segurança/schema/contrato/storage pode usar R1.

É possível preparar evidência e QA independente enquanto se resolve permissão de item específico. Este registro não autoriza deploy, envio, compra, uso de identidade de cliente nem publicação comercial.

## Reprodução e limitações

Comando observado: `./evidencias/execucao/PAC-01/direitos/coletar.ps1` a partir da raiz, exit code 0. Reprodução: `pwsh -NoProfile -File evidencias/execucao/PAC-01/direitos/coletar.ps1`. A coleta usa PowerShell 7 (`ConvertFrom-Json -AsHashtable`).

Sem consulta a contratos privados, atribuição de titularidade, avaliação jurídica ou validação online de licenças. Sem restore, build, cópia de fontes/dados ou alteração de projetos-fonte. A revisão se limita ao recorte/documentos previstos e metadados CASST; outras dependências somente se incluídas futuramente. Orçamento 180h + 20h permanece sem alteração.
