# RevisÃ£o da plataforma genÃ©rica â€” 07/10/2026

A referÃªncia inicial Ã© a EBT Platform genÃ©rica. Connect Ã© o produto atual; Flow, Portal, Contracts, SST e Legislative compÃµem o roteiro. Vikings e CASST fornecem padrÃµes de arquitetura, sem converter o Core em domÃ­nio SST. [Remapeamento de todas as fases e produtos](../arquitetura/REMAPEAMENTO_PLATAFORMA_GENERICA_20261007.md).

## ProveniÃªncia e escopo

O checkout original estava no commit `4c185f761b2b5e212800464f4b450167a26c1b88`, com implementaÃ§Ã£o Connect anterior ainda nÃ£o versionada nesse commit. Foi copiado somente o material pÃºblico para worktree isolado. [Manifesto dos arquivos e hashes da cÃ³pia](../../evidencias/proveniencia_plataforma_generica.json). A importaÃ§Ã£o preserva trabalho preexistente; nÃ£o Ã© cÃ³digo integralmente escrito nesta revisÃ£o. ConfiguraÃ§Ãµes privadas, bancos, certificados, pacotes de entrega e credenciais nÃ£o foram copiados. O documento local de conta Outlook foi excluÃ­do da publicaÃ§Ã£o desta revisÃ£o.

Nenhum arquivo do checkout original ou Vikings foi editado por esta tarefa. NÃ£o foi feito merge, deploy, envio comercial, contrataÃ§Ã£o ou restore sobre produÃ§Ã£o. EvidÃªncias Azure/WazVox anteriores permanecem histÃ³ricas e limitadas Ã  sua versÃ£o/cenÃ¡rio.

## AlteraÃ§Ãµes desta revisÃ£o

- Remapeamento verificÃ¡vel C0â€“C13 e seis produtos, preservando 180h de entregas e 20h de reserva; capacidades parciais nÃ£o fecham fases inteiras.
- CatÃ¡logo autenticado `/api/platform/v1/capabilities`, com tenant/perfil derivados da identidade do servidor; UI diferencia EBT Platform e Connect e anuncia somente o recorte implementado.
- Cliente HTTP descarta JSON, arquivo, token CSRF e 401 de geraÃ§Ãµes antigas, incluindo troca de usuÃ¡rio com empresa/perfil iguais. Downloads aceitam apenas caminho interno de API.
- NavegaÃ§Ã£o repetida substitui carga invalidada. Troca de empresa e revogaÃ§Ã£o limpam tambÃ©m a lista de conversas; falha da nova consulta nÃ£o mantÃ©m conversas da empresa anterior.
- Scanner exige resposta INSTREAM completa com terminador NUL. AprovaÃ§Ã£o/download de versÃµes nÃ£o verificadas sÃ£o bloqueados fora de Development. Mesmo em Development estados desconhecidos, pendentes e infectados nÃ£o sÃ£o liberados; apenas `not_scanned` mantÃ©m o bypass sintÃ©tico existente.
- CI preparada com builds, contratos, cliente HTTP, SQL Server real isolado, ClamAV real e Chromium. VerificaÃ§Ã£o SQL ocorre apÃ³s criar documento sintÃ©tico para testar isolamento sem negativa vazia.
- Contrato PromptSpellSmith especÃ­fico da plataforma: [agente e limites](../execucao/AGENTE_PLATAFORMA_GENERICA.md), validado pelo lint estrito.

## EvidÃªncia local

Fixtures prÃ³prias: banco `EbtPlatformQa_Generic_88f7c845fc`, localhost; API em 5196. NÃ£o reutilizam dados comerciais. Backend e frontend compilam; dependÃªncias restauradas de lockfile; auditoria de produÃ§Ã£o npm sem vulnerabilidades.

- Cliente HTTP: 7 cenÃ¡rios; defeitos reproduzidos antes da correÃ§Ã£o.
- Protocolos WazVox: 17; proxy: 10; scanner sintÃ©tico: 4; catÃ¡logo/polÃ­tica de documento: 4.
- HTTP com SQL real: 25/25; catÃ¡logo autenticado: 3/3.
- SQL direto: oito verificaÃ§Ãµes, incluindo RLS, escrita cruzada bloqueada, leitura de documento existente de A por B bloqueada e schema alheio preservado.
- Navegador: sete jornadas configuradas; resultado da versÃ£o final deve ser consultado na prova especÃ­fica, sem reutilizar a rodada anterior como se cobrisse alteraÃ§Ãµes novas.
- Integridade documental: 14 fases, seis produtos, PDF original vinculado por hash, orÃ§amento 180h+20h e 1.347 links conferidos. Esses verificadores nÃ£o testam funcionamento dos mÃ³dulos.

A revisÃ£o independente encontrou a configuraÃ§Ã£o `Qa:SqlReport` ausente e a navegaÃ§Ã£o repetida sem recarga; ambas foram corrigidas com reproduÃ§Ã£o/verificaÃ§Ã£o. TambÃ©m foi corrigida a limpeza da lista de conversas. O CI hospedado e o engine real sÃ³ podem ser declarados aprovados apÃ³s execuÃ§Ã£o no GitHub.

## Fronteiras que permanecem abertas

Scanner privado de produÃ§Ã£o, restore Azure e aceite operacional ainda dependem de prova prÃ³pria. NÃ£o foram homologados OAuth/Outlook, templates/campanhas de fornecedor, mÃ­dia, motor Workflow, protocolo ou Builders. O catÃ¡logo nÃ£o Ã© ativaÃ§Ã£o persistida de mÃ³dulos por cliente. NÃ£o hÃ¡ migraÃ§Ã£o de dados das fontes nem alteraÃ§Ã£o do namespace Data Protection ou schema existente.

O roteiro restante estÃ¡ remapeado por contrato e dependÃªncia; nÃ£o cabe afirmar que todo C0â€“C13 e todas as verticais foram implementados nas 200h. Horas reais nÃ£o foram inventadas.

RepositÃ³rio: [EBT Platform no GitHub](https://github.com/98erickgarcia-maker/ebt-platform). Branch desta revisÃ£o: [plataforma genÃ©rica](https://github.com/98erickgarcia-maker/ebt-platform/tree/codex/plataforma-generica-finalizacao).
