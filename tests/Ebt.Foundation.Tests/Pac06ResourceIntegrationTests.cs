using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;

namespace Ebt.Foundation.Tests;

public sealed class Pac06ResourceIntegrationTests
{
    [QaFact]
    [Trait("Category", "QaPersistence")]
    public async Task Api_enforces_resource_scope_on_ID_download_list_export_and_role_switch()
    {
        await using var factory = new QaApiFactory();
        using var admin = Client(factory);
        using var op = Client(factory);
        using var nexo = Client(factory);
        await Login(admin, "admin.orbe@demo.invalid");
        using var created = await admin.PostAsJsonAsync("/api/foundation/records", new
        {
            tenantKey = "nexo", title = "Carteira admin", attachmentFileName = "prova.txt",
            attachmentContentType = "text/plain", attachmentBase64 = "RUJUIFFBIEcx"
        });
        Assert.Equal(HttpStatusCode.Created, created.StatusCode);
        AssertNoStore(created);
        var record = await created.Content.ReadFromJsonAsync<JsonElement>();
        var id = record.GetProperty("id").GetGuid();
        Assert.Equal("orbe", record.GetProperty("tenantKey").GetString());
        await Login(op, "operador.orbe@demo.invalid");
        using var deniedId = await op.GetAsync($"/api/foundation/records/{id}");
        Assert.Equal(HttpStatusCode.NotFound, deniedId.StatusCode);
        AssertNoStore(deniedId);
        using var deniedAttachment = await op.GetAsync($"/api/foundation/records/{id}/attachment");
        Assert.Equal(HttpStatusCode.NotFound, deniedAttachment.StatusCode);
        AssertNoStore(deniedAttachment);
        using var opCreated = await op.PostAsJsonAsync("/api/foundation/records", new { title = "Carteira operador" });
        Assert.Equal(HttpStatusCode.Created, opCreated.StatusCode);
        var own = await opCreated.Content.ReadFromJsonAsync<JsonElement>();
        var ownId = own.GetProperty("id").GetGuid();
        var listed = await op.GetFromJsonAsync<JsonElement[]>("/api/foundation/records/");
        Assert.Equal(ownId, Assert.Single(listed!).GetProperty("id").GetGuid());
        using var export = await op.GetAsync("/api/foundation/records/export");
        Assert.Equal(HttpStatusCode.OK, export.StatusCode);
        AssertNoStore(export);
        var exported = await export.Content.ReadFromJsonAsync<JsonElement[]>();
        Assert.Equal(ownId, Assert.Single(exported!).GetProperty("id").GetGuid());
        await Login(nexo, "admin.nexo@demo.invalid");
        using var crossId = await nexo.GetAsync($"/api/foundation/records/{id}");
        using var crossFile = await nexo.GetAsync($"/api/foundation/records/{id}/attachment");
        Assert.Equal(HttpStatusCode.NotFound, crossId.StatusCode);
        Assert.Equal(HttpStatusCode.NotFound, crossFile.StatusCode);
        Assert.Empty((await nexo.GetFromJsonAsync<JsonElement[]>("/api/foundation/records/"))!);
        using var allowedDownload = await admin.GetAsync($"/api/foundation/records/{id}/attachment");
        Assert.Equal("EBT QA G1", await allowedDownload.Content.ReadAsStringAsync());
        AssertNoStore(allowedDownload);
        // Same cookie jar changes profile; server must use the new identity.
        await Login(op, "consulta.orbe@demo.invalid");
        using var readOnlyWrite = await op.PostAsJsonAsync("/api/foundation/records", new { title = "Não permitido" });
        Assert.Equal(HttpStatusCode.Forbidden, readOnlyWrite.StatusCode);
        using var logout = await op.PostAsJsonAsync("/api/auth/logout", new { });
        Assert.Equal(HttpStatusCode.NoContent, logout.StatusCode);
        AssertNoStore(logout);
        using var afterLogout = await op.GetAsync("/api/foundation/records/");
        Assert.Equal(HttpStatusCode.Unauthorized, afterLogout.StatusCode);
        AssertNoStore(afterLogout);
    }

    private static HttpClient Client(WebApplicationFactory<Program> factory) => factory.CreateClient(
        new WebApplicationFactoryClientOptions { AllowAutoRedirect = false, HandleCookies = true });

    private static async Task Login(HttpClient client, string email)
    {
        using var response = await client.PostAsJsonAsync("/api/auth/qa-login", new
        {
            email, code = Environment.GetEnvironmentVariable("EBT_QA_LOGIN_CODE")
        });
        Assert.Equal(HttpStatusCode.NoContent, response.StatusCode);
        AssertNoStore(response);
    }

    private static void AssertNoStore(HttpResponseMessage response) =>
        Assert.True(response.Headers.CacheControl?.NoStore);

    private sealed class QaApiFactory : WebApplicationFactory<Program>
    {
        protected override void ConfigureWebHost(IWebHostBuilder builder)
        {
            builder.UseEnvironment("QA");
            builder.ConfigureAppConfiguration((_, configuration) =>
                configuration.AddConfiguration(Pac06SqlIntegrationTests.Configuration("api")));
        }
    }
}
