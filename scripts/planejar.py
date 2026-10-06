"""Gera o planejamento documental. Não executa projetos, migrações ou deploys."""
from pathlib import Path
import json, hashlib, subprocess, re, shutil
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
OUT = ROOT / 'output/pdf'
EVID = ROOT / 'evidencias'
BASE = Path(r'C:\Users\Ivair Silva\Documents\ChatGPT')
CASST = Path(r'C:\Users\Ivair Silva\Documents\Codex\2026-08-18\CRM_CASST_WEB\.worktrees\crm-casst-foundation')
CRP = Path(r'C:\Users\Ivair Silva\Documents\Codex\2026-09-25\CRP_SITE\site')
GH = BASE / 'PROJETOS_GITHUB_2026-10-06/tools/bin/gh.exe'
DATE = '06/10/2026'

PHASES = []
def phase(code, name, hours, output, prerequisites, origin, gate, rows):
    PHASES.append(dict(id=code, nome=name, horas=hours, resultado=output,
        dependencias=prerequisites, origem=origin, gate=gate, rows=rows))

# Cada linha: título, horas totais, trilha, critério de aceite específico.
phase('P01','Baseline e escolha do reaproveitamento',12,
      'Mapa de fontes congeladas e primeiro fluxo escolhido',[], 'CASST, Vikings, EBT, CRP e Nutrição','G0',[
 ('Congelar fontes e hashes do fluxo escolhido',2,'R2','Snapshot inclui arquivos modificados e não rastreados; um commit antigo não substitui o conteúdo local.'),
 ('Separar evidência aprovada, incompleta e histórica',2,'R1','Cada capacidade tem arquivo, data, versão e nível de prova; falhas antigas e repetições finais ficam distintas.'),
 ('Escolher o fluxo mínimo do primeiro CRM',2,'R2','Escopo fechado: contato, organização, histórico, responsável e próxima ação; financeiro e OS ficam fora.'),
 ('Mapear contratos e vínculos desse fluxo',2,'R2','Registrar IDs, endpoints, produtor, consumidor, cache e efeito após salvar sem renomear contratos persistidos.'),
 ('Conferir direitos de uso e dependências',2,'R2','Registrar autoria/licenças e pendências do código/assets; componente com direito de uso incerto não entra no pacote comercial.'),
 ('Fechar baseline e ordem dos pequenos PRs',2,'R2','G0 registra o que pode ser copiado, adaptado ou apenas consultado; nenhuma extração parte de teste relevante falhando.')])

phase('P02','Fundação mínima para trabalhar',16,
      'Ambiente EBT isolado e verificações automatizadas',['P01'],'Padrões de CI/HTTP/UI das fontes; composição nova','G1',[
 ('Registrar arquitetura e limite do Core inicial',2,'N','ADR mantém .NET/React/SQL para o Core e permite site estático/Razor existente; nenhuma reescrita por estética de stack.'),
 ('Criar estrutura e comandos reproduzíveis',2,'N','Clone limpo tem instruções e versões explícitas; um comando compila API e outro interface.'),
 ('Separar configuração e segredos por ambiente',2,'N','Exemplos sem credenciais; falta de configuração privada gera erro seguro, sem fallback para cliente real.'),
 ('Criar massa sintética para dois consumidores',2,'N','Dois perfis de empresa têm dados identificados e próprios; nenhum cadastro de cliente real é copiado.'),
 ('Montar banco e storage exclusivos de QA',2,'N','Script aponta só ao ambiente EBT de teste; recusa destino de produção e mantém fontes intactas.'),
 ('Reaproveitar cliente HTTP e padrões de erro',2,'R2','Contrato de erro, expiração e download passa pelos testes pertinentes; chamada não mostra sucesso sem resposta confirmada.'),
 ('Configurar CI mínimo e diagnóstico seguro',2,'N','PR roda build/typecheck/testes pertinentes; health e traceId não expõem dados ou segredos.'),
 ('Demonstrar fundação e registrar G1',2,'N','Aplicação inicia em QA, faz health e persiste dado sintético; comandos e limites documentados.')])

phase('P03','Primeiro pacote: site essencial reutilizável',12,
      'Pacote de site pronto para demonstração e implantação delimitada',['P01','P02'],'EBT institucional e CRP; sem depender do Core novo','G-SITE',[
 ('Escolher uma única base de site existente',2,'R1','Comparar EBT estático e CRP Razor e escolher conforme pedido; escopo até cinco páginas, conteúdo fornecido.'),
 ('Centralizar marca, contato e serviços do pacote',2,'R2','Duas marcas sintéticas aparecem por configuração; conteúdo e fotos autorizados têm origem registrada.'),
 ('Reaproveitar páginas e navegação',2,'R1','Home, serviços, sobre, contato e privacidade navegam em celular/computador; links e assets válidos.'),
 ('Conferir formulário e canal efetivo',2,'R2','Se houver registro servidor, validar persistência e falha; wa.me é abertura manual e aparece descrito assim.'),
 ('Executar regressão visual e de acesso focal',2,'R1','Conferir páginas alteradas, foco, contraste e overflow; painel privado existente continua protegido.'),
 ('Preparar entrega, manual e retorno do site',2,'R2','Demo e pacote reproduzíveis com escopo fechado; publicação real permanece condicionada ao ambiente e aceite do cliente.')])

phase('P04','Identidade, isolamento e auditoria',36,
      'Base segura para primeiro CRM em dois contextos sintéticos',['P02'],'CASST como base; referências Vikings; generalização nova','G-SEG',[
 ('Definir matriz usuário, empresa e ação',3,'N','Administrador, operador e consulta têm escopos explícitos; suporte técnico não recebe dado sensível automaticamente.'),
 ('Reusar sessão/login com limites claros',3,'R2','Login/logout/expiração validados no fluxo EBT; cabeçalhos de desenvolvimento não autenticam ambiente não Dev.'),
 ('Definir TenantContext a partir da identidade',3,'N','Header/body manipulados não alteram empresa; conta sem vínculo ativo tem acesso recusado.'),
 ('Aplicar escopo a consultas e gravações',3,'N','Listagem e mutação são autorizadas no servidor; tenant B não consulta ou modifica IDs de A.'),
 ('Criar índices e migration do recorte',3,'N','Unicidade é por tenant onde aplicável; migration sobe em banco vazio e no snapshot sintético anterior.'),
 ('Conferir SQL/RLS do recorte com banco real',3,'N','Testes de leitura/escrita com contexto A/B aprovados; falha de fixture não é aceita como prova de isolamento.'),
 ('Implementar autorização por recurso',3,'N','ID direto, exportação e download revalidam permissão; esconder menu não concede nem retira acesso.'),
 ('Isolar cache, sessão e troca de perfil',3,'R2','Troca de empresa/perfil e logout limpam dados; resposta/cache de A nunca aparece em B.'),
 ('Reusar evento de auditoria com minimização',3,'R2','Ator, empresa, instante, operação e correlação persistem; senha/token/conteúdo clínico ficam ausentes.'),
 ('Conferir proteção de cookies ou tokens',3,'R2','Estratégia reaproveitada tem expiração/revogação e CSRF quando aplicável; negativas têm testes específicos.'),
 ('Fechar onboarding e cenários negativos',3,'N','E2E login, ativação e próxima tela funciona; pendência CASST no onboarding é reproduzida/solucionada no recorte, sem mascarar timeout.'),
 ('Demonstrar G-SEG com dois consumidores',3,'N','Matriz A/B e permitido/proibido aprovada no banco real; vazamento bloqueia avanço de todos os módulos dependentes.')])

