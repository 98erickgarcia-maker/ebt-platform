-- EBT Platform only. Additive catalog; never move or rewrite application data.
SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF SCHEMA_ID(N'ebt_platform') IS NULL EXEC(N'CREATE SCHEMA [ebt_platform] AUTHORIZATION [dbo]');
IF OBJECT_ID(N'ebt_platform.Applications', N'U') IS NULL
BEGIN
    CREATE TABLE [ebt_platform].[Applications] (
        [Code] varchar(32) COLLATE Latin1_General_100_BIN2 NOT NULL,
        [Name] nvarchar(100) NOT NULL,
        [Description] nvarchar(400) NOT NULL,
        [State] varchar(16) NOT NULL,
        [DataSchema] sysname NULL,
        [SortOrder] int NOT NULL,
        CONSTRAINT [PK_PlatformApplications] PRIMARY KEY ([Code]),
        CONSTRAINT [CK_PlatformApplications_State] CHECK ([State] IN ('available','planned','disabled')),
        CONSTRAINT [CK_PlatformApplications_Order] CHECK ([SortOrder] >= 0)
    );
END;
IF OBJECT_ID(N'ebt_platform.SchemaVersions', N'U') IS NULL
    CREATE TABLE [ebt_platform].[SchemaVersions] ([Version] varchar(80) NOT NULL PRIMARY KEY, [AppliedAt] datetimeoffset NOT NULL);
-- Insert public application definitions once; later operator decisions are preserved.
INSERT INTO [ebt_platform].[Applications] ([Code],[Name],[Description],[State],[DataSchema],[SortOrder])
SELECT v.Code,v.Name,v.Description,v.State,v.DataSchema,v.SortOrder
FROM (VALUES
 ('connect',N'EBT Connect',N'Relacionamentos, conversas, tarefas e documentos da sua empresa.','available',N'ebt_connect',10),
 ('flow',N'EBT Flow',N'Protocolos, processos e fluxos de trabalho.','planned',NULL,20),
 ('portal',N'EBT Portal',N'Conteúdo, serviços e publicações para o público.','planned',NULL,30),
 ('sites',N'EBT Sites',N'Sites institucionais e presença digital.','planned',NULL,40),
 ('contracts',N'EBT Contracts',N'Contratos, vigências e acompanhamento.','planned',NULL,50),
 ('sst',N'EBT SST',N'Rotinas, documentos e acompanhamento de SST.','planned',NULL,60),
 ('legislativo',N'EBT Legislativo',N'Processos e rotinas do Legislativo.','planned',NULL,70),
 ('educacao',N'EBT Educação',N'Aplicativos e processos para educação.','planned',NULL,80),
 ('saude',N'EBT Saúde',N'Aplicativos e processos para saúde.','planned',NULL,90)
) v(Code,Name,Description,State,DataSchema,SortOrder)
WHERE NOT EXISTS (SELECT 1 FROM [ebt_platform].[Applications] a WITH (UPDLOCK,HOLDLOCK) WHERE a.Code=v.Code);
IF NOT EXISTS (SELECT 1 FROM [ebt_platform].[SchemaVersions] WITH (UPDLOCK,HOLDLOCK) WHERE Version='20261009_PlatformCatalog_v1')
    INSERT INTO [ebt_platform].[SchemaVersions] VALUES ('20261009_PlatformCatalog_v1',SYSUTCDATETIME());
COMMIT;
