using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Migrations;

namespace Ebt.Infrastructure.Persistence.Migrations;

[DbContext(typeof(EbtDataContext))]
[Migration("202610070001_FoundationBaseline")]
public sealed class FoundationBaseline : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder) => migrationBuilder.Sql("""
        IF OBJECT_ID(N'dbo.FoundationRecords', N'U') IS NULL
        BEGIN
            CREATE TABLE dbo.FoundationRecords (
                Id uniqueidentifier NOT NULL,
                TenantKey nvarchar(64) NOT NULL,
                Title nvarchar(200) NOT NULL,
                CreatedAtUtc datetimeoffset NOT NULL,
                BlobName nvarchar(260) NULL,
                FileName nvarchar(120) NULL,
                ContentType nvarchar(120) NULL,
                AttachmentLength bigint NULL,
                CONSTRAINT PK_FoundationRecords PRIMARY KEY (Id)
            );
            CREATE INDEX IX_FoundationRecords_TenantKey_CreatedAtUtc
                ON dbo.FoundationRecords(TenantKey, CreatedAtUtc);
        END
        ELSE
        BEGIN
            -- Adopt only the exact PAC-03/05 EnsureCreated schema; never erase data.
            IF (SELECT COUNT(*) FROM sys.columns WHERE object_id=OBJECT_ID(N'dbo.FoundationRecords')) <> 8
                OR EXISTS (
                    SELECT name, TYPE_NAME(user_type_id), max_length, is_nullable
                    FROM sys.columns WHERE object_id=OBJECT_ID(N'dbo.FoundationRecords')
                    EXCEPT
                    SELECT * FROM (VALUES
                        (N'Id', N'uniqueidentifier', 16, 0),
                        (N'TenantKey', N'nvarchar', 128, 0),
                        (N'Title', N'nvarchar', 400, 0),
                        (N'CreatedAtUtc', N'datetimeoffset', 10, 0),
                        (N'BlobName', N'nvarchar', 520, 1),
                        (N'FileName', N'nvarchar', 240, 1),
                        (N'ContentType', N'nvarchar', 240, 1),
                        (N'AttachmentLength', N'bigint', 8, 1)
                    ) AS expected(name, type_name, max_length, is_nullable)
                )
                OR NOT EXISTS (SELECT 1 FROM sys.key_constraints
                    WHERE parent_object_id=OBJECT_ID(N'dbo.FoundationRecords')
                    AND name=N'PK_FoundationRecords' AND type=N'PK')
                OR (SELECT COUNT(*) FROM sys.index_columns ic
                    JOIN sys.indexes i ON i.object_id=ic.object_id AND i.index_id=ic.index_id
                    WHERE i.object_id=OBJECT_ID(N'dbo.FoundationRecords') AND i.is_primary_key=1
                    AND ic.key_ordinal > 0) <> 1
                OR NOT EXISTS (SELECT 1 FROM sys.index_columns ic
                    JOIN sys.indexes i ON i.object_id=ic.object_id AND i.index_id=ic.index_id
                    JOIN sys.columns c ON c.object_id=ic.object_id AND c.column_id=ic.column_id
                    WHERE i.object_id=OBJECT_ID(N'dbo.FoundationRecords') AND i.is_primary_key=1
                    AND c.name=N'Id' AND ic.key_ordinal=1)
                OR (SELECT COUNT(*) FROM sys.indexes WHERE object_id=OBJECT_ID(N'dbo.FoundationRecords')
                    AND index_id>0 AND is_hypothetical=0) <> 2
                OR NOT EXISTS (SELECT 1 FROM sys.indexes
                    WHERE object_id=OBJECT_ID(N'dbo.FoundationRecords')
                    AND name=N'IX_FoundationRecords_TenantKey_CreatedAtUtc'
                    AND is_unique=0 AND is_disabled=0 AND has_filter=0 AND type=2)
                OR (SELECT COUNT(*) FROM sys.index_columns ic
                    JOIN sys.indexes i ON i.object_id=ic.object_id AND i.index_id=ic.index_id
                    WHERE i.object_id=OBJECT_ID(N'dbo.FoundationRecords')
                    AND i.name=N'IX_FoundationRecords_TenantKey_CreatedAtUtc'
                    AND (ic.key_ordinal>0 OR ic.is_included_column=1)) <> 2
                OR NOT EXISTS (SELECT 1 FROM sys.index_columns ic
                    JOIN sys.indexes i ON i.object_id=ic.object_id AND i.index_id=ic.index_id
                    JOIN sys.columns c ON c.object_id=ic.object_id AND c.column_id=ic.column_id
                    WHERE i.object_id=OBJECT_ID(N'dbo.FoundationRecords')
                    AND i.name=N'IX_FoundationRecords_TenantKey_CreatedAtUtc'
                    AND c.name=N'TenantKey' AND ic.key_ordinal=1 AND ic.is_descending_key=0 AND ic.is_included_column=0)
                OR NOT EXISTS (SELECT 1 FROM sys.index_columns ic
                    JOIN sys.indexes i ON i.object_id=ic.object_id AND i.index_id=ic.index_id
                    JOIN sys.columns c ON c.object_id=ic.object_id AND c.column_id=ic.column_id
                    WHERE i.object_id=OBJECT_ID(N'dbo.FoundationRecords')
                    AND i.name=N'IX_FoundationRecords_TenantKey_CreatedAtUtc'
                    AND c.name=N'CreatedAtUtc' AND ic.key_ordinal=2 AND ic.is_descending_key=0 AND ic.is_included_column=0)
                THROW 51000, 'Schema anterior de QA incompatÃ­vel; migration interrompida.', 1;
        END;
        """);

    protected override void Down(MigrationBuilder migrationBuilder) =>
        throw new NotSupportedException("Rollback destrutivo bloqueado. Use restore de QA validado.");
}