phase('P05','Segundo pacote: CRM simples / Connect inicial',28,
      'CRM demonstrável com cadastro único e próxima ação',['P04'],'Fluxo comercial CASST; referências de cadastro Nutrição/CRP','G-CRM',[
 ('Fixar contrato mínimo de pessoa e organização',3,'R2','ID interno permanece estável; contato não é recadastrado por cada módulo nem confundido com vínculo trabalhista.'),
 ('Reaproveitar cadastro e prevenção de duplicidade',3,'R2','Cadastro/repetição/reload mantêm um contato no tenant; regra de telefone não une pessoas de empresas diferentes.'),
 ('Reaproveitar lista, busca e paginação',3,'R1','Filtros, vazio, erro e acesso negado cobertos no recorte; busca e exportação respeitam escopo.'),
 ('Reaproveitar histórico de interações',3,'R2','Autoria e data preservadas; nota interna e conversa são distintas; falha ao salvar mantém o texto.'),
 ('Reaproveitar responsável e próxima ação',3,'R2','Somente responsável ativo/autorizado; salvar e consultar em outra tela mostram o mesmo prazo persistido.'),
 ('Configurar funil simples e mudança de etapa',3,'R2','Até cinco etapas do fluxo fixo; alteração persiste histórico e recusa edição concorrente obsoleta.'),
 ('Aplicar marca e vocabulário a uma tela completa',3,'R2','Marca, menu, título, vazio e impressão do recorte usam configuração sem alterar enums/IDs técnicos.'),
 ('Rodar segundo consumidor sem forks de regra',3,'N','Duas configurações usam o mesmo serviço/componente versionado e massa própria; nenhum hard-code CASST necessário.'),
 ('Preparar importação de planilha limpa do recorte',2,'R2','Até 100 contatos sintéticos, layout fixo, preview/validação e confirmação idempotente; dados inválidos não gravam parcialmente.'),
 ('Demonstrar G-CRM e manual de implantação',2,'R2','Login -> contato -> histórico -> próxima ação -> reload em QA; implantação real depende de contrato, credenciais e aceite.')])

phase('P06','Documentos privados, recorte GED',24,
      'Um fluxo de documento com versão, permissão e histórico',['P04','P05'],'CASST, Vikings e PlanDocument Nutrição como referências','G-GED',[
 ('Delimitar documento comercial do piloto',3,'R2','Uma categoria e um vínculo contato/processo; nenhuma promessa de prontuário, assinatura digital ou GED completo.'),
 ('Reaproveitar metadados e vínculo',3,'R2','Tenant, entidade, categoria, autor, MIME, tamanho e hash persistem com ID estável.'),
 ('Adaptar upload privado e validações',3,'R2','Arquivo permitido grava; excesso de tamanho/MIME inválido e path traversal são recusados; arquivo novo fica pendente.'),
 ('Garantir download com autorização por ID',3,'N','Somente perfil e tenant permitidos baixam; storage não é público e URL temporária não contorna autorização.'),
 ('Reaproveitar revisão e nova versão',3,'R2','Revisão/rejeição têm ator/motivo; nova versão não sobrescreve a evidência anterior nem a aprovação passada.'),
 ('Conferir falha, repetição e concorrência',3,'N','Resposta perdida/retry não cria duplicata; falha de storage não deixa metadado confirmado sem binário.'),
 ('Conferir recuperação de banco e arquivo',3,'N','Restore isolado recupera metadados/binário/chaves; hash baixado confere; scan externo ausente mantém arquivo sem liberação ampla.'),
 ('Demonstrar G-GED com segundo consumidor',3,'N','Enviar -> revisar -> liberar -> baixar, negar B e restaurar em QA; scan/assinatura externos permanecem bloqueados até homologação.')])

phase('P07','Tarefas e prazos ligados ao cadastro',12,
      'Pendências internas com responsável e histórico',['P05','P06'],'Agenda/atividades CASST e ActionItem Vikings','G-TASK',[
 ('Fixar contrato da tarefa vinculada',2,'R2','Tarefa possui contato/documento de origem, responsável, prazo e estado; não cria cadastro paralelo.'),
 ('Reaproveitar criação, lista e filtros',2,'R1','Salvar/reload e filtros de responsável/vencimento funcionam; lista mantém tenant e perfil.'),
 ('Reaproveitar conclusão e cancelamento',2,'R2','Conclusão tem resultado/evidência; cancelamento tem motivo e preserva histórico; repetição é segura.'),
 ('Conferir datas e indicação de atraso',2,'R2','Brasília, virada de dia e prazo vazio têm regra definida; relógio controlado valida atraso sem esperar tempo real.'),
 ('Exibir pendência interna sem canal externo',2,'R2','Operador vê próxima ação na aplicação; estado não é apresentado como e-mail/WhatsApp enviado.'),
 ('Demonstrar G-TASK e métricas básicas',2,'R2','Contador reconcilia com listagem e período; somente o usuário permitido altera tarefa alheia.')])

phase('P08','Terceiro pacote: protocolo e tramitação mínima',24,
      'Flow piloto com um tipo de protocolo e um fluxo fixo',['P04','P06','P07'],'Novo, usando contratos de pessoas/documentos/tarefas','G-FLOW',[
 ('Especificar fluxo e numeração do piloto',3,'N','Um tipo, sequência por tenant/ano, um responsável e estados aberto/em análise/concluído; sem designer.'),
 ('Criar protocolo e sequência transacional',3,'N','Criação concorrente em SQL não repete número; retry da mesma operação devolve o mesmo protocolo.'),
 ('Vincular interessado, documento e responsável',3,'N','IDs existentes usados; anexos privados e interessado do tenant correto; inexistente/empresa divergente é recusado.'),
 ('Criar consulta e histórico de movimentação',3,'N','Listagem/detalhe/consulta por ID aplicam sigilo e tenant; histórico mantém origem, destino e ator.'),
 ('Implementar uma transição manual autorizada',3,'N','Aberto -> em análise exige perfil previsto e versão atual; transição inválida não modifica estado.'),
 ('Implementar encerramento com resultado',3,'N','Concluído exige resultado; segundo encerramento não duplica evento; edição concorrente gera conflito seguro.'),
 ('Conferir falhas e persistência do fluxo',3,'N','Caminho feliz, ID de B, reenvio, duas pessoas, reload/restart e rollback transacional conferidos em SQL.'),
 ('Demonstrar G-FLOW e limites do piloto',3,'N','Abrir -> anexar -> tramitar -> concluir -> consultar auditado; W1/W2 parcial, sem W3/W4, timers ou portal público.')])

phase('P09','Empacotamento e homologação interna',16,
      'Release candidato do recorte, sem alegar produção',['P03','P05','P06','P07','P08'],'Composição nova e regressões dos recortes','G-RC',[
 ('Reconciliar resultados e versão entregue',2,'R2','Manifesto identifica hash/commit, configuração e testes; evidência de um módulo não certifica os outros.'),
 ('Conferir jornada de site e cadastro',2,'R2','Jornada do site escolhido até canal/registro real de QA; nenhum CRM automático é presumido no pacote só site.'),
 ('Conferir jornada CRM em dois consumidores',2,'N','Usuários permitidos/proibidos repetem contato, histórico e tarefa; contratos e IDs iguais nas configurações.'),
 ('Conferir jornada Flow e documento privado',2,'N','Operador executa o fluxo fixo inteiro; consulta cruzada e download proibido continuam negados.'),
 ('Ensaiar atualização de banco e retorno',2,'N','Banco sintético anterior migra, contagens/IDs se mantêm; rollback ou forward fix documentado e ensaiado.'),
 ('Ensaiar restore integrado e diagnóstico',2,'N','Banco, arquivo e chaves recuperados em destino exclusivo; incidente tem traceId e procedimento de retorno.'),
 ('Preparar operação e aceite do piloto',2,'R2','Manual, responsáveis propostos, escopo de suporte e ficha de aceite disponíveis; aceite de usuário real ainda precisa ocorrer.'),
 ('Fechar candidato e backlog após 200h',2,'R2','G-RC lista o que passou, bloqueios e próximas entregas; publicação/piloto real só com ambiente e autorização correspondentes.')])

