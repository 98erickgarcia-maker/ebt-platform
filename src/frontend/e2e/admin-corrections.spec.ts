import { test, expect, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(process.cwd(), "../..");
const qa = JSON.parse(
  fs.readFileSync(path.join(root, "tmp/runtime/qa-access.json"), "utf8"),
) as {
  password: string;
  tenantA: string;
  tenantB: string;
};
async function login(page: Page) {
  await page.goto("/");
  await page.getByLabel("E-mail", { exact: true }).fill("admin@ebt.example");
  await page.getByLabel("Senha", { exact: true }).fill(qa.password);
  await page.getByRole("button", { name: "Entrar", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Meu dia", exact: true }),
  ).toBeVisible();
  await page.getByLabel("Empresa", { exact: true }).selectOption(qa.tenantA);
  await expect(page.locator(".loading-bar")).not.toBeVisible();
}
test("R04: an administrator can find and revoke a key after reloading", async ({
  page,
}) => {
  await login(page);
  await page
    .getByRole("button", { name: "Configurações", exact: true })
    .click();
  const created = page.waitForResponse(
    (response) =>
      response.url().endsWith("/api/admin/api-keys") &&
      response.request().method() === "POST",
  );
  await page
    .getByRole("button", { name: "Criar chave de API", exact: true })
    .click();
  const key = (await (await created).json()) as { id: string };
  await expect(page.locator(".alert.success")).toContainText("Chave criada");
  await page.reload();
  await page
    .getByRole("button", { name: "Configurações", exact: true })
    .click();
  const revoke = page.getByRole("button", {
    name: "Revogar chave " + key.id,
    exact: true,
  });
  await expect(revoke).toBeEnabled();
  await expect(page.getByLabel("Chave ou link preparado")).not.toBeVisible();
  await revoke.click();
  await expect(revoke).toBeDisabled();
  await expect(revoke.locator("..")).toContainText("Revogada");
});
test("R05: existing account accepts an invitation using its original password", async ({
  page,
}) => {
  await login(page);
  await page.getByLabel("Empresa", { exact: true }).selectOption(qa.tenantB);
  await expect(page.locator(".alert.success")).toContainText("Empresa selecionada");
  const token = await (await page.request.get("/api/security/csrf")).json();
  const response = await page.request.post("/api/admin/invitations", {
    data: {
      email: "outra@ebt.example",
      role: "reader",
      portfolio: "principal",
    },
    headers: { "X-CSRF-TOKEN": token.token },
  });
  expect(response.ok()).toBe(true);
  const invitation = (await response.json()) as { activationToken: string };
  await page.getByRole("button", { name: "Sair", exact: true }).click();
  await page.goto("/?activation=" + invitation.activationToken);
  await page
    .getByRole("button", {
      name: "Já tenho conta: usar meu acesso",
      exact: true,
    })
    .click();
  await page.getByLabel("E-mail", { exact: true }).fill("outra@ebt.example");
  await page.getByLabel("Senha", { exact: true }).fill(qa.password);
  await page
    .getByRole("button", { name: "Entrar e aceitar convite", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Meu dia", exact: true }),
  ).toBeVisible();
  await expect(page.getByLabel("Empresa", { exact: true })).toHaveValue(
    qa.tenantB,
  );
  await expect(
    page.getByRole("button", {
      name: "Aceitar convite com esta conta",
      exact: true,
    }),
  ).not.toBeVisible();
  await expect(
    page.getByRole("button", { name: "Novo contato", exact: true }),
  ).not.toBeVisible();
  const me = await (await page.request.get("/api/auth/me")).json();
  expect(me.tenants.map((tenant: { id: string }) => tenant.id)).toContain(
    qa.tenantA,
  );
  expect(me.role).toBe("reader");
});
