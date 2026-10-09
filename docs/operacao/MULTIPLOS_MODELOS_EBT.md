# Modelos por papel no runner EBT

Alteracao autorizada em09/10/2026. Manifesto model_routing seleciona OpenAI pela conta Codex existente; nenhuma API paga, compra ou provedor externo foi ativado.

|Modelo|Papeis|
|---|---|
|gpt-5.6-sol|Escopo, contratos, backend e seguranca|
|gpt-5.6-terra|Frontend, negativas, regressao e revisao independente|
|gpt-5.6-luna|Acessibilidade e handoff|

Atribuicao e escolha operacional inicial, nao benchmark de qualidade. Slugs apareceram no catalogo da conta VPS; catalogo nao comprova execucao. Cada tarefa envia --model e model_reasoning_effort explicitamente, registra selected_model no checkpoint e evidencia. Backend/seguranca/revisao recebem high; demais medium. Revisao usa outro modelo em relacao ao backend, sem garantir independencia dos dados/arquitetura.

49 testes locais do supervisor passaram incluindo routing, rejeicao de modelo nao aprovado/injecao, provedor/API paga e uma unica chamada seguida de cooldown na falta de cota. Chamadas reais a cada modelo permanecem pendentes da cota. O runner nao troca modelo para contornar bloqueio e nao amplia12chamadas/dia ou concorrencia1. Para provar o modelo realmente utilizado, exigir evento/metadado do provedor; selected_model prova configuracao enviada somente.

O n8n/EasyPanel/Traefik nao foi instalado nesta alteracao; coordena-se o runner existente. Modelos locais e provedores externos requerem incremento proprio, acesso e teste de recursos. Erro de modelo indisponivel deve ser revisado, sem fallback silencioso.