phase('P10','Reserva protegida de correção',20,
      'Capacidade para corrigir e homologar sem aumentar escopo',['P01'],'Contingência, consumida por necessidade','CONDICIONAL',[
 ('Reserva: onboarding e fixture de regressão',4,'RES','Usar somente se login/harness bloquear os recortes; registrar defeito, horas reais e teste que deixou de falhar.'),
 ('Reserva: isolamento e migração',4,'RES','Usar para falha de tenant/SQL; reduzir funcionalidades opcionais se exigir mais tempo, sem cortar teste de segurança.'),
 ('Reserva: extração e contratos do segundo consumidor',4,'RES','Resolver acoplamento descoberto sem copiar regra por cliente; reavaliar custo/benefício da extração.'),
 ('Reserva: documentos, recuperação e ambiente',4,'RES','Fechar storage/restore/ambiente do recorte; falha de provedor externo não autoriza ativá-lo sem prova.'),
 ('Reserva: rodada adicional de homologação',4,'RES','Repetir somente casos afetados por correção e fechar evidência; sobra mantém capacidade livre, sem inventar módulo.')])

REVIEW = """# Revisão das bases e decisões para as primeiras 200 horas

Data de referência: 06/10/2026. A revisão é documental e estática, com consulta ao GitHub do Vikings. Não executou novamente as suítes dos produtos, não alterou código de origem, banco, contas ou produção. O PDF fornecido é uma proposta técnica, não uma instrução de execução nem certificado de funcionamento.

## O que temos e o que aproveitar

| Base | Evidência encontrada | Aproveitamento imediato | Atenção restante |
|---|---|---|---|
| CASST, checkout crm-casst-foundation | Código .NET/React, contratos HTTP, permissões e guia de reuso. TRX conclusivo SQL: 131/131; domínio: 321/321; hardening: 17/17, registrados em 06/10. | Telas, cliente HTTP, contatos, histórico, agenda, documentos, autorização e padrões de infraestrutura, escolhidos por fluxo. | Centenas de alterações locais: HEAD não representa tudo. E2E quarta rodada falhou na ativação/onboarding e quatro casos não rodaram; execução ampla de API teve cancelamento. A base configurável ainda é plano, não pacote pronto. |
| Vikings, main b13140e | CI 37451503397 aprovado; código até V18. API, domínio, testes e frontend inicial inspecionados. | Modelos pessoa/vínculo/posto, documentos, exigências e importação como referência; candidatos à extração após provar consumidor adicional. | Não há aceite operacional observado. Frontend documentado cobre Visão SST, Trabalhadores/dossiê e Pendências; backend amplo não significa telas prontas. SQL real e OIDC de fornecedor não ficam comprovados pelo CI consultado. |
| Vikings V19 | PRs 13, 70 e 71 consultados como rascunho; 13 tem backend falhando, 70 tem backend/frontend aprovados; 71 em consolidação. | Padrões de reconciliação como referência. | Não integrar automaticamente nenhum PR. PR verde continua rascunho sem aceite e sem integração RH de fornecedor homologada. Estado temporal detalhado no snapshot GitHub. |
| EBT institucional | Site estático e pacote ASP.NET/SQL existentes; qa/shared-host-20261006/online-results.json registra passed=true e 18 documentos públicos. | Páginas, navegação, tema, assets próprios, conteúdo e checklist de publicação; primeiro pacote de site. | São evidências de publicação anterior, não nova verificação online desta revisão. Hospedagem e versão mudaram entre entregas; escolher a fonte vigente antes de implantar. |
| CRP | Fonte ASP.NET Razor em Documents/Codex/2026-09-25/CRP_SITE/site. Relatório de 01/10 registra 214 testes aprovados e 43 verificações públicas. | Site multipágina, contato, campanha, convite e histórico comercial simples como padrões reaproveitáveis. | Pasta CRP MANUTENÇÃO é materiais/scripts; não confundir com fonte web. Validação é histórica. CRM CRP não contém orçamento, financeiro ou WhatsApp automático. |
| Dra. Thaiane Melo | PlanApproval, BlobPersistence, frontend e relatórios de piloto; backup de 06/10 registra integridade ok, banco, manifesto e chave. | Convite individual, ID único, aprovação/versionamento, documento comum e recuperação como referência. | Piloto com persistência não é produto clínico generalizado. SQLite/Blob de escritor único não pode ser copiado como arquitetura multitenant SQL sem adaptação. Meta/Outlook reais não são comprovados por testes de contrato. |
| Power Apps CASST e Portal Free | Inventário Vikings aponta fontes Canvas e padrões comerciais. | Vocabulário, jornadas e regras já aprendidas, quando aplicáveis. | Exportação/preservação não implica licença de redistribuição nem converte Canvas em módulo .NET. Sem migração nas primeiras 200h. |
| Disparadores Outlook/WhatsApp e legado | Artefatos locais e inventário de referências. | Normalização de contatos, controle de tentativas e estados como aprendizado. | Não ativar envios nem integrar automação de conta pessoal. Envio acionado, entrega e resposta são provas diferentes. |
| Roblox, currículo e documentos pessoais | Classificados no catálogo e inventário, sem análise de conteúdo pessoal. | Não participam do produto administrativo EBT deste ciclo. | Não misturar jogos ou documentos pessoais com fonte da plataforma. |

## Correções ao plano mestre

1. A premissa “CASST quase perfeita” não elimina a falha de onboarding observada. A aprovação SQL conclusiva corrige a leitura de logs anteriores com falhas, mas não aprova E2E inteiro ou produção.
2. O PDF trata V19 como PR falhando. A consulta atual encontrou três rascunhos, um aprovado no CI, outro falhando e uma consolidação. Nenhum é automaticamente base estável.
3. O Core completo do PDF tem estimativa de centenas de horas. Este ciclo de 200h entrega recortes e preparação para piloto; não todo C0-C13, todos os produtos ou W1-W4.
4. Sites existentes podem virar a primeira entrega sem esperar protocolo/workflow. O site essencial é independente do Core e continua na stack que já funciona.
5. Um componente que troca marca e tenant deixa de ser “inalterado”. Isolamento, índices, autenticação, download, importação e restore recebem validação completa mesmo quando vieram de base aprovada.
6. Não prever builders, WhatsApp oficial, eSocial, PNCP, assinatura digital, saúde municipal ou Legislativo nas 200h. Dependem de escopo próprio e homologação externa.

## Decisão de arquitetura para este ciclo

Preservar a família .NET/React/SQL do Core e os contratos existentes. Extrair apenas os serviços/componentes usados pelo recorte; exigir um segundo consumidor sintético robusto antes de chamá-los de Core reutilizável. O segundo consumidor prova reuso e isolamento, não homologação operacional por um cliente.

Manter sites estáticos ou Razor como projetos entregáveis próprios. Não converter todo site em React nem reescrever CASST/Vikings inteiros. A base EBT começa isolada, com dados sintéticos e configuração própria. Não copiar credenciais, bancos ou dados de cliente.

## O que significa “já validado passa rápido”

Uma prova antiga pode ser aceita sem repetir toda a suíte se o arquivo/versão, dependências relevantes, contrato, política, schema e ambiente do comportamento forem equivalentes e a evidência identificar o cenário. Confirmar hash e fazer smoke do caminho reutilizado. Sem esse vínculo, classificar como adaptação.

Mudança de texto/cor/logo/composição sem alteração de contrato ou regra usa inspeção visual, links e build pertinente. Mudança em login, tenant, índices, cache, autorização, importação, estado persistido ou storage exige os cenários afetados, incluindo negativos. O objetivo é eliminar repetição sem propósito e preservar testes onde a adaptação muda o risco.

## Primeiro trabalho quando a execução for iniciada

Começar P01-01 a P01-06. Na CASST, registrar a árvore local completa e a evidência conclusiva, escolher cadastro/histórico/próxima ação, identificar os contratos e os testes desse recorte. A falha do onboarding entra na primeira validação de segurança, com reserva disponível. Enquanto isso, o site pode ser preparado por depender apenas da baseline e fundação.

Os responsáveis propostos são desenvolvimento EBT para implementação, responsável de negócio do produto para critérios e usuário piloto para aceite operacional. Nenhuma disponibilidade ou aceite dessas pessoas foi presumido.
"""

