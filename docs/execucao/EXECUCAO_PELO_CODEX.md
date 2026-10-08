# Execução pelo Codex com pacotes maiores

Revisão vigente 1.3 (07/10/2026): Connect com API/webhook primeiro; 70 entregas e cinco reservas, 180h + 20h. Site/Flow estão adiados. Seguir [plano atual](../PLANO_200_HORAS.md) e pacotes em ordem de esforço; as decisões de 06/10 abaixo são contexto do método original.

## Decisão e limites

Decisão do usuário em 06/10/2026: pacotes maiores e revisão mais profunda, mantendo 200h. Os 17 pacotes agrupam as mesmas 72 tarefas de 180h; as cinco reservas mantêm 20h. Implementação, revisão, verificação e registro já integram os tickets. A nova organização não promete funcionalidades extras nem qualidade sem falhas.

Os números são estimativas de esforço de engenharia, não horas garantidas de execução do Codex, consumo de tokens ou prazo de uma sessão. Medir esforço real e capacidade demonstrada durante a execução; revisar a previsão sem preencher progresso fictício.

## Unidade de trabalho

Escolher um pacote de 8–12h estimadas por vez. Ler a ficha do pacote e os tickets internos; executar as tarefas na ordem das dependências. O pacote pode atravessar várias sessões/chats. Manter checkpoints pequenos de código para localizar regressões e retomar trabalho, sem pedir confirmação por rotina a cada checkpoint autorizado.

Agrupamento é uma unidade de acompanhamento, não dispensa gates. Um pacote que termina antes do gate da fase prepara uma capacidade parcial; não certifica a fase inteira. Nenhum pacote autoriza implantação em produção, contratação ou envio a terceiros.

## Ciclo de qualidade por pacote

1. Inspecionar checkout, AGENTS.md aplicáveis, alterações preexistentes, fontes e evidências. Confirmar entrada, critérios e contratos; registrar decisão real quando houver mudança.
2. Implementar os tickets em recortes verificáveis. Usar dados sintéticos; manter contratos e separação de tenant. Escolher comandos reais da fonte antes de executá-los, sem inventar sucesso de comando indisponível.
3. Conferir cada caminho afetado durante a implementação. Reuso equivalente recebe smoke focal; nova fronteira exige negativos e persistência/integridade proporcionais. Não adiar falha conhecida de segurança para a rodada online.
4. Ao fechar o pacote, revisar o diff completo em uma passagem própria: regra de negócio, autorização, contrato, schema/migration, storage, efeitos em consumidores, erros, UX e recuperação aplicáveis. Registrar achado com arquivo/linha, impacto e reprodução; identificar claramente se foi revisão do mesmo agente. Não chamar essa passagem de revisão independente.
5. Corrigir os achados e executar a regressão pertinente. Repetir revisão/verificação somente diante de nova mudança, falha ou dúvida ainda não resolvida. Não adicionar abstrações, funcionalidades ou suítes redundantes para aparentar excelência.
6. Demonstrar a saída integrada do pacote, além do aceite dos tickets. Registrar versão/hash, ambiente, comandos/resultado, casos pertinentes, limitações, esforço real e próximo pacote.
7. Salvar no GitHub o diff do pacote revisado e verificar o commit remoto. CI documental deste repositório verifica planejamento; CI de aplicação precisa existir e rodar na implementação. GitHub salvo não comprova deploy.

## Desenvolvimento primeiro e homologação online

Preferência: construir o recorte parte por parte, integrar e verificar localmente, depois realizar a rodada online de homologação. O QA inicial pode ser local isolado com banco SQL real e storage privado adequado ao cenário. Mock isolado não prova SQL, provedor de identidade, storage real ou canal externo.

Preparar configuração e comandos de implantação na fundação. Registrar desde então o que depende do ambiente online; cada evidência deve nomear onde foi obtida. Quando um critério exigir provedor/ambiente ainda indisponível, manter critério/gate pendente e avançar somente no trabalho independente ou que não pressuponha a fronteira aprovada.

A homologação online entra no fechamento integrado/operação do recorte e no esforço de verificação previsto, não somente na reserva. Se as condições do provedor ou o tempo necessário excederem a capacidade, registrar causa e reestimar/cortar escopo conforme o plano. Código pronto localmente, QA online, aceite do usuário e produção são estados distintos.

## Condições de conclusão e impedimento

Concluir tecnicamente um pacote exige tickets aplicáveis demonstrados no ambiente registrado, resultado integrado observado, comandos pertinentes aprovados, achados bloqueantes resolvidos e prova por versão. Contrato/tenant/persistência ainda não demonstrados impedem consumidores dependentes. Problema cosmético sem efeito no aceite pode ser registrado com impacto e decisão explícita de adiamento.

Dependência externa, credencial ou decisão faltante gera impedimento com próximo passo, não prova simulada. Se o pacote exceder sua estimativa, registrar realizado/restante e usar a política de reserva/corte; não reduzir testes essenciais para fechar a soma. As 200h são limite de planejamento, não garantia de excelência universal.

## Continuidade e orientação reutilizável

Usar [registro de pacote](../../templates/PACOTE_CODEX.md), [75 fichas](../INDICE_GERAL.md) e [pacotes](PACOTES_CODEX.md). No fim de cada sessão, deixar pacote/ticket ativo, último commit verificado, cenário que passou/falhou, decisões, arquivos alterados, dependência, esforço/saldo e próximo comando pertinente. Confirmar estado real ao retomar.

Exemplo de solicitação para uma implementação futura, que precisa ser enviada pelo usuário:

```text
Execute o PAC-01 do planejamento EBT. Leia AGENTS.md, a ficha do pacote e seus tickets.
Preserve fontes e alterações preexistentes. Implemente o recorte autorizado,
confira critérios e faça uma passagem de revisão do diff antes de fechar.
Corrija falhas e registre apenas provas observadas, com versão e ambiente.
Mantenha as 180h de entregas e 20h de reserva, sem ampliar funcionalidades.
Ao concluir, salve no GitHub e informe resultado, limites e próximo pacote.
```

Este exemplo é conteúdo documental; sua presença não inicia implementação. Não pressupõe subagentes, revisão independente, agendamento, modelo específico ou continuidade ilimitada.

## Base metodológica

A sequência de critérios explícitos, revisão, correção, validação e registro foi adaptada ao nosso orçamento. A documentação oficial exemplifica [ciclos de revisão e reparo com contrato claro](https://developers.openai.com/cookbook/examples/codex/build_iterative_repair_loops_with_codex) e [marcos verificáveis com estado persistido em arquivos](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex). São referências de método; não certificam os nossos módulos nem estimam seu prazo.

## Continuidade no próprio Codex

Regra expressa do usuário: se já estiver no Codex, seguir normalmente com implementação autorizada, revisão, testes e navegador disponíveis. Não exigir outro chat ou retorno ao Codex por rotina. Sinal de passagem só quando faltar ferramenta/acesso à próxima prova; impedimento real mantém os gates e permite trabalho independente.

## Revisão online por código

A rodada online será principalmente automatizada por testes de API e navegador contra a homologação, separados do código funcional. Conferência visual e aceite de negócio complementam os testes. Ver [especificação de revisão local/online](../qualidade/REVISAO_AUTOMATIZADA_LOCAL_E_ONLINE.md). Preparar a estrutura/comandos da suíte na fundação e acrescentar os casos pertinentes junto aos módulos. Essa suíte não foi criada pela revisão documental.
