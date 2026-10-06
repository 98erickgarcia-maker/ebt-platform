# Runbook candidato: release, smoke e retorno

## Candidato

Identificar commit e manifesto; conferir gates do recorte; listar migrations/config; preservar versão anterior, dados e caminho de recuperação. Pacote e resultado de build não significam que houve deploy.

## QA e piloto

1. Confirmar destino e identidade do operador antes de executar qualquer implantação.
2. Conferir config sem expor segredos; distinguir revisão nova e anterior.
3. Instalar candidato em QA permitido; aplicar somente migration ensaiada pertinente.
4. Verificar saúde/prontidão e a jornada do recorte, não apenas status Running.
5. Conferir a versão servida, assets/contratos, proteção de rotas, negativo de tenant e persistência.
6. Registrar tempo, revision/commit/digest se existirem, resultado, captura sanitizada e limitações.
7. Piloto real exige participantes/aceite; usar ficha própria com autoria.

## Retorno

Se health/jornada/isolamento falhar, interromper expansão, preservar diagnóstico e retornar conforme estratégia validada. Não misturar rollback de código com rollback de banco destrutivo. Corrigir por forward fix quando essa for a única via segura aos dados. Conferir saúde e jornada após retorno.

## Produção

Somente no escopo autorizado e ambiente confirmado. Nenhum comando específico de Azure/DNS é inventado antes de conhecer a infraestrutura. Não mexer em MX, serviço pago ou banco de outro cliente a partir do planejamento. Registro de release preenchido depois da operação, não como intenção.