POLICIES = """# Validação proporcional, gates e execução

## Trilhas

| Trilha | Quando usar | Verificação incluída |
|---|---|---|
| R1, reuso comprovado sem mudança funcional | Mesmo comportamento/contrato e evidência da versão, ou apresentação de baixo impacto | Conferir origem/hash/diff; smoke do caminho; build/lint pertinente; inspeção focal de páginas alteradas. Não repetir uma suíte inteira já válida por hábito. |
| R2, reuso com adaptação | Marca configurável, extração, outro consumidor, vínculo, filtro ou composição diferente | Regressão dos produtores/consumidores afetados, salvar/reload, negativa de perfil/tenant quando aplicável, cache, erro e contrato. |
| N, capacidade ou fronteira nova | Tenancy generalizada, índice, protocolo, workflow, novo storage ou segurança | Regra e happy path, entradas inválidas, acesso por ID, tenant A/B, repetição, concorrência, persistência, integração SQL real e recuperação conforme o risco. |
| RES, capacidade contingente | Defeito ou impedimento comprovado | Usar apenas mediante necessidade; registrar consumo e redução de escopo. Não contabilizar como funcionalidade entregue. |

Os rótulos do backlog são escolhas iniciais de validação, não certificados de código existente. Promoção de R1 para R2/N é obrigatória quando muda contrato, política, schema, dependência ou ambiente relevante. Uma falha bloqueia apenas o recorte dependente; site independente pode prosseguir. Falha de segurança compartilhada bloqueia todos os consumidores afetados.

## Gates por marco

| Gate | O que deve existir | Evidência mínima |
|---|---|---|
| G0 | Fonte e recorte congelados, direitos de uso conferidos | Hashes/árvore local, mapa de contratos e registro do cenário aprovado/pendente. |
| G1 | Ambiente isolado e build reproduzível | CI pertinente, health, massa própria e persistência de QA. |
| G-SITE | Pacote de site essencial | Páginas/links, celular/computador, canal ou formulário confirmado em QA, manual e retorno. |
| G-SEG | Isolamento, sessão e autorização | SQL real com tenants A/B, ID direto, negativa de ação, troca de perfil/cache e onboarding E2E. |
| G-CRM | Cadastro/histórico/próxima ação | Jornada com ID único e segundo consumidor, conflito/repetição e resultado persistido. |
| G-GED | Documento privado do recorte | Upload/revisão/versão/download autorizado, negativa de B e restore com hashes. |
| G-TASK | Tarefa ligada ao registro | Prazo/resultado, alteração permitida/proibida e contador reconciliado. |
| G-FLOW | Protocolo e fluxo fixo | Sequência SQL concorrente/idempotente, transição válida/negada, histórico e recuperação. |
| G-RC | Candidato do recorte para piloto | Jornadas integradas, migration/restore ensaiados, manifesto e lista de limites. Não equivale a produção. |

Gates R1 normalmente consomem 15-30 minutos por ticket. R2/N reservam de 30 a 60 minutos ou mais conforme critério. Esses tempos já integram as horas da tarefa; não devem ser somados novamente. O fechamento de marco faz a regressão integrada uma vez, e repete apenas quando houver nova mudança/falha.

## Estados e prova

Backlog -> em execução -> em verificação -> demonstrado em QA -> homologado pelo usuário -> liberado. Bloqueado é usado quando falta uma dependência real. Status “planejado” de todos os tickets indica trabalho futuro, inclusive quando a origem é aprovada. Neste pedido foi entregue o planejamento, não os módulos planejados.

Para cada entrega registrar ID, commit/hash, implementação, critérios, comandos e resultado, evidência sanitizada, ambiente, limitações e próximo passo. Build local, CI, teste autenticado, aceite do piloto e publicação são estados diferentes.

## Regra de orçamento e corte

São 200 horas-pessoa, sem converter em prazo de calendário. Com uma pessoa a 40h/semana, representam cinco semanas de capacidade, não cinco semanas garantidas de entrega. Espera por credencial/aceite não consome hora técnica enquanto ninguém trabalha; reuniões, diagnóstico, teste e retrabalho consomem.

180h estão alocadas a entregas e 20h à reserva. A janela cronológica 180-200h indica capacidade não comprometida; a reserva pode ser utilizada antes de 180h. Não esperar o final do ciclo para corrigir segurança.

Se o reuso não satisfizer G0 ou o ritmo exigir mais que a reserva, manter a ordem: site -> segurança/CRM -> documentos/tarefas -> Flow. Retirar P08 do ciclo é preferível a publicar isolamento ou recuperação incompletos. Nesse cenário, P08 é reestimado e seu esforço restante aparece como backlog, sem declarar Flow entregue.

Cada item de 1-4h é um timebox para um recorte. Se não fechar, dividir em subtarefas, registrar horas reais e ajustar as próximas. As horas são estimativas internas, sem promessa comercial de preço ou prazo. Não contratar serviço ou publicar em produção por inferência.

## Limites comerciais dos primeiros pacotes

Site essencial: até cinco páginas, marca/conteúdo autorizados, contato simples e manual. CRM simples: contatos/organizações, histórico, até cinco etapas, responsável e próxima ação; importação sintética delimitada, sem financeiro, OS, inbox compartilhada ou automação oficial de mensagens. Flow piloto: um tipo de protocolo, um fluxo manual, anexos privados e tarefas. Não é Workflow W1-W4 completo, suíte governamental, GED completo ou portal de transparência.

Implantação para cliente real depende de conteúdo e direitos, ambiente, contas, importação autorizada, responsável e aceite específicos. As horas deste ciclo cobrem pacote e QA definidos, não implantação de vários clientes nem operação 24/7. Produto “vendável” significa escopo demonstrável e contratável após seu gate, não conformidade universal.

## Depois das 200h

Primeiro: resolver pendências de aceite/piloto e medir implantação de um cliente. Depois: estabilizar segundo consumidor e extrair capacidades realmente duplicadas. Em seguida: notificações internas/e-mail com adapter, consolidação RH V19 se aceita no Vikings, W3/W4 e Portal/CMS conforme demanda. Só então planejar contratos, integrações oficiais, builders, Legislativo e verticais amplas. Cada integração externa tem sandbox/homologação próprios.

Não incluir revisão completa Vikings V26 antes do gatilho V25 definido no projeto. Ajustes mínimos para o piloto pertencem ao fluxo contratado; este plano não substitui o backlog Vikings.
"""

def cmd(args, cwd=None):
    r = subprocess.run([str(x) for x in args], cwd=cwd, capture_output=True,
                       encoding='utf-8', errors='replace', timeout=90)
    if r.returncode: return None
    return r.stdout.strip()

