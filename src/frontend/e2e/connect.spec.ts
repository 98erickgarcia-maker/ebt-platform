import { test, expect, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
const root = path.resolve(process.cwd(), "../..");
const qa = JSON.parse(
  fs.readFileSync(path.join(root, "tmp/runtime/qa-access.json"), "utf8"),
) as { password: string; tenantA: string; tenantB: string };
const run = Date.now().toString();
async function login(page: Page, email = "operador@ebt.example") {
  await page.goto("/");
  await page.getByLabel("E-mail", { exact: true }).fill(email);
  await page.getByLabel("Senha", { exact: true }).fill(qa.password);
  await page.getByRole("button", { name: "Entrar", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Meu dia", exact: true }),
  ).toBeVisible();
  await expect(page.getByText("Atualizando dados…")).not.toBeVisible();
}
test("Desktop CRM journey: create, reload, note, next action, close, document", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await login(page);
  await page.screenshot({
    path: path.join(root, "evidencias/capturas/connect-desktop.png"),
    fullPage: true,
  });
  await page
    .getByRole("button", { name: "Relacionamentos", exact: true })
    .click();
  await page.getByRole("button", { name: "Novo contato", exact: true }).click();
  let dialog = page.getByRole("dialog");
  await dialog.getByLabel("Nome", { exact: true }).fill("Browser QA " + run);
  await dialog
    .getByLabel("E-mail", { exact: true })
    .fill("browser@client.example");
  await dialog.getByRole("button", { name: "Salvar", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await page
    .getByRole("button", { name: "Abrir Browser QA " + run, exact: true })
    .click();
  await expect(
    page
      .getByRole("heading", { name: "Browser QA " + run, exact: true })
      .first(),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Registrar nota", exact: true })
    .click();
  dialog = page.getByRole("dialog");
  await dialog
    .getByLabel("Conteúdo da nota")
    .fill("Nota sintética pela interface");
  await dialog.getByRole("button", { name: "Salvar", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await expect(
    page.getByText("Nota sintética pela interface", { exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Nova tarefa", exact: true }).click();
  dialog = page.getByRole("dialog");
  await dialog.getByLabel("Próximo passo").fill("Próximo passo browser");
  await dialog.getByLabel("Prazo", { exact: true }).fill("2026-10-12T10:00");
  await dialog.getByRole("button", { name: "Salvar", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await expect(
    page.getByText("Próximo passo browser", { exact: true }),
  ).toHaveCount(2);
  await page.getByRole("button", { name: "Encerrar", exact: true }).click();
  dialog = page.getByRole("dialog");
  await dialog
    .getByLabel("Descreva o resultado ou motivo")
    .fill("Concluído pela interface");
  await dialog
    .getByRole("button", { name: "Confirmar resultado", exact: true })
    .click();
  await expect(dialog).not.toBeVisible();
  await expect(
    page.getByText("Nenhuma tarefa aberta", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Enviar arquivo", exact: true })
    .click();
  dialog = page.getByRole("dialog");
  await dialog.getByLabel("Título", { exact: true }).fill("Documento browser");
  await dialog.getByLabel("Arquivo PDF ou texto").setInputFiles({
    name: "browser.txt",
    mimeType: "text/plain",
    buffer: Buffer.from("Documento comercial sintético da interface"),
  });
  await dialog.getByRole("button", { name: "Salvar", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await expect(
    page.getByText("Documento browser", { exact: true }),
  ).toBeVisible();
  await page.screenshot({
    path: path.join(root, "evidencias/capturas/connect-contato.png"),
    fullPage: true,
  });
  await page.reload();
  await page
    .getByRole("button", { name: "Relacionamentos", exact: true })
    .click();
  await page.getByLabel("Buscar contatos").fill("Browser QA " + run);
  await page
    .getByRole("button", { name: "Abrir Browser QA " + run, exact: true })
    .click();
  await expect(
    page.getByText("Nota sintética pela interface", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Documento browser", { exact: true }),
  ).toBeVisible();
  expect(errors).toEqual([]);
});

test("Permission change clears a loaded contact and removes write controls", async ({
  page,
  browser,
}) => {
  await login(page);
  await page
    .getByRole("button", { name: "Relacionamentos", exact: true })
    .click();
  await page.getByLabel("Buscar contatos").fill("Contato Exemplo A");
  await page
    .getByRole("button", { name: /Contato Exemplo A contato@cliente.example/ })
    .click();
  await expect(
    page.getByRole("heading", { name: "Contato Exemplo A", exact: true, level: 1 }),
  ).toBeVisible();
  const context = await browser.newContext();
  const adminPage = await context.newPage();
  await login(adminPage, "admin@ebt.example");
  const rows = await (await context.request.get("/api/admin/members")).json();
  const member = rows.find(
    (x: { name: string }) => x.name === "Atendimento QA",
  );
  const mutate = async (body: unknown, version: number) => {
    const token = (
      await (await context.request.get("/api/security/csrf")).json()
    ).token;
    const response = await context.request.put(
      "/api/admin/members/" + member.id,
      {
        data: body,
        headers: { "X-CSRF-TOKEN": token, "If-Match": `"${version}"` },
      },
    );
    expect(response.ok()).toBe(true);
  };
  try {
    await mutate(
      { role: "reader", portfolio: "outra", active: true },
      member.version,
    );
    await page.getByRole("button", { name: "Meu dia", exact: true }).click();
    await expect(
      page.getByText(
        "Seu acesso foi atualizado. Confira a empresa e a carteira.",
      ),
    ).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "Contato Exemplo A", exact: true, level: 1 }),
    ).not.toBeVisible();
    await page
      .getByRole("button", { name: "Relacionamentos", exact: true })
      .click();
    await expect(
      page.getByRole("button", { name: "Novo contato", exact: true }),
    ).not.toBeVisible();
    await expect(
      page.getByText("Carteira: outra", { exact: true }),
    ).toBeVisible();
  } finally {
    const current = (
      await (await context.request.get("/api/admin/members")).json()
    ).find((x: { id: string }) => x.id === member.id);
    await mutate(
      { role: member.role, portfolio: member.portfolio, active: member.active },
      current.version,
    );
    await context.close();
  }
});
test("Tenant switch clears old contact data; consumer B works", async ({
  page,
}) => {
  await login(page, "admin@ebt.example");
  await page.getByLabel("Empresa", { exact: true }).selectOption(qa.tenantA);
  await expect(
    page.getByRole("status").filter({ hasText: "Empresa selecionada." }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Relacionamentos", exact: true })
    .click();
  await page.getByLabel("Buscar contatos").fill("Contato Exemplo A");
  await page
    .getByRole("button", { name: /Contato Exemplo A contato@cliente.example/ })
    .click();
  await page.getByLabel("Empresa", { exact: true }).selectOption(qa.tenantB);
  await expect(
    page.getByRole("heading", { name: "Relacionamentos", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", {
      name: /Contato Exemplo B contato@cliente.example/,
    }),
  ).toBeVisible();
  await expect(
    page.getByText("Contato Exemplo A", { exact: true }),
  ).not.toBeVisible();
  await page
    .getByRole("button", { name: /Contato Exemplo B contato@cliente.example/ })
    .click();
  await expect(
    page
      .getByRole("heading", { name: "Contato Exemplo B", exact: true })
      .first(),
  ).toBeVisible();
});
test("Mobile layout and reader profile prevent edit controls", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await login(page, "consulta@ebt.example");
  await expect(
    page.getByRole("button", { name: "Novo contato", exact: true }),
  ).not.toBeVisible();
  await page
    .getByRole("button", { name: "Abrir navegação", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Relacionamentos", exact: true })
    .click();
  await page.getByLabel("Buscar contatos").fill("Contato Exemplo A");
  await page
    .getByRole("button", { name: /Contato Exemplo A contato@cliente.example/ })
    .click();
  await expect(
    page.getByRole("button", { name: "Editar cadastro e etapa", exact: true }),
  ).not.toBeVisible();
  await expect(
    page.getByRole("button", { name: "Registrar nota", exact: true }),
  ).not.toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: path.join(root, "evidencias/capturas/connect-mobile.png"),
    fullPage: true,
  });
});
