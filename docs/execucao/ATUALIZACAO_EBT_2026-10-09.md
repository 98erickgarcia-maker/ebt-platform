# Atualização EBT — 09/10/2026

Verificação iniciada em 09/10/2026 às 09:09 UTC. Escopo: site institucional, EBT Platform/Connect e central de e-mail EBT. Este registro acompanha a atualização atual; não substitui os estados e critérios dos 77 tickets do plano de 200 horas.

## Estado observado hoje

As consultas `git ls-remote --symref origin HEAD` concluíram com sucesso nos três repositórios. As cópias locais correspondiam ao `main` remoto no momento da consulta:

| Projeto | Commit confirmado | Situação |
| --- | --- | --- |
| Site institucional | `9c5e12c84f7dd7dff8aeb99314ce9ff505d5d4f7` | Revisão editorial e sincronização da página 404 de 06/10 presentes. |
| EBT Platform/Connect | `fdc3a9fa76c713c41323739ba816491293a6381a` | Baseline documental de 07/10 disponível; runtime do novo produto ainda não existe. |
| Central de e-mail | `00939998ed18313941af8646795e5684ba7e93a5` | Código de 07/10 disponível; encontrados problemas concretos de autenticação e identificação de simulações. |

[Versões verificadas](../../evidencias/execucao/atualizacao-2026-10-09/versoes-verificadas.json). O estado remoto do CI não foi consultado. As alterações estão sendo registradas na branch de revisão `codex/ebt-atualizacao-2026-10-09` de cada repositório. Branch de revisão não equivale a integração no main ou implantação.

## Metas de hoje e critério de conclusão

| Ordem | Meta | Critério | Estado |
| --- | --- | --- | --- |
| 1 | Confirmar as versões e as pendências reais | Comparação com GitHub, validações executadas hoje e distinção entre provas históricas e atuais. | Concluída. |
| 2 | Preparar o site atual | Geração, links, assets, página 404, pacote com hashes e QA de celular/computador. | Concluída localmente; publicação pendente. |
| 3 | Corrigir os bloqueios da central de e-mail | Login de desenvolvimento fechado por padrão; política de proprietário; sessões verificáveis; envio real sem Graph falha; simulação identificada sem contar como envio real. | Concluída neste recorte; integração real pendente. |
| 4 | Corrigir a continuidade do Platform | Baseline de 07/10 consultável, próximo PAC-02 indicado, verificadores aprovados e orçamento/estados preservados. | Concluída. |
| 5 | Conferir a produção pública | Raiz e www com conteúdo igual ao pacote, status/cabeçalhos esperados e separação das rotas do CRM. | Bloqueada pela política de rede deste ambiente. |
| 6 | Publicar a atualização que estiver diferente | Destino atual identificado, versão anterior preservada, acesso autorizado, atualização no recurso existente e validação pública posterior aprovada. | Depende das metas 5 e do acesso Azure. |

As metas 5 e 6 continuam pendentes; o pacote local não comprova publicação. Não há base para prometer a conclusão dessas etapas hoje enquanto os acessos estiverem indisponíveis.

## Site institucional

Em 09/10, o site foi gerado e verificado a partir de uma cópia dos arquivos rastreados. A verificação aprovou as 15 páginas públicas, os 18 documentos HTML, os 52 arquivos estáticos, a sintaxe JavaScript, a igualdade das duas cópias 404 e o hash da foto original.

O pacote estático `ebt-static-site-2026-10-09.zip`, disponível em `/workspace/ebt-enterprise-site/qa/atualizacao-2026-10-09/`, possui raiz `ebt-public/`, 4.260.196 bytes e SHA-256 `b3ab3ad091e3a46108df04c9cc22748dae79051388df85037fa6946d8d6b2bbb`. Os resultados estão no [relatório do site](../../evidencias/execucao/atualizacao-2026-10-09/site-local-verificado.json).

O smoke HTTP local aprovou 104 verificações GET/HEAD. O navegador Chromium conferiu as 15 páginas em 390 e 1440 pixels, incluindo menu, seletores, modal e contato, sem erro JavaScript ou transbordamento. Nove regressões do verificador foram aprovadas. Há uma observação visual de glifos de seta como quadrados neste Chromium/Linux; validar a renderização no navegador de produção antes de fechar o aceite visual. [Navegador](../../evidencias/execucao/atualizacao-2026-10-09/site-navegador.json) e [HTTP local](../../evidencias/execucao/atualizacao-2026-10-09/site-http-local.json).

O comando reutilizável, da raiz do repositório do site, é:

```sh
python scripts/verificar_publicacao.py --package qa/atualizacao-2026-10-09/ebt-static-site-2026-10-09.zip --output qa/atualizacao-2026-10-09/publicacao-production.json
```

Ele retorna 0 se aprovado, 1 se houver divergência e 2 se a rede estiver bloqueada. Exige conteúdo, status, identificação da camada estática, nosniff, diretivas CSP e bloqueio das rotas CRM no host público. A execução de hoje marcou 232 verificações bloqueadas, após uma tentativa por domínio. [Resultado público](../../evidencias/execucao/atualizacao-2026-10-09/site-publicacao.json).

O guia de 03/10 descreve uma aplicação SQL separada; a revisão de 06/10 e `shared-host/Ebt.StaticHost` descrevem uma camada estática na hospedagem compartilhada. Antes de alterar uma aplicação Azure, consultar o recurso que atende atualmente aos domínios e confirmar imagem, revisão, diretório e configuração. O script `Publish-SharedAzure.ps1` é de primeira implantação/retomada e exige diários ausentes nesta cópia; não é o procedimento de atualização editorial desta camada.

