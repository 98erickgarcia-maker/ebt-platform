-- EBT-only schema. No CREATE DATABASE or other product schema mutations.
-- Reviewed target: existing sqldb-crm-casst-dev-v2; local rehearsal: EbtPlatformQa_*.
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET ARITHABORT ON;
SET NUMERIC_ROUNDABORT OFF;
SET XACT_ABORT ON;
GO
IF DB_NAME() <> N'sqldb-crm-casst-dev-v2' AND LEFT(DB_NAME(),14) <> N'EbtPlatformQa_'
    THROW 51011, 'Wrong EBT shared or synthetic QA database.', 1;
IF SCHEMA_ID(N'ebt_connect') IS NOT NULL AND OBJECT_ID(N'ebt_connect.__EFMigrationsHistory') IS NULL
   AND EXISTS(SELECT 1 FROM sys.tables WHERE schema_id=SCHEMA_ID(N'ebt_connect'))
    THROW 51012, 'Existing EBT tables without reviewed migration history.', 1;
GO
IF OBJECT_ID(N'[ebt_connect].[__EFMigrationsHistory]') IS NULL
BEGIN
    IF SCHEMA_ID(N'ebt_connect') IS NULL EXEC(N'CREATE SCHEMA [ebt_connect];');
    CREATE TABLE [ebt_connect].[__EFMigrationsHistory] (
        [MigrationId] nvarchar(150) NOT NULL,
        [ProductVersion] nvarchar(32) NOT NULL,
        CONSTRAINT [PK___EFMigrationsHistory] PRIMARY KEY ([MigrationId])
    );
END;
GO

