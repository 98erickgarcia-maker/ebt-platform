# Continuar EBT Connect

Primeira entrega online: https://ebt-connect-hml.greenrock-01c2b42d.brazilsouth.azurecontainerapps.io. Ler [guia](PASSO_A_PASSO_PUBLICACAO_CONNECT.md), [prova ao vivo](evidencias/connect_primeira_entrega_online.json), [SQL](evidencias/connect_sql_runtime_verificado.json) e [gates](docs/qualidade/STATUS_IMPLEMENTACAO_CONNECT.md).

Banco pago compartilhado existente e aplicações independentes. Identidade própria, certificado/keyring privado no SQL, administrador EBT e webhook WazVox instalados. 26 checks HTTP, isolamento A/B, grants e reinício verificados. Fixtures técnicas desativadas, firewall temporário removido. Recebimento, resposta e leitura reais por WazVox demonstrados; correção 0.1.5 de data.id/recipient_id publicada, sem reenvio.

Disponibilidade HTTP/SQL publicada na 0.1.4. Próximos passos: Scanner privado, recuperação Azure, CI hospedada e aceite de negócio. Publicação com valor variável autorizada; contato ao suporte F1 foi recusado. Configuração privada em tmp/private-integrations, fora de Git/ZIP. Preservar fontes, diferenças preexistentes e 180h + 20h, sem consumo inventado. Backlog/matriz permanecem planejados; atualizar status somente com prova específica.
