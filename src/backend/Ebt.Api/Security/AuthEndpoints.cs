using Ebt.Application.Security;
using Microsoft.AspNetCore.Authentication;

namespace Ebt.Api.Security;

public static class AuthEndpoints
{
    public static IEndpointRouteBuilder MapEbtAuthEndpoints(this IEndpointRouteBuilder endpoints)
    {
        var group = endpoints.MapGroup("/api/auth");

        group.MapPost("/qa-login", LoginAsync);
        group.MapPost("/logout", (Delegate)LogoutAsync).RequireAuthorization();
        group.MapGet("/me", Me).RequireAuthorization();

        return endpoints;
    }

    private static async Task<IResult> LoginAsync(
        QaLoginRequest request,
        IWebHostEnvironment environment,
        IEbtIdentityCatalog catalog,
        TimeProvider clock,
        HttpContext context)
    {
        if (!environment.IsDevelopment() && !environment.IsEnvironment("QA"))
            return Results.NotFound();

        var expectedCode = Environment.GetEnvironmentVariable(
            EbtAuthentication.QaLoginCodeEnvironmentVariable);

        if (string.IsNullOrWhiteSpace(expectedCode)
            || string.IsNullOrWhiteSpace(request.Code)
            || !string.Equals(request.Code, expectedCode, StringComparison.Ordinal))
            return Results.Unauthorized();

        var identity = catalog.FindByEmail(request.Email ?? string.Empty);
        if (identity is not { IsActive: true })
            return Results.Unauthorized();

        var principal = EbtAuthentication.CreatePrincipal(identity, clock.GetUtcNow());
        await context.SignInAsync(
            EbtAuthentication.Scheme,
            principal,
            new AuthenticationProperties
            {
                IsPersistent = false,
                AllowRefresh = false,
                ExpiresUtc = clock.GetUtcNow().Add(EbtAuthentication.SessionLifetime)
            });

        return Results.NoContent();
    }

    private static async Task<IResult> LogoutAsync(HttpContext context)
    {
        await context.SignOutAsync(EbtAuthentication.Scheme);
        context.Response.Cookies.Delete("ebt.session", new CookieOptions
        {
            HttpOnly = true,
            SameSite = SameSiteMode.Strict,
            Secure = context.Request.IsHttps,
            Path = "/"
        });
        context.Response.StatusCode = StatusCodes.Status204NoContent;
        return Results.Empty;
    }

    private static IResult Me(IEbtTenantContext tenantContext)
    {
        var identity = tenantContext.Current;
        if (identity is null)
            return Results.Unauthorized();

        return Results.Ok(new
        {
            identity.UserId,
            identity.Email,
            identity.DisplayName,
            role = identity.Role.ToString(),
            identity.TenantId,
            identity.TenantKey
        });
    }
}

public sealed record QaLoginRequest(string? Email, string? Code);
