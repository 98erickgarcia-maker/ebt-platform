# EBT — prospecção econômica, contatos e automações

Extensão pronta em código para o aplicativo FastAPI/MongoDB/React criado na Emergent. O backend de referência foi fornecido pelo usuário; a interface original, `email_engine.py` e `graph_mailer.py` não estavam disponíveis. O pacote oferece um módulo e uma tela reais, com pontos de integração explícitos. Não substitui o EBT Connect .NET nem altera CASST ou bancos atuais.

## Links confirmados do GitHub

- Repositório: [98erickgarcia-maker/ebt-platform](https://github.com/98erickgarcia-maker/ebt-platform).
- Branch desta entrega: [codex/prospeccao-emergent](https://github.com/98erickgarcia-maker/ebt-platform/tree/codex/prospeccao-emergent).
- Código para a Emergent: [entregas/emergent-prospeccao-v1](https://github.com/98erickgarcia-maker/ebt-platform/tree/codex/prospeccao-emergent/entregas/emergent-prospeccao-v1).
- Pedidos prontos: [PEDIDOS_EMERGENT.md](https://github.com/98erickgarcia-maker/ebt-platform/blob/codex/prospeccao-emergent/entregas/emergent-prospeccao-v1/docs/PEDIDOS_EMERGENT.md).
- Revisão desta entrega: [pull request nº 5](https://github.com/98erickgarcia-maker/ebt-platform/pull/5).

O branch concentra somente esta extensão e seu workflow. A aplicação Emergent deve importar o pacote e adaptar os pontos descritos abaixo; publicar código no GitHub não ativa contas ou faz deploy.

## Funcionalidades entregues

- Painel inicial, contatos e próxima ação; origem/data da informação, empresa, CNPJ numérico ou alfanumérico, CNAE, município, responsável, cargo, e-mail, telefone, site e LinkedIn.
- Links diretos de e-mail, telefone, WhatsApp, site, LinkedIn e mapa; indicação da qualidade do dado.
- Templates de apresentação, retorno, SST e WhatsApp, com variáveis, prévia e versões; sem IA.
- Área específica de prospecção automática: receitas por UF/município/CNAE, lotes, intervalos, pausa, cursor persistido, deduplicação por CNPJ e orçamento mensal atômico.
- E-mail como canal principal: clique de aprovação, agendamento durável, conector Microsoft automático que reutiliza as credenciais e o remetente do disparador, e alternativa OAuth por usuário.
- Evidência por API: aprovação, identificador imutável, resposta do Graph e reconciliação da mensagem nos Itens Enviados. Exportação JSON; nenhuma captura de tela exigida. Entrega ao destinatário não é presumida.
- WhatsApp oficial: chamada Cloud API de template, confirmação do número/opt-in, orçamento, webhook HMAC, deduplicação de eventos e evidências separadas de envio, entrega e leitura.
- Repetir o mesmo conteúdo WhatsApp recupera a operação persistida, inclusive após recarregar a tela ou editar notas; o histórico mostra payload e estado. A chave de aprovação não pode ser reutilizada com outro conteúdo. Esta v1 conserva uma operação por número remetente/destinatário/template/idioma/parâmetros; versão e opt-in são contexto separado. Cadências futuras precisam de uma nova aprovação definida por etapa e tratamento explícito do resultado anterior.
- Orçamento WhatsApp reserva centavos arredondados para cima, com teto arredondado para baixo. Operações recusadas/adiadas/bloqueadas pelo limite e sem ID do provedor têm retomada explícita após corrigir a causa. Operação aceita ou incerta nunca é retomada automaticamente.
- WhatsApp manual: botão abre a conversa com o template preenchido para concluir o envio no WhatsApp. Guarda telefone, texto, versão, digest e responsável no histórico, exportável em JSON. Esse registro comprova a preparação, sem presumir envio manual.
- Simulador de custos com valores informados; busca e templates fazem zero chamadas de IA/API paga. Tarifas Meta, Microsoft 365, infraestrutura e suporte continuam sendo custos separados.

## Como incorporar

1. Faça backup do projeto e use branch próprio. Copie `backend/ebt_prospecting` para a pasta backend da aplicação e `frontend/ProspectingArea.jsx` + `prospecting.css` para seus componentes.
2. Reutilize `app`, `db` e `get_current_user` que já existem em `server.py`. Depois de defini-los e antes de iniciar o servidor, acrescente:

```python
from ebt_prospecting import install_prospecting
prospecting = install_prospecting(app, db, get_current_user)
```

3. Acrescente um item de navegação “Prospecção automática” na interface autenticada:

```jsx
import ProspectingArea from './components/ProspectingArea';
// Renderizar dentro da navegação autenticada que já existe:
<ProspectingArea />
```

4. Confira o lock existente antes de acrescentar `backend/requirements.txt`. O módulo aceita a interface assíncrona Motor já usada no aplicativo e PyMongo Async. Não refaça a conexão MongoDB.
5. Acrescente as variáveis `EP_*` de `.env.example` aos Secrets da Emergent. Preserve os valores existentes. `OWNER_EMAIL` e `FRONTEND_URL` precisam estar definidos. A interface chama a API na mesma origem; configure CORS somente para as origens reais, com credenciais, sem `*`.
6. O aplicativo fornecido usa startup/shutdown: o módulo registra os dois eventos. Se a versão real usar `lifespan`, incorpore `prospecting['start']()` / `prospecting['shutdown']()` nesse lifespan e remova os handlers duplicados. Não iniciar dois loops no mesmo processo.
7. O modo padrão `application` usa `MS_CLIENT_ID/MS_TENANT_ID/MS_CLIENT_SECRET` ou `AZURE_*`, além de `EP_SENDER_MAILBOX`, `SENDER_MAILBOX` ou `settings.sender_mailbox`. A autenticação do conector é automática, sem janela de login. Reutilize o registro Entra do disparador e restrinja suas permissões à caixa autorizada. Para rascunho + confirmação via Itens Enviados, a aplicação precisa `Mail.ReadWrite`; para enviar, `Mail.Send`, ambos com consentimento administrativo. Credenciais de login com apenas `User.Read` não substituem essas permissões. O módulo não concede permissões na conta.
8. Primeiro valide um rascunho e um envio destinado a uma caixa controlada. Ative `EP_EMAIL_SEND_ENABLED=true` quando as permissões e o remetente estiverem corretos. O código não foi conectado à conta real nesta entrega. Um envio com resultado ambíguo fica `unknown` e não é repetido automaticamente.

   Se o job ficou `needs_connection`, corrija a conexão e use “Retomar após corrigir Outlook”. A API permite isso somente se nenhum ID de mensagem foi criado e contato/destinatário/versão continuam iguais. `unknown` não pode ser retomado por esse botão.
9. O modo alternativo `delegated` usa `EP_MS_REDIRECT_URI` registrado como Web no Entra e `EP_TOKEN_KEY` (Fernet). A autorização por usuário só aparece nesse modo. Não é o padrão pedido pelo usuário.
10. Para WhatsApp oficial, configure os Secrets da Meta, número autorizado, template já aprovado e custo conservador por mensagem. Registre o webhook `/api/prospecting/whatsapp/webhook`. Mantenha o envio desativado até o teste com número autorizado. `wa.me` é somente link, não integração oficial.

O middleware bloqueia os endpoints de login temporário e limpeza global do backend de referência. Isto precisa ser considerado na integração; a autenticação Microsoft existente é mantida. Todas as rotas novas são limitadas ao proprietário configurado, com espaço derivado no servidor. A extensão ainda não implementa equipes com múltiplos atendentes.

## Dados para descoberta

A automação encontra empresas em um catálogo local previamente importado. Não consulta a internet para inventar contatos, não varre sites nem compra listas. Use uma base autorizada e atualizada, incluindo e-mail empresarial quando disponível. O exemplo é inteiramente sintético. Dados brutos da Receita exigem juntar Empresas, Estabelecimentos e Municípios segundo o dicionário; `backend/convert_csv.py` converte um CSV já normalizado em lotes de até 1.000 empresas, filtrando UF/CNAE. Depois importe os JSON na tela com a fonte e a data reais.

Não copiar clientes/credenciais CASST. Contatos novos usam coleções `ebt_p_*`; os IDs e o histórico das coleções antigas não são substituídos. A incorporação de contatos antigos deve preservar o ID de origem e tratar duplicidades antes de qualquer migração.

## Verificações

```text
cd backend
python -m pip install -r requirements-test.txt
python -m pytest

cd ../frontend
npm ci
npm run build
```

Para o navegador local, em um terminal: `EP_QA_ONLY=1 python -m uvicorn qa_server:app --app-dir tests --host 127.0.0.1 --port 5198`, executado em `backend`; no outro, `npm run test:e2e` em `frontend`. Em PowerShell, configure `$env:EP_QA_ONLY='1'` antes do comando. Esse servidor usa dados sintéticos e nunca deve ser publicado. O teste MongoDB real utiliza somente `EP_TEST_MONGO_URL` e um banco temporário com nome `ep_synthetic_test_*`; ele não lê `DB_NAME` de produção.

Leia [o roteiro de pedidos à Emergent](docs/PEDIDOS_EMERGENT.md), [a pesquisa e a revisão](docs/PESQUISA_E_REVISAO.md) e [o guia WhatsApp/COREN](docs/WHATSAPP_E_COREN.md).

Para começar, leia [o documento de entrega com os links GitHub e próximas automações](docs/ENTREGA.md).

## Retorno à versão anterior

Antes de integrar, registre o commit do aplicativo real e guarde sua configuração. Para reverter, primeiro desative os envios `EP_*`, pare o worker da extensão, retire `install_prospecting` do startup/lifespan e o item de navegação/componente. Reverta somente o diff de integração. Preserve as coleções `ebt_p_*` e as evidências; não execute limpeza global nem altere credenciais ou banco do disparador existente. A remoção do middleware também retira seu bloqueio de rotas temporárias: mantenha essas rotas excluídas do aplicativo de produção.