BEGIN TRANSACTION;
IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    IF SCHEMA_ID(N'ebt_connect') IS NULL EXEC(N'CREATE SCHEMA [ebt_connect];');
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Receipts] (
        [Id] uniqueidentifier NOT NULL,
        [AppKey] nvarchar(100) NOT NULL,
        [BodyHash] nvarchar(64) NOT NULL,
        [ProtectedBody] nvarchar(max) NOT NULL,
        [State] nvarchar(max) NOT NULL,
        [Diagnostic] nvarchar(max) NOT NULL,
        [ReceivedAt] datetimeoffset NOT NULL,
        CONSTRAINT [PK_Receipts] PRIMARY KEY ([Id])
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Tenants] (
        [Id] uniqueidentifier NOT NULL,
        [Name] nvarchar(max) NOT NULL,
        [Product] nvarchar(max) NOT NULL,
        [Active] bit NOT NULL,
        CONSTRAINT [PK_Tenants] PRIMARY KEY ([Id])
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Users] (
        [Id] uniqueidentifier NOT NULL,
        [Email] nvarchar(254) NOT NULL,
        [Name] nvarchar(max) NOT NULL,
        [PasswordHash] nvarchar(max) NOT NULL,
        [Stamp] nvarchar(max) NOT NULL,
        [Active] bit NOT NULL,
        [FailedLogins] int NOT NULL,
        [LockedUntil] datetimeoffset NULL,
        CONSTRAINT [PK_Users] PRIMARY KEY ([Id])
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Audit] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [ActorId] uniqueidentifier NULL,
        [Action] nvarchar(max) NOT NULL,
        [ResourceId] uniqueidentifier NULL,
        [TraceId] nvarchar(max) NOT NULL,
        [At] datetimeoffset NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_Audit] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_Audit_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Connections] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [Name] nvarchar(max) NOT NULL,
        [Provider] nvarchar(max) NOT NULL,
        [AppKey] nvarchar(100) NOT NULL,
        [AccountId] nvarchar(100) NOT NULL,
        [PhoneNumberId] nvarchar(100) NOT NULL,
        [SecretRef] nvarchar(max) NOT NULL,
        [Portfolio] nvarchar(max) NOT NULL,
        [OperatorId] uniqueidentifier NOT NULL,
        [Active] bit NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_Connections] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_Connections_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Imports] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [UserId] uniqueidentifier NOT NULL,
        [Portfolio] nvarchar(max) NOT NULL,
        [Content] nvarchar(max) NOT NULL,
        [PayloadHash] nvarchar(max) NOT NULL,
        [State] nvarchar(max) NOT NULL,
        [OperationKey] nvarchar(100) NOT NULL,
        [ResultJson] nvarchar(max) NOT NULL,
        [ExpiresAt] datetimeoffset NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_Imports] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_Imports_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Invitations] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [Email] nvarchar(max) NOT NULL,
        [Role] nvarchar(max) NOT NULL,
        [Portfolio] nvarchar(max) NOT NULL,
        [TokenHash] nvarchar(64) NOT NULL,
        [ExpiresAt] datetimeoffset NOT NULL,
        [UsedAt] datetimeoffset NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_Invitations] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_Invitations_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Organizations] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [Name] nvarchar(max) NOT NULL,
        [ExternalKey] nvarchar(100) NOT NULL,
        [Portfolio] nvarchar(max) NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_Organizations] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_Organizations_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Credentials] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [UserId] uniqueidentifier NOT NULL,
        [Name] nvarchar(max) NOT NULL,
        [TokenHash] nvarchar(64) NOT NULL,
        [ExpiresAt] datetimeoffset NOT NULL,
        [Active] bit NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_Credentials] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_Credentials_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_Credentials_Users_UserId] FOREIGN KEY ([UserId]) REFERENCES [ebt_connect].[Users] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Memberships] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [UserId] uniqueidentifier NOT NULL,
        [Role] nvarchar(max) NOT NULL,
        [Portfolio] nvarchar(max) NOT NULL,
        [Active] bit NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_Memberships] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [AK_Memberships_TenantId_UserId] UNIQUE ([TenantId], [UserId]),
        CONSTRAINT [FK_Memberships_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_Memberships_Users_UserId] FOREIGN KEY ([UserId]) REFERENCES [ebt_connect].[Users] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[DeliveryEvents] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [ConnectionId] uniqueidentifier NOT NULL,
        [ProviderId] nvarchar(max) NOT NULL,
        [Status] nvarchar(max) NOT NULL,
        [OccurredAt] datetimeoffset NOT NULL,
        [EventKey] nvarchar(64) NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_DeliveryEvents] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_DeliveryEvents_Connections_TenantId_ConnectionId] FOREIGN KEY ([TenantId], [ConnectionId]) REFERENCES [ebt_connect].[Connections] ([TenantId], [Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_DeliveryEvents_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Contacts] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [CreationHash] nvarchar(max) NOT NULL,
        [Name] nvarchar(max) NOT NULL,
        [ExternalKey] nvarchar(100) NOT NULL,
        [Email] nvarchar(max) NOT NULL,
        [Phone] nvarchar(max) NOT NULL,
        [Stage] nvarchar(max) NOT NULL,
        [Portfolio] nvarchar(max) NOT NULL,
        [OwnerId] uniqueidentifier NOT NULL,
        [OrganizationId] uniqueidentifier NULL,
        [CreatedAt] datetimeoffset NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_Contacts] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_Contacts_Memberships_TenantId_OwnerId] FOREIGN KEY ([TenantId], [OwnerId]) REFERENCES [ebt_connect].[Memberships] ([TenantId], [UserId]) ON DELETE NO ACTION,
        CONSTRAINT [FK_Contacts_Organizations_TenantId_OrganizationId] FOREIGN KEY ([TenantId], [OrganizationId]) REFERENCES [ebt_connect].[Organizations] ([TenantId], [Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_Contacts_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Conversations] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [ContactId] uniqueidentifier NOT NULL,
        [ConnectionId] uniqueidentifier NOT NULL,
        [Recipient] nvarchar(24) NOT NULL,
        [State] nvarchar(max) NOT NULL,
        [LastInboundAt] datetimeoffset NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_Conversations] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_Conversations_Connections_TenantId_ConnectionId] FOREIGN KEY ([TenantId], [ConnectionId]) REFERENCES [ebt_connect].[Connections] ([TenantId], [Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_Conversations_Contacts_TenantId_ContactId] FOREIGN KEY ([TenantId], [ContactId]) REFERENCES [ebt_connect].[Contacts] ([TenantId], [Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_Conversations_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Interactions] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [ContactId] uniqueidentifier NOT NULL,
        [ActorId] uniqueidentifier NOT NULL,
        [Kind] nvarchar(max) NOT NULL,
        [Content] nvarchar(max) NOT NULL,
        [OccurredAt] datetimeoffset NOT NULL,
        [RecordedAt] datetimeoffset NOT NULL,
        [OperationKey] nvarchar(100) NOT NULL,
        [PayloadHash] nvarchar(max) NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_Interactions] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_Interactions_Contacts_TenantId_ContactId] FOREIGN KEY ([TenantId], [ContactId]) REFERENCES [ebt_connect].[Contacts] ([TenantId], [Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_Interactions_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Tasks] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [CloseKey] nvarchar(max) NOT NULL,
        [CloseHash] nvarchar(max) NOT NULL,
        [ContactId] uniqueidentifier NOT NULL,
        [OwnerId] uniqueidentifier NOT NULL,
        [Title] nvarchar(max) NOT NULL,
        [DueAt] datetimeoffset NOT NULL,
        [State] nvarchar(max) NOT NULL,
        [Result] nvarchar(max) NOT NULL,
        [ClosedAt] datetimeoffset NULL,
        [OperationKey] nvarchar(100) NOT NULL,
        [PayloadHash] nvarchar(max) NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_Tasks] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_Tasks_Contacts_TenantId_ContactId] FOREIGN KEY ([TenantId], [ContactId]) REFERENCES [ebt_connect].[Contacts] ([TenantId], [Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_Tasks_Memberships_TenantId_OwnerId] FOREIGN KEY ([TenantId], [OwnerId]) REFERENCES [ebt_connect].[Memberships] ([TenantId], [UserId]) ON DELETE NO ACTION,
        CONSTRAINT [FK_Tasks_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Messages] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [ConversationId] uniqueidentifier NOT NULL,
        [Direction] nvarchar(max) NOT NULL,
        [Content] nvarchar(max) NOT NULL,
        [Status] nvarchar(max) NOT NULL,
        [ProviderId] nvarchar(250) NOT NULL,
        [ReplyToMessageId] uniqueidentifier NULL,
        [ActorId] uniqueidentifier NULL,
        [FailureCode] nvarchar(max) NOT NULL,
        [CreatedAt] datetimeoffset NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_Messages] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_Messages_Conversations_TenantId_ConversationId] FOREIGN KEY ([TenantId], [ConversationId]) REFERENCES [ebt_connect].[Conversations] ([TenantId], [Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_Messages_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Documents] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [CreationKey] nvarchar(100) NOT NULL,
        [CreationHash] nvarchar(max) NOT NULL,
        [ContactId] uniqueidentifier NOT NULL,
        [TaskId] uniqueidentifier NULL,
        [Title] nvarchar(max) NOT NULL,
        [CurrentVersion] int NOT NULL,
        [ReviewState] nvarchar(max) NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_Documents] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_Documents_Contacts_TenantId_ContactId] FOREIGN KEY ([TenantId], [ContactId]) REFERENCES [ebt_connect].[Contacts] ([TenantId], [Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_Documents_Tasks_TenantId_TaskId] FOREIGN KEY ([TenantId], [TaskId]) REFERENCES [ebt_connect].[Tasks] ([TenantId], [Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_Documents_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[Outbox] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [MessageId] uniqueidentifier NOT NULL,
        [ConversationId] uniqueidentifier NOT NULL,
        [ActorId] uniqueidentifier NOT NULL,
        [OperationKey] nvarchar(100) NOT NULL,
        [PayloadHash] nvarchar(max) NOT NULL,
        [State] nvarchar(max) NOT NULL,
        [Attempts] int NOT NULL,
        [DueAt] datetimeoffset NOT NULL,
        [LeaseUntil] datetimeoffset NULL,
        [Fence] nvarchar(max) NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_Outbox] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_Outbox_Messages_TenantId_MessageId] FOREIGN KEY ([TenantId], [MessageId]) REFERENCES [ebt_connect].[Messages] ([TenantId], [Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_Outbox_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE TABLE [ebt_connect].[DocumentVersions] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [OperationKey] nvarchar(100) NOT NULL,
        [PayloadHash] nvarchar(max) NOT NULL,
        [DocumentId] uniqueidentifier NOT NULL,
        [Number] int NOT NULL,
        [Content] varbinary(max) NOT NULL,
        [Sha256] nvarchar(max) NOT NULL,
        [FileName] nvarchar(max) NOT NULL,
        [MediaType] nvarchar(max) NOT NULL,
        [ActorId] uniqueidentifier NOT NULL,
        [CreatedAt] datetimeoffset NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_DocumentVersions] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_DocumentVersions_Documents_TenantId_DocumentId] FOREIGN KEY ([TenantId], [DocumentId]) REFERENCES [ebt_connect].[Documents] ([TenantId], [Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_DocumentVersions_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_Connections_AppKey_AccountId_PhoneNumberId] ON [ebt_connect].[Connections] ([AppKey], [AccountId], [PhoneNumberId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_Contacts_TenantId_ExternalKey] ON [ebt_connect].[Contacts] ([TenantId], [ExternalKey]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE INDEX [IX_Contacts_TenantId_OrganizationId] ON [ebt_connect].[Contacts] ([TenantId], [OrganizationId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE INDEX [IX_Contacts_TenantId_OwnerId] ON [ebt_connect].[Contacts] ([TenantId], [OwnerId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_Conversations_TenantId_ConnectionId_Recipient] ON [ebt_connect].[Conversations] ([TenantId], [ConnectionId], [Recipient]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE INDEX [IX_Conversations_TenantId_ContactId] ON [ebt_connect].[Conversations] ([TenantId], [ContactId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_Credentials_TokenHash] ON [ebt_connect].[Credentials] ([TokenHash]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE INDEX [IX_Credentials_UserId] ON [ebt_connect].[Credentials] ([UserId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_DeliveryEvents_TenantId_ConnectionId_EventKey] ON [ebt_connect].[DeliveryEvents] ([TenantId], [ConnectionId], [EventKey]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_Documents_TenantId_ContactId_CreationKey] ON [ebt_connect].[Documents] ([TenantId], [ContactId], [CreationKey]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE INDEX [IX_Documents_TenantId_TaskId] ON [ebt_connect].[Documents] ([TenantId], [TaskId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_DocumentVersions_TenantId_DocumentId_Number] ON [ebt_connect].[DocumentVersions] ([TenantId], [DocumentId], [Number]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_DocumentVersions_TenantId_DocumentId_OperationKey] ON [ebt_connect].[DocumentVersions] ([TenantId], [DocumentId], [OperationKey]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    EXEC(N'CREATE UNIQUE INDEX [IX_Imports_TenantId_UserId_OperationKey] ON [ebt_connect].[Imports] ([TenantId], [UserId], [OperationKey]) WHERE [OperationKey] <> ''''');
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_Interactions_TenantId_ContactId_OperationKey] ON [ebt_connect].[Interactions] ([TenantId], [ContactId], [OperationKey]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_Invitations_TokenHash] ON [ebt_connect].[Invitations] ([TokenHash]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_Memberships_TenantId_UserId] ON [ebt_connect].[Memberships] ([TenantId], [UserId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE INDEX [IX_Memberships_UserId] ON [ebt_connect].[Memberships] ([UserId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    EXEC(N'CREATE UNIQUE INDEX [IX_Messages_TenantId_ConversationId_ProviderId] ON [ebt_connect].[Messages] ([TenantId], [ConversationId], [ProviderId]) WHERE [ProviderId] <> ''''');
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_Organizations_TenantId_ExternalKey] ON [ebt_connect].[Organizations] ([TenantId], [ExternalKey]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_Outbox_TenantId_ConversationId_OperationKey] ON [ebt_connect].[Outbox] ([TenantId], [ConversationId], [OperationKey]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE INDEX [IX_Outbox_TenantId_MessageId] ON [ebt_connect].[Outbox] ([TenantId], [MessageId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_Receipts_AppKey_BodyHash] ON [ebt_connect].[Receipts] ([AppKey], [BodyHash]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_Tasks_TenantId_ContactId_OperationKey] ON [ebt_connect].[Tasks] ([TenantId], [ContactId], [OperationKey]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE INDEX [IX_Tasks_TenantId_OwnerId] ON [ebt_connect].[Tasks] ([TenantId], [OwnerId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    CREATE UNIQUE INDEX [IX_Users_Email] ON [ebt_connect].[Users] ([Email]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061736_InitialConnect'
)
BEGIN
    INSERT INTO [ebt_connect].[__EFMigrationsHistory] ([MigrationId], [ProductVersion])
    VALUES (N'20261007061736_InitialConnect', N'10.0.12');
END;

COMMIT;
GO

BEGIN TRANSACTION;
IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061901_DocumentReviewHistory'
)
BEGIN
    ALTER TABLE [ebt_connect].[DocumentVersions] ADD [ReviewReason] nvarchar(max) NOT NULL DEFAULT N'';
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061901_DocumentReviewHistory'
)
BEGIN
    ALTER TABLE [ebt_connect].[DocumentVersions] ADD [ReviewState] nvarchar(max) NOT NULL DEFAULT N'';
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061901_DocumentReviewHistory'
)
BEGIN
    ALTER TABLE [ebt_connect].[DocumentVersions] ADD [ReviewedAt] datetimeoffset NULL;
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061901_DocumentReviewHistory'
)
BEGIN
    ALTER TABLE [ebt_connect].[DocumentVersions] ADD [ReviewedBy] uniqueidentifier NULL;
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061901_DocumentReviewHistory'
)
BEGIN
    ALTER TABLE [ebt_connect].[DocumentVersions] ADD [ScanState] nvarchar(max) NOT NULL DEFAULT N'';
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007061901_DocumentReviewHistory'
)
BEGIN
    INSERT INTO [ebt_connect].[__EFMigrationsHistory] ([MigrationId], [ProductVersion])
    VALUES (N'20261007061901_DocumentReviewHistory', N'10.0.12');
END;

COMMIT;
GO

BEGIN TRANSACTION;
IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007062209_TenantStorageBarrier'
)
BEGIN
    EXEC(N'CREATE FUNCTION [ebt_connect].[tenant_guard](@TenantId uniqueidentifier)
    RETURNS TABLE WITH SCHEMABINDING AS
    RETURN SELECT 1 AS allowed
    WHERE @TenantId = TRY_CONVERT(uniqueidentifier, SESSION_CONTEXT(N''ebt_tenant''))
       OR TRY_CONVERT(int, SESSION_CONTEXT(N''ebt_system'')) = 1;');
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007062209_TenantStorageBarrier'
)
BEGIN
    EXEC(N'CREATE SECURITY POLICY [ebt_connect].[tenant_barrier]
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Contacts],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Contacts] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Contacts] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Contacts] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Contacts] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Organizations],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Organizations] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Organizations] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Organizations] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Organizations] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Interactions],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Interactions] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Interactions] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Interactions] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Interactions] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Tasks],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Tasks] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Tasks] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Tasks] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Tasks] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Imports],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Imports] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Imports] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Imports] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Imports] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Connections],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Connections] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Connections] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Connections] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Connections] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Conversations],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Conversations] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Conversations] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Conversations] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Conversations] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Messages],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Messages] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Messages] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Messages] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Messages] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Outbox],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Outbox] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Outbox] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Outbox] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Outbox] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DeliveryEvents],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DeliveryEvents] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DeliveryEvents] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DeliveryEvents] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DeliveryEvents] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Documents],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Documents] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Documents] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Documents] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Documents] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DocumentVersions],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DocumentVersions] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DocumentVersions] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DocumentVersions] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[DocumentVersions] BEFORE DELETE,
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Audit],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Audit] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Audit] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Audit] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[Audit] BEFORE DELETE
    WITH (STATE=ON);');
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007062209_TenantStorageBarrier'
)
BEGIN
    INSERT INTO [ebt_connect].[__EFMigrationsHistory] ([MigrationId], [ProductVersion])
    VALUES (N'20261007062209_TenantStorageBarrier', N'10.0.12');
