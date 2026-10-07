# PAC-01 — Baseline do EBT Connect para EBT Platform

Data: 07/10/2026.

## Decisão principal

O **produto-alvo é EBT Platform**. O primeiro módulo de relacionamento é **EBT Connect**.

O repositório técnico legado usado nesta análise é somente uma **fonte de consulta para contratos, testes e comportamentos já aprendidos**. Ele não é o produto-alvo, não define a marca e não será copiado integralmente. Regras específicas do produto-fonte ficam fora do recorte inicial.

## Fontes congeladas

| Fonte | Papel | Ref congelada |
|---|---|---|
| `98erickgarcia-maker/ebt-platform` | alvo e fonte de verdade do plano | `4c185f761b2b5e212800464f4b450167a26c1b88` |
| `98erickgarcia-maker/crm-casst-web` | referência técnica de CRM/contratos | `ce14f567ff2b529953e14e09b0a74b72a7cbeb6b` |
| `98erickgarcia-maker/ebt-enterprise-site` | referência de identidade EBT | `9c5e12c84f7dd7dff8aeb99314ce9ff505d5d4f7` |
| `98erickgarcia-maker/grupo-vikings-sst` | referência secundária de padrões de isolamento/dados | `b13140e16465585f37c6933b865666082883b7b9` |

A árvore local histórica citada no planejamento possuía alterações não publicadas. Ela permanece **evidência histórica**, não fonte de extração desta execução, porque o ambiente atual não permite confirmar seus arquivos não rastreados. A extração futura parte somente de refs reproduzíveis. Se um arquivo local vier a ser proposto depois, G0 precisa ser reaberto para esse arquivo.

O manifesto reproduzível do recorte está em `evidencias/execucao/P01-01/source-manifest.json`.

## Fluxo mínimo escolhido

```text
login/ativação
  -> lista de empresas/prospecções
  -> criar/vincular contato
  -> abrir detalhe
  -> registrar conversa ou nota
  -> definir responsável e próxima ação
  -> mover etapa
  -> recarregar
  -> consultar histórico/timeline
```

O Design System prevê dashboard, relatórios e outras telas, mas o primeiro aceite funcional continua restrito ao contrato do Connect inicial.

## Contratos candidatos observados na fonte técnica

### Prospecção / organização

Fonte congelada:

- `ProspectEndpoints.cs` blob `7bfad713f13628f2cd99ae9b25286cd8c644d33e`
- `ProspectContracts.cs` blob `388c29d41565991b7d7061b5cab2b190d48ab990`
- `contracts.ts` blob `c2752b76638170700458ef246f4b939fe2c74ceb`

Operações candidatas observadas:

- `GET /api/prospects/`
- `GET /api/prospects/{id}`
- `POST /api/prospects/`
- `PUT /api/prospects/{id}`
- `POST /api/prospects/{id}/people`
- `PUT /api/prospects/{id}/primary-person`

Campos úteis observados: ID, nome/organização, cidade/UF, segmento, origem, status, responsável, pessoa principal, último contato, próximo contato, timestamps e `rowVersion`.

### Pessoas / contatos

Fonte:

- `PeopleEndpoints.cs` blob `525653d83d35a8f77fdaef8e0a54f78796870887`

Contrato candidato:

- listagem por tenant/perfil;
- atualização de pessoa;
- vínculo entre pessoa e registro comercial.

A normalização de canal não pode unir automaticamente pessoas de empresas diferentes.

### Histórico / próxima ação / agenda

Fonte:

- `CommercialInteractionEndpoints.cs` blob `615ea5ddff5f02b3a46f6ec483ed9cd5b76decf3`
- `CommercialInteractionContracts.cs` blob `b24e69948a90edfb63fb9da147ef1a6d78d83092`
- teste de endpoint blob `cbef32baf8dec8df230a76f0953e74a48c7c9c6e`

Operações candidatas observadas:

- `GET /api/interactions/`
- `GET /api/interactions/agenda`
- `GET /api/interactions/{id}`
- `POST /api/interactions/`
- `PUT /api/interactions/{id}`
- `POST /api/interactions/{id}/complete`
- `POST /api/interactions/{id}/cancel`

Comportamentos candidatos:

- paginação/filtros;
- vínculo a empresa/prospecção/pessoa;
- responsável;
- atividade planejada e realizada;
- sincronização da próxima ação;
- `rowVersion` para concorrência;
- isolamento por tenant e carteira.

Strings, nomes de arquivos e saídas da marca do produto-fonte **não são reutilizados na EBT Platform**.

### Pipeline

Fonte:

- `OpportunityEndpoints.cs` blob `c0719f421de58c5df088fb7e01c2e13f3b0fa0ce`
- `contracts.ts` blob `c2752b76638170700458ef246f4b939fe2c74ceb`

A fonte possui seis tipos de etapa. Para o Connect inicial, a apresentação será limitada a cinco colunas abertas/positivas: prospecção, qualificação, proposta, negociação e ganho. Perda é resultado terminal e não uma sexta coluna obrigatória. A implementação EBT deve manter IDs/estado persistido separados do rótulo visual.

### Interface candidata

Fonte:

- `ProspectsPage.tsx` blob `30fb87bfec7e067cef412aac0cd110c84102dcd2`
- `ProspectWorkspaceDrawer.tsx` blob `e55d23191df8ede2a3b306b6a12d453da447df36`
- `QuickInteractionDialog.tsx` blob `0d18972018f30705442d39ffc62042c89593664d`

Reaproveitar apenas padrões de jornada, validação e estados. O visual aprovado para EBT Connect é definido em `docs/design/EBT_CONNECT_DESIGN_SYSTEM_V1.md`.

## Mapa tela -> capacidade -> contrato

| Tela EBT | Capacidade | Origem candidata | Regra EBT |
|---|---|---|---|
| Empresas | busca/paginação/filtro | prospects list | organização é entidade comercial neutra |
| Empresa detalhe | identificação/contexto | prospect detail | sem vocabulário específico da fonte |
| Contatos | pessoas vinculadas | people + prospect people | vínculo pertence ao tenant/empresa |
| Prospecção | qualificação | prospect create/update | escopo fechado do Connect |
| Timeline | histórico | interactions list/detail | nota interna != conversa |
| Próxima ação | responsável/prazo | interaction planned + next contact | responsável ativo e autorizado |
| Pipeline | etapa | opportunity stage | mudança gera histórico e trata conflito |
| Agenda | atividades planejadas | interactions agenda | filtro e contador precisam concordar |
| Dashboard | leitura derivada | consultas agregadas futuras | não duplicar regra transacional |
| Relatórios | leitura | projeções futuras | não entra antes do dado-base estável |

## Limites explícitos

Fora do Connect inicial:

- financeiro;
- OS;
- propostas completas;
- estoque;
- inbox coletivo;
- WhatsApp oficial;
- disparos automáticos;
- regras SST;
- documentos regulatórios específicos;
- importador universal.

## Identidade visual congelada

A identidade vem do repositório EBT Enterprise, ref congelada acima:

- EBT Connect / EBT Platform / EBT Enterprise;
- `#111214`, `#1B1D20`, `#F6F6F4`, `#FF853E`;
- sidebar EBT proprietária;
- componentes compartilhados;
- nenhuma marca do produto-fonte na aplicação EBT.

Referências de marca:

- `site/public/assets/styles.css` blob `6b835c7476429e33011b7970a6689f1786c5b999`;
- `site/public/assets/ebt-logo-oficial.png` blob `684556cbf1c924191bb73419161ece096a8b6dfb`.

## Dependências e direito de uso

Os repositórios consultados são privados sob o mesmo proprietário GitHub usado para o projeto. Isso permite rastrear autoria/origem interna, mas **não converte automaticamente dependências ou assets de terceiros em licença comercial**.

Regra para PAC-02:

1. não copiar asset externo sem origem/licença;
2. não incorporar biblioteca fora do gerenciador de dependências;
3. registrar licença das dependências efetivamente escolhidas;
4. preferir ícones/bibliotecas com licença explícita;
5. usar dados sintéticos;
6. nenhum dado/segredo de cliente entra no novo repositório;
7. não reaproveitar o lockfile vulnerável da fonte técnica.

## Evidência atual da fonte técnica

No commit congelado `ce14f5...`, a execução GitHub Actions `37453203674` mostrou:

- backend: restore, build, testes, auditoria de pacotes, verificação de segredos e `git diff --check` aprovados;
- frontend: instalação, testes, lint e build aprovados;
- frontend: auditoria de dependências reprovada por duas dependências transitivas de alta severidade;
- SQL/E2E: cancelado, portanto sem prova conclusiva.

Consequência: o comportamento do fluxo é referência útil, mas o conjunto de dependências da fonte não é baseline do EBT Platform. PAC-02 cria a árvore e as dependências da EBT do zero; P04 refaz a validação de segurança/tenant/onboarding.

## Ordem dos primeiros PRs

1. **PAC-02A — estrutura real:** solution/backend/frontend/testes/configuração EBT.
2. **PAC-02B — Design System:** tokens, shell, componentes básicos e páginas vazias com estados.
3. **PAC-02C — dados sintéticos:** fixtures A/B e configuração de marcas sem forks.
4. **PAC-03 — SQL/diagnóstico/CI:** somente depois da árvore real estar reproduzível.
5. **PAC-05 a PAC-07 — identidade/tenant/segurança:** antes de liberar dados multiempresa.
6. **PAC-08 a PAC-10 — CRM Connect:** jornada funcional selecionada.

## Estado do G0

- fonte remota reproduzível: **aprovado**;
- fluxo mínimo fechado: **aprovado**;
- mapa inicial de contratos: **aprovado**;
- identidade EBT separada: **aprovado**;
- direitos/origem: **aprovado para fontes internas e marca EBT; terceiros continuam condicionados à licença**;
- fonte local histórica não rastreada: **fora da baseline e proibida para extração sem reabrir o gate**;
- runtime do novo produto: **ainda não existe**, logo não há teste runtime EBT a declarar.

**G0 está aprovado para iniciar a fundação PAC-02**, condicionado a manter o PR documental verde no commit efetivamente mesclado. Esse gate não aprova produção, segurança multiempresa nem qualquer módulo funcional.