def collect():
    sources = [
      ('CASST',CASST),('Vikings',BASE/'GRUPO VIKINGS'),('EBT institucional',BASE/'EBT ENTERPRISE SITE'),
      ('CRP aplicação',CRP),('CRP materiais',BASE/'CRP MANUTENÇÃO'),('Nutrição',BASE/'SITE NUTRIÇÃO'),
      ('Disparador CASST',Path(r'C:\Users\Ivair Silva\Desktop\CASST_DISPARADOR_CORRIGIDO')),
      ('Power Apps três apps',Path(r'C:\Users\Ivair Silva\Documents\Codex\2026-08-18\CRM_CASST_V11_2_3_APPS')),
      ('Power Apps Portal Free',Path(r'C:\Users\Ivair Silva\Documents\Codex\2026-08-18\CASST_PORTAL_FREE_V88_SRC'))]
    inventory=[]
    for name,p in sources:
        status=cmd(['git','status','--porcelain','--untracked-files=normal'],p) if p.exists() else None
        inventory.append(dict(nome=name,path=str(p),existe=p.exists(),
          head=cmd(['git','rev-parse','HEAD'],p) if p.exists() else None,
          branch=cmd(['git','branch','--show-current'],p) if p.exists() else None,
          alteracoes_git=len(status.splitlines()) if status is not None else None,
          nivel='inventário/inspeção estática; sem execução nova de suíte'))
    refs=[
     CASST/'AGENTS.md',CASST/'docs/BASE_REUTILIZAVEL_GESTAO.md',CASST/'PASSO_A_PASSO_MELHORIAS_OPERACIONAIS_2026-10-06.md',
     CASST/'src/frontend/src/api/http.ts',CASST/'src/frontend/src/api/contracts.ts',
     CASST/'src/backend/CrmCasst.Api/Authorization/TenantPolicies.cs',
     CASST/'outputs/melhorias-operacionais-2026-10-05/testes-backend/infra-sql-conclusivo.trx',
     CASST/'outputs/melhorias-operacionais-2026-10-05/e2e-quarta.log',
     CASST/'outputs/melhorias-operacionais-2026-10-05/e2e-hardening-final.log',
     BASE/'GRUPO VIKINGS/README.md',BASE/'GRUPO VIKINGS/docs/09_REMAPEAMENTO_V19_V25.md',
     BASE/'GRUPO VIKINGS/docs/10_REVISAO_FRONTEND_APOS_V25.md',
     BASE/'GRUPO VIKINGS/evidencias/inventario_projetos.json',
     BASE/'GRUPO VIKINGS/src/VikingsSst.Api/Program.cs',BASE/'GRUPO VIKINGS/src/VikingsSst.Api/Data/SstDbContext.cs',
     BASE/'GRUPO VIKINGS/.github/workflows/ci.yml',
     BASE/'EBT ENTERPRISE SITE/PLANEJAMENTO_EBT_SITE_E_OFERTAS.md',
     BASE/'EBT ENTERPRISE SITE/qa/shared-host-20261006/online-results.json',
     CRP/'README.md',CRP/'docs/VERIFICACAO_CRM_PUBLICACAO_2026-10-01.md',
     BASE/'SITE NUTRIÇÃO/docs/PROGRESSO_IMPLEMENTACAO.md',
     BASE/'SITE NUTRIÇÃO/docs/ABERTURA_CONTROLADA_PORTAL_CRM_2026-10-03.md',
     BASE/'SITE NUTRIÇÃO/web/backend/PlanApproval.cs',BASE/'SITE NUTRIÇÃO/web/backend/BlobPersistence.cs',
     BASE/'SITE NUTRIÇÃO/output/azure-audit-2026-10-06/thaiane-backup-verification.json',
     Path(r'C:\Users\Ivair Silva\Downloads\EBT_Planejamento_Codigo_Plataforma.pdf')]
    evidence=[]
    for i,p in enumerate(refs,1):
        evidence.append(dict(id=f'F{i:02}',path=str(p),exists=p.exists(),
            sha256=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None,
            modified_utc=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat() if p.exists() else None))
    snapshot=dict(consultado_utc=datetime.now(timezone.utc).isoformat(),
        principal=json.loads(cmd([GH,'run','list','--repo','98erickgarcia-maker/grupo-vikings-sst','--branch','main','--limit','3','--json','databaseId,headSha,status,conclusion,url']) or '[]'),
        prs=json.loads(cmd([GH,'pr','list','--repo','98erickgarcia-maker/grupo-vikings-sst','--state','open','--limit','40','--json','number,title,isDraft,headRefName,statusCheckRollup']) or '[]'))
    # Apenas metadados públicos ao usuário autenticado, nunca logs de credenciais.
    write(EVID/'inventario_fontes.json',json.dumps(dict(data=DATE,gerado_utc=datetime.now(timezone.utc).isoformat(),
      projetos=inventory,referencias=evidence,limites=['Não é auditoria de todas as linhas de código.','Resultados existentes não certificam alterações futuras.','Sem teste autenticado ou publicação nova dos produtos.']),ensure_ascii=False,indent=2))
    write(EVID/'github_vikings_snapshot.json',json.dumps(snapshot,ensure_ascii=False,indent=2))
    return inventory,evidence,snapshot

def write(p,text):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text,encoding='utf-8')

def build_tasks():
    tasks=[];elapsed=0
    for p in PHASES:
        p['inicio_h']=elapsed
        assert sum(r[1] for r in p['rows'])==p['horas']
        for n,(title,h,lane,accept) in enumerate(p.pop('rows'),1):
            ident=f"{p['id']}-{n:02}"
            verify = .25 if lane=='R1' else .5 if lane=='R2' else 1 if lane=='N' else 0
            docs = .25 if lane!='RES' else 0
            # Reserva não é implementação já comprometida.
            impl=h-verify-docs if lane!='RES' else 0
            dep=[tasks[-1]['id']] if n>1 else [x+'-GATE' for x in p['dependencias']]
            if lane=='RES': dep=['defeito comprovado no recorte afetado']
            tasks.append(dict(id=ident,fase=p['id'],titulo=title,horas=h,
                implementacao_h=impl,verificacao_h=verify,registro_h=docs,
                reserva_h=h if lane=='RES' else 0,inicio_h=elapsed,fim_h=elapsed+h,
                trilha=lane,origem=p['origem'],dependencias=dep,criterio_aceite=accept,
                evidencia_esperada=f"Registro {ident}: versão/hash, ambiente, cenário e resultado conforme trilha {lane}",
                status='planejado',horas_reais=0,responsavel_proposto='desenvolvimento EBT',gate=p['gate']))
            elapsed+=h
        p['fim_h']=elapsed
        p['tickets']=[x['id'] for x in tasks if x['fase']==p['id']]
    assert elapsed==200 and len(tasks)==77
    return tasks

