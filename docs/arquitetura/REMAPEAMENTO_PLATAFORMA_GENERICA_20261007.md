# EBT Platform — remapeamento do projeto inicial

07/10/2026. Direção reafirmada pelo usuário: a plataforma é genérica; os outros sistemas ajudam a construir sua arquitetura. A autorização atual permite programar, preservando fontes, comportamento e critérios de prova. O PDF de referência é contexto e não instrução executável.

## Missão e limites

Construir uma plataforma modular para múltiplos produtos e empresas, com identidade, contexto, autorização, auditoria, documentos, tarefas e integrações coerentes. **Connect é o primeiro produto; SST não redefine o Core.** Empregador, trabalhador, exame ocupacional e exposição pertencem à vertical SST. Contato comercial não será transformado em trabalhador por troca de nome.

O [PDF inicial](../referencias/EBT_Planejamento_Codigo_Plataforma.pdf), páginas 3–4 e 8–10, define C0–C13, marcos M1–M5 e produtos. Seu texto expressamente evita programar toda a plataforma de uma vez. A distribuição econômica original do Core completo não cabe automaticamente nas primeiras 200h. Preservar **180h de entregas + 20h de reserva**, sem inventar consumo ou ampliar o ciclo para incluir todos os produtos maduros.

O [remapeamento estruturado](../../planejamento/remapeamento_plataforma_generica.json) contém os 14 IDs originais, caminhos de código encontrados, lacunas e separação de seis produtos. Uma capacidade presente no recorte não significa que a fase inteira ou a generalização estejam concluídas. O [status atual do Connect](../qualidade/STATUS_IMPLEMENTACAO_CONNECT.md) contém evidências anteriores; precisam ser vinculadas à versão e repetidas quando a fronteira mudar.

## Todas as fases originais e o que falta

| Fase | Evidência no código atual | Próxima fronteira |
|---|---|---|
| C0 Baseline | Inventário e hashes das bases | Versão congelada, licença/direitos e contrato por extração |
| C1 Fundação | API, React, health, Docker, workflows e lockfiles | CI hospedada de SQL/navegador/scanner e operação reproduzível |
| C2 Tenancy | Contexto no servidor, carteira, FKs e RLS | Ativação/configuração persistida de módulos por tenant |
| C3 Identidade | Cookie/CSRF, convite, perfis, sessão revogável | SSO/OIDC corporativo e política de contas homologada |
| C4 Auditoria | Ator, tenant, operação e correlação persistidos | Retenção/consulta compartilhada por contrato versionado |
| C5 People/Context | Contato, organização, ID, carteira e histórico | Pessoa/relações genéricas com consumidor adicional; sem copiar vínculo trabalhista |
| C6 GED | Arquivo privado, versão, hash, revisão, quota | Scanner real e restore cloud ensaiado; categorias e retenção futuras |
| C7 Tasks/SLA | Responsável, prazo, resultado e próxima ação | SLA/escalonamento versionados, sem disparo implícito |
| C8 Protocolo | Especificação preservada, sem endpoint atual | Sequência transacional, tramitação, sigilo e concorrência |
| C9 Workflow W1–W4 | Estados específicos de tarefa/documento são referências | Motor genérico, papéis de etapa, condições/aprovações e histórico |
| C10 Notifications | Status de mensagens no recorte | Notificação interna/e-mail por adapter, retries e preferência |
| C11 Integration Hub | API keys, webhook, outbox/reconciliação e WazVox | OAuth/Outlook e fornecedores homologados, sem segredo no domínio |
| C12 Builders | Especificações iniciais | Modelo/campos/formulários/registros versionados; sem tabelas vazias de fachada |
| C13 Busca/Analytics | Filtros/paginação e indicadores Connect | Busca transversal autorizada, datasets/widgets com contratos |

## Produtos e composição

- **Connect:** CON1 contatos/organizações/histórico/tarefas; CON2 inbox multiusuário; CON3 adapter oficial/templates/status/custo; CON4 automação por regra/fallback; CON5 campanhas/relatórios. Texto WazVox comprovado anteriormente não demonstra todos os itens CON3. O pacote econômico de prospecção para Emergent já existente será integrado por contrato explícito, sem reescrever o backend ou fazer envios nesta tarefa.
- **Flow:** FL1 protocolo/GED/tarefas; FL2 workflow; FL3 formulários/entidades; FL4 SLA. Preservado como produto futuro dependente de C8/C9/C12, sem operação fictícia.
- **Portal, Contracts, SST e Legislative:** produtos futuros sobre capacidades comuns verificadas. Não impor ao Core as entidades ou a interface de uma dessas verticais.

