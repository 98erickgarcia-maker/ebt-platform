# PASSO A PASSO — EBT Platform PAC-01

## Objetivo e resultado alcançado

Corrigir o alvo do trabalho para **EBT Platform** e preparar o primeiro módulo, **EBT Connect**, sem transformar o sistema-fonte em produto final.

Resultado desta branch:

- fonte e hashes remotos congelados;
- fluxo mínimo do Connect definido;
- mapa inicial tela -> contrato -> dado;
- Design System EBT v1 documentado;
- limites de reuso e licenças registrados;
- ordem dos primeiros PRs definida;
- evidências P01-01 a P01-06 registradas sem inventar execução runtime.

## Pré-requisitos para continuar

- revisar este PR;
- CI documental verde;
- iniciar PAC-02 somente em branch própria;
- usar dados sintéticos;
- não copiar segredos, bancos ou assets sem licença.

## Explicação simples

O projeto antigo pode ensinar como resolver certas regras, mas não vira a EBT Platform. A nova plataforma recebe sua própria árvore, marca, componentes e contratos. Reuso é feito por capacidade, não por cópia integral.

## Como continuar

1. Abrir o baseline do PAC-01.
2. Conferir o Design System.
3. Revisar hashes e exclusões.
4. Verificar CI documental.
5. Fechar G0.
6. Abrir PAC-02 para criar a solução real `Ebt.Api`, `Ebt.Web` e testes conforme os tickets da fase.
7. Implementar shell/tokens/componentes EBT antes das páginas de domínio.
8. Adicionar fixtures sintéticas A/B antes de qualquer dado real.

## Arquivos criados

- `docs/design/EBT_CONNECT_DESIGN_SYSTEM_V1.md`
- `docs/execucao/PAC01_BASELINE_EBT_CONNECT_2026-10-07.md`
- `evidencias/execucao/P01-01/registro.md`
- `evidencias/execucao/P01-02/registro.md`
- `evidencias/execucao/P01-03/registro.md`
- `evidencias/execucao/P01-04/registro.md`
- `evidencias/execucao/P01-05/registro.md`
- `evidencias/execucao/P01-06/registro.md`

## Validação

Aplicável agora:

- revisão do diff;
- workflow documental do repositório.

Não aplicável ainda:

- build frontend/backend EBT;
- teste SQL EBT;
- teste E2E EBT;
- deploy.

Esses itens não existem porque o repositório ainda estava em fase de planejamento antes desta execução.

## Limitações

A árvore local histórica citada no planejamento tinha arquivos modificados/não rastreados e não está disponível neste ambiente. Por isso ela não foi usada como fonte de extração. As refs remotas reproduzíveis foram escolhidas como baseline seguro.
