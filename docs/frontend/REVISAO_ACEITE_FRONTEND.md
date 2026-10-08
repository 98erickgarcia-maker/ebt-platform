# Revisão e aceite de frontend por pacote

## Entrada

Pacote/ticket, commit e versão do destino, layout candidato, perfil, tenant/carteira, registros sintéticos, rota/jornada, critérios de negócio e origem. Revisar texto de tarefa e decisão de layout antes de produzir componentes. Código de teste e interface são entregues juntos no recorte autorizado.

## Passagem própria de revisão

Conferir diff completo: primitivas reaproveitadas, fontes únicas de token, ausência de override global sem motivo, nomenclatura, ID/vínculos, contratos, cache e estados. Conferir ação existente, foco/teclado, semântica de formulário, responsividade e permissão real. Identificar autoria da revisão; a mesma IA revisando não equivale a revisão independente.

## Verificação automatizada prevista

Build/lint/tipos pertinentes; componentes com regras relevantes; jornada de navegador com salvar/reload, filtro/seleção mantidos e mesma identidade; perfis/tenant A/B e ID direto; estados erro/vazio/negado/conflito quando aplicáveis; teclado/Escape/retorno de foco; larguras previstas e captura vinculada à versão. Ferramenta de acessibilidade automática ajuda, mas não comprova toda WCAG ou compreensão do fluxo. Reutilizar os cenários existentes por versão/escopo; não criar testes redundantes por cada componente meramente visual.

## Inspeção visual e jornada

- Cabeçalho e ações têm hierarquia clara e nomes iguais para operações equivalentes.
- Busca informa seu escopo e produz resultado; ação futura não aparenta pronta.
- Menu mostra contexto e capacidades disponíveis sem esconder funções essenciais.
- Formulário conserva dados em falha e mostra motivo/recuperação.
- Lista/detalhe usam a mesma identidade; retorno preserva filtros e posição.
- Salvar demonstra persistência após reload, não apenas toast.
- Sem corte, sobreposição ou perda de ação em celular; teclado alcança ações e o foco retorna corretamente.
- Status usa texto além de cor, contraste e alvos conferidos conforme o contrato.
- Perfil de consulta não altera; operações por ID continuam autorizadas no backend.

Registrar resultado observado e a imagem realmente inspecionada, com rota, largura, estado, usuário sintético e versão. Screenshot capturado não é automaticamente screenshot revisado. Se já estiver no Codex, continuar normalmente com navegador disponível; sinalizar passagem apenas por ferramenta/acesso realmente ausente.

## Fechamento

O gate de interface é parte dos gates de produto existentes, sem estado adicional fictício. Falha de jornada/identidade/autorização bloqueia dependentes; problema cosmético tem impacto e decisão registrados. Aceite visual do usuário complementa testes técnicos. Salvar no GitHub não comprova publicação nem conformidade.

Usar [template](../../templates/REVISAO_FRONTEND.md) e [revisão local/online](../qualidade/REVISAO_AUTOMATIZADA_LOCAL_E_ONLINE.md). O [contrato visual](PADRAO_VISUAL_E_COMPONENTES.md) define a referência, e o [catálogo de melhorias](../../planejamento/melhorias_frontend.json) mantém sugestões separadas do backlog executado.
