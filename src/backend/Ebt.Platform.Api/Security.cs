using System.Security.Claims;
using Microsoft.AspNetCore.Antiforgery;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;

namespace Ebt.Platform.Api;

public static class Security
{
    public static string Password(PlatformUser user, string password)
    {
        if (password.Length is < 12 or > 128 || !password.Any(char.IsLetter) || !password.Any(char.IsDigit))
            throw new ApiFault(400, "invalid_password", "Use uma senha com 12 a 128 caracteres, letras e números.");
        return new PasswordHasher<PlatformUser>().HashPassword(user, password);
    }
    public static async Task SignIn(HttpContext http, PlatformUser user, Guid tenantId)
    {
        var db = http.RequestServices.GetRequiredService<PlatformDb>();
        if (Guid.TryParse(http.User.FindFirstValue("session"), out var previousId))
        {
            var previous = await db.Sessions.SingleOrDefaultAsync(x => x.Id == previousId && x.UserId == user.Id);
            if (previous != null) previous.Revoked = true;
        }
        var session = new UserSession { UserId = user.Id, TenantId = tenantId, ExpiresAt = DateTimeOffset.UtcNow.AddHours(8) };
        db.Sessions.Add(session); await db.SaveChangesAsync();
        var principal = new ClaimsPrincipal(new ClaimsIdentity(new[] {
            new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()), new Claim("stamp", user.Stamp), new Claim("tenant", tenantId.ToString()), new Claim("session", session.Id.ToString())
        }, CookieAuthenticationDefaults.AuthenticationScheme));
        await http.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, principal,
            new AuthenticationProperties { IsPersistent = false, ExpiresUtc = DateTimeOffset.UtcNow.AddHours(8) });
    }
    public static async Task ValidateContext(HttpContext http, RequestDelegate next)
    {
        var db = http.RequestServices.GetRequiredService<PlatformDb>();
        var access = http.RequestServices.GetRequiredService<AccessScope>();
        var bearer = http.Request.Headers.Authorization.ToString();
        Guid userId = Guid.Empty, tenantId = Guid.Empty;
        PlatformUser? user = null;
        if (bearer.StartsWith("Bearer ", StringComparison.Ordinal))
        {
            var token = bearer[7..];
            if (token.Length == 64 && http.Request.Path.StartsWithSegments("/api/connect"))
            {
                var hash = Contract.Hash(token);
                var key = await db.Credentials.IgnoreQueryFilters().AsNoTracking().SingleOrDefaultAsync(x => x.TokenHash == hash && x.Active && x.ExpiresAt > DateTimeOffset.UtcNow);
                if (key != null) { userId = key.UserId; tenantId = key.TenantId; http.Items["api-key"] = true; }
            }
        }
        else if (http.User.Identity?.IsAuthenticated == true)
        {
            Guid.TryParse(http.User.FindFirstValue(ClaimTypes.NameIdentifier), out userId);
            Guid.TryParse(http.User.FindFirstValue("tenant"), out tenantId);
            user = await db.Users.AsNoTracking().SingleOrDefaultAsync(x => x.Id == userId && x.Active);
            Guid.TryParse(http.User.FindFirstValue("session"), out var sessionId);
            if (user?.Stamp != http.User.FindFirstValue("stamp") || !await db.Sessions.AnyAsync(x => x.Id == sessionId && x.UserId == userId && x.TenantId == tenantId && !x.Revoked && x.ExpiresAt > DateTimeOffset.UtcNow)) userId = Guid.Empty;
        }
        if (userId != Guid.Empty)
        {
            user ??= await db.Users.AsNoTracking().SingleOrDefaultAsync(x => x.Id == userId && x.Active);
            var membership = await db.Memberships.IgnoreQueryFilters().AsNoTracking().SingleOrDefaultAsync(x => x.UserId == userId && x.TenantId == tenantId && x.Active);
            var tenant = await db.Tenants.AsNoTracking().SingleOrDefaultAsync(x => x.Id == tenantId && x.Active);
            if (user != null && membership != null && tenant != null && membership.Role != "support")
            {
                access.UserId = userId; access.TenantId = tenantId; access.Role = membership.Role; access.Portfolio = membership.Portfolio;
            }
        }
        var path = http.Request.Path.Value ?? "";
        var anonymous = path is "/api/security/csrf" or "/api/auth/login" or "/api/auth/activate" or "/api/auth/logout" || path.StartsWith("/webhooks/", StringComparison.Ordinal);
        if (path.StartsWith("/api/", StringComparison.Ordinal) && !anonymous && !access.CanRead)
            throw new ApiFault(401, "authentication_required", "Entre novamente para continuar.");
        if (access.CanRead) http.Response.Headers["X-Access-Scope"] = $"{access.TenantId}|{access.Role}|{access.Portfolio}";
        if (access.CanRead && !HttpMethods.IsGet(http.Request.Method) && http.Request.Headers.TryGetValue("X-Expected-Tenant", out var expectedTenant) && expectedTenant.ToString() != access.TenantId.ToString())
            throw new ApiFault(409, "context_changed", "A empresa selecionada mudou. Confira o contexto antes de repetir.");
        if (path.StartsWith("/api/", StringComparison.Ordinal) && !HttpMethods.IsGet(http.Request.Method) && !HttpMethods.IsHead(http.Request.Method) && http.Items["api-key"] == null)
        {
            try { await http.RequestServices.GetRequiredService<IAntiforgery>().ValidateRequestAsync(http); }
            catch (AntiforgeryValidationException) { throw new ApiFault(400, "csrf_invalid", "Sua sessão mudou. Atualize a página e tente novamente."); }
        }
        await next(http);
    }
    public static void Map(WebApplication app)
    {
        app.MapGet("/api/security/csrf", (HttpContext http, IAntiforgery csrf) => Results.Ok(new { token = csrf.GetAndStoreTokens(http).RequestToken }));
        app.MapPost("/api/auth/login", async (LoginCommand command, HttpContext http, PlatformDb db) =>
        {
            var email = Contract.Email(command.Email);
            await using var tx = await db.Lock("login:" + Contract.Hash(email));
            var user = await db.Users.SingleOrDefaultAsync(x => x.Email == email);
            var now = DateTimeOffset.UtcNow;
            var verify = new PasswordHasher<PlatformUser>();
            if (user == null || !user.Active || user.LockedUntil > now || verify.VerifyHashedPassword(user, user.PasswordHash, command.Password ?? "") == PasswordVerificationResult.Failed)
            {
                if (user != null && user.LockedUntil <= now || user != null && user.LockedUntil == null)
                { user.FailedLogins++; if (user.FailedLogins >= 5) user.LockedUntil = now.AddMinutes(15); await db.SaveChangesAsync(); }
                await tx.CommitAsync();
                throw new ApiFault(401, "invalid_login", "E-mail ou senha inválidos, ou acesso temporariamente bloqueado.");
            }
            var membership = await db.Memberships.IgnoreQueryFilters().Where(x => x.UserId == user.Id && x.Active && x.Role != "support" && db.Tenants.Any(t => t.Id == x.TenantId && t.Active)).OrderBy(x => x.TenantId).FirstOrDefaultAsync();
            if (membership == null) throw new ApiFault(401, "invalid_login", "Não há empresa ativa disponível para este acesso.");
            user.FailedLogins = 0; user.LockedUntil = null;
            await db.SaveChangesAsync(); await tx.CommitAsync();
            await SignIn(http, user, membership.TenantId);
            return Results.Ok(new { user.Name, tenantId = membership.TenantId });
        }).RequireRateLimiting("auth");
        app.MapPost("/api/auth/logout", async (HttpContext http, PlatformDb db) =>
        {
            if (Guid.TryParse(http.User.FindFirstValue("session"), out var id) && Guid.TryParse(http.User.FindFirstValue(ClaimTypes.NameIdentifier), out var userId))
            {
                var session = await db.Sessions.SingleOrDefaultAsync(x => x.Id == id && x.UserId == userId);
                if (session != null) { session.Revoked = true; await db.SaveChangesAsync(); }
            }
            await http.SignOutAsync(); return Results.NoContent();
        });
        app.MapGet("/api/auth/me", async (AccessScope access, PlatformDb db) =>
        {
            var user = await db.Users.AsNoTracking().SingleAsync(x => x.Id == access.UserId);
            var memberships = await db.Memberships.IgnoreQueryFilters().Where(x => x.UserId == access.UserId && x.Active && x.Role != "support").Join(db.Tenants.Where(x => x.Active), x => x.TenantId, x => x.Id, (m, t) => new { t.Id, t.Name, t.Product, m.Role }).ToListAsync();
            return Results.Ok(new { user.Name, user.Email, userId = user.Id, tenantId = access.TenantId, role = access.Role, portfolio = access.Portfolio, tenants = memberships });
        });
        app.MapPost("/api/auth/context/{id:guid}", async (Guid id, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            if (!await db.Memberships.IgnoreQueryFilters().AnyAsync(x => x.TenantId == id && x.UserId == access.UserId && x.Active && x.Role != "support") || !await db.Tenants.AnyAsync(x => x.Id == id && x.Active)) throw ApiFault.NotFound();
            var user = await db.Users.SingleAsync(x => x.Id == access.UserId);
            await SignIn(http, user, id); return Results.NoContent();
        });
        app.MapGet("/api/admin/members", async (AccessScope access, PlatformDb db) =>
        {
            var query = db.Memberships.Where(x => access.IsAdmin || x.Active && x.Role != "support" && x.Portfolio == access.Portfolio);
            return Results.Ok(await query.Join(db.Users.Where(x => x.Active), x => x.UserId, x => x.Id, (m, u) => new { m.Id, m.UserId, u.Name, m.Role, m.Portfolio, m.Active, m.Version }).ToListAsync());
        });
        app.MapPut("/api/admin/members/{id:guid}", async (Guid id, MembershipCommand command, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            access.RequireAdmin();
            if (command.Role is not ("admin" or "operator" or "reader" or "support")) throw new ApiFault(400, "invalid_role", "Perfil inválido.");
            await using var tx = await db.Lock("members");
            var m = await db.Memberships.SingleOrDefaultAsync(x => x.Id == id) ?? throw ApiFault.NotFound();
            Contract.Match(http.Request, m.Version);
            if (m.Role == "admin" && (command.Role != "admin" || !command.Active) && !await db.Memberships.AnyAsync(x => x.Id != id && x.Role == "admin" && x.Active)) throw new ApiFault(409, "last_admin", "Mantenha ao menos um administrador ativo.");
            m.Role = command.Role; m.Active = command.Active; m.Portfolio = Contract.Required(command.Portfolio, 60, "Carteira");
            db.Record(access, "membership.changed", id, http.TraceIdentifier); await db.SaveChangesAsync(); await tx.CommitAsync(); return Results.Ok(new { m.Id, m.Version });
        });
        app.MapPost("/api/admin/invitations", async (InviteCommand command, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            access.RequireAdmin();
            if (command.Role is not ("admin" or "operator" or "reader")) throw new ApiFault(400, "invalid_role", "Perfil inválido.");
            var email = Contract.Email(command.Email);
            if (email == "") throw new ApiFault(400, "invalid_email", "Informe o e-mail do convidado.");
            var existingUserId = await db.Users.AsNoTracking().Where(x => x.Email == email).Select(x => (Guid?)x.Id).SingleOrDefaultAsync();
            if (existingUserId.HasValue && await db.Memberships.AnyAsync(x => x.UserId == existingUserId.Value && x.Active))
                throw new ApiFault(409, "already_member", "Este e-mail já possui vínculo ativo com esta empresa.");
            var token = Contract.Token();
            var invite = new Invitation { TenantId = access.TenantId, Email = email, Role = command.Role, Portfolio = Contract.Required(command.Portfolio, 60, "Carteira"), TokenHash = Contract.Hash(token), ExpiresAt = DateTimeOffset.UtcNow.AddDays(2) };
            db.Invitations.Add(invite); db.Record(access, "invitation.created", invite.Id, http.TraceIdentifier); await db.SaveChangesAsync();
            return Results.Ok(new { invite.Id, invite.ExpiresAt, activationToken = token });
        });
        app.MapPost("/api/auth/activate", async (AcceptInviteCommand command, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            var hash = Contract.Hash(Contract.Required(command.Token, 64, "Convite"));
            await using var tx = await db.Lock("invite:" + hash);
            var invite = await db.Invitations.IgnoreQueryFilters().SingleOrDefaultAsync(x => x.TokenHash == hash && x.UsedAt == null && x.ExpiresAt > DateTimeOffset.UtcNow) ?? throw new ApiFault(400, "invalid_invitation", "Convite inválido, expirado ou já utilizado.");
            if (!await db.Tenants.AnyAsync(x => x.Id == invite.TenantId && x.Active)) throw new ApiFault(400, "invalid_invitation", "Convite indisponível.");
            // Existing users must authenticate; activation never resets another user's password.
            var existing = await db.Users.AnyAsync(x => x.Email == invite.Email);
            if (existing) throw new ApiFault(409, "existing_user", "Este e-mail já possui conta. Entre com ela e aceite o convite recebido.");
            access.TenantId = invite.TenantId;
            var user = new PlatformUser { Email = invite.Email, Name = Contract.Required(command.Name, 120, "Nome") };
            user.PasswordHash = Password(user, command.Password);
            db.Users.Add(user); db.Memberships.Add(new Membership { TenantId = invite.TenantId, UserId = user.Id, Role = invite.Role, Portfolio = invite.Portfolio });
            invite.UsedAt = DateTimeOffset.UtcNow; db.Record(access, "invitation.activated", invite.Id, http.TraceIdentifier);
            await db.SaveChangesAsync(); await tx.CommitAsync(); await SignIn(http, user, invite.TenantId);
            return Results.Ok(new { user.Id, user.Name, tenantId = invite.TenantId });
        }).RequireRateLimiting("auth");
        app.MapPost("/api/auth/invitations/accept-existing", async (AcceptExistingInviteCommand command, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            var hash = Contract.Hash(Contract.Required(command.Token, 64, "Convite"));
            var user = await db.Users.AsNoTracking().SingleAsync(x => x.Id == access.UserId && x.Active);
            // Different tokens for the same account cannot create duplicate memberships concurrently.
            await using var tx = await db.Lock("global:invite-existing-user:" + access.UserId);
            var invite = await db.Invitations.IgnoreQueryFilters().SingleOrDefaultAsync(x => x.TokenHash == hash && x.UsedAt == null && x.ExpiresAt > DateTimeOffset.UtcNow)
                ?? throw new ApiFault(400, "invalid_invitation", "Convite inválido, expirado ou já utilizado.");
            if (!await db.Tenants.AsNoTracking().AnyAsync(x => x.Id == invite.TenantId && x.Active))
                throw new ApiFault(400, "invalid_invitation", "Convite indisponível.");
            if (!string.Equals(user.Email, invite.Email, StringComparison.OrdinalIgnoreCase))
                throw new ApiFault(403, "invitation_owner_mismatch", "Este convite pertence a outra conta.");

            var membership = await db.Memberships.IgnoreQueryFilters().SingleOrDefaultAsync(x => x.TenantId == invite.TenantId && x.UserId == access.UserId);
            if (membership?.Active == true)
                throw new ApiFault(409, "already_member", "Sua conta já possui vínculo ativo com esta empresa.");

            access.TenantId = invite.TenantId;
            if (membership == null)
            {
                membership = new Membership { TenantId = invite.TenantId, UserId = access.UserId, Role = invite.Role, Portfolio = invite.Portfolio };
                db.Memberships.Add(membership);
            }
            else
            {
                membership.Role = invite.Role;
                membership.Portfolio = invite.Portfolio;
                membership.Active = true;
            }

            invite.UsedAt = DateTimeOffset.UtcNow;
            db.Record(access, "invitation.linked", invite.Id, http.TraceIdentifier);
            await db.SaveChangesAsync(); await tx.CommitAsync();
            return Results.Ok(new { membership.Id, tenantId = invite.TenantId, membership.Role, membership.Portfolio });
        }).RequireRateLimiting("auth");
        app.MapGet("/api/admin/api-keys", async (AccessScope access, PlatformDb db) =>
        {
            access.RequireAdmin();
            var now = DateTimeOffset.UtcNow;
            var keys = await db.Credentials.AsNoTracking()
                .Join(db.Users.AsNoTracking(), key => key.UserId, user => user.Id, (key, user) => new
                {
                    key.Id,
                    key.Name,
                    key.UserId,
                    ownerName = user.Name,
                    ownerEmail = user.Email,
                    key.ExpiresAt,
                    key.Active,
                    state = !key.Active ? "revoked" : key.ExpiresAt <= now ? "expired" : "active"
                })
                .OrderByDescending(x => x.ExpiresAt)
                .ToListAsync();
            return Results.Ok(keys);
        });
        app.MapPost("/api/admin/api-keys", async (AccessScope access, PlatformDb db, HttpContext http) =>
        {
            access.RequireAdmin(); var token = Contract.Token();
            var key = new ApiCredential { TenantId = access.TenantId, UserId = access.UserId, Name = "Connect API", TokenHash = Contract.Hash(token), ExpiresAt = DateTimeOffset.UtcNow.AddDays(30) };
            db.Credentials.Add(key); db.Record(access, "api_key.created", key.Id, http.TraceIdentifier); await db.SaveChangesAsync();
            return Results.Ok(new { key.Id, key.ExpiresAt, token });
        });
        app.MapDelete("/api/admin/api-keys/{id:guid}", async (Guid id, AccessScope access, PlatformDb db, HttpContext http) =>
        {
            access.RequireAdmin(); var key = await db.Credentials.SingleOrDefaultAsync(x => x.Id == id) ?? throw ApiFault.NotFound();
            if (!key.Active) return Results.NoContent();
            key.Active = false; db.Record(access, "api_key.revoked", id, http.TraceIdentifier); await db.SaveChangesAsync(); return Results.NoContent();
        });
    }
}
