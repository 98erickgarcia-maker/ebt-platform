# Continuar EBT Connect

Primeira entrega online: https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io. Ler [guia](PASSO_A_PASSO_PUBLICACAO_CONNECT.md), [prova ao vivo](evidencias/connect_primeira_entrega_online.json), [SQL](evidencias/connect_sql_runtime_verificado.json) e [gates](docs/qualidade/STATUS_IMPLEMENTACAO_CONNECT.md).

Banco pago compartilhado existente e aplicações independentes. Identidade própria, certificado/keyring privado no SQL, administrador EBT e webhook WazVox instalados. 26 checks HTTP, isolamento A/B, grants e reinício verificados. Fixtures técnicas desativadas, firewall temporário removido. Recebimento, resposta e leitura reais por WazVox demonstrados; correção 0.1.5 de data.id/recipient_id publicada, sem reenvio.

Disponibilidade HTTP/SQL publicada na 0.1.4. Próximos passos: Scanner privado, recuperação Azure e aceite de negócio. CI hospedada aprovada no commit 92e4006; consultar evidencias/enterprise_continuidade_20261007.json. Publicação com valor variável autorizada; contato ao suporte F1 foi recusado. Configuração privada em tmp/private-integrations, fora de Git/ZIP. Preservar fontes, diferenças preexistentes e 180h + 20h, sem consumo inventado. Backlog/matriz permanecem planejados; atualizar status somente com prova específica.

## Retomada da EBT Enterprise completa

Ler [visão integral](docs/arquitetura/EBT_ENTERPRISE_SISTEMA_COMPLETO.md), [estado de continuidade](planejamento/estado_continuidade.json), [contrato do agente](prompts/AGENTE_EBT_ENTERPRISE.md) e [prompt para o ChatGPT normal](prompts/RETOMAR_EBT_ENTERPRISE.md). Repositório: 98erickgarcia-maker/ebt-platform; branch em planejamento/continuidade_github.json. Conferir SHA remoto e continuidade/CHECKPOINT.json antes de continuar.

Depois de cada incremento revisado: `python scripts/checkpoint_github.py --approve --push`. Falha não é salvamento remoto. Exportar pacote revisado com `python scripts/exportar_continuidade.py`; não incluir tmp/private-integrations. A tarefa Windows só repete conteúdo já revisado, sem executar produto nem transferir sessões automaticamente. Seguir [procedimento](docs/execucao/CONTINUIDADE_GITHUB_CHATGPT.md).
