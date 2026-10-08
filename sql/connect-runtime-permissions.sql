-- REVIEW TEMPLATE. Run by authorized database administrator after schema migration.
-- Target: existing sqldb-crm-casst-dev-v2. Does NOT create a database or modify other schemas.
-- These public identity identifiers were verified against the deployed Connect identity.
-- SID for a managed identity uses its client/application ID, not its object/principal ID.
-- Do not grant db_owner/db_datareader/db_datawriter or permissions on other product schemas.
DECLARE @Identity sysname = N'id-ebt-connect-hml';
DECLARE @ClientId uniqueidentifier = '196bebfa-0c4d-49a7-9e9c-46a823d8816d';
DECLARE @Sid varbinary(16) = CONVERT(varbinary(16), @ClientId);
IF DB_NAME() <> N'sqldb-crm-casst-dev-v2'
    THROW 51011, 'Wrong shared Azure database.', 1;
IF SCHEMA_ID(N'ebt_connect') IS NULL
    THROW 51012, 'Apply reviewed EBT migration first.', 1;
IF USER_ID(@Identity) IS NULL
BEGIN
    DECLARE @Create nvarchar(max) = N'CREATE USER ' + QUOTENAME(@Identity) + N' WITH SID=' + CONVERT(nvarchar(34), @Sid, 1) + N', TYPE=E;';
    EXEC sp_executesql @Create;
END;
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name=@Identity AND sid=@Sid AND type='E')
    THROW 51013, 'Existing principal differs from verified Connect identity; preserve it and review.', 1;
DECLARE @Connect nvarchar(max) = N'GRANT CONNECT TO ' + QUOTENAME(@Identity) + N';';
EXEC sp_executesql @Connect;
DECLARE @Grant nvarchar(max) = N'GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::[ebt_connect] TO ' + QUOTENAME(@Identity) + N';';
EXEC sp_executesql @Grant;
-- Migrations remain administrator-operated; runtime has no ALTER/CONTROL permission.
