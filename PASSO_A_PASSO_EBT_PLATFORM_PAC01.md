# PASSO A PASSO — EBT Platform PAC-01

## Objetivo e resultado alcançado

Preparar o primeiro módulo da **EBT Platform**, o **EBT Connect**, sem transformar qualquer sistema-fonte em produto final.

Resultado desta branch:

- fontes e hashes remotos congelados;
- fluxo mínimo do Connect definido;
- mapa tela -> contrato -> dado;
- Design System EBT v1 documentado;
- limites de reuso, dependências e licenças registrados;
- evidência atual da fonte separada de evidência histórica;
- ordem dos primeiros PRs definida;
- G0 aprovado para fundação, condicionado ao CI do commit mesclado.

## Regra central

O projeto antigo pode ensinar regras e contratos, mas não vira a EBT Platform. A nova plataforma recebe árvore, marca, componentes, configuração e validação próprias. Reuso é por capacidade comprovada, não por cópia integral.

## Como continuar

1. Mesclar o PAC-01 somente com CI documental verde.
2. Abrir PAC-02 em branch própria.
3. Registrar o ADR do Core inicial.
4. Criar a solução real `Ebt.Api`, `Ebt.Web` e testes.
5. Centralizar tokens/componentes do Design System antes das páginas de domínio.
6. Separar configuração pública de segredos.
7. Criar fixtures sintéticas A/B sem dados reais.
8. Validar build backend e frontend em clone limpo.
9. Só depois avançar para SQL/diagnóstico/CI do PAC-03.

## Arquivos principais

- `docs/design/EBT_CONNECT_DESIGN_SYSTEM_V1.md`
- `docs/execucao/PAC01_BASELINE_EBT_CONNECT_2026-10-07.md`
- `evidencias/execucao/P01-01/source-manifest.json`
- `evidencias/execucao/P01-01/registro.md`
- `evidencias/execucao/P01-02/registro.md`
- `evidencias/execucao/P01-03/registro.md`
- `evidencias/execucao/P01-04/registro.md`
- `evidencias/execucao/P01-05/registro.md`
- `evidencias/execucao/P01-06/registro.md`

## Validação aplicável nesta fase

- revisão do diff;
- hashes reproduzíveis;
- rotas/contratos observados, sem endpoint inventado;
- CI documental do repositório.

Ainda não aplicável:

- build frontend/backend EBT;
- teste SQL EBT;
- teste E2E EBT;
- deploy.

Essas provas começam no PAC-02/PAC-03 porque o runtime EBT ainda não existia antes desta execução.
