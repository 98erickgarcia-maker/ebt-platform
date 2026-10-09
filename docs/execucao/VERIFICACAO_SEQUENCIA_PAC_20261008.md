# Verificação e atualização da sequência PAC — 08/10/2026

O pedido atual autoriza execução somente na EBT Platform. A branch `main` ainda contém a baseline G0; a sequência vigente possui 17 pacotes e runtime Connect na branch de continuidade, base `efba4e1f1df422d0d0b394f3c00b360624ce245b`. Esta revisão preserva essa árvore e integra correções em uma branch própria. Não recria a fundação dos PRs #2/#3/#6/#7 nem substitui o Connect pelo snapshot #9.

## Sequência conferida

1. PAC-01 → PAC-02 → PAC-03: baseline e fundação já possuem implementação/evidências publicadas; seus CIs históricos valem somente para os respectivos SHAs.
2. PAC-05 → PAC-06 → PAC-07: comparar com identidade, SQL RLS, sessão, CSRF, auditoria e onboarding do Connect vigente. O plano PAC-07 do PR #8 não é prova de execução adicional.
3. PAC-08 → PAC-09 → PAC-10 → PAC-13: cadastro, histórico, importação e tarefas presentes no runtime; corrigir o contexto antes de ampliar as jornadas.
4. PAC-18 → PAC-19 → PAC-20: comunicação do recorte; identificar destinatário e bloquear transferência incompatível antes do aceite. Texto WazVox real registrado é evidência histórica, sem novo envio nesta revisão.
5. PAC-11 → PAC-12: documentos presentes; scanner privado e recuperação Azure exigem suas próprias provas.
6. PAC-16 → PAC-17: fechar candidato somente com regressão integrada pertinente, scanner, restore e aceite operacional. Site e Flow permanecem adiados no recorte vigente.

A [conferência estruturada](../../evidencias/verificacao_sequencia_pac_20261008.json) enumera os 17 pacotes, tickets e gates. A baseline conserva 180h de entregas e 20h de reserva; horas reais não foram estimadas a partir da duração desta sessão. Seus 238 cenários não foram promovidos em lote.

## Correções aplicadas, aguardando regressão integrada

- **R01:** integrado o PR #12; troca/navegação limpa tarefas, notas, documentos e conversas, e invalida consultas antigas. Regressões de navegador incluem atraso e erro da consulta do contato B.
- **R02:** o contrato retorna nome autorizado e o destinatário imutável da conversa, independente do cache de 25 contatos. Confirmação exige identificação. Testes cobrem filtro, mais de 25 contatos e telefone de cadastro alterado. Aproveitado somente o incremento do cliente HTTP do #9, com sete casos de contexto/CSRF/401/download.
- **R03:** mudança de carteira incompatível com canal vinculado retorna 409 e preserva o cadastro. Worker e atualização compartilham lock do contato. A regressão exige que o próximo recebimento ainda apareça e mantenha negativas A/B/carteira.
- **R04:** integrado o backend do #11 e acrescentada listagem/revogação à interface. A lista contém metadados, sem segredo ou hash; revogação repetida é segura. O navegador confere a operação após recarregar.
- **R05:** integrado o contrato do #11; a tela de convite oferece usar a conta existente. O aceite autentica o titular, preserva sua senha, cria somente o vínculo convidado e seleciona a empresa. Backend confere pessoa errada e repetição; navegador usa a senha original.

## Provas e execução

Build .NET Release sem avisos/erros; frontend TypeScript/Vite; sete testes do cliente HTTP; 17 testes de protocolo; dez de proxy; auditorias npm e .NET sem vulnerabilidades reportadas. Planejamento e organização aprovados. Esses resultados não provam SQL ou navegador.

A imagem SQL local não pôde ser baixada devido à política de rede. O workflow de produto agora prepara SQL Server efêmero e configuração sintética por execução no GitHub, aplica migrations, verifica HTTP/SQL, reinicia o servidor e executa Playwright. Scanner permanece desabilitado nessa fixture: ela não certifica scanner de produção. Relatórios sanitizados são anexados à CI.

Revisão do diff pelo mesmo agente; não foi declarada revisão independente. Estado de CI, SHA validado e pendências ficam na conferência estruturada. Nenhum merge em main, deploy ou envio real foi realizado. Os PRs de origem permanecem preservados.

## Continuidade

O checkpoint desta revisão aponta exclusivamente para `codex/ebt-enterprise-continuity-pac-review-20261008`. Usar `python scripts/checkpoint_github.py --approve --push` somente após rever o diff; confirmar SHA remoto. A branch original de continuidade não é sobrescrita. Após passar a CI integrada, preparar as provas externas pendentes com o ambiente e credenciais adequados, antes de promover os gates dependentes.
