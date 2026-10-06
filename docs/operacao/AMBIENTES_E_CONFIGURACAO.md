# Runbook candidato: ambientes e configuração

Status: procedimento para futura implementação. Nenhum ambiente EBT de produto foi provisionado pela organização documental.

## Pré-requisitos

Ticket autorizado, fonte do recorte, nomes reais dos destinos QA e usuário com acesso necessário. Separar desenvolvimento, QA sintético, piloto real e produção. Nome de recurso e conexão devem ser confirmados antes de qualquer ação.

## Passos

1. Registrar aplicação/versão, finalidade, banco, storage, identidade, chaves e responsáveis.
2. Validar que o destino pertence ao EBT QA escolhido, sem reutilizar CASST/CRP/Nutrição/Vikings reais.
3. Mapear nomes de opções e origem dos valores privados; manter exemplos sem credenciais.
4. Definir diferença Dev/QA: modo de headers de desenvolvimento não autentica fora de Dev.
5. Conferir opções obrigatórias e falha segura quando ausentes; evitar fallback de conexão.
6. Iniciar somente com massa sintética. Conferir health e um registro persistido.
7. Registrar comandos reais e resultado; retirar do manual valores privados e links de convite.

## Verificação e retorno

Clone/config documentados iniciam no QA autorizado. Config incorreta não toca outro banco. Antes de trocar opção, salvar configuração segura anterior e definir retorno. Não apagar/recriar destino calculado sem confirmar caminho absoluto e escopo. Registrar pendência se ambiente/credencial ainda não existir.
