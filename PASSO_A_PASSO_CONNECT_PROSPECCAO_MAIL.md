# Connect: prospecção, templates e e-mail

## Resultado e pré-requisitos

Candidato 0.3.0: relacionamento comercial até venda/cliente ativo, qualificação, templates, mensagens revisadas e fila persistente SQL. Consulte `planejamento/estado_continuidade.json` para a versão online e a evidência atual; o código local não comprova publicação.

Precisa de acesso à empresa/carteira correta. Consulta não permite gravações. Aprovar mensagens e controlar a fila exige administrador. O envio real exige caixa Microsoft vinculada explicitamente ao tenant EBT, permissão Mail.Send application e consentimento/configuração segura. Não copie credenciais de CASST ou arquivos de origem.

## Uso comercial

1. Abra Relacionamentos e pesquise antes de cadastrar. Avisos de duplicidade apresentam apenas registros permitidos.
2. Cadastre contato/organização/responsável. Em Qualificação, informe origem, cargo, segmento, necessidade real, decisor confirmado, canal e melhor horário. Fonte aceita HTTPS sem credenciais.
3. Registre observações e crie uma tarefa com ação planejada e prazo. A agenda mostra janelas de hoje/atraso/semana; contadores são calculados no servidor. Exportação `.ics` é importação manual no calendário.
4. Atualize a etapa até Cliente ativo quando a venda estiver concluída. O mesmo ID conserva histórico e qualificação. O sistema registra a primeira conversão feita nessa versão; não inventa data histórica para clientes anteriores.
5. Continue o relacionamento comercial pelo mesmo registro. Pedidos, execução operacional e financeiro pertencem aos outros aplicativos.

## Templates

1. Em E-mail → Modelos, crie ou edite um modelo. Escolha E-mail, WhatsApp ou roteiro de ligação e o objetivo: primeiro contato, retorno, acompanhamento de proposta ou cliente ativo.
2. Use `{nome}`, `{empresa}`, `{email}`, `{cargo}` e `{necessidade}`. Sem organização cadastrada, a referência é “sua empresa”. Informações desconhecidas não são inventadas.
3. Abra o contato e selecione Template comercial. Confira a prévia preenchida e ajuste o texto. Para e-mail, prepare o rascunho; para WhatsApp, abra o texto no aplicativo; para ligação, use o roteiro. Abertura/cópia não registra contato realizado.
4. Em Nova mensagem também é possível aplicar um modelo ao contato selecionado.
5. Atualizar um modelo afeta as próximas preparações. Rascunhos e versões já revisados preservam o conteúdo de origem. Se o modelo mudar entre prévia e salvamento, aplique a nova versão.

## E-mail e confirmação automática Outlook

1. Prepare mensagem individual ou lote de até 100 contatos existentes com e-mails distintos. Lote cria rascunhos; não dispara automaticamente.
2. Confira destinatário, assunto, corpo e anexo. Anexo precisa pertencer ao contato, estar na versão aprovada e passar pela inspeção permitida no ambiente.
3. Administrador aprova a versão. Editar invalida a aprovação.
4. Com Microsoft configurada, solicite envio real. A fila usa quota diária, intervalo por mensagem e pausa persistente. Sem configuração, o envio fica indisponível e os rascunhos continuam utilizáveis.
5. O retorno Graph atualiza automaticamente estado e histórico CRM, sem confirmação manual normal. “Aceito pela Microsoft” representa aceite da solicitação; entrega/leitura não são inferidas.
6. Timeout, reinício ou retorno incerto pausam a fila. Confira o resultado antes de reconciliar; não repita automaticamente uma mensagem incerta. A reconciliação manual exige motivo/evidência. Leitura automática dos Itens Enviados depende de uma integração adicional autorizada.
7. Supressões por e-mail/domínio são verificadas novamente no envio. Exportação `.eml` é rascunho sem anexo e não representa envio.

## SQL e arquivos