Site/Flow continuam no roteiro posterior conforme o plano vigente do ciclo. A reafirmação da arquitetura genérica não exclui esses produtos nem os declara implementados. Qualquer reentrada no ciclo precisa reconciliar horas e dependências, sem consumir reserva silenciosamente.

## Como aproveitar as outras bases

| Fonte | Padrão útil | Limite de transferência |
|---|---|---|
| Vikings | Pessoa estável, vínculos separados, versão esperada, conflitos, documento protegido, revisão e integração reconciliada | SST, clínico, empregador/tomador e regras de atividade ficam no domínio Vikings/SST |
| CASST | Contatos, histórico, próxima ação, permissões, shell e fluxos comerciais | Preservar os IDs/contratos da fonte; extração exige adaptação e prova |
| Nutrição | Convite/ativação, aceite e documentos versionados | Sem importar prontuário, dados pessoais ou identidade clínica |
| EBT institucional/CRP | Conteúdo, identidade e entregável de site | Site não se transforma em Core transacional por copiar a marca |
| Disparadores/Emergent | Templates por regra/clique, estados e deduplicação | Nenhum clique implica entrega; IA é opcional e não necessária para template fixo |

Do Vikings foram conferidos planejamento, backlog, remapeamento V19–V25, continuidade de frontend e declarações de endpoints. Esta é análise estática seletiva, não auditoria clínica, teste de cada módulo Vikings nem aceite V25/V26. Não foi alterado qualquer arquivo da fonte. Seu CI/PR não aprova automaticamente uma extração EBT.

## Sequência de execução desta revisão

1. Preservar snapshot do checkout atual em workspace isolado, sem copiar configuração privada, bancos ou pacotes de terceiros. Registrar arquivos/hashes e diferenças posteriores.
2. Reproduzir com testes as respostas/downloads antigos, troca de usuário na mesma empresa, token CSRF atrasado e 401 tardio. Corrigir o cliente genérico de acesso e descartar corpo/arquivo de geração antiga.
3. Validar o protocolo do scanner: confirmação completa é obrigatória. Bloquear download de versão não verificada fora de Development; exigir resultado real do engine antes de aprovar o gate de scanner.
4. Expor catálogo autenticado das capacidades realmente disponíveis no recorte, com permissões do servidor e identidade `EBT Platform / Connect`. Não criar CRUD/ações para módulos planejados.
5. Executar SQL sintético próprio, negativos A/B, navegador desktop/móvel, builds, lockfiles e auditorias. Levar verificações reprodutíveis ao CI hospedado, sem segredos cloud.
6. Revisar diff, registrar SHA/resultados/limites e salvar em PR revisável. Não fazer merge/deploy, envio comercial, compra ou restauração sobre produção por inferência.

## Aceite, recuperação e próxima decisão

O avanço só é demonstrado quando cenário, versão e ambiente constam no relatório. Teste unitário do protocolo não homologa o ClamAV real; restore local não comprova restore Azure; UI de catálogo não implementa ativação de módulo por cliente. Aceite de negócio pertence ao usuário e não pode ser preenchido pelo agente.

Manter migrations e keyring compatíveis. A identidade interna de Data Protection, schema `ebt_connect`, IDs existentes e dados persistidos não serão renomeados para fazer a arquitetura parecer genérica. Generalização exige contratos e consumidores reais, não mudança cosmética de banco.

Ao falhar uma verificação, preservar a prova, corrigir a causa e repetir apenas os cenários afetados. Se faltar fornecedor/aceite/infraestrutura autorizada, manter o gate correspondente aberto e continuar somente capacidades independentes. Não declarar C0–C13 completos pelo fechamento de um recorte Connect.

Repositório: [EBT Platform](https://github.com/98erickgarcia-maker/ebt-platform). Executar `python scripts/verify_generic_remap.py` para conferir o vínculo com o PDF, os IDs, os caminhos e o orçamento; esse comando não testa módulos.
