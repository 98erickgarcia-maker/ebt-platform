using System.Net;
using System.Net.Http.Json;
using System.Security.Claims;
using Ebt.Application.Security;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;

namespace Ebt.Foundation.Tests;

public sealed class SecurityBoundaryTests
{
    [Theory]
    [InlineData(EbtRole.Administrator, true, true, true)]
    [InlineData(EbtRole.Operator, true, true, true)]
    [InlineData(EbtRole.ReadOnly, true, false, true)]
    [InlineData(EbtRole.TechnicalSupport, false, false, false)]
    public void Access_matrix_is_explicit(
        EbtRole role,
        bool canRead,
        bool canWrite,
        bool canDownload)
    {
        Assert.Equal(canRead, EbtAccessMatrix.Allows(role, EbtPermission.FoundationRecordRead));
        Assert.Equal(canWrite, EbtAccessMatrix.Allows(role, EbtPermission.FoundationRecordWrite));
        Assert.Equal(canDownload, EbtAccessMatrix.Allows(role, EbtPermission.FoundationAttachmentDownload));
    }

    [Fact]
    public void Expired_session_claim_is_rejected()
    {
        var identity = new ClaimsIdentity(
        [
            new Claim(ClaimTypes.NameIdentifier, Guid.NewGuid().ToString("D")),
            new Claim(
                EbtSessionClaims.ExpiresAtUnix,
                DateTimeOffset.UtcNow.AddMinutes(-1).ToUnixTimeSeconds().ToString())
        ],
        "test");

        var principal = new ClaimsPrincipal(identity);
        Assert.False(EbtSessionClaims.IsSessionCurrent(principal, TimeProvider.System));
    }

    [Fact]
    public async Task Qa_login_uses_server_identity_and_client_headers_do_not_switch_tenant()
    {
        const string loginCode = "synthetic-login-code";
        var previous = Environment.GetEnvironmentVariable("EBT_QA_LOGIN_CODE");
        Environment.SetEnvironmentVariable("EBT_QA_LOGIN_CODE", loginCode);

        try
        {
            await using var factory = new SecurityApiFactory();
            using var client = factory.CreateClient(new WebApplicationFactoryClientOptions
            {
                AllowAutoRedirect = false,
                HandleCookies = true
            });

            using var login = await client.PostAsJsonAsync("/api/auth/qa-login", new
            {
                email = "admin.orbe@demo.invalid",
                code = loginCode
            });
            Assert.Equal(HttpStatusCode.NoContent, login.StatusCode);

            using var request = new HttpRequestMessage(HttpMethod.Get, "/api/auth/me");
            request.Headers.Add("X-EBT-TENANT", "nexo");
            request.Headers.Add("X-Tenant-Id", "22222222-2222-4222-8222-222222222222");
            using var me = await client.SendAsync(request);
            Assert.Equal(HttpStatusCode.OK, me.StatusCode);

            var payload = await me.Content.ReadFromJsonAsync<MeResponse>();
            Assert.NotNull(payload);
            Assert.Equal("orbe", payload.TenantKey);
            Assert.Equal("Administrator", payload.Role);

            using var logout = await client.PostAsJsonAsync("/api/auth/logout", new { });
            Assert.Equal(HttpStatusCode.NoContent, logout.StatusCode);

            using var afterLogout = await client.GetAsync("/api/auth/me");
            Assert.Equal(HttpStatusCode.Unauthorized, afterLogout.StatusCode);
        }
        finally
        {
            Environment.SetEnvironmentVariable("EBT_QA_LOGIN_CODE", previous);
        }
    }

    [Fact]
    public async Task Debug_headers_do_not_authenticate_anonymous_request()
    {
        await using var factory = new SecurityApiFactory();
        using var client = factory.CreateClient(new WebApplicationFactoryClientOptions
        {
            AllowAutoRedirect = false,
            HandleCookies = false
        });

        using var request = new HttpRequestMessage(HttpMethod.Get, "/api/auth/me");
        request.Headers.Add("X-EBT-USER", "admin.orbe@demo.invalid");
        request.Headers.Add("X-EBT-TENANT", "orbe");

        using var response = await client.SendAsync(request);
        Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
    }

    private sealed record MeResponse(
        Guid UserId,
        string Email,
        string DisplayName,
        string Role,
        Guid? TenantId,
        string? TenantKey);

    private sealed class SecurityApiFactory : WebApplicationFactory<Program>
    {
        protected override void ConfigureWebHost(IWebHostBuilder builder)
        {
            builder.UseEnvironment("Development");
            builder.ConfigureAppConfiguration((_, configuration) =>
            {
                configuration.AddInMemoryCollection(new Dictionary<string, string?>
                {
                    ["Ebt:ProductName"] = "EBT Connect",
                    ["Ebt:PlatformName"] = "EBT Platform",
                    ["Ebt:EnvironmentName"] = "Development",
                    ["Ebt:DefaultConsumerKey"] = "orbe",
                    ["Ebt:SyntheticDataEnabled"] = "true",
                    ["Ebt:RequirePrivateConfiguration"] = "false",
                    ["QaPersistence:Enabled"] = "false"
                });
            });
        }
    }
}
