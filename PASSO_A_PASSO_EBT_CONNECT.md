# Executar e verificar o EBT Connect

**Estado vigente de 07/10/2026:** primeira entrega publicada e 26 verificações ao vivo aprovadas. [Acesso e provas](PASSO_A_PASSO_PUBLICACAO_CONNECT.md). Banco pago compartilhado preservado; valor variável autorizado posteriormente. Referências abaixo a host inexistente/F1/R$30 fixos descrevem o cenário anterior e foram superadas por esta publicação. Homologação real de mensagens, scanner, CI hospedada, restore Azure e aceite continuam pendentes.


Primeira entrega online: [EBT Connect](https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io). O administrador inicial está cadastrado; ver [guia de acesso](PASSO_A_PASSO_PUBLICACAO_CONNECT.md). O fluxo local abaixo permanece disponível com massa sintética.

Resultado desta etapa: aplicação local .NET/React/SQL com relacionamento, histórico, tarefas, documentos privados e resposta via API/webhook. A programação foi autorizada depois do planejamento. O destino de implantação continua sendo **o banco Azure já existente sqldb-crm-casst-dev-v2**, schema ebt_connect, sem criação de banco Azure ou alteração de plano. Publicação foi verificada separadamente; homologação real de mensagens e aceite não são comprovados pelos testes locais.

## Pré-requisitos

Windows/PowerShell, .NET SDK 10, Node 24/npm, Python 3.12, SQL Server local com autenticação integrada e sqlcmd. Ferramenta EF fixada em `.config/dotnet-tools.json`; versões/lockfiles no projeto. O SQL local contém exclusivamente fixtures EbtPlatformQa_*; não apontar scripts de QA para cliente/Azure. O ambiente usado teve SDK 10.0.401, SQL Server Developer 17.0.1135.8 e Node 24.19.0.

## Primeira execução local

Abrir terminal na pasta **C:\Users\Ivair Silva\Documents\ChatGPT\EBT PLATAFORM**:

```powershell
$env:MSBuildEnableWorkloadResolver='false'
$env:PYTHONUTF8='1'
dotnet tool restore
dotnet restore src/backend/Ebt.Platform.Api --locked-mode
dotnet build src/backend/Ebt.Platform.Api --no-restore
Push-Location src/frontend
npm ci
npm run build
npx playwright install chromium
Pop-Location
powershell -NoProfile -File scripts/Start-Local.ps1 -Initialize
powershell -NoProfile -File scripts/Start-Local.ps1
```

O comando Initialize aplica migrations somente em localhost/Development/banco QA e preserva dados já existentes. Não usa EnsureCreated no fluxo atual. Start inicia em **http://127.0.0.1:5186**. O arquivo privado `tmp/runtime/qa-access.json` contém acessos sintéticos gerados localmente; consultar no próprio computador. Não enviar senha no chat nem incluir esse arquivo em Git/pacote. `operador@ebt.example` atende sua carteira, `consulta@ebt.example` consulta, `admin@ebt.example` administra A/B. Essas contas não são clientes reais.

## Usar a interface

1. Entrar e conferir empresa/carteira no topo. Meu dia mostra tarefas e relacionamentos; trocar empresa limpa dados anteriores.
2. Relacionamentos: pesquisar, cadastrar contato, vincular organização/responsável e escolher uma das cinco etapas. O ID permanece no histórico/tarefas/documentos/conversa.
3. Registrar nota: conteúdo, autoria e datas de ocorrência/registro ficam separados. Criar tarefa com prazo/responsável. Concluir/cancelar exige resultado/motivo; próxima ação é recalculada das abertas.
4. Tarefas: filtrar situação, responsável e intervalo de prazo. Consultas ficam limitadas a 100; usar filtros para delimitar períodos.
5. Importar: baixar modelo CSV UTF-8, até 100 linhas, cabeçalho `chave;nome;email;telefone`. Preparar preview, conferir e confirmar. Erro de conflito não importa metade do lote.
6. Conversas: receber mensagem pelo webhook de QA/teste, selecionar conversa e confirmar resposta. A interface mostra fila/aceite/status observados. Canal QA é explicitamente local, sem envio ao cliente. Resultado incerto precisa de conferência; não reenviar automaticamente.
7. Documento: PDF/texto até 2 MiB, título e vínculo a contato/tarefa. Nova versão preserva a anterior; administrador aprova/rejeita com motivo. Consultar versões e baixar a autorizada. Leitor não baixa uma versão pendente. Produção exige varredura clean da versão; QA não comprova scanner real.
8. Administração: alterar perfis/vínculos, preparar convite de novo usuário, criar/revogar chave técnica e consultar auditoria. Convite preparado não foi enviado por e-mail. Ativação é individual; não redefine senha de conta existente. Chave aparece uma vez, com prazo de validade.

