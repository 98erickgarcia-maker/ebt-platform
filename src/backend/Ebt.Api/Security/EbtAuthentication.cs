using System.Security.Claims;
using Ebt.Application.Security;
using Microsoft.AspNetCore.Authentication.Cookies;

namespace Ebt.Api.Security;

public static class EbtAuthentication
{
    public const string Scheme = "ebt.session";
    public const string QaLoginCodeEnvironmentVariable = "EBT_QA_LOGIN_CODE";
    public static readonly TimeSpan SessionLifetime = TimeSpan.FromMinutes(30);

    public static IServiceCollection AddEbtAuthentication(this IServiceCollection services)
    {
        services.AddHttpContextAccessor();
        services.AddSingleton(TimeProvider.System);
        services.AddScoped<IEbtTenantContext, CurrentIdentityTenantContext>();

        services
            .AddAuthentication(Scheme)
            .AddCookie(Scheme, options =>
            {
                options.Cookie.Name = "ebt.session";
                options.Cookie.HttpOnly = true;
                options.Cookie.SameSite = SameSiteMode.Strict;
                options.Cookie.SecurePolicy = CookieSecurePolicy.SameAsRequest;
                options.ExpireTimeSpan = SessionLifetime;
                options.SlidingExpiration = false;
                options.Events = new CookieAuthenticationEvents
                {
                    OnRedirectToLogin = context =>
                    {
                        context.Response.StatusCode = StatusCodes.Status401Unauthorized;
                        return Task.CompletedTask;
                    },
                    OnRedirectToAccessDenied = context =>
                    {
                        context.Response.StatusCode = StatusCodes.Status403Forbidden;
                        return Task.CompletedTask;
                    }
                };
            });

        services.AddAuthorization();
        return services;
    }

    public static ClaimsPrincipal CreatePrincipal(
        EbtIdentityProfile identity,
        DateTimeOffset now)
    {
        var claims = new[]
        {
            new Claim(ClaimTypes.NameIdentifier, identity.UserId.ToString("D")),
            new Claim(ClaimTypes.Email, identity.Email),
            new Claim(ClaimTypes.Name, identity.DisplayName),
            new Claim(EbtSessionClaims.ExpiresAtUnix, now.Add(SessionLifetime).ToUnixTimeSeconds().ToString())
        };

        return new ClaimsPrincipal(new ClaimsIdentity(claims, Scheme));
    }
}

public sealed class CurrentIdentityTenantContext(
    IHttpContextAccessor httpContextAccessor,
    IEbtIdentityCatalog catalog,
    TimeProvider clock) : IEbtTenantContext
{
    public EbtIdentityProfile? Current
    {
        get
        {
            var principal = httpContextAccessor.HttpContext?.User;
            if (principal?.Identity?.IsAuthenticated != true
                || !EbtSessionClaims.IsSessionCurrent(principal, clock))
                return null;

            var rawUserId = principal.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            if (!Guid.TryParse(rawUserId, out var userId))
                return null;

            var identity = catalog.FindByUserId(userId);
            return identity is { IsActive: true } ? identity : null;
        }
    }
}
