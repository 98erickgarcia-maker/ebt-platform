# Qualidade do frontend EBT Connect — 10/10/2026

## Incremento aplicado

Camada visual comum em `src/frontend/src/quality.css`, mantendo a identidade EBT, componentes de produto e contratos de API. Tipografia e espaçamento consistentes, cartões com bordas/sombras discretas, foco visível, controles com altura mínima de 44 px e navegação com área rolável em telas baixas.

Atalho de teclado “Ir para o conteúdo principal”, região principal nomeada pelo título e botão de fechar dentro do menu móvel. Ao abrir o menu, o foco chega ao botão de fechar; Tab permanece dentro da navegação e Escape devolve o foco ao acionador. Ao aumentar a janela para desktop, o estado móvel é encerrado.

Nenhum novo módulo, dependência, fonte externa, acesso, dado de cliente, mudança no banco ou envio foi introduzido. As alterações anteriores do workspace permaneceram preservadas.

## Evidência local do candidato

- TypeScript e bundle de produção aprovados; build isolado em `tmp/frontend-quality/dist`, sem substituir artefatos publicados.
- Quatro testes de navegador aprovados: salto para conteúdo; navegação em celular de 390×420; catálogo e painel diário em 320, 768 e 1440 pixels sem overflow horizontal; foco/Tab/Escape do menu móvel.
- Nove testes existentes do cliente de API aprovados, incluindo troca de contexto, logout, CSRF e destinos de download.
- Imagens de desktop e celular renderizadas e conferidas em `tmp/frontend-quality/daily-1440.png` e `daily-320.png`.
- Testes de apresentação usam respostas sintéticas interceptadas no navegador. Comprovam renderização e interação do frontend; não comprovam SQL, autenticação real, e-mail, backend ou publicação online.

## Reproduzir

Na pasta `src/frontend`, com dependências existentes:

```text
node node_modules/@playwright/test/cli.js test --config playwright.frontend-quality.config.ts
node node_modules/typescript/bin/tsc -b
node node_modules/vite/bin/vite.js build --outDir ../../tmp/frontend-quality/dist
```

Os testes novos usam Vite em loopback com porta exclusiva e não inicializam banco. O checkpoint revisado será salvo em `codex/frontend-quality-20261010`. Publicação permanece pendente de validação do candidato no ambiente real; não há promoção de gates ou declaração de conclusão da Enterprise.
