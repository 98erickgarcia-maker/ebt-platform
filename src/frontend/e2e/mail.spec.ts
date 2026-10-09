import { test, expect, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { reserveQaAuthOperation } from "./qa-auth-budget";

test("Commercial context and templates stay usable at notebook and mobile widths", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1366, height: 768 });
  await login(page);
  const stamp = Date.now().toString();
  const csrf = await (await page.request.get("/api/security/csrf")).json();
  const headers = {
    "X-CSRF-TOKEN": csrf.token,
    "Idempotency-Key": "commercial-browser-" + stamp,
  };
  const contactResponse = await page.request.post("/api/connect/v1/contacts", {
    headers,
    data: {
      name: "Commercial browser " + stamp,
      email: "commercial-" + stamp + "@ebt.example",
      stage: "ganho",
      prospection: {
        source: "Indicação QA",
        contactRole: "Compras",
        need: "Organizar contatos",
        preferredChannel: "email",
        decisionMaker: "yes",
      },
    },
  });
  expect(contactResponse.status()).toBe(201);
  const contact = await contactResponse.json();
  const templateResponse = await page.request.post(
    "/api/connect/v1/mail/templates",
    {
      headers: {
        ...headers,
        "Idempotency-Key": "commercial-template-" + stamp,
      },
      data: {
        name: "Retorno browser " + stamp,
        subject: "Retorno {nome}",
        body: "Olá {nome}. Necessidade: {necessidade}. Cargo: {cargo}.",
        channel: "email",
        purpose: "relationship",
      },
    },
  );
  expect(templateResponse.status()).toBe(200);
  const template = await templateResponse.json();
  await page.keyboard.press("Control+k");
  await page
    .getByLabel("Contato, organização, tarefa ou documento")
    .fill(contact.name);
  await page
    .locator(".search-result")
    .filter({ hasText: contact.name })
    .first()
    .click();
  await expect(
    page.getByRole("heading", { name: contact.name, exact: true, level: 1 }),
  ).toBeVisible();
  await expect(
    page.getByText("Cliente ativo", { exact: true }).first(),
  ).toBeVisible();
  await page
    .getByRole("combobox", { name: "Template comercial", exact: true })
    .selectOption(template.id);
  await expect(
    page.getByRole("textbox", { name: "Texto personalizado", exact: true }),
  ).toHaveValue(
    "Olá " +
      contact.name +
      ". Necessidade: Organizar contatos. Cargo: Compras.",
  );
  await page
    .getByRole("button", {
      name: "Preparar e-mail com este modelo",
      exact: true,
    })
    .click();
  await expect(
    page.getByText(
      "Rascunho preparado. Acesse E-mail para revisar e aprovar esta versão.",
      { exact: true },
    ),
  ).toBeVisible();
  await page.screenshot({
    path: path.join(root, "tmp/e2e/commercial-notebook.png"),
    fullPage: true,
  });
  await page
    .getByRole("button", { name: "Editar cadastro e etapa", exact: true })
    .click();
  await page
    .getByText("Qualificação e contexto comercial", { exact: true })
    .click();
  await expect(
    page.getByRole("textbox", {
      name: "Necessidade identificada",
      exact: true,
    }),
  ).toHaveValue("Organizar contatos");
  expect(
    await page
      .getByRole("dialog")
      .evaluate(
        (el) => el.getBoundingClientRect().height <= window.innerHeight,
      ),
  ).toBeTruthy();
  await page.getByRole("button", { name: "Cancelar", exact: true }).click();
  await page.setViewportSize({ width: 390, height: 844 });
  await expect
    .poll(() =>
      page
        .locator(".sidebar")
        .evaluate((el) => el.getBoundingClientRect().right),
    )
    .toBeLessThanOrEqual(0);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.screenshot({
    path: path.join(root, "tmp/e2e/commercial-mobile.png"),
    fullPage: true,
  });
});
const root = path.resolve(process.cwd(), "../.."),
  qa = JSON.parse(
    fs.readFileSync(path.join(root, "tmp/runtime/qa-access.json"), "utf8"),
  );
