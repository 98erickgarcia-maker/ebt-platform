# Fluxo único: desenvolver, revisar e passar ao teste no Codex

## Modalidade escolhida

O usuário esclareceu em 06/10/2026 que pretende usar o próprio ChatGPT na conversa normal, sem Work, e retornar ao Codex para testes de navegador. Este documento complementa os 17 pacotes existentes, mantendo 180h de entregas e 20h de reserva. Não inicia implementação nem configura uma automação entre chats.

Para o acompanhamento do usuário, tratar tudo como um único projeto e uma sequência única de pacotes. Usar o mesmo roteiro de escopo, revisão, provas e continuidade onde estiver trabalhando. O critério de passagem é a próxima prova necessária e a ferramenta disponível para obtê-la; não exigir troca de modalidade por rotina.

O usuário confirmou que a sessão escolhida consegue editar e salvar no GitHub. O fluxo passa a usar esse acesso diretamente para alterações e commits, sem obrigar transferência manual de arquivos. Essa capacidade foi informada pelo usuário; não houve execução naquela sessão por esta revisão. Terminal/banco/navegador e outros acessos são avaliados conforme disponibilidade efetiva. A documentação oficial registra que [ambientes e ferramentas têm permissões diferentes](https://learn.chatgpt.com/docs/enterprise/work-admin-faq).

Não assumir execução ilimitada nem transferência automática de contexto. Limites, ferramentas e disponibilidade dependem da modalidade/plano; não há confirmação nesta revisão do plano ou capacidade da conversa normal. Instrução de parada orienta a resposta, mas não constitui bloqueio técnico de um executor autônomo. Não foi criado runner, monitor, mensagem automática ou proteção de branch por este complemento.

## Fluxo concreto

1. O ChatGPT consulta o repositório autorizado, confirma branch/commit e lê a ficha do pacote, tickets, instruções e arquivos pertinentes. Se algum arquivo privado não estiver acessível, registrar a falta; um link sozinho não comprova leitura.
2. Edita o recorte diretamente no GitHub pelo acesso disponível, preserva fontes e alterações preexistentes e revisa o diff completo. Registra contratos, motivos e cenários necessários; salva o commit e verifica o conteúdo remoto efetivo.
3. O usuário revisa a proposta de negócio/escopo quando necessário. Revisão de texto/código não certifica build, persistência, isolamento ou UI. A prova de cada teste deve identificar o commit ou artefato testado.
4. Executa as verificações disponíveis, inclusive CI de aplicação quando estiver configurada, e consulta resultados do commit correspondente. Corrige falhas antes de avançar no consumidor dependente. Se faltar terminal/banco/storage ou execução necessária que a sessão não consegue obter, entregar o sinal de execução; caso contrário continuar normalmente.
5. Quando a jornada estiver executável e a próxima prova exigir navegação/inspeção que a sessão não consegue realizar, entregar o sinal de navegador com commit, URL, cenários e pendências. O usuário abre o Codex no mesmo repositório. Se já estiver no Codex, ele segue normalmente com as ferramentas disponíveis, sem exigir passagem adicional.
6. O Codex confirma checkout/diff e versão do destino, testa com massa própria e registra resultado. O destino pode ser local; homologação online depende de ambiente implantado/disponível. Corrige os achados na versão correspondente, repete apenas o necessário, salva as correções no GitHub e atualiza o registro. Aceite do usuário e produção continuam separados da aprovação técnica; salvar código no GitHub não publica aplicação na internet.

Este fluxo permite concentrar escrita/revisão e commits na conversa escolhida. A passagem ocorre somente quando falta a próxima ferramenta/prova necessária. Não repetir por rotina verificações que já têm evidência equivalente por versão/cenário. A CI atual deste repositório é documental; build e testes dos módulos exigem a CI de aplicação prevista na fundação.

## Regra expressa: se já estiver no Codex, seguir normalmente

Observação do usuário em 06/10/2026: seguir normalmente se já estiver no Codex. Quando este roteiro estiver sendo aplicado em uma execução autorizada no Codex, continuar aplicação, revisão, comandos pertinentes e testes de navegador com as ferramentas disponíveis. Não encerrar a etapa só para pedir que o usuário volte ao Codex, não exigir novo chat nem produzir sinal de passagem desnecessário.

Os sinais de passagem abaixo só se aplicam quando a sessão atual não consegue obter a próxima prova por falta real de ferramenta/acesso. Estar no Codex não remove indisponibilidade de ambiente, decisão ou login; nesse caso registrar o impedimento e continuar o trabalho independente possível. Os limites e critérios dos pacotes permanecem.

## Sinais de passagem e critérios objetivos

| Sinal no relatório de passagem | Quando usar | Próxima ação |
|---|---|---|
| PROPOSTA_PARA_REVISAO | Patch delimitado, versão-base e critérios identificados | Usuário confere escopo; não chamar produto de concluído |
| AGUARDANDO_CODEX_EXECUCAO | Próxima conclusão exige aplicar/compilar/testar e a sessão não consegue obter essa prova | Encerrar a etapa dependente com patch, comandos pertinentes e pendências; levar ao Codex |
| AGUARDANDO_CODEX_NAVEGADOR | Jornada executável na versão identificada; faltam prova via navegador ou leitura visual e a sessão não tem ferramenta/acesso para obtê-las | Entregar URL local/QA, passos, usuários sintéticos por referência segura e resultados esperados; levar ao Codex |
| BLOQUEADO_AMBIENTE_OU_DECISAO | Destino, permissão, dependência ou decisão realmente ausente | Informar causa e próximo passo; não simular navegação nem aprovação |
| RETORNAR_PARA_CORRECAO | Teste observado falhou ou revisão mostrou defeito bloqueante | Registrar reprodução, ambiente/versão e correção necessária |

Esses sinais pertencem ao relatório de passagem e não substituem os estados oficiais dos 77 tickets. A hora de parar é definida pela próxima evidência necessária, não por tempo de relógio ou quantidade de código. Se houver apenas previsão de teste, informar que ainda falta executar; não declarar o sinal de navegador como prova de prontidão sem verificar as entradas.

Ao surgir a dependência, encerrar a resposta com o sinal e pacote de passagem. Não continuar o consumidor que pressupõe a evidência faltante. Trabalho independente pode continuar apenas no recorte autorizado e deve manter a pendência visível. Se o usuário quiser parada técnica obrigatória de um agente futuro, será necessário integrar o executor a controles de execução e acesso; não é uma capacidade configurada aqui.

## Conteúdo mínimo para retomar

Usar [template de passagem](../../templates/PASSAGEM_CHATGPT_CODEX.md): pacote/tickets, versão-base, arquivos/diff, revisão/decisões, provas realmente obtidas, comandos pendentes, sinal, primeiro passo, cenário esperado, ambiente/URL, dependências e esforço/saldo. Não enviar senha, token ou dados reais no relatório. Identificar usuário sintético por referência segura ao ambiente.

Depois de aplicar, o Codex registra o commit testado e verifica que a versão do navegador corresponde a ele ou a um artefato rastreável. Se o código mudar após o teste, avaliar os cenários afetados antes de reutilizar a aprovação.

## Instrução pronta para a conversa normal

```text
Trabalhe no pacote [ID] do planejamento EBT usando o acesso autorizado ao GitHub.
Confirme repositório, branch e commit; leia AGENTS.md, ficha e critérios aplicáveis.
Edite o recorte, revise contratos e efeitos nos consumidores e mantenha
os cenários afetados. Preserve o recorte e as 180h de entregas + 20h de reserva.
Salve as alterações revisadas no GitHub e confira o commit remoto. Execute os testes
disponíveis e consulte a CI de aplicação do mesmo commit; corrija falhas pertinentes.
Não chame código escrito de código testado. Se a próxima evidência exigir execução
indisponível, pare a etapa dependente e sinalize AGUARDANDO_CODEX_EXECUCAO.
Se a jornada já estiver executável e faltar conferência de navegador,
sinalize AGUARDANDO_CODEX_NAVEGADOR somente se não puder realizá-la nesta sessão.
Se já estiver no Codex, siga normalmente com revisão, testes e navegador disponíveis,
sem exigir outra passagem ou novo chat. Quando houver impedimento real, entregue o relatório,
com primeiro passo, arquivos, versão, cenário, expectativa e pendências.
Não invente resultado, aceite, publicação ou commit remoto.
```

## Solicitação pronta para retomar no Codex

```text
Retome o pacote [ID] a partir deste relatório e destes arquivos/diff.
Leia AGENTS.md e confirme versão-base, checkout e alterações preexistentes.
Aplique somente o recorte autorizado, compile e rode as verificações pertinentes.
Quando houver jornada executável e destino autorizado, confira pelo navegador os
cenários pendentes com dados sintéticos; corrija falhas e registre as provas.
Salve no GitHub o resultado revisado e informe commit, estado demonstrado e limites.
Não publique em produção nem atualize status sem a prova correspondente.
```

Os exemplos são conteúdo para o usuário copiar/adaptar; não acionam outra conversa, não enviam mensagens e não iniciam execução neste pedido.

## Navegação

[Pacotes maiores](PACOTES_CODEX.md) | [Execução pelo Codex](EXECUCAO_PELO_CODEX.md) | [Revisão local/online](../qualidade/REVISAO_AUTOMATIZADA_LOCAL_E_ONLINE.md)
