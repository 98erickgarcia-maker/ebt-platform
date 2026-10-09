-- EBT-only schema. Reviewed additive Mail and commercial qualification migration; no source data import.
BEGIN TRANSACTION;
IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    CREATE TABLE [ebt_connect].[MailDrafts] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [ContactId] uniqueidentifier NOT NULL,
        [ActorId] uniqueidentifier NOT NULL,
        [Recipient] nvarchar(max) NOT NULL,
        [Subject] nvarchar(max) NOT NULL,
        [Body] nvarchar(max) NOT NULL,
        [Origin] nvarchar(max) NOT NULL,
        [State] nvarchar(max) NOT NULL,
        [ApprovedBy] uniqueidentifier NULL,
        [ApprovedAt] datetimeoffset NULL,
        [DocumentId] uniqueidentifier NULL,
        [DocumentNumber] int NULL,
        [CreationKey] nvarchar(100) NOT NULL,
        [CreationHash] nvarchar(max) NOT NULL,
        [Diagnostic] nvarchar(max) NOT NULL,
        [CreatedAt] datetimeoffset NOT NULL,
        [AttemptedAt] datetimeoffset NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_MailDrafts] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_MailDrafts_Contacts_TenantId_ContactId] FOREIGN KEY ([TenantId], [ContactId]) REFERENCES [ebt_connect].[Contacts] ([TenantId], [Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_MailDrafts_Documents_TenantId_DocumentId] FOREIGN KEY ([TenantId], [DocumentId]) REFERENCES [ebt_connect].[Documents] ([TenantId], [Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_MailDrafts_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    CREATE TABLE [ebt_connect].[MailQuotas] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [Day] nvarchar(10) NOT NULL,
        [Used] int NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_MailQuotas] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_MailQuotas_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    CREATE TABLE [ebt_connect].[MailSettings] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [IntervalSeconds] int NOT NULL,
        [DailyCap] int NOT NULL,
        [Paused] bit NOT NULL,
        [NextSendAt] datetimeoffset NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_MailSettings] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_MailSettings_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    CREATE TABLE [ebt_connect].[MailSuppressions] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [Value] nvarchar(254) NOT NULL,
        [Reason] nvarchar(max) NOT NULL,
        [ActorId] uniqueidentifier NOT NULL,
        [Active] bit NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_MailSuppressions] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_MailSuppressions_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    CREATE TABLE [ebt_connect].[MailTemplates] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [Name] nvarchar(max) NOT NULL,
        [Subject] nvarchar(max) NOT NULL,
        [Body] nvarchar(max) NOT NULL,
        [Portfolio] nvarchar(max) NOT NULL,
        [CreationKey] nvarchar(100) NOT NULL,
        [CreationHash] nvarchar(max) NOT NULL,
        [Active] bit NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_MailTemplates] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_MailTemplates_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    CREATE TABLE [ebt_connect].[MailRevisions] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [OperationKey] nvarchar(100) NOT NULL,
        [PayloadHash] nvarchar(max) NOT NULL,
        [DraftId] uniqueidentifier NOT NULL,
        [ActorId] uniqueidentifier NOT NULL,
        [Subject] nvarchar(max) NOT NULL,
        [Body] nvarchar(max) NOT NULL,
        [Recipient] nvarchar(max) NOT NULL,
        [State] nvarchar(max) NOT NULL,
        [Reason] nvarchar(max) NOT NULL,
        [At] datetimeoffset NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_MailRevisions] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_MailRevisions_MailDrafts_TenantId_DraftId] FOREIGN KEY ([TenantId], [DraftId]) REFERENCES [ebt_connect].[MailDrafts] ([TenantId], [Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_MailRevisions_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    CREATE INDEX [IX_MailDrafts_TenantId_ContactId] ON [ebt_connect].[MailDrafts] ([TenantId], [ContactId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    CREATE UNIQUE INDEX [IX_MailDrafts_TenantId_CreationKey] ON [ebt_connect].[MailDrafts] ([TenantId], [CreationKey]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    CREATE INDEX [IX_MailDrafts_TenantId_DocumentId] ON [ebt_connect].[MailDrafts] ([TenantId], [DocumentId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    CREATE UNIQUE INDEX [IX_MailQuotas_TenantId_Day] ON [ebt_connect].[MailQuotas] ([TenantId], [Day]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    EXEC(N'CREATE UNIQUE INDEX [IX_MailRevisions_TenantId_DraftId_OperationKey] ON [ebt_connect].[MailRevisions] ([TenantId], [DraftId], [OperationKey]) WHERE [OperationKey] <> ''''');
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    CREATE UNIQUE INDEX [IX_MailSettings_TenantId] ON [ebt_connect].[MailSettings] ([TenantId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    CREATE UNIQUE INDEX [IX_MailSuppressions_TenantId_Value] ON [ebt_connect].[MailSuppressions] ([TenantId], [Value]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    CREATE UNIQUE INDEX [IX_MailTemplates_TenantId_CreationKey] ON [ebt_connect].[MailTemplates] ([TenantId], [CreationKey]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    ALTER SECURITY POLICY [ebt_connect].[tenant_barrier]
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailDrafts],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailDrafts] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailDrafts] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailDrafts] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailDrafts] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailQuotas],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailQuotas] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailQuotas] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailQuotas] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailQuotas] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailRevisions],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailRevisions] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailRevisions] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailRevisions] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailRevisions] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSettings],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSettings] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSettings] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSettings] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSettings] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSuppressions],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSuppressions] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSuppressions] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSuppressions] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailSuppressions] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailTemplates],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailTemplates] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailTemplates] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailTemplates] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[MailTemplates] BEFORE DELETE;
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009050643_ConnectMail'
)
BEGIN
    INSERT INTO [ebt_connect].[__EFMigrationsHistory] ([MigrationId], [ProductVersion])
    VALUES (N'20261009050643_ConnectMail', N'10.0.12');
END;

COMMIT;
GO

BEGIN TRANSACTION;
IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009062431_CommercialProspection'
)
BEGIN
    ALTER TABLE [ebt_connect].[MailTemplates] ADD [Channel] nvarchar(20) NOT NULL DEFAULT N'email';
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009062431_CommercialProspection'
)
BEGIN
    ALTER TABLE [ebt_connect].[MailTemplates] ADD [Purpose] nvarchar(20) NOT NULL DEFAULT N'prospection';
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009062431_CommercialProspection'
)
BEGIN
    ALTER TABLE [ebt_connect].[Contacts] ADD [ActiveSince] datetimeoffset NULL;
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009062431_CommercialProspection'
)
BEGIN
    ALTER TABLE [ebt_connect].[Contacts] ADD [BestTime] nvarchar(160) NOT NULL DEFAULT N'';
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009062431_CommercialProspection'
)
BEGIN
    ALTER TABLE [ebt_connect].[Contacts] ADD [ContactRole] nvarchar(100) NOT NULL DEFAULT N'';
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009062431_CommercialProspection'
)
BEGIN
    ALTER TABLE [ebt_connect].[Contacts] ADD [DecisionMaker] nvarchar(20) NOT NULL DEFAULT N'unknown';
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009062431_CommercialProspection'
)
BEGIN
    ALTER TABLE [ebt_connect].[Contacts] ADD [Need] nvarchar(2000) NOT NULL DEFAULT N'';
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009062431_CommercialProspection'
)
BEGIN
    ALTER TABLE [ebt_connect].[Contacts] ADD [PreferredChannel] nvarchar(20) NOT NULL DEFAULT N'';
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009062431_CommercialProspection'
)
BEGIN
    ALTER TABLE [ebt_connect].[Contacts] ADD [Segment] nvarchar(100) NOT NULL DEFAULT N'';
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009062431_CommercialProspection'
)
BEGIN
    ALTER TABLE [ebt_connect].[Contacts] ADD [Source] nvarchar(160) NOT NULL DEFAULT N'';
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009062431_CommercialProspection'
)
BEGIN
    ALTER TABLE [ebt_connect].[Contacts] ADD [SourceUrl] nvarchar(500) NOT NULL DEFAULT N'';
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261009062431_CommercialProspection'
)
BEGIN
    INSERT INTO [ebt_connect].[__EFMigrationsHistory] ([MigrationId], [ProductVersion])
    VALUES (N'20261009062431_CommercialProspection', N'10.0.12');
END;

COMMIT;
GO