async function login(page: Page, email = "admin@ebt.example") {
  await page.goto("/");
  await page.getByLabel("E-mail", { exact: true }).fill(email);
  await page.getByLabel("Senha", { exact: true }).fill(qa.password);
  await reserveQaAuthOperation();
  await page.getByRole("button", { name: "Entrar", exact: true }).click();
  await page
    .getByRole("button", { name: "Acessar Connect", exact: true })
    .click();
  const me = await (await page.request.get("/api/auth/me")).json();
  if (me.tenantId !== qa.tenantA) {
    await page.getByLabel("Empresa", { exact: true }).selectOption(qa.tenantA);
    await expect(
      page.getByText("Empresa selecionada.", { exact: true }),
    ).toBeVisible();
  }
  await expect(page.locator(".loading-bar")).not.toBeVisible();
}
async function mail(page: Page) {
  if (await page.getByRole("button", { name: "Abrir navegação" }).isVisible())
    await page.getByRole("button", { name: "Abrir navegação" }).click();
  await page
    .getByRole("navigation")
    .getByRole("button", { name: "E-mail", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "E-mail", exact: true }),
  ).toBeVisible();
  await expect(page.getByText("Carregando e-mails…")).not.toBeVisible();
}
test("Mail persists reviewed draft, no simulation, approval invalidated by edit, history and blocked provider", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await login(page);
  const stamp = Date.now().toString();
  const csrf = await (await page.request.get("/api/security/csrf")).json();
  const response = await page.request.post("/api/connect/v1/contacts", {
    data: {
      name: "Mail browser " + stamp,
      email: "browser-" + stamp + "@ebt.example",
    },
    headers: {
      "X-CSRF-TOKEN": csrf.token,
      "Idempotency-Key": "browser-mail-" + stamp,
    },
  });
  expect(response.status()).toBe(201);
  const contact = await response.json();
  await mail(page);
  await expect(
    page.getByRole("button", { name: "Simular", exact: true }),
  ).toHaveCount(0);
  await page
    .getByRole("button", { name: "Nova mensagem", exact: true })
    .click();
  await page.getByLabel("Buscar contato", { exact: true }).fill(contact.name);
  await page
    .getByRole("combobox", { name: "Contato", exact: true })
    .selectOption(contact.id);
  await page
    .getByLabel("Assunto", { exact: true })
    .fill("Mensagem browser " + stamp);
  await page
    .getByRole("textbox", { name: "Mensagem", exact: true })
    .fill("Texto para revisão, sem disparo real.");
  await page
    .getByRole("button", { name: "Salvar rascunho", exact: true })
    .click();
  await expect(
    page.getByText(
      "Rascunho salvo. A versão atual precisa de revisão antes do envio.",
      { exact: true },
    ),
  ).toBeVisible();
  await page.getByLabel("Buscar mensagens").fill("Mensagem browser " + stamp);
  let card = page
    .locator(".mail-list article")
    .filter({ hasText: "Mensagem browser " + stamp });
  await card.getByRole("button", { name: /Aprovar versão/ }).click();
  await expect(
    card.getByRole("button", { name: "Solicitar envio real", exact: true }),
  ).toBeDisabled();
  await page.reload();
  await page
    .getByRole("button", { name: "Acessar Connect", exact: true })
    .click();
  await mail(page);
  await page.getByLabel("Buscar mensagens").fill("Mensagem browser " + stamp);
  card = page
    .locator(".mail-list article")
    .filter({ hasText: "Mensagem browser " + stamp });
  await expect(card.getByText("Aprovado", { exact: true })).toBeVisible();
  await card.getByRole("button", { name: "Editar", exact: true }).click();
  await page
    .getByRole("textbox", { name: "Mensagem", exact: true })
    .fill("Texto alterado exige nova aprovação.");
  await page
    .getByRole("button", { name: "Salvar rascunho", exact: true })
    .click();
  await expect(card.getByText("Rascunho", { exact: true })).toBeVisible();
  await card
    .getByRole("button", { name: "Mensagem browser " + stamp, exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Histórico preservado" }),
  ).toBeVisible();
  await expect(
    page.getByText(/Texto editado; aprovação anterior invalidada/),
  ).toBeVisible();
  await page.screenshot({
    path: path.join(root, "tmp/e2e/mail-desktop.png"),
    fullPage: true,
  });
  expect(errors).toEqual([]);
});
test("Mail mobile, real scoped Ctrl K search, retry after failure and reader controls", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await login(page, "consulta@ebt.example");
  await mail(page);
  await expect(
    page.getByRole("button", { name: "Nova mensagem", exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Controle de envio", exact: true }),
  ).toHaveCount(0);
  await page.screenshot({
    path: path.join(root, "tmp/e2e/mail-mobile.png"),
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.keyboard.press("Control+k");
  await expect(
    page.getByRole("dialog", { name: "Buscar no Connect" }),
  ).toBeVisible();
  await page
    .getByLabel("Contato, organização, tarefa ou documento")
    .fill("Contato Exemplo A");
  await expect(page.locator(".search-result").first()).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.route("**/api/connect/v1/mail/status", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/problem+json",
      body: JSON.stringify({
        title: "Indisponibilidade sintética",
        code: "service_unavailable",
      }),
    }),
  );
  await page.getByRole("button", { name: "Atualizar", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText(
    "Indisponibilidade sintética",
  );
  await page.unroute("**/api/connect/v1/mail/status");
  await page
    .getByRole("button", { name: "Atualizar dados", exact: true })
    .click();
  await expect(page.getByRole("alert")).toHaveCount(0);
});