O runtime suportado usa .NET/EF Core/SQL Server, com isolamento do schema `ebt_connect` no banco compartilhado existente. MailDrafts/Templates/Revisions/Settings/Suppressions/Quotas substituem a persistência MongoDB das funções adaptadas. Users/Sessions/Memberships e Contacts são as fontes únicas de identidade e contatos. Pacotes Mail/Emergent antigos permanecem fontes históricas fora do build/deploy; não foram apagados nem usados para importar dados reais.

Principais arquivos: `MailEndpoints.cs`, `GraphMail.cs`, `MailModels.cs`, `CrmEndpoints.cs`, `CommercialTemplates.tsx`, `MailPanel.tsx`, `QuickSearch.tsx`; migrations ConnectMail/CommercialProspection; `sql/connect-commercial-20261009.sql`; revisão em `docs/qualidade/REVISAO_COMERCIAL_MAIL_20261009.md`.

## Validação e continuidade

Execute no checkout revisado, com SQL local exclusivo de QA e configuração privada em `tmp/runtime`:

```powershell
python scripts/verify_sql_runtime.py
python tests/integration/mail_connect_qa.py
dotnet run --project tests/WazVox.ProtocolTests -c Release -- --mail
dotnet run --project tests/WazVox.ProtocolTests -c Release -- --mail-sql
```

No frontend: `npm.cmd run test:unit`, `npm.cmd run build` e `npm.cmd run test:e2e`. Termine o build frontend antes de compilar backend: o Vite troca os arquivos wwwroot, e builds simultâneos podem divergir nos assets. Testes de autenticação usam uma janela compartilhada de QA, mantendo o limite do produto.

API/SQL: 12 cenários locais aprovados. Protocolo: 12 cenários com HTTP controlado. Worker: 8 cenários SQL, incluindo concorrência, intervalo medido e interação automática após aceite. Frontend: 9 testes de contexto. Browser: 22 cenários aprovados localmente, incluindo desktop/mobile, templates, contexto e permissões. CI da fonte publicada aprovado: 22 browser, 12 Mail API/SQL, 8 worker SQL, 2 scanner real e 10 restore isolado sintético. Script de publicação executado duas vezes em QA. Online: 34 checks HTTP e navegador desktop/mobile. Ver evidencias/connect_mail_ci_20261009.json e evidencias/connect_commercial_online_20261009.json; isso não comprova scanner/restore Azure ou envio Microsoft real.

Revise diff, arquivos e segredos; atualize estado; salve com `python scripts/checkpoint_github.py --approve --push`. Só anuncie GitHub salvo após SHA remoto igual. Exporte com `python scripts/exportar_continuidade.py`; pacote contém código revisado, sem configuração privada ou banco. ChatGPT normal usa o prompt de retomada e acesso efetivo ao GitHub/pacote; não há transferência automática de créditos/sessão.

## Limites e solução de problemas

- Microsoft ainda não configurada/homologada neste Connect: prepare/revise mensagens, mas não considere envio real comprovado. Não habilite envio sem caixa/permissões corretas.
- Arquivo sem inspeção: aguarde scanner autorizado; não contorne a proteção. Scanner Azure e restore Azure isolado continuam pendentes.
- Versão divergente: atualize e confira os dados antes de salvar, sem apagar o histórico.
- Troca de empresa/perfil: dados anteriores são descartados; permissões permanecem no servidor.
- Busca sem resposta: a tela apresenta erro e tentativa novamente; não confundir erro com cadastro vazio.
- Importação Excel ampliada, OAuth individual e reconciliação automática de Itens Enviados ainda são pendências registradas. CSV controlado continua existente.
- Orçamento documental permanece 180h de entregas + 20h de reserva; horas reais não foram inventadas.

## Publicação verificada

Versão 0.3.0 online em https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io. Fonte `bde34225781702f08158f9d832956c4ec326b469`; revisão `ebt-connect-hml--connect030-bde3422`. Migração aditiva no banco existente: seis tabelas Mail com 30 predicados RLS e campos de qualificação; valores originais dos sete contatos preservados por hash, catálogo/contagens dos outros schemas iguais. Sessão anterior e cinco IDs da carteira consultada preservados. Ambiente, secrets, identidade, ingress e recursos iguais. Nenhum e-mail real enviado nesta revisão. O checkpoint documental final pode ser posterior ao SHA compilado.