As consultas HTTPS de hoje a `ebtenterprise.com.br`, `www.ebtenterprise.com.br` e ao endereço Azure histórico falharam no túnel do proxy com `403 Forbidden`. A política é restrita e não inclui esses destinos. Isso demonstra um bloqueio deste ambiente e não permite concluir que o site esteja fora do ar. [Evidência do acesso](../../evidencias/execucao/atualizacao-2026-10-09/acesso-publicacao.json).

## Central de e-mail

A auditoria confirmou que o projeto pertence à EBT. O PDF institucional já existe; o item que ainda o chama de placeholder é uma pendência documental antiga.

Correções desta atualização: impedir acesso público de proprietário pelo login temporário; exigir a identidade de proprietário na configuração Microsoft; recusar sessões sem origem verificável; distinguir resultado simulado de envio real; falhar em envio real quando faltam credenciais Graph; corrigir o assunto comercial de fallback para o posicionamento tecnológico da EBT.

As 22 regressões isoladas passaram, assim como a compilação Python. A compilação do frontend passou em uma cópia temporária com os dois plugins de prévia desativados; os 70 arquivos de código foram comparados e permanecem idênticos. A instalação original encontrou conflito de dependências React e bloqueio de `assets.emergent.sh`, e não existe lockfile versionado. Essa compilação isolada não comprova a instalação completa ou integração da hospedagem. Sessões antigas sem marcador de provedor precisarão de novo login após instalar a correção. [Evidência do e-mail](../../evidencias/execucao/atualizacao-2026-10-09/mail-verificado.json).

As verificações desta correção devem usar dados sintéticos e dependências substituídas, sem contas ou bancos operacionais. A suíte histórica apaga registros e não deve ser executada contra uma base existente. Integração real Microsoft/MongoDB e disponibilidade da hospedagem precisam de provas separadas; o relatório histórico de 17 testes não demonstra esses comportamentos hoje.

## Platform/Connect e capacidade restante

Os [dois](../../evidencias/execucao/atualizacao-2026-10-09/plano-verificado.json) [verificadores documentais](../../evidencias/execucao/atualizacao-2026-10-09/organizacao-verificado.json) passaram hoje. A continuidade foi corrigida nas fontes geradoras e nos documentos, com manifesto reconciliado. `verificar_plano.py` agora aceita `--no-write`. Os 77 estados, as horas reais, as estimativas, o PDF e as evidências históricas foram preservados.

A baseline G0 de 07/10 libera a fundação sob a condição de CI documental aprovado no commit mesclado. P01-01 e P01-04 ainda têm critérios antigos a reconciliar com a fonte remota escolhida. Não marcar módulos como entregues por causa dessa baseline.

| Próximo recorte de desenvolvimento | Estimativa existente | Dependência |
| --- | ---: | --- |
| PAC-02A/B/C: estrutura, Design System, configuração e dados sintéticos | 8h no PAC-02 inteiro | Condição documental do G0 e fundação isolada. |
| PAC-03: SQL/storage QA, diagnóstico, cliente HTTP e CI | 8h | Fundação e serviços QA. |
| PAC-04: pacote de site essencial da Platform | 12h | Critérios próprios do pacote; site institucional anterior não fecha automaticamente esse gate. |
| PAC-05 a PAC-07: identidade, tenant, autorização e onboarding | 36h | SQL e testes de isolamento. |
| PAC-08 a PAC-10: jornada CRM Connect | 28h | Segurança aprovada e persistência real. |

Essas estimativas são horas-pessoa do planejamento, não horas realizadas neste atendimento. O orçamento permanece 180h de entregas e 20h de reserva. Desenvolver todos os módulos requer as etapas e provas previstas; não há evidência para converter o plano inteiro em uma entrega de hoje.

## Continuidade sem pedidos repetidos

1. Seguir as metas em ordem de dependência, corrigir falhas encontradas e repetir somente as verificações afetadas.
2. Quando uma integração estiver indisponível, registrar o erro e continuar o trabalho independente.
3. Com rede liberada, executar a comparação pública antes de decidir se é necessária outra publicação.
4. Com acesso Azure, consultar o destino atual e a recuperação; preparar a atualização no recurso existente e validar o resultado real.
5. Manter as correções locais e os artefatos disponíveis; atualizar este registro apenas com resultados executados.

Não há tarefa agendada que mantenha estes agentes executando depois de encerrado o atendimento. O workflow atual do Platform valida documentos em push/PR/manual; não publica aplicações. Os agentes internos executam as etapas deste atendimento e usam os recursos disponíveis da sessão.

## Acesso que falta

Este ambiente não tem identidade Azure configurada. A alteração da lista de rede foi proposta pelo fluxo suportado, mas o serviço respondeu `draft_not_editable` e não confirmou o salvamento. A leitura posterior mostrou o mesmo rascunho, revisão 1.

Os domínios e as instruções propostos estão preservados no [arquivo de configuração para transferência](../../evidencias/execucao/atualizacao-2026-10-09/environment-config-proposto.json). É necessário editar a configuração nas opções do ambiente para liberar os destinos e disponibilizar uma identidade Azure autorizada. Valores de credenciais devem entrar pelas configurações seguras, nunca neste documento ou no chat.

Salvar a configuração, preparar o pacote e publicar a aplicação são operações distintas. Revalidar os acessos depois que a configuração for aplicada.

## Entrega registrada

Branches de revisão dos três projetos: `codex/ebt-atualizacao-2026-10-09`. Código e evidências de continuidade foram preservados no GitHub; a implantação permanece pendente pelos acessos descritos acima. Não foi criado PR automaticamente. O pacote estático e as capturas são artefatos locais disponibilizados separadamente.