END;

COMMIT;
GO

BEGIN TRANSACTION;
IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007062505_ContactCreationLedger'
)
BEGIN
    CREATE TABLE [ebt_connect].[ContactCreations] (
        [Id] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [ContactId] uniqueidentifier NOT NULL,
        [OperationKey] nvarchar(100) NOT NULL,
        [PayloadHash] nvarchar(max) NOT NULL,
        [Version] bigint NOT NULL,
        CONSTRAINT [PK_ContactCreations] PRIMARY KEY ([TenantId], [Id]),
        CONSTRAINT [FK_ContactCreations_Contacts_TenantId_ContactId] FOREIGN KEY ([TenantId], [ContactId]) REFERENCES [ebt_connect].[Contacts] ([TenantId], [Id]) ON DELETE NO ACTION,
        CONSTRAINT [FK_ContactCreations_Tenants_TenantId] FOREIGN KEY ([TenantId]) REFERENCES [ebt_connect].[Tenants] ([Id]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007062505_ContactCreationLedger'
)
BEGIN
    CREATE INDEX [IX_ContactCreations_TenantId_ContactId] ON [ebt_connect].[ContactCreations] ([TenantId], [ContactId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007062505_ContactCreationLedger'
)
BEGIN
    CREATE UNIQUE INDEX [IX_ContactCreations_TenantId_OperationKey] ON [ebt_connect].[ContactCreations] ([TenantId], [OperationKey]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007062505_ContactCreationLedger'
)
BEGIN
    EXEC(N'ALTER SECURITY POLICY [ebt_connect].[tenant_barrier]
    ADD FILTER PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[ContactCreations],
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[ContactCreations] AFTER INSERT,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[ContactCreations] AFTER UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[ContactCreations] BEFORE UPDATE,
    ADD BLOCK PREDICATE [ebt_connect].[tenant_guard]([TenantId]) ON [ebt_connect].[ContactCreations] BEFORE DELETE;');
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007062505_ContactCreationLedger'
)
BEGIN
    INSERT INTO [ebt_connect].[__EFMigrationsHistory] ([MigrationId], [ProductVersion])
    VALUES (N'20261007062505_ContactCreationLedger', N'10.0.12');
END;

COMMIT;
GO

BEGIN TRANSACTION;
IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007064302_RevocableSessions'
)
BEGIN
    CREATE TABLE [ebt_connect].[Sessions] (
        [Id] uniqueidentifier NOT NULL,
        [UserId] uniqueidentifier NOT NULL,
        [TenantId] uniqueidentifier NOT NULL,
        [ExpiresAt] datetimeoffset NOT NULL,
        [Revoked] bit NOT NULL,
        CONSTRAINT [PK_Sessions] PRIMARY KEY ([Id]),
        CONSTRAINT [FK_Sessions_Memberships_TenantId_UserId] FOREIGN KEY ([TenantId], [UserId]) REFERENCES [ebt_connect].[Memberships] ([TenantId], [UserId]) ON DELETE NO ACTION
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007064302_RevocableSessions'
)
BEGIN
    CREATE INDEX [IX_Sessions_ExpiresAt] ON [ebt_connect].[Sessions] ([ExpiresAt]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007064302_RevocableSessions'
)
BEGIN
    CREATE INDEX [IX_Sessions_TenantId_UserId] ON [ebt_connect].[Sessions] ([TenantId], [UserId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007064302_RevocableSessions'
)
BEGIN
    INSERT INTO [ebt_connect].[__EFMigrationsHistory] ([MigrationId], [ProductVersion])
    VALUES (N'20261007064302_RevocableSessions', N'10.0.12');
END;

COMMIT;
GO

BEGIN TRANSACTION;
IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007071227_ProviderConnectionIdentity'
)
BEGIN
    DROP INDEX [IX_Messages_TenantId_ConversationId_ProviderId] ON [ebt_connect].[Messages];
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007071227_ProviderConnectionIdentity'
)
BEGIN
    DECLARE @var nvarchar(max);
    SELECT @var = QUOTENAME([d].[name])
    FROM [sys].[default_constraints] [d]
    INNER JOIN [sys].[columns] [c] ON [d].[parent_column_id] = [c].[column_id] AND [d].[parent_object_id] = [c].[object_id]
    WHERE ([d].[parent_object_id] = OBJECT_ID(N'[ebt_connect].[Messages]') AND [c].[name] = N'ProviderId');
    IF @var IS NOT NULL EXEC(N'ALTER TABLE [ebt_connect].[Messages] DROP CONSTRAINT ' + @var + ';');
    ALTER TABLE [ebt_connect].[Messages] ALTER COLUMN [ProviderId] nvarchar(250) COLLATE Latin1_General_100_BIN2 NOT NULL;
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007071227_ProviderConnectionIdentity'
)
BEGIN
    ALTER TABLE [ebt_connect].[Messages] ADD [ConnectionId] uniqueidentifier NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007071227_ProviderConnectionIdentity'
)
BEGIN
    DECLARE @var1 nvarchar(max);
    SELECT @var1 = QUOTENAME([d].[name])
    FROM [sys].[default_constraints] [d]
    INNER JOIN [sys].[columns] [c] ON [d].[parent_column_id] = [c].[column_id] AND [d].[parent_object_id] = [c].[object_id]
    WHERE ([d].[parent_object_id] = OBJECT_ID(N'[ebt_connect].[DeliveryEvents]') AND [c].[name] = N'ProviderId');
    IF @var1 IS NOT NULL EXEC(N'ALTER TABLE [ebt_connect].[DeliveryEvents] DROP CONSTRAINT ' + @var1 + ';');
    ALTER TABLE [ebt_connect].[DeliveryEvents] ALTER COLUMN [ProviderId] nvarchar(250) COLLATE Latin1_General_100_BIN2 NOT NULL;
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007071227_ProviderConnectionIdentity'
)
BEGIN
    EXEC sys.sp_set_session_context @key=N'ebt_system', @value=1; EXEC(N'UPDATE m SET ConnectionId=c.ConnectionId FROM ebt_connect.Messages m JOIN ebt_connect.Conversations c ON c.TenantId=m.TenantId AND c.Id=m.ConversationId;'); EXEC sys.sp_set_session_context @key=N'ebt_system', @value=NULL;
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007071227_ProviderConnectionIdentity'
)
BEGIN
    EXEC(N'CREATE UNIQUE INDEX [IX_Messages_TenantId_ConnectionId_ProviderId] ON [ebt_connect].[Messages] ([TenantId], [ConnectionId], [ProviderId]) WHERE [ProviderId] <> ''''');
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007071227_ProviderConnectionIdentity'
)
BEGIN
    CREATE INDEX [IX_Messages_TenantId_ConversationId] ON [ebt_connect].[Messages] ([TenantId], [ConversationId]);
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007071227_ProviderConnectionIdentity'
)
BEGIN
    ALTER TABLE [ebt_connect].[Messages] ADD CONSTRAINT [FK_Messages_Connections_TenantId_ConnectionId] FOREIGN KEY ([TenantId], [ConnectionId]) REFERENCES [ebt_connect].[Connections] ([TenantId], [Id]) ON DELETE NO ACTION;
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007071227_ProviderConnectionIdentity'
)
BEGIN
    INSERT INTO [ebt_connect].[__EFMigrationsHistory] ([MigrationId], [ProductVersion])
    VALUES (N'20261007071227_ProviderConnectionIdentity', N'10.0.12');
END;

COMMIT;
GO

BEGIN TRANSACTION;
IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007090647_WazVoxEventIdentity'
)
BEGIN
    ALTER TABLE [ebt_connect].[Receipts] ADD [ProviderEventId] nvarchar(200) COLLATE Latin1_General_100_BIN2 NOT NULL DEFAULT N'';
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007090647_WazVoxEventIdentity'
)
BEGIN
    EXEC(N'CREATE UNIQUE INDEX [IX_Receipts_AppKey_ProviderEventId] ON [ebt_connect].[Receipts] ([AppKey], [ProviderEventId]) WHERE [ProviderEventId] <> ''''');
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007090647_WazVoxEventIdentity'
)
BEGIN
    INSERT INTO [ebt_connect].[__EFMigrationsHistory] ([MigrationId], [ProductVersion])
    VALUES (N'20261007090647_WazVoxEventIdentity', N'10.0.12');
END;

COMMIT;
GO

BEGIN TRANSACTION;
IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007114135_PersistentProtectedKeyRing'
)
BEGIN
    CREATE TABLE [ebt_connect].[DataProtectionKeys] (
        [Id] int NOT NULL IDENTITY,
        [FriendlyName] nvarchar(max) NULL,
        [Xml] nvarchar(max) NULL,
        CONSTRAINT [PK_DataProtectionKeys] PRIMARY KEY ([Id])
    );
END;

IF NOT EXISTS (
    SELECT * FROM [ebt_connect].[__EFMigrationsHistory]
    WHERE [MigrationId] = N'20261007114135_PersistentProtectedKeyRing'
)
BEGIN
    INSERT INTO [ebt_connect].[__EFMigrationsHistory] ([MigrationId], [ProductVersion])
    VALUES (N'20261007114135_PersistentProtectedKeyRing', N'10.0.12');
END;

COMMIT;
GO
