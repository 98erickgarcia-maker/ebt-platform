# Decisão de implementação — 07/10/2026

O usuário autorizou começar a programação, substituindo a restrição anterior de planejamento apenas. Mantidos 180h de entregas e 20h de reserva estimadas; horas não são certificação de trabalho consumido nem prazo prometido.

## Avaliação das fontes

Baseline atual em [inventário de execução](../../evidencias/baseline_execucao_20261007.json): hashes dos arquivos técnicos e estado Git das nove bases administrativas conhecidas, sem exportar conteúdo de clientes, configurações privadas ou credenciais. CASST: HEAD 046e7c6 e 377 alterações; Vikings: HEAD 35b53ef e árvore limpa, diferente da revisão histórica. Não rodadas novamente suítes dessas fontes. Jogos, currículo e arquivos pessoais não são módulos administrativos e não foram analisados por conteúdo.

CASST orienta ID de contato, interações e proteção HTTP, mas seu webhook usa contexto fixo e o onboarding anterior tem falhas; não é extraído inteiro. Vikings orienta autorização de documento e importação em lote, sem incorporar regras SST ou código de PRs. Nutrição orienta versões, quotas e recuperação, sem trazer persistência SQLite de escritor único nem regras clínicas. CRP orienta convite individual e comunicação comercial. EBT institucional orienta identidade legível e entrega de assets. Power Apps/Portal Free orientam vocabulário; disparadores orientam a distinção entre tentativa, aceite e entrega. Nenhum disparador pessoal será ativado.

Implementação original em .NET 10, React/TypeScript e SQL Server. Não foram copiados arquivos de implementação; direitos de redistribuição das fontes não são presumidos. Todas as novas fronteiras de schema, contrato, tenant, sessão e storage seguem trilha N.

## Banco conforme instrução do usuário

Usar **o banco Azure existente `sqldb-crm-casst-dev-v2`**, servidor `sql-crm-casst-dev-crmenterprise98`, sem criar outro banco, aumentar SKU ou trocar tabelas dos projetos. Schema exclusivo `ebt_connect`, incluindo histórico de migrations próprio. O banco Basic atual tem máximo 2 GiB e o ponto da métrica `storage_percent` consultado em 07/10 registra 3%; isso não é teste de carga ou garantia de capacidade futura. O banco anterior `sqldb-crm-casst-dev` está pausado e não é o destino.

QA local usa base descartável exclusiva `EbtPlatformQa_20261007Migrated` para ensaiar antes de qualquer alteração compartilhada. `--init-qa` aplica migrations em Development, localhost e nome QA; não usa EnsureCreated no fluxo atual. A base inicial de ensaio anterior permaneceu preservada. Nunca aplicar `EnsureCreated`, `EnsureDeleted`, reset ou migrações de outras aplicações no Azure compartilhado. A conexão Azure deve usar identidade própria com acesso apenas ao schema EBT; identidade de administrador só na aplicação controlada da migration.

## Contratos fechados

Sessão humana por cookie HttpOnly, SameSite Strict, prazo de 8h, CSRF nas mutations e revalidação de usuário/vínculo/empresa por requisição. API técnica por chave aleatória, hash no banco, expiração e revogação; restrita às rotas Connect e às permissões atuais do titular. Suporte técnico não recebe dados por padrão. Empresa vem da sessão/vínculo ou conexão externa; não de campos de cadastro.

Próxima ação é a primeira tarefa aberta por prazo/ID. Contato não guarda cópia editável desse prazo. Cinco etapas fixas. Conflito otimista por versão e If-Match. Chaves de repetição guardam hash do comando; locks transacionais SQL e índices únicos protegem concorrência. Preview de importação guarda lote próprio; confirmação revalida contexto, lote e dados atuais e grava tudo atomicamente.

Documentos comerciais limitados a PDF/texto, 2 MiB por versão, privados, com revisão e vínculo a contato/tarefa. Conteúdo BLOB limitado no schema SQL torna versão, hash e conteúdo atômicos e permite recuperação no mesmo backup; esta escolha exige quota e monitoramento em banco compartilhado. Upload não prova varredura antimalware; liberação real requer política aprovada e scanner quando exigido.

Canal local sintético permite implementar/testar protocolos sem enviar mensagens reais. Adapter Meta será configurável, desabilitado inicialmente e só recebe homologação após prova da conta de QA. G-MSG permanece pendente para o canal real, mesmo com todos os testes locais aprovados.
