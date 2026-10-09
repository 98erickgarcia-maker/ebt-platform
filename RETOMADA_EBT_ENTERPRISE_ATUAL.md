# Retomada EBT Enterprise — revisão de 08/10/2026

A versão revisada está em `.worktrees/revisao-github-20261008`. Preserve a árvore original e suas alterações. Não use o checkout original como substituto do snapshot revisado.

GitHub: https://github.com/98erickgarcia-maker/ebt-platform/tree/codex/ebt-enterprise-continuity-reviewed-20261008

Branch de checkpoint: `codex/ebt-enterprise-continuity-reviewed-20261008`. O último SHA confirmado fica em `tmp/continuidade/ultimo_checkpoint.json` do checkout revisado; verificar o SHA remoto antes de declarar salvo. As partes 1–3 tiveram build e continuidade aprovados; a quarta adiciona scanner fail-closed e guarda de liberação, com testes locais. Consulte o relatório e o CI da versão final.

Arquivos no checkout revisado:
- `docs/qualidade/REVISAO_GITHUB_INCREMENTAL_20261008.md`: resultados, regressões e limites.
- `planejamento/estado_continuidade.json`: estado e próximo recorte.
- `prompts/RETOMAR_EBT_ENTERPRISE.md`: contrato de retomada.
- `tmp/continuidade/EBT_ENTERPRISE_CONTINUIDADE.zip`: pacote exportado do commit revisado, sem dados privados.

Enterprise continua a família completa, Platform a fundação e Connect o primeiro produto. Orçamento 180h + 20h preservado. Não há novo deploy ou merge em main. Scanner real, restore Azure isolado e aceite operacional exigem prova própria.

No ChatGPT normal, abrir o prompt de retomada e fornecer acesso efetivo ao GitHub ou anexar o ZIP. Não há transferência automática de sessão ou créditos. No Codex, continuar usando as ferramentas disponíveis no checkout revisado.

Após mudanças autorizadas: revisar diff/caminhos/segredos, atualizar o estado e executar `python scripts/checkpoint_github.py --approve --push` no checkout revisado. O agendador usa somente `--push` e recusa conteúdo novo sem revisão. Ele repete salvamentos revisados; não desenvolve o sistema nem contorna limites de créditos.