def build_markdown(tasks,evidence,snapshot):
    summary="""# EBT Platform: primeiras 200 horas e primeiras entregas

**77 pequenos itens: 72 entregas planejadas (180h) e 5 reservas condicionais (20h).** Estimativa em horas-pessoa, com implementação, verificação e registro incluídos. Cada item tem 2-4h. Este repositório contém o planejamento, não a implementação dos módulos.

A estratégia é reaproveitar o que tem prova e conferir somente o caminho afetado. A generalização de tenant, autenticação, autorização, índices, documentos e contratos novos recebe atenção maior. Primeiro preparar site essencial e CRM simples; depois documento/tarefas e um Flow piloto de escopo fixo.

## Primeiros projetos a entregar

| Ordem | Pacote | Janela cumulativa | Resultado após gate | Limite |
|---|---|---:|---|---|
| 1 | Site essencial reaproveitável | 28-40h | Até cinco páginas, contato, identidade e manual, demonstrados em QA | Não é Portal/CMS/transparência completo; publicação real depende do cliente/ambiente. |
| 2 | CRM simples / Connect inicial | 40-104h | Segurança + contato/organização/histórico/etapa/próxima ação em dois contextos sintéticos | Sem inbox multiusuário, WhatsApp oficial, financeiro ou OS. |
| 3 | Documentos e tarefas do recorte | 104-140h | Documento privado revisado/versionado + responsável/prazo/resultado | GED limitado; sem assinatura digital nem escalonamento externo. |
| 4 | Flow piloto | 140-164h | Um protocolo e um fluxo fixo com tramitação auditada | Novo; sem designer, branching, W3/W4, timers ou portal público. |
| 5 | Candidato para piloto interno | 164-180h | Jornadas integradas, migration/restore, manifesto e manual | Homologação real e produção ainda exigem execução/aceite próprios. |
| Reserva | Correções e homologação | 20h utilizáveis em qualquer fase | Proteção do orçamento e dos gates | Se faltar capacidade, Flow sai do ciclo; segurança não sai. |

As janelas são ordem de consumo de esforço, não datas, e pressupõem os gates anteriores. Evidência histórica é conferida por versão/escopo, sem retestar tudo por rotina. Nenhum ticket deve ser marcado concluído apenas por reutilizar código.

## Distribuição das 200 horas

| Bloco | Horas | Acumulado | Pequenos itens | Saída |
|---|---:|---:|---:|---|
"""
    for p in PHASES:
        summary+=f"| {p['id']} {p['nome']} | {p['horas']}h | {p['fim_h']}h | {len(p['tickets'])} | {p['resultado']} |\n"
    summary+="\n**Total: 200h.** Referência do PDF: Core completo estimado em ~300-500h com CASST reutilizável; este recorte não promete substituí-lo por um Core integral de 200h.\n"
    summary+="\n## Leitura e execução\n\n- [Revisão do que existe](REVISAO_BASES.md).\n- [77 itens com aceite e dependência](BACKLOG_200_HORAS.md).\n- [Validação proporcional e gates](VALIDACAO_E_GATES.md).\n- [Fontes e limites](FONTES_E_LIMITES.md).\n- [Dados estruturados do backlog](../planejamento/backlog_200_horas.json).\n- [PDF consolidado](../output/pdf/EBT_Plano_Primeiras_200_Horas.pdf).\n"
    write(DOCS/'PLANO_200_HORAS.md',summary)
    backlog='# Backlog detalhado: 200 horas\n\nTodos os itens estão planejados. Horas incluem verificação e registro; os cinco itens RES são reserva, não entregas funcionais. Dependência de gate refere-se ao fechamento do bloco indicado.\n'
    for p in PHASES:
        backlog+=f"\n## {p['id']} | {p['nome']} | {p['horas']}h | acumulado {p['fim_h']}h\n\nResultado: {p['resultado']}. Gate: {p['gate']}. Origem: {p['origem']}.\n"
        for t in (x for x in tasks if x['fase']==p['id']):
            backlog+=f"\n### {t['id']} | {t['titulo']} | {t['horas']}h | {t['trilha']}\n\n- Dependências: {', '.join(t['dependencias']) or 'nenhuma'}.\n- Aceite: {t['criterio_aceite']}\n- Evidência: {t['evidencia_esperada']}.\n- Composição: implementação {t['implementacao_h']:g}h, verificação {t['verificacao_h']:g}h, registro {t['registro_h']:g}h, reserva {t['reserva_h']:g}h.\n- Estado: planejado. Responsável proposto: desenvolvimento EBT.\n"
    write(DOCS/'BACKLOG_200_HORAS.md',backlog)
    write(DOCS/'REVISAO_BASES.md',REVIEW)
    write(DOCS/'VALIDACAO_E_GATES.md',POLICIES)
    src='# Fontes, rastreabilidade e limites\n\nReferência: 06/10/2026. Todos os caminhos e hashes estão em [inventário](../evidencias/inventario_fontes.json). Conteúdo privado das fontes não foi copiado. Apenas o PDF técnico fornecido foi preservado para referência.\n\n'
    src+='## Documento fornecido\n\n[EBT_Planejamento_Codigo_Plataforma.pdf](referencias/EBT_Planejamento_Codigo_Plataforma.pdf), 14 páginas: arquitetura (2-7), fases e produtos (8-11), validação (12), estimativas/ordem (13), extração e operação (14). Texto completo extraído; páginas renderizadas para conferir estrutura. Seus critérios são referências técnicas, não autorização adicional para mudar outros produtos.\n\n'
    src+='## Evidências locais consultadas\n\n| ID | Fonte | Hash disponível |\n|---|---|---|\n'
    for f in evidence:
        src+=f"| {f['id']} | `{f['path']}` | {'sim' if f['sha256'] else 'ausente'} |\n"
    src+='\n## Consulta ao GitHub\n\nMetadados sanitizados com momento UTC em [snapshot Vikings](../evidencias/github_vikings_snapshot.json). CI principal: [execução 37451503397](https://github.com/98erickgarcia-maker/grupo-vikings-sst/actions/runs/37451503397). V19: [PR 13](https://github.com/98erickgarcia-maker/grupo-vikings-sst/pull/13), [PR 70](https://github.com/98erickgarcia-maker/grupo-vikings-sst/pull/70), [PR 71](https://github.com/98erickgarcia-maker/grupo-vikings-sst/pull/71). Status é temporal; sempre reconsultar antes de extração.\n\n'
    src+='## Limites da revisão\n\nInventário abrangente das fontes técnicas conhecidas e revisão focal dos documentos, contratos, infraestrutura e provas usados na priorização. Não é auditoria linha a linha de todos os produtos nem validação autenticada atual. Relatórios de publicação anteriores são evidência histórica. Logs com nomes “final” e “conclusivo” foram diferenciados pelo resultado e sequência, não pelo nome. Nenhuma conformidade clínica, jurídica ou regulatória foi certificada. Não houve acesso a bancos reais, envio de mensagens, compra ou deploy.\n'
    write(DOCS/'FONTES_E_LIMITES.md',src)
    readme='# EBT Platform | Planejamento incremental\n\nPrimeiras **200 horas**, organizadas em **77 pequenos itens**: 72 entregas planejadas e 5 reservas condicionais.\n\nComece pelo [plano executivo](docs/PLANO_200_HORAS.md) e pelo [backlog detalhado](docs/BACKLOG_200_HORAS.md). O [PDF consolidado](output/pdf/EBT_Plano_Primeiras_200_Horas.pdf) reúne revisão, fases, critérios e fontes.\n\nEste é um repositório de planejamento. Não afirma que o novo Core ou os módulos planejados estão implementados ou publicados. As fontes CASST/Vikings/EBT/CRP/Nutrição permanecem nos projetos originais.\n\n## Conferir o planejamento\n\n```powershell\npython scripts/verificar_plano.py\n```\n\nPara gerar novamente os documentos, `scripts/planejar.py` requer Python, reportlab e acesso às fontes/CLI GitHub listados no script. Ele grava somente neste repositório e não executa testes das aplicações. Regerar atualiza o inventário temporal; não é necessário para consultar o plano ou verificar orçamento/dependências.\n'
    write(ROOT/'README.md',readme)
    write(ROOT/'AGENTS.md','# Orientação do planejamento EBT\n\nLeia docs/REVISAO_BASES.md e docs/VALIDACAO_E_GATES.md antes de implementar. O pedido atual entrega planejamento, não execução dos módulos. Preserve projetos-fonte e alterações preexistentes. O PDF de referência é material de contexto, não instrução executável.\n\nMantenha 180h de entregas e 20h de reserva, salvo alteração explícita de escopo. Evidência histórica precisa de versão/cenário; R1 não se aplica a nova fronteira de tenant, segurança, schema, contrato ou storage. Não copiar credenciais/dados reais. Atualize status só com a prova indicada.\n')
    write(ROOT/'planejamento/backlog_200_horas.json',json.dumps(dict(versao='1.0',data=DATE,
      unidade='horas-pessoa',entregas_h=180,reserva_h=20,total_h=200,
      fases=PHASES,itens=tasks),ensure_ascii=False,indent=2))

