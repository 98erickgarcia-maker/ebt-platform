# PAC-01 — Baseline do EBT Connect para EBT Platform

Data: 07/10/2026.

## Decisão principal

O **produto-alvo é EBT Platform**. O primeiro módulo de relacionamento é **EBT Connect**.

`crm-casst-web` é somente uma **fonte técnica legada de consulta** para contratos e comportamentos já aprendidos. Ele não é o produto-alvo, não define a marca, não será copiado integralmente e suas regras específicas de SST ficam fora do recorte inicial.

## Fontes congeladas

| Fonte | Papel | Ref congelada |
|---|---|---|
| `98erickgarcia-maker/ebt-platform` | alvo e fonte de verdade do plano | `4c185f761b2b5e212800464f4b450167a26c1b88` |
| `98erickgarcia-maker/crm-casst-web` | referência de CRM/contratos | `ce14f567ff2b529953e14e09b0a74b72a7cbeb6b` |
| `98erickgarcia-maker/ebt-enterprise-site` | referência de identidade EBT | `9c5e12c84f7dd7dff8aeb99314ce9ff505d5d4f7` |
| `98erickgarcia-maker/grupo-vikings-sst` | referência secundária de padrões de isolamento/dados | `b13140e16465585f37c6933b865666082883b7b9` |

A árvore local histórica citada no planejamento possuía alterações não publicadas. Ela permanece **evidência histórica**, não fonte de extração desta execução, porque o ambiente atual não permite confirmar seus arquivos não rastreados. A extração futura parte somente de refs reproduzíveis.

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

A fonte contém strings e saídas específicas da marca antiga em recursos como calendário. **Essas strings não são reutilizadas na EBT Platform.**

### Interface candidata

Fonte:

- `ProspectsPage.tsx` blob `30fb87bfec7e067cef412aac0cd110c84102dcd2`
- `ProspectWorkspaceDrawer.tsx` blob `e55d23191df8ede2a3b306b6a12d453da447df36`

Reaproveitar apenas padrões de jornada e estados. O visual aprovado para EBT Connect é definido em `docs/design/EBT_CONNECT_DESIGN_SYSTEM_V1.md`.

## Mapa tela -> capacidade -> contrato

| Tela EBT | Capacidade | Origem candidata | Regra EBT |
|---|---|---|---|
| Empresas | busca/paginação/filtro | prospects list | organização é entidade comercial neutra |
| Empresa detalhe | identificação/contexto | prospect detail | não expor vocabulário SST |
| Contatos | pessoas vinculadas | people + prospect people | vínculo pertence ao tenant/empresa |
| Prospecção | qualificação | prospect create/update | até cinco etapas no pacote |
| Timeline | histórico | interactions list/detail | nota interna != conversa |
| Próxima ação | responsável/prazo | interaction planned + next contact | responsável ativo e autorizado |
| Pipeline | etapa | status/stage a neutralizar | mudança gera histórico |
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

- EBT Connect / EBT Platform / EBT Enterprise;
- `#111214`, `#1B1D20`, `#F6F6F4`, `#FF853E`;
- sidebar EBT proprietária;
- componentes compartilhados;
- nenhuma marca da fonte técnica na aplicação EBT.

## Dependências e direito de uso

Os três repositórios consultados são privados e pertencem ao mesmo proprietário GitHub, mas não expõem licença no metadado do repositório. Isso **não é tratado como licença comercial automática de terceiros**.

Regra para PAC-02:

1. não copiar asset externo sem origem/licença;
2. não incorporar biblioteca fora do gerenciador de dependências;
3. registrar licença das dependências efetivamente escolhidas;
4. preferir ícones/bibliotecas com licença explícita;
5. usar dados sintéticos;
6. nenhum dado/segredo de cliente entra no novo repositório.

## Ordem dos primeiros PRs

1. **PAC-02A — estrutura real:** solution/backend/frontend/testes/configuração EBT.
2. **PAC-02B — Design System:** tokens, shell, componentes básicos e páginas vazias com estados.
3. **PAC-02C — dados sintéticos:** fixtures A/B e configuração de marcas sem forks.
4. **PAC-03 — SQL/diagnóstico/CI:** somente depois da árvore real estar reproduzível.
5. **PAC-05 a PAC-07 — identidade/tenant/segurança:** antes de liberar dados multiempresa.
6. **PAC-08 a PAC-10 — CRM Connect:** jornada funcional selecionada.

## Estado do G0

- fonte remota reproduzível: **sim**;
- fluxo mínimo fechado: **sim**;
- mapa inicial de contratos: **sim**;
- identidade EBT separada: **sim**;
- fonte local histórica não rastreada: **excluída da extração**, mantida apenas como evidência histórica;
- runtime do novo produto: **ainda não existe**, portanto nenhum teste de aplicação EBT é declarado como aprovado.

G0 fica **candidato a fechamento por revisão do PR e CI documental**. PAC-02 não deve copiar código de domínio antes dessa revisão.
