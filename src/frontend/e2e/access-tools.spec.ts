import { reserveQaAuthOperation } from "./qa-auth-budget";
import {
  test,
  expect,
  type Page,
  type APIRequestContext,
} from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
const root = path.resolve(process.cwd(), "../..");
const qa = JSON.parse(
  fs.readFileSync(path.join(root, "tmp/runtime/qa-access.json"), "utf8"),
) as { password: string; tenantA: string; tenantB: string };

async function post(
  client: APIRequestContext,
  url: string,
  body?: unknown,
  expected = 200,
) {
  const csrf = await (await client.get("/api/security/csrf")).json();
  if (
    [
      "/api/auth/login",
      "/api/auth/activate",
      "/api/auth/invitations/accept-existing",
    ].includes(url)
  )
    await reserveQaAuthOperation();
  const response = await client.post(url, {
    data: body,
    headers: { "X-CSRF-TOKEN": csrf.token },
  });
  expect(response.status()).toBe(expected);
  return response.status() === 204 ? null : response.json();
}
async function login(page: Page, email = "admin@ebt.example") {
  await page.goto("/");
  await page.getByLabel("E-mail", { exact: true }).fill(email);
  await page.getByLabel("Senha", { exact: true }).fill(qa.password);
  await reserveQaAuthOperation();
  await page.getByRole("button", { name: "Entrar", exact: true }).click();
  await page.getByRole("button", { name: "Acessar Connect", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Meu dia", exact: true }),
  ).toBeVisible({ timeout: 20000 });
  const me = await (await page.request.get("/api/auth/me")).json();
  if (me.tenantId !== qa.tenantA) {
    await page.getByLabel("Empresa", { exact: true }).selectOption(qa.tenantA);
    await expect(
      page.getByText("Empresa selecionada.", { exact: true }),
    ).toBeVisible();
  }
  await expect(page.locator(".loading-bar")).not.toBeVisible();
}

test("R04: reload preserves key metadata, hides secret and permits effective revocation", async ({
  page,
}) => {
  await login(page);
  await page
    .getByRole("button", { name: "Configurações", exact: true })
    .click();
  const panel = page.getByRole("region", {
    name: "Chaves de API",
    exact: true,
  });
  const created = page.waitForResponse(
    (response) =>
      response.url().endsWith("/api/admin/api-keys") &&
      response.request().method() === "POST",
  );
  await panel
    .getByRole("button", { name: "Criar chave de API", exact: true })
    .click();
  const key = await (await created).json();
  await expect(panel.getByRole("textbox")).toHaveValue(key.token);
  await page.reload();
  await page
    .getByRole("button", { name: "Configurações", exact: true })
    .click();
  await expect(panel.getByRole("textbox")).toHaveCount(0);
  const row = panel.getByRole("article", {
    name: "Chave " + key.id,
    exact: true,
  });
  await expect(row).toContainText("Ativa");
  await row.getByRole("button", { name: "Revogar chave", exact: true }).click();
  await expect(row).toContainText("Revogada");
  await expect(
    row.getByRole("button", { name: "Revogar chave", exact: true }),
  ).toBeDisabled();
  const response = await page.request.get("/api/connect/v1/summary", {
    headers: { Authorization: "Bearer " + key.token },
  });
  expect(response.status()).toBe(401);
  await page.getByLabel("Empresa", { exact: true }).selectOption(qa.tenantB);
  await expect(panel.getByText(key.id, { exact: true })).toHaveCount(0);
});

test("R05: existing-account link uses the original password and makes the invited tenant available", async ({
  page,
  playwright,
}) => {
  const admin = await playwright.request.newContext({
    baseURL: "http://127.0.0.1:5186",
  });
  const newUser = await playwright.request.newContext({
    baseURL: "http://127.0.0.1:5186",
  });
  const email =
    "browser-invite-" + crypto.randomUUID().slice(0, 8) + "@ebt.example";
  try {
    await post(admin, "/api/auth/login", {
      email: "admin@ebt.example",
      password: qa.password,
    });
    await post(admin, "/api/auth/context/" + qa.tenantA, undefined, 204);
    const original = await post(admin, "/api/admin/invitations", {
      email,
      role: "reader",
      portfolio: "principal",
    });
    await post(newUser, "/api/auth/activate", {
      token: original.activationToken,
      name: "Synthetic invited account",
      password: qa.password,
    });
    await post(admin, "/api/auth/context/" + qa.tenantB, undefined, 204);
    const invite = await post(admin, "/api/admin/invitations", {
      email,
      role: "reader",
      portfolio: "principal",
    });
    await page.goto("/?activation=" + invite.activationToken);
    await page
      .getByRole("button", {
        name: "Já tenho conta: entrar para aceitar o convite",
        exact: true,
      })
      .click();
    await page.getByLabel("E-mail", { exact: true }).fill(email);
    await page.getByLabel("Senha", { exact: true }).fill(qa.password);
    await reserveQaAuthOperation();
    await page.getByRole("button", { name: "Entrar", exact: true }).click();
    const form = page.getByRole("region", {
      name: "Aceitar convite",
      exact: true,
    });
    await expect(form.getByLabel("Código do convite")).toHaveValue(
      invite.activationToken,
      { timeout: 20000 },
    );
    await reserveQaAuthOperation();
    await form
      .getByRole("button", {
        name: "Aceitar convite com esta conta",
        exact: true,
      })
      .click();
    await expect(
      page
        .getByLabel("Empresa", { exact: true })
        .locator(`option[value="${qa.tenantB}"]`),
    ).toHaveCount(1);
    await page.getByLabel("Empresa", { exact: true }).selectOption(qa.tenantB);
    await expect(
      page.getByText("Empresa selecionada.", { exact: true }),
    ).toBeVisible();
    await page
      .getByRole("button", { name: "Configurações", exact: true })
      .click();
    await expect(
      page.getByRole("heading", { name: "Equipe e acesso", exact: true }),
    ).toHaveCount(0);
    await expect(
      page.getByRole("region", { name: "Chaves de API", exact: true }),
    ).toHaveCount(0);
    await page.getByLabel("Código do convite").fill(invite.activationToken);
    await reserveQaAuthOperation();
    await page
      .getByRole("button", {
        name: "Aceitar convite com esta conta",
        exact: true,
      })
      .click();
    await expect(page.getByRole("alert")).toContainText(
      "Convite inválido, expirado ou já utilizado",
    );
    expect(new URL(page.url()).search).toBe("");
  } finally {
    await newUser.dispose();
    await admin.dispose();
  }
});

test("R05: signed-in wrong account cannot accept another person's invitation", async ({
  page,
  playwright,
}) => {
  const admin = await playwright.request.newContext({
    baseURL: "http://127.0.0.1:5186",
  });
  try {
    await post(admin, "/api/auth/login", {
      email: "admin@ebt.example",
      password: qa.password,
    });
    await post(admin, "/api/auth/context/" + qa.tenantA, undefined, 204);
    const invite = await post(admin, "/api/admin/invitations", {
      email: "unrelated-" + crypto.randomUUID().slice(0, 8) + "@ebt.example",
      role: "reader",
      portfolio: "principal",
    });
    await login(page, "operador@ebt.example");
    await page.goto("/?activation=" + invite.activationToken);
    const form = page.getByRole("region", {
      name: "Aceitar convite",
      exact: true,
    });
    await reserveQaAuthOperation();
    await form
      .getByRole("button", {
        name: "Aceitar convite com esta conta",
        exact: true,
      })
      .click();
    await expect(form.getByRole("alert")).toContainText(
      "Este convite pertence a outra conta",
    );
  } finally {
    await admin.dispose();
  }
});

test("R04/R05: administration remains usable on mobile without horizontal overflow", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await login(page);
  await page
    .getByRole("button", { name: "Abrir navegação", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Configurações", exact: true })
    .click();
  await expect(
    page.getByRole("region", { name: "Chaves de API", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Consultando chaves…", { exact: true }),
  ).not.toBeVisible();
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth,
  );
  expect(overflow).toBe(false);
});
