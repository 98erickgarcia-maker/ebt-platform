# Entrega EBT para a Emergent — 07/10/2026

## GitHub confirmado

- [Repositório EBT Platform](https://github.com/98erickgarcia-maker/ebt-platform).
- [Branch com o código pronto](https://github.com/98erickgarcia-maker/ebt-platform/tree/codex/prospeccao-emergent/entregas/emergent-prospeccao-v1).
- [Revisão nº 5](https://github.com/98erickgarcia-maker/ebt-platform/pull/5).
- [Roteiro completo de pedidos](https://github.com/98erickgarcia-maker/ebt-platform/blob/codex/prospeccao-emergent/entregas/emergent-prospeccao-v1/docs/PEDIDOS_EMERGENT.md).
- [Verificação automática no GitHub](https://github.com/98erickgarcia-maker/ebt-platform/actions/workflows/prospecting-extension.yml).

O pacote é uma extensão FastAPI/MongoDB/React para integrar ao aplicativo atual. O repositório contém também planejamento EBT Connect .NET; use somente a pasta desta entrega para a Emergent. O projeto atual e os dados existentes devem ser preservados.

## O que já está programado

Painel, contatos enriquecidos com origem/data, próxima ação, histórico, links, templates editáveis e versionados, prospecção por UF/cidade/CNAE na base importada, lotes agendados, pausa, deduplicação e limite mensal. Busca e templates não chamam IA.

E-mail é o canal principal. O Outlook reaproveita automaticamente as credenciais Microsoft e a caixa do disparador; tem fila persistente, prévia/aprovação, rascunho, agendamento e evidência de envio via Graph. Não exige captura de tela. Credenciais reais permanecem no servidor.

WhatsApp oferece duas opções: clique para abrir um template manual preenchido e envio de template aprovado pela API oficial. O histórico guarda a preparação manual; a API oficial registra seus próprios eventos de envio/entrega/leitura. Abrir a conversa não confirma envio. O envio real por API permanece condicionado à configuração e ao teste autorizado.

## Como começar na Emergent

Envie o ZIP ou forneça o link do branch e copie o **Pedido 1** de PEDIDOS_EMERGENT.md. Ele manda incorporar este código, reutilizar login/banco/disparador, adaptar somente os pontos necessários e executar os testes. Ao terminar, peça à Emergent os arquivos alterados, logs e a versão para revisão aqui.

## Próximas automações, em ordem

1. **Cadências por e-mail:** apresentação, retorno em 3 e 7 dias; parar por resposta, opt-out, alteração do contato ou cancelamento. É o Pedido 2, ainda a implementar.
2. **WhatsApp por regras:** menu de atendimento, classificação, fila e passagem para uma pessoa, usando o conector oficial existente. É o Pedido 3, ainda a implementar.
3. **Plataforma de atendimento COREN:** permissões, múltiplos atendentes, relatórios, retenção, backups e carga, confrontados com cada cláusula do edital. É o Pedido 4, um escopo adicional.

Peça uma etapa por vez. Exemplo aqui: “Prepare somente o Pedido 2 para a Emergent, usando a versão integrada do pacote, preservando os contratos e entregando testes e arquivos alterados”. Depois: “Revise o diff e os logs que a Emergent entregou para o Pedido 2”.

## Economia e validação

O desenho reduz a dependência de créditos/IA na operação repetitiva ao reutilizar templates, regras, base importada, banco e hospedagem. Não há porcentagem garantida de economia sem comparar a fatura atual; Meta, Microsoft 365, infraestrutura e manutenção continuam no cálculo.

Os resultados e suas versões ficam em evidence/VALIDACAO.json e no workflow. Testes sintéticos aprovados não ativam Microsoft/Meta nem comprovam funcionamento dentro da Emergent. A integração real e o teste controlado são a etapa seguinte. A baseline original de 180h de entregas e 20h de reserva foi preservada.
