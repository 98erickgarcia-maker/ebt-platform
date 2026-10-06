# Runbook candidato: migration e compatibilidade

## Entrada

Migration do recorte, versão anterior sintética, destino QA conferido, backup consistente, índices e consumidores que serão afetados. Responsável técnico confirma a estratégia de retorno; ausência desses itens impede execução da migração daquele recorte.

## Procedimento

1. Registrar schema/versão atuais e lista de migrations aplicadas.
2. Conferir diff gerado, unicidade por tenant, campos opcionais/obrigatórios, FKs e efeitos nos IDs existentes.
3. Aplicar em banco vazio de QA para provar instalação nova.
4. Aplicar em cópia sintética da versão anterior para provar atualização.
5. Comparar contagens, IDs/vínculos, estado e cenários críticos, incluindo permissão e concorrência em SQL.
6. Ensaiar rollback seguro ou forward fix conforme desenho. Downgrade destrutivo não substitui recuperar dados.
7. Guardar comando, versão, resultado e evidência sanitizada; manter falhas anteriores separadas do resultado conclusivo.

## Saída

Ambos os caminhos passam; consumidores usam contratos compatíveis; retorno é conhecido e ensaiado. Nenhuma migração antiga é reescrita para ocultar diferença histórica. Produção real exige destino/janela/backup/autoridade específicos e não foi autorizada por este runbook.
