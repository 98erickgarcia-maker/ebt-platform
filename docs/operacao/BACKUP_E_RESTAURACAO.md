# Runbook candidato: backup e restore integrado

## Escopo

Banco, binários privados, chaves de proteção e configuração necessária para interpretar os dados. A consistência deve corresponder à arquitetura SQL/storage escolhida; o desenho SQLite/Blob do portal não é copiado automaticamente para o Core.

## Ensaio QA

1. Identificar versão do código/schema e conjunto de dados sintéticos a recuperar.
2. Garantir janela consistente entre banco e arquivos conforme mecanismo da implementação.
3. Capturar manifesto de arquivos, hashes, contagens e referência segura das chaves.
4. Selecionar destino exclusivo, diferente da origem e sem credencial real reaproveitada.
5. Restaurar conjunto e conferir integridade do banco e presença dos bytes necessários.
6. Iniciar a aplicação restaurada com a configuração correta.
7. Executar login sintético, consulta por ID e download autorizado; comparar hash.
8. Tentar acesso de B e perfil sem permissão; o restore não pode remover políticas.
9. Registrar duração medida, resultado, versão, limitações e procedimentos de limpeza do QA confirmado.

## Aceite

Aplicação abre os dados certos e o arquivo baixado é idêntico. Arquivo de backup criado, arquivo ZIP íntegro ou comando de restore sem erro não bastam isoladamente. Nenhum RPO/RTO comercial foi fixado; medir no ambiente real e acordar antes de prometer prazo de recuperação.
