"""Promote only the current overview when a live proof actually passed."""
import json
from pathlib import Path


def finalize_live_documents(generated, emit):
    root = Path(__file__).resolve().parents[1]
    publication_path = root / 'evidencias/azure_connect_publicacao.json'
    proof_path = root / 'evidencias/connect_primeira_entrega_online.json'
    if not publication_path.exists() or not proof_path.exists():
        return
    publication = json.loads(publication_path.read_text(encoding='utf-8'))
    proof = json.loads(proof_path.read_text(encoding='utf-8'))
    if publication.get('published') is not True or proof.get('passed') is not True:
        return
    url = publication['url']
    messaging_path = root / 'evidencias/connect_wazvox_real_015.json'
    messaging_verified = messaging_path.exists() and json.loads(messaging_path.read_text(encoding='utf-8')).get('passed') is True
    messaging_state = 'Recebimento, resposta e leitura reais por WazVox demonstrados; correção 0.1.5 de data.id/recipient_id publicada, sem reenvio.' if messaging_verified else 'Mensagens/status reais permanecem pendentes.'
    next_step = 'Scanner privado, recuperação Azure, CI hospedada e aceite de negócio.' if messaging_verified else 'Homologação real de recebimento/resposta/status com número de teste definido, scanner privado, recuperação Azure, CI hospedada e aceite de negócio.'
    previous = generated['README.md']
    start = previous.find('\n## ')
    tail = previous[start:] if start >= 0 else ''
    emit('README.md', f'''# EBT Platform | primeira entrega Connect online

07/10/2026: [EBT Connect]({url}) publicado no banco pago existente sqldb-crm-casst-dev-v2, schema ebt_connect. Identidade própria, keyring SQL cifrado, 26 verificações ao vivo e sessão preservada após reinício. Webhook WazVox instalado. Valor variável da hospedagem autorizado pelo usuário; nenhum novo banco/SKU.

- [Acesso e publicação](PASSO_A_PASSO_PUBLICACAO_CONNECT.md).
- [Guia de uso](PASSO_A_PASSO_EBT_CONNECT.md).
- [Prova da entrega](evidencias/connect_primeira_entrega_online.json).
- [Estado dos gates](docs/qualidade/STATUS_IMPLEMENTACAO_CONNECT.md).

{messaging_state} Scanner, CI hospedada, restore Azure e aceite permanecem pendentes. O orçamento e o backlog abaixo preservam 180h + 20h; não representam testes aprovados ou horas efetivamente consumidas.
''' + tail)
    emit('CONTINUAR_EM_OUTRO_CHAT.md', f'''# Continuar EBT Connect

Primeira entrega online: {url}. Ler [guia](PASSO_A_PASSO_PUBLICACAO_CONNECT.md), [prova ao vivo](evidencias/connect_primeira_entrega_online.json), [SQL](evidencias/connect_sql_runtime_verificado.json) e [gates](docs/qualidade/STATUS_IMPLEMENTACAO_CONNECT.md).

Banco pago compartilhado existente e aplicações independentes. Identidade própria, certificado/keyring privado no SQL, administrador EBT e webhook WazVox instalados. 26 checks HTTP, isolamento A/B, grants e reinício verificados. Fixtures técnicas desativadas, firewall temporário removido. {messaging_state}

Disponibilidade HTTP/SQL publicada na 0.1.4. Próximos passos: {next_step} Publicação com valor variável autorizada; contato ao suporte F1 foi recusado. Configuração privada em tmp/private-integrations, fora de Git/ZIP. Preservar fontes, diferenças preexistentes e 180h + 20h, sem consumo inventado. Backlog/matriz permanecem planejados; atualizar status somente com prova específica.
''')
