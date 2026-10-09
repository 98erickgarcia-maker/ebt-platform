import { test, expect, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(process.cwd(), "../..");
const qa = JSON.parse(
  fs.readFileSync(path.join(root, "tmp/runtime/qa-access.json"), "utf8"),
) as { password: string };

async function login(page: Page) {
  await page.goto("/");
  await page.getByLabel("E-mail", { exact: true }).fill("operador@ebt.example");
  await page.getByLabel("Senha", { exact: true }).fill(qa.password);
  await page.getByRole("button", { name: "Entrar", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Meu dia", exact: true }),
  ).toBeVisible();
  await expect(page.getByText("Atualizando dados…")).not.toBeVisible();
}
async function createContact(page: Page, name: string) {
  const token = await (await page.request.get("/api/security/csrf")).json();
  const response = await page.request.post("/api/connect/v1/contacts", {
    data: { name, externalKey: crypto.randomUUID() },
    headers: {
      "X-CSRF-TOKEN": token.token,
      "Idempotency-Key": crypto.randomUUID(),
    },
  });
  expect(response.status()).toBe(201);
  return response.json() as Promise<{ id: string }>;
}

test("R02: inbox identifies actual channel recipient independently of paged contacts", async ({
  page,
}) => {
  await login(page);
  for (let i = 0; i < 26; i++)
    await createContact(page, "Pagina R02 " + Date.now() + " " + i);
  await page
    .getByRole("button", { name: "Relacionamentos", exact: true })
    .click();
  await page.getByLabel("Buscar contatos").fill("Pagina R02");
  await expect(
    page.getByText("Contato Exemplo A", { exact: true }),
  ).not.toBeVisible();
  await expect(page.getByText("Atualizando dados…")).not.toBeVisible();
  await page.getByRole("button", { name: "Conversas", exact: true }).click();
  const inbox = page.locator(".inbox");
  await expect(inbox.getByText("Contato Exemplo A")).toBeVisible();
  await expect(inbox.getByText(/\+5511999990001/).first()).toBeVisible();
  await inbox.getByRole("button", { name: /Contato Exemplo A/ }).click();
  await expect(
    page.getByRole("heading", { name: "Contato Exemplo A", exact: true }),
  ).toBeVisible();
  await expect(page.getByText("Destinatário: +5511999990001")).toBeVisible();
  await expect(
    page.getByRole("button", { name: /Confirmar resposta/ }),
  ).toBeDisabled();
});

for (const failure of [false, true]) {
  test(`R01: previous contact actions stay absent during delay${failure ? " and failed request" : ""}`, async ({
    page,
  }) => {
    await login(page);
    const name = "Contexto B " + Date.now();
    const contact = await createContact(page, name);
    await page
      .getByRole("button", { name: "Relacionamentos", exact: true })
      .click();
    await page.getByLabel("Buscar contatos").fill("Contato Exemplo A");
    await page
      .getByRole("button", { name: "Abrir Contato Exemplo A", exact: true })
      .click();
    await expect(page.getByText("Apresentar o EBT Connect").first()).toBeVisible();
    await page.getByRole("button", { name: /Voltar aos relacionamentos/ }).click();
    await page.getByLabel("Buscar contatos").fill(name);
    let release!: () => void;
    const held = new Promise<void>((resolve) => {
      release = resolve;
    });
    await page.route(
      "**/api/connect/v1/tasks?contactId=" + contact.id,
      async (request) => {
        await held;
        if (failure)
          await request.fulfill({
            status: 503,
            contentType: "application/json",
            body: JSON.stringify({ title: "Falha QA do contato B" }),
          });
        else await request.continue();
      },
    );
    try {
      await page
        .getByRole("button", { name: "Abrir " + name, exact: true })
        .click();
      await expect(page.getByRole("heading", { name, level: 1 })).toBeVisible();
      await expect(page.locator(".loading-bar")).toBeVisible();
      await expect(
        page.getByText("Apresentar o EBT Connect"),
      ).not.toBeVisible();
      await expect(
        page.getByRole("button", { name: "Encerrar", exact: true }),
      ).not.toBeVisible();
      release();
      await expect(page.locator(".loading-bar")).not.toBeVisible();
      if (failure)
        await expect(page.getByRole("alert")).toContainText(
          "Falha QA do contato B",
        );
      await expect(
        page.getByText("Apresentar o EBT Connect"),
      ).not.toBeVisible();
    } finally {
      release();
    }
  });
}

test("R01: switching contacts does not display previous contact notes or tasks", async ({
  page,
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
    page.getByRole("heading", { name: "Contato Exemplo A", level: 1 }),
  ).toBeVisible();
  await expect(page.getByText("Apresentar o EBT Connect").first()).toBeVisible();
  await page.getByRole("button", { name: /Voltar aos relacionamentos/ }).click();
  await page.getByLabel("Buscar contatos").fill("R01 QA");
  await page.getByRole("button", { name: "Novo contato", exact: true }).click();
  const dialog = page.getByRole("dialog");
  const name = "R01 QA " + Date.now();
  await dialog.getByLabel("Nome", { exact: true }).fill(name);
  await dialog
    .getByLabel("E-mail", { exact: true })
    .fill("r01-qa@client.example");
  await dialog.getByRole("button", { name: "Salvar", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await page.getByLabel("Buscar contatos").fill(name);
  await page
    .getByRole("button", { name: "Abrir " + name, exact: true })
    .click();
  await expect(page.getByRole("heading", { name, level: 1 })).toBeVisible();
  await expect(page.getByText("Apresentar o EBT Connect")).not.toBeVisible();
});