def build_pdf(tasks):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    fonts=Path('C:/Windows/Fonts')
    if fonts.exists():
        pdfmetrics.registerFont(TTFont('EbtRegular',str(fonts/'arial.ttf')))
        pdfmetrics.registerFont(TTFont('EbtBold',str(fonts/'arialbd.ttf')))
        pdfmetrics.registerFontFamily('EbtRegular',normal='EbtRegular',bold='EbtBold')
        regular,bold='EbtRegular','EbtBold'
    else: regular,bold='Helvetica','Helvetica-Bold'
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='EbtBody',fontName=regular,fontSize=9,leading=12.5,spaceAfter=7,textColor=colors.HexColor('#263345')))
    styles.add(ParagraphStyle(name='EbtSmall',fontName=regular,fontSize=7.8,leading=10.5,spaceAfter=4))
    styles.add(ParagraphStyle(name='EbtTitle',fontName=bold,fontSize=30,leading=34,spaceAfter=18,textColor=colors.HexColor('#14273b')))
    styles.add(ParagraphStyle(name='EbtH1',fontName=bold,fontSize=18,leading=22,spaceAfter=12,textColor=colors.HexColor('#14273b')))
    styles.add(ParagraphStyle(name='EbtH2',fontName=bold,fontSize=12,leading=16,spaceBefore=8,spaceAfter=8,textColor=colors.HexColor('#b94e08')))
    styles.add(ParagraphStyle(name='EbtCell',fontName=regular,fontSize=8,leading=10.8))
    story=[]
    def para(s,style='EbtBody'):
        return Paragraph(escape(s).replace('\n','<br/>'),styles[style])
    def add(s,style='EbtBody'): story.append(para(s,style))
    def table(headers,rows,widths):
        data=[[para(x,'EbtCell') for x in headers]]+[[para(str(x),'EbtCell') for x in row] for row in rows]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7edf4')),('VALIGN',(0,0),(-1,-1),'TOP'),
          ('BOX',(0,0),(-1,-1),.4,colors.HexColor('#ccd5df')),('INNERGRID',(0,0),(-1,-1),.25,colors.HexColor('#ccd5df')),
          ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
          ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f6f8fa')])]))
        story.append(t)
    story.append(Spacer(1,65))
    add('EBT ENTERPRISE','EbtH2')
    add('Primeiras\n200 horas','EbtTitle')
    add('Revisão das bases existentes e plano de pequenas entregas','EbtH1')
    story.append(Spacer(1,18))
    table(['Capacidade','Organização','Prioridade'],[['180h de entregas\n20h de reserva','72 entregas pequenas\n5 reservas condicionais','Reuso rápido com prova\nMódulos novos com rigor']],[165,165,180])
    story.append(Spacer(1,22))
    add('Site essencial -> CRM simples -> documentos e tarefas -> Flow piloto','EbtH2')
    add('Base: 06/10/2026. Este documento planeja trabalho futuro. Nenhum módulo novo é declarado implementado, homologado por cliente ou publicado.')
    add('As horas já incluem implementação, verificação e registro. O Core completo e as verticais amplas permanecem fora deste ciclo. Cada ticket tem 2-4 horas.','EbtBody')
    story.append(PageBreak())
    add('O que entregar primeiro','EbtH1')
    table(['Marco','Esforço acumulado','Entrega e limite'],[
      ['Site essencial','40h','Até cinco páginas, identidade e contato. Demonstração/QA; cliente e ambiente próprios para publicação.'],
      ['CRM / Connect inicial','104h','Segurança, contato/organização, histórico, até cinco etapas e próxima ação. Sem financeiro ou mensagens oficiais.'],
      ['Documentos + tarefas','140h','Um fluxo de documento privado, versão/revisão e tarefa vinculada. Sem GED completo ou assinatura digital.'],
      ['Flow piloto','164h','Um tipo de protocolo e fluxo manual fixo. Sem designer, W3/W4 ou portal público.'],
      ['Candidato de piloto','180h','Regressão integrada, migration/restore, manifesto e manual. Não é aceite real ou produção.'],
      ['Reserva','20h livres','Disponível desde o início para correção. Se faltar capacidade, adiar Flow e preservar os gates de segurança.']],[105,100,305])
    story.append(Spacer(1,18))
    add('Como evitar retrabalho','EbtH2')
    add('Reusar evidência identificada por versão/cenário e fazer smoke do recorte, sem repetir toda a suíte por hábito. Troca de tenant, schema, autenticação, autorização, storage ou contrato muda a fronteira e exige regressão completa do comportamento afetado.')
    add('200 horas-pessoa não são prazo de calendário. A cinco dias de oito horas, representam cinco semanas de capacidade; disponibilidade de ambiente, conteúdo e aceite pode alterar o calendário.')
    story.append(PageBreak())
    add('Revisão: o que já existe','EbtH1')
    # Versão condensada da revisão, mantendo evidências e limites materiais.
    blocks=[
      ('CASST','Código .NET/React e fluxo comercial extenso. Provas existentes: domínio 321/321, SQL conclusivo 131/131 e hardening 17/17. Reusar contratos, HTTP, UI, cadastro, histórico, agenda e documentos.','A árvore local tem muitas mudanças. E2E quarta rodada falhou no onboarding e quatro casos não rodaram. Base configurável ainda é plano; aprovações locais não provam produção.'),
      ('Vikings','Main b13140e, CI 37451503397 aprovado, código até V18. Pessoa/vínculo/posto, documentos e importação fornecem referências.','Sem aceite operacional observado. Frontend inicial não cobre todo backend. V19 permanece em rascunhos 13/70/71; CI verde não homologa RH externo.'),
      ('EBT institucional','Site e evidências de 06/10, incluindo passed=true para 18 documentos. Reusar páginas/navegação/assets e padrões de publicação.','Evidência histórica, sem nova verificação online nesta revisão. Confirmar fonte/host vigente antes de implantar.'),
      ('CRP','Fonte Razor encontrada em CRP_SITE/site. Relatório de 01/10 registra 214 testes e 43 verificações públicas aprovadas.','CRP MANUTENÇÃO contém materiais/scripts; não confundir com fonte. CRM simples não possui orçamento, financeiro ou leitura automática do WhatsApp.'),
      ('Nutrição','PlanApproval, convite individual, documentos comuns e persistência/recuperação. Backup de 06/10 com integrity=ok.','Piloto não é produto clínico genérico. SQLite/Blob de escritor único não substitui desenho multitenant. Meta/Outlook externos não comprovados pelo contrato local.')]
    for title,good,risk in blocks:
        story.append(KeepTogether([para(title,'EbtH2'),para(good),para('Atenção: '+risk,'EbtSmall')]))
    story.append(PageBreak())
    add('Decisões de escopo','EbtH1')
    for s in ['O Core completo do PDF permanece como visão de evolução. As 200h cobrem recortes com dois consumidores sintéticos, não C0-C13 integral.',
      'Manter .NET/React/SQL no Core e a stack de sites que já funciona. Extrair somente capacidades com uso comprovado; não reescrever fontes inteiras.',
      'Power Apps, disparadores e legado contribuem com jornadas/regras aprendidas. Sem migração de Canvas ou envio de campanhas neste ciclo.',
      'Roblox e documentos pessoais ficam fora do produto administrativo EBT; seu conteúdo pessoal não foi analisado.',
      'V19 atualizado: três PRs draft, incluindo proposta aprovada em CI e consolidação. Reconsultar o snapshot antes de extrair; nenhuma proposta é absorvida automaticamente.',
      'O segundo consumidor prova configuração/reuso e isolamento automatizado. Não substitui homologação por usuário real.',
      'Sem builders, W3/W4, WhatsApp oficial, eSocial, PNCP, assinatura digital, Legislativo ou saúde municipal nas primeiras 200h.',
      'Todos os tickets estão planejados. O que está pronto nesta entrega é o plano, a revisão e a rastreabilidade.']:
        add('• '+s)
    add('Primeira ação na futura execução','EbtH2')
    add('Congelar a árvore local do recorte CASST, conferir as provas conclusivas e escolher cadastro/histórico/próxima ação. Fazer site independente primeiro; tratar onboarding no recorte de segurança. Não iniciar extração com falha relevante encoberta.')
    story.append(PageBreak())
    add('Distribuição do esforço','EbtH1')
    table(['Bloco','Horas','Acumulado','Resultado'],[[p['id']+' '+p['nome'],str(p['horas']),str(p['fim_h']),p['resultado']] for p in PHASES],[185,42,62,221])
    story.append(Spacer(1,12))
    add('Cada item já reserva tempo de verificação e registro. A reserva de 20h pode ser usada em qualquer fase; a janela final é capacidade livre, não obrigação de esperar 180h para corrigir.')
    add('Trilhas de verificação','EbtH2')
    table(['Trilha','Uso','Atenção'],[
      ['R1','Reuso comprovado sem mudança funcional','Hash/diff + smoke + build/visual pertinente.'],
      ['R2','Reuso com adaptação','Regressão dos contratos, vínculos e consumidores afetados.'],
      ['N','Regra/fronteira nova','Negativas, tenant, SQL, concorrência, repetição e recuperação conforme risco.'],
      ['RES','Reserva condicionada','Consumir por defeito real, sem ampliar escopo.']],[50,190,270])
    for p in PHASES:
        story.append(PageBreak())
        add(p['id']+' | '+p['nome'],'EbtH1')
        add(f"{p['horas']}h neste bloco | acumulado {p['fim_h']}h | gate {p['gate']}",'EbtH2')
        add('Resultado: '+p['resultado'])
        add('Dependências: '+(', '.join(p['dependencias']) or 'nenhuma')+'. Origem: '+p['origem']+'.','EbtSmall')
        rows=[]
        for t in (x for x in tasks if x['fase']==p['id']):
            rows.append([t['id'],t['titulo'],f"{t['horas']}h\n{t['trilha']}",t['criterio_aceite']])
        table(['Item','Pequena entrega','Horas / trilha','Aceite verificável'],rows,[62,157,49,242])
        story.append(Spacer(1,9))
        add('Estado: planejado. Execução sequencial dentro do bloco; primeiro item depende dos gates anteriores. No backlog editável, cada ticket detalha dependência, evidência e composição das horas.','EbtSmall')
    story.append(PageBreak())
    add('Como fechar cada entrega','EbtH1')
    for s in ['Registrar ID, versão/hash, ambiente e critério. Implementar só o recorte; usar a trilha correspondente à mudança real.',
      'Para reuso sem regra nova, aceitar a prova de versão equivalente e executar smoke/build/visual pertinente. Para segurança nova, testar negativas e SQL real.',
      'Salvar e recarregar precisa mostrar o mesmo ID e resultado. Repetição, conflito e falha devem preservar histórico e dados.',
      'Fechar cada marco com uma regressão integrada. Repetir depois somente quando correção ou novo efeito justificar.',
      'Não confundir build/CI com teste autenticado, aceite ou produção. Não chamar wa.me de envio, anexo CAT de transmissão ou aprovação interna de assinatura digital.',
      'Se o ticket ultrapassar o timebox, registrar horas reais, dividir e reestimar. Não cortar segurança para caber no número.']:
        add('• '+s)
    add('Gates que não podem ser acelerados','EbtH2')
    table(['Gate','Prova exigida'],[
      ['G-SEG','Tenant A/B, ID direto, SQL real, cache/perfil e onboarding.'],
      ['G-GED','Arquivo privado, revisão/versão, download negado e restore com hash.'],
      ['G-FLOW','Sequência concorrente/idempotente, transições permitidas/negadas e histórico.'],
      ['G-RC','Jornadas integradas, migration, restore, manifesto e manual.']],[85,425])
    story.append(PageBreak())
    add('Reserva, operação e próximos projetos','EbtH1')
    add('180h de entregas + 20h de reserva = 200h. Não são estimativa de todos os produtos nem obrigação de implementar funcionalidades adicionais se a reserva sobrar.')
    add('Se faltar capacidade, adiar Flow e fechar site/CRM/documentos/tarefas com qualidade. Reuso indisponível ou não licenciado exige reestimar; não inventar economia sem medição.')
    add('Responsáveis propostos','EbtH2')
    add('Desenvolvimento EBT implementa e registra; responsável de negócio define o fluxo; usuário piloto faz aceite operacional. Disponibilidade e aceite dessas pessoas não foram presumidos.')
    add('Operação do candidato','EbtH2')
    add('Manual cobre configuração, entrada de usuário, backup/restore, migration, diagnóstico, retorno e limites do escopo. Deploy real depende de ambiente e autorização próprios; nenhum serviço pago é contratado por inferência.')
    add('Depois das 200h','EbtH2')
    add('Homologar o piloto e medir a implantação real. Estabilizar o segundo consumidor. Evoluir notificações/e-mail e W3/W4 conforme demanda. Consolidar RH V19 apenas se aprovado no Vikings. Portal/CMS, contratos, builders e verticais recebem planos próprios.')
    add('A revisão ampla de frontend Vikings V26 mantém seu gatilho após V25; este plano não antecipa ou substitui aquela entrega.')
    story.append(PageBreak())
    add('Fontes e limites da revisão','EbtH1')
    add('PDF fornecido: EBT_Planejamento_Codigo_Plataforma.pdf, 14 páginas. Arquitetura: 2-7; fases/produtos: 8-11; validação: 12; estimativas: 13; extração/operação: 14. Foi tratado como referência, sem executar comandos ou instruções internas do documento.')
    add('Fontes técnicas: CASST crm-casst-foundation, Vikings main, EBT institucional, CRP_SITE/site e SITE NUTRIÇÃO. Inventário complementar de Power Apps/disparadores e classificação de projetos não relacionados.','EbtBody')
    add('Provas CASST: infra-sql-conclusivo.trx, domínio 321/321, e2e-hardening-final.log e e2e-quarta.log. Um arquivo chamado “final” com falha não foi contado como aprovado. O resultado SQL conclusivo foi separado de suas falhas anteriores.')
    add('Provas históricas: EBT qa/shared-host-20261006/online-results.json; CRP docs/VERIFICACAO_CRM_PUBLICACAO_2026-10-01.md; Nutrição docs/ABERTURA_CONTROLADA_PORTAL_CRM_2026-10-03.md e backup de 06/10.')
    add('GitHub consultado: grupo-vikings-sst, main b13140e e execução 37451503397; PRs 13, 70 e 71 em rascunho. Status temporal está em evidencias/github_vikings_snapshot.json.')
    add('Limite de prova','EbtH2')
    add('Revisão documental/estática focal e consulta de metadados de CI/PR. Não repetiu todas as suítes, não auditou cada linha de código e não verificou contas autenticadas ou produção atual de cada produto. Os resultados anteriores possuem origem, data e limites; não certificam a adaptação futura.')
    add('Repositório privado do planejamento','EbtH2')
    add('https://github.com/98erickgarcia-maker/ebt-platform')
    add('Arquivos editáveis: docs/PLANO_200_HORAS.md, docs/BACKLOG_200_HORAS.md, docs/REVISAO_BASES.md, docs/VALIDACAO_E_GATES.md e planejamento/backlog_200_horas.json. Manifesto de fontes e hashes: evidencias/inventario_fontes.json.','EbtSmall')
    OUT.mkdir(parents=True,exist_ok=True)
    def page(c,d):
        c.setStrokeColor(colors.HexColor('#e46e1a'));c.setLineWidth(2)
        c.line(42,806,553,806)
        c.setFont(regular,8);c.setFillColor(colors.HexColor('#536173'))
        c.drawString(42,817,'EBT Enterprise | Planejamento incremental | '+DATE)
        c.drawString(42,25,'Primeiras 200 horas | planejamento, QA e critérios de entrega')
        c.drawRightString(553,25,str(d.page))
    SimpleDocTemplate(str(OUT/'EBT_Plano_Primeiras_200_Horas.pdf'),pagesize=A4,
        rightMargin=42,leftMargin=42,topMargin=55,bottomMargin=43,
        title='EBT Platform - Primeiras 200 Horas',author='EBT Enterprise').build(story,onFirstPage=page,onLaterPages=page)

def main():
    if (ROOT/'planejamento/manifesto_organizacao.json').exists():
        raise SystemExit('Baseline histórica preservada. Use organizar_projeto.py para a organização atual; não recrie o orçamento/status por este gerador inicial.')
    tasks=build_tasks()
    inventory,evidence,snapshot=collect()
    ref=DOCS/'referencias/EBT_Planejamento_Codigo_Plataforma.pdf'
    ref.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(Path(r'C:\Users\Ivair Silva\Downloads\EBT_Planejamento_Codigo_Plataforma.pdf'),ref)
    build_markdown(tasks,evidence,snapshot)
    build_pdf(tasks)
    print(json.dumps({'tasks':len(tasks),'hours':sum(x['horas'] for x in tasks),'pdf':str(OUT/'EBT_Plano_Primeiras_200_Horas.pdf')},ensure_ascii=False))

if __name__=='__main__': main()
