-- EBT Flow MVP only. Explicit manual review and QA gate required before any application.
-- Never run automatically on the shared production database.
SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF SCHEMA_ID(N'ebt_flow') IS NULL EXEC(N'CREATE SCHEMA [ebt_flow] AUTHORIZATION [dbo]');
IF OBJECT_ID(N'ebt_flow.Protocols',N'U') IS NULL
BEGIN
 CREATE TABLE ebt_flow.Protocols (
  TenantId uniqueidentifier NOT NULL,
  Id uniqueidentifier NOT NULL,
  Number int NOT NULL,
  [Year] int NOT NULL,
  Subject nvarchar(180) NOT NULL,
  [State] varchar(16) NOT NULL CONSTRAINT DF_FlowState DEFAULT ('open'),
  Portfolio nvarchar(60) NOT NULL,
  Version bigint NOT NULL CONSTRAINT DF_FlowVersion DEFAULT (1),
  CreatedAt datetimeoffset NOT NULL,
  CreatedBy uniqueidentifier NOT NULL,
  OperationKey nvarchar(100) NOT NULL,
  PayloadHash varchar(64) NOT NULL,
  CONSTRAINT PK_FlowProtocols PRIMARY KEY (TenantId,Id),
  CONSTRAINT UQ_FlowNumber UNIQUE (TenantId,[Year],Number),
  CONSTRAINT UQ_FlowOperation UNIQUE (TenantId,OperationKey),
  CONSTRAINT CK_FlowState CHECK ([State] IN ('open','in_review','complete')),
  CONSTRAINT CK_FlowNumber CHECK (Number>0)
 );
END;
IF OBJECT_ID(N'ebt_flow.Movements',N'U') IS NULL
BEGIN
 CREATE TABLE ebt_flow.Movements (
  TenantId uniqueidentifier NOT NULL,
  Id uniqueidentifier NOT NULL,
  ProtocolId uniqueidentifier NOT NULL,
  ActorId uniqueidentifier NOT NULL,
  [Action] varchar(16) NOT NULL,
  Result nvarchar(1000) NOT NULL CONSTRAINT DF_FlowResult DEFAULT (N''),
  OccurredAt datetimeoffset NOT NULL,
  CONSTRAINT PK_FlowMovements PRIMARY KEY (TenantId,Id),
  CONSTRAINT FK_FlowProtocol FOREIGN KEY (TenantId,ProtocolId)
   REFERENCES ebt_flow.Protocols(TenantId,Id),
  CONSTRAINT CK_FlowAction CHECK ([Action] IN ('created','start','complete'))
 );
END;
COMMIT;
