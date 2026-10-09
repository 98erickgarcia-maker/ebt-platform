# EBT FLOW + AURA — Meu dia e Contato 360

**Produto:** EBT Platform / EBT Connect.
**Branch:** `feat/ebt-flow-aura-daily-contact360-20261009`.
**Base empilhada:** PR #15, commit `2ff1007060f60622a53335c712575cbe3903649f`.
Não integrar esta branch diretamente em `main`. A publicação existente pode não corresponder à fonte de trabalho.

## Mudanças
- **FLOW / Meu dia:** hero escuro com representação visual de conexões, hierarquia editorial, ação real para tarefas, quatro indicadores com filtros existentes, próximos passos e etapas legíveis.
- **AURA / Contato 360:** panorama obtido do contato selecionado (etapa, organização e prazo da próxima ação), com o mesmo ID e os módulos de cadastro/histórico/tarefas/documentos preservados.
- Tokens: preto `#111214`, grafite `#1B1D20`, off-white `#F6F6F4`, laranja `#FF853E`; estilos escopados a estas duas telas, sem alterar identidade de outras marcas.
- Acesso por teclado e foco existentes mantidos; CSS inclui redução de movimento, responsividade e impressão.
- Não adiciona dados fictícios, tela sem ação real, novos endpoints, alteração de tenant, SQL, credenciais ou envios.

## Verificações de aceite
1. `npm run build` e `npm run test:e2e` na CI do SHA candidato com banco e login de QA sintéticos.
2. Teste `src/frontend/e2e/flow-aura.spec.ts`: Platform → Meu dia, quatro indicadores, clique para lista, contato sintético, região de panorama acessível e retorno mantendo busca.
3. Inspecionar visualmente 320, 390, 768 e 1366 px, sem rolagem horizontal do documento e sem perder informações; verificar também zoom, textos longos, contraste e foco.
4. Conferir que o contato não foi recriado e que operações e filtros anteriores continuam autorizados no backend.
5. Revisão cruzada independente e aceite visual ainda são gates separados. CI verde não é homologação de produção.

**Sem merge, deploy, serviço externo ou envio de mensagem nesta entrega.**
