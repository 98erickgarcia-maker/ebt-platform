-- EBT Flow only. Explicit manual review and QA gate required before any application.
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

IF OBJECT_ID(N'ebt_flow.tenant_guard',N'IF') IS NULL
 EXEC(N'CREATE FUNCTION ebt_flow.tenant_guard(@TenantId uniqueidentifier)
 RETURNS TABLE WITH SCHEMABINDING AS RETURN SELECT 1 AS allowed
 WHERE @TenantId=TRY_CONVERT(uniqueidentifier,SESSION_CONTEXT(N''ebt_tenant''))
 OR TRY_CONVERT(int,SESSION_CONTEXT(N''ebt_system''))=1;');
IF NOT EXISTS (SELECT 1 FROM sys.security_policies WHERE name=N'tenant_barrier' AND schema_id=SCHEMA_ID(N'ebt_flow'))
 EXEC(N'CREATE SECURITY POLICY ebt_flow.tenant_barrier
 ADD FILTER PREDICATE ebt_flow.tenant_guard(TenantId) ON ebt_flow.Protocols,
 ADD BLOCK PREDICATE ebt_flow.tenant_guard(TenantId) ON ebt_flow.Protocols AFTER INSERT,
 ADD BLOCK PREDICATE ebt_flow.tenant_guard(TenantId) ON ebt_flow.Protocols AFTER UPDATE,
 ADD BLOCK PREDICATE ebt_flow.tenant_guard(TenantId) ON ebt_flow.Protocols BEFORE UPDATE,
 ADD BLOCK PREDICATE ebt_flow.tenant_guard(TenantId) ON ebt_flow.Protocols BEFORE DELETE,
 ADD FILTER PREDICATE ebt_flow.tenant_guard(TenantId) ON ebt_flow.Movements,
 ADD BLOCK PREDICATE ebt_flow.tenant_guard(TenantId) ON ebt_flow.Movements AFTER INSERT,
 ADD BLOCK PREDICATE ebt_flow.tenant_guard(TenantId) ON ebt_flow.Movements AFTER UPDATE,
 ADD BLOCK PREDICATE ebt_flow.tenant_guard(TenantId) ON ebt_flow.Movements BEFORE UPDATE,
 ADD BLOCK PREDICATE ebt_flow.tenant_guard(TenantId) ON ebt_flow.Movements BEFORE DELETE
 WITH (STATE=ON);');
-- Runtime grants are reviewed separately for the existing EBT identity.
COMMIT;