## Validar

Com a API local pronta, em outro terminal na raiz:

```powershell
$env:PYTHONUTF8='1'
python tests/integration/connect_qa.py
Push-Location src/frontend
npm run test:e2e
Pop-Location
$env:ASPNETCORE_ENVIRONMENT='Development'
$env:EBT_RUNTIME_CONFIG=Join-Path (Get-Location).Path 'tmp/runtime/local-config.json'
$env:Qa__SqlReport=Join-Path (Get-Location).Path 'evidencias/testes_connect_rls_sql.json'
dotnet src/backend/Ebt.Platform.Api/bin/Debug/net10.0/Ebt.Platform.Api.dll --verify-sql-qa
powershell -NoProfile -File scripts/Export-Migration.ps1
python scripts/test_migration.py
python scripts/verificar_plano.py
python scripts/verificar_organizacao.py --no-write
git diff --check
```

Para restore, terminar os testes e parar **somente** a API EBT deste checkout com Ctrl+C no terminal que a iniciou. Não parar SQL Server ou outros produtos. Executar `python scripts/test_recovery.py`: cria um destino local exclusivo, nunca sobrescreve banco existente; faz COPY_ONLY/CHECKSUM, compara fingerprints de tabelas/sentinel, reaplica migrations, copia keyring privado de QA, confere todos os hashes/envelopes e inicia o worker restaurado para provar que unknown não é reenviado. O teste exige dados documentais e envio incerto na fixture, por isso executar a suíte HTTP primeiro. Backups/bases locais de ensaio ficam preservados; não são bancos novos no Azure.

Relatórios observados nesta execução: suíte HTTP/SQL, SQL direto/RLS, navegador responsivo, migration limpa/repetida/bootstrap e restore. Os resultados exatos e os limites ficam em [registro de execução](evidencias/execucao_connect.json), [estado dos gates](docs/qualidade/STATUS_IMPLEMENTACAO_CONNECT.md) e [manifesto](evidencias/manifesto_connect_local.json). Não contar os 238 cenários planejados como executados. CI hospedada foi preparada, ainda não executada.

## Arquivos e integrações

`src/backend/Ebt.Platform.Api`: autenticação, SQL/RLS, contatos/tarefas/importação, documentos/scanner, API/worker/webhook, migrations, administração inicial e verificadores QA. `src/frontend`: aplicação, estilos, CSV e Playwright. `tests/integration`: integração HTTP com persistência real SQL local. `sql`: migration idempotente e permissões por schema. `scripts`: inicialização, exportação, inspeção Azure, ensaio de migration/restore e validação documental. `.github/workflows/validate.yml`: build preparado, sem deploy/segredos cloud.

Contrato efetivo em [CONNECT_V1.md](docs/api/CONNECT_V1.md); proposta OpenAPI de planejamento preservada separadamente. A arquitetura se baseou em padrões de CASST/Vikings/CRP/Nutrição/EBT, avaliados pelas versões/hashes atuais, e em referências oficiais Chatwoot/Stripe/Microsoft/Meta/RFC. Código e dados dos projetos-fonte não foram copiados.

## Problemas corrigidos e limites

Corrigidos: cancelamento de carregamento ao navegar, sessão antiga reutilizável depois de logout/troca, revisão documental sem histórico por versão, repetição de cadastro sem ledger, deduplicação de mensagem limitada à conversa, consulta ociosa frequente no banco e DDL condicional que falhava na migration repetida. Testes de recuperação foram reforçados para não aceitar zero documentos por filtro de tenant.

Azure: conexão deste computador bloqueada por firewall 40615; nenhuma migration/schema/rede/plano alterado. Use acesso autorizado existente e o [roteiro de implantação](docs/execucao/IMPLANTACAO_CONNECT_AZURE.md). Não liberar firewall ou publicar por inferência. A métrica de espaço não prova capacidade de carga. Meta real depende de conta/número/versionamento e callbacks homologados. Scanner real, HTTPS/proxy/domínio, observabilidade Azure e aceite são pendentes. Site e Flow continuam adiados; financeiro, SST completo, OS, chatbot, campanhas e omnichannel não pertencem ao recorte.

Se login/API falhar: conferir health e ambiente; não desabilitar CSRF/RLS. Em 409, atualizar versão/registro e preservar chave se a tentativa for repetição. Em 503, conferir serviço/scanner/storage/chaves e traceId. Em unknown, consultar operação/callback antes de qualquer nova transmissão. Falta de chave persistente exige recuperar o keyring compatível, não apagar envelopes ou inventar entrega.
