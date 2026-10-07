# Prospecção EBT Implementation Plan

> Execução nativa nesta conversa, usando writing-plans, test-driven-development e verification-before-completion. O usuário já pediu programação e entrega do código.

**Goal:** entregar extensão econômica de prospecção e contatos pronta para integração na Emergent.

**Architecture:** módulo FastAPI usa a sessão e o MongoDB existentes; React recebe o endereço da API. Catálogo importado alimenta receitas agendadas e uma fila persistente. Templates e regras substituem geração repetitiva por IA.

**Tech Stack:** Python 3.11+, FastAPI, MongoDB com API assíncrona compatível Motor/PyMongo, React, MSAL, Fernet.

**Spec:** ESPECIFICACAO.md.

## Restrições

Preservar todos os fontes atuais; dados sintéticos nos testes; isolamento pelo espaço derivado da sessão; envio por API desativado por padrão, somente após aprovação/configuração; sem LLM/API paga; sem mudar a baseline 180h + 20h.

## Review Focus

Deduplicação concorrente e retomada depois de queda; limite mensal não pode ser ultrapassado por workers simultâneos; outro usuário não pode ler nem alterar registros; troca de contato deve limpar conteúdo e rejeitar respostas antigas; OAuth não pode aceitar estado de outro navegador nem repetir criação ambígua de rascunho.

## Etapas

- [x] Criar testes negativos de CNPJ, templates, isolamento, origem, duplicação, orçamento e fila; observar falha antes de implementar.
- [x] Implementar backend/domain.py (normalização, pontuação, links), service.py (MongoDB, receitas, contatos), router.py (contratos HTTP e autorização), outlook.py (conexão automática, OAuth alternativo, rascunho/envio e reconciliação).
- [x] Criar frontend/ProspectingArea.jsx e CSS com início, contatos, automações, templates e custos; verificar integração consumidor/produtor por E2E.
- [x] Acrescentar adaptador install.py, worker com ciclo durável, conversor CSV de dados oficiais e instruções Emergent.
- [x] Validar backend (36 aprovados, 1 MongoDB real ignorado localmente), Playwright (4 aprovados), build, dependências de produção e prompts. Registrar em evidence/VALIDACAO.json.
- [ ] Publicar o branch e revisar o CI MongoDB real; empacotar para Emergent. Integração/autenticação real permanece pendente.

O pacote é isolado na pasta entregas; não será cometido junto das alterações acumuladas do repositório.
