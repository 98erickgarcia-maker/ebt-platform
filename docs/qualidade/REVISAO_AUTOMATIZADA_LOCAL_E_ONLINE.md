# Revisão automatizada local e online

## Decisão de execução

Visualizar online significa principalmente executar código de verificação contra o endereço de homologação. A conferência manual complementa a automação na avaliação visual e no aceite de negócio. Esta especificação é futura: este repositório ainda não contém suíte de aplicação/browser implementada.

Os testes ficam em projeto/pasta de QA apropriada à stack escolhida, separados do código funcional. Os mesmos cenários aplicáveis podem rodar localmente e em homologação com configuração de destino, usuários sintéticos e adaptadores próprios do ambiente. Escolher ferramenta/comandos durante a fundação, conforme os projetos-fonte, sem presumir framework instalado.

## Camadas e prova esperada

| Camada | Conferência automatizada | Prova e limite |
|---|---|---|
| Código e contrato | Build, lint/tipos pertinentes, domínio e consumidores afetados | Comando/saída/commit; não comprova ambiente online |
| API e persistência | Regras, entradas inválidas, salvar/recarregar, concorrência e idempotência no banco real | Asserções e IDs sintéticos; mock não comprova SQL |
| Navegador | Abrir URL, autenticar usuário de teste, navegar, preencher, salvar e reabrir registro | Resultado por cenário, trace/capturas sanitizadas; abrir página sozinho não comprova fluxo |
| Segurança | Tenant A/B, ID direto, negativa de ação, sessão/troca de perfil e documento privado | Resultado esperado/observado de permissão; resposta 200 isolada não basta |
| Ambiente online | Identificar versão implantada, health/configuração, sessão, banco e storage do destino | URL, ambiente, versão e dados persistidos; pacote gerado não comprova deploy |
| Visual e negócio | Capturas em larguras previstas e comparação pertinente; percurso do usuário | Automação ajuda a localizar diferenças, mas não substitui leitura visual ou aceite real do piloto |

Os cenários são os [234 casos já planejados](MATRIZ_CENARIOS.md); esta organização não cria uma nova bateria obrigatória por cima de todos eles. Selecionar os casos afetados conforme R1/R2/N, registrar casos não aplicáveis com motivo e fechar a jornada integrada no pacote pertinente.

## Cobertura online do recorte

1. Site: páginas/links, navegação em celular/computador e canal/formulário no ambiente de QA. Quando houver serviço externo, usar destino de teste/sandbox; recebimento real só é comprovado com a evidência correspondente.
2. Segurança: onboarding, sessão, tenant A/B, consultas/gravações e acesso por ID, incluindo negativas e troca de perfil/cache.
3. CRM: cadastrar, impedir duplicidade pertinente, registrar interação/etapa/próxima ação e recuperar a mesma identidade após reload e nova sessão.
4. Documentos: upload válido/inválido, versão/revisão, download autorizado e negado, repetição/falha e conferência de bytes quando aplicável.
5. Tarefas/Flow: responsável/prazo/resultado, transição autorizada/negada, histórico coerente, concorrência e idempotência do protocolo no SQL real.
6. Operação: atualização/retorno e restore em recursos isolados destinados ao ensaio, com comparação de banco/arquivo e registro de versão. Não executar teste destrutivo em banco de produção.

## Configuração e execução

Definir endereço-base, ambiente, versão esperada, identificação da massa e usuários de QA. Segredos entram por configuração segura, nunca pelo commit/relatório. Antes de criar dados, confirmar que o destino é o QA autorizado. Cada execução usa identificador próprio para evitar colisão; limpeza só alcança registros sintéticos explicitamente criados para aquele teste.

O runner deve encerrar com falha quando a expectativa não for satisfeita e salvar relatório por caso, ambiente e versão. Separar falha do produto de indisponibilidade do ambiente e teste não executado. Retentativa limitada e justificada não pode esconder resultado intermitente; guardar falha inicial e resultado da correção.

Preferência acordada: rodar verificações locais durante a construção dos 17 pacotes; realizar a rodada online do recorte na homologação final. As condições externas ainda não conferidas ficam pendentes. Uma evidência exigida por gate não pode ser substituída por simulação; consumidores dependentes aguardam ou recebem recorte independente explícito.

CI de aplicação deve chamar os comandos pertinentes e produzir artefatos sanitizados. Execução contra homologação ocorre quando o ambiente/versão de destino estiver disponível e autorizado. A CI atual deste repositório permanece documental; não declarar estes testes rodados só porque ela passou.

## Conferência visual e aceite

O Codex pode examinar capturas ou percorrer o navegador quando essas ferramentas estiverem disponíveis e o acesso for permitido. Registrar o que foi efetivamente visto, larguras/rotas e limitações; não tratar screenshot gerado como screenshot inspecionado. A opinião do usuário sobre o fluxo, legibilidade e adequação ao negócio é registrada no aceite real do piloto.

Automação local/online, inspeção visual, homologação pelo usuário e liberação em produção permanecem evidências distintas. Revisão e verificação estão dentro das 180h; a reserva de 20h cobre contingência comprovada.

## Navegação

[Execução pelo Codex](../execucao/EXECUCAO_PELO_CODEX.md) | [Pacotes](../execucao/PACOTES_CODEX.md) | [Estratégia de evidências](ESTRATEGIA_DE_EVIDENCIAS.md) | [Validação e gates](../VALIDACAO_E_GATES.md)
